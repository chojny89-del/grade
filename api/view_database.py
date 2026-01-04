#!/usr/bin/env python3
"""
Database Viewer for COM569 Assignment Grading System
Displays all tables and their contents in a formatted way
"""

import sqlite3
from datetime import datetime


def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_table(cursor, table_name, columns):
    """Print table contents in a formatted way"""
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()

    if not rows:
        print(f"  (No data in {table_name})")
        return

    # Print column headers
    print("\n" + "-" * 80)
    print("  " + " | ".join(columns))
    print("-" * 80)

    # Print rows
    for row in rows:
        print("  " + " | ".join(str(item) for item in row))

    print(f"\n  Total records: {len(rows)}")


def main():
    # Connect to database
    conn = sqlite3.connect('instance/grading_system.db')
    cursor = conn.cursor()

    print("\n" + "🎓" * 40)
    print("       COM569 ASSIGNMENT GRADING SYSTEM - DATABASE VIEWER")
    print("🎓" * 40)

    # 1. USERS
    print_header("1. USERS (Instructors & Students)")
    print_table(cursor, 'users',
                ['user_id', 'unique_id', 'email', 'first_name', 'last_name', 'role', 'created_at'])

    # Count by role
    cursor.execute("SELECT role, COUNT(*) FROM users GROUP BY role")
    counts = cursor.fetchall()
    print("\n  Summary:")
    for role, count in counts:
        print(f"    - {role.capitalize()}s: {count}")

    # 2. CLASSES
    print_header("2. CLASSES")
    cursor.execute("""
        SELECT c.class_id, c.class_code, c.class_name, c.description,
               u.first_name || ' ' || u.last_name as instructor_name,
               c.created_at
        FROM classes c
        JOIN users u ON c.instructor_id = u.user_id
    """)
    classes = cursor.fetchall()

    if classes:
        print("\n" + "-" * 80)
        for cls in classes:
            print(f"\n  Class ID: {cls[0]}")
            print(f"  Code: {cls[1]}")
            print(f"  Name: {cls[2]}")
            print(f"  Description: {cls[3]}")
            print(f"  Instructor: {cls[4]}")
            print(f"  Created: {cls[5]}")
            print("-" * 80)
        print(f"\n  Total classes: {len(classes)}")
    else:
        print("  (No classes)")

    # 3. ENROLLMENTS
    print_header("3. ENROLLMENTS")
    cursor.execute("""
        SELECT e.enrollment_id, c.class_code, c.class_name,
               u.unique_id, u.first_name || ' ' || u.last_name as student_name,
               e.enrolled_at
        FROM enrollments e
        JOIN classes c ON e.class_id = c.class_id
        JOIN users u ON e.student_id = u.user_id
    """)
    enrollments = cursor.fetchall()

    if enrollments:
        print("\n" + "-" * 80)
        for enr in enrollments:
            print(f"  {enr[1]} - {enr[2]} | Student: {enr[4]} ({enr[3]})")
        print("-" * 80)
        print(f"\n  Total enrollments: {len(enrollments)}")
    else:
        print("  (No enrollments)")

    # 4. ASSIGNMENTS
    print_header("4. ASSIGNMENTS")
    cursor.execute("""
        SELECT a.assignment_id, c.class_code, a.title, a.description,
               a.due_date, a.max_points,
               u.first_name || ' ' || u.last_name as instructor_name
        FROM assignments a
        JOIN classes c ON a.class_id = c.class_id
        JOIN users u ON a.instructor_id = u.user_id
    """)
    assignments = cursor.fetchall()

    if assignments:
        print("\n" + "-" * 80)
        for asgn in assignments:
            print(f"\n  Assignment ID: {asgn[0]}")
            print(f"  Class: {asgn[1]}")
            print(f"  Title: {asgn[2]}")
            print(f"  Description: {asgn[3]}")
            print(f"  Due Date: {asgn[4]}")
            print(f"  Max Points: {asgn[5]}")
            print(f"  Created by: {asgn[6]}")
            print("-" * 80)
        print(f"\n  Total assignments: {len(assignments)}")
    else:
        print("  (No assignments)")

    # 5. RUBRICS
    print_header("5. RUBRIC CRITERIA")
    cursor.execute("""
        SELECT r.rubric_id, a.title as assignment_title,
               r.criterion_name, r.max_points, r.description
        FROM rubrics r
        JOIN assignments a ON r.assignment_id = a.assignment_id
    """)
    rubrics = cursor.fetchall()

    if rubrics:
        print("\n" + "-" * 80)
        current_assignment = None
        for rub in rubrics:
            if current_assignment != rub[1]:
                current_assignment = rub[1]
                print(f"\n  Assignment: {current_assignment}")
            print(f"    - {rub[2]} ({rub[3]} pts): {rub[4]}")
        print("-" * 80)
        print(f"\n  Total rubric criteria: {len(rubrics)}")
    else:
        print("  (No rubric criteria)")

    # 6. SUBMISSIONS
    print_header("6. STUDENT SUBMISSIONS")
    cursor.execute("""
        SELECT s.submission_id, a.title, u.unique_id,
               u.first_name || ' ' || u.last_name as student_name,
               s.status, s.submitted_at
        FROM submissions s
        JOIN assignments a ON s.assignment_id = a.assignment_id
        JOIN users u ON s.student_id = u.user_id
    """)
    submissions = cursor.fetchall()

    if submissions:
        print("\n" + "-" * 80)
        for sub in submissions:
            print(f"  {sub[1]} | {sub[3]} ({sub[2]}) | Status: {sub[4]} | {sub[5]}")
        print("-" * 80)
        print(f"\n  Total submissions: {len(submissions)}")

        # Status breakdown
        cursor.execute("SELECT status, COUNT(*) FROM submissions GROUP BY status")
        status_counts = cursor.fetchall()
        print("\n  Status breakdown:")
        for status, count in status_counts:
            print(f"    - {status.capitalize()}: {count}")
    else:
        print("  (No submissions)")

    # 7. GRADES
    print_header("7. GRADES (Per Criterion)")
    cursor.execute("""
        SELECT g.grade_id, s.submission_id, r.criterion_name,
               g.points_earned, g.feedback, g.graded_at
        FROM grades g
        JOIN submissions s ON g.submission_id = s.submission_id
        LEFT JOIN rubrics r ON g.rubric_id = r.rubric_id
        LIMIT 20
    """)
    grades = cursor.fetchall()

    if grades:
        print("\n" + "-" * 80)
        for grade in grades:
            criterion = grade[2] or "Overall"
            print(f"  Submission {grade[1]} | {criterion}: {grade[3]} pts | {grade[5]}")
        print("-" * 80)

        cursor.execute("SELECT COUNT(*) FROM grades")
        total_grades = cursor.fetchone()[0]
        print(f"\n  Total grade entries: {total_grades}")
        if total_grades > 20:
            print(f"  (Showing first 20)")
    else:
        print("  (No grades)")

    # 8. OVERALL GRADES
    print_header("8. OVERALL GRADES & FEEDBACK")
    cursor.execute("""
        SELECT og.overall_grade_id, a.title,
               u.first_name || ' ' || u.last_name as student_name,
               og.total_points, a.max_points,
               og.overall_feedback, og.graded_at
        FROM overall_grades og
        JOIN submissions s ON og.submission_id = s.submission_id
        JOIN assignments a ON s.assignment_id = a.assignment_id
        JOIN users u ON s.student_id = u.user_id
    """)
    overall_grades = cursor.fetchall()

    if overall_grades:
        print("\n" + "-" * 80)
        for og in overall_grades:
            percentage = (og[3] / og[4] * 100) if og[4] > 0 else 0
            print(f"\n  Assignment: {og[1]}")
            print(f"  Student: {og[2]}")
            print(f"  Grade: {og[3]}/{og[4]} ({percentage:.1f}%)")
            print(f"  Feedback: {og[5]}")
            print(f"  Graded: {og[6]}")
            print("-" * 80)
        print(f"\n  Total graded submissions: {len(overall_grades)}")
    else:
        print("  (No overall grades)")

    # SUMMARY
    print_header("DATABASE SUMMARY")
    cursor.execute("SELECT COUNT(*) FROM users WHERE role='instructor'")
    instructor_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM users WHERE role='student'")
    student_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM classes")
    class_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM assignments")
    assignment_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM submissions")
    submission_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM overall_grades")
    graded_count = cursor.fetchone()[0]

    print(f"""
  📊 Total Records:
    - Instructors: {instructor_count}
    - Students: {student_count}
    - Classes: {class_count}
    - Assignments: {assignment_count}
    - Submissions: {submission_count}
    - Graded: {graded_count}
    - Pending: {submission_count - graded_count}
    """)

    print("=" * 80)
    print("\n✅ Database view complete!\n")

    conn.close()


if __name__ == '__main__':
    main()