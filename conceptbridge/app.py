"""ConceptBridge: teacher review of practical classroom activities."""
import copy
import json
from pathlib import Path
import streamlit as st
from assessment import RUBRIC, LEVELS, csv_report, evidence_checks, followup, review_errors

st.set_page_config(page_title="ConceptBridge · Classroom Lab", page_icon="🌱", layout="wide")
SEED = json.loads(Path(__file__).with_name("sample_learners.json").read_text(encoding="utf-8"))
if "learners" not in st.session_state:
    st.session_state.learners = copy.deepcopy(SEED)
    st.session_state.revision = 0
students = st.session_state.learners

st.markdown("""<style>
.block-container{padding-top:2.4rem;max-width:1450px}h1{letter-spacing:-1.3px}h2{letter-spacing:-.5px}
[data-testid="stSidebar"]{border-right:1px solid #dce5d6}div[data-testid="stMetric"]{background:white;border:1px solid #e0e6d9;border-radius:12px;padding:20px}
div[data-testid="stMetricValue"]{color:#163f36} div.stButton>button[kind="primary"]{background:#163f36;border-color:#163f36}
</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.title("🌱 ConceptBridge")
    st.caption("TEACHER WORKSPACE")
    page = st.radio("Navigation", ["Activity review", "Mission library", "Class insights", "Assessment guide"], label_visibility="collapsed")
    st.divider()
    st.caption("INTERACTIVE PROTOTYPE")
    st.write("Grade 6 · Mathematics")
    st.caption("Eight fictional learners. Reviews stay in your current Streamlit session. Export before leaving or refreshing.")
    reset = st.checkbox("Confirm reset of demo data")
    if st.button("Reset demo data", disabled=not reset):
        st.session_state.learners = copy.deepcopy(SEED)
        st.session_state.revision += 1
        st.rerun()

top, export = st.columns([3, 1])
top.caption(f"CLASSROOM LAB / {page.upper()}")
export.download_button("↓ Export class report", csv_report(students), "ConceptBridge-Class-Report.csv", "text/csv", use_container_width=True)
st.caption("EVIDENCE BEFORE EVALUATION")

def metrics():
    reviewed = [s for s in students if s["reviewed"]]
    scores = [n for s in reviewed for n in s["scores"]]
    cols = st.columns(4)
    cols[0].metric("Learners", len(students))
    cols[1].metric("Reviews complete", f"{len(reviewed)} / {len(students)}")
    cols[2].metric("Need concept support", sum(s["scores"][0] <= 1 for s in reviewed))
    cols[3].metric("Average rubric score", f"{sum(scores)/len(scores):.1f} / 3" if scores else "Not yet reviewed")
    st.caption("Score summaries include completed teacher reviews only.")

MISSIONS = [
    ("Save the School Garden", "Area & perimeter", "25 minutes", "String, ruler and squared paper", [
        "Each learner predicts whether equal perimeter means equal area.",
        "Teams build at least two rectangles with 24 units of fencing and compare areas.",
        "Add a one-unit-wide path along the inside of one edge. Compare usable areas.",
        "Individually find a rectangle with perimeter 24 and area at least 30. Explain the answer."],
     "Prediction, measured dimensions, area calculations, explanation and independent response."),
    ("Rescue the Paper Bridge", "Structures & fair testing", "25 minutes", "Paper, ruler, fixed tape allowance and identical small weights", [
        "Predict which paper shape will carry a load over a short fixed gap.",
        "Build and test over a tray. Keep gap, weights and loading position constant.",
        "Redesign with the same material allowance and retest.",
        "Individually explain the change and predict what a wider gap might do."],
     "Design sketch, controlled procedure, recorded loads and explanation linked to results."),
    ("The Canteen Deal Detective", "Unit prices & percentages", "20 minutes", "Fictional offer cards, paper money and shopping list", [
        "Predict which offer gives best value for the shopping list.",
        "Calculate total costs and compare unit prices.",
        "Change the quantity needed and recheck the choice.",
        "Individually justify the final purchase using calculations."],
     "Calculations, comparisons and an independent justification."),
]

def mission_brief(mission):
    title, concept, time, materials, steps, evidence = mission
    st.subheader(title)
    st.caption(f"{concept} · {time} · Teams of four")
    st.write("**Materials:** " + materials)
    for i, step in enumerate(steps, 1):
        st.write(f"{i}. {step}")
    st.write("**Evidence to collect:** " + evidence)

if page == "Activity review":
    st.title("See the thinking behind the activity.")
    st.write("Review what each learner did, understood and can apply independently.")
    with st.expander("Current mission: Save the School Garden · 24 units of fencing"):
        mission_brief(MISSIONS[0])
    metrics()
    left, right = st.columns([1, 2], gap="large")
    with left:
        st.subheader("Learner evidence")
        search = st.text_input("Search learner or team", placeholder="Search…")
        status = st.radio("Review status", ["All", "To review", "Reviewed"], horizontal=True)
        matching = [s for s in students if search.lower() in (s["name"] + " " + s["team"]).lower()
                    and (status == "All" or s["reviewed"] == (status == "Reviewed"))]
        if not matching:
            st.info("No learners match this filter.")
        else:
            learner_id = st.radio("Choose learner", [s["id"] for s in matching],
                format_func=lambda sid: next(f"{s['name']} · {s['team']} {'✓' if s['reviewed'] else '○'}" for s in matching if s["id"] == sid))
    with right:
        if matching:
            s = next(s for s in students if s["id"] == learner_id)
            st.subheader(s["name"])
            st.caption(f"{s['id']} · {s['team']} · {'Reviewed' if s['reviewed'] else 'To review'}")
            st.caption("01 / ACTIVITY EVIDENCE")
            # A form commits measurements, evidence and rubric scores together.
            with st.form(f"review_{s['id']}_{st.session_state.revision}"):
                a, b, c = st.columns(3)
                length = a.number_input("Length (units)", min_value=0.1, value=float(s["length"]), step=0.1)
                width = b.number_input("Width (units)", min_value=0.1, value=float(s["width"]), step=0.1)
                area = c.number_input("Reported area (square units)", min_value=0.1, value=float(s["area"]), step=0.1)
                explanation = st.text_area("Student's explanation", value=s["explanation"], height=100)
                transfer = st.text_area("Independent application", value=s["transfer"], height=100,
                    placeholder="A rectangle needs perimeter 24 and area at least 30. Record the learner's answer and reasoning.")
                st.caption("02 / TEACHER RUBRIC")
                scores = []
                for i, (title, description) in enumerate(RUBRIC):
                    options = list(LEVELS)
                    scores.append(st.selectbox(title, options, index=options.index(s["scores"][i]),
                        format_func=lambda n: "— Not observed" if n is None else f"{n} · {LEVELS[n]}", help=description))
                note = st.text_area("Teacher feedback / next step", value=s["note"])
                st.caption("Submit saves the entire form. Drafts remain pending. Switching learners before submitting discards unsaved changes.")
                draft_col, check_col, complete_col = st.columns(3)
                draft = draft_col.form_submit_button("Save draft", use_container_width=True)
                check = check_col.form_submit_button("Check evidence", use_container_width=True)
                complete = complete_col.form_submit_button("Complete review", type="primary", use_container_width=True)
            if draft or check or complete:
                candidate = {**s, "length": length, "width": width, "area": area, "explanation": explanation,
                             "transfer": transfer, "scores": scores, "note": note, "reviewed": False}
                errors = review_errors(candidate) if complete else []
                candidate["reviewed"] = complete and not errors
                students[students.index(s)] = candidate
                if errors:
                    st.session_state.feedback = ("warning", "Saved as pending. " + " ".join(errors))
                elif complete:
                    st.session_state.feedback = ("success", "Review complete. Class insights updated.")
                else:
                    st.session_state.feedback = ("info", "Evidence saved as a pending draft.")
                st.session_state.checked = candidate["id"] if check else None
                st.rerun()
            if "feedback" in st.session_state:
                kind, text = st.session_state.pop("feedback")
                getattr(st, kind)(text)
            st.caption("Transparent demo rules. No AI service connected. The teacher decides all scores.")
            if st.session_state.get("checked") == s["id"]:
                with st.container(border=True):
                    st.write("**Evidence check · Teacher confirmation needed**")
                    for message in evidence_checks(s):
                        st.write(message)
            if s["reviewed"]:
                title, text = followup(s)
                st.success(f"Suggested follow-up: {title}\n\n{text}")

elif page == "Mission library":
    st.title("Small missions. Meaningful thinking.")
    st.info("The working evaluation workflow covers the garden mission. The other missions are activity briefs for expansion.")
    for mission in MISSIONS:
        with st.expander(mission[0], expanded=mission == MISSIONS[0]):
            mission_brief(mission)

elif page == "Class insights":
    st.title("The next lesson starts with evidence.")
    metrics()
    reviewed = [s for s in students if s["reviewed"]]
    a, b = st.columns(2, gap="large")
    with a:
        st.subheader("Skills across the class")
        if not reviewed:
            st.info("Complete a teacher review to see skill summaries.")
        for i, (title, _) in enumerate(RUBRIC):
            if reviewed:
                score = sum(s["scores"][i] for s in reviewed) / len(reviewed)
                st.write(f"**{title}** · {score:.1f} / 3")
                st.progress(score / 3)
        st.caption("These scores describe this session. They are not permanent learner labels.")
    with b:
        st.subheader("Suggested follow-up groups")
        groups = {}
        for s in reviewed:
            title, text = followup(s)
            groups.setdefault(title, {"text": text, "names": []})["names"].append(s["name"])
        for title, group in groups.items():
            with st.container(border=True):
                st.write(f"**{title}**")
                st.write(group["text"])
                st.caption(", ".join(group["names"]))
        if not groups:
            st.info("No completed reviews yet.")

else:
    st.title("A shared language for understanding.")
    st.write("Score observable evidence, then choose a next step that helps the learner progress.")
    st.subheader("The four skills")
    for title, description in RUBRIC:
        st.write(f"**{title}:** {description}")
    st.subheader("Score meaning")
    for level, label in LEVELS.items():
        descriptions = {None: "Insufficient individual evidence. Leave pending.", 0: "An attempt does not yet demonstrate the skill, even with prompting.",
                        1: "Part of the skill appears with substantial support.", 2: "The skill appears with occasional prompting or an incomplete explanation.",
                        3: "The learner demonstrates and explains the skill without assistance."}
        st.write(f"**{'—' if level is None else level} · {label}:** {descriptions[level]}")
    st.info("Enjoyment, speed and a team's product do not establish individual understanding. Collect an individual explanation and a fresh application response.")
    st.caption("This demo does not provide login, a shared school database, image analysis or a live AI model. Reviews are isolated by Streamlit session and may reset after refresh or disconnection. Export before leaving.")
