# Skill Link

A complete, responsive, full-stack college web platform built with **Python (Flask)**, **SQLite**, **HTML5**, **CSS3**, and **Vanilla JavaScript**. 

Skill Link connects college students across different departments (CSE, IT, AI&DS, ECE, EEE, Mechanical, Civil, etc.) to exchange knowledge, find peer study partners, form multidisciplinary teams for college hackathons and capstone projects, and discover official campus events.

---

## 🌟 Key Features

### 1. Clean, Professional Green & White Design
- Clean, responsive design optimized for desktop, laptops, tablets, Android mobile phones, and iPhones.
- Built using an Emerald Green (`#059669`, `#10b981`) and crisp White color scheme.
- Completely clean layout without repetitive taglines or clutter.

### 2. Single, Consistent Back Buttons
- Every secondary page (Student Register, Student Login, Admin Login, Student Profile, Skill Exchange, Projects, Requests, Events) includes exactly **ONE clean Back button**.
- Authenticated students return directly to their **Student Dashboard**.
- Guests return directly to the **Home Page**.
- No duplicate Back buttons anywhere on the platform.

### 3. Dedicated Student Experience (No "Home" after Login)
- Upon logging in as a student, the public "Home" navigation link is completely removed.
- The **Student Dashboard** serves as the central hub.
- Navigation includes:
  - **Dashboard**
  - **My Profile** (View & update skills, portfolio, bio, or change password)
  - **Skill Exchange** (Search peers by skill name, filter by department & year, send exchange requests)
  - **Projects & Hackathons** (Post project ideas, specify required skills and team size, apply to join peer projects)
  - **Events & Hackathons** (Explore upcoming hackathons, workshops, and seminars posted by administration)
  - **My Requests** (Track status and accept or decline incoming skill exchange requests and team applications)
  - Student Profile Badge and Logout

### 4. Clean Admin Portal & Events Management
- Once logged in, the admin dashboard heading displays cleanly as **Dashboard** (not "Admin Dashboard").
- The public "Home" navigation link is removed after login.
- No exposed security notes or credential reminders on the login page; authentication remains secure in the backend.
- **Events & Hackathons Management**:
  - Admin can publish new hackathons, workshops, seminars, and competitions.
  - Fields: Title, Event Type (Hackathon, Workshop, Seminar, Competition, College Event, Other), Description, Event Date, Registration Deadline, Venue, and Registration Link.
  - Admin can **Edit** existing event details using the integrated edit modal.
  - Admin can **Delete** events when concluded.
  - Events appear automatically on the student side for immediate discovery.
- Student account directory with search/filters and account deletion (with cascade removal).
- Project management with status toggle (Open/Closed).

---

## 📁 Project Structure

```text
Skill Link/
├── .env                     # Private environment configurations (Secret key & Admin credentials)
├── .env.example             # Template for environment configuration
├── .gitignore               # Excludes virtual envs, SQLite DB, and caches from git
├── app.py                   # Main Flask application with all routes, auth, and logic
├── database.db              # SQLite relational database (auto-created & persisted)
├── database.py              # SQLite connection helpers, schema creation & sample seeds
├── requirements.txt         # Python dependencies
├── test_app.py              # Comprehensive automated test suite (7 end-to-end tests)
├── README.md                # Complete documentation and review presentation guide
├── static/
│   ├── css/
│   │   └── style.css        # Responsive emerald green & white theme stylesheet
│   └── js/
│       └── script.js        # Mobile menu, modals, event editing, tabs controller, and form helpers
└── templates/
    ├── base.html            # Clean shared layout with navigation, notifications, and minimal footer
    ├── home.html            # Clean landing page with Student & Admin portal selector
    ├── student_register.html# Registration form + single Back to Home button
    ├── student_login.html   # Student login form + single Back to Home button
    ├── student_dashboard.html # Personalized student dashboard + upcoming events preview
    ├── profile.html         # View and update student profile & skills + single Back to Dashboard button
    ├── skill_exchange.html  # Search & filter students, send exchange requests + single Back to Dashboard button
    ├── projects.html        # Post project ideas, browse & apply to join teams + single Back to Dashboard button
    ├── student_events.html  # Student view for upcoming events & hackathons + single Back to Dashboard button
    ├── requests.html        # Manage sent/received skill requests & project applications + single Back to Dashboard button
    ├── admin_login.html     # Clean administrator login + single Back to Home button
    ├── admin_dashboard.html # Admin analytics, student management, and events management
    ├── 404.html             # Page not found template
    └── 500.html             # Server error template
```

---

## ⚙️ How to Run the Website on Windows

Follow these steps in **PowerShell**, **Command Prompt (cmd)**, or inside **VS Code**:

### Step 1: Open the Project Directory
```powershell
cd "c:\Users\Acer\Desktop\Skill Link"
```

### Step 2: (Optional but Recommended) Activate Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### Step 3: Install Required Dependencies
```powershell
python -m pip install -r requirements.txt
```

### Step 4: Run the Application
```powershell
python app.py
```

### Step 5: Open in Google Chrome
Visit:
```text
http://127.0.0.1:5000
```

---

## 🔑 Default Login Credentials for Testing

### 1. Admin Portal
- **URL**: `http://127.0.0.1:5000/admin/login`
- **Username**: `admin`
- **Password**: `admin@skilllink2026`

### 2. Sample Student Accounts (Pre-Seeded)
All seeded student accounts share the default test password: `Student@123`

| Full Name | College Email ID | Password | Department | Year & Sec | Key Skills |
|-----------|------------------|----------|------------|------------|------------|
| **Aarav Sharma** | `aarav.sharma@college.edu` | `Student@123` | CSE | 3rd Year (A) | Python, Flask, SQLite, Machine Learning |
| **Priya Natarajan** | `priya.n@college.edu` | `Student@123` | IT | 2nd Year (B) | HTML, CSS, JavaScript, UI/UX Design, Figma |
| **Rohan Verma** | `rohan.verma@college.edu` | `Student@123` | ECE | 4th Year (A) | Embedded C, Arduino, IoT, Robotics, Python |
| **Sneha Kulkarni** | `sneha.k@college.edu` | `Student@123` | AI & DS | 1st Year (C) | C++, Data Structures, Algorithms, Python |
| **Karthik Raja** | `karthik.raja@college.edu` | `Student@123` | Mechanical | 3rd Year (B) | AutoCAD, SolidWorks, Python for Automation |
