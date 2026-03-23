# Jar Storage Feature Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** After typing a note on the typewriter, the user can click "Seal & Store" to save it to a jar archive, clearing the typewriter; clicking the jar later shows all stored letters.

**Architecture:** All state lives in `localStorage` under the key `jarLetters` as a JSON array of `{ text, date }` objects. The jar image and button are appended below the `.scene` div and toggled via CSS classes. No external dependencies — single `index.html` file.

**Tech Stack:** Vanilla HTML/CSS/JS, localStorage, Special Elite font (already loaded), jar.png image.

---

### Task 1: Add jar.png and "Seal & Store" button HTML

**Files:**
- Modify: `index.html` — add jar section below `.scene`

**Step 1: Add the HTML structure after the closing `</div>` of `.scene`**

```html
<!-- Jar section -->
<div id="jarSection" class="jar-section">
  <button id="sealBtn" class="seal-btn">✦ Seal &amp; Store ✦</button>
  <div id="jarWrap" class="jar-wrap hidden">
    <img src="jar.png" alt="jar" id="jarImg" />
    <span class="jar-count" id="jarCount"></span>
  </div>
</div>

<!-- Letters overlay -->
<div id="lettersOverlay" class="letters-overlay hidden">
  <div class="letters-modal">
    <button class="close-btn" id="closeOverlay">✕</button>
    <h2 class="letters-title">Letters in the Jar</h2>
    <div id="lettersList" class="letters-list"></div>
  </div>
</div>
```

**Step 2: Verify in browser**
Open `http://localhost:<port>` — the button should appear below the typewriter. Jar is hidden for now.

---

### Task 2: Style the jar section (CSS)

**Files:**
- Modify: `index.html` — add CSS rules inside `<style>`

**Step 1: Add these CSS rules**

```css
/* ── JAR SECTION ─────────────────────────────────── */
.jar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 28px;
  gap: 16px;
}

.seal-btn {
  display: none; /* shown via JS when text exists */
  font-family: 'Special Elite', monospace;
  font-size: clamp(11px, 1.4vw, 15px);
  color: #f0e6d3;
  background: transparent;
  border: 1px solid #a08060;
  padding: 8px 22px;
  cursor: pointer;
  letter-spacing: 0.12em;
  transition: background 0.2s, color 0.2s;
}
.seal-btn:hover {
  background: #a08060;
  color: #1a0e06;
}

.jar-wrap {
  position: relative;
  width: min(160px, 30vw);
  cursor: pointer;
  transition: transform 0.15s;
}
.jar-wrap:hover { transform: scale(1.04); }
.jar-wrap img { width: 100%; display: block; }

.jar-count {
  position: absolute;
  bottom: 18%;
  left: 50%;
  transform: translateX(-50%);
  font-family: 'Special Elite', monospace;
  font-size: clamp(9px, 1.2vw, 13px);
  color: #f0e6d3;
  pointer-events: none;
}

.hidden { display: none !important; }

/* ── LETTERS OVERLAY ──────────────────────────────── */
.letters-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.82);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.letters-modal {
  background: #0d0d0d;
  border: 1px solid #5a4030;
  padding: 32px;
  width: min(520px, 90vw);
  max-height: 75vh;
  overflow-y: auto;
  position: relative;
}

.letters-title {
  font-family: 'Special Elite', monospace;
  color: #d4b896;
  font-size: clamp(14px, 2vw, 20px);
  margin: 0 0 20px;
  text-align: center;
  letter-spacing: 0.1em;
}

.close-btn {
  position: absolute;
  top: 12px; right: 16px;
  background: transparent;
  border: none;
  color: #a08060;
  font-size: 18px;
  cursor: pointer;
}
.close-btn:hover { color: #f0e6d3; }

.letters-list { display: flex; flex-direction: column; gap: 20px; }

.letter-entry {
  border-top: 1px solid #3a2a1a;
  padding-top: 14px;
}
.letter-date {
  font-family: 'Special Elite', monospace;
  font-size: clamp(9px, 1vw, 11px);
  color: #7a6040;
  margin-bottom: 6px;
  letter-spacing: 0.08em;
}
.letter-text {
  font-family: 'Special Elite', monospace;
  font-size: clamp(10px, 1.3vw, 14px);
  color: #d4c4a8;
  white-space: pre-wrap;
  line-height: 1.6;
}
```

**Step 2: Verify in browser**
Reload — button should be hidden (display:none), jar hidden. No visual change yet.

---

### Task 3: Wire up JavaScript logic

**Files:**
- Modify: `index.html` — add JS inside `<script>` at the bottom (before closing `</script>`)

**Step 1: Add jar logic JS**

```js
// ── JAR STORAGE ───────────────────────────────────
const sealBtn      = document.getElementById('sealBtn');
const jarWrap      = document.getElementById('jarWrap');
const jarCount     = document.getElementById('jarCount');
const lettersOverlay = document.getElementById('lettersOverlay');
const lettersList  = document.getElementById('lettersList');
const closeOverlay = document.getElementById('closeOverlay');

function getLetters() {
  return JSON.parse(localStorage.getItem('jarLetters') || '[]');
}
function saveLetters(arr) {
  localStorage.setItem('jarLetters', JSON.stringify(arr));
}

function updateJarUI() {
  const letters = getLetters();
  if (letters.length > 0) {
    jarWrap.classList.remove('hidden');
    jarCount.textContent = letters.length === 1 ? '1 letter' : `${letters.length} letters`;
  }
}

function updateSealBtn() {
  const hasText = lines.join('').trim().length > 0;
  sealBtn.style.display = hasText ? 'inline-block' : 'none';
}

// Seal & Store
sealBtn.addEventListener('click', () => {
  const text = lines.join('\n').trim();
  if (!text) return;
  const letters = getLetters();
  letters.unshift({
    text,
    date: new Date().toLocaleDateString('en-US', { year:'numeric', month:'long', day:'numeric', hour:'2-digit', minute:'2-digit' })
  });
  saveLetters(letters);
  // Clear typewriter
  lines = [''];
  lineIndex = 0;
  carriageX = 0;
  document.querySelector('.carriage-wrap').style.transform = 'translateX(0px)';
  updateDisplay();
  updateSealBtn();
  updateJarUI();
});

// Open jar
jarWrap.addEventListener('click', () => {
  const letters = getLetters();
  lettersList.innerHTML = '';
  letters.forEach(l => {
    const entry = document.createElement('div');
    entry.className = 'letter-entry';
    entry.innerHTML = `<div class="letter-date">${l.date}</div><div class="letter-text">${l.text.replace(/</g,'&lt;')}</div>`;
    lettersList.appendChild(entry);
  });
  lettersOverlay.classList.remove('hidden');
});

// Close overlay
closeOverlay.addEventListener('click', () => lettersOverlay.classList.add('hidden'));
lettersOverlay.addEventListener('click', e => {
  if (e.target === lettersOverlay) lettersOverlay.classList.add('hidden');
});

// Hook into typeChar / backspace to show/hide seal button
// Wrap existing updateDisplay to also call updateSealBtn
const _origUpdateDisplay = updateDisplay;
updateDisplay = function() { _origUpdateDisplay(); updateSealBtn(); };

// Init on load
updateJarUI();
```

**Step 2: Verify in browser — full flow**
1. Type some text → "Seal & Store" button should appear
2. Click "Seal & Store" → text clears, jar appears below with "1 letter"
3. Type more text → seal again → jar shows "2 letters"
4. Click jar → overlay opens showing both letters with dates
5. Click ✕ or outside modal → overlay closes
6. Refresh page → jar still shows (persisted in localStorage)

---

### Task 4: Sync to preview server and do final check

**Step 1: Copy to preview server**
```bash
cp "/Users/patriciay/Desktop/Personal projects/typewriter-project-2/index.html" /private/tmp/typewriter-serve/index.html
```

**Step 2: Screenshot the final result**
Take a preview screenshot to confirm layout looks correct end-to-end.
