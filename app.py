import os
import cv2
import numpy as np
import base64
import json
import smtplib
import pickle
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import sqlite3
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import tensorflow as tf
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications.resnet50 import preprocess_input
from pathlib import Path
import uuid
import logging

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chest-diagnosis-secret-key-2024'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['RESULTS_FOLDER'] = 'static/results'
app.config['DATABASE'] = 'chest_patients.db'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'gowthamdcloudstudyjam@gmail.com'
app.config['MAIL_PASSWORD'] = 'Key'

# ──────────────────────────────────────────────
# Model configuration
# lung  → Keras .h5  (128×128 CNN)
# chest → Keras .h5  (128×128 CNN)
# pneumonia → ResNet50 features → PCA → XGBoost  (224×224)
# ──────────────────────────────────────────────
MODEL_CONFIG = {
    'lung': {
        'path': 'artifacts/model/lung_model.h5',
        'classes': ['Adenocarcinoma', 'Large Cell Carcinoma', 'Normal', 'Squamous Cell Carcinoma'],
        'label': 'Lung Cancer Detection',
        'icon': 'fa-lungs',
        'type': 'keras',
    },
    'chest': {
        'path': 'artifacts/model/chest_model.h5',
        'classes': ['COVID-19', 'Normal', 'Pneumonia-Bacterial', 'Pneumonia-Viral'],
        'label': 'Chest X-Ray Analysis',
        'icon': 'fa-x-ray',
        'type': 'keras',
    },
    'pneumonia': {
        # XGBoost + PCA pipeline – no .h5 used here
        'xgb_path': 'artifacts/model_training/pnemonia/xgb_model.pkl',
        'pca_path':  'artifacts/model_training/pnemonia/pca_model.pkl',
        'classes':   [],          # filled at load time from saved class_names
        'class_names_path': 'artifacts/model/pneumonia_class_names.pkl',
        'label': 'Pneumonia Detection (ResNet50 + PCA + XGBoost)',
        'icon': 'fa-viruses',
        'type': 'xgb',
    },
}

# ── Keras model cache (lazy) ──────────────────
_keras_models: dict = {}

def get_keras_model(scan_type):
    """Return (keras_model, class_names) for lung/chest, lazy-loaded."""
    if scan_type in _keras_models:
        return _keras_models[scan_type]
    cfg = MODEL_CONFIG[scan_type]
    try:
        if os.path.exists(cfg['path']):
            m = tf.keras.models.load_model(cfg['path'])
            print(f"✅ Keras model loaded for '{scan_type}': {cfg['path']}")
        else:
            print(f"⚠️  Keras model not found for '{scan_type}': {cfg['path']} – mock mode")
            m = None
        _keras_models[scan_type] = (m, cfg['classes'])
        return m, cfg['classes']
    except Exception as e:
        print(f"❌ Error loading Keras model '{scan_type}': {e}")
        _keras_models[scan_type] = (None, cfg['classes'])
        return None, cfg['classes']

# ── Pneumonia pipeline (ResNet50 + PCA + XGBoost) ────────────────
# These are loaded once at startup to avoid re-loading per request.
_resnet_extractor = None   # ResNet50 feature extractor (shared)
_pneumonia_pca    = None   # fitted PCA
_pneumonia_xgb    = None   # fitted XGBClassifier
_pneumonia_classes: list = ['Normal', 'Pneumonia']   # fallback default

PNEUMONIA_IMG_SIZE = 224   # ResNet50 expects 224×224

def _load_pneumonia_pipeline():
    """Load PCA and XGBoost pkl files. ResNet50 extractor is built separately."""
    global _pneumonia_pca, _pneumonia_xgb, _pneumonia_classes, _resnet_extractor

    cfg = MODEL_CONFIG['pneumonia']

    # ResNet50 feature extractor (no top, global avg pool)
    try:
        _resnet_extractor = ResNet50(weights='imagenet', include_top=False, pooling='avg')
        print("✅ ResNet50 feature extractor ready")
    except Exception as e:
        print(f"❌ ResNet50 load error: {e}")
        _resnet_extractor = None

    # PCA
    try:
        if os.path.exists(cfg['pca_path']):
            with open(cfg['pca_path'], 'rb') as f:
                _pneumonia_pca = pickle.load(f)
            print(f"✅ PCA loaded: {cfg['pca_path']}")
        else:
            print(f"⚠️  PCA file not found: {cfg['pca_path']} – mock mode")
    except Exception as e:
        print(f"❌ PCA load error: {e}")

    # XGBoost
    try:
        if os.path.exists(cfg['xgb_path']):
            with open(cfg['xgb_path'], 'rb') as f:
                _pneumonia_xgb = pickle.load(f)
            print(f"✅ XGBoost model loaded: {cfg['xgb_path']}")
        else:
            print(f"⚠️  XGBoost file not found: {cfg['xgb_path']} – mock mode")
    except Exception as e:
        print(f"❌ XGBoost load error: {e}")

    # Class names (saved during training as pkl)
    try:
        if os.path.exists(cfg['class_names_path']):
            with open(cfg['class_names_path'], 'rb') as f:
                _pneumonia_classes = pickle.load(f)
            MODEL_CONFIG['pneumonia']['classes'] = _pneumonia_classes
            print(f"✅ Pneumonia classes: {_pneumonia_classes}")
        else:
            # Use default and carry on
            _pneumonia_classes = ['Normal', 'Pneumonia']
            MODEL_CONFIG['pneumonia']['classes'] = _pneumonia_classes
            print(f"⚠️  Class names file not found – using default: {_pneumonia_classes}")
    except Exception as e:
        print(f"❌ Class names load error: {e}")

# Load the pneumonia pipeline once at startup
_load_pneumonia_pipeline()

# ──────────────────────────────────────────────
# Database
# ──────────────────────────────────────────────
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
            scan_type TEXT NOT NULL DEFAULT 'chest',
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
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT patient_id FROM patients WHERE patient_id LIKE 'C%' ORDER BY patient_id DESC LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    if result:
        last_number = int(result['patient_id'][1:])
        return f"C{last_number + 1:03d}"
    return "C001"

init_db()
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)

# ──────────────────────────────────────────────
# Image processing
# ──────────────────────────────────────────────
KERAS_TARGET_SIZE = (128, 128)   # lung / chest CNN models

def preprocess_for_keras(image_path):
    """Resize to 128×128, normalise to [0,1], add batch dim."""
    try:
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError("Could not read image file")
        img = cv2.resize(img, KERAS_TARGET_SIZE)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = img.astype(np.float32) / 255.0
        img = np.expand_dims(img, axis=0)
        print(f"Keras preprocess → shape {img.shape}")
        return img
    except Exception as e:
        print(f"Keras preprocess error: {e}")
        return None

def extract_resnet_features(image_path):
    """
    Replicate the training pipeline exactly:
      1. Read image with cv2
      2. Resize to 224×224
      3. Apply ResNet50 preprocess_input  (BGR→RGB conversion done internally)
      4. Predict with ResNet50 (no top, global avg pool) → 2048-d vector
    Returns a (1, 2048) numpy array, or None on failure.
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError("Could not read image file")
        img = cv2.resize(img, (PNEUMONIA_IMG_SIZE, PNEUMONIA_IMG_SIZE))
        # preprocess_input expects BGR (cv2 default) – matches training code
        img = preprocess_input(img.astype(np.float32))
        img = np.expand_dims(img, axis=0)                  # (1, 224, 224, 3)
        features = _resnet_extractor.predict(img, verbose=0)  # (1, 2048)
        print(f"ResNet50 features extracted: shape {features.shape}")
        return features
    except Exception as e:
        print(f"ResNet50 feature extraction error: {e}")
        return None

# ──────────────────────────────────────────────
# Unified analysis dispatcher
# ──────────────────────────────────────────────
def analyze_image(image_path, scan_type):
    """
    Route the image to the correct pipeline:
      • lung / chest  → Keras CNN (128×128)
      • pneumonia     → ResNet50 → PCA → XGBoost (224×224)
    Returns (condition: str, confidence: float, status: str)
    """
    cfg = MODEL_CONFIG.get(scan_type)
    if cfg is None:
        return None, 0.0, 'unknown_scan_type'

    # ── Pneumonia: ResNet50 + PCA + XGBoost ──────────────────────
    if scan_type == 'pneumonia':
        class_names = _pneumonia_classes

        # Mock if any component is missing
        if _resnet_extractor is None or _pneumonia_pca is None or _pneumonia_xgb is None:
            idx  = np.random.randint(len(class_names))
            conf = round(np.random.uniform(0.82, 0.97), 4)
            print(f"[MOCK pneumonia] → {class_names[idx]} ({conf:.1%})")
            return class_names[idx], conf, 'mock'

        # Step 1: extract 2048-d ResNet50 features
        features = extract_resnet_features(image_path)
        if features is None:
            return None, 0.0, 'feature_extraction_failed'

        # Step 2: PCA transform → 50-d vector
        features_pca = _pneumonia_pca.transform(features)   # (1, 50)
        print(f"PCA transform → shape {features_pca.shape}")

        # Step 3: XGBoost predict
        pred_idx  = int(_pneumonia_xgb.predict(features_pca)[0])
        # XGBoost predict_proba gives class probabilities
        proba     = _pneumonia_xgb.predict_proba(features_pca)[0]
        confidence = float(proba[pred_idx])
        condition  = class_names[pred_idx]
        print(f"[PNEUMONIA XGB] → {condition} ({confidence:.1%})")
        return condition, confidence, 'success'

    # ── Lung / Chest: Keras CNN ───────────────────────────────────
    model, class_names = get_keras_model(scan_type)

    if model is None:
        idx  = np.random.randint(len(class_names))
        conf = round(np.random.uniform(0.82, 0.97), 4)
        print(f"[MOCK {scan_type}] → {class_names[idx]} ({conf:.1%})")
        return class_names[idx], conf, 'mock'

    processed = preprocess_for_keras(image_path)
    if processed is None:
        return None, 0.0, 'preprocessing_failed'

    try:
        preds = model.predict(processed)
        idx   = int(np.argmax(preds[0]))
        conf  = float(preds[0][idx])
        cond  = class_names[idx]
        print(f"[{scan_type.upper()} CNN] → {cond} ({conf:.1%})")
        return cond, conf, 'success'
    except Exception as e:
        print(f"Keras prediction error: {e}")
        return None, 0.0, str(e)

# ──────────────────────────────────────────────
# Clinical content per scan type & condition
# ──────────────────────────────────────────────
FINDINGS_DB = {
    'lung': {
        'Normal': {
            'description': 'Lungs appear within normal limits on imaging',
            'details': [
                'Clear lung fields bilaterally',
                'Normal bronchovascular markings',
                'No focal consolidation or mass lesion identified',
                'Normal lung volumes and symmetry'
            ]
        },
        'Adenocarcinoma': {
            'description': 'Peripheral lung mass suggestive of adenocarcinoma',
            'details': [
                'Irregular peripheral nodule/mass identified',
                'Ground-glass opacity with partial solid component',
                'Possible pleural involvement',
                'Correlate with PET-CT for staging'
            ]
        },
        'Large Cell Carcinoma': {
            'description': 'Large peripheral mass detected, consistent with large cell carcinoma',
            'details': [
                'Large heterogeneous peripheral mass',
                'Possible necrosis within the lesion',
                'Mediastinal lymph node enlargement suspected',
                'Urgent multidisciplinary team review required'
            ]
        },
        'Squamous Cell Carcinoma': {
            'description': 'Central mass lesion consistent with squamous cell carcinoma',
            'details': [
                'Central hilar mass with endobronchial involvement',
                'Post-obstructive atelectasis noted',
                'Cavitation may be present',
                'Mediastinal staging required'
            ]
        },
    },
    'chest': {
        'Normal': {
            'description': 'Chest X-ray appears within normal limits',
            'details': [
                'Clear lung fields with no consolidation',
                'Normal cardiac silhouette',
                'No pleural effusion detected',
                'Bony thorax unremarkable'
            ]
        },
        'COVID-19': {
            'description': 'Bilateral ground-glass opacities consistent with COVID-19 pneumonia',
            'details': [
                'Bilateral peripheral ground-glass opacities',
                'Lower lobe predominant infiltrates',
                'Consolidation may be present in severe cases',
                'Classic COVID-19 radiological pattern identified'
            ]
        },
        'Pneumonia-Bacterial': {
            'description': 'Lobar/segmental consolidation consistent with bacterial pneumonia',
            'details': [
                'Dense lobar or segmental consolidation',
                'Air bronchograms may be visible',
                'Unilateral predominance common',
                'Consider sputum culture and sensitivity'
            ]
        },
        'Pneumonia-Viral': {
            'description': 'Bilateral interstitial infiltrates consistent with viral pneumonia',
            'details': [
                'Bilateral interstitial or reticulonodular pattern',
                'Peribronchial thickening noted',
                'Diffuse bilateral involvement',
                'Viral aetiology to be confirmed with serology'
            ]
        },
    },
    'pneumonia': {
        'Normal': {
            'description': 'No evidence of pneumonia on chest X-ray',
            'details': [
                'Clear lung parenchyma bilaterally',
                'No focal opacity or consolidation',
                'Normal pulmonary vasculature',
                'No pleural effusion detected'
            ]
        },
        'Pneumonia': {
            'description': 'Consolidation consistent with pneumonia detected',
            'details': [
                'Focal area of consolidation identified',
                'Air bronchograms present within opacity',
                'Increased density consistent with alveolar filling',
                'Clinical correlation and microbiological workup advised'
            ]
        },
    },
}

RECOMMENDATIONS_DB = {
    'lung': {
        'Normal': [
            'Annual low-dose CT screening if high-risk (smoker ≥30 pack-years)',
            'Continue smoking cessation programme if applicable',
            'Routine follow-up as per pulmonologist guidance'
        ],
        'Adenocarcinoma': [
            'URGENT: Urgent referral to thoracic oncology',
            'Contrast-enhanced CT chest/abdomen/pelvis for staging',
            'PET-CT scan for metastatic evaluation',
            'Bronchoscopy or CT-guided biopsy for tissue diagnosis',
            'Multidisciplinary team (MDT) conference scheduling'
        ],
        'Large Cell Carcinoma': [
            'URGENT: Immediate thoracic oncology referral',
            'Whole-body PET-CT for staging',
            'Tissue biopsy for histological confirmation',
            'Pulmonary function tests prior to surgical planning',
            'MDT discussion for treatment planning'
        ],
        'Squamous Cell Carcinoma': [
            'URGENT: Urgent bronchoscopy for endobronchial assessment',
            'Thoracic surgery and oncology joint consultation',
            'Mediastinoscopy or EBUS for nodal staging',
            'Smoking cessation mandatory',
            'MDT review within 2 weeks'
        ],
    },
    'chest': {
        'Normal': [
            'No immediate intervention required',
            'Maintain healthy lifestyle and regular check-ups',
            'Return if respiratory symptoms develop'
        ],
        'COVID-19': [
            'Isolate and follow local public health guidelines',
            'Monitor oxygen saturation at home (target SpO2 ≥95%)',
            'Seek emergency care if SpO2 drops below 94%',
            'Antiviral therapy as per current protocol',
            'Follow-up chest X-ray in 4–6 weeks'
        ],
        'Pneumonia-Bacterial': [
            'Start appropriate antibiotic therapy promptly',
            'Sputum culture before antibiotics if possible',
            'Consider hospital admission if CURB-65 score ≥2',
            'Follow-up chest X-ray in 6 weeks to confirm resolution',
            'Pneumococcal vaccination after recovery'
        ],
        'Pneumonia-Viral': [
            'Supportive care: rest, hydration, antipyretics',
            'Antiviral therapy if influenza confirmed',
            'Monitor for secondary bacterial superinfection',
            'Follow-up in 5–7 days or sooner if worsening',
            'Annual influenza vaccination recommended'
        ],
    },
    'pneumonia': {
        'Normal': [
            'No treatment required at this time',
            'Continue preventive measures (vaccination, handwashing)',
            'Return if symptoms develop or worsen'
        ],
        'Pneumonia': [
            'Initiate antibiotic therapy guided by clinical assessment',
            'Chest physiotherapy to aid sputum clearance',
            'Adequate hydration and rest',
            'Follow-up X-ray in 6 weeks to confirm resolution',
            'Consider hospital admission if clinically unwell'
        ],
    },
}

def get_severity(condition, scan_type):
    low_risk = ['Normal']
    high_risk = ['Adenocarcinoma', 'Large Cell Carcinoma', 'Squamous Cell Carcinoma', 'COVID-19', 'Pneumonia']
    if condition in high_risk:
        return 'High'
    if 'Pneumonia' in condition or condition in ['Pneumonia-Bacterial', 'Pneumonia-Viral']:
        return 'Medium'
    if condition in low_risk:
        return 'Low'
    return 'Medium'

def get_findings(condition, scan_type):
    return FINDINGS_DB.get(scan_type, {}).get(condition, {
        'description': f'{condition} detected on {scan_type} imaging',
        'details': ['Further clinical evaluation required']
    })

def get_recommendations(condition, scan_type, confidence):
    base = RECOMMENDATIONS_DB.get(scan_type, {}).get(condition, ['Clinical review recommended'])
    if confidence > 0.95:
        base.append('High confidence result – proceed with recommended management')
    elif confidence > 0.85:
        base.append('Moderate confidence – consider confirmatory imaging if clinically indicated')
    else:
        base.append('Lower confidence – additional imaging or specialist review recommended')
    return base

# ──────────────────────────────────────────────
# Email
# ──────────────────────────────────────────────
def send_medical_report(patient_email, patient_name, diagnosis_data, image_path=None):
    try:
        message = MIMEMultipart()
        message['Subject'] = f'Chest Diagnosis Report – {patient_name}'
        message['From'] = app.config['MAIL_USERNAME']
        message['To'] = patient_email

        image_html = ""
        if image_path and os.path.exists(image_path):
            with open(image_path, 'rb') as img_file:
                img_data = img_file.read()
            image = MIMEImage(img_data, name=os.path.basename(image_path))
            image.add_header('Content-ID', '<scan_image>')
            message.attach(image)
            image_html = """
                <div class="section">
                    <h2>Scan Image</h2>
                    <div style="text-align:center;">
                        <img src="cid:scan_image" alt="Chest Scan" style="max-width:100%;border-radius:8px;">
                        <p><em>Original Scan Image</em></p>
                    </div>
                </div>
            """

        sev_class = {'High': 'critical', 'Medium': 'urgent', 'Low': 'normal'}.get(diagnosis_data['severity'], 'normal')
        html_content = f"""
        <html><head><style>
            body{{font-family:Arial,sans-serif;line-height:1.6;color:#333}}
            .header{{background:linear-gradient(135deg,#1a6cf5,#0ea5e9);color:white;padding:24px;text-align:center}}
            .content{{padding:20px}}
            .section{{margin-bottom:20px;padding:15px;border-left:4px solid #1a6cf5;background:#f8f9fa}}
            .critical{{border-left-color:#dc3545;background:#f8d7da}}
            .urgent{{border-left-color:#ffc107;background:#fff3cd}}
            .normal{{border-left-color:#28a745;background:#d4edda}}
            .footer{{text-align:center;padding:20px;font-size:12px;color:#666}}
        </style></head><body>
            <div class="header">
                <h1>Chest Disease Diagnosis Report</h1>
                <p>PulmoScan AI Diagnostic System</p>
            </div>
            <div class="content">
                <div class="section">
                    <h2>Patient Information</h2>
                    <p><strong>Name:</strong> {patient_name}</p>
                    <p><strong>Date:</strong> {diagnosis_data['timestamp']}</p>
                    <p><strong>Report ID:</strong> {diagnosis_data['report_id']}</p>
                    <p><strong>Scan Type:</strong> {diagnosis_data.get('scan_type','chest').upper()}</p>
                </div>
                <div class="section {sev_class}">
                    <h2>Diagnosis Summary</h2>
                    <p><strong>Condition:</strong> {diagnosis_data['condition']}</p>
                    <p><strong>Confidence:</strong> {diagnosis_data['confidence']:.1%}</p>
                    <p><strong>Severity:</strong> {diagnosis_data['severity']}</p>
                </div>
                {image_html}
                <div class="section">
                    <h2>Clinical Findings</h2>
                    <p><strong>Description:</strong> {diagnosis_data['findings']['description']}</p>
                    <ul>{''.join(f'<li>{f}</li>' for f in diagnosis_data['findings']['details'])}</ul>
                </div>
                <div class="section">
                    <h2>Medical Recommendations</h2>
                    <ol>{''.join(f'<li>{r}</li>' for r in diagnosis_data['recommendations'])}</ol>
                </div>
                <div class="section">
                    <h2>Important Notes</h2>
                    <p>This AI-generated report must be reviewed by a qualified healthcare professional before any clinical decisions are made.</p>
                </div>
            </div>
            <div class="footer">
                <p>Confidential Medical Document – For authorised use only</p>
                <p>PulmoScan AI Diagnostic Center © 2024</p>
            </div>
        </body></html>
        """
        message.attach(MIMEText(html_content, 'html'))

        with smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT']) as server:
            server.starttls()
            server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            server.send_message(message)
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

# ──────────────────────────────────────────────
# RAG Chat endpoint
# ──────────────────────────────────────────────
@app.route('/chat', methods=['POST'])
def chat():
    """
    Integrate your existing RAG system here.
    Expected JSON body: { "message": "...", "history": [...] }
    Replace the body of this function with your RAG pipeline.
    """
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        history = data.get('history', [])

        # ── REPLACE THIS BLOCK WITH YOUR RAG SYSTEM ──
        # Example stub response:
        reply = (
            f"[RAG] You asked: '{user_message}'. "
            "Connect your RAG pipeline by replacing the stub in the /chat route of app.py."
        )
        # ──────────────────────────────────────────────

        return jsonify({'reply': reply})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ──────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

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
    patient = conn.execute('SELECT * FROM patients WHERE patient_id = ?', (patient_id,)).fetchone()
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
        scan_type = request.form.get('scan_type', 'chest')

        if file.filename == '':
            return jsonify({'error': 'No file selected'})
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only JPG/PNG accepted.'})

        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{scan_type}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        condition, confidence, status = analyze_image(filepath, scan_type)

        if condition:
            findings = get_findings(condition, scan_type)
            recommendations = get_recommendations(condition, scan_type, confidence)
            severity = get_severity(condition, scan_type)

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO diagnoses (patient_id, scan_type, image_path, condition, confidence,
                   severity, findings, recommendations)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                (patient_id, scan_type, filename, condition, float(confidence),
                 severity, json.dumps(findings), json.dumps(recommendations))
            )
            diagnosis_id = cursor.lastrowid
            conn.commit()
            conn.close()

            return jsonify({
                'success': True,
                'diagnosis_id': diagnosis_id,
                'scan_type': scan_type,
                'condition': condition,
                'confidence': float(confidence),
                'severity': severity,
                'findings': findings,
                'recommendations': recommendations,
                'image_url': f'/uploads/{filename}',
                'image_path': filepath,
                'model_info': MODEL_CONFIG[scan_type]['label']
            })
        else:
            return jsonify({'error': f'Failed to analyse {scan_type} scan. Status: {status}'})

    patient_id = request.args.get('patient_id', '')
    return render_template('diagnose.html', patient_id=patient_id, model_config=MODEL_CONFIG)

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
        'report_id': f"CHE{diagnosis_id:06d}",
        'scan_type': diagnosis['scan_type']
    }

    success = send_medical_report(diagnosis['email'], diagnosis['name'], report_data, image_path)

    if success:
        conn.execute('UPDATE diagnoses SET report_sent = 1 WHERE id = ?', (diagnosis_id,))
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
        data = request.get_json() or {}
        name = data.get('name') or request.form.get('name')
        age = data.get('age') or request.form.get('age')
        gender = data.get('gender') or request.form.get('gender')
        email = data.get('email') or request.form.get('email')
        phone = data.get('phone') or request.form.get('phone')

        if not name:
            return jsonify({'error': 'Patient name is required'})

        patient_id = generate_patient_id()
        conn = get_db_connection()
        try:
            conn.execute(
                'INSERT INTO patients (patient_id, name, age, gender, email, phone) VALUES (?, ?, ?, ?, ?, ?)',
                (patient_id, name, age, gender, email, phone)
            )
            conn.commit()
            return jsonify({'success': True, 'patient_id': patient_id, 'message': 'Patient added successfully'})
        except sqlite3.IntegrityError:
            return jsonify({'error': 'Patient ID conflict – please retry'})
        finally:
            conn.close()
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'})

if __name__ == '__main__':
    print("🫁  Starting PulmoScan – Chest Disease Diagnosis System")
    print(f"📁  Upload folder : {app.config['UPLOAD_FOLDER']}")
    print(f"📊  Database      : {app.config['DATABASE']}")
    print(f"🖼️   Keras size    : {KERAS_TARGET_SIZE}  |  Pneumonia (ResNet50) size: {PNEUMONIA_IMG_SIZE}×{PNEUMONIA_IMG_SIZE}")
    for k, v in MODEL_CONFIG.items():
        if v['type'] == 'keras':
            exists = "✅" if os.path.exists(v['path']) else "⚠️  (not found – mock mode)"
            print(f"🤖  {k.upper()} model  : {v['path']} {exists}")
        else:
            xgb_ok = "✅" if os.path.exists(v['xgb_path']) else "⚠️  missing"
            pca_ok = "✅" if os.path.exists(v['pca_path'])  else "⚠️  missing"
            print(f"🤖  PNEUMONIA XGB: {v['xgb_path']} {xgb_ok}")
            print(f"    PNEUMONIA PCA: {v['pca_path']}  {pca_ok}")
    print("🌐  Server starting on http://localhost:5000")
    app.run(debug=True, host='localhost', port=5000)