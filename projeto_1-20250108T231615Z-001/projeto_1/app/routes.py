from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session
from app.models import db, User, Doctor, Patient, Biomedico, Appointment
from datetime import datetime, date, time

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
                                "id": doctor.id,
                                "role": "doctor",
                                "date": "2023-10-01",  # Ajuste conforme necessário
                                "time": f"{date_time[0]} - {date_time[1]}"
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
                                "id": biomedico.id,
                                "role": "biomedico",
                                "date": "2023-10-01",  # Ajuste conforme necessário
                                "time": f"{date_time[0]} - {date_time[1]}"
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
    try:
        data = request.form
        email = data.get('email')
        password = data.get('password')
        role = data.get('role')

        if not email or not password or not role:
            return jsonify({"error": "Missing required fields"}), 400

        new_user = User(email=email, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        print(f"Error registering user: {e}")
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500


@main.route('/api/register_appointment', methods=['POST'])
def register_appointment():
    try:
        data = request.json
        appointments = data.get('appointments', [])
        
        for appointment in appointments:
            print(f"Received appointment: {appointment}")
            try:
                parts = appointment.split('-')
                print(f"Parts: {parts}")  # Log the parts
                if len(parts) != 6:
                    raise ValueError(f"Expected 6 parts but got {len(parts)}: {parts}")
                slot_id = parts[0]
                date_str = f"{parts[1]}-{parts[2]}-{parts[3]}"
                time_start_str = parts[4].strip()
                time_end_str = parts[5].strip()
                print(f"slot_id: {slot_id}, date: {date_str}, time_start: {time_start_str}, time_end: {time_end_str}")  # Log the values

                # Convert strings to date and time objects
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                time_start_obj = datetime.strptime(time_start_str, "%H:%M").time()
                time_end_obj = datetime.strptime(time_end_str, "%H:%M").time()
                print(f"Converted date: {date_obj}, time_start: {time_start_obj}, time_end: {time_end_obj}")  # Log the converted values

                # Check if the appointment slot is already taken
                existing_appointment = Appointment.query.filter_by(date=date_obj, time=time_start_obj).first()
                if existing_appointment:
                    return jsonify({"error": "Horário desejado, já foi utilizado"}), 400

            except ValueError as ve:
                print(f"Error unpacking appointment: {ve}")
                return jsonify({"error": "Invalid appointment format", "details": str(ve)}), 400
            
            print(f"Processing appointment: slot_id={slot_id}, date={date_obj}, time_start={time_start_obj}, time_end={time_end_obj}")
            
            # Determine role and specialty based on slot_id
            doctor = Doctor.query.filter_by(id=slot_id).first()
            biomedico = Biomedico.query.filter_by(id=slot_id).first()
            
            if doctor:
                print(f"Doctor found: {doctor}")
                role = 'doctor'
                specialty = doctor.specialty
                doctor_id = doctor.id
                biomedico_id = None
            elif biomedico:
                print(f"Biomedico found: {biomedico}")
                role = 'biomedico'
                specialty = biomedico.specialty
                doctor_id = None
                biomedico_id = biomedico.id
            else:
                print(f"Invalid slot ID: {slot_id}")
                print(f"Available doctor IDs: {[doctor.id for doctor in Doctor.query.all()]}")
                print(f"Available biomedico IDs: {[biomedico.id for biomedico in Biomedico.query.all()]}")
                return jsonify({"error": "Invalid slot ID"}), 400
            
            new_appointment = Appointment(doctor_id=doctor_id, biomedico_id=biomedico_id, patient_id=session['user_id'], date=date_obj, time=time_start_obj, status='scheduled')
            db.session.add(new_appointment)
        
        db.session.commit()
        return jsonify({"message": "Appointments registered successfully"}), 200
    except Exception as e:
        print(f"Error registering appointment: {e}")
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500


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