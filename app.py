import os
import re
from functools import wraps
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, session, g
)
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

import database

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "skill_link_college_platform_secret_key_2026")

# Admin credentials configured via environment variables
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin@skilllink2026")

# Standard Department and Academic Choices
DEPARTMENTS = [
    "Computer Science and Engineering",
    "Information Technology",
    "Artificial Intelligence and Data Science",
    "Electronics and Communication Engineering",
    "Electrical and Electronics Engineering",
    "Mechanical Engineering",
    "Civil Engineering",
    "Biomedical Engineering",
    "Chemical Engineering"
]

YEARS = ["1st Year", "2nd Year", "3rd Year", "4th Year"]
SECTIONS = ["A", "B", "C", "D"]
PROJECT_CATEGORIES = [
    "Hackathon",
    "Web App",
    "AI / Machine Learning",
    "Mobile App",
    "IoT / Hardware",
    "Data Science",
    "Cybersecurity",
    "Final Year Project",
    "Research & Open Source"
]

EVENT_TYPES = [
    "Hackathon",
    "Workshop",
    "Seminar",
    "Competition",
    "College Event",
    "Other"
]

# Database helper per request
def get_db():
    if "db" not in g:
        g.db = database.get_db()
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop("db", None)
    if db is not None:
        db.close()

# Initialize DB tables on startup
with app.app_context():
    database.init_db()
    database.seed_sample_data()

# Inject current student or admin into all templates
@app.context_processor
def inject_user_context():
    current_student = None
    if session.get("user_id"):
        db = get_db()
        current_student = db.execute(
            "SELECT * FROM students WHERE id = ?", (session["user_id"],)
        ).fetchone()
    
    return {
        "current_student": current_student,
        "is_admin": session.get("is_admin", False),
        "admin_user": session.get("admin_user", ""),
        "departments_list": DEPARTMENTS,
        "years_list": YEARS,
        "sections_list": SECTIONS,
        "categories_list": PROJECT_CATEGORIES,
        "event_types_list": EVENT_TYPES
    }

# Authentication Decorators
def student_login_required(view):
    """Ensure student is logged in."""
    @wraps(view)
    def wrapped_view(**kwargs):
        if not session.get("user_id"):
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("student_login"))
        return view(**kwargs)
    return wrapped_view

def admin_login_required(view):
    """Ensure admin is logged in."""
    @wraps(view)
    def wrapped_view(**kwargs):
        if not session.get("is_admin"):
            flash("Admin authentication required to access this area.", "warning")
            return redirect(url_for("admin_login"))
        return view(**kwargs)
    return wrapped_view

# -------------------------------------------------------------
# 1. HOME PAGE
# -------------------------------------------------------------
@app.route("/")
def home():
    """Render the Skill Link landing page."""
    db = get_db()
    stats = {
        "students": db.execute("SELECT COUNT(*) FROM students").fetchone()[0],
        "projects": db.execute("SELECT COUNT(*) FROM projects").fetchone()[0],
        "requests": db.execute("SELECT COUNT(*) FROM skill_requests").fetchone()[0]
    }
    return render_template("home.html", stats=stats)

# -------------------------------------------------------------
# 2. STUDENT REGISTRATION
# -------------------------------------------------------------
@app.route("/student/register", methods=["GET", "POST"])
def student_register():
    """Register a new student account."""
    if session.get("user_id"):
        return redirect(url_for("student_dashboard"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        register_number = request.form.get("register_number", "").strip().upper()
        college_email = request.form.get("college_email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        department = request.form.get("department", "").strip()
        year_of_study = request.form.get("year_of_study", "").strip()
        section = request.form.get("section", "").strip()
        skills_known = request.form.get("skills_known", "").strip()
        skills_interested = request.form.get("skills_interested", "").strip()
        project_experience = request.form.get("project_experience", "").strip()
        certifications = request.form.get("certifications", "").strip()
        bio = request.form.get("bio", "").strip()

        # Validation
        errors = []
        if not full_name:
            errors.append("Full Name is required.")
        if not register_number:
            errors.append("Register Number is required.")
        if not college_email:
            errors.append("College Email ID is required.")
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", college_email):
            errors.append("Please enter a valid College Email ID.")
        if not password:
            errors.append("Password is required.")
        elif len(password) < 6:
            errors.append("Password must be at least 6 characters long.")
        if password != confirm_password:
            errors.append("Password and Confirm Password do not match.")
        if not department:
            errors.append("Please select your Department.")
        if not year_of_study:
            errors.append("Please select your Year of Study.")
        if not section:
            errors.append("Please select your Section.")
        if not skills_known:
            errors.append("Please enter at least one skill you know.")
        if not skills_interested:
            errors.append("Please enter skills you are interested in learning.")

        db = get_db()
        # Check uniqueness of Register Number
        if not errors:
            existing_reg = db.execute(
                "SELECT id FROM students WHERE register_number = ?", (register_number,)
            ).fetchone()
            if existing_reg:
                errors.append(f"Register Number '{register_number}' is already registered.")

        # Check uniqueness of College Email
        if not errors:
            existing_email = db.execute(
                "SELECT id FROM students WHERE college_email = ?", (college_email,)
            ).fetchone()
            if existing_email:
                errors.append(f"College Email '{college_email}' is already registered.")

        if errors:
            for err in errors:
                flash(err, "danger")
            return render_template(
                "student_register.html",
                form_data=request.form
            )

        # Hash password and insert into SQLite database
        password_hash = generate_password_hash(password)
        db.execute("""
            INSERT INTO students (
                full_name, register_number, college_email, password_hash,
                department, year_of_study, section, skills_known,
                skills_interested, project_experience, certifications, bio
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            full_name, register_number, college_email, password_hash,
            department, year_of_study, section, skills_known,
            skills_interested, project_experience, certifications, bio
        ))
        db.commit()

        flash("Registration successful! You can now log in with your college email.", "success")
        return redirect(url_for("student_login"))

    return render_template("student_register.html", form_data={})

# -------------------------------------------------------------
# 3. STUDENT LOGIN & LOGOUT
# -------------------------------------------------------------
@app.route("/student/login", methods=["GET", "POST"])
def student_login():
    """Authenticate registered student."""
    if session.get("user_id"):
        return redirect(url_for("student_dashboard"))

    if request.method == "POST":
        college_email = request.form.get("college_email", "").strip().lower()
        password = request.form.get("password", "")

        if not college_email or not password:
            flash("Please enter both College Email ID and Password.", "danger")
            return render_template("student_login.html", college_email=college_email)

        db = get_db()
        student = db.execute(
            "SELECT * FROM students WHERE college_email = ?", (college_email,)
        ).fetchone()

        if student and check_password_hash(student["password_hash"], password):
            session.clear()
            session["user_id"] = student["id"]
            session["user_name"] = student["full_name"]
            session["user_role"] = "student"
            flash(f"Welcome back, {student['full_name']}!", "success")
            return redirect(url_for("student_dashboard"))
        else:
            flash("Invalid College Email ID or Password. Please try again.", "danger")

    return render_template("student_login.html")

@app.route("/student/logout")
def student_logout():
    """Log out student."""
    session.clear()
    flash("You have been successfully logged out.", "info")
    return redirect(url_for("student_login"))

# -------------------------------------------------------------
# 4. STUDENT DASHBOARD
# -------------------------------------------------------------
@app.route("/student/dashboard")
@student_login_required
def student_dashboard():
    """Display personalized student dashboard."""
    student_id = session["user_id"]
    db = get_db()

    student = db.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    if not student:
        session.clear()
        flash("Student account not found.", "warning")
        return redirect(url_for("student_login"))

    # Summary counts
    received_requests_count = db.execute(
        "SELECT COUNT(*) FROM skill_requests WHERE receiver_id = ? AND status = 'Pending'",
        (student_id,)
    ).fetchone()[0]

    sent_requests_count = db.execute(
        "SELECT COUNT(*) FROM skill_requests WHERE sender_id = ?",
        (student_id,)
    ).fetchone()[0]

    my_projects_count = db.execute(
        "SELECT COUNT(*) FROM projects WHERE owner_id = ?",
        (student_id,)
    ).fetchone()[0]

    my_applications_count = db.execute(
        "SELECT COUNT(*) FROM project_applications WHERE applicant_id = ?",
        (student_id,)
    ).fetchone()[0]

    events_count = db.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    upcoming_events = db.execute("SELECT * FROM events ORDER BY event_date ASC LIMIT 3").fetchall()

    # Recent skill requests
    recent_requests = db.execute("""
        SELECT sr.*, s.full_name as sender_name, s.department as sender_dept
        FROM skill_requests sr
        JOIN students s ON sr.sender_id = s.id
        WHERE sr.receiver_id = ?
        ORDER BY sr.created_at DESC LIMIT 3
    """, (student_id,)).fetchall()

    # Recommended peers matching student's learning interests
    learning_terms = [t.strip().lower() for t in student["skills_interested"].split(",") if t.strip()]
    suggested_peers = []
    if learning_terms:
        # Simple match against peers' skills known
        query = "SELECT * FROM students WHERE id != ?"
        all_peers = db.execute(query, (student_id,)).fetchall()
        for peer in all_peers:
            peer_skills = peer["skills_known"].lower()
            if any(term in peer_skills for term in learning_terms):
                suggested_peers.append(peer)
            if len(suggested_peers) >= 3:
                break
    if not suggested_peers:
        suggested_peers = db.execute(
            "SELECT * FROM students WHERE id != ? ORDER BY id DESC LIMIT 3",
            (student_id,)
        ).fetchall()

    # Latest projects posted across the campus
    latest_projects = db.execute("""
        SELECT p.*, s.full_name as owner_name, s.department as owner_dept
        FROM projects p
        JOIN students s ON p.owner_id = s.id
        WHERE p.status = 'Open' AND p.owner_id != ?
        ORDER BY p.created_at DESC LIMIT 3
    """, (student_id,)).fetchall()

    return render_template(
        "student_dashboard.html",
        student=student,
        stats={
            "pending_requests": received_requests_count,
            "sent_requests": sent_requests_count,
            "my_projects": my_projects_count,
            "my_applications": my_applications_count,
            "events_count": events_count
        },
        recent_requests=recent_requests,
        suggested_peers=suggested_peers,
        latest_projects=latest_projects,
        upcoming_events=upcoming_events
    )

# -------------------------------------------------------------
# 4A. MY PROFILE
# -------------------------------------------------------------
@app.route("/student/profile", methods=["GET", "POST"])
@student_login_required
def student_profile():
    """View and update student profile."""
    student_id = session["user_id"]
    db = get_db()
    student = db.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        department = request.form.get("department", "").strip()
        year_of_study = request.form.get("year_of_study", "").strip()
        section = request.form.get("section", "").strip()
        skills_known = request.form.get("skills_known", "").strip()
        skills_interested = request.form.get("skills_interested", "").strip()
        project_experience = request.form.get("project_experience", "").strip()
        certifications = request.form.get("certifications", "").strip()
        bio = request.form.get("bio", "").strip()

        # Optional password change
        current_password = request.form.get("current_password", "")
        new_password = request.form.get("new_password", "")
        confirm_new_password = request.form.get("confirm_new_password", "")

        errors = []
        if not full_name:
            errors.append("Full Name cannot be empty.")
        if not department:
            errors.append("Department cannot be empty.")
        if not year_of_study:
            errors.append("Year of Study cannot be empty.")
        if not section:
            errors.append("Section cannot be empty.")
        if not skills_known:
            errors.append("Skills Known cannot be empty.")
        if not skills_interested:
            errors.append("Skills Interested cannot be empty.")

        if new_password:
            if not current_password:
                errors.append("Please enter your current password to set a new password.")
            elif not check_password_hash(student["password_hash"], current_password):
                errors.append("Current password is incorrect.")
            elif len(new_password) < 6:
                errors.append("New password must be at least 6 characters long.")
            elif new_password != confirm_new_password:
                errors.append("New password and confirmation do not match.")

        if errors:
            for err in errors:
                flash(err, "danger")
            return render_template("profile.html", student=student)

        # Update profile
        if new_password:
            new_hash = generate_password_hash(new_password)
            db.execute("""
                UPDATE students SET
                    full_name = ?, department = ?, year_of_study = ?, section = ?,
                    skills_known = ?, skills_interested = ?, project_experience = ?,
                    certifications = ?, bio = ?, password_hash = ?
                WHERE id = ?
            """, (
                full_name, department, year_of_study, section,
                skills_known, skills_interested, project_experience,
                certifications, bio, new_hash, student_id
            ))
        else:
            db.execute("""
                UPDATE students SET
                    full_name = ?, department = ?, year_of_study = ?, section = ?,
                    skills_known = ?, skills_interested = ?, project_experience = ?,
                    certifications = ?, bio = ?
                WHERE id = ?
            """, (
                full_name, department, year_of_study, section,
                skills_known, skills_interested, project_experience,
                certifications, bio, student_id
            ))
        
        db.commit()
        session["user_name"] = full_name
        flash("Your profile has been updated successfully!", "success")
        return redirect(url_for("student_profile"))

    return render_template("profile.html", student=student)

# -------------------------------------------------------------
# 4B. SKILL EXCHANGE
# -------------------------------------------------------------
@app.route("/student/skill-exchange")
@student_login_required
def skill_exchange():
    """Browse student skills with search and filters, and send exchange requests."""
    student_id = session["user_id"]
    db = get_db()

    query = request.args.get("q", "").strip()
    selected_dept = request.args.get("department", "").strip()
    selected_year = request.args.get("year", "").strip()

    sql = "SELECT * FROM students WHERE id != ?"
    params = [student_id]

    if query:
        sql += " AND (skills_known LIKE ? OR skills_interested LIKE ? OR full_name LIKE ?)"
        wildcard = f"%{query}%"
        params.extend([wildcard, wildcard, wildcard])

    if selected_dept:
        sql += " AND department = ?"
        params.append(selected_dept)

    if selected_year:
        sql += " AND year_of_study = ?"
        params.append(selected_year)

    sql += " ORDER BY full_name ASC"
    peers = db.execute(sql, params).fetchall()

    # Track existing requests sent to peers so button can show "Request Sent"
    sent_requests_raw = db.execute(
        "SELECT receiver_id, status FROM skill_requests WHERE sender_id = ?",
        (student_id,)
    ).fetchall()
    sent_map = {row["receiver_id"]: row["status"] for row in sent_requests_raw}

    return render_template(
        "skill_exchange.html",
        peers=peers,
        query=query,
        selected_dept=selected_dept,
        selected_year=selected_year,
        sent_map=sent_map
    )

@app.route("/student/skill-exchange/request", methods=["POST"])
@student_login_required
def send_skill_request():
    """Handle sending a skill exchange request to a peer."""
    sender_id = session["user_id"]
    receiver_id = request.form.get("receiver_id", type=int)
    offered_skill = request.form.get("offered_skill", "").strip()
    wanted_skill = request.form.get("wanted_skill", "").strip()
    message = request.form.get("message", "").strip()

    if not receiver_id or sender_id == receiver_id:
        flash("Invalid recipient for skill exchange.", "danger")
        return redirect(url_for("skill_exchange"))

    db = get_db()
    # Check if target student exists
    target = db.execute("SELECT full_name FROM students WHERE id = ?", (receiver_id,)).fetchone()
    if not target:
        flash("The selected student does not exist.", "danger")
        return redirect(url_for("skill_exchange"))

    # Check for existing pending request
    existing = db.execute("""
        SELECT id, status FROM skill_requests
        WHERE sender_id = ? AND receiver_id = ? AND status = 'Pending'
    """, (sender_id, receiver_id)).fetchone()

    if existing:
        flash(f"You already have a pending skill exchange request with {target['full_name']}.", "info")
        return redirect(url_for("skill_exchange"))

    db.execute("""
        INSERT INTO skill_requests (sender_id, receiver_id, offered_skill, wanted_skill, message, status)
        VALUES (?, ?, ?, ?, ?, 'Pending')
    """, (sender_id, receiver_id, offered_skill, wanted_skill, message))
    db.commit()

    flash(f"Skill exchange request sent to {target['full_name']} successfully!", "success")
    return redirect(url_for("skill_exchange"))

# -------------------------------------------------------------
# 4C. HACKATHON AND PROJECT COLLABORATION
# -------------------------------------------------------------
@app.route("/student/projects")
@student_login_required
def projects():
    """Browse hackathon and project collaboration posts with filters."""
    student_id = session["user_id"]
    db = get_db()

    query = request.args.get("q", "").strip()
    selected_category = request.args.get("category", "").strip()

    sql = """
        SELECT p.*, s.full_name as owner_name, s.department as owner_dept,
               s.year_of_study as owner_year, s.college_email as owner_email,
               (SELECT COUNT(*) FROM project_applications WHERE project_id = p.id) as app_count
        FROM projects p
        JOIN students s ON p.owner_id = s.id
        WHERE 1=1
    """
    params = []

    if query:
        sql += " AND (p.title LIKE ? OR p.required_skills LIKE ? OR p.description LIKE ?)"
        wildcard = f"%{query}%"
        params.extend([wildcard, wildcard, wildcard])

    if selected_category:
        sql += " AND p.category = ?"
        params.append(selected_category)

    sql += " ORDER BY p.created_at DESC"
    all_projects = db.execute(sql, params).fetchall()

    # Track projects applied to by current student
    my_applications_raw = db.execute(
        "SELECT project_id, status FROM project_applications WHERE applicant_id = ?",
        (student_id,)
    ).fetchall()
    applied_map = {row["project_id"]: row["status"] for row in my_applications_raw}

    return render_template(
        "projects.html",
        projects=all_projects,
        query=query,
        selected_category=selected_category,
        applied_map=applied_map
    )

@app.route("/student/projects/create", methods=["POST"])
@student_login_required
def create_project():
    """Post a new project / hackathon idea."""
    owner_id = session["user_id"]
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    required_skills = request.form.get("required_skills", "").strip()
    team_size = request.form.get("team_size", type=int) or 3
    category = request.form.get("category", "").strip()

    if not title or not description or not required_skills or not category:
        flash("Please fill in all required fields to post a project.", "danger")
        return redirect(url_for("projects"))

    db = get_db()
    db.execute("""
        INSERT INTO projects (owner_id, title, description, required_skills, team_size, category, status)
        VALUES (?, ?, ?, ?, ?, ?, 'Open')
    """, (owner_id, title, description, required_skills, team_size, category))
    db.commit()

    flash("Your project idea has been posted successfully!", "success")
    return redirect(url_for("projects"))

@app.route("/student/projects/apply", methods=["POST"])
@student_login_required
def apply_project():
    """Apply to join a posted project / hackathon team."""
    applicant_id = session["user_id"]
    project_id = request.form.get("project_id", type=int)
    message = request.form.get("message", "").strip()

    if not project_id:
        flash("Invalid project selection.", "danger")
        return redirect(url_for("projects"))

    db = get_db()
    project = db.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    if not project:
        flash("Project not found.", "danger")
        return redirect(url_for("projects"))

    if project["owner_id"] == applicant_id:
        flash("You cannot apply to your own project.", "warning")
        return redirect(url_for("projects"))

    # Check if already applied
    existing = db.execute("""
        SELECT id, status FROM project_applications
        WHERE project_id = ? AND applicant_id = ?
    """, (project_id, applicant_id)).fetchone()

    if existing:
        flash(f"You have already submitted an application for this project (Status: {existing['status']}).", "info")
        return redirect(url_for("projects"))

    db.execute("""
        INSERT INTO project_applications (project_id, applicant_id, message, status)
        VALUES (?, ?, ?, 'Pending')
    """, (project_id, applicant_id, message))
    db.commit()

    flash("Your application to join the team has been submitted to the project owner!", "success")
    return redirect(url_for("projects"))

# -------------------------------------------------------------
# 4D. MY REQUESTS AND APPLICATIONS
# -------------------------------------------------------------
@app.route("/student/requests")
@student_login_required
def requests_page():
    """View sent and received skill requests and project applications."""
    student_id = session["user_id"]
    db = get_db()

    # 1. Received Skill Requests
    received_skill_requests = db.execute("""
        SELECT sr.*, s.full_name as sender_name, s.register_number as sender_reg,
               s.department as sender_dept, s.year_of_study as sender_year,
               s.college_email as sender_email, s.skills_known as sender_skills
        FROM skill_requests sr
        JOIN students s ON sr.sender_id = s.id
        WHERE sr.receiver_id = ?
        ORDER BY sr.created_at DESC
    """, (student_id,)).fetchall()

    # 2. Sent Skill Requests
    sent_skill_requests = db.execute("""
        SELECT sr.*, s.full_name as receiver_name, s.register_number as receiver_reg,
               s.department as receiver_dept, s.year_of_study as receiver_year,
               s.college_email as receiver_email
        FROM skill_requests sr
        JOIN students s ON sr.receiver_id = s.id
        WHERE sr.sender_id = ?
        ORDER BY sr.created_at DESC
    """, (student_id,)).fetchall()

    # 3. Project Applications Received (for projects owned by student)
    received_project_apps = db.execute("""
        SELECT pa.*, p.title as project_title, p.category as project_category,
               s.full_name as applicant_name, s.register_number as applicant_reg,
               s.department as applicant_dept, s.year_of_study as applicant_year,
               s.college_email as applicant_email, s.skills_known as applicant_skills
        FROM project_applications pa
        JOIN projects p ON pa.project_id = p.id
        JOIN students s ON pa.applicant_id = s.id
        WHERE p.owner_id = ?
        ORDER BY pa.created_at DESC
    """, (student_id,)).fetchall()

    # 4. Project Applications Sent by student
    sent_project_apps = db.execute("""
        SELECT pa.*, p.title as project_title, p.category as project_category,
               p.status as project_status, s.full_name as owner_name,
               s.college_email as owner_email, s.department as owner_dept
        FROM project_applications pa
        JOIN projects p ON pa.project_id = p.id
        JOIN students s ON p.owner_id = s.id
        WHERE pa.applicant_id = ?
        ORDER BY pa.created_at DESC
    """, (student_id,)).fetchall()

    return render_template(
        "requests.html",
        received_skill_requests=received_skill_requests,
        sent_skill_requests=sent_skill_requests,
        received_project_apps=received_project_apps,
        sent_project_apps=sent_project_apps
    )

@app.route("/student/requests/respond-skill", methods=["POST"])
@student_login_required
def respond_skill_request():
    """Accept or reject incoming skill exchange request."""
    student_id = session["user_id"]
    request_id = request.form.get("request_id", type=int)
    action = request.form.get("action", "").strip().lower()

    if action not in ["accept", "reject"]:
        flash("Invalid action.", "danger")
        return redirect(url_for("requests_page"))

    new_status = "Accepted" if action == "accept" else "Rejected"
    db = get_db()

    result = db.execute("""
        UPDATE skill_requests
        SET status = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND receiver_id = ?
    """, (new_status, request_id, student_id))
    db.commit()

    if result.rowcount > 0:
        flash(f"Skill exchange request has been {new_status.lower()}.", "success")
    else:
        flash("Request not found or unauthorized.", "danger")

    return redirect(url_for("requests_page"))

@app.route("/student/requests/respond-project", methods=["POST"])
@student_login_required
def respond_project_app():
    """Accept or reject incoming project collaboration application."""
    student_id = session["user_id"]
    app_id = request.form.get("app_id", type=int)
    action = request.form.get("action", "").strip().lower()

    if action not in ["accept", "reject"]:
        flash("Invalid action.", "danger")
        return redirect(url_for("requests_page"))

    new_status = "Accepted" if action == "accept" else "Rejected"
    db = get_db()

    # Verify that the current student owns the project
    app_record = db.execute("""
        SELECT pa.id FROM project_applications pa
        JOIN projects p ON pa.project_id = p.id
        WHERE pa.id = ? AND p.owner_id = ?
    """, (app_id, student_id)).fetchone()

    if not app_record:
        flash("Application not found or unauthorized.", "danger")
        return redirect(url_for("requests_page"))

    db.execute("""
        UPDATE project_applications
        SET status = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (new_status, app_id))
    db.commit()

    flash(f"Project application has been {new_status.lower()}.", "success")
    return redirect(url_for("requests_page"))

# -------------------------------------------------------------
# 4E. STUDENT EVENTS AND HACKATHONS
# -------------------------------------------------------------
@app.route("/student/events")
@student_login_required
def student_events():
    """View upcoming events and hackathons posted by college administration."""
    db = get_db()
    query = request.args.get("q", "").strip()
    selected_type = request.args.get("type", "").strip()

    sql = "SELECT * FROM events WHERE 1=1"
    params = []

    if query:
        sql += " AND (title LIKE ? OR description LIKE ? OR venue LIKE ?)"
        wildcard = f"%{query}%"
        params.extend([wildcard, wildcard, wildcard])

    if selected_type:
        sql += " AND event_type = ?"
        params.append(selected_type)

    sql += " ORDER BY event_date ASC"
    events_list = db.execute(sql, params).fetchall()

    return render_template(
        "student_events.html",
        events=events_list,
        query=query,
        selected_type=selected_type
    )

# -------------------------------------------------------------
# 5. ADMIN LOGIN & LOGOUT
# -------------------------------------------------------------
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    """Authenticate administrator using secure environment credentials."""
    if session.get("is_admin"):
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session.clear()
            session["is_admin"] = True
            session["admin_user"] = username
            session["user_role"] = "admin"
            flash("Logged in successfully as Administrator.", "success")
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid Admin username or password. Check environment configuration.", "danger")

    return render_template("admin_login.html")

@app.route("/admin/logout")
def admin_logout():
    """Log out administrator."""
    session.clear()
    flash("Admin logged out successfully.", "info")
    return redirect(url_for("admin_login"))

# -------------------------------------------------------------
# 6. ADMIN DASHBOARD
# -------------------------------------------------------------
@app.route("/admin/dashboard")
@admin_login_required
def admin_dashboard():
    """Display comprehensive administrator dashboard."""
    db = get_db()

    # Filters
    search_query = request.args.get("q", "").strip()
    selected_dept = request.args.get("department", "").strip()
    selected_year = request.args.get("year", "").strip()

    # Overall system metrics
    total_students = db.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    total_projects = db.execute("SELECT COUNT(*) FROM projects").fetchone()[0]
    total_skill_reqs = db.execute("SELECT COUNT(*) FROM skill_requests").fetchone()[0]
    total_project_apps = db.execute("SELECT COUNT(*) FROM project_applications").fetchone()[0]

    # Query Students with filters
    student_sql = "SELECT * FROM students WHERE 1=1"
    student_params = []
    if search_query:
        student_sql += " AND (full_name LIKE ? OR register_number LIKE ? OR college_email LIKE ? OR skills_known LIKE ?)"
        wildcard = f"%{search_query}%"
        student_params.extend([wildcard, wildcard, wildcard, wildcard])

    if selected_dept:
        student_sql += " AND department = ?"
        student_params.append(selected_dept)

    if selected_year:
        student_sql += " AND year_of_study = ?"
        student_params.append(selected_year)

    student_sql += " ORDER BY id DESC"
    students = db.execute(student_sql, student_params).fetchall()

    # All Skill Exchange Requests with participant names
    skill_requests = db.execute("""
        SELECT sr.*, s1.full_name as sender_name, s1.register_number as sender_reg,
               s2.full_name as receiver_name, s2.register_number as receiver_reg
        FROM skill_requests sr
        JOIN students s1 ON sr.sender_id = s1.id
        JOIN students s2 ON sr.receiver_id = s2.id
        ORDER BY sr.created_at DESC LIMIT 50
    """).fetchall()

    # All Projects with owner info and application counts
    projects = db.execute("""
        SELECT p.*, s.full_name as owner_name, s.register_number as owner_reg,
               (SELECT COUNT(*) FROM project_applications WHERE project_id = p.id) as total_apps
        FROM projects p
        JOIN students s ON p.owner_id = s.id
        ORDER BY p.created_at DESC LIMIT 50
    """).fetchall()

    # Aggregated Skills List
    all_skills_rows = db.execute("SELECT skills_known FROM students").fetchall()
    skill_set = set()
    for row in all_skills_rows:
        for skill in row["skills_known"].split(","):
            s_clean = skill.strip()
            if s_clean:
                skill_set.add(s_clean)
    available_skills = sorted(list(skill_set))

    # All Events and Hackathons
    events = db.execute("SELECT * FROM events ORDER BY event_date ASC").fetchall()
    total_events = len(events)

    return render_template(
        "admin_dashboard.html",
        stats={
            "students": total_students,
            "projects": total_projects,
            "skill_requests": total_skill_reqs,
            "project_applications": total_project_apps,
            "skills_count": len(available_skills),
            "events_count": total_events
        },
        students=students,
        skill_requests=skill_requests,
        projects=projects,
        events=events,
        available_skills=available_skills,
        search_query=search_query,
        selected_dept=selected_dept,
        selected_year=selected_year
    )

@app.route("/admin/student/delete/<int:student_id>", methods=["POST"])
@admin_login_required
def admin_delete_student(student_id):
    """Delete a student account and cascade-delete associated requests/projects."""
    db = get_db()
    student = db.execute("SELECT full_name FROM students WHERE id = ?", (student_id,)).fetchone()
    if student:
        db.execute("DELETE FROM students WHERE id = ?", (student_id,))
        db.commit()
        flash(f"Student account '{student['full_name']}' has been deleted.", "success")
    else:
        flash("Student account not found.", "warning")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/project/toggle-status/<int:project_id>", methods=["POST"])
@admin_login_required
def admin_toggle_project_status(project_id):
    """Toggle a project between Open and Closed status."""
    db = get_db()
    project = db.execute("SELECT status FROM projects WHERE id = ?", (project_id,)).fetchone()
    if project:
        new_status = "Closed" if project["status"] == "Open" else "Open"
        db.execute("UPDATE projects SET status = ? WHERE id = ?", (new_status, project_id))
        db.commit()
        flash(f"Project status changed to '{new_status}'.", "success")
    return redirect(url_for("admin_dashboard"))

# -------------------------------------------------------------
# 6A. ADMIN EVENTS & HACKATHONS MANAGEMENT
# -------------------------------------------------------------
@app.route("/admin/events/create", methods=["POST"])
@admin_login_required
def admin_create_event():
    """Publish a new college event or hackathon."""
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    event_type = request.form.get("event_type", "").strip()
    event_date = request.form.get("event_date", "").strip()
    registration_deadline = request.form.get("registration_deadline", "").strip()
    venue = request.form.get("venue", "").strip()
    registration_link = request.form.get("registration_link", "").strip()

    if not title or not description or not event_type or not event_date or not registration_deadline or not venue:
        flash("Please fill in all required fields to publish an event.", "danger")
        return redirect(url_for("admin_dashboard"))

    db = get_db()
    db.execute("""
        INSERT INTO events (title, description, event_type, event_date, registration_deadline, venue, registration_link)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (title, description, event_type, event_date, registration_deadline, venue, registration_link))
    db.commit()

    flash(f"Event '{title}' published successfully!", "success")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/events/edit/<int:event_id>", methods=["POST"])
@admin_login_required
def admin_edit_event(event_id):
    """Edit existing college event or hackathon details."""
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    event_type = request.form.get("event_type", "").strip()
    event_date = request.form.get("event_date", "").strip()
    registration_deadline = request.form.get("registration_deadline", "").strip()
    venue = request.form.get("venue", "").strip()
    registration_link = request.form.get("registration_link", "").strip()

    if not title or not description or not event_type or not event_date or not registration_deadline or not venue:
        flash("Please fill in all required fields to update the event.", "danger")
        return redirect(url_for("admin_dashboard"))

    db = get_db()
    db.execute("""
        UPDATE events
        SET title = ?, description = ?, event_type = ?, event_date = ?,
            registration_deadline = ?, venue = ?, registration_link = ?
        WHERE id = ?
    """, (title, description, event_type, event_date, registration_deadline, venue, registration_link, event_id))
    db.commit()

    flash(f"Event '{title}' updated successfully!", "success")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/events/delete/<int:event_id>", methods=["POST"])
@admin_login_required
def admin_delete_event(event_id):
    """Delete an event from the platform."""
    db = get_db()
    event = db.execute("SELECT title FROM events WHERE id = ?", (event_id,)).fetchone()
    if event:
        db.execute("DELETE FROM events WHERE id = ?", (event_id,))
        db.commit()
        flash(f"Event '{event['title']}' deleted successfully.", "success")
    else:
        flash("Event not found.", "warning")
    return redirect(url_for("admin_dashboard"))

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500

if __name__ == "__main__":
    # Run development server on port 5000
    print("Starting Skill Link College Platform...")
    print(f"Admin Credentials: {ADMIN_USERNAME} / (set in .env)")
    app.run(debug=True, host="127.0.0.1", port=5000)
