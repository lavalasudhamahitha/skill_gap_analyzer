document.addEventListener('DOMContentLoaded', function () {
    // Initial setup for the tool page
    // Ensure only step 1 is visible initially
    if (document.getElementById('step1')) {
        showStep(1);
    }
});

let currentBranchId = null;

function showStep(step) {
    // Hide all steps
    document.querySelectorAll('.form-step').forEach(el => el.classList.add('d-none'));
    // Update steppers
    document.querySelectorAll('.stepper-item').forEach((el, index) => {
        if (index < step) {
            el.classList.add('active');
        } else {
            el.classList.remove('active');
        }
    });
    // Show current step
    document.getElementById(`step${step}`).classList.remove('d-none');
}

function nextStep(step) {
    if (step === 2) {
        // Validate branch selection
        const branchEl = document.querySelector('input[name="branch"]:checked');
        if (!branchEl) {
            alert("Please select a branch first.");
            return;
        }

        const branchId = branchEl.value;
        if (branchId !== currentBranchId) {
            currentBranchId = branchId;
            fetchBranchData(branchId);
        }
    }

    if (step === 3) {
        // Validate skills selection
        // Even if none, they can proceed, but we should make sure they saw it
    }

    showStep(step);
}

function prevStep(step) {
    showStep(step);
}

function fetchBranchData(branchId) {
    const loader = document.getElementById('skills-loader');
    const skillsContainer = document.getElementById('skills-container');
    const rolesContainer = document.getElementById('roles-container');

    loader.classList.remove('d-none');
    skillsContainer.innerHTML = '';
    rolesContainer.innerHTML = '';

    fetch(`/api/get_branch_data/${branchId}/`)
        .then(response => response.json())
        .then(data => {
            loader.classList.add('d-none');

            // Render skills as checkbox cards
            if (data.skills.length === 0) {
                skillsContainer.innerHTML = `<div class="col-12 text-center text-muted py-4"><p>No skills mapped to this branch yet. Create mappings in admin panel.</p></div>`;
            } else {
                data.skills.forEach(skill => {
                    skillsContainer.innerHTML += `
                        <div class="col-md-4 col-lg-3 col-6">
                            <label class="w-100 h-100">
                                <input type="checkbox" name="skills" class="card-input-element d-none" value="${skill.id}">
                                <div class="card card-input border-2 h-100 p-3 shadow-sm d-flex justify-content-center align-items-center text-center">
                                    <h6 class="mb-0 fw-semibold">${skill.name}</h6>
                                </div>
                            </label>
                        </div>
                    `;
                });
            }

            // Render job roles as radio cards
            if (data.job_roles.length === 0) {
                rolesContainer.innerHTML = `<div class="col-12 text-center text-muted py-4"><p>No job roles mapped to this branch yet. Create mappings in admin panel.</p></div>`;
                document.getElementById('submitAnalysisBtn').disabled = true;
            } else {
                document.getElementById('submitAnalysisBtn').disabled = false;
                data.job_roles.forEach(role => {
                    rolesContainer.innerHTML += `
                        <div class="col-md-6">
                            <label class="w-100 h-100">
                                <input type="radio" name="job_role" class="card-input-element d-none" value="${role.id}">
                                <div class="card card-input border-2 h-100 p-4 shadow-sm text-center">
                                    <h5 class="mb-0 fw-bold">${role.name}</h5>
                                </div>
                            </label>
                        </div>
                    `;
                });
            }
        })
        .catch(error => {
            console.error('Error fetching data:', error);
            loader.classList.add('d-none');
            skillsContainer.innerHTML = `<div class="alert alert-danger">Error loading data. Please try again.</div>`;
        });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function submitAnalysis() {
    const jobRoleEl = document.querySelector('input[name="job_role"]:checked');
    if (!jobRoleEl) {
        alert("Please select a target job role.");
        return;
    }

    // Disable button and show loading text
    const btn = document.getElementById('submitAnalysisBtn');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Analyzing...';
    btn.disabled = true;

    const jobRoleId = jobRoleEl.value;

    // Get all checked skills
    const selectedSkills = Array.from(document.querySelectorAll('input[name="skills"]:checked'))
        .map(el => el.value);

    const payload = {
        job_role_id: jobRoleId,
        student_skills: selectedSkills
    };

    fetch('/tool/submit/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(payload)
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.href = data.redirect_url;
            } else {
                alert("Error processing analysis: " + data.error);
                btn.innerHTML = originalText;
                btn.disabled = false;
            }
        })
        .catch(error => {
            console.error("Error:", error);
            alert("An error occurred. Please try again.");
            btn.innerHTML = originalText;
            btn.disabled = false;
        });
}
