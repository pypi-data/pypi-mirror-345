import types
from typing import List, Any, Callable, Dict, Union
from langchain_core.runnables import RunnableLambda, RunnableSequence
import logging

# Optional interfaces/types
class LLMAgentOutput:
    pass

class BaseClient:
    pass

logger = logging.getLogger(__name__)

class AgentExecutor:
    def __init__(
        self,
        agents: List[Any],
        verbose: bool = False,
        patch_run_output_json: Callable[[LLMAgentOutput], None] = None,
        client: BaseClient = None,
        workflow_run_id: str = ""
    ):
        self.agents = agents
        self.verbose = verbose
        self.patch_run_output_json = patch_run_output_json
        self.client = client
        self.workflow_run_id = workflow_run_id

        # Inject shared attributes into agents
        for agent in self.agents:
            if hasattr(agent, 'patch_run_output_json'):
                agent.patch_run_output_json = self.patch_run_output_json
            if hasattr(agent, 'set_client'):
                agent.set_client(self.client)
            if hasattr(agent, 'verbose'):
                agent.verbose = self.verbose
            if hasattr(agent, 'workflow_run_id'):
                agent.set_workflow_run_id(self.workflow_run_id)

        self.pipeline = self._build_pipeline()

    def _wrap_agent_runnable(self, agent, input_key: str, output_key: str) -> RunnableLambda:
        """
        Wraps the agent's .run() method into a RunnableLambda with a custom function name.
        Properly propagates errors instead of continuing to the next agent.
        """
        def base_fn(inputs: Dict[str, Any]) -> Dict[str, Any]:
            if self.verbose:
                logger.info(f"[{agent.__class__.__name__}] received input: {inputs}")
            
            # Run the agent, but don't catch exceptions - let them propagate
            # This will stop the entire pipeline on agent failure
            result = agent.run(inputs[input_key])
            
            # Check if result starts with "An error occurred" which indicates agent failure
            if isinstance(result, str) and result.startswith("An error occurred during execution:"):
                # Propagate the error by raising an exception to stop the execution
                raise RuntimeError(f"Agent {agent.__class__.__name__} failed: {result}")
                
            return {output_key: result}

        # Clone function and set custom name
        fn_name = f"runnable_{agent.__class__.__name__.lower().replace(' ', '_')}"
        runnable_fn = types.FunctionType(
            base_fn.__code__,
            base_fn.__globals__,
            name=fn_name,
            argdefs=base_fn.__defaults__,
            closure=base_fn.__closure__,
        )

        return RunnableLambda(runnable_fn)

    def _build_pipeline(self) -> RunnableSequence:
        if not self.agents:
            raise ValueError("At least one agent must be provided.")

        # Assign input/output keys
        for i, agent in enumerate(self.agents):
            agent.input_key = "input" if i == 0 else f"output_{i - 1}"
            agent.output_key = f"output_{i}"

        runnables = []
        for agent in self.agents:
            runnables.append(
                self._wrap_agent_runnable(agent, agent.input_key, agent.output_key)
            )

        # Build RunnableSequence from all steps
        pipeline = runnables[0]
        for r in runnables[1:]:
            pipeline = pipeline | r  # chaining

        return pipeline

    def run(self, input_data: Union[str, Dict[str, str]]) -> Dict[str, Any]:
        """
        Execute the pipeline using the provided input.
        Properly handles and propagates errors from agents.
        """
        first_input_key = getattr(self.agents[0], 'input_key', 'input')

        # Normalize input
        if isinstance(input_data, str):
            input_data = {first_input_key: input_data}
        elif first_input_key not in input_data:
            raise ValueError(f"Missing required input key: '{first_input_key}'")

        if self.verbose:
            logger.info("Running agent pipeline...")
            logger.info(f"Initial input: {input_data}")

        try:
            # Run the pipeline but don't catch exceptions
            result = self.pipeline.invoke(input_data)
            
            if self.verbose:
                logger.info("Pipeline execution completed")
                logger.info(f"Final output: {result}")
                
            return result
            
        except Exception as e:
            # Log the error
            if self.verbose:
                logger.error(f"Pipeline execution failed: {str(e)}")
            
            # Propagate the exception so calling code can handle it
            raise
