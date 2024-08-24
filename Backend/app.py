import pickle
from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
from skimage.filters import sobel, roberts, laplace
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load the model
model_path = 'C:/Users/DELL/OneDrive/Desktop/pro/Backend/blur_image_detection_svm_model.pkl'
with open(model_path, 'rb') as model_file:
    model = pickle.load(model_file)

# Directory to save uploaded images
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to extract features from an image
def extract_features(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    sobel_edges = sobel(gray)
    roberts_edges = roberts(gray)
    laplacian_edges = laplace(gray)

    features = []
    for edges in [sobel_edges, roberts_edges, laplacian_edges]:
        features.extend([np.mean(edges), np.max(edges), np.var(edges)])

    return features

# Test route to check if the server is running
@app.route('/')
def home():
    return "Flask server is running!"

# Prediction route
@app.route('/predict', methods=['POST'])
def predict():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file in request'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Load and preprocess the image
        image = cv2.imread(file_path)
        features = extract_features(image)
        features = np.array(features).reshape(1, -1)

        # Make prediction
        prediction = model.predict(features)[0]
        result = 'sharp' if prediction == 0 else 'blurry'

        return jsonify({'prediction': result})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
