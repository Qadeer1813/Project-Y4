from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from .app import create_patient, search_patient, decrypt_patient_data

# Create your views here.
def home(request):
    return render(request, 'home.html')

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

        # Search for patients based on search type
        if search_type == 'Name':
            results = search_patient(name=search_value)
        else:  # search_type == 'DOB'
            results = search_patient(dob=search_value)

        if results:
            # Decrypt the patient data
            decrypted_results = decrypt_patient_data(results)
            # Create a list to hold all patient data
            patients_data = []

            # Process all results
            for patient in decrypted_results:
                patient_data = {
                    'Name': patient[1],
                    'DOB': patient[2],
                    'Contact_Number': patient[3],
                    'Email_Address': patient[4],
                    'Home_Address': patient[5],
                    'Next_Of_Kin_Name': patient[6],
                    'Emergency_Contact_Number': patient[7],
                    'Next_Of_Kin_Home_Address': patient[8],
                    'Emergency_Email_Address': patient[9]
                }
                patients_data.append(patient_data)

            return JsonResponse({'status': 'success', 'patients': patients_data})
        else:
            return JsonResponse({'status': 'not_found'})

    return render(request, 'search_patient_profile.html')