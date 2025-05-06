
from typing import List
from fairo.core.agent.base_agent import SimpleAgent


def output_workflow_tools(agents):
        tools = []
        seen_names = set()
        tool_num = 1

        for agent in agents:
            for tool in agent.tool_instances:
                if tool.name in seen_names:
                    continue

                seen_names.add(tool.name)
                tools.append({
                    "name": tool.name,
                    "schema": tool.args_schema.args_schema.model_json_schema() if tool.args_schema else None,
                    "returns": tool.returns,
                    "tool_num": tool_num,
                    "description": tool.description
                })
                tool_num += 1

        return tools

def output_workflow_dependencies(agents: List[SimpleAgent]):
    dependencies = []
    seen_dependencies = set()
    dependency_num = 1
    for agent in agents:
        for store in agent.knowledge_stores:
            if store.collection_name in seen_dependencies:
                continue
            seen_dependencies.add(store.collection_name)
            store_info = {
                "dependency_num": dependency_num,
                "name": store.collection_name
            }
            if hasattr(store, 'collection_uuid'):
                store_info['id'] = store.collection_uuid
            dependencies.append(store_info)
            dependency_num += 1
    return dependencies

def output_workflow_agent_nodes(tools, dependencies, agents: List[SimpleAgent]):
    tool_map = {t['name']: t['tool_num'] for t in tools}
    dependency_map = {t['name']: t['dependency_num'] for t in dependencies}
    _agents = []
    outputs = []
    agent_num = 1
    output_num = 1
    for agent in agents:
        agent_outputs = []
        agent_tools = [
            tool_map[tool.name]
            for tool in agent.tool_instances
            if tool.name in tool_map
        ]
        agent_dependencies = [
            dependency_map[store.collection_name]
            for store in agent.knowledge_stores
            if store.collection_name in dependency_map
        ]
        if agent.output and len(agent.output) > 0:
            for output in agent.output:
                outputs.append({
                    "name": output.name,
                    "source": f"Node-{agent_num}",
                    "description": output.description,
                    "destination": output.destination,
                    "num": output_num
                })
                agent_outputs.append(output_num)
                output_num += 1
        _agents.append({
            "goal": agent.goal,
            "name": agent.agent_name,
            "role": agent.role,
            "tool": agent_tools,
            "knowledge_store": agent_dependencies,
            "output": agent_outputs,
            "tigger": {},
            "backstory": agent.backstory,
        })
        agent_num += 1
    nodes = {
                "1": {
                    "id": "1",
                    "slug": "",
                    "stage": "middle",
                    "title": "Agent Executor",
                    "params": {
                        "agents": _agents
                    },
                    "handler": [{
                        "step": "2",
                        "type": "go_to",
                        "condition": {
                            "value": "is_success",
                            "test_value": True,
                            "condition_test": "=="
                        },
                        "edge_description": ""
                    }],
                    "node_type": "KNOWLEDGE_STORE_AGENT_EXECUTOR",
                    "position_x": 490.24,
                    "position_y": 66.4,
                    "description": ""
                },
            }
    if len(outputs) > 0:
        nodes["2"] = {
                        "id": "2",
                        "slug": "",
                        "stage": "end",
                        "title": "Outputs",
                        "params": {
                            "outputs": outputs
                        },
                        "handler": [
                            {
                                "step": None,
                                "type": "finish",
                                "condition": {
                                    "value": "output",
                                    "test_value": True,
                                    "condition_test": "=="
                                },
                                "edge_description": "=="
                            }
                        ],
                        "node_type": "KNOWLEDGE_STORE_OUTPUT",
                        "position_x": 1031.65,
                        "position_y": 66.4,
                        "description": ""
                    }
    return nodes

def output_workflow_process_graph(agents):
    tools = output_workflow_tools(agents)
    dependencies = output_workflow_dependencies(agents)
    tools_json = {"tool": {
            "id": "tool",
            "slug": "",
            "type": "KNOWLEDGE_STORE_TOOLS",
            "stage": "start",
            "title": "Tools",
            "params": {
                "tools": tools
            },
            "handler": [
                {
                    "step": "1",
                    "type": "go_to",
                    "condition": None,
                    "edge_description": ""
                }
            ],
            "position_x": -152.7,
            "position_y": 353,
            "description": ""
        }} if len(tools) > 0 else {}
    dependency_json = {"dependency": {
            "id": "dependency",
            "slug": "",
            "type": "KNOWLEDGE_STORE_DEPENDENCIES",
            "stage": "start",
            "title": "Dependencies",
            "params": {
                "dependencies": dependencies
            },
            "handler": [
                {
                    "step": "1",
                    "type": "go_to",
                    "condition": None,
                    "edge_description": ""
                }
            ],
            "position_x": -152.7,
            "position_y": 121.61,
            "description": ""
        }} if len(dependencies) > 0 else {}
    return {
        "nodes": output_workflow_agent_nodes(tools, dependencies, agents),
        **dependency_json,
        **tools_json,
    }        
            