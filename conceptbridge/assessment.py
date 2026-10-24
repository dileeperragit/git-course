"""Transparent assessment helpers. No external AI or student-data service."""
import csv
import io
import math

RUBRIC = [
    ("Conceptual understanding", "Distinguishes area from perimeter."),
    ("Testing & evidence", "Uses measurements to compare designs fairly."),
    ("Reasoning & explanation", "Explains why the evidence supports a conclusion."),
    ("Independent application", "Applies the concept to a new situation alone."),
]
LEVELS = {None: "Not observed", 0: "Needs guidance", 1: "Emerging", 2: "Developing", 3: "Independent"}

def review_errors(student):
    errors = []
    if not student.get("explanation", "").strip():
        errors.append("Record the learner's individual explanation.")
    if not student.get("transfer", "").strip():
        errors.append("Record an independent application response.")
    scores = student.get("scores", [])
    if len(scores) != 4 or any(type(n) is not int or n not in range(4) for n in scores):
        errors.append("Collect evidence and score all four skills. Not observed stays pending.")
    if not all(isinstance(student.get(k), (int, float)) and not isinstance(student[k], bool)
               and math.isfinite(student[k]) and student[k] > 0 for k in ("length", "width", "area")):
        errors.append("Enter positive, finite measurements.")
    return errors

def evidence_checks(student):
    messages = []
    dims = [student.get(k) for k in ("length", "width", "area")]
    if all(isinstance(n, (int, float)) and math.isfinite(n) and n > 0 for n in dims):
        length, width, area = dims
        perimeter = 2 * (length + width)
        actual = length * width
        if not math.isclose(perimeter, 24, abs_tol=0.01):
            messages.append(f"The dimensions use {perimeter:g} units of fencing. Check the 24-unit constraint.")
        if not math.isclose(area, actual, abs_tol=0.01):
            messages.append(f"Reported area is {area:g}, but length × width gives {actual:g}. Ask the learner to count the interior squares. This mismatch alone does not establish a misconception.")
        else:
            messages.append("The reported area matches the dimensions. Ask why another rectangle with equal perimeter can have a different area.")
    else:
        messages.append("Collect positive measurements before checking arithmetic.")
    if len(student.get("explanation", "").strip()) < 25:
        messages.append("There is little explanation. Ask the learner to describe a design decision.")
    if not student.get("transfer", "").strip():
        messages.append("Independent application evidence is missing. Give a fresh problem before scoring that skill.")
    return messages

def followup(student):
    if not student.get("reviewed"):
        return ("Evidence check first", "Collect missing evidence and complete the teacher review.")
    scores = student["scores"]
    if scores[0] <= 1:
        return ("Boundary or planting space?", "Trace the boundary with string, then count the squares inside. Compare 2 × 10 and 6 × 6 designs.")
    if scores[3] <= 1:
        return ("A fresh problem, independently", "Find a rectangle with perimeter 24 and area at least 30. Ask for calculations and a reason.")
    if all(n == 3 for n in scores):
        return ("The garden path extension", "Add a one-unit-wide path along the inside of one edge. Compare usable planting areas.")
    return ("Compare and justify", "Compare 4 × 8, 5 × 7 and 6 × 6 rectangles. Explain what stays the same and why areas change.")

def csv_report(students):
    def safe(value):
        text = str(value if value is not None else "Not observed")
        return "'" + text if text.startswith(("=", "+", "-", "@", "\t", "\r", "\n")) else text
    stream = io.StringIO(newline="")
    writer = csv.writer(stream)
    writer.writerow(["Learner code", "Learner", "Team", "Review status", "Length (units)", "Width (units)",
                     "Reported area (square units)", "Explanation", "Independent application",
                     *[r[0] for r in RUBRIC], "Teacher feedback", "Suggested follow-up"])
    for s in students:
        writer.writerow([safe(v) for v in [s["id"], s["name"], s["team"], "Reviewed" if s["reviewed"] else "Pending",
                         s["length"], s["width"], s["area"], s["explanation"], s["transfer"],
                         *s["scores"], s["note"], followup(s)[0]]])
    return ("\ufeff" + stream.getvalue()).encode("utf-8")
