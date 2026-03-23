# Jar Zoom View — Design Document

## Overview
Clicking the jar transitions to an immersive full-screen view of the jar interior (top-down perspective). Orbs float inside the circular opening. Clicking an orb reveals the letter text overlaid above it — orb stays visible beneath. A back arrow exits to the typewriter.

---

## Transition In
- Click jar → full-screen overlay fades + scales in (`opacity 0→1`, `scale 0.95→1`, ~400ms ease-out)
- Background: black (`#000`)
- `perspective1.png` centered, large (fills most of the screen, circular crop feel)
- z-index: 200 (above everything)
- Small `←` back arrow top-left to exit

## Jar Interior / Orbs
- Float zone = circular region inside the jar opening in `perspective1.png`
- Orbs re-rendered from existing letter data (color, size per letter)
- Same rAF glow/float loop, new bounds based on the circle
- Orbs slightly larger in this view (20–30px)
- Each orb carries its letter index so clicking it knows which letter to show

## Letter Reveal
- Click orb → letter text fades in centered on the orb's position
- Orb stays visible and glowing beneath the text
- Text: Special Elite font, white, date small above, letter content below
- No modal border — text floats in the dark interior
- Click anywhere outside the text → text fades out, orb resumes floating

## Exit
- `←` back arrow or ESC → overlay fades out (~300ms), returns to typewriter view

## Architecture
- Single `index.html` — all inline
- New `#jarView` overlay div with `perspective1.png` background
- New `#jarViewOrbContainer` for the scaled-up orbs (separate from the small jar's `#orbContainer`)
- New `#letterReveal` div for the floating letter text
- Separate float loop instance for the jar view (same `tickFloat` logic, different bounds + array)
- Letter data loaded from `getLetters()` matched by index to orb order
