from flask import Flask, render_template, request, jsonify
from google.cloud import vision
from flask_cors import CORS
import requests
import json
import os
from datetime import datetime
import base64

import os, json, tempfile

# New: load service account JSON from environment (set this in Vercel dashboard)
if os.getenv("GOOGLE_CREDENTIALS"):
    sa_json = os.getenv("GOOGLE_CREDENTIALS")
    # write to a temp file and point GOOGLE_APPLICATION_CREDENTIALS to it
    fd, path = tempfile.mkstemp(suffix=".json")
    with os.fdopen(fd, "w") as f:
        f.write(sa_json)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = path
else:
    # In local dev you may still use a local file
    # os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "visionapi-437910-51d31e476e2d.json"
    pass


app = Flask(__name__)
CORS(app)
API_ENDPOINT = "http://127.0.0.1:5000/update_job"

def detect_text(image_data):
    """Extract text from image using Google Vision API"""
    try:
        client = vision.ImageAnnotatorClient()
        image = vision.Image(content=image_data)
        response = client.text_detection(image=image)
        annotations = response.text_annotations
        if annotations:
            return annotations[0].description.strip()
        return ""
    except Exception as e:
        print(f"Error detecting text: {str(e)}")
        return ""

def get_api_data(job_code):
    """Fetch job data from ERP API"""
    try:
        url = "https://erp.tbsinter.com/ai_api/get_job_data.php"
        payload = {"erp_sta_job_id": job_code}
        response = requests.post(url, data=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                return data
    except Exception as e:
        print(f"Error fetching API data: {str(e)}")
    return None

def send_to_api(result):
    """Send scan result to API endpoint"""
    try:
        response = requests.post(API_ENDPOINT, json=result, timeout=5)
        if response.status_code == 200:
            return True
        return False
    except Exception as e:
        print(f"Error sending to API: {str(e)}")
        return False

def save_scan(job_code, part_name, scan):
    """Save scan to local JSON file"""
    filename = f"scans_{job_code}.json"
    
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            data = json.load(f)
    else:
        data = {
            "job_code": job_code,
            "part_name": part_name,
            "scans": []
        }
    
    data["scans"].append(scan)
    data["total_scans"] = len(data["scans"])
    data["last_updated"] = datetime.now().isoformat()
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    return data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/get_job_data', methods=['POST'])
def api_get_job_data():
    """Fetch job data from ERP"""
    job_code = request.json.get('job_code', '').strip()
    
    if not job_code:
        return jsonify({"error": "Job code required"}), 400
    
    data = get_api_data(job_code)
    
    if not data:
        return jsonify({"error": "No data found for this job code"}), 404
    
    # Get unique parts
    parts = []
    seen_names = set()
    for item in data:
        name = item.get("erp_sta_part_master_name", "")
        if name and name not in seen_names:
            parts.append({
                "name": name,
                "id": item.get("erp_sta_part_master_id", ""),
                "lot_number": item.get("erp_item_lot_lotnum", "")
            })
            seen_names.add(name)
    
    return jsonify({
        "job_code": job_code,
        "parts": parts
    })

@app.route('/api/process_image', methods=['POST'])
def api_process_image():
    """Process captured image and extract text"""
    data = request.json
    image_base64 = data.get('image', '')
    
    if not image_base64:
        return jsonify({"error": "No image provided"}), 400
    
    try:
        image_data = base64.b64decode(image_base64)
    except Exception as e:
        return jsonify({"error": "Invalid image data"}), 400
    
    text = detect_text(image_data)
    
    return jsonify({
        "extracted_text": text
    })

@app.route('/api/save_scan', methods=['POST'])
def api_save_scan():
    """Save scan result"""
    data = request.json
    job_code = data.get('job_code', '')
    part_name = data.get('part_name', '')
    lot_number = data.get('lot_number', '')
    part_id = data.get('part_id', '')
    sequence = data.get('sequence', 1)
    
    scan_result = {
        "sequence": sequence,
        "job_id": job_code,
        "part_id": part_id,
        "lot_number": lot_number,
        "timestamp": datetime.now().isoformat()
    }
    
    # Send to external API
    send_to_api(scan_result)
    
    # Save locally
    saved_data = save_scan(job_code, part_name, scan_result)
    
    return jsonify({
        "success": True,
        "message": "Scan saved successfully",
        "total_scans": saved_data["total_scans"]
    })

