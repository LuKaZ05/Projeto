from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session
from app.models import db, User, Doctor, Patient, Biomedico
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/', methods=['GET'])
def test_route():
    return "Apenas teste de rota"

@main.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@main.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter_by(email=email, password=password).first()

    if user:
        session['user_id'] = user.id
        session['role'] = user.role
        return redirect(url_for('main.schedule_appointment'))
    else:
        return render_template('login.html', error="Invalid email or password")

@main.route('/schedule_appointment', methods=['GET'])
def schedule_appointment():
    doctors = Doctor.query.all()
    biomedicos = Biomedico.query.all()
    return render_template('schedule_appointment.html', doctors=doctors, biomedicos=biomedicos)

@main.route('/api/available_slots', methods=['GET'])
def available_slots():
    doctor_id = request.args.get('doctor_id')
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return jsonify([])

    # Parse available hours from the database
    available_hours = doctor.available_hours.split(';')
    available_slots = []
    for entry in available_hours:
        date, slots = entry.split(':')
        slots = slots.split(',')
        available_slots.append({"date": date, "slots": slots})

    return jsonify(available_slots)

@main.route('/register', methods=['GET'])
def register_page():
    return render_template('register.html')

@main.route('/register', methods=['POST'])
def register():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    role = request.form.get('role')  # 'paciente', 'médico', 'biomédico'

    # Verifica se o e-mail já está cadastrado
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email já cadastrado"}), 400

    # Cria o usuário
    user = User(name=name, email=email, password=password, role=role)
    db.session.add(user)
    db.session.commit()

    # Redireciona para a página de registro específica com base no papel
    if role == 'médico':
        crm = request.form.get('crm')
        return redirect(url_for('main.register_doctor_page', user_id=user.id, crm=crm))
    elif role == 'biomédico':
        return redirect(url_for('main.register_biomedico_page', user_id=user.id))
    elif role == 'paciente':
        return redirect(url_for('main.register_patient_page', user_id=user.id))
    else:
        return redirect(url_for('main.success'))

@main.route('/register_doctor', methods=['GET'])
def register_doctor_page():
    user_id = request.args.get('user_id')
    crm = request.args.get('crm')
    return render_template('register_doctor.html', user_id=user_id, crm=crm)

@main.route('/register_doctor', methods=['POST'])
def register_doctor():
    user_id = request.form.get('user_id')
    specialty = request.form.get('specialty')
    crm = request.form.get('crm')
    available_hours = request.form.get('available_hours')

    doctor = Doctor(id=user_id, specialty=specialty, crm=crm, available_hours=available_hours)
    db.session.add(doctor)
    db.session.commit()

    return redirect(url_for('main.success'))

@main.route('/register_biomedico', methods=['GET'])
def register_biomedico_page():
    user_id = request.args.get('user_id')
    return render_template('register_biomedico.html', user_id=user_id)

@main.route('/register_biomedico', methods=['POST'])
def register_biomedico():
    user_id = request.form.get('user_id')
    crbm = request.form.get('crbm')
    available_hours = request.form.get('available_hours')

    biomedico = Biomedico(id=user_id, crbm=crbm, available_hours=available_hours)
    db.session.add(biomedico)
    db.session.commit()

    return redirect(url_for('main.success'))

@main.route('/register_patient', methods=['GET'])
def register_patient_page():
    user_id = request.args.get('user_id')
    return render_template('register_patient.html', user_id=user_id)

@main.route('/register_patient', methods=['POST'])
def register_patient():
    user_id = request.form.get('user_id')
    date_of_birth_str = request.form.get('date_of_birth')
    medical_history = request.form.get('medical_history', "")

    # Converte a string de data para um objeto date do Python
    date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d').date()

    patient = Patient(id=user_id, date_of_birth=date_of_birth, medical_history=medical_history)
    db.session.add(patient)
    db.session.commit()

    return redirect(url_for('main.success'))

@main.route('/success', methods=['GET'])
def success():
    return render_template('success.html')