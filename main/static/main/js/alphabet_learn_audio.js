function setPlaying(btn, isPlaying) {
  if (!btn) return;
  btn.classList.toggle("is-playing", Boolean(isPlaying));
}

const audio = new Audio();
audio.preload = "none";

let currentBtn = null;
let queuedSoundUrl = null;

async function playUrl(url) {
  audio.pause();
  audio.currentTime = 0;
  audio.src = url;
  // Some browsers return a promise from play(); catch to prevent uncaught rejections.
  const p = audio.play();
  if (p && typeof p.then === "function") {
    await p;
  }
}

audio.addEventListener("ended", async () => {
  if (!queuedSoundUrl) {
    if (currentBtn) setPlaying(currentBtn, false);
    currentBtn = null;
    return;
  }
  const next = queuedSoundUrl;
  queuedSoundUrl = null;
  try {
    await playUrl(next);
  } catch (e) {
    console.warn("Audio play failed:", e);
    if (currentBtn) setPlaying(currentBtn, false);
    currentBtn = null;
  }
});

function attach() {
  const buttons = document.querySelectorAll("[data-audio-name],[data-audio-sound]");
  buttons.forEach((btn) => {
    btn.addEventListener("click", async () => {
      const nameUrl = btn.getAttribute("data-audio-name") || "";
      const soundUrl = btn.getAttribute("data-audio-sound") || "";

      // Stop any current playback.
      if (currentBtn && currentBtn !== btn) setPlaying(currentBtn, false);
      currentBtn = btn;
      setPlaying(btn, true);
      queuedSoundUrl = null;

      try {
        if (nameUrl) {
          // Play name first, then sound (if provided).
          queuedSoundUrl = soundUrl || null;
          await playUrl(nameUrl);
          return;
        }
        if (soundUrl) {
          await playUrl(soundUrl);
          queuedSoundUrl = null;
          return;
        }
        setPlaying(btn, false);
      } catch (e) {
        // Common when the file doesn't exist yet (404) or autoplay is blocked.
        console.warn("Audio play failed:", e);
        setPlaying(btn, false);
      }
    });
  });
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", attach);
} else {
  attach();
}

