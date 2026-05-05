/**
 * Phone Number Validation and Filtering
 * Ensures only digits are entered in phone input fields
 */

document.addEventListener('DOMContentLoaded', function() {
    // Get all phone input fields
    const phoneInputs = document.querySelectorAll('.phone-input');
    
    phoneInputs.forEach(function(input) {
        // Add input event listener for real-time filtering
        input.addEventListener('input', function(e) {
            // Remove all non-digit characters
            let value = e.target.value.replace(/\D/g, '');
            
            // Enforce maximum length
            if (value.length > 15) {
                value = value.substring(0, 15);
            }
            
            // Update the input value
            e.target.value = value;
            
            // Add visual feedback
            validatePhoneInput(e.target);
        });
        
        // Add paste event listener to handle clipboard content
        input.addEventListener('paste', function(e) {
            e.preventDefault();
            
            // Get pasted data
            const pastedData = (e.clipboardData || window.clipboardData).getData('text');
            
            // Filter to digits only
            const filteredData = pastedData.replace(/\D/g, '').substring(0, 15);
            
            // Insert filtered data
            document.execCommand('insertText', false, filteredData);
            
            // Validate after paste
            validatePhoneInput(e.target);
        });
        
        // Add blur event listener for final validation
        input.addEventListener('blur', function(e) {
            validatePhoneInput(e.target);
        });
        
        // Initial validation
        validatePhoneInput(input);
    });
    
    /**
     * Validate phone input and provide visual feedback
     */
    function validatePhoneInput(input) {
        const value = input.value.trim();
        const isValid = value.length >= 10 && value.length <= 15 && /^\d+$/.test(value);
        
        // Remove existing validation classes
        input.classList.remove('is-valid', 'is-invalid');
        
        // Add appropriate validation class
        if (value.length > 0) {
            if (isValid) {
                input.classList.add('is-valid');
                input.style.borderColor = '#28a745'; // Green
            } else {
                input.classList.add('is-invalid');
                input.style.borderColor = '#dc3545'; // Red
                
                // Show error message
                showPhoneError(input, 'Phone number must contain 10-15 digits only');
            }
        } else {
            input.style.borderColor = ''; // Default
            hidePhoneError(input);
        }
        
        return isValid;
    }
    
    /**
     * Show phone validation error message
     */
    function showPhoneError(input, message) {
        hidePhoneError(input); // Remove existing error
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'phone-error-message';
        errorDiv.style.cssText = `
            color: #dc3545;
            font-size: 0.875rem;
            margin-top: 0.25rem;
            display: block;
        `;
        errorDiv.textContent = message;
        
        // Insert error message after the input
        input.parentNode.insertBefore(errorDiv, input.nextSibling);
    }
    
    /**
     * Hide phone validation error message
     */
    function hidePhoneError(input) {
        const existingError = input.parentNode.querySelector('.phone-error-message');
        if (existingError) {
            existingError.remove();
        }
    }
    
    /**
     * Form validation helper
     * Call this before form submission to validate all phone inputs
     */
    window.validatePhoneInputs = function() {
        let allValid = true;
        const phoneInputs = document.querySelectorAll('.phone-input');
        
        phoneInputs.forEach(function(input) {
            if (!validatePhoneInput(input)) {
                allValid = false;
            }
        });
        
        return allValid;
    };
    
    /**
     * Get clean phone number
     * Returns digits only or null if invalid
     */
    window.getCleanPhoneNumber = function(input) {
        const value = input.value.trim();
        const digits = value.replace(/\D/g, '');
        
        if (digits.length >= 10 && digits.length <= 15) {
            return digits;
        }
        
        return null;
    };
});
