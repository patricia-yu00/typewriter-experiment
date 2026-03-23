# Magical Jar Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** The jar stores all memories forever but surfaces 10 random ones at a time; orbs slow on hover and show a letter preview; each open letter has a delete ("forget") button.

**Architecture:** All changes in `index.html`. Three feature areas: (1) `openJarView` selects 10 random letter indices from the full pool on each open; (2) the `tickJarView` loop handles hover detection, velocity damping, and tooltip positioning; (3) `showLetterReveal` stores the current letter index so a "forget" button can delete it and re-sync in-memory floater indices.

**Tech Stack:** Vanilla JS, CSS transitions, localStorage.

---

### Task 1: Magic jar — random 10 selection, "memories" count, sealed-away flash

**Files:**
- Modify: `index.html` — `openJarView()`, `updateJarUI()`, seal button handler, HTML, CSS

**Context:**
Currently `openJarView` shows ALL stored orbs. It should instead pick up to 10 random ones from the full pool on each open. `updateJarUI` shows "N letters" — change to "N memories". After sealing, a brief "sealed away" message should appear below the typewriter.

---

**Step 1: Update `openJarView` to pick 10 random orbs**

Find the top of `openJarView`:
```js
    function openJarView() {
      const orbData  = getOrbs();
      if (!orbData.length) return;
```

Replace with:
```js
    function openJarView() {
      const letters  = getLetters();
      const orbData  = getOrbs();
      if (!letters.length) return;

      // Pick up to 10 random indices from the full pool
      const allIndices = letters.map((_, i) => i);
      for (let i = allIndices.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [allIndices[i], allIndices[j]] = [allIndices[j], allIndices[i]];
      }
      const selectedIndices = allIndices.slice(0, 10);
```

Then find the inner `orbData.forEach((o, i) => {` loop (inside the double rAF):
```js
          orbData.forEach((o, i) => {
            const size  = Math.round(randBetween(24, 38));
            const angle = Math.random() * Math.PI * 2;
            const dist  = Math.random() * (r - size);
            const x = cx - size/2 + Math.cos(angle) * dist;
            const y = cy - size/2 + Math.sin(angle) * dist;
            const speed = randBetween(0.4, 1.0);
            const vAngle = Math.random() * Math.PI * 2;

            const el = createOrbElement(o.color, size);
            el.classList.add('jar-view-orb');
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
```

Replace with (iterate `selectedIndices`, use real `letterIndex`, fall back to random color/size if orb data missing):
```js
          selectedIndices.forEach(letterIndex => {
            const o     = orbData[letterIndex] || { color: ORB_PALETTE[Math.floor(Math.random()*ORB_PALETTE.length)], size: 18 };
            const size  = Math.round(randBetween(24, 38));
            const angle = Math.random() * Math.PI * 2;
            const dist  = Math.random() * (r - size);
            const x = cx - size/2 + Math.cos(angle) * dist;
            const y = cy - size/2 + Math.sin(angle) * dist;
            const speed = randBetween(0.4, 1.0);
            const vAngle = Math.random() * Math.PI * 2;

            const el = createOrbElement(o.color, size);
            el.classList.add('jar-view-orb');
            el.style.opacity = '0';
            el.style.transform = `translate(${x}px, ${y}px)`;
            el.dataset.letterIndex = letterIndex;
            orbCon.appendChild(el);

            jarViewFloaters.push({
              el, x, y,
              vx: Math.cos(vAngle) * speed,
              vy: Math.sin(vAngle) * speed,
              phase: Math.random() * Math.PI * 2,
              size,
              letterIndex,
              maxSpeed: speed,
            });
          });
```

---

**Step 2: Update `updateJarUI` — "memories" label**

Find:
```js
        jarCount.textContent = letters.length === 1 ? '1 letter' : `${letters.length} letters`;
```

Replace with:
```js
        jarCount.textContent = letters.length === 1 ? '1 memory' : `${letters.length} memories`;
```

---

**Step 3: Add "sealed away" flash HTML + CSS**

Find this HTML:
```html
  <button id="sealBtn" class="seal-btn">✦ Seal &amp; Store ✦</button>
```

Replace with:
```html
  <button id="sealBtn" class="seal-btn">✦ Seal &amp; Store ✦</button>
  <div id="sealFlash" class="seal-flash">sealed away</div>
```

Add CSS after `.seal-btn:hover { ... }`:
```css
    .seal-flash {
      font-family: 'Special Elite', monospace;
      font-size: clamp(10px, 1.1vw, 13px);
      color: rgba(100, 60, 20, 0.45);
      letter-spacing: 0.22em;
      text-align: center;
      opacity: 0;
      transition: opacity 0.6s ease;
      pointer-events: none;
    }
    .seal-flash.visible { opacity: 1; }
```

---

**Step 4: Trigger flash in the seal button handler**

Find the end of `sealBtn.addEventListener('click', ...)`, just before the closing `});`:
```js
      // Show jar, persist orbs, clear bounds cache, launch flight
      _cachedBounds = null;
      updateJarUI(newOrbData);
      launchOrbsToJar(text, newOrbData);
    });
```

Replace with:
```js
      // Show jar, persist orbs, clear bounds cache, launch flight
      _cachedBounds = null;
      updateJarUI(newOrbData);
      launchOrbsToJar(text, newOrbData);

      // Sealed-away flash
      const flash = document.getElementById('sealFlash');
      flash.classList.add('visible');
      setTimeout(() => flash.classList.remove('visible'), 2200);
    });
```

---

**Step 5: Sync and verify**
```bash
cp "/Users/patriciay/Desktop/Personal projects/typewriter-project-2/index.html" /private/tmp/typewriter-serve/index.html
```
- Reload, type something, seal → "sealed away" should fade in below the button then out
- Click jar → should show at most 10 orbs even if many letters stored
- Jar label should read "N memories"
- Open jar multiple times → different orbs should appear each time (due to random shuffle)

---

### Task 2: Delete ("forget") button on the paper letter reveal

**Files:**
- Modify: `index.html` — `showLetterReveal()`, `#letterPaper` HTML, CSS, forget button click handler

**Context:**
When a user opens a letter, they should be able to delete it permanently. The button removes the letter and orb from localStorage by index, removes the orb element from the current jar view, re-indexes remaining floater `letterIndex` values, and closes the paper.

---

**Step 1: Add module-level variable to track current revealed letter index**

Find this line (just before `showLetterReveal`):
```js
    let _textVisibleTimer = null;
```

Add after it:
```js
    let _revealingLetterIdx = null;
```

---

**Step 2: Update `showLetterReveal` to accept and store index**

Find the function signature and its call site in the orb click handler:
```js
    function showLetterReveal(letter) {
```

Replace with:
```js
    function showLetterReveal(letter, idx) {
      _revealingLetterIdx = idx;
```

Then find the orb click handler that calls it:
```js
      showLetterReveal(letter);
```

Replace with:
```js
      showLetterReveal(letter, idx);
```

---

**Step 3: Add "forget" button HTML inside `#letterPaper`**

Find:
```html
  <div id="letterReveal">
    <div id="letterPaper">
      <div id="letterRevealDate"></div>
      <div id="letterRevealText"></div>
    </div>
  </div>
```

Replace with:
```html
  <div id="letterReveal">
    <div id="letterPaper">
      <div id="letterRevealDate"></div>
      <div id="letterRevealText"></div>
      <button id="forgetBtn" class="forget-btn">forget</button>
    </div>
  </div>
```

---

**Step 4: Add CSS for the forget button**

Add after `#letterRevealDate::after { ... }`:
```css
    .forget-btn {
      display: block;
      margin-top: 22px;
      background: transparent;
      border: none;
      font-family: 'Special Elite', monospace;
      font-size: clamp(9px, 0.9vw, 11px);
      color: rgba(100, 60, 20, 0.35);
      letter-spacing: 0.18em;
      cursor: pointer;
      padding: 0;
      transition: color 0.2s;
    }
    .forget-btn:hover { color: rgba(160, 40, 20, 0.7); }
```

---

**Step 5: Add forget button click handler**

Add after the `#letterReveal` backdrop click listener:
```js
    document.getElementById('forgetBtn').addEventListener('click', () => {
      const idx = _revealingLetterIdx;
      if (idx === null) return;

      // Remove from storage
      const letters = getLetters();
      const orbs    = getOrbs();
      letters.splice(idx, 1);
      orbs.splice(idx, 1);
      saveLetters(letters);
      saveOrbs(orbs);

      // Remove orb element from jar view + re-index floaters
      const floaterIdx = jarViewFloaters.findIndex(f => f.letterIndex === idx);
      if (floaterIdx >= 0) {
        jarViewFloaters[floaterIdx].el.remove();
        jarViewFloaters.splice(floaterIdx, 1);
      }
      // Decrement letterIndex for all floaters that pointed past the deleted one
      jarViewFloaters.forEach(f => {
        if (f.letterIndex > idx) {
          f.letterIndex--;
          f.el.dataset.letterIndex = f.letterIndex;
        }
      });

      _revealingLetterIdx = null;
      updateJarUI();
      hideLetterReveal();

      // If jar is now empty, close jar view
      if (!getLetters().length) closeJarView();
    });
```

---

**Step 6: Sync and verify**
```bash
cp "/Users/patriciay/Desktop/Personal projects/typewriter-project-2/index.html" /private/tmp/typewriter-serve/index.html
```
- Open jar → click orb → paper unfurls with "forget" button at bottom
- Click forget → paper closes, orb disappears from view, count decrements
- Remaining orbs still open the correct letters

---

### Task 3: Hover to slow orbs + tooltip letter preview

**Files:**
- Modify: `index.html` — `tickJarView()`, `openJarView()`, `closeJarView()`, HTML tooltip element, CSS

**Context:**
Mouse position is tracked relative to `#jarViewOrbContainer`. Each frame, `tickJarView` finds which floater (if any) is within cursor range, damps its velocity, and positions a tooltip with the letter's first 40 characters above the orb. Velocity recovers smoothly when the cursor moves away.

---

**Step 1: Add module-level state for hover tracking**

Find:
```js
    const jarViewFloaters = []; // { el, x, y, vx, vy, phase, size, letterIndex }
    let jarViewRafId = null;
```

Replace with:
```js
    const jarViewFloaters = []; // { el, x, y, vx, vy, phase, size, letterIndex, maxSpeed }
    let jarViewRafId = null;
    let _jarMouseX = -9999, _jarMouseY = -9999;
    let _jarContainerRect = null;
    let _jarViewLetters   = [];    // cached letters for tooltip, set on open, cleared on close
```

---

**Step 2: Cache container rect and letters on open; clear on close**

In `openJarView`, inside the double rAF block, after `startJarViewLoop()`:
```js
          startJarViewLoop();
          _jarContainerRect = orbCon.getBoundingClientRect();
          _jarViewLetters   = getLetters();
```

In `closeJarView`, add after `stopJarViewLoop()`:
```js
      _jarContainerRect = null;
      _jarViewLetters   = [];
      _jarMouseX = -9999; _jarMouseY = -9999;
      const tt = document.getElementById('orbTooltip');
      if (tt) tt.classList.remove('visible');
```

---

**Step 3: Wire mouse tracking on the orb container**

Add after the `#jarBackBtn` click listener:
```js
    document.getElementById('jarViewOrbContainer').addEventListener('mousemove', e => {
      if (!_jarContainerRect) return;
      _jarMouseX = e.clientX - _jarContainerRect.left;
      _jarMouseY = e.clientY - _jarContainerRect.top;
    });
    document.getElementById('jarViewOrbContainer').addEventListener('mouseleave', () => {
      _jarMouseX = -9999; _jarMouseY = -9999;
    });
```

---

**Step 4: Add tooltip HTML**

Find:
```html
  <button id="jarBackBtn">←</button>
```

Replace with:
```html
  <button id="jarBackBtn">←</button>
  <div id="orbTooltip"></div>
```

---

**Step 5: Add tooltip CSS**

Add after `#jarBackBtn.open { ... }`:
```css
    #orbTooltip {
      position: fixed;
      z-index: 215;
      font-family: 'Special Elite', monospace;
      font-size: clamp(10px, 1.1vw, 13px);
      color: rgba(255, 255, 255, 0.88);
      background: rgba(0, 0, 0, 0.62);
      border: 1px solid rgba(255,255,255,0.12);
      padding: 4px 10px;
      pointer-events: none;
      opacity: 0;
      transition: opacity 0.18s ease;
      max-width: 220px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      transform: translateX(-50%);
    }
    #orbTooltip.visible { opacity: 1; }
```

---

**Step 6: Update `tickJarView` to handle hover damping + tooltip**

Find the full `tickJarView` function:
```js
    function tickJarView() {
      if (jarViewFloaters.length === 0) { jarViewRafId = null; return; }
      const { cx, cy, r } = getJarViewBounds();
      jarViewFloaters.forEach(o => {
        o.x += o.vx; o.y += o.vy;
        const dx = o.x + o.size/2 - cx, dy = o.y + o.size/2 - cy;
        const dist = Math.sqrt(dx*dx + dy*dy);
        if (dist + o.size/2 > r) {
          const nx = dx/dist, ny = dy/dist;
          const dot = o.vx*nx + o.vy*ny;
          o.vx -= 2*dot*nx; o.vy -= 2*dot*ny;
          const overlap = dist + o.size/2 - r;
          o.x -= nx*overlap; o.y -= ny*overlap;
        }
        o.phase += 0.012;
        o.el.style.transform = `translate(${o.x}px, ${o.y}px)`;
        const opacity = 0.65 + 0.35 * Math.sin(o.phase);
        o.el.style.opacity = opacity;
      });
      jarViewRafId = requestAnimationFrame(tickJarView);
    }
```

Replace with:
```js
    function tickJarView() {
      if (jarViewFloaters.length === 0) { jarViewRafId = null; return; }
      const { cx, cy, r } = getJarViewBounds();

      // Find which floater (if any) the cursor is over
      let hoveredIdx = -1;
      jarViewFloaters.forEach((o, i) => {
        const dx = _jarMouseX - (o.x + o.size / 2);
        const dy = _jarMouseY - (o.y + o.size / 2);
        if (Math.sqrt(dx * dx + dy * dy) < o.size / 2 + 10) hoveredIdx = i;
      });

      jarViewFloaters.forEach((o, i) => {
        // Velocity damping / recovery
        const spd = Math.sqrt(o.vx * o.vx + o.vy * o.vy);
        if (i === hoveredIdx) {
          o.vx *= 0.88; o.vy *= 0.88;   // slow toward stop
        } else if (spd < o.maxSpeed * 0.92) {
          const scale = Math.min(1.1, o.maxSpeed / Math.max(spd, 0.01));
          o.vx *= scale; o.vy *= scale;
          // Re-clamp to maxSpeed
          const s2 = Math.sqrt(o.vx * o.vx + o.vy * o.vy);
          if (s2 > o.maxSpeed) { o.vx *= o.maxSpeed / s2; o.vy *= o.maxSpeed / s2; }
        }

        o.x += o.vx; o.y += o.vy;
        const dx = o.x + o.size/2 - cx, dy = o.y + o.size/2 - cy;
        const dist = Math.sqrt(dx*dx + dy*dy);
        if (dist + o.size/2 > r) {
          const nx = dx/dist, ny = dy/dist;
          const dot = o.vx*nx + o.vy*ny;
          o.vx -= 2*dot*nx; o.vy -= 2*dot*ny;
          const overlap = dist + o.size/2 - r;
          o.x -= nx*overlap; o.y -= ny*overlap;
        }
        o.phase += 0.012;
        o.el.style.transform = `translate(${o.x}px, ${o.y}px)`;
        o.el.style.opacity = 0.65 + 0.35 * Math.sin(o.phase);
      });

      // Update tooltip
      const tooltip = document.getElementById('orbTooltip');
      if (tooltip && _jarContainerRect) {
        if (hoveredIdx >= 0) {
          const o = jarViewFloaters[hoveredIdx];
          const letter = _jarViewLetters[o.letterIndex];
          if (letter) {
            const preview = letter.text.slice(0, 42) + (letter.text.length > 42 ? '…' : '');
            tooltip.textContent = preview;
            tooltip.classList.add('visible');
            tooltip.style.left = (_jarContainerRect.left + o.x + o.size / 2) + 'px';
            tooltip.style.top  = (_jarContainerRect.top  + o.y - 34) + 'px';
          }
        } else {
          tooltip.classList.remove('visible');
        }
      }

      jarViewRafId = requestAnimationFrame(tickJarView);
    }
```

---

**Step 7: Sync and verify**
```bash
cp "/Users/patriciay/Desktop/Personal projects/typewriter-project-2/index.html" /private/tmp/typewriter-serve/index.html
```
- Open jar → hover over an orb → it slows to near-still, tooltip appears above with first line of letter
- Move cursor away → orb speeds back up, tooltip disappears
- Tooltip does not flicker (no rapid show/hide)
- Tooltip doesn't appear outside the jar view when it's closed
