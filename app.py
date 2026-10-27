from flask import Flask, request, jsonify, send_from_directory, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, json, os, re, secrets
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "career_compass.db")
app = Flask(__name__, static_folder=None)
app.secret_key = os.environ.get("CAREER_COMPASS_SECRET", secrets.token_hex(32))
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax")

CAREER_DATA = {
 "engineering": {"name":"Engineering & Applied Science","summary":"Explore how maths and science are used to design, build and improve systems.","degree":"After Class 12, compare B.E./B.Tech branches and other eligible technical routes."},
 "computer": {"name":"Computer Science & Software","summary":"Explore programming, digital products, cybersecurity and structured problem-solving.","degree":"After Class 12, compare B.Tech/B.E. CSE or IT, BCA and B.Sc. Computer Science routes."},
 "ai": {"name":"AI, Data & Mathematics","summary":"Explore patterns, statistics, coding and evidence-led decisions.","degree":"Compare computing, statistics, mathematics and data-science degrees against eligibility rules."},
 "health": {"name":"Healthcare & Life Sciences","summary":"Explore health, biology, patient care, lab science and biological research.","degree":"Routes may include medicine, nursing, pharmacy, allied health and life sciences; requirements differ."},
 "commerce": {"name":"Commerce, Finance & Business","summary":"Explore accounting, economics, entrepreneurship, marketing and business analytics.","degree":"Compare B.Com, BBA, economics, finance and professional qualification routes."},
 "law": {"name":"Law & Public Policy","summary":"Explore legal reasoning, reading, writing, debate and policy.","degree":"Compare integrated law after Class 12 and other eligible routes; entrance rules vary."},
 "design": {"name":"Design & Creative Technology","summary":"Explore visual communication, product design, interaction design and creative problem-solving.","degree":"Compare design programmes, portfolios and entrance requirements."},
 "humanities": {"name":"Humanities, Psychology & Social Sciences","summary":"Explore people, society, language, history, education and research.","degree":"Compare BA and related programmes; some careers require further study."}
}

def now(): return datetime.now(timezone.utc).isoformat(timespec="seconds")
def connect():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    return con

def init_db():
    with connect() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE COLLATE NOCASE, password_hash TEXT NOT NULL,
            grade TEXT NOT NULL CHECK(grade IN ('10','12')), stream TEXT DEFAULT '',
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER NOT NULL UNIQUE,
            name TEXT, email TEXT, grade TEXT, stream TEXT, goal TEXT, notes TEXT,
            created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
            FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER NOT NULL,
            grade TEXT NOT NULL, name TEXT, stream TEXT, goal TEXT,
            payload TEXT NOT NULL, result TEXT NOT NULL, created_at TEXT NOT NULL,
            FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS idx_assessments_student_grade ON assessments(student_id, grade, id DESC);
        """)
init_db()

def current_student():
    sid = session.get("student_id")
    if not sid: return None
    with connect() as con:
        row = con.execute("SELECT id,name,email,grade,stream FROM students WHERE id=?", (sid,)).fetchone()
    return dict(row) if row else None

def auth_required():
    student = current_student()
    if not student: return None, (jsonify({"error":"Please log in to continue.","code":"LOGIN_REQUIRED"}), 401)
    return student, None

def make_guidance(data):
    grade = str(data.get("grade", "10"))
    answers = data.get("answers") or {}
    interests = answers.get("interests") or []
    scores = answers.get("scores") or {}
    goal = (data.get("goal") or "").lower()
    stream = (data.get("stream") or "").lower()
    counts = {}
    for key in interests:
        if key in CAREER_DATA: counts[key] = counts.get(key, 0) + 3
    for score_key, key in [("logic","computer"),("math","ai"),("people","humanities"),("creative","design"),("biology","health"),("business","commerce"),("build","engineering"),("writing","law"),("data","ai")]:
        try: counts[key] = counts.get(key, 0) + max(0, int(scores.get(score_key, 0)))
        except (ValueError, TypeError): pass

    def add_goal(terms, ids):
        if any(term in goal for term in terms):
            for idx, key in enumerate(reversed(ids)):
                counts[key] = counts.get(key, 0) + (idx + 2)

    if grade == "10":
        # Class 10 is a stream-exploration result, not a post-Class-12 degree shortlist.
        add_goal(("engineering", "technology", "computer"), ["engineering", "computer", "ai"])
        add_goal(("medicine", "health", "biology"), ["health", "ai", "humanities"])
        add_goal(("commerce", "business", "finance"), ["commerce", "ai", "law"])
        add_goal(("law", "humanities", "psychology", "social"), ["humanities", "law", "design"])
        add_goal(("design", "creative", "art"), ["design", "humanities", "computer"])
        # No user goal: provide a varied exploration set, but score answers still influence order.
        fallback = ["engineering", "commerce", "humanities", "health", "design", "computer"]
        stage = "Class 10 exploration"
        intro = "These are career families to explore while comparing Class 11–12 subject streams. Your interests and answers influence the order; this is not a fixed stream decision."
    else:
        if "pcm" in stream or "mathematics" in stream:
            counts["engineering"] = counts.get("engineering", 0) + 3
            counts["computer"] = counts.get("computer", 0) + 2
            counts["ai"] = counts.get("ai", 0) + 2
        elif "pcb" in stream or "biology" in stream:
            counts["health"] = counts.get("health", 0) + 4
            counts["ai"] = counts.get("ai", 0) + 1
        elif "commerce" in stream:
            counts["commerce"] = counts.get("commerce", 0) + 4
            counts["law"] = counts.get("law", 0) + 1
        elif "humanities" in stream or "arts" in stream:
            counts["humanities"] = counts.get("humanities", 0) + 4
            counts["law"] = counts.get("law", 0) + 2
            counts["design"] = counts.get("design", 0) + 1
        add_goal(("engineering",), ["engineering", "computer", "ai"])
        add_goal(("computer", "software"), ["computer", "ai", "engineering"])
        add_goal(("ai", "data"), ["ai", "computer", "commerce"])
        add_goal(("medicine", "health"), ["health", "ai", "humanities"])
        add_goal(("commerce", "finance", "business"), ["commerce", "ai", "law"])
        add_goal(("law",), ["law", "humanities", "commerce"])
        add_goal(("design",), ["design", "computer", "humanities"])
        add_goal(("humanities", "psychology", "social sciences"), ["humanities", "law", "design"])
        fallback = ["computer", "commerce", "health", "law", "design", "humanities"]
        stage = "Class 12 course and career planning"
        intro = "These options are ranked using your stream, intended direction and assessment responses. Compare course eligibility and entrance requirements before deciding."

    ranked = sorted(counts, key=lambda k: (counts[k], k), reverse=True)
    for key in fallback:
        if key not in ranked: ranked.append(key)
    recommendations = []
    for key in ranked[:3]:
        item = dict(CAREER_DATA[key]); item.update({"id": key, "score": counts.get(key, 0)})
        if grade == "10":
            item["next_step"] = "Compare subject combinations and prerequisites for this field before selecting your Class 11–12 stream."
        else:
            item["next_step"] = "Compare degree routes, eligibility, entrance exams and course curricula for this field."
        recommendations.append(item)
    return {"assessment_id": None, "stage": stage, "interpretation": intro, "recommendations": recommendations}

@app.get("/")
def home(): return send_from_directory(BASE_DIR, "index.html")
@app.get("/api/health")
def health(): return jsonify({"ok": True, "service": "Career Compass API"})
@app.get("/api/me")
def me(): return jsonify({"student": current_student()})

@app.post("/api/register")
def register():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))
    grade = str(data.get("grade", ""))
    stream = str(data.get("stream", "")).strip()
    if len(name) < 2: return jsonify({"error":"Enter your full name."}), 400
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email): return jsonify({"error":"Enter a valid email address."}), 400
    if len(password) < 8: return jsonify({"error":"Password must be at least 8 characters."}), 400
    if grade not in ("10", "12"): return jsonify({"error":"Choose Class 10 or Class 12."}), 400
    with connect() as con:
        try:
            cur = con.execute("INSERT INTO students(name,email,password_hash,grade,stream,created_at) VALUES(?,?,?,?,?,?)", (name,email,generate_password_hash(password),grade,stream,now()))
            sid = cur.lastrowid
            con.execute("INSERT INTO profiles(student_id,name,email,grade,stream,goal,notes,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?)", (sid,name,email,grade,stream,"","{}",now(),now()))
        except sqlite3.IntegrityError:
            return jsonify({"error":"An account with this email already exists. Please log in."}), 409
    session.clear(); session["student_id"] = sid
    return jsonify({"ok":True,"student":{"id":sid,"name":name,"email":email,"grade":grade,"stream":stream}}), 201

@app.post("/api/login")
def login():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower(); password = str(data.get("password", ""))
    with connect() as con: row = con.execute("SELECT * FROM students WHERE email=? COLLATE NOCASE", (email,)).fetchone()
    if not row or not check_password_hash(row["password_hash"], password): return jsonify({"error":"Email or password is incorrect."}), 401
    session.clear(); session["student_id"] = row["id"]
    return jsonify({"ok":True,"student":{"id":row["id"],"name":row["name"],"email":row["email"],"grade":row["grade"],"stream":row["stream"]}})

@app.post("/api/logout")
def logout(): session.clear(); return jsonify({"ok":True})

@app.get("/api/careers")
def careers(): return jsonify([dict({"id": k}, **v) for k, v in CAREER_DATA.items()])

@app.post("/api/assess")
def assess():
    student, error = auth_required()
    if error: return error
    data = request.get_json(silent=True) or {}
    grade = str(data.get("grade", "10"))
    if grade not in ("10", "12"): return jsonify({"error":"grade must be 10 or 12"}), 400
    if grade != student["grade"]: return jsonify({"error":f"This account is registered for Class {student['grade']} only."}), 403
    data["name"] = student["name"]; data["grade"] = grade
    if grade == "12" and not data.get("stream"): data["stream"] = student.get("stream", "")
    result = make_guidance(data); timestamp = now()
    with connect() as con:
        cur = con.execute("INSERT INTO assessments(student_id,grade,name,stream,goal,payload,result,created_at) VALUES(?,?,?,?,?,?,?,?)", (student["id"],grade,student["name"],data.get("stream",""),data.get("goal",""),json.dumps(data,ensure_ascii=False),json.dumps(result,ensure_ascii=False),timestamp))
        result["assessment_id"] = cur.lastrowid
        con.execute("UPDATE assessments SET result=? WHERE id=?", (json.dumps(result,ensure_ascii=False),cur.lastrowid))
        con.execute("UPDATE profiles SET grade=?,stream=?,goal=?,updated_at=? WHERE student_id=?", (grade,data.get("stream",student.get("stream","")),data.get("goal",""),timestamp,student["id"]))
    return jsonify(result)

@app.post("/api/profile")
def save_profile():
    student, error = auth_required()
    if error: return error
    data = request.get_json(silent=True) or {}; grade = str(data.get("grade", student["grade"]))
    if grade != student["grade"]: return jsonify({"error":"You can only edit your own class profile."}), 403
    with connect() as con:
        con.execute("UPDATE profiles SET name=?,email=?,grade=?,stream=?,goal=?,notes=?,updated_at=? WHERE student_id=?", (student["name"],student["email"],grade,data.get("stream",student.get("stream","")),data.get("goal",""),data.get("notes","{}"),now(),student["id"]))
    return jsonify({"ok":True,"message":"Your profile has been saved."})

@app.get("/api/dashboard")
def dashboard():
    student, error = auth_required()
    if error: return error
    grade = request.args.get("grade", student["grade"])
    if grade not in ("10", "12"): return jsonify({"error":"grade must be 10 or 12"}), 400
    if grade != student["grade"]: return jsonify({"error":"This dashboard does not match your registered class."}), 403
    with connect() as con:
        profile = con.execute("SELECT name,email,grade,stream,goal,notes,created_at,updated_at FROM profiles WHERE student_id=?", (student["id"],)).fetchone()
        rows = con.execute("SELECT id,grade,stream,goal,result,created_at FROM assessments WHERE student_id=? AND grade=? ORDER BY id DESC LIMIT 20", (student["id"],grade)).fetchall()
    assessments = []
    for row in rows:
        result = json.loads(row["result"])
        assessments.append({"id":row["id"],"title":f"Class {grade} career guidance", "created_at":row["created_at"], "stream":row["stream"],"goal":row["goal"],"interpretation":result.get("interpretation",""),"recommendations":result.get("recommendations",[])})
    return jsonify({"grade":grade,"student":student,"profile":dict(profile) if profile else None,"assessments":assessments})

if __name__ == "__main__": app.run(host="127.0.0.1", port=int(os.environ.get("PORT",5000)), debug=False)
