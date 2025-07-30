import os
import requests
import yaml

GITHUB_OWNER = os.getenv('GITHUB_OWNER', 'cainam') # Get from environment, default to 'yourusername'
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

# GitHub API Endpoint for a user's repositories:
API_REPOS = f"https://api.github.com/users/{GITHUB_OWNER}/repos"

def check_file_exists_and_fetch(repo, path, headers):
    """
    Checks if a file exists in a GitHub repository and, if so, fetches its content.
    Args:
        repo (str): The name of the repository.
        path (str): The path to the file within the repository (e.g., 'src/main.py').
    Returns:
        tuple: (bool, str or None) - (True if file exists, file content if exists else None)
    """
    base_url = f"https://api.github.com/repos/{GITHUB_OWNER}/{repo}/contents/{path}"

    print(f"Checking for file existence: {base_url}")

    try:
        headers["Accept"] = "application/vnd.github.v3.raw"
        get_response = requests.get(base_url, headers=headers, timeout=10)
        get_response.raise_for_status()
        return True, get_response.text.split("\n")

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"File '{path}' not found (404 Error).")
            return False, []
        else:
            print(f"An HTTP error occurred: {e}")
            return False, []
    except requests.exceptions.ConnectionError as e:
        print(f"A connection error occurred: {e}")
        return False, []
    except requests.exceptions.Timeout as e:
        print(f"The request timed out: {e}")
        return False, []
    except requests.exceptions.RequestException as e:
        print(f"An unexpected request error occurred: {e}")
        return False, []

def generate_site_inventory():
    headers = {
        "Accept": "application/vnd.github.v3+json", "Authorization": f"token {GITHUB_TOKEN}" }

    print(f"Fetching repositories for {GITHUB_OWNER}...")
    response = requests.get(API_REPOS, headers=headers)
    response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
    repos = response.json()

    site_inventory = []
    for repo in repos:
        if repo.get('has_pages') and not repo.get('archived'):
            if repo['name'] == f"{GITHUB_OWNER}.github.io":
                name = "Main"
                url = f"https://{GITHUB_OWNER}.github.io/"
            else:
                name = repo['name'].replace('-', ' ').title()
                url = f"https://{GITHUB_OWNER}.github.io/{repo['name']}/"
            got_pages, pages = check_file_exists_and_fetch(repo['name'], 'docs/_data/pages.txt', headers)
            if 'index' in pages: pages.remove('index')
            site_inventory.append({
                "name": name,
                "url": url,
                "description": repo['description'] if repo['description'] else f"",
                "pages": pages
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
