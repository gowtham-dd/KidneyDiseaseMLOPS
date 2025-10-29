// Global variables
let currentDiagnosisId = null;
let currentFile = null;
let currentImagePath = null;

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
});

// Initialize event listeners
function initializeEventListeners() {
    // File upload handling
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const uploadForm = document.getElementById('uploadForm');
    
    if (uploadArea && fileInput) {
        uploadArea.addEventListener('click', () => fileInput.click());
        uploadArea.addEventListener('dragover', handleDragOver);
        uploadArea.addEventListener('drop', handleFileDrop);
        
        fileInput.addEventListener('change', handleFileSelect);
        if (uploadForm) {
            uploadForm.addEventListener('submit', handleFormSubmit);
        }
    }
    
    // Patient form handling
    const addPatientForm = document.getElementById('addPatientForm');
    if (addPatientForm) {
        addPatientForm.addEventListener('submit', function(e) {
            e.preventDefault();
            addPatient();
        });
    }
}

// File upload handling
function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    e.dataTransfer.dropEffect = 'copy';
    document.getElementById('uploadArea').style.backgroundColor = '#f0f8ff';
}

function handleFileDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    document.getElementById('uploadArea').style.backgroundColor = '';
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

function handleFileSelect(e) {
    if (e.target.files.length > 0) {
        handleFile(e.target.files[0]);
    }
}

function handleFile(file) {
    const fileName = document.getElementById('fileName');
    const fileInfo = document.getElementById('fileInfo');
    const processBtn = document.querySelector('.btn-process');
    
    if (fileName) fileName.textContent = file.name;
    if (fileInfo) fileInfo.style.display = 'flex';
    if (processBtn) processBtn.disabled = false;
    
    // Store file reference
    currentFile = file;
}

function removeFile() {
    const fileInput = document.getElementById('fileInput');
    const fileInfo = document.getElementById('fileInfo');
    const processBtn = document.querySelector('.btn-process');
    
    if (fileInput) fileInput.value = '';
    if (fileInfo) fileInfo.style.display = 'none';
    if (processBtn) processBtn.disabled = true;
    currentFile = null;
}

async function handleFormSubmit(e) {
    e.preventDefault();
    
    if (!currentFile) {
        alert('Please select a file first');
        return;
    }
    
    const patientId = document.getElementById('patient_id').value;
    if (!patientId) {
        alert('Please select a patient first');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', currentFile);
    formData.append('patient_id', patientId);
    
    const loadingOverlay = document.getElementById('loadingOverlay');
    const processBtn = document.querySelector('.btn-process');
    
    if (loadingOverlay) loadingOverlay.style.display = 'flex';
    if (processBtn) processBtn.disabled = true;
    
    try {
        const response = await fetch('/diagnose', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayDiagnosisResults(result);
            // Don't reset form to allow sending report
        } else {
            alert('Error: ' + result.error);
            // Reset form on error
            removeFile();
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while processing the file');
        removeFile();
    } finally {
        if (loadingOverlay) loadingOverlay.style.display = 'none';
        if (processBtn) processBtn.disabled = false;
    }
}

function displayDiagnosisResults(result) {
    const resultsContent = document.getElementById('resultsContent');
    
    if (!resultsContent) return;
    
    // Determine severity class
    const severityClass = result.severity.toLowerCase();
    
    // Determine confidence badge
    let confidenceBadge = 'confidence-low';
    if (result.confidence > 0.9) {
        confidenceBadge = 'confidence-high';
    } else if (result.confidence > 0.8) {
        confidenceBadge = 'confidence-medium';
    }
    
    resultsContent.innerHTML = `
        <div class="diagnosis-report">
            <div class="report-header">
                <h3><i class="fas fa-diagnoses"></i> Kidney Diagnosis Report</h3>
                <p>Generated on ${new Date().toLocaleString()}</p>
            </div>
            
            <div class="report-section ${severityClass}">
                <h4><i class="fas fa-stethoscope"></i> Diagnosis Summary</h4>
                <div class="diagnosis-stats">
                    <div class="stat">
                        <label>Condition:</label>
                        <span class="condition-value">${result.condition}</span>
                    </div>
                    <div class="stat">
                        <label>Confidence:</label>
                        <span class="confidence-value ${confidenceBadge}">${(result.confidence * 100).toFixed(1)}%</span>
                    </div>
                    <div class="stat">
                        <label>Severity:</label>
                        <span class="severity-badge severity-${severityClass}">${result.severity}</span>
                    </div>
                </div>
            </div>
            
            ${result.image_url ? `
            <div class="report-section">
                <h4><i class="fas fa-image"></i> CT Scan Image</h4>
                <div class="result-image">
                    <img src="${result.image_url}" alt="Kidney CT Scan" style="max-width: 100%; border-radius: 8px;">
                </div>
            </div>
            ` : ''}
            
            <div class="report-section">
                <h4><i class="fas fa-search"></i> Clinical Findings</h4>
                <p><strong>Description:</strong> ${result.findings.description}</p>
                <ul class="findings-list">
                    ${result.findings.details.map(finding => `<li>${finding}</li>`).join('')}
                </ul>
            </div>
            
            <div class="report-section">
                <h4><i class="fas fa-clipboard-list"></i> Medical Recommendations</h4>
                <ol class="recommendations-list">
                    ${result.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                </ol>
            </div>
            
            <div class="email-section">
                <h4><i class="fas fa-envelope"></i> Send Report to Patient</h4>
                <p>Click the button below to send this medical report to the patient via email.</p>
                <button id="sendReportBtn" class="btn btn-primary">
                    <i class="fas fa-paper-plane"></i> Send Medical Report
                </button>
                <div class="email-status">
                    <i class="fas fa-info-circle"></i>
                    <span>Report will be sent to the patient's registered email address</span>
                </div>
            </div>
        </div>
    `;
    
    // Store diagnosis ID and image path for sending report
    currentDiagnosisId = result.diagnosis_id;
    currentImagePath = result.image_path;
    
    // Re-attach event listener for the send report button
    const sendReportBtn = document.getElementById('sendReportBtn');
    if (sendReportBtn) {
        sendReportBtn.addEventListener('click', sendMedicalReport);
    }
}

async function sendMedicalReport() {
    if (!currentDiagnosisId) {
        alert('No diagnosis available to send');
        return;
    }
    
    const sendBtn = document.getElementById('sendReportBtn');
    if (!sendBtn) return;
    
    const originalText = sendBtn.innerHTML;
    
    sendBtn.disabled = true;
    sendBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
    
    try {
        const response = await fetch('/send_report', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                diagnosis_id: currentDiagnosisId,
                image_path: currentImagePath
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Update UI to show success
            const emailSection = document.querySelector('.email-section');
            if (emailSection) {
                emailSection.innerHTML = `
                    <div style="text-align: center; color: #28a745;">
                        <i class="fas fa-check-circle fa-2x" style="margin-bottom: 1rem;"></i>
                        <h4>Report Sent Successfully!</h4>
                        <p>The medical report has been sent to the patient's email address.</p>
                        <p><small>${result.message}</small></p>
                    </div>
                `;
            }
        } else {
            alert('Error sending report: ' + result.error);
            sendBtn.disabled = false;
            sendBtn.innerHTML = originalText;
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while sending the report');
        sendBtn.disabled = false;
        sendBtn.innerHTML = originalText;
    }
}

// Patient management
function showAddPatientModal() {
    const modal = document.getElementById('addPatientModal');
    if (modal) {
        modal.style.display = 'block';
    }
}

function closeAddPatientModal() {
    const modal = document.getElementById('addPatientModal');
    if (modal) {
        modal.style.display = 'none';
        // Reset form
        const form = document.getElementById('addPatientForm');
        if (form) form.reset();
    }
}

async function addPatient() {
    const form = document.getElementById('addPatientForm');
    if (!form) return;
    
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    
    // Remove empty fields
    Object.keys(data).forEach(key => {
        if (!data[key]) delete data[key];
    });
    
    console.log('Sending patient data:', data);
    
    try {
        const response = await fetch('/add_patient', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert(`Patient added successfully! Patient ID: ${result.patient_id}`);
            closeAddPatientModal();
            location.reload();
        } else {
            alert('Error: ' + result.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while adding patient');
    }
}

// Close modal when clicking outside
window.addEventListener('click', function(event) {
    const modal = document.getElementById('addPatientModal');
    if (modal && event.target === modal) {
        closeAddPatientModal();
    }
});

// Utility functions
function updateStatus(message) {
    const statusElement = document.getElementById('statusValue');
    if (statusElement) {
        statusElement.textContent = message;
    }
}

// Format date for display
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

// Enhanced file handling for diagnose page
document.addEventListener('DOMContentLoaded', function() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const uploadForm = document.getElementById('uploadForm');

    if (uploadArea && fileInput) {
        uploadArea.addEventListener('click', () => fileInput.click());
        
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.stopPropagation();
            uploadArea.style.backgroundColor = '#f0f8ff';
        });
        
        uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            e.stopPropagation();
            uploadArea.style.backgroundColor = '';
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            e.stopPropagation();
            uploadArea.style.backgroundColor = '';
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFile(files[0]);
            }
        });

        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFile(e.target.files[0]);
            }
        });
        
        if (uploadForm) {
            uploadForm.addEventListener('submit', handleFormSubmit);
        }
    }
});

// Auto-select patient from URL parameter
document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const patientId = urlParams.get('patient_id');
    if (patientId) {
        const patientIdInput = document.getElementById('patient_id');
        if (patientIdInput) {
            patientIdInput.value = patientId;
        }
    }
});