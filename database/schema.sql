-- Assignment Grading System Database Schema v2
-- With Classes, Unique IDs, and Rubrics

-- Users table with unique student/instructor IDs
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    unique_id VARCHAR(20) UNIQUE NOT NULL,  -- e.g., s22770067 or i00123
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL,  -- 'instructor' or 'student'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Classes/Courses table
CREATE TABLE classes (
    class_id INTEGER PRIMARY KEY AUTOINCREMENT,
    instructor_id INTEGER NOT NULL,
    class_code VARCHAR(20) UNIQUE NOT NULL,  -- e.g., COM569
    class_name VARCHAR(255) NOT NULL,         -- e.g., Software Engineering
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (instructor_id) REFERENCES users(user_id)
);

-- Student enrollment in classes
CREATE TABLE enrollments (
    enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (class_id) REFERENCES classes(class_id),
    FOREIGN KEY (student_id) REFERENCES users(user_id),
    UNIQUE(class_id, student_id)
);

-- Assignments linked to classes
CREATE TABLE assignments (
    assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_id INTEGER NOT NULL,
    instructor_id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    due_date TIMESTAMP NOT NULL,
    max_points INTEGER DEFAULT 100,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (class_id) REFERENCES classes(class_id),
    FOREIGN KEY (instructor_id) REFERENCES users(user_id)
);

-- Rubrics (grading criteria)
CREATE TABLE rubrics (
    rubric_id INTEGER PRIMARY KEY AUTOINCREMENT,
    assignment_id INTEGER NOT NULL,
    criteria_name VARCHAR(255) NOT NULL,
    description TEXT,
    max_points INTEGER NOT NULL,
    weight DECIMAL(5,2) DEFAULT 1.00,
    FOREIGN KEY (assignment_id) REFERENCES assignments(assignment_id)
);

-- Submissions
CREATE TABLE submissions (
    submission_id INTEGER PRIMARY KEY AUTOINCREMENT,
    assignment_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    submission_text TEXT,
    file_path VARCHAR(500),
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'submitted',
    FOREIGN KEY (assignment_id) REFERENCES assignments(assignment_id),
    FOREIGN KEY (student_id) REFERENCES users(user_id),
    UNIQUE(assignment_id, student_id)
);

-- Grades with feedback
CREATE TABLE grades (
    grade_id INTEGER PRIMARY KEY AUTOINCREMENT,
    submission_id INTEGER NOT NULL,
    rubric_id INTEGER,
    points_earned DECIMAL(5,2) NOT NULL,
    feedback TEXT,  -- Instructor's comments
    graded_by INTEGER NOT NULL,
    graded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (submission_id) REFERENCES submissions(submission_id),
    FOREIGN KEY (rubric_id) REFERENCES rubrics(rubric_id),
    FOREIGN KEY (graded_by) REFERENCES users(user_id)
);

-- Overall grades summary
CREATE TABLE overall_grades (
    overall_grade_id INTEGER PRIMARY KEY AUTOINCREMENT,
    submission_id INTEGER NOT NULL,
    total_points DECIMAL(5,2) NOT NULL,
    percentage DECIMAL(5,2),
    letter_grade VARCHAR(2),
    general_feedback TEXT,  -- Overall comments
    FOREIGN KEY (submission_id) REFERENCES submissions(submission_id)
);

-- Sample data with unique IDs
INSERT INTO users (unique_id, email, password_hash, first_name, last_name, role) VALUES
('i00001', 'instructor1@wrexham.ac.uk', 'hashed_password', 'John', 'Smith', 'instructor'),
('s22770067', 'student1@wrexham.ac.uk', 'hashed_password', 'Alice', 'Brown', 'student'),
('s22770068', 'student2@wrexham.ac.uk', 'hashed_password', 'Bob', 'Wilson', 'student');

-- Sample classes
INSERT INTO classes (instructor_id, class_code, class_name, description) VALUES
(1, 'COM569', 'Software Engineering', 'Software development and project management'),
(1, 'COM570', 'Cloud Computing', 'Cloud architecture and distributed systems');

-- Sample enrollments
INSERT INTO enrollments (class_id, student_id) VALUES
(1, 2),  -- Alice in COM569
(1, 3),  -- Bob in COM569
(2, 2);  -- Alice in COM570