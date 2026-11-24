/* ===================================================================
   SKILL LINK - Interactive Client-side Script
   =================================================================== */

document.addEventListener('DOMContentLoaded', function () {
  // 1. Mobile Navigation Toggle
  const navToggle = document.getElementById('navToggle');
  const navMenu = document.getElementById('navMenu');
  if (navToggle && navMenu) {
    navToggle.addEventListener('click', function () {
      navMenu.classList.toggle('active');
    });
  }

  // 2. Alert Dismissal
  const alertCloseBtns = document.querySelectorAll('.alert-close');
  alertCloseBtns.forEach(function (btn) {
    btn.addEventListener('click', function () {
      const alert = btn.closest('.alert');
      if (alert) {
        alert.style.opacity = '0';
        alert.style.transform = 'translateY(-6px)';
        setTimeout(() => alert.remove(), 200);
      }
    });
  });

  // 3. Home Page Student Portal Option Toggle
  const studentPortalBox = document.getElementById('studentPortalBox');
  const studentActionsPanel = document.getElementById('studentActionsPanel');
  if (studentPortalBox && studentActionsPanel) {
    studentPortalBox.addEventListener('click', function () {
      const isVisible = studentActionsPanel.style.display === 'block';
      studentActionsPanel.style.display = isVisible ? 'none' : 'block';
      if (!isVisible) {
        studentActionsPanel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    });
  }

  // 4. Modal Triggers
  // Any button with data-modal-target="#modalId" opens that modal
  const modalTriggers = document.querySelectorAll('[data-modal-target]');
  modalTriggers.forEach(function (trigger) {
    trigger.addEventListener('click', function (e) {
      e.preventDefault();
      const targetSelector = trigger.getAttribute('data-modal-target');
      const targetModal = document.querySelector(targetSelector);
      if (targetModal) {
        // If data attributes are provided (e.g. receiver_id, receiver_name)
        const receiverId = trigger.getAttribute('data-receiver-id');
        const receiverName = trigger.getAttribute('data-receiver-name');
        const projectId = trigger.getAttribute('data-project-id');
        const projectTitle = trigger.getAttribute('data-project-title');

        if (receiverId) {
          const recIdInput = targetModal.querySelector('#modalReceiverId');
          if (recIdInput) recIdInput.value = receiverId;
        }
        if (receiverName) {
          const recNameSpan = targetModal.querySelector('#modalReceiverName');
          if (recNameSpan) recNameSpan.textContent = receiverName;
        }
        if (projectId) {
          const projIdInput = targetModal.querySelector('#modalProjectId');
          if (projIdInput) projIdInput.value = projectId;
        }
        if (projectTitle) {
          const projTitleSpan = targetModal.querySelector('#modalProjectTitle');
          if (projTitleSpan) projTitleSpan.textContent = projectTitle;
        }

        openModal(targetModal);
      }
    });
  });

  // Modal Close Buttons
  const modalCloseBtns = document.querySelectorAll('.modal-close, [data-modal-close]');
  modalCloseBtns.forEach(function (btn) {
    btn.addEventListener('click', function () {
      const modal = btn.closest('.modal-overlay');
      if (modal) closeModal(modal);
    });
  });

  // Close modal when clicking on overlay background
  const modals = document.querySelectorAll('.modal-overlay');
  modals.forEach(function (modal) {
    modal.addEventListener('click', function (e) {
      if (e.target === modal) {
        closeModal(modal);
      }
    });
  });

  function openModal(modal) {
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  function closeModal(modal) {
    modal.classList.remove('active');
    document.body.style.overflow = '';
  }

  // 5. Tabs Controller (for Requests and Admin views)
  const tabButtons = document.querySelectorAll('.tab-btn');
  tabButtons.forEach(function (btn) {
    btn.addEventListener('click', function () {
      const parentContainer = btn.closest('.tabs-container') || document;
      const targetId = btn.getAttribute('data-tab');

      // Update button active state
      parentContainer.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      // Show target tab pane
      parentContainer.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
      const activePane = parentContainer.querySelector(`#${targetId}`);
      if (activePane) activePane.classList.add('active');
    });
  });

  // 6. Real-time Search Filter for Client Tables/Cards
  const liveSearchInputs = document.querySelectorAll('[data-filter-target]');
  liveSearchInputs.forEach(function (input) {
    input.addEventListener('input', function () {
      const targetSelector = input.getAttribute('data-filter-target');
      const term = input.value.toLowerCase().trim();
      const items = document.querySelectorAll(targetSelector);

      items.forEach(function (item) {
        const text = item.textContent.toLowerCase();
        if (text.includes(term)) {
          item.style.display = '';
        } else {
          item.style.display = 'none';
        }
      });
    });
  });

  // 7. Form validation helper for registration & password confirmation
  const registerForm = document.getElementById('studentRegisterForm');
  if (registerForm) {
    registerForm.addEventListener('submit', function (e) {
      const pass = document.getElementById('password').value;
      const confirmPass = document.getElementById('confirm_password').value;
      if (pass !== confirmPass) {
        e.preventDefault();
        alert('Password and Confirm Password do not match. Please verify.');
      }
    });
  }

  // 8. Admin Event Edit Modal Handler
  const editEventBtns = document.querySelectorAll('.edit-event-btn');
  const editEventModal = document.getElementById('editEventModal');
  const editEventForm = document.getElementById('editEventForm');
  if (editEventBtns.length && editEventModal && editEventForm) {
    editEventBtns.forEach(function (btn) {
      btn.addEventListener('click', function () {
        const id = btn.getAttribute('data-event-id');
        editEventForm.action = '/admin/events/edit/' + id;
        const titleInput = document.getElementById('edit_event_title');
        const typeInput = document.getElementById('edit_event_type');
        const dateInput = document.getElementById('edit_event_date');
        const deadlineInput = document.getElementById('edit_event_deadline');
        const venueInput = document.getElementById('edit_event_venue');
        const descInput = document.getElementById('edit_event_desc');
        const linkInput = document.getElementById('edit_event_link');

        if (titleInput) titleInput.value = btn.getAttribute('data-event-title') || '';
        if (typeInput) typeInput.value = btn.getAttribute('data-event-type') || '';
        if (dateInput) dateInput.value = btn.getAttribute('data-event-date') || '';
        if (deadlineInput) deadlineInput.value = btn.getAttribute('data-event-deadline') || '';
        if (venueInput) venueInput.value = btn.getAttribute('data-event-venue') || '';
        if (descInput) descInput.value = btn.getAttribute('data-event-desc') || '';
        if (linkInput) linkInput.value = btn.getAttribute('data-event-link') || '';

        openModal(editEventModal);
      });
    });
  }
});
