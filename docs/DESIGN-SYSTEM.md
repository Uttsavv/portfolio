# Utsav Singh portfolio: design system

The one system for the site. It is built from the approved mock and checked against the taste skill's `references/system.md`. In code: tokens in `src/styles/tokens.css`, components in `src/styles/global.css`, and a living page at `/design-system/` (not linked, noindex). Use these tokens and components everywhere, and never add a second button, radius, link style or type scale.

## 1. Principles

1. **Readability beats spectacle.** Text never sits on the floor glow or behind a model. A dark shade on the left (desktop) and a bottom scrim (phone) are part of the system, not an extra.
2. **One accent.** Sky blue `#5ab9fc` is only for the primary button, links, focus, small state marks and the one glow in 3D. Everything else is neutral blue-grey.
3. **Highlight with contrast, not colour.** Key facts are white (`--ink`, weight 600). Supporting words are grey (`--muted`). Example: **2+ years experience** · TypeScript, Python / Based in **Delhi, India**.
4. **No filler copy.** Plain labels ("Experience", "Projects", "Get in touch"). No taglines, summaries or cute headings.
5. **Motion is smooth and earned.** Eased, damped, never jumpy. Everything works with reduced motion.

## 2. Colour tokens

Palette: taste-skill "Night and sky blue" (`blue-black-cornflower`). Dark only.

| Token | Value | Use | Contrast on bg |
|---|---|---|---|
| `--bg` | `#0a0d14` | page, renderer clear colour, fog, scrims | — |
| `--surface` | `#131824` | form fields, toasts, panels | — |
| `--ink` | `#e9edf3` | headings, key facts, labels | 16:1 |
| `--ink-2` | `#c3ccda` | reading text: job lines, project descriptions | 11:1 |
| `--muted` | `#8891a1` | meta, dates, secondary words, placeholders | 6:1 |
| `--accent` | `#5ab9fc` | primary button, links, focus ring, Now tag, progress bar | 9:1 |
| `--accent-ink` | `#0a0d14` | text on the accent button | 9:1 |
| `--line` | `rgba(233,237,243,.10)` | hairlines and dividers | — |
| `--field-line` | `rgba(233,237,243,.16)`, hover `.28` | field borders | — |
| `--error` | `#ff9a9a` | field errors | 8:1 |

Never use violet or lavender. Never use pure black or white.

## 3. Type

Font: **Geist** (400, 500, 600, 700), with `system-ui, -apple-system, "SF Pro Display"` as fallback. Use tight tracking on display sizes.

| Role | Size | Weight / line height / tracking | Colour |
|---|---|---|---|
| h1 (name) | `clamp(56px, 8.4vw, 128px)` | 700 / .92 / -.045em | ink; the second line is a gradient from white to the accent |
| Eyebrow (above h1) | `clamp(15px, 1.3vw, 18px)` | 600 / 1.2 | accent, **8px above the h1** |
| Hero sub | `clamp(19px, 1.8vw, 24px)` | 500 / 1.35 / -.015em | muted, with key facts in ink 600 |
| h2 (section) | `clamp(40px, 5.2vw, 72px)` | 700 / 1 / -.04em | ink |
| h3 (project name) | `clamp(36px, 3.8vw, 52px)` | 700 / 1.02 / -.035em | ink |
| h3 (job title) | 17px | 600 / 1.3 | ink |
| Reading text | 16–17px (15.5px on phones) | 400 / 1.5 | ink-2 |
| Meta (dates, stack) | 14px | 500, tabular numbers | muted, or accent for the project stack |
| Label (form) | 14px | 500 | ink |
| Nav links | 15px | 500 | muted, ink when hovered or current |
| Small print (footer) | 13.5px | 400 | muted |

Rules: nothing under 13px, sentence case everywhere, no tracked capitals, and lines at most about 62 characters.

## 4. Spacing, radius, layout

- Spacing scale: 4, 8, 12, 16, 24, 32, 48, 64, 96, 128. Eyebrow to h1 8, h1 to sub 22 (16 on phones), sub to buttons 32, h2 to content 32, field gap 16, label to field 8.
- Radius: fields 12, buttons pill (99px), the tag pill (99px), focus ring 8. No cards with boxes in boxes.
- Container: 1240px max, side gutter 28px (respect the safe area). The text panel is at most 470px wide and sits on the left. The 3D owns the right side.
- Nav: 60px, with the name on the left and Work · Projects · Contact on the right (only Contact under 820px). It becomes solid with a blur and a hairline after the hero.
- Sections are sticky pins, 100svh tall: `#top 150vh`, `#work 230vh`, `#projects 420vh`, `#contact 170vh`.

## 5. Components

- **Primary button** (`.btn`): 48px tall, 24px side padding, pill, accent fill, accent-ink label 15.5px/600. Hover lifts 2px and brightens 1.08. Press goes back to 0 and scales to .98. Only one per view.
- **Text link** (`.more`, `.chip`): accent, 16px/500, a 12px chevron or arrow icon, 44px tap height. Hover underlines (offset 4) and nudges the icon. Use ↗ for external links, ↓ for downloads and › for in-page links.
- **Secondary button** (`.btn2`): 48px tall, pill, a 1px border at 28% ink, ink label 15.5px/600, and an accent icon. Hover lifts 2px, gets an accent border and an 8% accent tint. Used for "Download resume".
- **Icon button** (`.icon-btn`): a 48px circle with a 1px border at 16% ink, a 19px brand glyph in ink-2, and an `aria-label`. Hover gets an accent border, glyph and tint. Used for LinkedIn and GitHub.
- **Contact actions row** (`.reach`): below the form, after a hairline (24px above it, 32px margin): [Download resume] (LinkedIn) (GitHub).
- **Tag** (`.tag`): 13px/500 accent text in a pill with a 1px border at 40% accent. Only "Now".
- **Experience list** (`.list` / `.item`): hairline rows. The title (h3) and date sit on one line, and the company (ink, 500) and one line of what was done (ink-2) sit underneath.
- **Project slide** (`.pslide`): meta (accent) / name (h3) / one-line description (ink-2) / "View on GitHub ›". The progress bar is 01 ▬▬▬▬ 04, 3px tall, and the bars fill with the accent. Slides cross-fade with a 16px rise.
- **Form field** (`.field`): the label sits above the field (14px ink). The input is 48px+ tall (the message box 112px), on `--surface`, with a 1px `--field-line` border, radius 12, padding 12/16, 16px text and muted placeholders. Hover strengthens the border. Focus gets an accent border plus a 3px ring at 22% accent. An error gets an `--error` border and label, and the reason goes under the field with `aria-describedby`. Show success only after a real send.
- **Toast**: on the surface colour, ink text, pill, bottom centre, for 2.6s.
- **Scroll cue**: a 22×34 outlined mouse on the hero only. Hidden on phones and with reduced motion.
- **Readability shade**: a fixed layer over the canvas: on desktop a `linear-gradient(90deg, bg 0%, bg/.92 28%, bg/.55 46%, transparent 62%)`, and on phones a bottom scrim (`bg/0` to `bg/.86` at 34% to `bg` at 72%, 60% of the height).

## 6. 3D look

- Materials: steel-blue clay `#b9cde6` (roughness .5), dark clay `#7f98b8`, graphite `#1b2131`, steel `#8a95a8`, paper `#d6e4f5`, glass (MeshPhysical, transmission), the accent blue `#2a6fb8` for the Now block, and the one emissive glow `#5ab9fc`. Floor `#080b12`, roughness .78.
- Lights: hemisphere `#c9d6e8` over bg at .55, key directional `#dfeaff` at 2.2 with soft shadows (the only shadow caster), rim directional in the accent at 2.2 from behind, and a RoomEnvironment PMREM at low intensity. Fog in bg from 20 to 52. ACES tone mapping.
- Framing: on desktop, `setViewOffset` shifts the scene right (hero .18, work .22, projects .2, contact .26). On phones the scene shifts up 24%, pulls back 1.7× and uses fov 46. No model may cross the text column at any scroll position. Passed project models sink and shrink away; they never fly across the text or the nav.
- Motion: pop-up spring on load, hold windows (20–80% of each section) with a Catmull-Rom glide in between, smootherstep easing, damping `1 - 0.025^dt`, a ±0.3 rad orbit during work and contact holds, mouse parallax and idle drift on desktop only.

## 7. Motion tokens

| Name | Value |
|---|---|
| Ease out | `cubic-bezier(.16, 1, .3, 1)` (slides, reveals) |
| Ease in-out | easeInOutCubic (nav scrolling, 900ms + distance × .25, up to 2200ms) |
| Hover | 180–250ms |
| Slide cross-fade | 500ms opacity, 600ms transform |
| Canvas fade-in | 1.4s |
| Reduced motion | no springs, orbit, drift or cue; instant scroll; all content visible |

## 8. Accessibility and quality bar

- A skip link, visible focus rings (2px accent, offset 3, never animated), every control named, heading order h1 → h2 → h3, canvas `aria-hidden`, and all text real and in the DOM.
- Tap targets at least 44px, 16px text in inputs, no sideways scroll at 320px.
- Contrast: reading text 7:1+, meta 4.5:1+, the accent 3:1+ on bg.
- Check at 1440×900, 1024×768, 820×1180, 390×844 and 320 wide. Text is never overlapped by a model.

## 9. Taste-skill review of the mock (applied)

| Section | Finding | Fix applied |
|---|---|---|
| Hero | The eyebrow sat too far from the name | 18px to 8px |
| Hero | The sub-line highlighted the wrong words, and the floor glow washed out the grey text | Key facts are now ink 600 (2+ years experience, Delhi, India) and the stack is muted; the left readability shade was added |
| Hero (phone) | The stack line broke mid-phrase | The stack gets its own line on phones |
| Nav | 13.5px links are below the taste minimum for nav | 15px |
| Experience | The '23 block overlapped the dates; descriptions were 15px grey | Camera pulled back and offset .22; descriptions 16px in ink-2 |
| Experience | The "NOW" tag was 11px tracked capitals | 13px sentence case |
| Projects | Passed models flew up across the nav | They sink and shrink away |
| Projects | Descriptions were grey | ink-2 |
| Contact | Resume was a plain text link that was easy to miss | A secondary outlined "Download resume" button, with LinkedIn and GitHub as icon buttons |
| Contact | Inline labels and borderless inputs were hard to read and didn't look like fields | Labels above, 48px boxed fields on the surface colour, an accent focus ring |

Known gaps the real build must close: a real form endpoint with errors under each field and a status line, the real resume PDF and links, OG and share meta, a favicon, and running the taste skill's own checks (`gate.mjs`, `copy-lint.mjs`). These scripts could not be run in this environment, so this review was done by hand against the skill's rules.
