// ====================
// Shared Search Handler
// ====================

function setupSearchForm({
    formId,
    nameInputId,
    dobInputId,
    resultCardId,
    showDashboardLink = false
}) {
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
                if (response.status === 'success' && response.patients.length > 0) {
                     window.searchResults = response;

                    $resultsCard.show();
                    $alert.hide();
                    $resultsList.empty();

                    response.patients.forEach((p, index) => {
                        let html = `
                            <div class="row patient-result p-2 border-bottom" data-index="${index}">
                                <div class="col-4">${p.Name}</div>
                                <div class="col-4">${p.DOB}</div>
                                <div class="col-4 d-flex justify-content-between align-items-center">
                                    <span>${p.Contact_Number || 'N/A'}</span>
                                    ${showDashboardLink ? `<a href="/medical-dashboard/details/${p.Patient_ID}" class="btn btn-sm btn-outline-primary ml-2">View Dashboard</a>` : ''}
                                </div>
                            </div>`;
                        $resultsList.append(html);
                    });
                } else {
                    $resultsCard.hide();
                    $alert.show();
                    $resultsList.empty();
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
// Search Usage
// ====================
$(document).ready(function () {
    if ($('#searchForm').length) {
        setupSearchForm({
            formId: '#searchForm',
            nameInputId: '#searchName',
            dobInputId: '#searchDob',
            resultCardId: '#resultsCard',
            showDashboardLink: false
        });
    }

    if ($('#medicalSearchForm').length) {
        setupSearchForm({
            formId: '#medicalSearchForm',
            nameInputId: '#searchName',
            dobInputId: '#searchDob',
            resultCardId: '#resultsCard',
            showDashboardLink: true
        });
    }
});

// ====================
// Patient Profile Logic
// ====================
$(document).on('click', '.patient-result', function () {
    if ($('#patientForm').length) {
        const index = $(this).data('index');
        const patient = window.searchResults.patients[index];

        $('#Patient_ID').val(patient.Patient_ID);
        $('#Name').val(patient.Name);
        $('#DOB').val(patient.DOB);
        $('#Contact_Number').val(patient.Contact_Number);
        $('#Email_Address').val(patient.Email_Address);
        $('#Home_Address').val(patient.Home_Address);
        $('#Next_Of_Kin_Name').val(patient.Next_Of_Kin_Name);
        $('#Emergency_Contact_Number').val(patient.Emergency_Contact_Number);
        $('#Emergency_Email_Address').val(patient.Emergency_Email_Address);
        $('#Next_Of_Kin_Home_Address').val(patient.Next_Of_Kin_Home_Address);

        $('#resultsCard').hide();
        $('#detailCard').show();
        $('.patient-field').prop('readonly', true);
        $('#saveButton').hide();
        $('#editButton').show();
    }
});

$('#backToResults').click(function () {
    $('#detailCard').hide();
    $('#resultsCard').show();
});

$('#editButton').click(function () {
    $('.patient-field').prop('readonly', false);
    $('#editButton').hide();
    $('#saveButton').show();
});

$('#saveButton').click(function () {
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
            } else {
                alert('Error updating patient');
            }
        },
        error: function () {
            alert('An error occurred while updating.');
        }
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
            error: function () {
                alert('Delete failed');
            }
        });
    }
});

// ====================
// Dynamic Medication Fields
// ====================
let medicationIndex = 1;

function updateRemoveButtons() {
    $('.removeMedicationBtn').hide();
    if ($('.medication-group').length > 1) {
        $('.removeMedicationBtn').show();
    }
}

$(document).on('click', '#addMedicationBtn', function () {
    medicationIndex++;

    const newRow = `
        <div class="form-group medication-group">
            <div class="form-row">
                <div class="col-md-5">
                    <label for="Medication_Name_${medicationIndex}">Medication Name ${medicationIndex}</label>
                    <input type="text" class="form-control" name="Medication_Name[]" id="Medication_Name_${medicationIndex}" required>
                </div>
                <div class="col-md-5">
                    <label for="Medication_Dosage_${medicationIndex}">Dosage ${medicationIndex}</label>
                    <input type="text" class="form-control" name="Medication_Dosage[]" id="Medication_Dosage_${medicationIndex}" required>
                </div>
                <div class="col-md-2 d-flex align-items-end">
                    <button type="button" class="btn btn-danger btn-sm removeMedicationBtn">Remove</button>
                </div>
            </div>
        </div>`;
    $('#medicationFieldsWrapper').append(newRow);
    updateRemoveButtons();
});

$(document).on('click', '.removeMedicationBtn', function () {
    $(this).closest('.medication-group').remove();
    updateRemoveButtons();
});

// ====================
// File Upload Preview
// ====================
let selectedFiles = [];

document.addEventListener("DOMContentLoaded", function () {
    const fileInput = document.getElementById("Medical_File");
    const fileListDiv = document.getElementById("selectedFilesList");

    fileInput.addEventListener("change", function () {
        Array.from(fileInput.files).forEach(file => {
            if (!selectedFiles.some(f => f.name === file.name && f.size === file.size)) {
                selectedFiles.push(file);
            }
        });
        updateFileList();
    });

    function updateFileList() {
        fileListDiv.innerHTML = "";

        selectedFiles.forEach((file, index) => {
            const fileRow = document.createElement("div");
            fileRow.classList.add("d-flex", "align-items-center", "mb-2");

            const nameSpan = document.createElement("span");
            nameSpan.classList.add("mr-3");
            nameSpan.textContent = file.name;

            const removeBtn = document.createElement("button");
            removeBtn.classList.add("btn", "btn-danger", "btn-sm", "ml-2");
            removeBtn.textContent = "Remove";

            removeBtn.onclick = () => {
                selectedFiles.splice(index, 1);
                updateFileList();
            };

            fileRow.appendChild(nameSpan);
            fileRow.appendChild(removeBtn);
            fileListDiv.appendChild(fileRow);
        });

        const dataTransfer = new DataTransfer();
        selectedFiles.forEach(file => dataTransfer.items.add(file));
        fileInput.files = dataTransfer.files;
    }
});

// ====================
// Edit/Cancel for Medical Dashboard
// ====================
$(document).ready(function () {
    const detailForm = $('#medicalDetailForm');

    if (detailForm.length) {
        $('#editBtn').on('click', function () {
            detailForm.find('input, textarea, select').prop('readonly', false).prop('disabled', false);
            $('#addMedicationBtn, #saveBtn, #cancelBtn').show();
            $('#fileUploadSection').removeClass('d-none');
            $('#editBtn').hide();
            $('.deleteFileBtn').show();
            $('.edit-only').removeClass('d-none');

            RemovalButton('.removeMedicationBtn', '.med-delete-flag');
            RemovalButton('.deleteFileBtn', '.delete-flag');
        });

        $('#cancelBtn').on('click', function () {
            location.reload();
        });

        function RemovalButton(buttonSelector, hiddenInputSelector) {
            $(document).on('click', buttonSelector, function () {
                const row = $(this).closest('.form-row, .file-entry');
                row.find(hiddenInputSelector).val("1");
                row.addClass('text-muted').fadeTo(300, 0.5);
                $(this).text("Marked").prop('disabled', true);
            });
        }
    }
});

