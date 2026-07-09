// Stroke O Clock — site interactions
// Intentionally minimal per the design brief: no flashy animation.

document.addEventListener('DOMContentLoaded', () => {

  // Mobile nav toggle
  const navToggle = document.querySelector('.nav-toggle');
  const navLinks = document.querySelector('.nav-links');
  if (navToggle && navLinks) {
    navToggle.addEventListener('click', () => {
      const isOpen = navLinks.classList.toggle('open');
      navToggle.setAttribute('aria-expanded', String(isOpen));
    });
  }

  // Highlight the current nav link
  const currentPath = window.location.pathname;
  document.querySelectorAll('.nav-links a').forEach((link) => {
    if (link.getAttribute('href') === currentPath) {
      link.classList.add('active');
    }
  });

  // Confirm before destructive admin actions
  document.querySelectorAll('form[data-confirm]').forEach((form) => {
    form.addEventListener('submit', (e) => {
      const message = form.getAttribute('data-confirm');
      if (!window.confirm(message)) {
        e.preventDefault();
      }
    });
  });

  // Lightweight client-side required-field check on the registration form
  // (server still validates everything independently — this is just UX)
  const joinForm = document.querySelector('#registration-form');
  if (joinForm) {
    joinForm.addEventListener('submit', (e) => {
      const required = joinForm.querySelectorAll('[required]');
      let firstInvalid = null;
      required.forEach((field) => {
        if (!field.value || (field.type === 'checkbox' && !field.checked)) {
          field.classList.add('field-invalid');
          if (!firstInvalid) firstInvalid = field;
        } else {
          field.classList.remove('field-invalid');
        }
      });
      if (firstInvalid) {
        e.preventDefault();
        firstInvalid.focus();
      }
    });
  }

  // Auto-dismiss success flash messages after a few seconds
  document.querySelectorAll('.flash-success').forEach((el) => {
    setTimeout(() => {
      el.style.transition = 'opacity 0.4s ease';
      el.style.opacity = '0';
      setTimeout(() => el.remove(), 450);
    }, 5000);
  });
});
