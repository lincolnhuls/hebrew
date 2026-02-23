/**
 * Lesson Runner – loads lesson via resume/start API, renders questions (mc, fill, match), handles submit.
 */

// Feedback display timeout (milliseconds)
const FEEDBACK_DISPLAY_TIMEOUT = 800;

const cfg = window.LESSON_RUNNER_CONFIG || {};
if (!cfg.resumeUrl || !cfg.userId || !cfg.lessonSlug) {
  console.error("LESSON_RUNNER_CONFIG missing required fields");
}

// Import shared utilities
import { getCookie } from "./utils.js";

function shuffle(arr) {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

const loadingSection = document.getElementById("loadingSection");
const errorSection = document.getElementById("errorSection");
const errorMsg = document.getElementById("errorMsg");
const questionSection = document.getElementById("questionSection");
const completedSection = document.getElementById("completedSection");
const feedbackSection = document.getElementById("feedbackSection");
const feedbackMsg = document.getElementById("feedbackMsg");
const progressFill = document.getElementById("progressFill");
const progressPct = document.getElementById("progressPct");
const currentIdx = document.getElementById("currentIdx");
const totalQuestions = document.getElementById("totalQuestions");
const questionPrompt = document.getElementById("questionPrompt");
const hebrewBox = document.getElementById("hebrewBox");
const hebrewText = document.getElementById("hebrewText");
const mcChoices = document.getElementById("mcChoices");
const fillSection = document.getElementById("fillSection");
const fillInput = document.getElementById("fillInput");
const matchSection = document.getElementById("matchSection");
const matchPairs = document.getElementById("matchPairs");
const submitBtn = document.getElementById("submitBtn");
const tipText = document.getElementById("tipText");
const startOverBtn = document.getElementById("startOverBtn");
const completedScore = document.getElementById("completedScore");
const completedResult = document.getElementById("completedResult");
const restartBtn = document.getElementById("restartBtn");

let state = {
  sessionId: null,
  currentIndex: 0,
  totalQuestions: 0,
  question: null,
  selectedChoice: null,
  matchSelections: {},
};

function hideAll() {
  loadingSection?.classList.add("hidden");
  errorSection?.classList.add("hidden");
  questionSection?.classList.add("hidden");
  completedSection?.classList.add("hidden");
  feedbackSection?.classList.add("hidden");
}

function showLoading() {
  hideAll();
  loadingSection?.classList.remove("hidden");
}

function showError(msg) {
  hideAll();
  errorMsg.textContent = msg || "Something went wrong.";
  errorSection?.classList.remove("hidden");
}

function showQuestion(q, idx, total) {
  hideAll();
  questionSection?.classList.remove("hidden");
  state.question = q;
  state.currentIndex = idx;
  state.totalQuestions = total;
  state.selectedChoice = null;
  state.matchSelections = {};

  const pct = total ? Math.round((idx / total) * 100) : 0;
  if (progressFill) progressFill.style.width = `${pct}%`;
  if (progressPct) progressPct.textContent = `${pct}%`;
  if (currentIdx) currentIdx.textContent = String(idx + 1);
  if (totalQuestions) totalQuestions.textContent = String(total);

  if (questionPrompt) questionPrompt.textContent = q.prompt || "";

  hebrewBox?.classList.add("hidden");
  mcChoices?.classList.add("hidden");
  fillSection?.classList.add("hidden");
  matchSection?.classList.add("hidden");
  submitBtn.disabled = true;

  if (q.type === "mc") {
    mcChoices?.classList.remove("hidden");
    mcChoices.innerHTML = "";
    const choices = shuffle(q.choices || []);
    choices.forEach((letter) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "lesson-runner-choice hebrew-rtl";
      btn.textContent = letter;
      btn.dataset.choice = letter;
      btn.addEventListener("click", () => {
        document.querySelectorAll(".lesson-runner-choice").forEach((b) => b.classList.remove("selected"));
        btn.classList.add("selected");
        state.selectedChoice = letter;
        submitBtn.disabled = false;
      });
      mcChoices.appendChild(btn);
    });
    if (tipText) tipText.textContent = "Select one answer.";
  } else if (q.type === "fill") {
    hebrewBox?.classList.remove("hidden");
    fillSection?.classList.remove("hidden");
    if (hebrewText) hebrewText.textContent = q.shown || "";
    if (fillInput) {
      fillInput.value = "";
      fillInput.placeholder = "Type your answer…";
      fillInput.addEventListener("input", () => {
        submitBtn.disabled = !fillInput.value.trim();
      });
      fillInput.focus();
    }
    if (tipText) tipText.textContent = "Type the name of the letter.";
  } else if (q.type === "match") {
    matchSection?.classList.remove("hidden");
    matchPairs.innerHTML = "";
    const pairs = q.pairs || [];
    const normLetter = (l) => (typeof l === "string" ? l.normalize("NFC") : l);
    const names = shuffle(
      pairs.map((p) => p.right).filter((r) => r != null && String(r).trim() !== "")
    );
    pairs.forEach((p, i) => {
      const letterKey = normLetter(p.left);
      const hasDagesh = /\u05bc/.test((p.left || "").normalize("NFC"));
      const row = document.createElement("div");
      row.className = "lesson-runner-match-row";
      const left = document.createElement("div");
      left.className = "lesson-runner-match-left hebrew-rtl";
      left.textContent = p.left;
      const selId = `match-select-${i}`;
      const lbl = document.createElement("label");
      lbl.htmlFor = selId;
      lbl.className = "lesson-runner-match-label";
      lbl.textContent = hasDagesh
        ? `Select name for letter ${p.left} (with dagesh)`
        : `Select name for letter ${p.left}`;
      const sel = document.createElement("select");
      sel.id = selId;
      sel.className = "lesson-runner-match-right";
      sel.dataset.left = letterKey;
      const optPlaceholder = document.createElement("option");
      optPlaceholder.value = "";
      optPlaceholder.textContent = "Choose…";
      sel.appendChild(optPlaceholder);
      shuffle([...names]).forEach((n) => {
        const opt = document.createElement("option");
        opt.value = n;
        opt.textContent = n;
        sel.appendChild(opt);
      });
      sel.addEventListener("change", () => {
        state.matchSelections[letterKey] = sel.value;
        const allSet = pairs.every((x) => state.matchSelections[normLetter(x.left)]);
        submitBtn.disabled = !allSet;
      });
      row.appendChild(left);
      row.appendChild(lbl);
      row.appendChild(sel);
      matchPairs.appendChild(row);
    });
    if (tipText) tipText.textContent = "Match each letter to its name.";
  }

  startOverBtn?.classList.remove("hidden");
}

function showCompleted(data) {
  hideAll();
  completedSection?.classList.remove("hidden");
  const score = data.score_correct ?? 0;
  const total = data.total_questions ?? 0;
  const passed = data.passed ?? false;
  if (progressFill) progressFill.style.width = `100%`;
  if (progressPct) progressPct.textContent = `100%`;
  if (completedScore) completedScore.textContent = `Score: ${score} / ${total}`;
  if (completedResult) completedResult.textContent = passed ? "You passed! Great job." : "Keep practicing! Complete the lesson again.";
}

function showFeedback(correct) {
  feedbackMsg.textContent = correct ? "Correct! ✓" : "Incorrect";
  feedbackSection.classList.remove("hidden");
  feedbackMsg.style.color = correct ? "var(--success, green)" : "var(--error, #dc2626)";
}

function hideFeedback() {
  feedbackSection.classList.add("hidden");
}

function buildUserAnswer() {
  const q = state.question;
  if (!q) return null;
  if (q.type === "mc") return { choice: state.selectedChoice };
  if (q.type === "fill") return { answer: fillInput?.value?.trim() ?? "" };
  if (q.type === "match") {
    const normLetter = (l) => (typeof l === "string" ? l.normalize("NFC") : l);
    const pairs = (q.pairs || []).map((p) => {
      const letterKey = normLetter(p.left);
      return { left: letterKey, right: state.matchSelections[letterKey] ?? "" };
    });
    return { pairs };
  }
  return null;
}

async function resume() {
  showLoading();
  try {
    const url = `${cfg.resumeUrl}?user_id=${encodeURIComponent(cfg.userId)}&lesson_slug=${encodeURIComponent(cfg.lessonSlug)}`;
    const res = await fetch(url, { credentials: "same-origin" });
    const data = await res.json();
    if (!res.ok) {
      showError(data.error || "Failed to load lesson.");
      return;
    }
    state.sessionId = data.session_id;
    if (data.completed) {
      showCompleted(data);
    } else {
      showQuestion(data.question, data.question_index, data.total_questions);
    }
  } catch (err) {
    console.error(err);
    showError("Network error. Please try again.");
  }
}

async function startFresh() {
  showLoading();
  try {
    const url = cfg.startUrl;
    const csrf = getCookie("csrftoken");
    const res = await fetch(url, {
      method: "POST",
      credentials: "same-origin",
      headers: {
        "Content-Type": "application/json",
        ...(csrf ? { "X-CSRFToken": csrf } : {}),
      },
      body: JSON.stringify({
        user_id: cfg.userId,
        lesson_slug: cfg.lessonSlug,
      }),
    });
    const data = await res.json();
    if (!res.ok) {
      showError(data.error || "Failed to start lesson.");
      return;
    }
    state.sessionId = data.session_id;
    showQuestion(data.question, data.question_index, data.total_questions);
  } catch (err) {
    console.error(err);
    showError("Network error. Please try again.");
  }
}

async function submitAnswer() {
  const userAnswer = buildUserAnswer();
  if (userAnswer === null) return;
  submitBtn.disabled = true;

  try {
    const submitUrl = cfg.submitUrlTemplate.replace("{session_id}", state.sessionId);
    const csrf = getCookie("csrftoken");
    const res = await fetch(submitUrl, {
      method: "POST",
      credentials: "same-origin",
      headers: {
        "Content-Type": "application/json",
        ...(csrf ? { "X-CSRFToken": csrf } : {}),
      },
      body: JSON.stringify({
        question_index: state.currentIndex,
        user_answer: userAnswer,
      }),
    });
    const data = await res.json();
    if (!res.ok) {
      showError(data.error || "Failed to submit.");
      return;
    }
    if (!data.correct && data.match_debug) {
      console.warn("Match marked incorrect. Debug:", data.match_debug);
    }
    showFeedback(data.correct);
    setTimeout(() => {
      hideFeedback();
      if (data.completed) {
        showCompleted(data);
      } else {
        showQuestion(data.next_question, data.next_question_index, state.totalQuestions);
      }
    }, FEEDBACK_DISPLAY_TIMEOUT);
  } catch (err) {
    console.error(err);
    showError("Network error. Please try again.");
  }
}

if (cfg.lessonError) {
  showError(cfg.lessonError);
} else {
  resume();
}

if (submitBtn) submitBtn.addEventListener("click", submitAnswer);
if (fillInput) fillInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    submitAnswer();
  }
});
if (startOverBtn) {
  startOverBtn.classList.remove("hidden");
  startOverBtn.addEventListener("click", startFresh);
}
if (restartBtn) restartBtn.addEventListener("click", startFresh);
