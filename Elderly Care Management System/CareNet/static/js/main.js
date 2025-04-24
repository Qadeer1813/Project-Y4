// ====================
// Patient Profile Logic
// ====================

$(document).ready(function () {
    if ($('#searchForm').length && $('#patientForm').length) {

        // Toggle search fields
        $('#searchType').change(function () {
            if ($(this).val() === 'Name') {
                $('#nameField').show();
                $('#dobField').hide();
            } else {
                $('#nameField').hide();
                $('#dobField').show();
            }
        });

        // Handle search form submission
        $('#searchForm').on('submit', function (e) {
            e.preventDefault();

            const searchType = $('#searchType').val();
            let searchValue = searchType === 'Name' ? $('#searchName').val() : $('#searchDob').val();

            $.ajax({
                url: $(this).data('url'),
                type: 'POST',
                data: {
                    'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val(),
                    'search_type': searchType,
                    'search_value': searchValue
                },
                success: function (response) {
                    if (response.status === 'success') {
                        $('#resultsCard').show();
                        $('#noResultsAlert').hide();
                        $('#patientResultsList').empty();
                        window.searchResults = response;

                        response.patients.forEach(function (patient, index) {
                            const resultHtml = `
                                <div class="row patient-result p-2 border-bottom" data-index="${index}">
                                    <div class="col-4">${patient.Name}</div>
                                    <div class="col-4">${patient.DOB}</div>
                                    <div class="col-4">${patient.Contact_Number || 'N/A'}</div>
                                </div>`;
                            $('#patientResultsList').append(resultHtml);
                        });
                    } else {
                        $('#resultsCard').hide();
                        $('#noResultsAlert').show();
                    }
                },
                error: function () {
                    $('#resultsCard').hide();
                    $('#noResultsAlert').show();
                }
            });
        });

        // Handle patient result click
        $(document).on('click', '.patient-result', function () {
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
        });

        // Back to results
        $('#backToResults').click(function () {
            $('#detailCard').hide();
            $('#resultsCard').show();
        });

        // Edit button
        $('#editButton').click(function () {
            $('.patient-field').prop('readonly', false);
            $('#editButton').hide();
            $('#saveButton').show();
        });

        // Save button
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

        // Delete button
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
    }
});

// ====================
// Medical Dashboard Logic
// ====================

$('#medicalSearchForm').on('submit', function (e) {
    e.preventDefault();

    const searchType = $('#searchType').val();
    const searchValue = searchType === 'Name' ? $('#searchName').val() : $('#searchDob').val();

    $.ajax({
        url: $(this).data('url'),
        type: 'POST',
        data: {
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
            search_type: searchType,
            search_value: searchValue
        },
        success: function (response) {
            if (response.status === 'success' && response.patients.length > 0) {
                $('#resultsCard').show();
                $('#noResultsAlert').hide();

                let html = '';
                response.patients.forEach(function (p) {
                    html += `
                        <div class="row patient-result p-2 border-bottom">
                            <div class="col-4">${p.Name}</div>
                            <div class="col-4">${p.DOB}</div>
                            <div class="col-4">
                                <a href="/medical-dashboard/details/${p.Patient_ID}" class="btn btn-sm btn-outline-primary">View Dashboard</a>
                            </div>
                        </div>
                    `;
                });

                $('#patientResultsList').html(html);
            } else {
                $('#resultsCard').hide();
                $('#noResultsAlert').show();
                $('#patientResultsList').empty();
            }
        },
        error: function () {
            $('#resultsCard').hide();
            $('#noResultsAlert').show();
            $('#patientResultsList').empty();
        }
    });
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
        </div>
    `;

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
// Edit/Cancel Logic for Medical Dashboard Details
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
        });

        $('#cancelBtn').on('click', function () {
            location.reload();
        });

        $('.deleteFileBtn').on('click', function () {
            const fileId = $(this).data("id");
            $(`input[name="delete_file_${fileId}"]`).val("1");
            $(this).closest('.file-entry').addClass('text-muted').fadeTo(300, 0.5);
            $(this).text("Marked").prop('disabled', true);
        });
    }
});
