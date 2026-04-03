function getCookie(name) {
  var match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
  return match ? match[2] : null;
}

document.addEventListener('DOMContentLoaded', function () {
  var modal = document.getElementById('learningGoalsModal');
  var form = document.getElementById('learningGoalsModalForm');
  var skipBtn = document.getElementById('modalSkipButton');

  if (!modal || !form) return;

  fetch('/users/preferences/', { credentials: 'same-origin' })
    .then(function (r) {
      return r.json();
    })
    .then(function (data) {
      if (!data.ok) return;
      if (data.has_preferences) return;
      modal.classList.remove('hidden');
    })
    .catch(function () {
      // Modal breaks
    });

  if (skipBtn) {
    skipBtn.addEventListener('click', function () {
      modal.classList.add('hidden');
    });
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var msgEl = document.getElementById('modalGoalsMessage');
    if (!msgEl) return;

    var target = document.getElementById('modalDailyLessons');
    var enabled = document.getElementById('modalReminderEnabled');
    var freq = document.getElementById('modalReminderFrequency');
    var time = document.getElementById('modalReminderTime');

    var payload = {
      daily_lessons_target: parseInt(target && target.value ? target.value : 1, 10),
      reminder_enabled: enabled ? enabled.checked : true,
      reminder_frequency: freq ? freq.value : 'weekly',
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC',
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
          msgEl.textContent = 'Goals saved';
          msgEl.style.color = '';
          modal.classList.add('hidden');
        } else {
          msgEl.textContent = data.error || 'Something went wrong';
          msgEl.style.color = 'var(--secondary-accent-foreground, #B45309)';
        }
      })
      .catch(function () {
        msgEl.textContent = 'Something went wrong';
        msgEl.style.color = 'var(--secondary-accent-foreground, #B45309)';
      });
  });
});
