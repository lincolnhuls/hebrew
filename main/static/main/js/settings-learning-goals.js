function getCookie(name) {
  var match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
  return match ? match[2] : null;
}

document.addEventListener('DOMContentLoaded', function () {
  var form = document.getElementById('learningGoalsForm');
  if (!form) return;

  if (form.dataset.goalsSubmitAttached === 'true') return;
  form.dataset.goalsSubmitAttached = 'true';

  fetch('/users/preferences/', { credentials: 'same-origin' })
    .then(function (r) {
      return r.json();
    })
    .then(function (data) {
      if (!data.ok || !data.has_preferences || !data.preferences) return;
      var p = data.preferences;

      var target = document.getElementById('dailyLessonsTarget');
      if (target) target.value = p.daily_lessons_target;

      var enabled = document.getElementById('reminderEnabled');
      if (enabled) enabled.checked = p.reminder_enabled;

      var freq = document.getElementById('reminderFrequency');
      if (freq) freq.value = p.reminder_frequency;

      var time = document.getElementById('reminderTime');
      if (time && p.reminder_time) {
        time.value = p.reminder_time.substring(0, 5);
      }

      var tz = document.getElementById('timezone');
      if (tz) tz.value = p.timezone || 'UTC';
    })
    .catch(function () {});

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var msgEl = document.getElementById('goalsMessage');
    if (!msgEl) return;

    var submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn && submitBtn.disabled) return;
    if (submitBtn) submitBtn.disabled = true;

    var target = document.getElementById('dailyLessonsTarget');
    var enabled = document.getElementById('reminderEnabled');
    var freq = document.getElementById('reminderFrequency');
    var time = document.getElementById('reminderTime');
    var tz = document.getElementById('timezone');

    var payload = {
      daily_lessons_target: parseInt(target && target.value ? target.value : 1, 10),
      reminder_enabled: enabled ? enabled.checked : true,
      reminder_frequency: freq ? freq.value : 'weekly',
      timezone: tz ? tz.value : 'UTC',
    };
    if (time && time.value) {
      payload.reminder_time = time.value;
    }

    fetch('/users/preferences/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'),
      },
      credentials: 'same-origin',
      body: JSON.stringify(payload),
    })
      .then(function (r) {
        return r.json();
      })
      .then(function (data) {
        if (data.ok) {
          msgEl.textContent = 'Goals Saved';
          msgEl.style.color = '';
        } else {
          msgEl.textContent = data.error || 'Something Went Wrong';
          msgEl.style.color = 'var(--secondary-accent-foreground, #B45309)';
        }
      })
      .catch(function () {
        msgEl.textContent = 'Something went wrong.';
        msgEl.style.color = 'var(--secondary-accent-foreground, #B45309)';
      })
      .finally(function () {
        if (submitBtn) submitBtn.disabled = false;
      });
  });
});
