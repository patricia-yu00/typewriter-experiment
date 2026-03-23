# Jar Zoom View Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace the letter-list modal with an immersive full-screen jar interior view where clicking an orb reveals its letter text floating above it.

**Architecture:** A `#jarView` full-screen overlay uses `perspective1.png` as background. A separate `#jarViewOrbContainer` hosts scaled-up orbs driven by a new float loop with circular bounds. Clicking an orb shows `#letterReveal` text positioned above the orb. The old letters modal is removed. All changes are in `index.html`.

**Tech Stack:** Vanilla HTML/CSS/JS, CSS transitions, requestAnimationFrame, existing orb/float infrastructure.

---

### Task 1: Add jar view HTML and CSS

**Files:**
- Modify: `/Users/patriciay/Desktop/Personal projects/typewriter-project-2/index.html`

**Step 1: Add CSS for the jar view overlay, jar view orb container, back button, and letter reveal — paste inside `<style>` just before `</style>`**

```css
/* ── JAR ZOOM VIEW ───────────────────────────────── */
#jarView {
  position: fixed;
  inset: 0;
  background: #000;
  z-index: 200;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transform: scale(0.95);
  transition: opacity 0.4s ease-out, transform 0.4s ease-out;
  pointer-events: none;
}
#jarView.open {
  opacity: 1;
  transform: scale(1);
  pointer-events: all;
}
#jarViewBg {
  position: relative;
  width: min(90vw, 90vh);
  height: min(90vw, 90vh);
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
}
#jarViewBg img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  border-radius: 50%;
}
#jarViewOrbContainer {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  overflow: hidden;
}
.jar-view-orb {
  position: absolute;
  border-radius: 50%;
  cursor: pointer;
  will-change: transform, opacity;
  transition: filter 0.2s;
}
.jar-view-orb:hover {
  filter: brightness(1.4);
}
#jarBackBtn {
  position: fixed;
  top: 24px;
  left: 24px;
  background: transparent;
  border: none;
  color: rgba(255,255,255,0.6);
  font-size: 28px;
  cursor: pointer;
  z-index: 201;
  line-height: 1;
  transition: color 0.2s;
}
#jarBackBtn:hover { color: #fff; }

#letterReveal {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 210;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.3s ease;
}
#letterReveal.visible {
  opacity: 1;
  pointer-events: all;
}
#letterRevealDate {
  font-family: 'Special Elite', monospace;
  font-size: clamp(9px, 1vw, 12px);
  color: rgba(255,255,255,0.45);
  letter-spacing: 0.12em;
  margin-bottom: 10px;
  text-align: center;
}
#letterRevealText {
  font-family: 'Special Elite', monospace;
  font-size: clamp(13px, 1.8vw, 20px);
  color: rgba(255,255,255,0.92);
  white-space: pre-wrap;
  line-height: 1.7;
  text-align: center;
  max-width: min(480px, 80vw);
}
```

**Step 2: Add the HTML for `#jarView` just before the closing `</body>` tag (before the existing `<p class="hint">` line)**

```html
<!-- Jar zoom view -->
<div id="jarView">
  <div id="jarViewBg">
    <img src="perspective1.png" alt="" draggable="false">
    <div id="jarViewOrbContainer"></div>
  </div>
</div>
<button id="jarBackBtn" class="hidden">←</button>
<div id="letterReveal" >
  <div id="letterRevealDate"></div>
  <div id="letterRevealText"></div>
</div>
```

**Step 3: Verify manually**
Open preview — nothing should look different yet. The jar view overlay is invisible (`opacity: 0, pointer-events: none`).

---

### Task 2: Jar view float loop (separate from small jar)

**Files:**
- Modify: `/Users/patriciay/Desktop/Personal projects/typewriter-project-2/index.html` — add JS after `startFloatLoop`

**Step 1: Add jar view state and helpers inside `<script>`, after `startFloatLoop` and before `launchOrbsToJar`**

```js
// ── JAR VIEW ──────────────────────────────────────
const jarViewFloaters = []; // { el, x, y, vx, vy, phase, size, letterIndex }
let jarViewRafId = null;

function getJarViewBounds() {
  const bg = document.getElementById('jarViewBg');
  if (!bg) return { cx: 0, cy: 0, r: 0 };
  const r = bg.getBoundingClientRect();
  const radius = r.width * 0.38; // usable float radius inside the circular opening
  return { cx: r.width / 2, cy: r.height / 2, r: radius };
}

function tickJarView() {
  if (jarViewFloaters.length === 0) { jarViewRafId = null; return; }
  const { cx, cy, r } = getJarViewBounds();
  jarViewFloaters.forEach(o => {
    o.x += o.vx;
    o.y += o.vy;
    // Bounce inside circle: if orb center exits radius, reflect velocity
    const dx = o.x + o.size/2 - cx;
    const dy = o.y + o.size/2 - cy;
    const dist = Math.sqrt(dx*dx + dy*dy);
    if (dist + o.size/2 > r) {
      // Reflect velocity off the circle wall
      const nx = dx / dist;
      const ny = dy / dist;
      const dot = o.vx * nx + o.vy * ny;
      o.vx -= 2 * dot * nx;
      o.vy -= 2 * dot * ny;
      // Push back inside
      const overlap = dist + o.size/2 - r;
      o.x -= nx * overlap;
      o.y -= ny * overlap;
    }
    o.phase += 0.012;
    const opacity = 0.65 + 0.35 * Math.sin(o.phase);
    o.el.style.transform = `translate(${o.x}px, ${o.y}px)`;
    o.el.style.opacity = opacity;
  });
  jarViewRafId = requestAnimationFrame(tickJarView);
}

function startJarViewLoop() {
  if (jarViewRafId) return;
  jarViewRafId = requestAnimationFrame(tickJarView);
}

function stopJarViewLoop() {
  if (jarViewRafId) { cancelAnimationFrame(jarViewRafId); jarViewRafId = null; }
}
```

**Step 2: Verify mentally** — functions declared, loop not started yet.

---

### Task 3: Open jar view — populate orbs and animate in

**Files:**
- Modify: `/Users/patriciay/Desktop/Personal projects/typewriter-project-2/index.html`

**Step 1: Add `openJarView()` function after `stopJarViewLoop`**

```js
function openJarView() {
  const letters  = getLetters();
  const orbData  = getOrbs();
  if (!orbData.length) return;

  const jarView    = document.getElementById('jarView');
  const orbCon     = document.getElementById('jarViewOrbContainer');
  const backBtn    = document.getElementById('jarBackBtn');

  // Clear previous
  orbCon.innerHTML = '';
  jarViewFloaters.length = 0;
  stopJarViewLoop();

  // Show overlay
  jarView.classList.add('open');
  backBtn.classList.remove('hidden');

  // Wait one frame so transition fires, then compute bounds and spawn orbs
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      const { cx, cy, r } = getJarViewBounds();
      orbData.forEach((o, i) => {
        const size  = Math.round(randBetween(24, 38));
        const angle = Math.random() * Math.PI * 2;
        const dist  = Math.random() * (r - size);
        const x = cx - size/2 + Math.cos(angle) * dist;
        const y = cy - size/2 + Math.sin(angle) * dist;
        const speed = randBetween(0.4, 1.0);
        const vAngle = Math.random() * Math.PI * 2;

        const el = createOrbElement(o.color, size);
        el.className += ' jar-view-orb';
        el.style.width  = size + 'px';
        el.style.height = size + 'px';
        el.style.opacity = '0';
        el.style.transform = `translate(${x}px, ${y}px)`;
        el.dataset.letterIndex = i;
        orbCon.appendChild(el);

        jarViewFloaters.push({
          el, x, y,
          vx: Math.cos(vAngle) * speed,
          vy: Math.sin(vAngle) * speed,
          phase: Math.random() * Math.PI * 2,
          size,
          letterIndex: i,
        });
      });

      startJarViewLoop();
    });
  });
}
```

**Step 2: Verify mentally** — `openJarView` declared, not yet wired.

---

### Task 4: Close jar view

**Files:**
- Modify: `/Users/patriciay/Desktop/Personal projects/typewriter-project-2/index.html`

**Step 1: Add `closeJarView()` after `openJarView`**

```js
function closeJarView() {
  const jarView = document.getElementById('jarView');
  const backBtn = document.getElementById('jarBackBtn');
  const reveal  = document.getElementById('letterReveal');

  hideLetterReveal();
  jarView.classList.remove('open');
  backBtn.classList.add('hidden');
  stopJarViewLoop();

  // Clear orbs after transition
  setTimeout(() => {
    document.getElementById('jarViewOrbContainer').innerHTML = '';
    jarViewFloaters.length = 0;
  }, 420);
}

function hideLetterReveal() {
  const reveal = document.getElementById('letterReveal');
  reveal.classList.remove('visible');
}
```

**Step 2: Wire back button and ESC key — add after `closeJarView`**

```js
document.getElementById('jarBackBtn').addEventListener('click', closeJarView);

document.addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    if (!document.getElementById('letterReveal').classList.contains('visible')) {
      closeJarView();
    } else {
      hideLetterReveal();
    }
  }
});
```

**Step 3: Verify mentally** — close path declared, ESC wired.

---

### Task 5: Orb click → letter reveal

**Files:**
- Modify: `/Users/patriciay/Desktop/Personal projects/typewriter-project-2/index.html`

**Step 1: Add orb click handler — add after the ESC listener**

```js
document.getElementById('jarViewOrbContainer').addEventListener('click', e => {
  const orbEl = e.target.closest('.jar-view-orb');
  if (!orbEl) return;

  const idx     = parseInt(orbEl.dataset.letterIndex, 10);
  const letters = getLetters();
  const letter  = letters[idx];
  if (!letter) return;

  const reveal   = document.getElementById('letterReveal');
  const dateEl   = document.getElementById('letterRevealDate');
  const textEl   = document.getElementById('letterRevealText');

  dateEl.textContent = letter.date;
  textEl.textContent = letter.text;
  reveal.classList.add('visible');
});

// Click outside letter text → hide reveal
document.getElementById('letterReveal').addEventListener('click', e => {
  if (e.target === document.getElementById('letterReveal')) {
    hideLetterReveal();
  }
});
```

**Step 2: Verify mentally** — click path declared.

---

### Task 6: Wire jar click to open jar view + remove old modal

**Files:**
- Modify: `/Users/patriciay/Desktop/Personal projects/typewriter-project-2/index.html`

**Step 1: Replace the existing `jarWrap.addEventListener('click', ...)` block (which opens `lettersOverlay`) with:**

```js
// Open jar view
jarWrap.addEventListener('click', openJarView);
```

**Step 2: Remove the old letters overlay HTML** — find and delete this block:
```html
<!-- Letters overlay -->
<div id="lettersOverlay" class="letters-overlay hidden">
  <div class="letters-modal">
    <button class="close-btn" id="closeOverlay">✕</button>
    <h2 class="letters-title">Letters in the Jar</h2>
    <div id="lettersList" class="letters-list"></div>
  </div>
</div>
```

**Step 3: Remove the old JS references** — delete these lines:
- `const lettersOverlay = document.getElementById('lettersOverlay');`
- `const lettersList    = document.getElementById('lettersList');`
- `const closeOverlay   = document.getElementById('closeOverlay');`
- The `closeOverlay.addEventListener(...)` line
- The `lettersOverlay.addEventListener(...)` line

**Step 4: Also remove the old CSS blocks** for `.letters-overlay`, `.letters-modal`, `.letters-title`, `.close-btn`, `.letters-list`, `.letter-entry`, `.letter-date`, `.letter-text`

**Step 5: Sync to preview server**
```bash
cp "/Users/patriciay/Desktop/Personal projects/typewriter-project-2/index.html" /private/tmp/typewriter-serve/index.html
```

**Step 6: Verify manually**
1. Type text, seal it — orb appears in small jar
2. Click jar — full-screen jar interior fades in with `perspective1.png` background
3. Orbs float inside the circular opening
4. Click an orb — letter text appears above it (orb still visible below)
5. Click outside text — text dismisses
6. Click `←` or press ESC — returns to typewriter
