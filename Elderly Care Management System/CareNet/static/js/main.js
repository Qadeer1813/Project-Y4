// ====================
// Shared Search Handler
// ====================

function setupSearchForm({ formId, nameInputId, dobInputId, resultCardId, showDashboardLink = false, showCarePlanLink = false }) {
    const $form = $(formId);
    const $nameField = $(nameInputId).closest('.form-group');
    const $dobField = $(dobInputId).closest('.form-group');
    const $resultsCard = $(resultCardId);
    const $resultsList = $resultsCard.find('#patientResultsList');
    const $alert = $('#noResultsAlert');

    $form.find('#searchType').on('change', function () {
        if ($(this).val() === 'Name') {
            $nameField.show();
            $dobField.hide();
        } else {
            $nameField.hide();
            $dobField.show();
        }
    }).trigger('change');

    $form.on('submit', function (e) {
        e.preventDefault();
        const searchType = $form.find('#searchType').val();
        const searchValue = searchType === 'Name' ? $(nameInputId).val() : $(dobInputId).val();

        $.ajax({
            url: $form.data('url'),
            type: 'POST',
            data: {
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
                search_type: searchType,
                search_value: searchValue
            },
            success: function (response) {
                $resultsList.empty();
                if (response.status === 'success' && response.patients.length > 0) {
                    window.searchResults = response;
                    $resultsCard.show();
                    $alert.hide();
                    response.patients.forEach((p, index) => {
                        const buttonHtml = showDashboardLink
                            ? `<a href="/medical-dashboard/details/${p.Patient_ID}" class="btn btn-sm btn-outline-primary ml-2">View Dashboard</a>`
                            : showCarePlanLink
                            ? `<a href="/care_planner/${p.Patient_ID}" class="btn btn-sm btn-outline-primary ml-2">View Care Plan</a>` : '';
                        const html = `
                            <div class="row patient-result p-2 border-bottom" data-index="${index}">
                                <div class="col-4">${p.Name}</div>
                                <div class="col-4">${p.DOB}</div>
                                <div class="col-4 d-flex justify-content-between align-items-center">
                                    <span>${p.Contact_Number || 'N/A'}</span>
                                    ${buttonHtml}
                                </div>
                            </div>`;
                        $resultsList.append(html);
                    });
                } else {
                    $resultsCard.hide();
                    $alert.show();
                }
            },
            error: function () {
                $resultsCard.hide();
                $alert.show();
                $resultsList.empty();
            }
        });
    });
}

// ====================
// Helpers
// ====================

function startAdding(formSelector, noticeSelector, showEditSection = false) {
    $(formSelector).show();
    $(noticeSelector).remove();
    if (showEditSection) {
        $('#editOnlySection').removeClass('d-none');
    }
    $('#addMedicationBtn').removeClass('d-none');
}

function RemovalButton(buttonSelector, hiddenInputSelector) {
    $(document).on('click', buttonSelector, function () {
        const row = $(this).closest('.form-row, .file-entry');
        row.find(hiddenInputSelector).val("1");
        row.addClass('text-muted').fadeTo(300, 0.5);
        $(this).text("Marked").prop('disabled', true);
    });
}

// ====================
// Main Logic
// ====================

$(document).ready(function () {

    // Search forms
    const searchForms = [
        { id: '#searchForm', dashboard: false, careplan: false },
        { id: '#medicalSearchForm', dashboard: true, careplan: false },
        { id: '#carePlannerSearchForm', dashboard: false, careplan: true }
    ];
    searchForms.forEach(form => {
        if ($(form.id).length) {
            setupSearchForm({
                formId: form.id,
                nameInputId: '#searchName',
                dobInputId: '#searchDob',
                resultCardId: '#resultsCard',
                showDashboardLink: form.dashboard,
                showCarePlanLink: form.careplan
            });
        }
    });

    // Patient form view/edit/save/delete
    $(document).on('click', '.patient-result', function () {
        const index = $(this).data('index');
        const patient = window.searchResults.patients[index];

        ['Patient_ID', 'Name', 'DOB', 'Contact_Number', 'Email_Address', 'Home_Address', 'Next_Of_Kin_Name', 'Emergency_Contact_Number', 'Emergency_Email_Address', 'Next_Of_Kin_Home_Address']
            .forEach(id => $(`#${id}`).val(patient[id]));

        $('#resultsCard').hide();
        $('#detailCard').show();
        $('.patient-field').prop('readonly', true);
        $('#saveButton').hide();
        $('#editButton').show();
    });

    $('#backToResults').click(() => {
        $('#detailCard').hide();
        $('#resultsCard').show();
    });

    $('#editButton').click(() => {
        $('.patient-field').prop('readonly', false);
        $('#editButton').hide();
        $('#saveButton').show();
    });

    $('#saveButton').click(() => {
        $.ajax({
            url: $('#patientForm').data('update-url'),
            type: 'POST',
            data: $('#patientForm').serialize() + '&csrfmiddlewaretoken=' + $('input[name=csrfmiddlewaretoken]').val(),
            success: function (response) {
                if (response.status === 'success') {
                    alert('Patient updated successfully');
                    $('.patient-field').prop('readonly', true);
                    $('#saveButton').hide();
                    $('#editButton').show();
                    $('#detailCard').hide();
                    $('#resultsCard').hide();
                    $('#searchForm').submit();
                } else {
                    alert('Error updating patient');
                }
            },
            error: () => alert('An error occurred while updating.')
        });
    });

    $('#deleteButton').click(function () {
        const Patient_ID = $('#Patient_ID').val();
        if (confirm('Are you sure you want to delete this patient?')) {
            $.ajax({
                url: $('#patientForm').data('delete-url'),
                type: 'POST',
                data: {
                    csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
                    Patient_ID: Patient_ID
                },
                success: function (response) {
                    if (response.status === 'success') {
                        alert('Patient deleted');
                        $('#detailCard').hide();
                        $('#resultsCard').show();
                        $('#searchForm').submit();
                    } else {
                        alert('Error deleting patient');
                    }
                },
                error: () => alert('Delete failed')
            });
        }
    });

    // Dynamic medication fields
    $(document).on('click', '#addMedicationBtn', function () {
        $('#medicationFieldsWrapper').append(`
            <div class="form-row mb-2 medication-group">
                <div class="col-md-5">
                    <input type="text" class="form-control" name="Medication_Name[]" required placeholder="Medication Name">
                </div>
                <div class="col-md-5">
                    <input type="text" class="form-control" name="Medication_Dosage[]" required placeholder="Dosage">
                </div>
                <div class="col-md-2 d-flex align-items-end">
                    <button type="button" class="btn btn-danger btn-sm removeMedicationBtn">Remove</button>
                    <input type="hidden" class="med-delete-flag" name="delete_medication[]" value="0">
                </div>
            </div>
        `);
    });

    $(document).on('click', '.removeMedicationBtn', function () {
        $(this).closest('.medication-group').remove();
    });

    // Medical Dashboard Form
    $(document).on('click', '#startAddingMedicalDetails', () => startAdding('#medicalDetailForm', '#noMedicalDataNotice'));

    if ($('#medicalDetailForm').length) {
        $('#editBtn').click(() => {
            $('#medicalDetailForm').find('input, textarea, select').prop('readonly', false).prop('disabled', false);
            $('#addMedicationBtn, #saveBtn, #cancelBtn').removeClass('d-none').show();
            $('#fileUploadSection').removeClass('d-none');
            $('#editBtn').hide();
            $('.deleteFileBtn').show();
            $('.edit-only').removeClass('d-none');
            RemovalButton('.removeMedicationBtn', '.med-delete-flag');
            RemovalButton('.deleteFileBtn', '.delete-flag');
        });

        $('#cancelBtn').click(() => location.reload());
    }

    // Care Plan Logic
    $(document).on('click', '#startAddingCarePlan', () => startAdding('#carePlanForm', '#noCarePlanDataNotice', true));

    $('#addActivityBtn').click(() => {
        $('#activitiesWrapper').append(`
            <div class="form-row mb-2 activity-row">
                <div class="col-md-8">
                    <input type="text" class="form-control" name="activity_name[]" required placeholder="Activity Name">
                </div>
                <div class="col-md-2 d-flex align-items-center">
                    <input type="checkbox" name="activity_completed[]" value="1">
                </div>
                <div class="col-md-2">
                    <button type="button" class="btn btn-danger remove-activity-btn">Remove</button>
                </div>
            </div>
        `).find('input[name="activity_name[]"]').last().focus();
    });

    $(document).on('click', '.remove-activity-btn', function () {
        $(this).closest('.activity-row').remove();
    });

    $('#editCarePlanBtn').click(() => {
        $('#carePlanForm input:not([name="Medication_Name\\[\\]"]):not([name="Medication_Dosage\\[\\]"]), #carePlanForm textarea, #carePlanForm select')
            .prop('readonly', false)
            .prop('disabled', false);
        $('.edit-only').removeClass('d-none');
        $('#editCarePlanBtn').hide();
        $('#saveCarePlanBtn').show();
        $('#cancelCarePlanBtn').show();
    });

    $('#cancelCarePlanBtn').click(() => location.reload());

    $('#carePlanForm').submit(function (e) {
        e.preventDefault();
        $.ajax({
            url: window.location.href,
            type: 'POST',
            data: $(this).serialize(),
            success: function () {
                alert('Care plan saved successfully!');
                window.location.href = '/care_planner/';
            },
            error: function () {
                alert('Error saving care plan.');
            }
        });
    });
});