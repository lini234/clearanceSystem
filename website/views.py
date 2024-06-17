from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file
from flask_login import login_required, current_user
from .models import Department, ClearanceRequest, Document, User
from . import db, UPLOAD_FOLDER
import os
from werkzeug.utils import secure_filename
from website.generate_certificate import generate_certificate

views = Blueprint('views', __name__)

def all_clearances_approved(student_id):
    clearances = ClearanceRequest.query.filter_by(student_id=student_id).all()
    return all(clearance.status == 'Approved' for clearance in clearances)

@views.route("/")
@views.route("/home")
@login_required
def home():
    if current_user.is_staff:
        department = Department.query.filter_by(staff_id=current_user.id)
        return redirect(url_for('views.clearance_requests'))
    else:
        return render_template('student_home.html', user=current_user)

@views.route('/clearance', methods=['GET', 'POST'])
@login_required
def clearance():
    if request.method == 'POST':
        department_id = request.form.get('department_id')
        department = Department.query.get(department_id)

        # Get the previous department in the order
        prev_department = Department.query.filter(Department.order < department.order).order_by(
            Department.order.desc()).first()

        if prev_department:
            prev_request = ClearanceRequest.query.filter_by(student_id=current_user.id,
                                                            department_id=prev_department.id).first()
            if not prev_request or prev_request.status != 'Approved':
                flash('You must have the previous department\'s request approved before proceeding.', 'warning')
                return redirect(url_for('views.clearance'))

        existing_request = ClearanceRequest.query.filter_by(student_id=current_user.id,
                                                            department_id=department_id).first()
        if existing_request:
            flash('You have already sent a request to this department.', 'warning')
        else:
            new_request = ClearanceRequest(
                student_id=current_user.id,
                department_id=department_id,
                status='Pending'
            )
            db.session.add(new_request)
            db.session.commit()
            flash('Clearance request sent successfully.', 'success')

        return redirect(url_for('views.clearance'))

    departments = Department.query.order_by(Department.order).all()
    user_requests = {req.department_id: req.status for req in
                     ClearanceRequest.query.filter_by(student_id=current_user.id).all()}

    # Determine if the user can request clearance for each department
    department_statuses = []
    for department in departments:
        if department.id in user_requests:
            status = user_requests[department.id]
        else:
            prev_department = Department.query.filter(Department.order < department.order).order_by(
                Department.order.desc()).first()
            if prev_department:
                prev_request = ClearanceRequest.query.filter_by(student_id=current_user.id,
                                                                department_id=prev_department.id).first()
                if not prev_request or prev_request.status != 'Approved':
                    status = 'Not Requestable'
                else:
                    status = 'Not Requested'
            else:
                status = 'Not Requested'
        department_statuses.append((department, status))

    return render_template('clearance.html', department_statuses=department_statuses, user=current_user)

@views.route('/clearance-requests')
@login_required
def clearance_requests():
    if not current_user.is_staff:
        flash('You do not have access to this page.', 'warning')
        return redirect(url_for('index'))

    department = Department.query.filter_by(staff_id=current_user.id).first()
    if not department:
        flash('You are not assigned to any department.', 'warning')
        return redirect(url_for('index'))

    clearance_requests = ClearanceRequest.query.filter_by(department_id=department.id).all()
    documents = Document.query.filter_by(department_id=department.id).all()
    return render_template('clearance_requests.html', department=department,
                           clearance_requests=clearance_requests, documents=documents, user=current_user)

@views.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_documents():
    department_id = request.form.get('department_id')
    file = request.files['document']

    if file:
        filename = secure_filename(file.filename)
        upload_folder = UPLOAD_FOLDER
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)

        document = Document(
            student_id=current_user.id,
            department_id=department_id,
            filename=filename
        )
        db.session.add(document)
        db.session.commit()
        flash('Document uploaded successfully.', 'success')
    else:
        flash('No file selected.', 'warning')

    return redirect(url_for('views.clearance'))

@views.route('/update-clearance/<int:request_id>', methods=['GET', 'POST'])
@login_required
def update_clearance(request_id):
    if not current_user.is_staff:
        flash('You do not have access to perform this action.', 'warning')
        return redirect(url_for('views.home'))

    action = request.form.get('action')
    clearance_request = ClearanceRequest.query.get_or_404(request_id)

    if clearance_request.department.staff_id != current_user.id:
        flash('You do not have permission to update this request.', 'warning')
        return redirect(url_for('views.clearance_requests'))

    if action == 'accept':
        clearance_request.status = 'Approved'
        clearance_request.clearance_date = db.func.current_timestamp()
    elif action == 'decline':
        clearance_request.status = 'Declined'
        clearance_request.clearance_date = db.func.current_timestamp()

    db.session.commit()
    flash(f'Clearance request has been {clearance_request.status.lower()}.', 'success')
    return redirect(url_for('views.clearance_requests'))


@views.route('/generate_certificate/<int:student_id>', methods=['GET'])
@login_required
def generate_certificate_route(student_id):
    student = User.query.get_or_404(student_id)

    # Check if all clearances are approved
    if not all_clearances_approved(student_id):
        flash('All clearances are not yet approved.', 'warning')
        return redirect(url_for('views.clearance'))

    # Proceed with generating certificate
    clearance_requests = ClearanceRequest.query.filter_by(student_id=student_id).all()
    latest_clearance = ClearanceRequest.query.filter_by(student_id=student_id).order_by(
        ClearanceRequest.request_date.desc()).first()

    if latest_clearance:
        clearance_status = latest_clearance.status
        clearance_date = latest_clearance.clearance_date
        staff_name = latest_clearance.department.staff.otherNames  # Assuming staff name is stored in otherNames field
        department_name = latest_clearance.department.title
    else:
        clearance_status = "Pending"
        clearance_date = None  # Handle this case as needed
        staff_name = ""
        department_name = ""

    certificate_path = f"/static/certificates/{student.otherNames}_certificate.pdf"
    if not os.path.exists('/static/certificates'):
        os.makedirs('/static/certificates')

    generate_certificate(student.surname, student.otherNames, student.matricNumber, student.college, student.department,
                         staff_name, department_name, clearance_status, clearance_date, clearance_requests,
                         certificate_path)

    return send_file(certificate_path, as_attachment=True)