import io
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, FileResponse
from django.views.decorators.cache import never_cache
from .app import create_patient, search_patient, decrypt_patient_data, update_patient, delete_patient, reencryption, \
    patient_medical_info, add_patient_medical_info, patient_medical_dashboard_info, update_patient_medical_info, \
    add_roster, roster_entries, delete_roster, get_carers, get_patient, add_care_plan, update_care_plan, get_care_plan, get_medication
from . import config
from .functions import get_encryption_key, verify_password, current_key
from .authentication_service import *

# Create your views here.
# User Login
@never_cache
def login(request):
    storage = messages.get_messages(request)
    list(storage)

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = get_user_by_username(username)

        if user and verify_password(user[0], password):
            request.session['username'] = username
            request.session['role'] = user[1]
            request.session['_session_init'] = True
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')

# Logout
@never_cache
def logout(request):
    request.session.flush()
    return redirect('login')

# Create a user
@never_cache
def create_user_view(request):
    if request.session.get('role') != 'admin':
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')

        is_valid, error_message = password_complexity_check(password)

        if not is_valid:
            return render(request, 'create_user.html', {'error': error_message})

        create_user(username, password, role)
        return redirect('home')

    return render(request, 'create_user.html')

# Home
@never_cache
def home(request):
    if current_key is None:
        try:
            get_encryption_key(force_refresh=False)
            print("Key retrieved.")
        except Exception as e:
            print("Failed to retrieved key:", str(e))

    return render(request, 'home.html', {
        'maintenance_mode': config.MAINTENANCE_MODE,
        'debug': settings.DEBUG
    })

# Maintenance
@never_cache
def maintenance_mode(request):
    if request.method == 'POST':
        config.MAINTENANCE_MODE = True
        try:
            reencryption()
        except Exception as e:
            config.MAINTENANCE_MODE = False
            return JsonResponse({'status': 'error', 'message': str(e)})
        config.MAINTENANCE_MODE = False
        return JsonResponse({'status': 'started'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

@never_cache
def maintenance_status(request):
    return JsonResponse({'maintenance_mode': config.MAINTENANCE_MODE})

# Patient Profile
@never_cache
def create_patient_profile(request):
    if request.method == 'POST':
        name = request.POST.get('Name')
        dob = request.POST.get('DOB')
        contact_number = request.POST.get('Contact_Number')
        email_address = request.POST.get('Email_Address')
        home_address = request.POST.get('Home_Address')
        next_of_kin_name = request.POST.get('Next_Of_Kin_Name')
        emergency_contact_number = request.POST.get('Emergency_Contact_Number')
        next_of_kin_home_address = request.POST.get('Next_Of_Kin_Home_Address')
        emergency_email_address = request.POST.get('Emergency_Email_Address')

        create_patient(name, dob, contact_number, email_address, home_address, next_of_kin_name,
                       emergency_contact_number, next_of_kin_home_address, emergency_email_address)

        return redirect('home')
    else:
        return render(request, 'create_patient_profile.html')

# Search Patient Profile
@never_cache
def search_patient_profile(request):
    if request.method == 'POST':
        search_type = request.POST.get('search_type')
        search_value = request.POST.get('search_value')

        print(f"Searching with type: {search_type} and value: {search_value}")  # TODO need to remove debug line
        key = get_encryption_key(force_refresh=True)

        # Search for patients based on search type
        if search_type == 'Name':
            results = search_patient(name=search_value, key= key)
        else:  # search_type == 'DOB'
            results = search_patient(dob=search_value, key= key)

        print(f"Found {len(results) if results else 0} results")  # TODO need to remove debug line

        if results:
            decrypted_results = decrypt_patient_data(results, key)
            patients_data = []

            for result in decrypted_results:
                patient_data = {
                    'Patient_ID': result[0],
                    'Name': result[1],
                    'DOB': result[2],
                    'Contact_Number': result[3],
                    'Email_Address': result[4],
                    'Home_Address': result[5],
                    'Next_Of_Kin_Name': result[6],
                    'Emergency_Contact_Number': result[7],
                    'Next_Of_Kin_Home_Address': result[8],
                    'Emergency_Email_Address': result[9]
                }
                patients_data.append(patient_data)

            return JsonResponse({'status': 'success', 'patients': patients_data})
        else:
            return JsonResponse({'status': 'not_found'})

    return render(request, 'search_patient_profile.html')

# Update Patient Profile
@never_cache
def update_patient_profile(request):
    if request.method == 'POST':
        Patient_ID = request.POST.get('Patient_ID')
        name = request.POST.get('Name')
        dob = request.POST.get('DOB')
        contact_number = request.POST.get('Contact_Number')
        email_address = request.POST.get('Email_Address')
        home_address = request.POST.get('Home_Address')
        next_of_kin_name = request.POST.get('Next_Of_Kin_Name')
        emergency_contact_number = request.POST.get('Emergency_Contact_Number')
        next_of_kin_home_address = request.POST.get('Next_Of_Kin_Home_Address')
        emergency_email_address = request.POST.get('Emergency_Email_Address')

        success = update_patient(
            Patient_ID, name, dob, contact_number, email_address, home_address,
            next_of_kin_name, emergency_contact_number, next_of_kin_home_address,
            emergency_email_address
        )
        return JsonResponse({'status': 'success' if success else 'error'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

# Delete Patient Profile
@never_cache
def delete_patient_profile(request):
    if request.method == 'POST':
        Patient_ID = request.POST.get('Patient_ID')
        success = delete_patient(Patient_ID)
        return JsonResponse({'status': 'success' if success else 'error'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

# Medical Dashboard
@never_cache
def medical_dashboard(request):
    if request.method == 'POST':
        search_type = request.POST.get('search_type')
        search_value = request.POST.get('search_value')

        key = get_encryption_key(force_refresh=True)

        if search_type == 'Name':
            results = search_patient(name=search_value, key=key)
        else:
            results = search_patient(dob=search_value, key=key)

        if results:
            decrypted = decrypt_patient_data(results, key)

            patients_info = []
            for patient in decrypted:
                patient_id = patient[0]
                patients_info.append({
                    'Patient_ID': patient_id,
                    'Name': patient[1],
                    'DOB': patient[2],
                    'Contact_Number': patient[3],
                    'has_medical_data': patient_medical_info(patient_id)
                })

            return JsonResponse({
                'status': 'success',
                'patients': patients_info
            })

        return JsonResponse({'status': 'not_found'})

    return render(request, 'medical_dashboard.html')

# Patient Medical Dashboard Details
@never_cache
def patient_medical_dashboard_details(request, patient_id):
    key = get_encryption_key()
    patient_data = search_patient(key=key)

    selected = [p for p in patient_data if p[0] == patient_id]
    if not selected:
        return HttpResponse("Patient not found", status=404)

    decrypted_patient = decrypt_patient_data([selected[0]], key)[0]

    medical_info = patient_medical_dashboard_info(patient_id)

    if request.method == "POST":
        names = request.POST.getlist('Medication_Name[]')
        dosages = request.POST.getlist('Medication_Dosage[]')
        history = request.POST.get('Medical_History_Text')
        allergies = request.POST.get('Allergies')

        uploaded_files = request.FILES.getlist('Medical_File')
        medical_files = [f.read() for f in uploaded_files]
        file_names = [f.name for f in uploaded_files]

        if medical_info:
            update_patient_medical_info(
                patient_id=patient_id,
                names=names,
                dosages=dosages,
                history=history,
                new_files=medical_files,
                new_file_names=file_names,
                allergies=allergies,
                delete_flags=request.POST
            )
        else:
            add_patient_medical_info(
                patient_id,
                names,
                dosages,
                history,
                medical_files,
                file_names,
                allergies
            )

        return redirect("medical_dashboard")

    has_data = bool(medical_info)

    return render(request, "patient_medical_dashboard_details.html", {
        "patient": {
            "Patient_ID": decrypted_patient[0],
            "Name": decrypted_patient[1],
            "DOB": decrypted_patient[2]
        },
        "medical_info": medical_info,
        "has_data": has_data
    })

# Download Files
@never_cache
def download_medical_file(request, patient_id, file_index):
    medical_info = patient_medical_dashboard_info(patient_id)
    if not medical_info or file_index >= len(medical_info["files"]):
        return HttpResponse("File not found", status=404)

    file = medical_info["files"][file_index]
    file_stream = io.BytesIO(file["data"])
    return FileResponse(file_stream, as_attachment=True, filename=file["filename"])

# Roster view
def roster_view(request):
    rosters = roster_entries()
    return render(request, "roster.html", {"rosters": rosters})

# Add Roster
@never_cache
def add_roster_view(request):
    if request.method == 'POST':
        day = request.POST.get('Day')
        shift_time = request.POST.get('Shift_Time')
        carer = request.POST.get('Carer')
        patient = request.POST.get('Patient')

        add_roster(day, shift_time, carer, patient)
        return redirect('roster')

    carers = get_carers()
    patients = get_patient()
    return render(request, 'add_roster.html', {'carers': carers, 'patients': patients})

# Delete Roster
@never_cache
def delete_roster_view(request, roster_id):
    if request.method == 'POST':
        delete_roster(roster_id)
        return redirect('roster')

# Care Planner Search
@never_cache
def care_planner_search(request):
    if request.method == 'POST':
        search_type = request.POST.get('search_type')
        search_value = request.POST.get('search_value')

        key = get_encryption_key()

        if search_type == 'Name':
            results = search_patient(name=search_value, key=key)
        else:
            results = search_patient(dob=search_value, key=key)

        if results:
            decrypted = decrypt_patient_data(results, key)

            patients_info = []
            for patient in decrypted:
                patients_info.append({
                    'Patient_ID': patient[0],
                    'Name': patient[1],
                    'DOB': patient[2],
                    'Contact_Number': patient[3],
                })

            return JsonResponse({
                'status': 'success',
                'patients': patients_info
            })

        return JsonResponse({'status': 'not_found'})

    return render(request, 'care_planner_search.html')

# Patient Care Planner Details
@never_cache
def patient_care_planner_details(request, patient_id):
    key = get_encryption_key()
    patient_data = search_patient(key=key)

    selected = [p for p in patient_data if p[0] == patient_id]
    if not selected:
        return HttpResponse("Patient not found", status=404)

    decrypted_patient = decrypt_patient_data([selected[0]], key)[0]

    care_plan = get_care_plan(patient_id)

    medical_info = get_medication(patient_id)

    if request.method == "POST":
        activity_names = request.POST.getlist('activity_name[]')
        activity_completed = request.POST.getlist('activity_completed[]')

        activities = []
        for i, name in enumerate(activity_names):
            completed = i < len(activity_completed)
            activities.append({
                'activity': name,
                'completed': completed
            })

        notes = request.POST.get('Notes') or "N/A"

        if care_plan:
            update_care_plan(care_plan['Care_Planner_ID'], activities, notes)
        else:
            add_care_plan(patient_id, activities, notes)

        return redirect('patient_care_planner_details', patient_id=patient_id)

    has_data = False
    if care_plan:
        activities = care_plan.get('Daily_Activities', [])
        notes = care_plan.get('Notes')
        if activities or notes:
            has_data = True

    return render(request, 'patient_care_planner_details.html', {
        'patient': {
            'Patient_ID': decrypted_patient[0],
            'Name': decrypted_patient[1],
            'DOB': decrypted_patient[2]
        },
        'care_plan': care_plan,
        'medical_info': medical_info,
        'has_data': has_data
    })