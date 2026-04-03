(function () {
  var btn = document.getElementById('reviewRetakeBtn');
  if (!btn) return;
  function getCookie(name) {
    var m = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    return m ? m[2] : null;
  }
  btn.addEventListener('click', function () {
    var el = this;
    el.disabled = true;
    var url = el.getAttribute('data-start-review-url');
    var userId = el.getAttribute('data-user-id');
    var lessonSlug = el.getAttribute('data-lesson-slug');
    var runnerUrl = el.getAttribute('data-lesson-runner-url');
    fetch(url, {
      method: 'POST',
      credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') || '' },
      body: JSON.stringify({ user_id: userId, lesson_slug: lessonSlug }),
    })
      .then(function (r) {
        return r.json();
      })
      .then(function (data) {
        if (data.session_id) {
          window.location.href = runnerUrl + (runnerUrl.indexOf('?') !== -1 ? '&' : '?') + 'session_id=' + data.session_id;
        } else {
          alert(data.error || 'Could not start review quiz.');
          el.disabled = false;
        }
      })
      .catch(function () {
        alert('Network error. Please try again.');
        el.disabled = false;
      });
  });
})();
