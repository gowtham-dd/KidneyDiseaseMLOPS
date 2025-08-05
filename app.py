from flask import Flask, render_template, request, flash, redirect, url_for
import os
import numpy as np
import tensorflow as tf
from datetime import datetime
import logging
from werkzeug.utils import secure_filename

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'kidney-disease-secret-key-2024'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

# Initialize model
model = None
try:
    model = tf.keras.models.load_model('artifacts/model_training/kidney_model')
    logger.info("✅ Kidney Disease Model loaded successfully!")
except Exception as e:
    logger.error(f"❌ Error loading model: {e}")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def preprocess_image(image_path):
    """Preprocess the uploaded image for model prediction"""
    try:
        img = tf.keras.preprocessing.image.load_img(
            image_path, target_size=(28, 28))
        img_array = tf.keras.preprocessing.image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0) / 255.0
        return img_array
    except Exception as e:
        logger.error(f"Image preprocessing failed: {e}")
        raise

CLASS_NAMES = ['Cyst', 'Normal', 'Stone', 'Tumor']

@app.route('/')
def home():
    """Home page with information about the system"""
    return render_template('index.html')

@app.route('/predict-form')
def predict_form():
    """Prediction form page"""
    return render_template('predict.html')

@app.route('/predict', methods=['POST'])
def predict():
    """Handle prediction requests"""
    try:
        if not model:
            flash('Model not available. Please contact support.', 'error')
            return redirect(url_for('predict_form'))

        # Check if file was uploaded
        if 'ct_scan' not in request.files:
            flash('No CT scan image uploaded', 'error')
            return redirect(url_for('predict_form'))

        file = request.files['ct_scan']
        
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(url_for('predict_form'))

        if file and allowed_file(file.filename):
            # Save the uploaded file
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Preprocess and predict
            processed_image = preprocess_image(filepath)
            predictions = model.predict(processed_image)
            predicted_class = np.argmax(predictions[0])
            confidence = float(np.max(predictions[0]) * 100)
            
            result = {
                'class': CLASS_NAMES[predicted_class],
                'confidence': round(confidence, 2),
                'image_path': filepath,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'all_predictions': {
                    'Cyst': float(predictions[0][0] * 100),
                    'Normal': float(predictions[0][1] * 100),
                    'Stone': float(predictions[0][2] * 100),
                    'Tumor': float(predictions[0][3] * 100)
                }
            }

            return render_template('result.html', result=result)
        else:
            flash('Allowed image types are: png, jpg, jpeg', 'error')
            return redirect(url_for('predict_form'))

    except Exception as e:
        logger.error(f'Prediction error: {e}')
        flash('Something went wrong during prediction. Please try again.', 'error')
        return redirect(url_for('predict_form'))

@app.route('/api/predict', methods=['POST'])
def api_predict():
    """API endpoint for predictions"""
    try:
        if not model:
            return jsonify({
                'success': False,
                'error': 'Model not available'
            }), 500

        if 'ct_scan' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No CT scan image uploaded'
            }), 400

        file = request.files['ct_scan']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No selected file'
            }), 400

        if file and allowed_file(file.filename):
            # Save the uploaded file temporarily
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Preprocess and predict
            processed_image = preprocess_image(filepath)
            predictions = model.predict(processed_image)
            predicted_class = np.argmax(predictions[0])
            
            # Clean up temporary file
            os.remove(filepath)

            return jsonify({
                'success': True,
                'prediction': CLASS_NAMES[predicted_class],
                'confidence': float(np.max(predictions[0]) * 100),
                'all_predictions': {
                    'Cyst': float(predictions[0][0] * 100),
                    'Normal': float(predictions[0][1] * 100),
                    'Stone': float(predictions[0][2] * 100),
                    'Tumor': float(predictions[0][3] * 100)
                },
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Allowed image types are: png, jpg, jpeg'
            }), 400

    except Exception as e:
        logger.error(f"API Prediction error: {e}")
        return jsonify({
            'success': False,
            'error': 'An error occurred during prediction'
        }), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'model_loaded': bool(model)
        }
        return jsonify(status)
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

if __name__ == "__main__":
    print("🏥 Starting Kidney Disease Classification System")
    print(f"🔧 Model: {'✅ Loaded' if model else '❌ Not Loaded'}")
    print("🚀 Server starting on http://localhost:8080")
    
    app.run(host="0.0.0.0", port=8080, debug=True)