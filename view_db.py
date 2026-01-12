from sql_api import app, db, Job  # Import Flask app and models

# Use application context
with app.app_context():
    # Query all records
    jobs = Job.query.all()

    print(f"Total records: {len(jobs)}\n")

    for job in jobs:
        print(f"ID: {job.id}, Sequence: {job.sequence}, Job ID: {job.job_id}, Part ID: {job.part_id}, Lot: {job.lot_number}")
