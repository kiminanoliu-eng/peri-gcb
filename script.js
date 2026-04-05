// Language switching functionality
function switchLanguage(lang) {
  // Update all elements with data-* attributes
  document.querySelectorAll('[data-zh]').forEach(el => {
    const text = el.getAttribute('data-' + lang);
    if (text) {
      el.textContent = text;
    }
  });

  // Save preference
  localStorage.setItem('preferredLanguage', lang);
}

// Load saved language preference on page load
document.addEventListener('DOMContentLoaded', function() {
  const savedLang = localStorage.getItem('preferredLanguage');
  if (savedLang) {
    document.getElementById('lang-switcher').value = savedLang;
    switchLanguage(savedLang);
  }
});

// Form submission handler
document.addEventListener('DOMContentLoaded', function() {
  const form = document.getElementById('comment-form');
  if (form) {
    form.addEventListener('submit', function(e) {
      // Web3Forms will handle the submission
      // Show a simple confirmation
      setTimeout(function() {
        alert('留言已提交！Thank you for your message!');
      }, 100);
    });
  }
});
