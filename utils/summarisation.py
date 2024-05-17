#Assumes OPENAI_API_KEY is set in the environment variables

import openai

def extract_messages_from_commits(pr_commit_data):
    unique_pr_titles = pr_commit_data['PR Title'].unique()
    overall_text = ""
    for pr_title in unique_pr_titles:
        text = f"Commits for PR: {pr_title}"
        commits = pr_commit_data[pr_commit_data['PR Title'] == pr_title]
        for index, row in commits.iterrows():
            if row['Commit Message'].startswith("Merge branch"):
                continue
            text += f"\n- {row['Commit Message']}"
        overall_text = overall_text + text + "\n"
    print(overall_text)
    return overall_text


def gpt_inference_changelog(commits, start_date, end_date):

    system_prompt = """# Docs Changelog Guidelines

    ## How to make a good changelog? 

    1. Changelogs are for **humans**, not machines.
    2. There should be an entry for **every version**.
    3. The same types of changes **are be grouped**. [See sections](#sections).
    4. The latest version comes first, the release dates are displayed.

    ## Sections

    |  Section     | Section purpose                   |
    | ------------ | --------------------------------- |
    | `Added`      | new features                      |
    | `Changed`    | changes in existing functionality |
    | `Deprecated` | soon-to-be removed features       |
    | `Removed`    | now removed features              |
    | `Fixed`      | any bug fixes                     |
    | `Security`   | in case of security issues        |
    | `Unreleased` | to note down upcoming changes     |

    ## Template

    ```
    ### Unreleased
    - New method `fetchPotatoes()` fetching potatoes; details at [the project page](#)

    ### Added
    - New method `returnWeirdFace()` returning a random avatar URL for a anonymous customer
    - New object `weirdFaces` used in `returnWeirdFace()` method

    ### Changed
    - Renamed `textualCorrespondence` to `chat` as it seems more readable

    ### Removed
    - Section about "changelog" vs "CHANGELOG".

    ### Fixed
    - Fix Markdown links to tag comparison URL with footnote-style links.

    ...
    ```"""

    prompt = [
        {"type": "text",
            "text": f"""I am sharing the text of all commits that were merged into main between {start_date} and {end_date}. {commits} Use it to create a changelog in the format as suggested in the System Prompt. Keep the entire output in a code block, ending with     Made with [Changelog Generator](changelog-generator.streamlit.io)"""}
    ]

    from openai import OpenAI
    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    )

    print(response.choices[0])
    summary = response.choices[0].message.content
    print(summary)
    return summary