# COM569 Assignment Grading System

A full-stack web application for managing student assignments, grading with rubric support, and providing feedback in an educational environment.

## 🎓 System Architecture

- **Backend API:** Flask (Python 3.11) - RESTful API
- **Instructor Portal:** HTML/CSS/JavaScript - port 8001
- **Student Portal:** HTML/CSS/JavaScript - port 8002
- **Database:** SQLite with 8 normalized tables

## ✨ Features

### Instructor Features
- ✅ User authentication and authorization
- ✅ Class creation and management
- ✅ Assignment creation with customizable rubric criteria
- ✅ Student enrollment management (email-based)
- ✅ Detailed grading with per-criterion feedback
- ✅ CSV export of grades
- ✅ View enrolled students per class
- ✅ Delete operations (classes, assignments, enrollments)

### Student Features
- ✅ User registration and login
- ✅ View enrolled classes and available assignments
- ✅ Submit assignments (text + file URL)
- ✅ View detailed grades with rubric breakdown
- ✅ Delete ungraded submissions
- ✅ Real-time assignment status tracking

## 🚀 Installation

### Prerequisites
- Python 3.11+
- Git

### Setup Instructions

1. **Clone the repository:**
```bash
git clone https://github.com/kacpermielewczyk96-source/com569.git
cd com569
```

2. **Create and activate virtual environment:**
```bash
python3 -m venv .venv
source .venv/bin/activate  # Mac/Linux
# .venv\Scripts\activate  # Windows
```

3. **Install dependencies:**
```bash
cd api
pip install -r requirements.txt
```

## 🎮 Running the Application

You need **3 terminal windows** running simultaneously:

### Terminal 1: Backend API
```bash
cd api
source ../.venv/bin/activate
python app.py
```
**Runs on:** http://localhost:5001

### Terminal 2: Instructor Portal
```bash
cd provider
python3 -m http.server 8001
```
**Access at:** http://localhost:8001/login.html

### Terminal 3: Student Portal
```bash
cd consumer
python3 -m http.server 8002
```
**Access at:** http://localhost:8002/login.html

## 📊 Database Viewer

View all database contents with formatted output:
```bash
cd api
python3 view_database.py
```

This displays:
- All users (instructors and students)
- Classes and enrollments
- Assignments and rubrics
- Submissions and grades
- Summary statistics

## 🗄️ Database Schema

The system uses **8 normalized tables** (Third Normal Form):

| Table | Description |
|-------|-------------|
| `users` | User accounts (instructors and students) |
| `classes` | Course information |
| `enrollments` | Student-class relationships |
| `assignments` | Assignment details |
| `rubrics` | Grading criteria for assignments |
| `submissions` | Student submissions |
| `grades` | Individual criterion grades |
| `overall_grades` | Final grades with feedback |

## 🛠️ Technology Stack

**Backend:**
- Python 3.11
- Flask 3.0.0 (REST API framework)
- SQLAlchemy 3.1.1 (ORM)
- Flask-CORS 4.0.0 (Cross-origin support)
- Werkzeug 3.0.1 (Password hashing - scrypt)

**Frontend:**
- HTML5 / CSS3
- Vanilla JavaScript (ES6+)
- Responsive design with Flexbox/Grid
- Gradient color schemes (Purple for instructors, Teal for students)

**Database:**
- SQLite 3
- Foreign key constraints with CASCADE
- Indexed queries for performance

## 📁 Project Structure
```
com569/
├── api/                    # Backend API
│   ├── app.py             # Main Flask application
│   ├── view_database.py   # Database viewer script
│   ├── requirements.txt   # Python dependencies
│   └── instance/          # Database files (excluded from repo by default)
├── provider/              # Instructor portal
│   ├── index.html        # Main dashboard
│   └── login.html        # Authentication
├── consumer/              # Student portal
│   ├── index.html        # Main dashboard
│   └── login.html        # Authentication
├── database/             # Database schema documentation
│   └── schema.sql
├── docs/                 # Additional documentation
├── project_management/   # Project management artifacts
└── tests/               # Test files
```

## 🔐 Security Features

- Password hashing using Werkzeug (scrypt algorithm)
- Role-based access control (instructor vs student)
- Input validation on all forms
- Parameterized SQL queries (SQLAlchemy ORM)
- CORS configuration for API security

## 📖 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User authentication

### Classes
- `GET /api/classes` - List classes
- `POST /api/classes` - Create class
- `DELETE /api/classes/{id}` - Delete class
- `GET /api/classes/{id}/students` - List enrolled students

### Assignments
- `GET /api/assignments` - List assignments
- `POST /api/assignments` - Create assignment
- `DELETE /api/assignments/{id}` - Delete assignment

### Grading
- `POST /api/grades` - Submit criterion grade
- `POST /api/overall-grades` - Submit overall grade
- `GET /api/grades/student/{id}` - Get student grades
- `GET /api/grades/export/{assignment_id}` - Export grades as CSV

## 📸 Features Demo

- Dual portal architecture (separate instructor and student interfaces)
- Rubric-based grading with detailed feedback
- Real-time status updates (submitted/graded)
- Expandable student lists within class cards
- CSV export for grade reporting
- Color-coded UI (purple for instructors, teal for students)

## 📚 Module Information

- **Module:** COM569 - Software Engineering and Project Management
- **Institution:** Wrexham University
- **Academic Year:** 2025-26
- **Submission Deadline:** 14th January 2026

## 📜 License

This project is for educational purposes as part of COM569 module coursework.
