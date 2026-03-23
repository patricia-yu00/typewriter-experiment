# Firefly Orbs — Design Document

## Overview
When the user seals a letter into the jar, each character of typed text transforms into a glowing orb that flies from the typewriter paper into the jar and floats inside like a firefly.

---

## Orb Appearance
- Each letter in the sealed text = one orb `<div>`
- Style: soft radial-gradient (white center → random color midtone → transparent edge)
- No hard border — luminous blob aesthetic matching the reference image
- Random size: 14–20px per orb
- Random color drawn from palette: rose, lavender, sky blue, mint, amber, peach

## Flight Animation
- On seal: each orb spawns at the paper area position (absolute coords)
- Flies to a random landing spot inside the jar bounds
- Staggered: 50ms delay between each orb
- Path: slight arc via CSS `@keyframes` on `translate`
- Duration: ~600ms per orb, `ease-in` curve

## Firefly Motion (inside jar)
- On landing, each orb enters a `requestAnimationFrame` float loop
- Random slow velocity: 0.3–0.8px per frame
- Bounces off inner jar bounds (computed from jar image position/size)
- Opacity pulses 0.6→1.0→0.6 on a sine wave (slow, ~2–3s cycle) = glow breathing

## Persistence
- Orb data (color, size) stored in `localStorage`
- On page load, orbs are re-created and immediately enter float loop (no flight animation on reload)

## Architecture
- Single `index.html` — all logic inline, no dependencies
- Orb elements appended to a `#orbContainer` div positioned over the jar image
- Jar bounds computed dynamically from `jar img` `getBoundingClientRect()`
- Flight uses CSS class + keyframe injection; float loop uses JS only
