import os
import requests
import yaml

GITHUB_OWNER = os.getenv('GITHUB_OWNER', 'cainam') # Get from environment, default to 'yourusername'
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

# GitHub API Endpoint for a user's repositories:
API_URL = f"https://api.github.com/users/{GITHUB_OWNER}/repos"

def generate_site_inventory():
    headers = {
        "Accept": "application/vnd.github.v3+json", "Authorization": f"token {GITHUB_TOKEN}" }

    print(f"Fetching repositories for {GITHUB_OWNER}...")
    response = requests.get(API_URL, headers=headers)
    response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
    repos = response.json()

    site_inventory = []

    # Add the general pages home itself
    site_inventory.append({
        "name": "General Pages Home",
        "url": f"https://{GITHUB_OWNER}.github.io/",
        "description": "the main page"
    })

    for repo in repos:
        # Filter for repositories that are likely GitHub Pages project sites.
        # You can customize this logic:
        # - `has_pages`: Checks if GitHub Pages is enabled for the repo.
        # - `!repo['archived']`: Excludes archived repositories.
        # - `repo['name'] != f"{GITHUB_OWNER}.github.io"`: Excludes the general pages repo itself.
        if repo.get('has_pages') and not repo.get('archived') and repo['name'] != f"{GITHUB_OWNER}.github.io":
            site_inventory.append({
                "name": repo['name'].replace('-', ' ').title(), # Example: "my-project" -> "My Project"
                "url": f"https://{GITHUB_OWNER}.github.io/{repo['name']}/" # instead of the repo url# repo['html_url'],
                "description": repo['description'] if repo['description'] else f"A project about {repo['name'].replace('-', ' ')}."
            })

    # Sort the inventory alphabetically by name (optional)
    site_inventory.sort(key=lambda x: x['name'])

    # Ensure the _data directory exists
    os.makedirs('_data', exist_ok=True)
    output_path = os.path.join('_data', 'site_inventory.yml')

    with open(output_path, 'w') as f:
        yaml.dump(site_inventory, f, default_flow_style=False, sort_keys=False)

    print(f"Successfully generated {len(site_inventory)} entries in {output_path}")

if __name__ == "__main__":
    generate_site_inventory()
