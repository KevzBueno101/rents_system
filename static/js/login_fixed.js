// Login password toggle
function toggleLoginPassword() {
  try {
    const pass = document.getElementById("loginPassword");
    const icon = document.getElementById("loginEyeIcon");
    if (pass && icon) {
      if (pass.type === "password") {
        pass.type = "text";
        icon.classList.replace("bi-eye", "bi-eye-slash");
      } else {
        pass.type = "password";
        icon.classList.replace("bi-eye-slash", "bi-eye");
      }
    }
  } catch (error) {
    console.error('Error in toggleLoginPassword:', error);
  }
}

// Signup password toggle
function toggleSignupPassword() {
  try {
    const pass = document.getElementById("signupPassword");
    const icon = document.getElementById("signupEyeIcon");
    if (pass && icon) {
      if (pass.type === "password") {
        pass.type = "text";
        icon.classList.replace("bi-eye", "bi-eye-slash");
      } else {
        pass.type = "password";
        icon.classList.replace("bi-eye-slash", "bi-eye");
      }
    }
  } catch (error) {
    console.error('Error in toggleSignupPassword:', error);
  }
}

// Role toggle
window.selectRole = function(role) {
  try {
    document.getElementById("roleInput").value = role;
    const btnAdmin = document.getElementById("btnAdmin");
    const btnTenant = document.getElementById("btnTenant");
    const signupSection = document.getElementById("signupSection");

    if (role === "admin") {
      btnAdmin.classList.add("active");
      btnTenant.classList.remove("active");
      signupSection.classList.add("d-none");
    } else {
      btnTenant.classList.add("active");
      btnAdmin.classList.remove("active");
      signupSection.classList.remove("d-none");
    }
  } catch (error) {
    console.error('Error in selectRole:', error);
  }
};

// Signup room selection JavaScript
document.addEventListener('DOMContentLoaded', function() {
  const signupRoomSelect = document.getElementById('signupRoomSelect');
  const signupRoomDetails = document.getElementById('signupRoomDetails');

  if (signupRoomSelect) {
    // Room details elements
    const signupRoomRate = document.getElementById('signupRoomRate');
    const signupRoomCapacity = document.getElementById('signupRoomCapacity');
    const signupRoomFloor = document.getElementById('signupRoomFloor');
    const signupRoomAvailable = document.getElementById('signupRoomAvailable');
    const signupRoomBedType = document.getElementById('signupRoomBedType');
    
    // Section containers
    const signupInclusionsSection = document.getElementById('signupInclusionsSection');
    const signupAppliancesSection = document.getElementById('signupAppliancesSection');
    const signupInclusionsList = document.getElementById('signupInclusionsList');
    const signupAppliancesList = document.getElementById('signupAppliancesList');
    
    signupRoomSelect.addEventListener('change', function() {
      const selectedOption = this.options[this.selectedIndex];
      
      if (this.value === '') {
        signupRoomDetails.classList.add('d-none');
        return;
      }
      
      // Update room details
      signupRoomRate.textContent = `PHP ${parseFloat(selectedOption.dataset.rate).toFixed(0)}/month`;
      signupRoomCapacity.textContent = selectedOption.dataset.capacity;
      signupRoomFloor.textContent = selectedOption.dataset.floor;
      const available = parseInt(selectedOption.dataset.capacity) - parseInt(selectedOption.dataset.occupied);
      signupRoomAvailable.textContent = `${available} bed${available !== 1 ? 's' : ''}`;
      
      // Update bed type
      const bedType = selectedOption.dataset.bedType;
      let bedTypeText = bedType.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
      signupRoomBedType.textContent = bedTypeText;
      
      // Clear existing badges
      signupInclusionsList.innerHTML = '';
      signupAppliancesList.innerHTML = '';
      
      // Collect inclusions that are checked
      const inclusions = [];
      if (selectedOption.dataset.water === 'Yes') {
        inclusions.push('Water');
      }
      if (selectedOption.dataset.electricity === 'Yes') {
        inclusions.push('Electricity');
      }
      
      // Collect appliances that are checked
      const appliances = [];
      if (selectedOption.dataset.fan === 'Yes') {
        appliances.push('Fan');
      }
      if (selectedOption.dataset.aircon === 'Yes') {
        appliances.push('Aircon');
      }
      if (selectedOption.dataset.ref === 'Yes') {
        appliances.push('Refrigerator');
      }
      if (selectedOption.dataset.tv === 'Yes') {
        appliances.push('TV');
      }
      if (selectedOption.dataset.wifi === 'Yes') {
        appliances.push('WiFi');
      }
      
      // Show inclusions section only if there are inclusions
      if (inclusions.length > 0) {
        signupInclusionsSection.style.display = 'block';
        inclusions.forEach(inclusion => {
          const badge = document.createElement('span');
          badge.className = 'badge bg-success text-white';
          badge.textContent = inclusion;
          signupInclusionsList.appendChild(badge);
        });
      } else {
        signupInclusionsSection.style.display = 'none';
      }
      
      // Show appliances section only if there are appliances
      if (appliances.length > 0) {
        signupAppliancesSection.style.display = 'block';
        appliances.forEach(appliance => {
          const badge = document.createElement('span');
          badge.className = 'badge bg-success text-white';
          badge.textContent = appliance;
          signupAppliancesList.appendChild(badge);
        });
      } else {
        signupAppliancesSection.style.display = 'none';
      }
      
      signupRoomDetails.classList.remove('d-none');
    });
  }
});

// Profile modal functions for login page
window.openProfileModal = function () {
  try {
    new bootstrap.Modal(document.getElementById('profileModal')).show();
  } catch (error) {
    console.error('Error in openProfileModal:', error);
  }
};

window.toggleProfilePassword = function () {
  try {
    const currentPass = document.getElementById('currentPassword');
    const newPass = document.getElementById('newPassword');
    const confirmPass = document.getElementById('confirmPassword');
    const icon = document.getElementById('profileEyeIcon');
    
    if (currentPass && newPass && confirmPass && icon) {
      if (currentPass.type === 'password') {
        currentPass.type = 'text';
        newPass.type = 'text';
        confirmPass.type = 'text';
        icon.classList.replace('bi-eye', 'bi-eye-slash');
      } else {
        currentPass.type = 'password';
        newPass.type = 'password';
        confirmPass.type = 'password';
        icon.classList.replace('bi-eye-slash', 'bi-eye');
      }
    }
  } catch (error) {
    console.error('Error in toggleProfilePassword:', error);
  }
};

window.previewProfilePhoto = function (event) {
  try {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = function (e) {
        const preview = document.getElementById('profilePreview');
        preview.src = e.target.result;
      };
      reader.readAsDataURL(file);
    }
  } catch (error) {
    console.error('Error in previewProfilePhoto:', error);
  }
};
