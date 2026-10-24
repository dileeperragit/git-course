# ConceptBridge Classroom Lab

A native Streamlit prototype for teachers to evaluate practical classroom activities. Includes eight fictional learners, a garden design mission, four-skill rubric, evidence checks, follow-up groups and CSV export.

## Run locally

Use Python 3.12. From this folder:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Publish from the selected repository

The prepared layout for `dileeperragit/git-course` places app files in `conceptbridge/` and theme settings in `.streamlit/config.toml` at the repository root.

At https://share.streamlit.io/ select **Create app**, then use:

- Repository: `dileeperragit/git-course`
- Branch: `codex/conceptbridge-streamlit`
- Main file path: `conceptbridge/app.py`
- Advanced settings: Python **3.12**
- Secrets: none required

Click **Deploy**. A deployment is complete only after Streamlit reports success and the app opens at its returned URL.

If uploading this standalone folder to a new repository, upload its contents at the repository root (including `.streamlit/`) and use `app.py` as the main file path instead.

Official instructions: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy

## Demo walkthrough

1. Select Aarav under Activity review.
2. Click Check evidence to see the area mismatch and missing independent response.
3. Record the independent response and select an observed score for each skill.
4. Complete the review, then open Class insights to see updated groups.
5. Export the class report before leaving.

Forms save all values together. Save draft or Check evidence leaves the review pending. Complete review requires individual explanation, an independent application response, positive measurements and scores for all skills. A completed review may still contain an incorrect student answer: that is valid evidence for the teacher to assess.

## Data and scope

- This is a demo using fictional learners. It has no school login or shared database.
- Each Streamlit session has its own review state. Refresh, disconnection or server restart may reset reviews. Export CSV before leaving. Data does not persist between sessions.
- Suggestions use visible arithmetic checks and rules based on teacher scores. No AI model, API key or image analysis is connected.
- The evaluation workflow covers area and perimeter. Other missions are instructional briefs.
- Student responses are not sent to a model or external analysis service by this app.
