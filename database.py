import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.db")

def get_db():
    """Establish and return a SQLite database connection with row access by column name."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    """Create all required tables for the Skill Link platform."""
    conn = get_db()
    cursor = conn.cursor()

    # Students Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        register_number TEXT UNIQUE NOT NULL,
        college_email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        department TEXT NOT NULL,
        year_of_study TEXT NOT NULL,
        section TEXT NOT NULL,
        skills_known TEXT NOT NULL,
        skills_interested TEXT NOT NULL,
        project_experience TEXT,
        certifications TEXT,
        bio TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Skill Exchange Requests Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS skill_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL,
        receiver_id INTEGER NOT NULL,
        offered_skill TEXT,
        wanted_skill TEXT,
        message TEXT,
        status TEXT DEFAULT 'Pending' CHECK(status IN ('Pending', 'Accepted', 'Rejected')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (sender_id) REFERENCES students(id) ON DELETE CASCADE,
        FOREIGN KEY (receiver_id) REFERENCES students(id) ON DELETE CASCADE
    );
    """)

    # Projects Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        required_skills TEXT NOT NULL,
        team_size INTEGER NOT NULL,
        category TEXT NOT NULL,
        status TEXT DEFAULT 'Open' CHECK(status IN ('Open', 'Closed')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (owner_id) REFERENCES students(id) ON DELETE CASCADE
    );
    """)

    # Project Applications Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS project_applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        applicant_id INTEGER NOT NULL,
        message TEXT,
        status TEXT DEFAULT 'Pending' CHECK(status IN ('Pending', 'Accepted', 'Rejected')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
        FOREIGN KEY (applicant_id) REFERENCES students(id) ON DELETE CASCADE
    );
    """)

    # Events and Hackathons Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        event_type TEXT NOT NULL CHECK(event_type IN ('Hackathon', 'Workshop', 'Seminar', 'Competition', 'College Event', 'Other')),
        event_date TEXT NOT NULL,
        registration_deadline TEXT NOT NULL,
        venue TEXT NOT NULL,
        registration_link TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    conn.close()
    print("Database initialized successfully.")

def seed_sample_data():
    """Seed initial sample students and projects if the database is fresh."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM students;")
    count = cursor.fetchone()[0]

    if count == 0:
        sample_students = [
            (
                "Aarav Sharma",
                "21CS101",
                "aarav.sharma@college.edu",
                generate_password_hash("Student@123"),
                "Computer Science and Engineering",
                "3rd Year",
                "A",
                "Python, Flask, SQLite, Machine Learning",
                "React, Cloud Computing, Docker",
                "Built an automated attendance system using OpenCV; 2 hackathons won.",
                "AWS Certified Cloud Practitioner, Python Institute PCAP",
                "Passionate about AI and backend development. Love to mentor juniors in Python."
            ),
            (
                "Priya Natarajan",
                "22IT204",
                "priya.n@college.edu",
                generate_password_hash("Student@123"),
                "Information Technology",
                "2nd Year",
                "B",
                "HTML, CSS, JavaScript, UI/UX Design, Figma",
                "Python, Node.js, REST APIs",
                "Designed redesign concepts for college portal; Winner of UI/UX Designathon 2025.",
                "Google UX Design Professional Certificate",
                "Frontend enthusiast with keen eye for responsive design and user experience."
            ),
            (
                "Rohan Verma",
                "20EC315",
                "rohan.verma@college.edu",
                generate_password_hash("Student@123"),
                "Electronics and Communication",
                "4th Year",
                "A",
                "Embedded C, Arduino, IoT, Robotics, Python",
                "Flask, WebSockets, Deep Learning",
                "Developed Smart Agriculture Soil Monitoring device with LoRaWAN.",
                "Cisco IoT Fundamentals Certificate",
                "Final year student working on smart hardware and IoT sensor gateways."
            ),
            (
                "Sneha Kulkarni",
                "23AI042",
                "sneha.k@college.edu",
                generate_password_hash("Student@123"),
                "Artificial Intelligence and Data Science",
                "1st Year",
                "C",
                "C++, Data Structures, Algorithms, Python",
                "Web Development, Machine Learning, Git & GitHub",
                "Solved 200+ problems on LeetCode; high school robotics team lead.",
                "HackerRank Problem Solving (Intermediate)",
                "Eager 1st year student looking to build full-stack project skills with seniors."
            ),
            (
                "Karthik Raja",
                "21ME112",
                "karthik.raja@college.edu",
                generate_password_hash("Student@123"),
                "Mechanical Engineering",
                "3rd Year",
                "B",
                "AutoCAD, SolidWorks, Python for Automation",
                "3D Printing Web Apps, Web Development",
                "Formula Student chassis designer; automated CAD parameterization script in Python.",
                "Certified SOLIDWORKS Associate (CSWA)",
                "Interdisciplinary builder looking for web devs to build a 3D model sharing hub."
            )
        ]

        cursor.executemany("""
        INSERT INTO students (
            full_name, register_number, college_email, password_hash,
            department, year_of_study, section, skills_known,
            skills_interested, project_experience, certifications, bio
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, sample_students)

        # Retrieve student IDs
        cursor.execute("SELECT id, full_name FROM students;")
        students_dict = {row["full_name"]: row["id"] for row in cursor.fetchall()}

        sample_projects = [
            (
                students_dict["Aarav Sharma"],
                "Smart Campus Navigation & Event Tracker",
                "An interactive web platform allowing college students and visitors to navigate campus buildings, find lecture halls, and track ongoing club events and seminars in real-time.",
                "Flask, Python, JavaScript, UI/UX, SQLite",
                4,
                "Web App",
                "Open"
            ),
            (
                students_dict["Priya Natarajan"],
                "EcoTrack: College Carbon Footprint Dashboard",
                "A gamified dashboard tracking department-wise paper and electricity savings with daily leaderboards and green badges for sustainability initiatives.",
                "HTML, CSS, JavaScript, Figma, Python",
                3,
                "Hackathon",
                "Open"
            ),
            (
                students_dict["Rohan Verma"],
                "IoT Smart Lab Automation & Equipment Booking",
                "Hardware + Web dashboard system enabling students to reserve lab test benches and monitor energy consumption using microcontrollers and web sockets.",
                "Embedded C, IoT, Python, Flask, Hardware",
                3,
                "IoT / Hardware",
                "Open"
            )
        ]

        cursor.executemany("""
        INSERT INTO projects (
            owner_id, title, description, required_skills, team_size, category, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?);
        """, sample_projects)

        # Fetch Aarav's project ID for sample application
        cursor.execute("SELECT id FROM projects WHERE title LIKE 'Smart Campus Navigation%';")
        proj_row = cursor.fetchone()
        if proj_row:
            proj_id = proj_row["id"]
            # Priya applied to Aarav's project
            cursor.execute("""
            INSERT INTO project_applications (project_id, applicant_id, message, status)
            VALUES (?, ?, ?, 'Pending');
            """, (proj_id, students_dict["Priya Natarajan"], "Hi Aarav! I'd love to lead UI/UX and frontend for this campus navigation project. Check out my Figma portfolio."))

        # Sample Skill Request: Priya sent a skill exchange request to Aarav
        cursor.execute("""
        INSERT INTO skill_requests (sender_id, receiver_id, offered_skill, wanted_skill, message, status)
        VALUES (?, ?, ?, ?, ?, 'Pending');
        """, (
            students_dict["Priya Natarajan"],
            students_dict["Aarav Sharma"],
            "UI/UX Design, Figma, Frontend",
            "Python, Flask Backend",
            "Hello Aarav! I saw your profile and would love to exchange my frontend design knowledge for Flask backend guidance."
        ))

        # Sample Skill Request: Rohan sent request to Sneha
        cursor.execute("""
        INSERT INTO skill_requests (sender_id, receiver_id, offered_skill, wanted_skill, message, status)
        VALUES (?, ?, ?, ?, ?, 'Accepted');
        """, (
            students_dict["Rohan Verma"],
            students_dict["Sneha Kulkarni"],
            "Python, IoT Automation",
            "Data Structures & C++ Algorithms",
            "Hey Sneha, let's practice DSA together for campus placements!"
        ))

        conn.commit()
        print("Sample data seeded successfully.")

    # Seed sample events if events table is empty
    cursor.execute("SELECT COUNT(*) FROM events;")
    events_count = cursor.fetchone()[0]
    if events_count == 0:
        sample_events = [
            (
                "HackIndia 2026: Inter-College 24Hr Hackathon",
                "Join over 500+ student developers to build AI, Web3, and IoT solutions solving real-world campus and social challenges. Exciting cash prizes, sponsor swags, and internship interviews for winners!",
                "Hackathon",
                "2026-12-10",
                "2026-12-05",
                "Campus Tech Auditorium & Innovation Center",
                "https://hackindia.example.edu/register"
            ),
            (
                "Hands-On Full-Stack Web Development Bootcamp",
                "A comprehensive 2-day hands-on workshop covering modern backend architecture with Flask, database design, REST APIs, and responsive frontend UI principles.",
                "Workshop",
                "2026-12-02",
                "2026-11-30",
                "Computer Science Lab 3, Block B",
                "https://events.example.edu/fullstack-bootcamp"
            ),
            (
                "AI & Generative Tech Seminar: Future of Tech",
                "Distinguished guest lecture by industry AI researchers on the state of LLMs, agentic workflows, and career opportunities for undergraduate engineers.",
                "Seminar",
                "2026-12-15",
                "2026-12-12",
                "Main Seminar Hall, Ground Floor",
                ""
            )
        ]
        cursor.executemany("""
        INSERT INTO events (
            title, description, event_type, event_date,
            registration_deadline, venue, registration_link
        ) VALUES (?, ?, ?, ?, ?, ?, ?);
        """, sample_events)
        conn.commit()
        print("Sample events seeded successfully.")

    conn.close()

if __name__ == "__main__":
    init_db()
    seed_sample_data()
