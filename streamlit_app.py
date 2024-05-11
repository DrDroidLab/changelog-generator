import streamlit as st
import re
from utils.github_data_fetch import fetch_prs_merged_between_dates, fetch_commits_from_prs
from utils.summarisation import gpt_inference_changelog, extract_messages_from_commits

st.title('Changelog Auto-Generator')
st.text('This app generates a changelog based on the commits in a repository.')

def validate_github_url(url):
    pattern = r'^https:\/\/github\.com\/([A-Za-z0-9_.-]+)\/([A-Za-z0-9_.-]+)$'
    match = re.match(pattern, url)
    if match:
        owner = match.group(1)
        repository_name = match.group(2)
        return owner, repository_name
    else:
        return None, None

repository = st.text_input('Repository URL', 'https://github.com/DrDroidLab/playbooks')
owner, repo = validate_github_url(repository)
if owner is None or repo is None:
    st.error('Invalid repository URL. Switching to default repository.')
    owner, repo = 'DrDroidLab', 'playbooks'

start_date, end_date = st.columns(2)
start_date = start_date.date_input('Start Date')
end_date = end_date.date_input('End Date')

only_main_prs = st.checkbox('Only Include PRs merged into main branch', value=True)
if (st.checkbox('Change main branch name', value=False)):
    main_branch = st.text_input('Main branch name', 'main')
else:
    main_branch = 'main'

st.text("Review the details and click the button below to generate the changelog.")
st.markdown(f"Repository: {owner}/{repo}")
st.markdown(f"Date Range: {start_date} to {end_date}")
st.markdown(f"Main Branch: {main_branch}")

if 'clicked' not in st.session_state:
    st.session_state.clicked = False

def click_button():
    st.session_state.clicked = True

st.button('Generate Changelog', key='generate_button', on_click=click_button)

if(st.session_state.clicked):
    st.session_state.clicked = False
    st.text("Fetching PRs...")
    prs = fetch_prs_merged_between_dates(owner, repo, start_date, end_date, main_branch)
    st.text(f"Fetched {prs.shape[0]} PRs")
    st.text("Fetching commits...")
    commits = fetch_commits_from_prs(prs, owner, repo)
    st.text(f"Fetched {commits.shape[0]} commits")
    st.text("Extracting commit messages...")
    prompt_body = extract_messages_from_commits(commits)
    st.text("Commit messages extracted")
    st.text("Generating changelog...")
    changelog = gpt_inference_changelog(prompt_body)
    st.text("Changelog generated")
    st.markdown(changelog)
    # st.button('Generate Changelog', key='generate_button', on_click='enable')