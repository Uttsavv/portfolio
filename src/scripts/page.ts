// Page behaviour that works without WebGL: nav state, smooth section jumps, the project showcase and the form.
import { projectProgress, slideIndex } from './scroll';

const reduce = matchMedia('(prefers-reduced-motion: reduce)');
const nav = document.getElementById('nav')!;
const cue = document.getElementById('cue');
const navLinks = [...document.querySelectorAll<HTMLAnchorElement>('.links a')];
const sections = [...document.querySelectorAll<HTMLElement>('.scene')];

/* ---------- nav: solid bar after scrolling, current section marked ---------- */
function onScroll() {
  const y = scrollY;
  nav.classList.toggle('solid', y > 40);
  if (cue) cue.style.opacity = y > 40 ? '0' : '1';
  let current = '';
  for (const s of sections) {
    const r = s.getBoundingClientRect();
    if (r.top < innerHeight * 0.5 && r.bottom > innerHeight * 0.5) current = s.id;
  }
  for (const a of navLinks) a.setAttribute('aria-current', String(a.hash === '#' + current));
}

/* ---------- smooth, eased jumps that land where each scene is in place ---------- */
let jumpRaf = 0;
const easeInOut = (x: number) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);

function sectionY(el: HTMLElement) {
  if (el.id === 'top') return 0;
  if (innerWidth <= 860) return el.offsetTop; // phones: sections flow, land on the scene band
  const run = Math.max(0, el.offsetHeight - innerHeight);
  return el.offsetTop + run * 0.22;
}

export function smoothTo(to: number, focusEl?: HTMLElement | null) {
  cancelAnimationFrame(jumpRaf);
  const from = scrollY;
  const dist = Math.abs(to - from);
  const done = () => focusEl?.focus({ preventScroll: true });
  if (reduce.matches || dist < 2) {
    scrollTo(0, to);
    done();
    return;
  }
  const dur = Math.min(2000, 800 + dist * 0.22);
  const start = performance.now();
  const step = (now: number) => {
    const k = Math.min(1, (now - start) / dur);
    scrollTo(0, from + (to - from) * easeInOut(k));
    if (k < 1) jumpRaf = requestAnimationFrame(step);
    else done();
  };
  jumpRaf = requestAnimationFrame(step);
}
const cancelJump = () => cancelAnimationFrame(jumpRaf);
addEventListener('wheel', cancelJump, { passive: true });
addEventListener('touchstart', cancelJump, { passive: true });
addEventListener('keydown', (e) => { if (['ArrowDown', 'ArrowUp', 'PageDown', 'PageUp', 'Home', 'End', ' '].includes(e.key)) cancelJump(); });

document.addEventListener('click', (e) => {
  const a = (e.target as Element).closest<HTMLAnchorElement>('a[href^="#"]');
  if (!a || e.defaultPrevented || e.metaKey || e.ctrlKey) return;
  const id = a.hash.slice(1);
  if (id === 'main') return; // skip link keeps its native behaviour
  const el = document.getElementById(id);
  if (!el) return;
  e.preventDefault();
  history.replaceState(null, '', id === 'top' ? location.pathname : '#' + id);
  smoothTo(sectionY(el), el.querySelector<HTMLElement>('h1, h2'));
});

/* ---------- projects: one at a time, driven by scroll, tabs jump to a project ---------- */
const proj = document.getElementById('projects')!;
const slides = [...proj.querySelectorAll<HTMLElement>('.pslide')];
const tabs = [...proj.querySelectorAll<HTMLButtonElement>('.ptab')];
const bars = tabs.map((t) => t.querySelector('b')!);
const count = slides.length;
let activeSlide = 0;
// phones: projects are a tap/swipe carousel; wide screens: scroll drives them through a pinned stretch
const flowQ = matchMedia('(max-width: 860px)');

function setSlide(a: number) {
  activeSlide = a;
  proj.dataset.active = String(a); // the 3D world follows this on phones
  slides.forEach((s, i) => {
    s.classList.toggle('on', i === a);
    s.classList.toggle('past', i < a);
    s.toggleAttribute('inert', i !== a);
  });
  tabs.forEach((t, i) => t.setAttribute('aria-current', String(i === a)));
}

function onProjects() {
  if (flowQ.matches) {
    bars.forEach((b, i) => (b.style.width = i <= activeSlide ? '100%' : '0%'));
    return;
  }
  const p = projectProgress(proj);
  const a = slideIndex(p, count);
  if (a !== activeSlide) setSlide(a);
  bars.forEach((b, i) => (b.style.width = Math.max(0, Math.min(1, p * count - i)) * 100 + '%'));
}
slides.forEach((s, i) => s.toggleAttribute('inert', i !== 0));
proj.dataset.active = '0';
tabs.forEach((t, i) =>
  t.addEventListener('click', () => {
    if (flowQ.matches) { setSlide(i); onProjects(); return; }
    const run = proj.offsetHeight - innerHeight;
    // land in the middle of that project's stretch of scroll
    smoothTo(proj.offsetTop + run * (0.2 + 0.6 * ((i + 0.5) / count)));
  }),
);
// swipe left/right through projects on phones
const pshow = proj.querySelector<HTMLElement>('.pshow');
let swipeX = 0, swipeY = 0, swiping = false;
pshow?.addEventListener('pointerdown', (e) => { if (!flowQ.matches) return; swiping = true; swipeX = e.clientX; swipeY = e.clientY; });
pshow?.addEventListener('pointerup', (e) => {
  if (!swiping) return;
  swiping = false;
  const dx = e.clientX - swipeX, dy = e.clientY - swipeY;
  if (Math.abs(dx) < 40 || Math.abs(dx) < Math.abs(dy)) return;
  const next = Math.max(0, Math.min(count - 1, activeSlide + (dx < 0 ? 1 : -1)));
  if (next !== activeSlide) { setSlide(next); onProjects(); }
});
pshow?.addEventListener('pointercancel', () => (swiping = false));
flowQ.addEventListener('change', onProjects);

let scrollQueued = false; // one layout read per frame, not per scroll event
addEventListener('scroll', () => { if (scrollQueued) return; scrollQueued = true; requestAnimationFrame(() => { scrollQueued = false; onScroll(); onProjects(); }); }, { passive: true });
addEventListener('resize', onProjects);
onScroll();
onProjects();

/* ---------- contact form ---------- */
const form = document.getElementById('cform') as HTMLFormElement | null;
if (form) {
  const email = form.querySelector<HTMLInputElement>('#cf-email')!;
  const msg = form.querySelector<HTMLTextAreaElement>('#cf-msg')!;
  const status = form.querySelector<HTMLElement>('#cf-status')!;
  const button = form.querySelector<HTMLButtonElement>('button[type="submit"]')!;
  const setErr = (field: HTMLInputElement | HTMLTextAreaElement, text: string) => {
    field.setAttribute('aria-invalid', String(!!text));
    document.getElementById(field.id + '-err')!.textContent = text;
  };
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const okEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value.trim());
    const okMsg = msg.value.trim().length > 1;
    setErr(email, okEmail ? '' : 'Write an email address with an @, so I can reply.');
    setErr(msg, okMsg ? '' : 'Write a short message.');
    if (!okEmail || !okMsg) {
      status.textContent = '';
      (okEmail ? msg : email).focus();
      return;
    }
    const endpoint = form.dataset.endpoint;
    if (!endpoint) {
      // no form service yet: hand over to the visitor's mail app, prefilled
      const to = form.dataset.email || '';
      const body = `${msg.value.trim()}\n\nReply to: ${email.value.trim()}`;
      location.href = `mailto:${to}?subject=${encodeURIComponent('Hello from your portfolio')}&body=${encodeURIComponent(body)}`;
      status.textContent = 'Opening your mail app…';
      return;
    }
    button.disabled = true;
    const slow = setTimeout(() => (status.textContent = 'Sending…'), 300);
    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({ email: email.value.trim(), message: msg.value.trim() }),
      });
      if (!res.ok) throw new Error(String(res.status));
      form.reset();
      status.textContent = 'Message sent. I’ll reply by email.';
    } catch {
      status.textContent = 'That didn’t send. Try again, or use the GitHub link below.';
    } finally {
      clearTimeout(slow);
      button.disabled = false;
    }
  });
}

/* ---------- the 3D world: loaded after first paint, only where WebGL works ---------- */
function hasWebGL() {
  try {
    const c = document.createElement('canvas');
    return !!(c.getContext('webgl2') || c.getContext('webgl'));
  } catch {
    return false;
  }
}
if (hasWebGL()) {
  const start = () => import('./world/world').then((m) => m.start()).catch((err) => {
    console.error(err);
    document.documentElement.classList.add('no-gl');
  });
  // start straight away: the Delhi model is already downloading (preloaded in the head), so build the scene as soon as it lands
  start();
} else {
  document.documentElement.classList.add('no-gl');
}

/* ---------- offline cache: keep the 3D models and the hashed scripts on the device after the first visit ---------- */
if ('serviceWorker' in navigator && location.protocol === 'https:') {
  addEventListener('load', () => navigator.serviceWorker.register(import.meta.env.BASE_URL.replace(/\/$/, '') + '/sw.js').catch(() => {}), { once: true });
}
