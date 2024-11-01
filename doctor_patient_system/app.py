from flask import Flask, render_template, redirect, url_for, request, flash,session

from flask_socketio import SocketIO, send, emit, join_room




import threading
import time
from datetime import datetime, timedelta
from flask import jsonify
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user,
    UserMixin,
)
from werkzeug.security import generate_password_hash
from werkzeug.security import generate_password_hash, check_password_hash
import os
from flask_mail import Mail, Message
from twilio.rest import Client
from werkzeug.utils import secure_filename
import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
# Initialize Flask app and config
app = Flask(__name__)

# Config for Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your-email@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'your-email-password'    # Replace with your email password
app.config['MAIL_DEFAULT_SENDER'] = 'your-email@gmail.com'

# Initialize Flask-Mail
mail = Mail(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///medications.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


app.config['SECRET_KEY'] = 'your_secret_key_here'  # Replace with a random secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'uploads' 


# Initialize extensions

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
# Twilio configuration

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)


    # Other user fields as needed
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    read = db.Column(db.Boolean, default=False)
    
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))
    sender_id = db.Column(db.Integer, db.ForeignKey('doctor.id'))
    message_id = db.Column(db.Integer, db.ForeignKey('message.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# After a doctor sends a message
def send_notification(sender_id, receiver_id, message_id):
    notification = Notification(sender_id=sender_id, patient_id=receiver_id, message_id=message_id)
    db.session.add(notification)
    db.session.commit()


# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(10))  # 'doctor' or 'patient'
    name = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    
    
    # Relationships
    doctor_details = db.relationship('DoctorDetails', backref='user', uselist=False)
    health_history = db.relationship('HealthHistory', backref='user', uselist=False)


class Medication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dosage = db.Column(db.String(50), nullable=False)
    schedule = db.Column(db.String(50), nullable=False)

    def to_dict(self):
        return {
            'name': self.name,
            'dosage': self.dosage,
            'schedule': self.schedule
        }
class Prescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(100), nullable=False)
    condition = db.Column(db.String(200), nullable=False)
    medication = db.Column(db.String(100), nullable=False)
    dosage = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    image_path = db.Column(db.String(200))  # Path to prescription image

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    working_hours = db.Column(db.String(100), nullable=False)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(50))
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'))  # Add ForeignKey here
    doctor = db.relationship('Doctor', backref=db.backref('appointments', lazy=True))  # Relationship with Doctor
    date = db.Column(db.String(20))
    time = db.Column(db.String(20))
    status = db.Column(db.String(20)) 
class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
class DoctorDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # Personal Information
    full_name = db.Column(db.String(150))
    email = db.Column(db.String(150))
    phone = db.Column(db.String(20))
    gender = db.Column(db.String(10))
    profile_photo = db.Column(db.String(100))  # Path to uploaded photo (if implemented)

    # Qualifications
    degree = db.Column(db.String(100))
    certifications = db.Column(db.Text)
    experience_years = db.Column(db.Integer)
    license_number = db.Column(db.String(50))

    # Specialization
    specialty = db.Column(db.String(100))
    subspecialty = db.Column(db.String(100))

    # Consultation Details
    consultation_fees = db.Column(db.Float)
    payment_methods = db.Column(db.String(200))
    insurance_accepted = db.Column(db.String(200))

    # Availability
    working_days = db.Column(db.String(100))
    working_hours = db.Column(db.String(100))
    emergency_availability = db.Column(db.String(10))

    # Location
    clinic_name = db.Column(db.String(150))
    clinic_address = db.Column(db.Text)
    telemedicine_services = db.Column(db.String(10))

    # Languages
    languages_spoken = db.Column(db.String(200))

class HealthHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # Personal Information
    full_name = db.Column(db.String(150))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))

    # Medical History
    high_blood_pressure = db.Column(db.String(10))  # 'yes' or 'no'
    blood_pressure_rate = db.Column(db.String(20))
    diabetes = db.Column(db.String(10))  # 'yes' or 'no'
    glucose_level = db.Column(db.String(20))
    allergies = db.Column(db.String(10))  # 'yes' or 'no'
    allergy_info = db.Column(db.Text)

    # Family History
    family_heart_disease = db.Column(db.String(10))  # 'yes' or 'no'
    family_cancer = db.Column(db.String(10))  # 'yes' or 'no'

    # Lifestyle
    smoke = db.Column(db.String(10))  # 'yes' or 'no'
    alcohol = db.Column(db.String(10))  # 'yes' or 'no'

# models.py (or within your existing app.py)



# User loader callback for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form.get('user-type')
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email, role=role).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            if user.role == 'doctor':
                return redirect(url_for('doctor_dashboard'))
            else:
                return redirect(url_for('patient_dashboard'))
        else:
            flash('Invalid email or password', 'danger')

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Handle form submission
        data = request.get_json()
        role = data.get('userType')
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        hashed_password = generate_password_hash(password)

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'success': False, 'message': 'Email address already exists'})

        new_user = User(role=role, name=name, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)

        return jsonify({'success': True})

    # Handle GET request to render the signup page
    return render_template('signup.html')


    # Return success response
@app.route('/doctor_details', methods=['GET', 'POST'])
@login_required
def doctor_details():
    if current_user.role != 'doctor':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Personal Information
        full_name = request.form.get('doctor-name')
        email = request.form.get('doctor-email')
        phone = request.form.get('doctor-phone')
        gender = request.form.get('doctor-gender')
        # Profile photo handling can be implemented here

        # Qualifications
        degree = request.form.get('doctor-degree')
        certifications = request.form.get('doctor-certifications')
        experience_years = request.form.get('doctor-experience')
        license_number = request.form.get('doctor-license')

        # Specialization
        specialty = request.form.get('doctor-specialization')
        subspecialty = request.form.get('doctor-subspecialty')

        # Consultation Details
        consultation_fees = request.form.get('doctor-fees')
        payment_methods = request.form.get('doctor-payment-methods')
        insurance_accepted = request.form.get('doctor-insurance')

        # Availability
        working_days = request.form.get('doctor-working-hours')
        working_hours = request.form.get('doctor-working-time')
        emergency_availability = request.form.get('doctor-emergency')

        # Location
        clinic_name = request.form.get('doctor-clinic')
        clinic_address = request.form.get('doctor-address')
        telemedicine_services = request.form.get('doctor-telemedicine')

        # Languages
        languages_spoken = request.form.get('doctor-languages')

        # Save to database
        doctor_details = DoctorDetails(
            user_id=current_user.id,
            full_name=full_name,
            email=email,
            phone=phone,
            gender=gender,
            degree=degree,
            certifications=certifications,
            experience_years=experience_years,
            license_number=license_number,
            specialty=specialty,
            subspecialty=subspecialty,
            consultation_fees=consultation_fees,
            payment_methods=payment_methods,
            insurance_accepted=insurance_accepted,
            working_days=working_days,
            working_hours=working_hours,
            emergency_availability=emergency_availability,
            clinic_name=clinic_name,
            clinic_address=clinic_address,
            telemedicine_services=telemedicine_services,
            languages_spoken=languages_spoken
        )
        db.session.add(doctor_details)
        db.session.commit()

        flash('Doctor details saved successfully', 'success')
        return redirect(url_for('logout'))

    return render_template('doctor_details.html')

@app.route('/health_history', methods=['GET', 'POST'])
@login_required
def health_history():
    if current_user.role != 'patient':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Personal Information
        full_name = request.form.get('full-name')
        age = request.form.get('age')
        gender = request.form.get('gender')

        # Medical History
        high_blood_pressure = request.form.get('blood-pressure')
        blood_pressure_rate = request.form.get('pressure-rate-input')
        diabetes = request.form.get('diabetes')
        glucose_level = request.form.get('glucose-level')
        allergies = request.form.get('allergies')
        allergy_info = request.form.get('allergy-info')

        # Family History
        family_heart_disease = request.form.get('family-heart-disease')
        family_cancer = request.form.get('family-cancer')

        # Lifestyle
        smoke = request.form.get('smoke')
        alcohol = request.form.get('alcohol')

        # Save to database
        health_history = HealthHistory(
            user_id=current_user.id,
            full_name=full_name,
            age=age,
            gender=gender,
            high_blood_pressure=high_blood_pressure,
            blood_pressure_rate=blood_pressure_rate,
            diabetes=diabetes,
            glucose_level=glucose_level,
            allergies=allergies,
            allergy_info=allergy_info,
            family_heart_disease=family_heart_disease,
            family_cancer=family_cancer,
            smoke=smoke,
            alcohol=alcohol
        )
        db.session.add(health_history)
        db.session.commit()

        flash('Health history saved successfully', 'success')
        return redirect(url_for('logout'))

    return render_template('health_history.html')

@app.route('/doctor_dashboard')
@login_required
def doctor_dashboard():
    if current_user.role != 'doctor':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('login'))
    doctor_id = current_user.id
    
    appointments = Appointment.query.filter_by(doctor_id=doctor_id).all()
    
    # Debugging output
    for appt in appointments:
        print(f"Appointment for {appt.patient_name} on {appt.date} at {appt.time} - Status: {appt.status}")
    doctor_details = current_user.doctor_details
    return render_template('doctor_dashboard.html', doctor_details=doctor_details,doctor_id=doctor_id,appointments=appointments)
@app.route('/available_doctors')
@login_required
def available_doctors():
    # Fetch all doctors
    doctors = DoctorDetails.query.all()
    return render_template('Appointment.html', doctors=doctors)
@app.route('/patient_dashboard')
@login_required
def patient_dashboard():
    if current_user.role != 'patient':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('login'))
    patient_id = current_user.id 
    health_history = current_user.health_history
    doctors = DoctorDetails.query.all()
       
    return render_template('patient_dashboard.html', patient_id=patient_id, health_history=health_history,doctors=doctors)
@app.route('/health_details')
@login_required
def health_details():
    if current_user.role != 'patient':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('login'))

    # Fetch health history data for the current user
    health_history = current_user.health_history

    # Pass the data to the template to display the details
    return render_template('health_details.html', health_history=health_history)
@app.route('/edit_health_details', methods=['GET', 'POST'])
@login_required
def edit_health_details():
    if current_user.role != 'patient':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('login'))

    # Fetch the current patient's health history from the database
    health_history = HealthHistory.query.filter_by(user_id=current_user.id).first()

    if request.method == 'POST':
        # Fetch form data and update the health history in the database
        health_history.full_name = request.form['full_name']
        health_history.age = request.form['age']
        health_history.gender = request.form['gender']
        health_history.high_blood_pressure = request.form['high_blood_pressure']
        health_history.blood_pressure_rate = request.form['blood_pressure_rate']
        health_history.diabetes = request.form['diabetes']
        health_history.glucose_level = request.form['glucose_level']
        health_history.allergies = request.form['allergies']
        health_history.allergy_info = request.form['allergy_info']
        health_history.family_heart_disease = request.form['family_heart_disease']
        health_history.family_cancer = request.form['family_cancer']
        health_history.smoke = request.form['smoke']
        health_history.alcohol = request.form['alcohol']

        # Commit the changes to the database
        db.session.commit()

        flash('Health details updated successfully!')
        return redirect(url_for('health_details'))  # Redirect to the health details page after updating

    return render_template('edit_health_details.html', health_history=health_history)
@app.route('/profile')
@login_required
def profile():
    user = current_user
    return render_template('profile.html', user=user)

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    user = current_user
    if request.method == 'POST':
        # Process the form data
        notification_preferences = request.form.get('notification_preferences')
        language = request.form.get('language')
        timezone = request.form.get('timezone')

        if user.role == 'doctor':
            consultation_type = request.form.get('consultation_type')
            appointment_duration = request.form.get('appointment_duration')
            profile_visibility = 'profile_visibility' in request.form
            fee_management = request.form.get('fee_management')
        elif user.role == 'patient':
            health_record_sharing = 'health_record_sharing' in request.form
            appointment_reminders = request.form.get('appointment_reminders')
            medication_reminders = 'medication_reminders' in request.form

        # Update user settings in the database
        user.notification_preferences = notification_preferences
        user.language = language
        user.timezone = timezone

        if user.role == 'doctor':
            user.consultation_type = consultation_type
            user.appointment_duration = appointment_duration
            user.profile_visibility = profile_visibility
            user.fee_management = fee_management
        elif user.role == 'patient':
            user.health_record_sharing = health_record_sharing
            user.appointment_reminders = appointment_reminders
            user.medication_reminders = medication_reminders

        db.session.commit()  # Save changes to the database

        # Redirect to settings or dashboard with a success message
        flash('Settings updated successfully!')
        return redirect(url_for('settings'))  # Redirect to settings or another page based on the context

    return render_template('settings.html', user=current_user)



@app.route('/doctor/<int:doctor_id>')
@login_required
def doctor_profile(doctor_id):
    # Fetch the doctor details based on the id
    doctor = DoctorDetails.query.get_or_404(doctor_id)
    return render_template('doctor_profile.html', doctor=doctor)
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
@app.route('/chatbot')
@login_required
def chatbot():
    return render_template('chatbot.html')

@app.route('/update_credentials', methods=['GET', 'POST'])
@login_required
def update_credentials():
    if request.method == 'POST':
        new_email = request.form.get('email')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')

        if check_password_hash(current_user.password, current_password):
            current_user.email = new_email
            if new_password:
                current_user.password = generate_password_hash(new_password)
            db.session.commit()
            flash('Credentials updated successfully', 'success')
        else:
            flash('Incorrect current password', 'danger')
    
    return render_template('update_credentials.html')
@app.route('/medicine',methods=['GET', 'POST'],endpoint='medicine')
def medicine_remainder():
    return render_template('medicine_remainder.html')
@app.route('/health')
def healthtrack():
    return render_template('health_track_goal.html')
@app.route('/Appointment', methods=['GET'])
@login_required
def appointment():
    doctors = DoctorDetails.query.all()  # Fetch all doctors
    return render_template('Appointment.html', doctors=doctors)

@app.route('/add_medication', methods=['POST'])
def add_medication():
    med_name = request.form['med_name']
    dosage = request.form['dosage']
    schedule = request.form['schedule']

    # Add the medication to the database
    new_med = Medication(name=med_name, dosage=dosage, schedule=schedule)
    db.session.add(new_med)
    db.session.commit()

    return jsonify(get_all_medications())


@app.route('/update_status/<int:appointment_id>/<string:status>', methods=['POST'])
def update_status(appointment_id, status):
    appointment = Appointment.query.get(appointment_id)
    appointment.status = status
    db.session.commit()
    return redirect(url_for('doctor_dashboard', doctor_id=appointment.doctor_id))

# Route to upload and extract data from a file (stub)
@app.route('/upload_medsheet', methods=['POST'])
def upload_medsheet():
    # This is where you can implement your OCR or file extraction logic
    # For now, we just simulate adding a new medication
    new_med = Medication(name="Aspirin", dosage="100mg", schedule="Twice a day")
    db.session.add(new_med)
    db.session.commit()

    return jsonify(get_all_medications())


# Route to get all medications
@app.route('/get_medications', methods=['GET'])
def get_medications():
    return jsonify(get_all_medications())

# Utility function to get all medications from the database
def get_all_medications():
    medications = Medication.query.all()
    return [med.to_dict() for med in medications]

def send_email(to_email, subject, content):
    message = Mail(
        from_email='your-email@example.com',  # Your verified SendGrid email
        to_emails=to_email,
        subject=subject,
        plain_text_content=content
    )
    
    try:
        sg = SendGridAPIClient('YOUR_SENDGRID_API_KEY')  # Replace with your SendGrid API key
        response = sg.send(message)
        return response.status_code
    except Exception as e:
        return str(e)

# Function to send SMS using Twilio
def send_sms(to_phone, message):
    account_sid = 'ACcaf5542e642cab75075da2755dfd6a4a'  # Replace with your Twilio SID
    auth_token = 'a6c3caf5266c8e3868090475c74d1cfc'    # Replace with your Twilio Auth Token
    client = Client(account_sid, auth_token)
    
    try:
        message = client.messages.create(
            body=message,
            from_='+18605313110',  # Replace with your Twilio phone number
            to=to_phone
        )
        return message.sid
    except Exception as e:
        return str(e)

@app.route('/set_reminder', methods=['POST'])
def set_reminder():
    data = request.json  # Use JSON data
    notification_method = data.get('notificationMethod')
    message = f"Reminder for your medication: {data.get('medicineName')} at {data.get('alarmTime')}."

    # Send Email or SMS based on the method selected
    if notification_method == 'Email':
        email = data.get('email')
        status = send_email(email, "Medication Reminder", message)
    elif notification_method == 'SMS':
        phone = data.get('smsNumber')
        status = send_sms(phone, message)
    else:
        return jsonify({"message": "Invalid notification method"}), 400

    return jsonify({"message": "Reminder set successfully", "status": status})

 # Fetch notifications for the patient
    

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()  # Create tables if they don't exist
    app.run(debug=True)