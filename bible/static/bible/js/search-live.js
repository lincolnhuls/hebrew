(function () {
  var form = document.querySelector('.search-form');
  var input = form && form.querySelector('input[name="q"]');
  var container = document.getElementById('search-results-outer');
  if (!form || !input || !container) return;

  var debounceMs = 320;
  var debounceTimer = null;

  function updateResults() {
    var q = input.value.trim();
    var url = form.action + (form.action.indexOf('?') !== -1 ? '&' : '?') + 'q=' + encodeURIComponent(q);
    fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
      .then(function (r) {
        return r.text();
      })
      .then(function (html) {
        var parser = new DOMParser();
        var doc = parser.parseFromString(html, 'text/html');
        var outer = doc.getElementById('search-results-outer');
        container.innerHTML = outer ? outer.innerHTML : '';
      })
      .catch(function () {
        container.innerHTML = '<p class="search-note">Search unavailable.</p>';
      });
  }

  input.addEventListener('input', function () {
    if (debounceTimer) clearTimeout(debounceTimer);
    if (input.value.trim() === '') {
      container.innerHTML = '';
      return;
    }
    debounceTimer = setTimeout(updateResults, debounceMs);
  });

  input.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') {
      e.preventDefault();
      if (input.value.trim()) updateResults();
    }
  });
})();
