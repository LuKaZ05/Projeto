from app._init_ import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'doctor', 'patient', 'biomedico'

class Doctor(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    specialty = db.Column(db.String(100), nullable=False)
    crm = db.Column(db.String(20), nullable=False)
    available_hours = db.Column(db.String(255))  # Exemplo: '09:00-12:00,14:00-18:00'

class Patient(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    date_of_birth = db.Column(db.Date, nullable=False)
    medical_history = db.Column(db.Text)

class Biomedico(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    crbm = db.Column(db.String(20), nullable=False)
    available_hours = db.Column(db.String(255))  # Exemplo: '09:00-12:00,14:00-18:00'

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=True)
    biomedico_id = db.Column(db.Integer, db.ForeignKey('biomedico.id'), nullable=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default="scheduled")  # Exemplo: 'cancelled', 'completed'