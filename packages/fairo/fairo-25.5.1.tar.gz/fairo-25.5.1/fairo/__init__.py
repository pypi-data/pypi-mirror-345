import os


def extract_tag_release_id():
    # Get the full reference from the environment variable
    full_ref = os.getenv('GITHUB_REF')

    # Check if the GITHUB_REF is set and it's a tag
    if full_ref and full_ref.startswith('refs/tags/'):
        # Extract the tag name
        tag_name = full_ref.split('/')[-1]
        return tag_name.replace('release-v', '')
    else:
        return "0.1"


__version__ = extract_tag_release_id()
