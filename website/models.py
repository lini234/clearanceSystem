from . import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    surname = db.Column(db.String(150))
    otherNames = db.Column(db.String(150))
    matricNumber = db.Column(db.String(11), unique=True, nullable=True)
    department = db.Column(db.String(150))
    college = db.Column(db.String(150))
    is_staff = db.Column(db.Boolean, default=False)

    clearance_requests = db.relationship('ClearanceRequest', back_populates='student', lazy=True)
    documents = db.relationship('Document', backref='student', lazy=True)

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    filename = db.Column(db.String(150), nullable=False)
    upload_date = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    staff = db.relationship('User', backref=db.backref('departments', lazy=True))
    request = db.relationship('ClearanceRequest', backref='departments', lazy=True)
    order = db.Column(db.Integer, nullable=False, unique=True, default=0)

    # Relationship to ClearanceRequest
    clearance_requests = db.relationship('ClearanceRequest', back_populates='department', lazy=True)
    documents = db.relationship('Document', backref='department', lazy=True)

class ClearanceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='Pending')
    request_date = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    clearance_date = db.Column(db.DateTime, nullable=True)

    # Relationships
    student = db.relationship('User', back_populates='clearance_requests')
    department = db.relationship('Department', back_populates='clearance_requests')

