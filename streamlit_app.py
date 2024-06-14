import streamlit as st
import re
from utils.github_data_fetch import fetch_prs_merged_between_dates, fetch_commits_from_prs
from utils.summarisation import gpt_inference_changelog, extract_messages_from_commits
from htbuilder import HtmlElement, div, ul, li, br, hr, a, p, img, styles, classes, fonts
from htbuilder.units import percent, px

st.title('Changelog Auto-Generator')
st.markdown("This app generates a changelog based on the commits in a repository. [See code on Github](https://github.com/DrDroidLab/changelog-generator)")

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
    prs, repo_description = fetch_prs_merged_between_dates(owner, repo, start_date, end_date, main_branch)
    if prs is None or prs.shape[0] == 0:
        st.error("No PRs found in the given date range")
        st.stop()
    st.text(f"Fetched {prs.shape[0]} PRs")
    st.text("Fetching commits...")
    commits = fetch_commits_from_prs(prs, owner, repo)
    st.text(f"Fetched {commits.shape[0]} commits")
    st.text("Extracting commit messages...")
    prompt_body = extract_messages_from_commits(commits)
    st.text("Commit messages extracted")
    st.text("Generating changelog...")
    changelog = gpt_inference_changelog(prompt_body, start_date, end_date,owner, repo, repo_description, main_branch)
    st.text("Changelog generated")
    st.markdown(changelog)
    # st.button('Generate Changelog', key='generate_button', on_click='enable')


def image(src_as_string, **style):
    return img(src=src_as_string, style=styles(**style))

def link(hyperlink, text, **style):
    return a(_href=hyperlink, _target="_blank", style=styles(**style))(text)


def layout(*args):
    style = """
    <style>
      # MainMenu {visibility: hidden;}
      footer {visibility: hidden;}
     .stApp { bottom: 105px; }
    </style>
    """

    style_div = styles(
        position="fixed",
        left=0,
        bottom=0,
        margin=px(0, 0, 0, 0),
        width=percent(100),
        color="black",
        text_align="center",
        height="auto",
        opacity=1
    )

    style_hr = styles(
        display="block",
        margin=px(8, 8, "auto", "auto"),
        border_style="inset",
        border_width=px(2)
    )

    body = p()
    foot = div(
        style=style_div
    )(
        hr(
            style=style_hr
        ),
        body
    )

    st.markdown(style, unsafe_allow_html=True)

    for arg in args:
        if isinstance(arg, str):
            body(arg)

        elif isinstance(arg, HtmlElement):
            body(arg)

    st.markdown(str(foot), unsafe_allow_html=True)


def footer():
    my_args = [
        "Made with ❤️ by ",
        br(),
        link("https://drdroid.io", image(
            'https://assets-global.website-files.com/642ad9ebc00f9544d49b1a6b/652262b9496b7b6fa1843f19_Frame%2013910.png')),
    ]
    layout(*my_args)


if __name__ == "__main__":
    footer()