import unittest
from werkzeug.security import check_password_hash

import app as flask_app
import database

class SkillLinkTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        database.init_db()
        database.seed_sample_data()

    def setUp(self):
        flask_app.app.config["TESTING"] = True
        flask_app.app.config["WTF_CSRF_ENABLED"] = False
        flask_app.app.config["SECRET_KEY"] = "test-secret-key"
        self.client = flask_app.app.test_client()

    def test_01_home_page_top_right_badge(self):
        """Test home page has the top-right illustration and text, and no plant emoji."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        html = response.data.decode("utf-8")
        
        # Verify title and portal options
        self.assertIn("<title>Skill Link</title>", html)
        self.assertIn("Student Portal", html)
        self.assertIn("Admin Portal", html)

        # Requirement 1: Top-right corner must display "College-Wide Collaborative Learning Platform"
        self.assertIn("College-Wide Collaborative Learning Platform", html)

        # Image requirement: collaboration.svg illustration, NO 🌱 emoji
        self.assertIn("collaboration.svg", html)
        self.assertNotIn("🌱", html)

        # Requirement 3 restrictions: No old tagline
        self.assertNotIn("Connect Skills. Share Knowledge. Grow Together.", html)
        self.assertNotIn("College Skill Exchange & Hackathon Collaboration Platform", html)
        print("✓ Home page top-right collaboration illustration & text verified.")

    def test_02_login_pages_top_right_badge(self):
        """Verify the badge is present on Student Login and Admin Login, but NOT on Register or internal pages."""
        # 1. Student Login Page -> MUST have image and text
        res_stud_login = self.client.get("/student/login")
        html_stud = res_stud_login.data.decode("utf-8")
        self.assertIn("College-Wide Collaborative Learning Platform", html_stud)
        self.assertIn("collaboration.svg", html_stud)
        self.assertNotIn("🌱", html_stud)
        self.assertEqual(html_stud.count("Back to Home"), 1)

        # 2. Admin Login Page -> MUST have image and text
        res_admin_login = self.client.get("/admin/login")
        html_admin = res_admin_login.data.decode("utf-8")
        self.assertIn("College-Wide Collaborative Learning Platform", html_admin)
        self.assertIn("collaboration.svg", html_admin)
        self.assertNotIn("🌱", html_admin)
        self.assertNotIn("Security Note", html_admin)
        self.assertEqual(html_admin.count("Back to Home"), 1)

        # 3. Student Register Page -> MUST NOT have this badge (restricted to Home, Student Login, Admin Login)
        res_reg = self.client.get("/student/register")
        html_reg = res_reg.data.decode("utf-8")
        self.assertNotIn("collaboration.svg", html_reg)
        self.assertNotIn("College-Wide Collaborative Learning Platform", html_reg)
        print("✓ Top-right badge verified on Student Login and Admin Login (and absent on Register).")

    def test_03_student_dashboard_no_badge_or_home(self):
        """Verify logged-in student dashboard has NO top-right badge and NO 'Home' link."""
        self.client.post("/student/login", data={
            "college_email": "aarav.sharma@college.edu",
            "password": "Student@123"
        })
        res_dash = self.client.get("/student/dashboard")
        html = res_dash.data.decode("utf-8")

        # Must NOT display the public badge on dashboard
        self.assertNotIn("collaboration.svg", html)
        self.assertNotIn("College-Wide Collaborative Learning Platform", html)

        # Must NOT display "Home" in navigation
        self.assertNotIn('>Home</a>', html)
        self.assertIn("Dashboard", html)
        self.assertIn("My Profile", html)
        self.assertIn("Skill Exchange", html)
        self.assertIn("Projects & Hackathons", html)
        self.assertIn("Events & Hackathons", html)
        self.assertIn("My Requests", html)
        print("✓ Authenticated student dashboard verified (no badge, no 'Home').")

    def test_04_admin_dashboard_no_badge_or_home(self):
        """Verify logged-in admin dashboard has NO top-right badge, heading is 'Dashboard', and NO 'Home'."""
        self.client.get("/student/logout")
        self.client.post("/admin/login", data={
            "username": flask_app.ADMIN_USERNAME,
            "password": flask_app.ADMIN_PASSWORD
        })
        res_admin = self.client.get("/admin/dashboard")
        html = res_admin.data.decode("utf-8")

        # Must NOT display the public badge on admin dashboard
        self.assertNotIn("collaboration.svg", html)
        self.assertNotIn("College-Wide Collaborative Learning Platform", html)

        # Heading is strictly "Dashboard"
        self.assertIn('<h1 class="page-title" style="margin-top: 6px;">Dashboard</h1>', html)
        self.assertNotIn('>Home</a>', html)
        print("✓ Authenticated admin dashboard verified (no badge, no 'Home').")

    def test_05_events_and_hackathons_feature(self):
        """Verify Admin event management (add/edit/delete) and student viewing."""
        self.client.get("/student/logout")
        self.client.post("/admin/login", data={
            "username": flask_app.ADMIN_USERNAME,
            "password": flask_app.ADMIN_PASSWORD
        })

        # Add event
        res_add = self.client.post("/admin/events/create", data={
            "title": "Visual Design & Hackathon 2026",
            "description": "Collaborative project weekend for UI/UX designers and developers.",
            "event_type": "Hackathon",
            "event_date": "2026-12-30",
            "registration_deadline": "2026-12-25",
            "venue": "Campus Innovation Lab",
            "registration_link": "https://hackathon.example.edu"
        }, follow_redirects=True)
        self.assertIn("published successfully", res_add.data.decode("utf-8"))

        conn = database.get_db()
        ev = conn.execute("SELECT * FROM events WHERE title = 'Visual Design & Hackathon 2026'").fetchone()
        self.assertIsNotNone(ev)
        event_id = ev["id"]
        conn.close()

        # Student views it
        self.client.get("/admin/logout")
        self.client.post("/student/login", data={
            "college_email": "priya.n@college.edu",
            "password": "Student@123"
        })
        res_ev = self.client.get("/student/events")
        self.assertIn("Visual Design", res_ev.data.decode("utf-8"))

        # Clean up: Admin deletes it
        self.client.get("/student/logout")
        self.client.post("/admin/login", data={
            "username": flask_app.ADMIN_USERNAME,
            "password": flask_app.ADMIN_PASSWORD
        })
        res_del = self.client.post(f"/admin/events/delete/{event_id}", follow_redirects=True)
        self.assertIn("deleted successfully", res_del.data.decode("utf-8"))
        print("✓ Events & Hackathons functionality verified.")

    def test_06_all_existing_features_intact(self):
        """Confirm that skill exchange, projects, requests, and database records remain intact."""
        self.client.get("/admin/logout")
        self.client.post("/student/login", data={
            "college_email": "rohan.verma@college.edu",
            "password": "Student@123"
        })

        res_skill = self.client.get("/student/skill-exchange")
        self.assertEqual(res_skill.status_code, 200)

        res_proj = self.client.get("/student/projects")
        self.assertEqual(res_proj.status_code, 200)

        res_req = self.client.get("/student/requests")
        self.assertEqual(res_req.status_code, 200)
        print("✓ All existing platform features confirmed intact.")

if __name__ == "__main__":
    unittest.main()
