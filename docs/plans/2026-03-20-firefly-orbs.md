# Firefly Orbs Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** When a letter is sealed into the jar, each character transforms into a glowing colored orb that flies from the typewriter paper to the jar and floats inside like a firefly.

**Architecture:** All logic lives in `index.html`. Orbs are absolutely-positioned `<div>`s with radial-gradient glow. Flight uses CSS keyframe animations injected per-orb; idle float uses a shared `requestAnimationFrame` loop with per-orb velocity/phase state. Orb data persists in `localStorage` and is restored on page load.

**Tech Stack:** Vanilla HTML/CSS/JS, Web Animations API (none), `requestAnimationFrame`, `localStorage`, CSS radial-gradient.

---

### Task 1: Add orb CSS styles and `#orbContainer`

**Files:**
- Modify: `index.html` — add CSS block inside `<style>` and add `#orbContainer` div inside `#jarWrap`

**Step 1: Add CSS for `.orb` inside the `<style>` block, just before the closing `</style>` tag**

```css
/* ── FIREFLY ORBS ─────────────────────────────── */
#orbContainer {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
  border-radius: 4px;
}

.orb {
  position: absolute;
  border-radius: 50%;
  pointer-events: none;
  will-change: transform, opacity;
}
```

**Step 2: Add `#orbContainer` inside `#jarWrap` in the HTML, after `<img src="jar.png" ...>`**

```html
<div id="orbContainer"></div>
```

**Step 3: Verify manually**
Open the preview. The jar should render exactly as before — `#orbContainer` is invisible until orbs are added.

---

### Task 2: Orb factory function

**Files:**
- Modify: `index.html` — add JS constants and `createOrbElement()` function inside `<script>`, after the `updateJarUI` function

**Step 1: Add the color palette and factory function**

```js
// ── FIREFLY ORB SYSTEM ─────────────────────────
const ORB_PALETTE = [
  ['#ffe0f0','#e060a0'],  // rose
  ['#e8e0ff','#9060e0'],  // lavender
  ['#d0eeff','#4090d0'],  // sky blue
  ['#d0ffe8','#40c080'],  // mint
  ['#fff3c0','#d0a020'],  // amber
  ['#ffe8d0','#e08040'],  // peach
];

function randBetween(a, b) { return a + Math.random() * (b - a); }

function createOrbElement(color, size) {
  const [light, mid] = color;
  const el = document.createElement('div');
  el.className = 'orb';
  el.style.width  = size + 'px';
  el.style.height = size + 'px';
  el.style.background = `radial-gradient(circle at 38% 35%, #fff 0%, ${light} 30%, ${mid} 65%, transparent 100%)`;
  el.style.filter = `blur(0.5px) drop-shadow(0 0 ${Math.round(size * 0.4)}px ${mid}88)`;
  return el;
}
```

**Step 2: Verify manually**
In browser console run:
```js
const el = createOrbElement(ORB_PALETTE[0], 16);
el.style.position = 'fixed';
el.style.top = '50px'; el.style.left = '50px';
document.body.appendChild(el);
```
Expected: a soft rose-pink glowing circle appears at top-left.

---

### Task 3: Orb float loop

**Files:**
- Modify: `index.html` — add float state array and `startFloatLoop()` function after the orb factory

**Step 1: Add the float state and rAF loop**

```js
const orbFloaters = []; // { el, x, y, vx, vy, phase, size }
let floatRafId = null;

function getJarInnerBounds() {
  const jarImg = document.getElementById('jarImg');
  const container = document.getElementById('orbContainer');
  const jarR = jarImg.getBoundingClientRect();
  const conR = container.getBoundingClientRect();
  // Inset ~15% from jar edges to keep orbs inside the glass
  const ix = jarR.width  * 0.15;
  const iy = jarR.height * 0.18;
  return {
    left:   ix - (conR.left - jarR.left),
    top:    iy - (conR.top  - jarR.top),
    right:  jarR.width  - ix - (conR.left - jarR.left),
    bottom: jarR.height - iy - (conR.top  - jarR.top),
  };
}

function tickFloat(ts) {
  const bounds = getJarInnerBounds();
  orbFloaters.forEach(o => {
    o.x += o.vx;
    o.y += o.vy;
    // Bounce off bounds
    if (o.x <= bounds.left)                   { o.x = bounds.left;                  o.vx =  Math.abs(o.vx); }
    if (o.x + o.size >= bounds.right)         { o.x = bounds.right  - o.size;       o.vx = -Math.abs(o.vx); }
    if (o.y <= bounds.top)                    { o.y = bounds.top;                   o.vy =  Math.abs(o.vy); }
    if (o.y + o.size >= bounds.bottom)        { o.y = bounds.bottom - o.size;       o.vy = -Math.abs(o.vy); }
    // Opacity pulse
    o.phase += 0.012;
    const opacity = 0.6 + 0.4 * Math.sin(o.phase);
    o.el.style.transform = `translate(${o.x}px, ${o.y}px)`;
    o.el.style.opacity = opacity;
  });
  floatRafId = requestAnimationFrame(tickFloat);
}

function startFloatLoop() {
  if (floatRafId) return; // already running
  floatRafId = requestAnimationFrame(tickFloat);
}
```

**Step 2: Verify mentally** — function is declared but not called yet, no visible effect.

---

### Task 4: Flight animation from paper to jar

**Files:**
- Modify: `index.html` — add `launchOrbsToJar(text)` function after `startFloatLoop`

**Step 1: Add the flight launcher**

```js
function launchOrbsToJar(text) {
  const chars = text.replace(/\s/g, '').split(''); // skip whitespace orbs
  if (!chars.length) return;

  const paperArea  = document.querySelector('.paper-area');
  const orbCon     = document.getElementById('orbContainer');
  const paperR     = paperArea.getBoundingClientRect();
  const conR       = orbCon.getBoundingClientRect();

  // Source: center of paper area (in viewport coords)
  const srcX = paperR.left + paperR.width  / 2;
  const srcY = paperR.top  + paperR.height / 2;

  // Destination: center of orbContainer (in viewport coords)
  const dstX = conR.left + conR.width  / 2;
  const dstY = conR.top  + conR.height / 2;

  chars.forEach((ch, i) => {
    setTimeout(() => {
      const color  = ORB_PALETTE[Math.floor(Math.random() * ORB_PALETTE.length)];
      const size   = Math.round(randBetween(10, 18));

      // Create a flying orb fixed to viewport
      const flier = createOrbElement(color, size);
      flier.style.position = 'fixed';
      flier.style.left = (srcX - size / 2) + 'px';
      flier.style.top  = (srcY - size / 2) + 'px';
      flier.style.transition = 'none';
      flier.style.opacity = '0';
      document.body.appendChild(flier);

      // Arc flight via Web Animations
      const midX = (srcX + dstX) / 2 + randBetween(-40, 40);
      const midY = Math.min(srcY, dstY) - randBetween(30, 80);

      flier.animate([
        { transform: `translate(0,0)`,                                         opacity: 0,   offset: 0    },
        { transform: `translate(${midX-srcX}px, ${midY-srcY}px)`,             opacity: 0.9, offset: 0.45 },
        { transform: `translate(${dstX-srcX}px, ${dstY-srcY}px)`,             opacity: 1,   offset: 1    },
      ], { duration: 600, easing: 'ease-in', fill: 'forwards' })
        .finished.then(() => {
          flier.remove();

          // Land inside jar as a floater
          const bounds = getJarInnerBounds();
          const landX  = randBetween(bounds.left,  bounds.right  - size);
          const landY  = randBetween(bounds.top,   bounds.bottom - size);
          const speed  = randBetween(0.3, 0.8);
          const angle  = Math.random() * Math.PI * 2;

          const resident = createOrbElement(color, size);
          resident.style.opacity = '0';
          resident.style.transform = `translate(${landX}px, ${landY}px)`;
          orbCon.appendChild(resident);

          orbFloaters.push({
            el: resident,
            x: landX, y: landY,
            vx: Math.cos(angle) * speed,
            vy: Math.sin(angle) * speed,
            phase: Math.random() * Math.PI * 2,
            size,
            color,
          });

          startFloatLoop();
        });
    }, i * 50);
  });
}
```

**Step 2: Verify mentally** — function declared, not wired up yet.

---

### Task 5: Persistence — save and restore orbs

**Files:**
- Modify: `index.html` — update `saveLetters` / `getLetters` and add `saveOrbs` / `loadOrbs`; wire into `updateJarUI`

**Step 1: Add orb save/load functions after the `saveLetters` function**

```js
function getOrbs() {
  try { return JSON.parse(localStorage.getItem('jarOrbs') || '[]'); } catch { return []; }
}
function saveOrbs(arr) {
  try { localStorage.setItem('jarOrbs', JSON.stringify(arr)); } catch {}
}
```

**Step 2: Update `updateJarUI` to restore persisted orbs on page load**

Replace the existing `updateJarUI` function:

```js
function updateJarUI(newOrbs) {
  const letters = getLetters();
  if (letters.length > 0) {
    jarWrap.classList.remove('hidden');
    jarCount.textContent = letters.length === 1 ? '1 letter' : `${letters.length} letters`;
  } else {
    jarWrap.classList.add('hidden');
  }

  if (newOrbs) {
    // Accumulate and persist
    const existing = getOrbs();
    const merged = existing.concat(newOrbs);
    saveOrbs(merged);
    restoreOrbs(merged);
  }
}

function restoreOrbs(orbData) {
  const orbCon = document.getElementById('orbContainer');
  // Clear any existing orb elements
  orbCon.innerHTML = '';
  orbFloaters.length = 0;
  if (floatRafId) { cancelAnimationFrame(floatRafId); floatRafId = null; }
  if (!orbData.length) return;

  orbData.forEach(o => {
    const bounds = getJarInnerBounds();
    const size   = o.size || 14;
    const x      = randBetween(bounds.left, bounds.right  - size);
    const y      = randBetween(bounds.top,  bounds.bottom - size);
    const speed  = randBetween(0.3, 0.8);
    const angle  = Math.random() * Math.PI * 2;
    const el     = createOrbElement(o.color, size);
    el.style.opacity   = '0';
    el.style.transform = `translate(${x}px, ${y}px)`;
    orbCon.appendChild(el);
    orbFloaters.push({
      el, x, y,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed,
      phase: Math.random() * Math.PI * 2,
      size, color: o.color,
    });
  });
  startFloatLoop();
}
```

**Step 3: Verify mentally** — `updateJarUI` now accepts optional `newOrbs` array; existing call `updateJarUI()` still works (no-arg path).

---

### Task 6: Wire seal button to orb launch

**Files:**
- Modify: `index.html` — update the `sealBtn` click handler

**Step 1: Replace the existing `sealBtn.addEventListener('click', ...)` block**

```js
sealBtn.addEventListener('click', () => {
  const text = lines.join('\n').trim();
  if (!text) return;

  // Save letter
  const letters = getLetters();
  letters.unshift({
    text,
    date: new Date().toLocaleString('en-US', { year:'numeric', month:'long', day:'numeric', hour:'2-digit', minute:'2-digit' })
  });
  saveLetters(letters);

  // Build orb metadata for each non-whitespace char
  const chars = text.replace(/\s/g, '').split('');
  const newOrbData = chars.map(() => ({
    color: ORB_PALETTE[Math.floor(Math.random() * ORB_PALETTE.length)],
    size:  Math.round(randBetween(10, 18)),
  }));

  // Clear typewriter
  lines = [''];
  lineIndex = 0;
  carriageX = 0;
  carriage.style.transform = 'translateX(0px)';
  updateDisplay();
  updateSealBtn();
  started = false;
  hint.classList.remove('fade');

  // Show jar immediately, then launch orbs
  updateJarUI(newOrbData);
  launchOrbsToJar(text);
});
```

**Step 2: Verify manually**
1. Type a few characters (e.g. "hello")
2. Click "Seal & Store"
3. Expected: orbs fly from the paper area to the jar corner, then float inside the jar with soft glow
4. Refresh the page — orbs should reappear in the jar immediately (no flight on reload)

---

### Task 7: Init on load — restore orbs

**Files:**
- Modify: `index.html` — update the bottom `updateJarUI()` init call

**Step 1: Replace `updateJarUI();` at the bottom of the script with:**

```js
// Init
updateJarUI();
restoreOrbs(getOrbs());
```

**Step 2: Verify manually**
1. Seal a letter, refresh the page
2. Expected: orbs reappear floating in the jar immediately without flight animation
