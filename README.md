# portfolio

Utsav Singh's developer portfolio: a dark single page with a 3D world (three.js) that the camera flies through as you scroll. Built with Astro, hosted on GitHub Pages.

## Edit the content

Everything the page says lives in [`src/data/`](src/data/README.md): `profile.json`, `experience.json`, `projects.json`. Edit, push to `main`, and the site redeploys.

## Develop

```bash
npm install
npm run dev        # http://localhost:4321/portfolio/
npm run build      # static site in dist/
```

## 3D models

The models are made in Blender by Python scripts in [`blender/`](blender/), so they can be changed and rebuilt:

```bash
pip install bpy==5.2.3       # Blender as a Python module (Python 3.13)
npm run models:blender       # writes blender/out/*.glb   (add --preview for Cycles stills)
npm run models               # meshopt-compresses them into public/models/
```

| File | Scene | Objects (node names the site reads) |
|---|---|---|
| `delhi.glb` | Hero | `qutub`, `indiaGate`, `jamaMasjid`, `tower0`–`tower8` |
| `career.glb` | Experience | `slab`, `slabNow`, `flagPole`, `flagCloth` |
| `projects.glb` | Projects | `handheld`, `kanban`, `jar`, `terminal` (+ `cursor`) |
| `contact.glb` | Contact | `envelope`, `flap`, `letter`, `plane` |

Material names (`clay`, `clay2`, `glow`, `glass`, …) are mapped to tuned three.js materials in `src/scripts/world/world.ts`.

## Design system

Tokens: `src/styles/tokens.css`. Rules: [`docs/DESIGN-SYSTEM.md`](docs/DESIGN-SYSTEM.md). Living page: `/design-system/`.

## Deploy

`.github/workflows/deploy.yml` builds and publishes to GitHub Pages on every push to `main`
(repo Settings → Pages → Source: GitHub Actions). For a custom domain, set `SITE_URL` and `BASE_PATH=/` in the workflow's build step.
