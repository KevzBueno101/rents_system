// Login password toggle
function toggleLoginPassword() {
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
}

// Signup password toggle
function toggleSignupPassword() {
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
}

// Role toggle
window.selectRole = function(role) {
  document.getElementById("roleInput").value = role;
  const btnAdmin = document.getElementById("btnAdmin");
  const btnTenant = document.getElementById("btnTenant");
  const signupSection = document.getElementById("signupSection");

  if (role === "admin") {
    btnAdmin.className = "btn btn-dark role-btn";
    btnTenant.className = "btn btn-outline-dark role-btn";
    signupSection.classList.add("d-none");
  } else {
    btnTenant.className = "btn btn-dark role-btn";
    btnAdmin.className = "btn btn-outline-dark role-btn";
    signupSection.classList.remove("d-none");
  }
}

// Signup room selection JavaScript
document.addEventListener('DOMContentLoaded', function() {
  const signupRoomSelect = document.getElementById('signupRoomSelect');
  const signupRoomDetails = document.getElementById('signupRoomDetails');

  if (signupRoomSelect) {
    const signupRoomRate = document.getElementById('signupRoomRate');
    const signupRoomCapacity = document.getElementById('signupRoomCapacity');
    const signupRoomFloor = document.getElementById('signupRoomFloor');
    const signupRoomAvailable = document.getElementById('signupRoomAvailable');
    const signupRoomBedType = document.getElementById('signupRoomBedType');
    const signupInclusionsSection = document.getElementById('signupInclusionsSection');
    const signupInclusionsList = document.getElementById('signupInclusionsList');

    signupRoomSelect.addEventListener('change', function() {
      const selectedOption = this.options[this.selectedIndex];

      if (this.value === '') {
        signupRoomDetails.classList.add('d-none');
        return;
      }

      signupRoomRate.textContent = `PHP ${parseFloat(selectedOption.dataset.rate).toFixed(0)}/month`;
      signupRoomCapacity.textContent = selectedOption.dataset.capacity;
      signupRoomFloor.textContent = selectedOption.dataset.floor;
      const available = parseInt(selectedOption.dataset.capacity) - parseInt(selectedOption.dataset.occupied);
      signupRoomAvailable.textContent = `${available} bed${available !== 1 ? 's' : ''}`;

      const bedType = selectedOption.dataset.bedType;
      let bedTypeText = bedType.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
      signupRoomBedType.textContent = bedTypeText;

      signupInclusionsList.innerHTML = '';

      const inclusions = [];
      if (selectedOption.dataset.water === 'Yes') inclusions.push('Water');
      if (selectedOption.dataset.electricity === 'Yes') inclusions.push('Electricity');
      if (selectedOption.dataset.wifi === 'Yes') inclusions.push('WiFi');

      try {
        const dynamicInclusions = JSON.parse(selectedOption.dataset.dynamicInclusions || '[]');
        dynamicInclusions.forEach(inc => inclusions.push(inc.name));
      } catch (e) {
        console.log('Error parsing dynamic inclusions:', e);
      }

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

      signupRoomDetails.classList.remove('d-none');
    });
  }
});

// Profile modal functions
window.openProfileModal = function () {
  new bootstrap.Modal(document.getElementById('profileModal')).show();
};

window.toggleProfilePassword = function () {
  const currentPass = document.getElementById('currentPassword');
  const newPass = document.getElementById('newPassword');
  const confirmPass = document.getElementById('confirmPassword');
  const icon = document.getElementById('profileEyeIcon');

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
};

window.previewProfilePhoto = function (event) {
  const file = event.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = function (e) {
      const preview = document.getElementById('profilePreview');
      preview.src = e.target.result;
    };
    reader.readAsDataURL(file);
  }
};