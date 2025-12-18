from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, request, render_template
import os
import cv2
import pytesseract
from PIL import Image
import re
import pandas as pd
from collections import Counter
from symptom_disease_detection.detect_sym_dis import get_diseases_for_symptoms
from symptom_test_detection.detect_sym_test import predict_tests
from test_result_detection.detect_result_dis import predict_disease_from_image as predict_from_report
import specialization_analysis
from datetime import datetime
from flask import Flask
from flask_login import LoginManager
from flask_login import current_user
from flask_login import UserMixin
import json


app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)


app.secret_key = 'The_twin_Squad:_Two_Girls_Transforming_Healthcare_with_MedAIgnosis'  # Required for flashing messages


# Cache to store uploaded files per type
uploaded_reports = []
uploaded_mri_xray = []

# Update SQLAlchemy database URI with the environment variable
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost/medical_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
db = SQLAlchemy(app)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# User Model
class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_doctor = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<User {self.username}>"# 'patient' or 'doctor'
    

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id) 


# Define the Patient and Doctor models
class Patient(db.Model):
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    date_of_birth = db.Column(db.String(10), nullable=False)
    contact_number = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    address = db.Column(db.String(250), nullable=False)
    medical_history = db.Column(db.String(250))
    allergies = db.Column(db.String(100))
    emergency_contact_name = db.Column(db.String(50), nullable=False)
    emergency_contact_number = db.Column(db.String(15), nullable=False)

class Doctor(db.Model):
    __tablename__ = 'doctors'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    date_of_birth = db.Column(db.String(10), nullable=False)
    contact_number = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    address = db.Column(db.String(250), nullable=False)
    medical_license_number = db.Column(db.String(50), nullable=False)
    speciality = db.Column(db.String(50), nullable=False)
    education = db.Column(db.String(250), nullable=False)
    years_of_experience = db.Column(db.Integer, nullable=False)
    hospital_affiliation = db.Column(db.String(100), nullable=False)
    languages_spoken = db.Column(db.String(100))


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/balance')
def balance():
    return render_template('mainBD.html')

@app.route('/monday')
def monday():
    return render_template('monday.html')

@app.route('/tuesday')
def tuesday():
    return render_template('tuesday.html')

@app.route('/wednesday')
def wednesday():
    return render_template('wednesday.html')

@app.route('/thursday')
def thursday():
    return render_template('thursday.html')

@app.route('/friday')
def friday():
    return render_template('friday.html')

@app.route('/saturday')
def saturday():
    return render_template('saturday.html')

@app.route('/sunday')
def sunday():
    return render_template('sunday.html')

@app.route('/know_more')
def know_more():
    return render_template('Know more.html')

@app.route('/about_us')
def about_us():
    return render_template('About us.html')


@app.route('/patient_login', methods=['GET', 'POST'])
def patient_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Debugging information
        print(f"Attempting to log in patient with username: {username}")

        # Find the patient in the database
        patient = Patient.query.filter_by(username=username).first()
        
        # Check if patient exists and the password is correct
        if patient:
            if check_password_hash(patient.password, password):
                # Store patient ID and role in session
                session['user_id'] = patient.id
                session['role'] = 'Patient'
                
            
                return redirect(url_for('successful', username=patient.first_name, user_type='Patient'))
            else:
                flash('Invalid password. Please try again.', 'error')
        else:
            flash('Invalid username. Please try again.', 'error')
            return redirect(url_for('patient_login'))
    
    return render_template('patient_login.html')


@app.route('/doctor_login', methods=['GET', 'POST'])
def doctor_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Debugging information
        print(f"Attempting to log in doctor with username: {username}")

        # Find the doctor in the database
        doctor = Doctor.query.filter_by(username=username).first()
        
        # Check if doctor exists and the password is correct
        if doctor:
            if check_password_hash(doctor.password, password):
                # Store doctor ID and role in session
                session['user_id'] = doctor.id
                session['role'] = 'Doctor'
                
                
                return redirect(url_for('successful', username=doctor.first_name, user_type='Doctor'))
            else:
                flash('Invalid password. Please try again.', 'error')
        else:
            flash('Invalid username. Please try again.', 'error')
            return redirect(url_for('doctor_login'))

    return render_template('doctor_login.html')


@app.route('/get_registration_details')
def get_registration_details():
    if 'user_id' in session:
        user_id = session['user_id']

        # Check the user role to determine which model to query
        if session['role'] == 'Patient':
            user = Patient.query.get(user_id)
            if user:
                details = {
                    "id": user.id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "age": user.age,
                    "gender": user.gender,
                    "date_of_birth": user.date_of_birth,
                    "contact_number": user.contact_number,
                    "email": user.email,
                    "address": user.address,
                    "medical_history": user.medical_history,
                    "allergies": user.allergies,
                    "emergency_contact_name": user.emergency_contact_name,
                    "emergency_contact_number": user.emergency_contact_number
                }
                return jsonify(details)  # Return JSON response

        elif session['role'] == 'Doctor':
            user = Doctor.query.get(user_id)
            if user:
                details = {
                    "id": user.id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "gender": user.gender,
                    "date_of_birth": user.date_of_birth,
                    "contact_number": user.contact_number,
                    "email": user.email,
                    "address": user.address,
                    "medical_license_number": user.medical_license_number,
                    "speciality": user.speciality,
                    "education": user.education,
                    "years_of_experience": user.years_of_experience,
                    "hospital_affiliation": user.hospital_affiliation,
                    "languages_spoken": user.languages_spoken
                }
                return jsonify(details)  # Return JSON response

    return jsonify("User not logged in."), 401  # Ensure to return a 401 status code


@app.route('/successful')
def successful():
    username = request.args.get('username')
    user_type = request.args.get('user_type')
    return render_template('successful.html', username=username, user_type=user_type)


@app.route('/patient_form')
def patient_form():
    return render_template('patient_form.html')

@app.route('/submit_patient', methods=['POST'])
def submit_patient():
    patient = Patient(
        username=request.form['username'],
        password=generate_password_hash(request.form['password']),  # Hash the password
        first_name=request.form['first_name'],
        last_name=request.form['last_name'],
        age=request.form['age'],
        gender=request.form['gender'],
        date_of_birth=request.form['date_of_birth'],
        contact_number=request.form['contact_number'],
        email=request.form['email'],
        address=request.form['address'],
        medical_history=request.form['medical_history'],
        allergies=request.form['allergies'],
        emergency_contact_name=request.form['emergency_contact_name'],
        emergency_contact_number=request.form['emergency_contact_number'],
    )
    db.session.add(patient)
    db.session.commit()
    return redirect(url_for('welcome', user=patient.first_name, user_type='Patient'))


# Path to Tesseract executable (update as needed)
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\KAVYA B R\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

# License number patterns for various countries
license_patterns = {
    'USA': r'^[A-Z]{1,2}\d{5,7}$|^\d{6,7}$',  # A123456 or 1234567
    'UK': r'^\d{7}$',  # 1234567
    'Canada': r'^[A-Z]{0,3}-?\d{6,7}$',  # XYZ-123456
    'Australia': r'^\d{6}$',  # 123456
    'India': r'^\d{5}$',  # 12345
    'Germany': r'^Ärzte-[0-9]{5}$',  # Ärzte-12345
    'France': r'^RPPS\d{11}$',  # RPPS followed by 11 digits
    'Italy': r'^M-\d{5,7}$',  # M-12345
    'Spain': r'^\d{8}[A-Z]$',  # 12345678A
    'Brazil': r'^\d{2}-\d{4}-[A-Z]{2}$',  # 12-3456-AB
    'Mexico': r'^\d{7}$',  # 1234567
    'Argentina': r'^\d{6,8}$',  # 12345678
    'South Africa': r'^MP\d{5}$',  # MP12345
    'Japan': r'^\d{6}$',  # 123456
    'China': r'^\d{15}$',  # 123456789012345 (15 digits)
    'Russia': r'^\d{10}$',  # 1234567890
    'Nigeria': r'^[A-Z]{3}-\d{6}$',  # ABC-123456
    'Singapore': r'^\d{7}$',  # 1234567
    'Sweden': r'^\d{6}-\d{4}$',  # 123456-7890
    'Norway': r'^[0-9]{11}$',  # 12345678901
    'Finland': r'^\d{6}$',  # 123456
    'South Korea': r'^\d{8}$',  # 12345678
    'Denmark': r'^\d{8}$',  # 12345678
    'Philippines': r'^[0-9]{7}$',  # 1234567
    'Vietnam': r'^\d{8}$',  # 12345678
    'Thailand': r'^[A-Z]{1}[0-9]{8}$',  # A12345678
    'Colombia': r'^[0-9]{6}$',  # 123456
    'Chile': r'^\d{7}$',  # 1234567
    'New Zealand': r'^\d{6}$',  # 123456
    'Ireland': r'^[0-9]{6}$',  # 123456
    'Israel': r'^\d{7}$',  # 1234567
    'Turkey': r'^\d{6}$',  # 123456
    'Malaysia': r'^\d{7}$',  # 1234567
    'Iceland': r'^\d{7}$',  # 1234567
    'Kuwait': r'^[A-Z]{3}\d{4}$',  # ABC1234
    'Qatar': r'^\d{8}$',  # 12345678
    'United Arab Emirates': r'^[0-9]{8}$',  # 12345678
    'Saudi Arabia': r'^[0-9]{10}$',  # 1234567890
    'Oman': r'^[0-9]{6}$',  # 123456
    'Bangladesh': r'^[0-9]{8}$',  # 12345678
    'Pakistan': r'^[0-9]{7}$',  # 1234567
    'Sri Lanka': r'^[0-9]{7}$',  # 1234567
    'Nepal': r'^[0-9]{7}$',  # 1234567
    'Afghanistan': r'^\d{6}$',  # 123456
    'Myanmar': r'^[0-9]{6}$',  # 123456
    'Ethiopia': r'^[A-Z]{2}[0-9]{6}$',  # AB123456
    'Ghana': r'^[0-9]{6}$',  # 123456
    'Kenya': r'^\d{8}$',  # 12345678
    'Tanzania': r'^[0-9]{6}$',  # 123456
    'Zambia': r'^[0-9]{6}$',  # 123456
    'Uganda': r'^[0-9]{6}$',  # 123456
    'Jamaica': r'^[0-9]{6}$',  # 123456
    'Barbados': r'^[0-9]{6}$',  # 123456
    'Dominican Republic': r'^\d{7}$',  # 1234567
    'Hungary': r'^[A-Z]-\d{5}$',  # A-12345
    # Add more countries as necessary
}

def preprocess_image(image_path):
    """Preprocess the image for better OCR results."""
    image = cv2.imread(image_path)
    if image is None:
        return None
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray

def extract_text(image):
    """Extract text from the preprocessed image using Tesseract."""
    pil_image = Image.fromarray(image)
    extracted_text = pytesseract.image_to_string(pil_image)
    return extracted_text

def validate_license_format(license_number, country):
    """Validate the format of the entered license number against the country's pattern."""
    country = country.strip().title()
    pattern = license_patterns.get(country)
    if not pattern:
        return False, f"No pattern available for country: {country}"

    if not re.match(pattern, license_number):
        return False, "Entered license number does not match the expected format."
    
    return True, "License number format is valid."

def validate_license_number(text, license_number):
    """Validate the extracted license number from the image."""
    license_number = license_number.strip()  # Clean input license number
    # Check if the license number is in the extracted text
    if license_number in text:
        return True, "License validation successful."
    else:
        return False, "License number not found in the certificate."

@app.route('/licence')
def license_form():
    return render_template('licence.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    country = request.form['country']
    license_number = request.form['license_number']
    image_file = request.files['certificate_image']

    # Validate license number format first
    is_valid_format, format_message = validate_license_format(license_number, country)
    if not is_valid_format:
        return render_template('result.html', result='error', error_message=format_message)

    if image_file:
        image_path = f'./uploads/{image_file.filename}'
        image_file.save(image_path)
        
        processed_image = preprocess_image(image_path)
        if processed_image is None:
            return render_template('result.html', result='error', error_message="Error loading the image.")

        extracted_text = extract_text(processed_image)
        
        is_valid, message = validate_license_number(extracted_text, license_number)
        
        # Clean up uploaded file after processing
        os.remove(image_path)
        
        if is_valid:
            return render_template('result.html', result='success')
        else:
            return render_template('result.html', result='error', error_message=message)

    return render_template('result.html', result='error', error_message="No image uploaded.")


@app.route('/doctor_form')
def doctor_form():
    return render_template('doctor_form.html')

@app.route('/submit_doctor', methods=['POST'])
def submit_doctor():
    doctor = Doctor(
        username=request.form['username'],
        password=generate_password_hash(request.form['password']),  # Hash the password for doctors too
        first_name=request.form['first_name'],
        last_name=request.form['last_name'],
        gender=request.form['gender'],
        date_of_birth=request.form['date_of_birth'],
        contact_number=request.form['contact_number'],
        email=request.form['email'],
        address=request.form['address'],
        medical_license_number=request.form['medical_license_number'],
        speciality=request.form['specialty'],
        education=request.form['education'],
        years_of_experience=request.form['years_of_experience'],
        hospital_affiliation=request.form['hospital_affiliation'],
        languages_spoken=request.form['languages_spoken'],
    )
    db.session.add(doctor)
    db.session.commit()
    return redirect(url_for('welcome', user=doctor.first_name, user_type='Doctor'))


@app.route('/welcome')
def welcome():
    user = request.args.get('user')
    user_type = request.args.get('user_type')
    return render_template('welcome.html', user={'first_name': user, 'type': user_type})

# Landing page
@app.route('/landing')
def landing():
    return render_template('main.html')

# Symptom input page
@app.route('/symptom_input')
def symptom_input():
    return render_template('symptom.html')

# Symptom analysis route
@app.route('/analyze_symptoms', methods=['POST'])
def analyze_symptoms():
    symptoms = request.form['symptoms']
    # Get diseases and tests based on symptoms
    diseases = get_diseases_for_symptoms(symptoms)
    tests = predict_tests(symptoms)
    
    # Render the result page with diseases and tests
    return render_template('symptom_analysis.html', symptoms=symptoms, diseases=diseases, tests=tests)

# Page for uploading test result and MRI/X-ray images
@app.route('/test_result')
def index():
    return render_template('index.html', report_filenames=uploaded_reports)


# Upload medical reports route
@app.route('/upload_report', methods=['POST'])
def upload_report():
    files = request.files.getlist('report_files')  # multiple files
    for file in files:
        if file and file.filename.endswith(('.jpeg', '.jpg', '.png', '.webp')):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            if file.filename not in uploaded_reports:
                uploaded_reports.append(file.filename)  # store only filename
    return redirect(url_for('index'))


@app.route('/predict', methods=['POST'])
def predict():
    if not uploaded_reports:
        # No reports uploaded
        return render_template(
            'disease_result.html',
            prediction=None,
            doctors=[],
            message="Please upload at least one medical report to get a prediction."
        )

    # Run predictions on uploaded report images
    report_predictions = [
        predict_from_report(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        for filename in uploaded_reports
    ]

    final_prediction = Counter(report_predictions).most_common(1)[0][0] if report_predictions else "No disease detected"

    # Clear uploaded files for the next session
    uploaded_reports.clear()

    try:
        patient_name = current_user.username if current_user.is_authenticated else "Guest"
    except Exception as e:
        print(f"Error retrieving current user: {e}")
        patient_name = "Guest"

    # Determine medical specialization
    medical_specialization = specialization_analysis.get_specialization(final_prediction)
    print(f"Predicted Disease: {final_prediction}")
    print(f"Medical Specialization: {medical_specialization}")

    # Retrieve doctors
    doctors_list = specialization_analysis.get_doctors_by_specialization(medical_specialization) if medical_specialization else []

    # Decide message for user
    message = ""
    if not medical_specialization and final_prediction != "No disease detected":
        message = "No matching specialization found for the predicted disease."
    elif final_prediction == "No disease detected":
        message = "No disease detected from the uploaded report."

    return render_template(
        'disease_result.html',
        prediction=final_prediction,
        doctors=doctors_list,
        message=message
    )


# Notification model
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_first_name = db.Column(db.String, nullable=False)
    doctor_last_name = db.Column(db.String, nullable=False)
    patient_first_name = db.Column(db.String, nullable=False)
    patient_last_name = db.Column(db.String, nullable=False)
    disease = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/disease_result')
def disease_result():
    specialization = request.args.get('specialization')  # Assume specialization is passed as a query parameter
    patient_name = request.args.get('patient_name')      # Patient's name passed as a query parameter
    prediction = request.args.get('prediction')          # Predicted disease

    # Fetch doctors with the required specialization
    doctors = Doctor.query.filter_by(speciality=specialization).all()
    return render_template('disease_result.html', doctors=doctors, patient_name=patient_name, prediction=prediction)

@app.route('/connect_doctor', methods=['POST'])
def connect_doctor():
    data = request.get_json()
    notification = Notification(
        doctor_first_name=data['doctorFirstName'],
        doctor_last_name=data['doctorLastName'],
        patient_first_name=data['patientFirstName'],
        patient_last_name=data['patientLastName'],
        disease=data['disease']
    )
    db.session.add(notification)
    db.session.commit()
    return jsonify({'message': 'Notification sent to doctor.'}), 200


@app.route('/get_notifications', methods=['GET'])
def get_notifications():
    doctor_first_name = session.get('doctor_first_name')
    doctor_last_name = session.get('doctor_last_name')
    
    if doctor_first_name and doctor_last_name:
        # Retrieve notifications for the specific logged-in doctor
        notifications = Notification.query.filter_by(
            doctor_first_name=doctor_first_name,
            doctor_last_name=doctor_last_name
        ).order_by(Notification.timestamp.desc()).all()
        
        notifications_list = [{
            'patient_name': f"{notif.patient_first_name} {notif.patient_last_name}",
            'disease': notif.disease,
            'timestamp': notif.timestamp
        } for notif in notifications]
    else:
        # Retrieve all notifications if no specific doctor is logged in
        notifications = Notification.query.all()
        notifications_list = [{
            'id': n.id,
            'message': f"Connected regarding {n.disease} to doctor {n.doctor_first_name} {n.doctor_last_name}."
        } for n in notifications]  

    return jsonify({'notifications': notifications_list}), 200


@app.route('/view_patient_details', methods=['POST'])
def view_patient_details():
    data = request.get_json()
    first_name = data.get('firstName')
    last_name = data.get('lastName')

    # Retrieve patient details from Notification table based on doctor's first and last name
    notification = Notification.query.filter_by(doctor_first_name=first_name, doctor_last_name=last_name).first()
    if notification:
        return jsonify({
            'success': True,
            'patientFirstName': notification.patient_first_name,
            'patientLastName': notification.patient_last_name,
            'disease': notification.disease
        })
    else:
        return jsonify({'success': False, 'message': 'No patient details found for this doctor.'})
    

@app.route('/get_complete_patient_details', methods=['POST']) 
def get_complete_patient_details():
    data = request.get_json()
    patient_first_name = data.get('patientFirstName')
    patient_last_name = data.get('patientLastName')

    # Retrieve the complete details from Patient table based on patient's first and last name
    patient = Patient.query.filter_by(first_name=patient_first_name, last_name=patient_last_name).first()
    if patient:
        # Define the ordered fields to include in the response (excluding username and password)
        ordered_fields = [
            'first_name', 'last_name', 'age', 'gender', 'date_of_birth',
            'contact_number', 'email', 'address', 'medical_history', 
            'allergies', 'emergency_contact_name', 'emergency_contact_number'
        ]
        # Create ordered dictionary of patient details
        patient_data = {field: getattr(patient, field) for field in ordered_fields}
        return jsonify({'success': True, 'details': patient_data})
    else:
        return jsonify({'success': False, 'message': 'Patient details not found.'})


class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    age = db.Column(db.Integer)
    blood_group = db.Column(db.String(10))
    gender = db.Column(db.String(10))
    symptoms = db.Column(db.String(100))
    symptom_duration = db.Column(db.String(50))
    frequency_of_symptoms = db.Column(db.String(50))
    pain_level = db.Column(db.Integer)
    prior_symptoms = db.Column(db.String(10))
    medications_for_symptoms = db.Column(db.String(10))  
    allergies = db.Column(db.String(10))
    contact_with_sick = db.Column(db.String(10)) 
    recent_travel = db.Column(db.String(10))
    prior_health = db.Column(db.String(10))  
    mood_changes = db.Column(db.String(10))
    existing_conditions = db.Column(db.String(10))  
    diet_changes = db.Column(db.String(50))
    smoking_tobacco = db.Column(db.String(10)) 
    pregnancy_breastfeeding = db.Column(db.String(10))
    current_medications = db.Column(db.String(50))
    healthcare_provider = db.Column(db.String(10))
    appetite_weight_changes = db.Column(db.String(10))
    recent_injuries = db.Column(db.String(10))
    regular_exercise = db.Column(db.String(10))
    alcohol_consumption = db.Column(db.String(20))
    high_stress = db.Column(db.String(10))
    sleep_difficulties = db.Column(db.String(10))
    dietary_restrictions = db.Column(db.String(50))
    family_illness_history = db.Column(db.String(10))
    specified_illnesses = db.Column(db.String(50))  
    recent_vaccination = db.Column(db.String(10))
    vision_hearing_changes = db.Column(db.String(10))
    supplements_remedies = db.Column(db.String(50))
    headache_frequency = db.Column(db.String(20))
    bowel_urinary_changes = db.Column(db.String(10))
    environmental_exposure = db.Column(db.String(10))
    safe_home = db.Column(db.String(10))
    mobility_issues = db.Column(db.String(10))
    dental_checkup = db.Column(db.String(10))
    quality_of_life = db.Column(db.String(10))

# Form fields as a dictionary
fields = [
    {"question": "First Name", "type": "text", "name": "first_name"},
    {"question": "Last Name", "type": "text", "name": "last_name"},
    {"question": "Age", "type": "number", "name": "age"},
    {"question": "Blood Group", "type": "text", "name": "blood_group"},
    {"question": "Gender", "type": "select", "name": "gender", "options": ["Male", "Female", "Others"]},
    {"question": "Symptoms ", "type": "text", "name": "symptoms"},
    {"question": "Symptom Duration", "type": "text", "name": "symptom_duration", "placeholder": "E.g., '3 days', '1 week'"},
    {"question": "Frequency of Symptoms", "type": "select", "name": "frequency_of_symptoms", "options": ["Constantly", "Occasionally"]},
    {"question": "Pain/Discomfort Level (1-10)", "type": "number", "name": "pain_level"},
    {"question": "Prior Similar Symptoms", "type": "select", "name": "prior_symptoms", "options": ["Yes", "No"]},
    {"question": "Medications Taken for Symptoms", "type": "select", "name": "medications_for_symptoms", "options": ["Yes", "No"]},
    {"question": "Allergies", "type": "select", "name": "allergies", "options": ["Yes", "No"]},
    {"question": "Contact with Sick Individuals Recently", "type": "select", "name": "contact_with_sick", "options": ["Yes", "No"]},
    {"question": "Recent Travel", "type": "select", "name": "recent_travel", "options": ["Yes", "No"]},
    {"question": "Health Prior to Symptoms", "type": "select", "name": "prior_health", "options": ["Excellent", "Good", "Fair", "Poor"]},
    {"question": "Mood Changes or Irritability", "type": "select", "name": "mood_changes", "options": ["Yes", "No"]},
    {"question": "Existing Health Conditions (e.g., diabetes, hypertension)", "type": "select", "name": "existing_conditions", "options": ["Yes", "No"]},
    {"question": "Diet Pattern Changes", "type": "text", "name": "diet_changes"},
    {"question": "Smoking or Tobacco Use", "type": "select", "name": "smoking_tobacco", "options": ["Yes", "No"]},
    {"question": "Pregnancy/Breastfeeding (if applicable)", "type": "select", "name": "pregnancy_breastfeeding", "options": ["Yes", "No"]},
    {"question": "Current Medications", "type": "text", "name": "current_medications"},
    {"question": "Regular Healthcare Provider", "type": "select", "name": "healthcare_provider", "options": ["Yes", "No"]},
    {"question": "Appetite or Weight Changes", "type": "select", "name": "appetite_weight_changes", "options": ["Yes", "No"]},
    {"question": "Recent injuries/trauma", "type": "select", "name": "recent_injuries", "options": ["Yes", "No"]},
    {"question": "Regular exercise", "type": "select", "name": "regular_exercise", "options": ["Yes", "No"]},
    {"question": "Alcohol consumption", "type": "select", "name": "alcohol_consumption", "options": ["Never", "Occasionally", "Regularly"]},
    {"question": "High stress recently", "type": "select", "name": "high_stress", "options": ["Yes", "No"]},
    {"question": "Sleep difficulties", "type": "select", "name": "sleep_difficulties", "options": ["Yes", "No"]},
    {"question": "Dietary restrictions", "type": "text", "name": "dietary_restrictions"},
    {"question": "Family illness history", "type": "select", "name": "family_illness_history", "options": ["Yes", "No"]},
    {"question": "Specify illnesses", "type": "text", "name": "specified_illnesses"},
    {"question": "Recent vaccination", "type": "select", "name": "recent_vaccination", "options": ["Yes", "No"]},
    {"question": "Vision/hearing changes", "type": "select", "name": "vision_hearing_changes", "options": ["Yes", "No"]},
    {"question": "Supplements/herbal remedies", "type": "text", "name": "supplements_remedies"},
    {"question": "Headache frequency", "type": "select", "name": "headache_frequency", "options": ["Rarely", "Occasionally", "Frequently"]},
    {"question": "Bowel/urinary changes", "type": "select", "name": "bowel_urinary_changes", "options": ["Yes", "No"]},
    {"question": "Environmental exposure (e.g., pollution, chemicals)", "type": "select", "name": "environmental_exposure", "options": ["Yes", "No"]},
    {"question": "Safe home environment", "type": "select", "name": "safe_home", "options": ["Yes", "No"]},
    {"question": "Mobility issues", "type": "select", "name": "mobility_issues", "options": ["Yes", "No"]},
    {"question": "Dental check-up in last year", "type": "select", "name": "dental_checkup", "options": ["Yes", "No"]},
    {"question": "Quality of life (1-10)", "type": "number", "name": "quality_of_life"}
]

# Route to open the form page
@app.route("/form")
def form():
    return render_template("form.html", fields=fields)

# Handle form submission
@app.route('/submit', methods=['POST'])
def submit():
    # Get symptoms input as a comma-separated string and split it into a list
    symptoms = request.form.get('symptoms')
    symptoms_list = [symptom.strip() for symptom in symptoms.split(',')] if symptoms else []

    # Store symptoms as a JSON string
    response = Response(
        first_name=request.form.get('first_name'),
        last_name=request.form.get('last_name'),
        age=request.form.get('age'),
        blood_group=request.form.get('blood_group'),
        gender=request.form.get('gender'),
        symptoms=json.dumps(symptoms_list),  # Store as JSON string
        symptom_duration=request.form.get('symptom_duration'),
        frequency_of_symptoms=request.form.get('frequency_of_symptoms'),
        pain_level=request.form.get('pain_level'),
        prior_symptoms=request.form.get('prior_symptoms'),
        medications_for_symptoms=request.form.get('medications_for_symptoms'),
        allergies=request.form.get('allergies'),
        contact_with_sick=request.form.get('contact_with_sick'),
        recent_travel=request.form.get('recent_travel'),
        prior_health=request.form.get('prior_health'),
        mood_changes=request.form.get('mood_changes'),
        existing_conditions=request.form.get('existing_conditions'),
        diet_changes=request.form.get('diet_changes'),
        smoking_tobacco=request.form.get('smoking_tobacco'),
        pregnancy_breastfeeding=request.form.get('pregnancy_breastfeeding'),
        current_medications=request.form.get('current_medications'),
        healthcare_provider=request.form.get('healthcare_provider'),
        appetite_weight_changes=request.form.get('appetite_weight_changes'),
        recent_injuries=request.form.get('recent_injuries'),
        regular_exercise=request.form.get('regular_exercise'),
        alcohol_consumption=request.form.get('alcohol_consumption'),
        high_stress=request.form.get('high_stress'),
        sleep_difficulties=request.form.get('sleep_difficulties'),
        dietary_restrictions=request.form.get('dietary_restrictions'),
        family_illness_history=request.form.get('family_illness_history'),
        specified_illnesses=request.form.get('specified_illnesses'),
        recent_vaccination=request.form.get('recent_vaccination'),
        vision_hearing_changes=request.form.get('vision_hearing_changes'),
        supplements_remedies=request.form.get('supplements_remedies'),
        headache_frequency=request.form.get('headache_frequency'),
        bowel_urinary_changes=request.form.get('bowel_urinary_changes'),
        environmental_exposure=request.form.get('environmental_exposure'),
        safe_home=request.form.get('safe_home'),
        mobility_issues=request.form.get('mobility_issues'),
        dental_checkup=request.form.get('dental_checkup'),
        quality_of_life=request.form.get('quality_of_life')
    )
    db.session.add(response)
    db.session.commit()

    return redirect(url_for('report', response_id=response.id))

@app.template_filter('from_json')
def from_json(value):
    # Only parse the value if it is a string (not already a Python object like a list or dict)
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return []  # Return empty list if JSON is malformed
    return value  # If value is not a string, return it as is


@app.route('/report/<int:response_id>')
def report(response_id):
    response = Response.query.get(response_id)
    
    # If symptoms are stored as a JSON string, load it into a Python object
    symptoms = response.symptoms
    if isinstance(symptoms, str):
        try:
            symptoms = json.loads(symptoms)
        except json.JSONDecodeError:
            symptoms = []  # Return an empty list in case of a malformed JSON string
    
    return render_template('report.html', response=response, symptoms=symptoms)

@app.route('/health')
def health():
    return render_template('health_report.html')

@app.route("/report_final")
def report_final():
    first_name = request.args.get("firstName")
    last_name = request.args.get("lastName")
    
    # Fetch data from the database based on first name and last name
    patient_data = db.session.query(Response).filter_by(first_name=first_name, last_name=last_name).first()

    if patient_data:
        # Check if symptoms is a string, then convert it to a list
        if isinstance(patient_data.symptoms, str):
            patient_data.symptoms = patient_data.symptoms.split(", ")  # assuming symptoms are comma-separated

        # Pass the patient data to the report_final.html page
        return render_template("report_final.html", patient=patient_data)
    else:
        return "No patient found with that name.", 404




# Define the ChatMessage model
class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_first_name = db.Column(db.String(50))
    patient_last_name = db.Column(db.String(50))
    doctor_first_name = db.Column(db.String(50))
    doctor_last_name = db.Column(db.String(50))
    message = db.Column(db.Text)
    sender_role = db.Column(db.String(20))  # 'patient' or 'doctor'

    def __init__(self, patient_first_name, patient_last_name, doctor_first_name, doctor_last_name, message, sender_role):
        self.patient_first_name = patient_first_name
        self.patient_last_name = patient_last_name
        self.doctor_first_name = doctor_first_name
        self.doctor_last_name = doctor_last_name
        self.message = message
        self.sender_role = sender_role

@app.route('/connect')
def connect():
    return render_template('chat.html')


# Route to handle chat submission and retrieval
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    role = data['role']
    first_name = data['first_name']
    last_name = data['last_name']
    other_name = data['other_name']
    message = data.get('message')

    # Save message if provided
    if message:
        if role == 'patient':
            chat_message = ChatMessage(patient_first_name=first_name, patient_last_name=last_name,
                                       doctor_first_name=other_name['first_name'], doctor_last_name=other_name['last_name'],
                                       message=message, sender_role=role)
        else:
            chat_message = ChatMessage(patient_first_name=other_name['first_name'], patient_last_name=other_name['last_name'],
                                       doctor_first_name=first_name, doctor_last_name=last_name,
                                       message=message, sender_role=role)
        db.session.add(chat_message)
        db.session.commit()

    # Retrieve messages between the specific doctor and patient
    chat_history = ChatMessage.query.filter_by(
        patient_first_name=first_name if role == 'patient' else other_name['first_name'],
        patient_last_name=last_name if role == 'patient' else other_name['last_name'],
        doctor_first_name=other_name['first_name'] if role == 'patient' else first_name,
        doctor_last_name=other_name['last_name'] if role == 'patient' else last_name
    ).all()

    return jsonify([{'role': msg.sender_role, 'message': msg.message} for msg in chat_history])

# Start the app with the proper context for db.create_all()
if __name__ == '__main__':
    # Use PORT provided by host (Render/Heroku). Default to 5000 locally.
    port = int(os.environ.get("PORT", 5000))
    # Never run debug=True in production
    app.run(host="0.0.0.0", port=port, debug=False)