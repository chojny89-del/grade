from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import random
import csv
import io

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///grading_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app)


# ===========================
# MODELS
# ===========================

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    unique_id = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Class(db.Model):
    __tablename__ = 'classes'
    class_id = db.Column(db.Integer, primary_key=True)
    instructor_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    class_code = db.Column(db.String(20), unique=True, nullable=False)
    class_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    enrollment_id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.class_id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)


class Assignment(db.Model):
    __tablename__ = 'assignments'
    assignment_id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.class_id'), nullable=False)
    instructor_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.DateTime, nullable=False)
    max_points = db.Column(db.Float, default=100)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Rubric(db.Model):
    __tablename__ = 'rubrics'
    rubric_id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.assignment_id'), nullable=False)
    criterion_name = db.Column(db.String(255), nullable=False)
    max_points = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Submission(db.Model):
    __tablename__ = 'submissions'
    submission_id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.assignment_id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    submission_text = db.Column(db.Text)
    file_path = db.Column(db.String(500))
    status = db.Column(db.String(50), default='submitted')
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)


class Grade(db.Model):
    __tablename__ = 'grades'
    grade_id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submissions.submission_id'), nullable=False)
    rubric_id = db.Column(db.Integer, db.ForeignKey('rubrics.rubric_id'), nullable=True)
    points_earned = db.Column(db.Float, nullable=False)
    feedback = db.Column(db.Text)
    graded_by = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    graded_at = db.Column(db.DateTime, default=datetime.utcnow)


class OverallGrade(db.Model):
    __tablename__ = 'overall_grades'
    overall_grade_id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submissions.submission_id'), unique=True, nullable=False)
    total_points = db.Column(db.Float, nullable=False)
    letter_grade = db.Column(db.String(2))
    overall_feedback = db.Column(db.Text)
    graded_by = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    graded_at = db.Column(db.DateTime, default=datetime.utcnow)


# ===========================
# HELPER FUNCTIONS
# ===========================

def generate_unique_id(role):
    if role == 'student':
        return f"s{random.randint(10000000, 99999999)}"
    else:
        return f"i{random.randint(10000, 99999)}"


# ===========================
# AUTHENTICATION
# ===========================

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400

    unique_id = generate_unique_id(data['role'])
    while User.query.filter_by(unique_id=unique_id).first():
        unique_id = generate_unique_id(data['role'])

    user = User(
        unique_id=unique_id,
        email=data['email'],
        password_hash=generate_password_hash(data['password']),
        first_name=data['first_name'],
        last_name=data['last_name'],
        role=data['role']
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({
        'message': 'Registration successful',
        'user': {
            'user_id': user.user_id,
            'unique_id': user.unique_id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role
        }
    }), 201


@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()

    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401

    return jsonify({
        'message': 'Login successful',
        'user': {
            'user_id': user.user_id,
            'unique_id': user.unique_id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role
        }
    }), 200


# ===========================
# CLASSES
# ===========================

@app.route('/api/classes', methods=['GET', 'POST'])
def handle_classes():
    if request.method == 'POST':
        data = request.json
        new_class = Class(
            instructor_id=data['instructor_id'],
            class_code=data['class_code'],
            class_name=data['class_name'],
            description=data.get('description', '')
        )
        db.session.add(new_class)
        db.session.commit()
        return jsonify({'message': 'Class created', 'class_id': new_class.class_id}), 201

    instructor_id = request.args.get('instructor_id')
    if instructor_id:
        classes = Class.query.filter_by(instructor_id=instructor_id).all()
    else:
        classes = Class.query.all()

    return jsonify([{
        'class_id': c.class_id,
        'instructor_id': c.instructor_id,
        'class_code': c.class_code,
        'class_name': c.class_name,
        'description': c.description
    } for c in classes]), 200


@app.route('/api/classes/<int:class_id>/students', methods=['GET'])
def get_class_students(class_id):
    enrollments = Enrollment.query.filter_by(class_id=class_id).all()
    students = []
    for enrollment in enrollments:
        user = User.query.get(enrollment.student_id)
        if user:
            students.append({
                'enrollment_id': enrollment.enrollment_id,
                'user_id': user.user_id,
                'unique_id': user.unique_id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            })
    return jsonify(students), 200


@app.route('/api/classes/<int:class_id>', methods=['DELETE'])
def delete_class(class_id):
    class_obj = Class.query.get(class_id)
    if not class_obj:
        return jsonify({'error': 'Class not found'}), 404

    db.session.delete(class_obj)
    db.session.commit()
    return jsonify({'message': 'Class deleted successfully'}), 200


# ===========================
# ENROLLMENTS
# ===========================

@app.route('/api/enrollments', methods=['POST'])
def enroll_student():
    data = request.json

    if 'student_email' in data:
        student = User.query.filter_by(email=data['student_email'], role='student').first()
        if not student:
            return jsonify({'error': 'Student not found with this email'}), 404
        student_id = student.user_id
    else:
        student_id = data['student_id']

    existing = Enrollment.query.filter_by(
        class_id=data['class_id'],
        student_id=student_id
    ).first()

    if existing:
        return jsonify({'error': 'Student already enrolled'}), 400

    enrollment = Enrollment(
        class_id=data['class_id'],
        student_id=student_id
    )
    db.session.add(enrollment)
    db.session.commit()

    return jsonify({'message': 'Student enrolled successfully'}), 201


@app.route('/api/enrollments/<int:enrollment_id>', methods=['DELETE'])
def delete_enrollment(enrollment_id):
    enrollment = Enrollment.query.get(enrollment_id)
    if not enrollment:
        return jsonify({'error': 'Enrollment not found'}), 404

    db.session.delete(enrollment)
    db.session.commit()
    return jsonify({'message': 'Student unenrolled successfully'}), 200


@app.route('/api/students/<int:student_id>/classes', methods=['GET'])
def get_student_classes(student_id):
    enrollments = Enrollment.query.filter_by(student_id=student_id).all()
    classes = []
    for enrollment in enrollments:
        class_obj = Class.query.get(enrollment.class_id)
        if class_obj:
            classes.append({
                'class_id': class_obj.class_id,
                'class_code': class_obj.class_code,
                'class_name': class_obj.class_name,
                'description': class_obj.description
            })
    return jsonify(classes), 200


# ===========================
# ASSIGNMENTS
# ===========================

@app.route('/api/assignments', methods=['GET', 'POST'])
def handle_assignments():
    if request.method == 'POST':
        data = request.json
        assignment = Assignment(
            class_id=data['class_id'],
            instructor_id=data['instructor_id'],
            title=data['title'],
            description=data.get('description', ''),
            due_date=datetime.fromisoformat(data['due_date']),
            max_points=data.get('max_points', 100)
        )
        db.session.add(assignment)
        db.session.commit()
        return jsonify({
            'message': 'Assignment created',
            'assignment_id': assignment.assignment_id
        }), 201

    class_id = request.args.get('class_id')
    instructor_id = request.args.get('instructor_id')

    query = Assignment.query
    if class_id:
        query = query.filter_by(class_id=class_id)
    if instructor_id:
        query = query.filter_by(instructor_id=instructor_id)

    assignments = query.all()
    result = []
    for a in assignments:
        class_obj = Class.query.get(a.class_id)
        result.append({
            'assignment_id': a.assignment_id,
            'class_id': a.class_id,
            'class_code': class_obj.class_code if class_obj else '',
            'class_name': class_obj.class_name if class_obj else '',
            'title': a.title,
            'description': a.description,
            'due_date': a.due_date.isoformat(),
            'max_points': a.max_points
        })

    return jsonify(result), 200


@app.route('/api/assignments/<int:assignment_id>', methods=['DELETE'])
def delete_assignment(assignment_id):
    assignment = Assignment.query.get(assignment_id)
    if not assignment:
        return jsonify({'error': 'Assignment not found'}), 404

    db.session.delete(assignment)
    db.session.commit()
    return jsonify({'message': 'Assignment deleted successfully'}), 200


# ===========================
# RUBRICS
# ===========================

@app.route('/api/rubrics', methods=['GET', 'POST'])
def handle_rubrics():
    if request.method == 'POST':
        data = request.json
        rubric = Rubric(
            assignment_id=data['assignment_id'],
            criterion_name=data['criterion_name'],
            max_points=data['max_points'],
            description=data.get('description', '')
        )
        db.session.add(rubric)
        db.session.commit()
        return jsonify({
            'message': 'Rubric criterion created',
            'rubric_id': rubric.rubric_id
        }), 201

    assignment_id = request.args.get('assignment_id')
    if assignment_id:
        rubrics = Rubric.query.filter_by(assignment_id=assignment_id).all()
    else:
        rubrics = Rubric.query.all()

    return jsonify([{
        'rubric_id': r.rubric_id,
        'assignment_id': r.assignment_id,
        'criterion_name': r.criterion_name,
        'max_points': r.max_points,
        'description': r.description
    } for r in rubrics]), 200


# ===========================
# SUBMISSIONS
# ===========================

@app.route('/api/submissions', methods=['GET', 'POST'])
def handle_submissions():
    if request.method == 'POST':
        data = request.json

        existing = Submission.query.filter_by(
            assignment_id=data['assignment_id'],
            student_id=data['student_id']
        ).first()

        if existing:
            return jsonify({'error': 'Assignment already submitted'}), 400

        submission = Submission(
            assignment_id=data['assignment_id'],
            student_id=data['student_id'],
            submission_text=data.get('submission_text', ''),
            file_path=data.get('file_path', '')
        )
        db.session.add(submission)
        db.session.commit()
        return jsonify({
            'message': 'Submission created',
            'submission_id': submission.submission_id
        }), 201

    assignment_id = request.args.get('assignment_id')
    student_id = request.args.get('student_id')

    query = Submission.query
    if assignment_id:
        query = query.filter_by(assignment_id=assignment_id)
    if student_id:
        query = query.filter_by(student_id=student_id)

    submissions = query.all()
    result = []
    for s in submissions:
        student = User.query.get(s.student_id)
        assignment = Assignment.query.get(s.assignment_id)
        result.append({
            'submission_id': s.submission_id,
            'assignment_id': s.assignment_id,
            'assignment_title': assignment.title if assignment else 'Unknown',
            'student_id': s.student_id,
            'student_name': f"{student.first_name} {student.last_name}" if student else "Unknown",
            'student_unique_id': student.unique_id if student else "",
            'submission_text': s.submission_text,
            'file_path': s.file_path,
            'status': s.status,
            'submitted_at': s.submitted_at.isoformat()
        })

    return jsonify(result), 200


@app.route('/api/submissions/<int:submission_id>', methods=['DELETE'])
def delete_submission(submission_id):
    submission = Submission.query.get(submission_id)
    if not submission:
        return jsonify({'error': 'Submission not found'}), 404

    if submission.status == 'graded':
        return jsonify({'error': 'Cannot delete graded submission'}), 400

    db.session.delete(submission)
    db.session.commit()
    return jsonify({'message': 'Submission deleted successfully'}), 200


# ===========================
# GRADING
# ===========================

@app.route('/api/grades', methods=['POST'])
def create_grade():
    data = request.json

    grade = Grade(
        submission_id=data['submission_id'],
        rubric_id=data.get('rubric_id'),
        points_earned=data['points_earned'],
        feedback=data.get('feedback', ''),
        graded_by=data['graded_by']
    )
    db.session.add(grade)

    submission = Submission.query.get(data['submission_id'])
    if submission:
        submission.status = 'graded'

    db.session.commit()
    return jsonify({'message': 'Grade saved'}), 201


@app.route('/api/overall-grades', methods=['POST'])
def create_overall_grade():
    data = request.json

    existing = OverallGrade.query.filter_by(submission_id=data['submission_id']).first()

    if existing:
        existing.total_points = data['total_points']
        existing.letter_grade = data.get('letter_grade', '')
        existing.overall_feedback = data.get('overall_feedback', '')
        existing.graded_by = data['graded_by']
        existing.graded_at = datetime.utcnow()
    else:
        overall_grade = OverallGrade(
            submission_id=data['submission_id'],
            total_points=data['total_points'],
            letter_grade=data.get('letter_grade', ''),
            overall_feedback=data.get('overall_feedback', ''),
            graded_by=data['graded_by']
        )
        db.session.add(overall_grade)

    db.session.commit()
    return jsonify({'message': 'Overall grade saved'}), 201


@app.route('/api/grades/student/<int:student_id>', methods=['GET'])
def get_student_grades(student_id):
    submissions = Submission.query.filter_by(student_id=student_id, status='graded').all()
    result = []

    for submission in submissions:
        assignment = Assignment.query.get(submission.assignment_id)
        overall_grade = OverallGrade.query.filter_by(submission_id=submission.submission_id).first()

        rubric_grades = []
        grades = Grade.query.filter_by(submission_id=submission.submission_id).all()
        for g in grades:
            rubric = Rubric.query.get(g.rubric_id) if g.rubric_id else None
            rubric_grades.append({
                'criterion_name': rubric.criterion_name if rubric else 'Overall',
                'max_points': rubric.max_points if rubric else assignment.max_points,
                'points_earned': g.points_earned,
                'feedback': g.feedback
            })

        result.append({
            'submission_id': submission.submission_id,
            'assignment_title': assignment.title if assignment else 'Unknown',
            'max_points': assignment.max_points if assignment else 100,
            'total_points': overall_grade.total_points if overall_grade else 0,
            'letter_grade': overall_grade.letter_grade if overall_grade else '',
            'overall_feedback': overall_grade.overall_feedback if overall_grade else '',
            'rubric_grades': rubric_grades,
            'graded_at': overall_grade.graded_at.isoformat() if overall_grade else ''
        })

    return jsonify(result), 200


# ===========================
# CSV EXPORT
# ===========================

@app.route('/api/grades/export/<int:assignment_id>', methods=['GET'])
def export_grades_csv(assignment_id):
    assignment = Assignment.query.get(assignment_id)
    if not assignment:
        return jsonify({'error': 'Assignment not found'}), 404

    submissions = Submission.query.filter_by(assignment_id=assignment_id, status='graded').all()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(
        ['Student ID', 'Student Name', 'Email', 'Total Points', 'Max Points', 'Percentage', 'Overall Feedback',
         'Graded At'])

    for submission in submissions:
        student = User.query.get(submission.student_id)
        overall_grade = OverallGrade.query.filter_by(submission_id=submission.submission_id).first()

        if student and overall_grade:
            percentage = (overall_grade.total_points / assignment.max_points * 100) if assignment.max_points > 0 else 0
            writer.writerow([
                student.unique_id,
                f"{student.first_name} {student.last_name}",
                student.email,
                overall_grade.total_points,
                assignment.max_points,
                f"{percentage:.1f}%",
                overall_grade.overall_feedback or '',
                overall_grade.graded_at.strftime('%Y-%m-%d %H:%M:%S')
            ])

    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers[
        'Content-Disposition'] = f'attachment; filename=grades_{assignment.class_id}_{assignment.title.replace(" ", "_")}.csv'

    return response


# ===========================
# HEALTH CHECK
# ===========================

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'API v2 is running'}), 200


# ===========================
# MAIN
# ===========================

if __name__ == '__main__':
    with app.app_context():
        # db.drop_all()  # Database persistence - don't reset on restart
        db.create_all()
        print("✅ Database ready!")

    print("🚀 Starting API v2 on http://localhost:5001")

    import os

    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('DEBUG', 'True') == 'True'
    app.run(debug=debug, host='0.0.0.0', port=port)