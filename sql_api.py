from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# --- Database Config ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jobs.db'  # SQLite file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Database Model ---
class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sequence = db.Column(db.Integer, nullable=False)
    job_id = db.Column(db.String(50), nullable=False)
    part_id = db.Column(db.Integer, nullable=False)
    lot_number = db.Column(db.String(100), nullable=False)

# --- Create Table ---
with app.app_context():
    db.create_all()

# --- API Endpoint ---
@app.route('/update_job', methods=['POST'])
def update_job():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No JSON received"}), 400

    try:
        sequence = data['sequence']
        job_id = data['job_id']
        part_id = data['part_id']
        lot_number = data['lot_number']

        # Check if record exists (based on job_id or part_id)
        existing_job = Job.query.filter_by(job_id=job_id, part_id=part_id).first()

        if existing_job:
            # Update existing record
            existing_job.sequence = sequence
            existing_job.lot_number = lot_number
            message = "Record updated"
        else:
            # Insert new record
            new_job = Job(sequence=sequence, job_id=job_id, part_id=part_id, lot_number=lot_number)
            db.session.add(new_job)
            message = "New record added"

        db.session.commit()

        return jsonify({"status": "success", "message": message}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# --- Run Server ---
if __name__ == '__main__':
    app.run(debug=True)
