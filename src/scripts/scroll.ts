// Scroll maths shared by the page text and the 3D world, so both stay in step.

/** 0..1 progress through the projects showcase (the middle 60% of the pinned run). */
export function projectProgress(proj: HTMLElement) {
  const r = proj.getBoundingClientRect();
  const run = r.height - innerHeight;
  return Math.max(0, Math.min(1, (-r.top - run * 0.2) / (run * 0.6)));
}

export const slideIndex = (p: number, count: number) => Math.min(count - 1, Math.floor(p * count));

/**
 * Continuous scene index: 0 = hero, 1 = experience, 2 = projects, 3 = contact.
 * Each section holds its scene for the middle of its pinned scroll; between holds t moves from i to i+1.
 * `local` is the 0..1 progress through the current hold.
 */
export function sceneT(sections: HTMLElement[]) {
  const y = scrollY, vh = innerHeight;
  const holds = sections.map((s, i) => {
    const run = Math.max(1, s.offsetHeight - vh);
    return [s.offsetTop + run * (i === 0 ? 0 : 0.2), s.offsetTop + run * 0.8];
  });
  for (let i = 0; i < holds.length; i++) {
    const [a, b] = holds[i];
    if (y <= a) {
      if (i === 0) return { t: 0, local: 0 };
      const pb = holds[i - 1][1];
      return { t: i - 1 + (y - pb) / Math.max(1, a - pb), local: 0 };
    }
    if (y <= b) return { t: i, local: (y - a) / Math.max(1, b - a) };
  }
  return { t: holds.length - 1, local: 1 };
}
