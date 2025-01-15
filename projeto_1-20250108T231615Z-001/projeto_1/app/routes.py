from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session
from app.models import db, User, Doctor, Patient, Biomedico
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/', methods=['GET'])
def home_page():
    return render_template('c_home.html')

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
def get_available_slots():
    try:
        doctors = Doctor.query.all()
        biomedicos = Biomedico.query.all()

        slots_list = []

        for doctor in doctors:
            if doctor.available_hours:
                try:
                    print(f"Doctor {doctor.specialty} available hours: {doctor.available_hours}")
                    for hour in doctor.available_hours.split(','):
                        date_time = hour.split('-')
                        if len(date_time) == 2:
                            slots_list.append({
                                "date": "2023-10-01",  # Ajuste conforme necessário
                                "time": date_time[0] + " - " + date_time[1]
                            })
                        else:
                            print(f"Invalid format in doctor {doctor.specialty} available_hours: {hour}")
                except Exception as doctor_error:
                    print(f"Error processing doctor {doctor.specialty}: {doctor_error}")

        for biomedico in biomedicos:
            if biomedico.available_hours:
                try:
                    print(f"Biomedico CRBM {biomedico.crbm} available hours: {biomedico.available_hours}")
                    for hour in biomedico.available_hours.split(','):
                        date_time = hour.split('-')
                        if len(date_time) == 2:
                            slots_list.append({
                                "date": "2023-10-01",  # Ajuste conforme necessário
                                "time": date_time[0] + " - " + date_time[1]
                            })
                        else:
                            print(f"Invalid format in biomedico CRBM {biomedico.crbm} available_hours: {hour}")
                except Exception as biomedico_error:
                    print(f"Error processing biomedico CRBM {biomedico.crbm}: {biomedico_error}")

        print(f"Slots list: {slots_list}")
        return jsonify({"slots": slots_list})
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

@main.route('/api/show_tables', methods=['GET'])
def show_tables():
    try:
        doctors = Doctor.query.all()
        biomedicos = Biomedico.query.all()

        doctors_list = [{"id": doctor.id, "specialty": doctor.specialty, "crm": doctor.crm, "available_hours": doctor.available_hours} for doctor in doctors]
        biomedicos_list = [{"id": biomedico.id, "crbm": biomedico.crbm, "available_hours": biomedico.available_hours} for biomedico in biomedicos]

        return jsonify({"doctors": doctors_list, "biomedicos": biomedicos_list})
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500
@main.route('/register', methods=['GET'])
def register_page():
    return render_template('register.html')

@main.route('/register', methods=['POST'])
def register():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    role = request.form.get('role')

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 400

    user = User(name=name, email=email, password=password, role=role)
    db.session.add(user)
    db.session.commit()

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

    date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d').date()

    patient = Patient(id=user_id, date_of_birth=date_of_birth, medical_history=medical_history)
    db.session.add(patient)
    db.session.commit()

    return redirect(url_for('main.success'))

@main.route('/success', methods=['GET'])
def success():
    return render_template('success.html')