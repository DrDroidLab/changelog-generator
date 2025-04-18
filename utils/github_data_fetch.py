#Assumes github_api_key is set in the environment variables 

import requests
import pandas as pd
import time
from tqdm import tqdm
from datetime import datetime, timedelta
import os

def github_api_call(url_suffix, owner, repo, params = {}):

    # Set the bearer token
    token = os.getenv('github_api_key',None)
    if token is None:
        raise ValueError("Please set the 'github_api_key' environment variable")

    # Set the headers for the API request
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }
    if repo is not None:
        url = f'https://api.github.com/repos/{owner}/{repo}/{url_suffix}'
    else:
        url = f'https://api.github.com/orgs/{owner}/{url_suffix}'
    print(url)
    time.sleep(1)  # Add a sleep of 1 second
    response = requests.get(url, params=params, headers=headers)
    return response

def fetch_commits_from_prs(prs, owner, repo, progress_callback=None):
    commit_data = []
    total_prs = len(prs.index)
    for i, idx in enumerate(prs.index):
        pr_number = prs.loc[idx, 'number']
        pr_user = prs.loc[idx, 'user']['login']
        time.sleep(1)
        commits = fetch_commits_from_pr(pr_number, owner, repo)
        for commit in commits:
            if 'committer' in commit and commit['committer'] is not None:
                commit_author = commit['committer'].get('login')
            else:
                commit_author = pr_user
            commit_data.append({
                'PR Number': pr_number,
                'PR Title': prs.loc[idx,'title'],
                'Commit SHA': commit['sha'],
                'Commit Message': commit['commit']['message'],
                'Commit Author': commit_author
            })
        if progress_callback:
            progress_callback((i + 1) / total_prs)
    df_commit_data = pd.DataFrame(commit_data)
    return df_commit_data

def fetch_commits_from_pr(pr_number, owner, repo):
    # Construct the API URL for fetching the commits of the PR
    commits_url_suffix = f"pulls/{pr_number}/commits"
    # Make the API call to fetch the commits
    response = github_api_call(commits_url_suffix, owner, repo)

    # Check if the API call was successful
    if response.status_code == 200:
        commits = response.json()
        return commits
    else:
        print(f"Failed to fetch commits from PR {pr_number}. Status code: {response.status_code}")
        return None
    
def fetch_prs_merged_between_dates(owner, repo, start_date, end_date, main_branch='main'):
    # Format the date range in ISO 8601 format
    start_date_str = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_date_str = end_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    # Construct the API URL for fetching the PRs merged between the dates
    prs_url_suffix = "pulls"
    params = {
        "state": "closed",
        "base": main_branch,
        "sort": "updated",
        "direction": "desc",
        "per_page": 100    
        }
    # Make the API call to fetch the PRs
    response = github_api_call(prs_url_suffix, owner, repo, params)

    # Check if the API call was successful
    if response.status_code == 200:
        prs = response.json()
        # Create a DataFrame from the merged PRs
        df = pd.DataFrame(prs)
        try:
            repo_description = prs[0]['head']['repo']['description']
        except:
            repo_description = ''
            print('repo description fetch failed')
        df = df[~df['merged_at'].isnull()]
        df['merged_at'] = pd.to_datetime(df['merged_at'])
        df = df[(df['merged_at'].dt.date >= start_date) & (df['merged_at'].dt.date <= end_date)]
        return df, repo_description
    else:
        print(f"Failed to fetch PRs merged between {start_date} and {end_date}. Status code: {response.status_code} - {response.text}")
        return None, ''

def fetch_org_users(owner):
    # Construct the API URL for fetching the users of the organization
    org_users_url_suffix = f"members?per_page=100"
    # Make the API call to fetch the users
    response = github_api_call(org_users_url_suffix, owner, None)

    # Check if the API call was successful
    if response.status_code == 200:
        users = response.json()
        return [user['login'] for user in users]
    else:
        print(f"Failed to fetch users from organization {owner}. Status code: {response.status_code}")
        return None