from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from .app import create_patient, search_patient, decrypt_patient_data, update_patient, delete_patient, reencryption
from . import config
from .functions import get_encryption_key, verify_password, current_key
from .authentication_service import create_user, get_user_by_username

# Create your views here.
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

def logout(request):
    request.session.flush()
    return redirect('login')

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

def delete_patient_profile(request):
    if request.method == 'POST':
        Patient_ID = request.POST.get('Patient_ID')
        success = delete_patient(Patient_ID)
        return JsonResponse({'status': 'success' if success else 'error'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

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
            patient = results[0]
            decrypted = decrypt_patient_data([patient], key)[0]

            has_medical_data = False

            return render(request, 'medical_dashboard.html', {
                'patient': decrypted,
                'has_medical_data': has_medical_data
            })

        return render(request, 'medical_dashboard.html', {
            'error': 'No matching patient found.'
        })

    return render(request, 'medical_dashboard.html')
