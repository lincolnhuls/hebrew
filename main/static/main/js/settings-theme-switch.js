(function () {
  var switchEl = document.getElementById('themeSwitch');
  var root = document.documentElement;
  function applyTheme(isLight) {
    if (isLight) root.classList.add('theme-light');
    else root.classList.remove('theme-light');
    try {
      localStorage.setItem('theme', isLight ? 'light' : 'dark');
    } catch (e) {}
  }
  function init() {
    var saved = localStorage.getItem('theme');
    var isLight = saved === 'light';
    switchEl.checked = isLight;
    applyTheme(isLight);
  }
  if (switchEl) {
    init();
    switchEl.addEventListener('change', function () {
      applyTheme(switchEl.checked);
    });
  }
})();
