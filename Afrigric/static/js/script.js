document.addEventListener('DOMContentLoaded', function() {
    // Initialize all tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Global error handler for AJAX requests
    $(document).ajaxError(function(event, jqxhr, settings, thrownError) {
        console.error("AJAX Error:", thrownError);
        alert("An error occurred during processing. Please try again.");
    });

    // Initialize all file upload forms
    const initFileUploadForm = function(form) {
        const fileInput = form.querySelector('input[type="file"]');
        const uploadArea = form.querySelector('.upload-area');
        const selectButton = form.querySelector('#selectButton');
        const fileInfo = form.querySelector('#fileInfo');
        const previewImage = form.querySelector('#previewImage');
        const fileName = form.querySelector('#fileName');
        const removeButton = form.querySelector('#removeButton');
        const analyzeButton = form.querySelector('#analyzeButton');

        if (!fileInput || !uploadArea) return;

        // Handle file selection
        if (selectButton) {
            selectButton.addEventListener('click', function() {
                fileInput.click();
            });
        }

        // Handle file input change
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                // Check file size (client-side validation)
                if (file.size > 16 * 1024 * 1024) {
                    alert('File size exceeds 16MB limit');
                    return;
                }
                
                // Check file type
                const fileType = file.name.split('.').pop().toLowerCase();
                if (!['jpg', 'jpeg', 'png'].includes(fileType)) {
                    alert('Only JPG, JPEG, and PNG files are allowed');
                    return;
                }
                
                // Create preview
                const reader = new FileReader();
                reader.onload = function(event) {
                    if (previewImage) previewImage.src = event.target.result;
                    if (fileName) fileName.textContent = file.name;
                    
                    // Show file info and hide upload area
                    if (uploadArea) uploadArea.classList.add('d-none');
                    if (fileInfo) fileInfo.classList.remove('d-none');
                    
                    // Enable analyze button
                    if (analyzeButton) analyzeButton.disabled = false;
                }
                reader.readAsDataURL(file);
            }
        });

        // Handle remove button
        if (removeButton) {
            removeButton.addEventListener('click', function() {
                // Reset file input
                fileInput.value = '';
                
                // Hide file info and show upload area
                if (fileInfo) fileInfo.classList.add('d-none');
                if (uploadArea) uploadArea.classList.remove('d-none');
                
                // Disable analyze button
                if (analyzeButton) analyzeButton.disabled = true;
            });
        }

        // Handle form submission
        form.addEventListener('submit', function(e) {
            const file = fileInput.files[0];
            if (!file) {
                e.preventDefault();
                alert('Please select an image file first');
                return;
            }
            
            // Show loading state
            if (analyzeButton) {
                analyzeButton.disabled = true;
                analyzeButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Processing...';
            }
        });
    };

    // Initialize all forms on page
    const forms = document.querySelectorAll('form[id^="uploadForm"]');
    forms.forEach(form => initFileUploadForm(form));
});