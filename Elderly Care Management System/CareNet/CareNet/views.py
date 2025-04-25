import io
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, FileResponse
from django.views.decorators.cache import never_cache
from .app import create_patient, search_patient, decrypt_patient_data, update_patient, delete_patient, reencryption, \
    patient_medical_info, add_patient_medical_info, patient_medical_dashboard_info, update_patient_medical_info
from . import config
from .functions import get_encryption_key, verify_password, current_key
from .authentication_service import create_user, get_user_by_username

# Create your views here.
@never_cache
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = get_user_by_username(username)

        if user and verify_password(user[0], password):
            request.session['username'] = username
            request.session['role'] = user[1]
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')

@never_cache
def logout(request):
    request.session.flush()
    return redirect('login')

@never_cache
def create_user_view(request):
    if request.session.get('role') != 'admin':
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')

        create_user(username, password, role)
        return redirect('home')

    return render(request, 'create_user.html')

@never_cache
def home(request):
    if current_key is None:
        try:
            get_encryption_key(force_refresh=True)
            print("Key retrieved .")
        except Exception as e:
            print("Failed to retrieved key:", str(e))

    return render(request, 'home.html', {
        'maintenance_mode': config.MAINTENANCE_MODE,
    })

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
            # Decrypt the patient data
            decrypted_results = decrypt_patient_data(results, key)
            # Create a list to hold all patient data
            patients_data = []

            # Process all results
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

@never_cache
def delete_patient_profile(request):
    if request.method == 'POST':
        Patient_ID = request.POST.get('Patient_ID')
        success = delete_patient(Patient_ID)
        return JsonResponse({'status': 'success' if success else 'error'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

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

@never_cache
def patient_medical_dashboard_details(request, patient_id):
    key = get_encryption_key()
    patient_data = search_patient(key=key)

    selected = [p for p in patient_data if p[0] == patient_id]
    if not selected:
        return HttpResponse("Patient not found", status=404)

    decrypted_patient = decrypt_patient_data([selected[0]], key)[0]

    if request.method == "POST":
        names = request.POST.getlist('Medication_Name[]')
        dosages = request.POST.getlist('Medication_Dosage[]')
        history = request.POST.get('Medical_History_Text')
        allergies = request.POST.get('Allergies')

        uploaded_files = request.FILES.getlist("Medical_File")
        medical_files = [f.read() for f in uploaded_files]
        file_names = [f.name for f in uploaded_files]

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

        return redirect("patient_medical_dashboard_details", patient_id=patient_id)

    medical_info = patient_medical_dashboard_info(patient_id)

    has_data = (
        medical_info and (
            medical_info.get('medications') or
            medical_info.get('history') or
            medical_info.get('allergies') or
            medical_info.get('files')
        )
    )

    return render(request, "patient_medical_dashboard_details.html", {
        "patient": {
            "Patient_ID": decrypted_patient[0],
            "Name": decrypted_patient[1],
            "DOB": decrypted_patient[2]
        },
        "medical_info": medical_info,
        "has_data": has_data
    })

@never_cache
def download_medical_file(request, patient_id, file_index):
    medical_info = patient_medical_dashboard_info(patient_id)
    if not medical_info or file_index >= len(medical_info["files"]):
        return HttpResponse("File not found", status=404)

    file = medical_info["files"][file_index]
    file_stream = io.BytesIO(file["data"])
    return FileResponse(file_stream, as_attachment=True, filename=file["filename"])

@never_cache
def add_patient_medical_details(request, patient_id):
    key = get_encryption_key()
    patient_data = search_patient(key=key)

    selected = [p for p in patient_data if p[0] == patient_id]
    if not selected:
        return HttpResponse("Patient not found", status=404)

    decrypted = decrypt_patient_data([selected[0]], key)[0]

    if request.method == 'POST':
        names = request.POST.getlist('Medication_Name[]')
        dosages = request.POST.getlist('Medication_Dosage[]')
        allergies = request.POST.get('Allergies')
        medical_history_text = request.POST.get('Medical_History_Text')
        uploaded_files = request.FILES.getlist('Medical_File')
        medical_files = [file.read() for file in uploaded_files if file]
        medical_filenames = [file.name for file in uploaded_files if file]

        success = add_patient_medical_info(
            patient_id,
            names,
            dosages,
            medical_history_text,
            medical_files,
            medical_filenames,
            allergies
        )

        if not success:
            return HttpResponse("Something went wrong while saving", status=500)

        return redirect('medical_dashboard')

    return render(request, 'add_patient_medical_details.html', {
        'patient': {
            'Patient_ID': decrypted[0],
            'Name': decrypted[1],
            'DOB': decrypted[2]
        }
    })
