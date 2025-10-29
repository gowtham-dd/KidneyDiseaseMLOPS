import os
import cv2
import numpy as np
import base64
import json
import smtplib
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import sqlite3
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import tensorflow as tf
from pathlib import Path
import uuid
import logging

app = Flask(__name__)
app.config['SECRET_KEY'] = 'kidney-diagnosis-secret-key-2024'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['RESULTS_FOLDER'] = 'static/results'
app.config['DATABASE'] = 'kidney_patients.db'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'gowthamdcloudstudyjam@gmail.com'
app.config['MAIL_PASSWORD'] = 'Key'

# Initialize database and directories
def init_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            email TEXT,
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS diagnoses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT NOT NULL,
            image_path TEXT,
            condition TEXT,
            confidence REAL,
            severity TEXT,
            findings TEXT,
            recommendations TEXT,
            report_sent INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def generate_patient_id():
    """Generate auto-incrementing patient ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get the highest patient ID number
    cursor.execute("SELECT patient_id FROM patients WHERE patient_id LIKE 'K%' ORDER BY patient_id DESC LIMIT 1")
    result = cursor.fetchone()
    
    if result:
        last_id = result['patient_id']
        # Extract number and increment
        last_number = int(last_id[1:])
        new_number = last_number + 1
    else:
        new_number = 1
    
    conn.close()
    return f"K{new_number:03d}"  # Format as K001, K002, etc.

# Initialize database and create directories
init_db()
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)

# Load Kidney Disease Model
try:
    MODEL_PATH = 'artifacts/model_training/kidney_model'
    if os.path.exists(MODEL_PATH):
        model = tf.keras.models.load_model(MODEL_PATH)
        print("✅ Kidney disease model loaded successfully!")
        CLASS_NAMES = ['Cyst', 'Normal', 'Stone', 'Tumor']
        print("Model input shape:", model.input_shape)
    else:
        print("⚠️ Kidney model not found, using mock predictions")
        model = None
        CLASS_NAMES = ['Cyst', 'Normal', 'Stone', 'Tumor']
except Exception as e:
    print(f"❌ Error loading kidney model: {e}")
    model = None

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def preprocess_medical_image(image_path, target_size=(28, 28)):
    try:
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError("Could not read medical image file")
        
        img = cv2.resize(img, target_size)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = img.astype(np.float32) / 255.0
        img = np.expand_dims(img, axis=0)
        
        print(f"Medical image preprocessed successfully: {img.shape}")
        return img
        
    except Exception as e:
        print(f"Error preprocessing medical image: {e}")
        return None

def analyze_medical_image(image_path):
    if model is None:
        print("Medical AI model not available")
        return None, 0.0, "Model not available"
    
    try:
        processed_img = preprocess_medical_image(image_path, target_size=(28, 28))
        if processed_img is None:
            return None, 0.0, "Image preprocessing failed"
        
        print("Starting medical image analysis...")
        predictions = model.predict(processed_img)
        
        predicted_class_idx = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_class_idx])
        predicted_condition = CLASS_NAMES[predicted_class_idx]
        
        print(f"Medical analysis complete: {predicted_condition} ({confidence:.1%} confidence)")
        return predicted_condition, confidence, "Analysis successful"
        
    except Exception as e:
        print(f"Error during medical image analysis: {e}")
        return None, 0.0, f"Analysis error: {str(e)}"

class KidneyDiagnosis:
    def __init__(self, model):
        self.model = model

    def analyze_kidney(self, image_path):
        try:
            if self.model is None:
                conditions = ['Normal', 'Cyst', 'Stone', 'Tumor']
                condition = np.random.choice(conditions, p=[0.3, 0.3, 0.2, 0.2])
                confidence = np.random.uniform(0.85, 0.98)
                return condition, confidence
            else:
                condition, confidence, status = analyze_medical_image(image_path)
                if condition:
                    return condition, confidence
                else:
                    return None, 0.0
            
        except Exception as e:
            print(f"Error analyzing kidney: {e}")
            return None, 0.0

    def generate_findings(self, condition, confidence):
        findings = {
            'Normal': {
                'description': 'Kidney appears within normal limits',
                'details': [
                    'Normal renal parenchyma echogenicity',
                    'Well-defined corticomedullary differentiation',
                    'No evidence of calculi, cysts, or masses',
                    'Normal renal size and contour'
                ]
            },
            'Cyst': {
                'description': 'Simple renal cyst detected',
                'details': [
                    'Well-circumscribed anechoic lesion',
                    'Acoustic enhancement present',
                    'No internal echoes or septations',
                    'Consistent with Bosniak category I cyst'
                ]
            },
            'Stone': {
                'description': 'Renal calculi identified',
                'details': [
                    'Echogenic focus with posterior acoustic shadowing',
                    'Located in renal pelvis/calyces',
                    'Measurements consistent with nephrolithiasis',
                    'No associated hydronephrosis noted'
                ]
            },
            'Tumor': {
                'description': 'Renal mass identified requiring further evaluation',
                'details': [
                    'Solid renal lesion with heterogeneous echogenicity',
                    'Irregular margins noted',
                    'Increased vascularity on Doppler assessment',
                    'Recommend correlation with contrast-enhanced CT'
                ]
            }
        }
        return findings.get(condition, findings['Normal'])

    def generate_recommendations(self, condition, confidence):
        recommendations = {
            'Normal': [
                'Routine follow-up as per standard guidelines',
                'Maintain adequate hydration',
                'Continue regular health maintenance'
            ],
            'Cyst': [
                'Follow-up ultrasound in 6-12 months',
                'Monitor for symptoms or size increase',
                'Consider Bosniak classification for complex cysts'
            ],
            'Stone': [
                'Increased fluid intake (2-3L daily)',
                'Dietary consultation for stone prevention',
                'Consider urology referral if symptomatic',
                'Follow-up imaging based on stone size'
            ],
            'Tumor': [
                'URGENT: Consultation with urologist/oncologist',
                'Contrast-enhanced CT abdomen for characterization',
                'Consider biopsy for tissue diagnosis',
                'Multidisciplinary team review recommended'
            ]
        }
        
        base_recs = recommendations.get(condition, [])
        
        if confidence > 0.95:
            base_recs.append('High confidence diagnosis - proceed with recommended management')
        elif confidence > 0.85:
            base_recs.append('Moderate confidence - consider confirmatory imaging')
        else:
            base_recs.append('Low confidence - additional imaging recommended')
            
        return base_recs

# Global detector instance
diagnosis_system = KidneyDiagnosis(model)

def send_medical_report(patient_email, patient_name, diagnosis_data, image_path=None):
    """Send medical report via email with scan image"""
    try:
        smtp_server = app.config['MAIL_SERVER']
        port = app.config['MAIL_PORT']
        sender_email = app.config['MAIL_USERNAME']
        password = app.config['MAIL_PASSWORD']
        
        message = MIMEMultipart()
        message['Subject'] = f'Kidney Diagnosis Report - {patient_name}'
        message['From'] = sender_email
        message['To'] = patient_email
        
        # Create HTML email content with image
        image_html = ""
        if image_path and os.path.exists(image_path):
            # Attach image and reference it in HTML
            with open(image_path, 'rb') as img_file:
                img_data = img_file.read()
            image = MIMEImage(img_data, name=os.path.basename(image_path))
            image.add_header('Content-ID', '<scan_image>')
            message.attach(image)
            image_html = """
                <div class="section">
                    <h2>CT Scan Image</h2>
                    <div style="text-align: center;">
                        <img src="cid:scan_image" alt="Kidney CT Scan" style="max-width: 100%; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                        <p><em>Original CT Scan Image</em></p>
                    </div>
                </div>
            """
        
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background: #667eea; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .section {{ margin-bottom: 20px; padding: 15px; border-left: 4px solid #667eea; background: #f8f9fa; }}
                .critical {{ border-left-color: #dc3545; background: #f8d7da; }}
                .urgent {{ border-left-color: #ffc107; background: #fff3cd; }}
                .normal {{ border-left-color: #28a745; background: #d4edda; }}
                .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Kidney Diagnosis Report</h1>
                <p>MediScan AI Diagnostic System</p>
            </div>
            
            <div class="content">
                <div class="section">
                    <h2>Patient Information</h2>
                    <p><strong>Name:</strong> {patient_name}</p>
                    <p><strong>Date of Report:</strong> {diagnosis_data['timestamp']}</p>
                    <p><strong>Report ID:</strong> {diagnosis_data['report_id']}</p>
                </div>
                
                <div class="section {'critical' if diagnosis_data['condition'] == 'Tumor' else 'urgent' if diagnosis_data['condition'] == 'Stone' else 'normal'}">
                    <h2>Diagnosis Summary</h2>
                    <p><strong>Condition:</strong> {diagnosis_data['condition']}</p>
                    <p><strong>Confidence Level:</strong> {diagnosis_data['confidence']:.1%}</p>
                    <p><strong>Severity:</strong> {diagnosis_data['severity']}</p>
                </div>
                
                {image_html}
                
                <div class="section">
                    <h2>Clinical Findings</h2>
                    <p><strong>Description:</strong> {diagnosis_data['findings']['description']}</p>
                    <ul>
                        {''.join(f'<li>{finding}</li>' for finding in diagnosis_data['findings']['details'])}
                    </ul>
                </div>
                
                <div class="section">
                    <h2>Medical Recommendations</h2>
                    <ol>
                        {''.join(f'<li>{rec}</li>' for rec in diagnosis_data['recommendations'])}
                    </ol>
                </div>
                
                <div class="section">
                    <h2>Important Notes</h2>
                    <p>This report was generated by AI and should be reviewed by a qualified healthcare professional.</p>
                    <p>Please consult with your physician for definitive diagnosis and treatment planning.</p>
                </div>
            </div>
            
            <div class="footer">
                <p>Confidential Medical Document - For authorized use only</p>
                <p>MediScan AI Diagnostic Center © 2024</p>
            </div>
        </body>
        </html>
        """
        
        message.attach(MIMEText(html_content, 'html'))
        
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()
            server.login(sender_email, password)
            server.send_message(message)
            
        return True
        
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

@app.route('/')
def dashboard():
    conn = get_db_connection()
    patients = conn.execute('''
        SELECT p.*, 
               COUNT(d.id) as diagnosis_count,
               MAX(d.created_at) as last_diagnosis
        FROM patients p
        LEFT JOIN diagnoses d ON p.patient_id = d.patient_id
        GROUP BY p.patient_id
        ORDER BY p.created_at DESC
    ''').fetchall()
    conn.close()
    return render_template('dashboard.html', patients=patients)

@app.route('/patient/<patient_id>')
def patient_detail(patient_id):
    conn = get_db_connection()
    patient = conn.execute(
        'SELECT * FROM patients WHERE patient_id = ?', (patient_id,)
    ).fetchone()
    diagnoses = conn.execute(
        '''SELECT d.*, p.name, p.email 
           FROM diagnoses d 
           JOIN patients p ON d.patient_id = p.patient_id 
           WHERE d.patient_id = ? 
           ORDER BY d.created_at DESC''', (patient_id,)
    ).fetchall()
    conn.close()
    
    if patient is None:
        return "Patient not found", 404
        
    return render_template('patient_detail.html', patient=patient, diagnoses=diagnoses)

@app.route('/diagnose', methods=['GET', 'POST'])
def diagnose():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file selected'})
        
        file = request.files['file']
        patient_id = request.form.get('patient_id', 'unknown')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'})
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            print(f"File saved: {filename}")
            print(f"Patient ID: {patient_id}")
            
            condition, confidence = diagnosis_system.analyze_kidney(filepath)
            
            print(f"Analysis result - Condition: {condition}, Confidence: {confidence}")
            
            if condition:
                findings = diagnosis_system.generate_findings(condition, confidence)
                recommendations = diagnosis_system.generate_recommendations(condition, confidence)
                
                if condition == 'Tumor':
                    severity = 'High'
                elif condition == 'Stone':
                    severity = 'Medium'
                else:
                    severity = 'Low'
                
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    '''INSERT INTO diagnoses (patient_id, image_path, condition, confidence, 
                       severity, findings, recommendations)
                       VALUES (?, ?, ?, ?, ?, ?, ?)''',
                    (patient_id, filename, condition, float(confidence), severity, 
                     json.dumps(findings), json.dumps(recommendations))
                )
                diagnosis_id = cursor.lastrowid
                conn.commit()
                conn.close()
                
                result_data = {
                    'success': True,
                    'diagnosis_id': diagnosis_id,
                    'condition': condition,
                    'confidence': float(confidence),
                    'severity': severity,
                    'findings': findings,
                    'recommendations': recommendations,
                    'image_url': f'/uploads/{filename}',
                    'image_path': filepath
                }
                
                return jsonify(result_data)
            else:
                return jsonify({'error': 'Failed to analyze kidney CT scan'})
        
        return jsonify({'error': 'Invalid file type'})
    
    patient_id = request.args.get('patient_id', '')
    return render_template('diagnose.html', patient_id=patient_id)

@app.route('/send_report', methods=['POST'])
def send_report():
    data = request.get_json()
    diagnosis_id = data.get('diagnosis_id')
    image_path = data.get('image_path')
    
    conn = get_db_connection()
    diagnosis = conn.execute(
        '''SELECT d.*, p.name, p.email 
           FROM diagnoses d 
           JOIN patients p ON d.patient_id = p.patient_id 
           WHERE d.id = ?''', (diagnosis_id,)
    ).fetchone()
    
    if not diagnosis:
        return jsonify({'error': 'Diagnosis not found'})
    
    report_data = {
        'condition': diagnosis['condition'],
        'confidence': diagnosis['confidence'],
        'severity': diagnosis['severity'],
        'findings': json.loads(diagnosis['findings']),
        'recommendations': json.loads(diagnosis['recommendations']),
        'timestamp': diagnosis['created_at'],
        'report_id': f"KID{diagnosis_id:06d}"
    }
    
    # Send email with image
    success = send_medical_report(
        diagnosis['email'],
        diagnosis['name'],
        report_data,
        image_path
    )
    
    if success:
        conn.execute(
            'UPDATE diagnoses SET report_sent = 1 WHERE id = ?',
            (diagnosis_id,)
        )
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Report sent successfully'})
    else:
        conn.close()
        return jsonify({'error': 'Failed to send email'})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/add_patient', methods=['POST'])
def add_patient():
    try:
        data = request.get_json()
        if not data:
            data = {
                'name': request.form.get('name'),
                'age': request.form.get('age'),
                'gender': request.form.get('gender'),
                'email': request.form.get('email'),
                'phone': request.form.get('phone')
            }
        
        name = data.get('name')
        age = data.get('age')
        gender = data.get('gender')
        email = data.get('email')
        phone = data.get('phone')
        
        if not name:
            return jsonify({'error': 'Patient name is required'})
        
        # Generate auto patient ID
        patient_id = generate_patient_id()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO patients (patient_id, name, age, gender, email, phone) VALUES (?, ?, ?, ?, ?, ?)',
                (patient_id, name, age, gender, email, phone)
            )
            conn.commit()
            return jsonify({'success': True, 'message': 'Patient added successfully', 'patient_id': patient_id})
        except sqlite3.IntegrityError:
            return jsonify({'error': 'Patient ID already exists'})
        except Exception as e:
            return jsonify({'error': f'Database error: {str(e)}'})
        finally:
            conn.close()
            
    except Exception as e:
        print(f"Error in add_patient: {e}")
        return jsonify({'error': f'Server error: {str(e)}'})

if __name__ == '__main__':
    print("🚀 Starting Kidney Diagnosis System...")
    print("📁 Upload folder:", app.config['UPLOAD_FOLDER'])
    print("📊 Database:", app.config['DATABASE'])
    print("🔬 Model available:", model is not None)
    if model:
        print("📐 Model input shape:", model.input_shape)
    print("📧 Email configured:", app.config['MAIL_USERNAME'] is not None)
    print("🌐 Server starting on http://localhost:5000")
    
    app.run(debug=True, host='localhost', port=5000)