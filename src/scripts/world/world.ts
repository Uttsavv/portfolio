// The 3D world behind the page: four scenes along one camera path, driven by scroll.
// Models are made in Blender (see /blender) and loaded as meshopt-compressed GLBs.
import * as THREE from 'three';
import { GLTFLoader, type GLTF } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { MeshoptDecoder } from 'three/examples/jsm/libs/meshopt_decoder.module.js';
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js';
import { projectProgress, sceneT } from '../scroll';

type WorldData = { models: string; years: string[]; projects: string[] };

const BG = 0x0a0d14;
const SKY = 0x5ab9fc;
const WX = 34, PX = 68, CX = 102; // x of each scene along the path

const clamp01 = (v: number) => Math.max(0, Math.min(1, v));
const ease = (v: number) => (v < 0.5 ? 4 * v * v * v : 1 - Math.pow(-2 * v + 2, 3) / 2);
const smoother = (v: number) => v * v * v * (v * (v * 6 - 15) + 10);
const spring = (v: number) => (v <= 0 ? 0 : v >= 1 ? 1 : 1 - Math.exp(-6 * v) * Math.cos(9 * v)); // a little overshoot

export async function start() {
  const data: WorldData = JSON.parse(document.getElementById('world-data')!.textContent!);
  const canvas = document.getElementById('world') as HTMLCanvasElement;
  const reduceQ = matchMedia('(prefers-reduced-motion: reduce)');
  let reduce = reduceQ.matches;
  reduceQ.addEventListener('change', () => (reduce = reduceQ.matches));

  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance' });
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.05;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.setClearColor(BG, 1);

  const scene = new THREE.Scene();
  scene.fog = new THREE.Fog(BG, 20, 52);
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
  scene.environmentIntensity = 0.35;
  const camera = new THREE.PerspectiveCamera(34, 1, 0.1, 200);

  /* ---------- light ---------- */
  scene.add(new THREE.HemisphereLight(0xc9d6e8, BG, 0.55));
  const key = new THREE.DirectionalLight(0xdfeaff, 2.2);
  key.castShadow = true;
  const small = innerWidth <= 860;
  key.shadow.mapSize.set(small ? 1024 : 2048, small ? 1024 : 2048);
  Object.assign(key.shadow.camera, { left: -11, right: 11, top: 11, bottom: -11, near: 1, far: 60 });
  key.shadow.bias = -0.0004;
  key.shadow.normalBias = 0.02;
  const rim = new THREE.DirectionalLight(SKY, 2.0);
  scene.add(key, key.target, rim, rim.target);

  /* ---------- materials: the Blender material names map onto tuned three.js materials ---------- */
  const std = (color: number, roughness: number, metalness = 0.06, extra: THREE.MeshStandardMaterialParameters = {}) =>
    new THREE.MeshStandardMaterial({ color, roughness, metalness, envMapIntensity: 0.45, ...extra });
  const MATS: Record<string, THREE.Material> = {
    clay: std(0xb9cde6, 0.5),
    clay2: std(0x7f98b8, 0.55),
    clayDark: std(0x5d7393, 0.55),
    marble: std(0xd9e5f3, 0.42, 0.04),
    graphite: std(0x1b2131, 0.38, 0.35),
    steel: std(0x8a95a8, 0.28, 0.85),
    glow: std(SKY, 0.4, 0, { emissive: SKY, emissiveIntensity: 1.5 }),
    blue: std(0x2a6fb8, 0.35, 0.2, { emissive: SKY, emissiveIntensity: 0.16 }),
    glass: new THREE.MeshPhysicalMaterial({ color: 0xdfeaf7, roughness: 0.06, metalness: 0, transmission: 0.94, thickness: 0.5, ior: 1.45, envMapIntensity: 0.8, side: THREE.DoubleSide }),
    paper: std(0xd6e4f5, 0.62, 0, { side: THREE.DoubleSide }),
    paperShade: std(0xa9bdd8, 0.6, 0, { side: THREE.DoubleSide }),
    ink: std(0x2a3346, 0.5, 0),
    rubber: std(0x2b3447, 0.7, 0),
  };
  const glowMat = MATS.glow as THREE.MeshStandardMaterial;
  function dress(root: THREE.Object3D) {
    root.traverse((o) => {
      const m = o as THREE.Mesh;
      if (!m.isMesh) return;
      const swap = (mat: THREE.Material) => MATS[mat.name.replace(/\.\d+$/, '')] ?? mat;
      m.material = Array.isArray(m.material) ? m.material.map(swap) : swap(m.material);
      m.castShadow = true;
      m.receiveShadow = true;
      if ((m.material as THREE.Material).name === 'glass' || m.material === MATS.glass) m.castShadow = false;
    });
    return root;
  }

  /* ---------- floor: matte, so it never throws a blue glare under the text ---------- */
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(400, 140), new THREE.MeshLambertMaterial({ color: 0x0b0f18 }));
  floor.rotation.x = -Math.PI / 2;
  floor.position.x = 50;
  floor.receiveShadow = true;
  scene.add(floor);

  /* ---------- loading ---------- */
  const loader = new GLTFLoader().setMeshoptDecoder(MeshoptDecoder);
  const load = (name: string) => loader.loadAsync(data.models + name + '.glb').then((g: GLTF) => dress(g.scene));
  const node = (root: THREE.Object3D, name: string) => {
    const o = root.getObjectByName(name);
    if (!o) throw new Error('missing node ' + name);
    return o;
  };

  /* ---------- scene 0: Delhi (pop-up pieces stand up on load) ---------- */
  const delhiRoot = await load('delhi');
  const pops: { pivot: THREE.Group; delay: number }[] = [];
  const delhi = new THREE.Group();
  scene.add(delhi);
  [...delhiRoot.children].forEach((child) => {
    const pivot = new THREE.Group();
    pivot.position.copy(child.position);
    child.position.set(0, 0, 0);
    pivot.add(child);
    delhi.add(pivot);
    const n = child.name;
    const delay = n === 'jamaMasjid' ? 0 : n === 'qutub' ? 0.1 : n === 'indiaGate' ? 0.25 : 0.02 * Number(n.replace(/\D/g, '') || 0);
    pops.push({ pivot, delay });
  });
  const moon = new THREE.Mesh(new THREE.SphereGeometry(1.0, 48, 24), new THREE.MeshStandardMaterial({ color: SKY, emissive: 0x1f6fb0, emissiveIntensity: 0.9, roughness: 0.85 }));
  moon.position.set(3.4, 8.2, -10.5);
  const moonLight = new THREE.PointLight(SKY, 3, 12, 2);
  moonLight.position.copy(moon.position);
  delhi.add(moon, moonLight);

  /* ---------- camera path: one key per section ---------- */
  const KEYS = [
    { p: [6, 4.6, 21], l: [0, 2.4, 0], off: 0.18 },
    { p: [WX + 7.5, 6, 21.5], l: [WX, 2.2, 0], off: 0.24 },
    { p: [PX + 3, 3.6, 12.5], l: [PX, 2.4, 0], off: 0.13 },
    { p: [CX + 5, 5.4, 15], l: [CX, 2.4, 0], off: 0.26 },
  ];
  const camCurve = new THREE.CatmullRomCurve3(KEYS.map((k) => new THREE.Vector3(...k.p)), false, 'centripetal');
  const lookCurve = new THREE.CatmullRomCurve3(KEYS.map((k) => new THREE.Vector3(...k.l)), false, 'centripetal');
  const sections = [...document.querySelectorAll<HTMLElement>('.scene')];
  const projEl = document.getElementById('projects')!;

  /* ---------- sizing ---------- */
  let W = 0, H = 0, phone = false;
  function resize() {
    W = innerWidth;
    H = innerHeight;
    phone = W <= 860;
    renderer.setPixelRatio(Math.min(devicePixelRatio, phone ? 1.5 : 1.75));
    renderer.setSize(W, H, false);
    camera.aspect = W / H;
    camera.fov = phone ? 46 : 34;
    camera.updateProjectionMatrix();
  }
  addEventListener('resize', resize);
  resize();

  /* ---------- the later scenes load after the hero is on screen ---------- */
  type Block = { g: THREE.Group; h: number; label: THREE.Mesh };
  let blocks: Block[] = [];
  let flag: THREE.Object3D | null = null, cloth: THREE.Mesh | null = null, clothBase: Float32Array | null = null;
  let floaters: { g: THREE.Group; i: number; size: number }[] = [];
  let cursor: THREE.Object3D | null = null;
  let flap: THREE.Object3D | null = null, letter: THREE.Object3D | null = null, plane: THREE.Object3D | null = null;
  let trail: THREE.Line | null = null, trailPts: Float32Array | null = null;
  const planePath = new THREE.CatmullRomCurve3([[-0.2, 0.6, 0.4], [-1.5, 2.2, 1.5], [1.2, 3.6, 1], [3.5, 4.6, -1.5], [1, 5.6, -3.5], [-3, 4.6, -2]].map((p) => new THREE.Vector3(...p)));

  function label(text: string, dark: boolean) {
    const c = document.createElement('canvas');
    c.width = 512; c.height = 256;
    const g = c.getContext('2d')!;
    g.fillStyle = dark ? '#2a3346' : '#ffffff';
    g.font = '700 150px Geist, system-ui, sans-serif';
    g.textBaseline = 'middle';
    g.fillText(text, 34, 134);
    const t = new THREE.CanvasTexture(c);
    t.colorSpace = THREE.SRGBColorSpace;
    t.anisotropy = 4;
    return new THREE.MeshBasicMaterial({ map: t, transparent: true, toneMapped: false, depthWrite: false });
  }

  async function loadRest() {
    const [career, projects, contact] = await Promise.all([load('career'), load('projects'), load('contact')]);

    // experience: one stack of slabs per job, oldest on the left, taller each year
    const work = new THREE.Group();
    work.position.x = WX;
    scene.add(work);
    const slab = node(career, 'slab'), slabNow = node(career, 'slabNow');
    const n = data.years.length;
    data.years.forEach((yr, i) => {
      const isNow = yr === 'Now';
      const h = 1.6 + (n > 1 ? (3 * i) / (n - 1) : 0);
      const count = Math.max(2, Math.round(h / 0.4));
      const g = new THREE.Group();
      const span = Math.min(3.1, 9 / Math.max(1, n));
      g.position.set((i - (n - 1) / 2) * span, 0, 1.4 - i * (2.8 / Math.max(1, n - 1)));
      for (let k = 0; k < count; k++) {
        const s = (isNow ? slabNow : slab).clone();
        s.position.set(0, k * 0.4, 0);
        g.add(s);
      }
      const lab = new THREE.Mesh(new THREE.PlaneGeometry(1.9, 0.95), label(yr, !isNow));
      lab.position.set(-0.05, count * 0.4 - 0.5, 1.165);
      g.add(lab);
      work.add(g);
      blocks.push({ g, h: count * 0.4, label: lab });
    });
    document.fonts.ready.then(() => blocks.forEach((b, i) => {
      (b.label.material as THREE.MeshBasicMaterial).dispose();
      b.label.material = label(data.years[i], data.years[i] !== 'Now');
    }));
    const pole = node(career, 'flagPole');
    cloth = node(career, 'flagCloth') as THREE.Mesh;
    flag = new THREE.Group();
    pole.position.set(0, 0, 0);
    cloth.position.set(0, 0, 0);
    flag.add(pole, cloth);
    clothBase = (cloth.geometry.attributes.position.array as Float32Array).slice();
    // meshopt quantization may give an integer attribute; make it plain floats so we can wave it
    const pos = cloth.geometry.attributes.position as THREE.BufferAttribute;
    const plain = new Float32Array(pos.count * 3);
    for (let k = 0; k < pos.count; k++) { plain[k * 3] = pos.getX(k); plain[k * 3 + 1] = pos.getY(k); plain[k * 3 + 2] = pos.getZ(k); }
    cloth.geometry = cloth.geometry.clone();
    cloth.geometry.setAttribute('position', new THREE.BufferAttribute(plain, 3));
    clothBase = plain.slice();
    const top = blocks[blocks.length - 1];
    flag.position.set(0.7, top.h, 0);
    top.g.add(flag);

    // projects: one object per project, in data order
    const proj = new THREE.Group();
    proj.position.x = PX;
    scene.add(proj);
    const SIZES: Record<string, number> = { handheld: 1.6, kanban: 1.3, jar: 1.6, terminal: 1.25 };
    data.projects.forEach((m, i) => {
      const src = node(projects, m);
      const obj = src.clone();
      obj.position.set(0, 0, 0);
      const g = new THREE.Group();
      g.add(obj);
      g.visible = false;
      proj.add(g);
      floaters.push({ g, i, size: SIZES[m] ?? 1.2 });
      if (m === 'terminal') cursor = obj.getObjectByName('cursor') ?? null;
    });

    // contact: envelope, flap, letter and a paper plane with a dashed trail
    const cont = new THREE.Group();
    cont.position.set(CX, 0, 0.6);
    scene.add(cont);
    const env = node(contact, 'envelope');
    flap = node(contact, 'flap');
    letter = node(contact, 'letter');
    plane = node(contact, 'plane');
    env.position.set(0, 0, 0);
    flap.position.set(0, 0.205, -1.15);
    cont.add(env, flap, letter);
    plane.position.set(0, 0, 0);
    const planeHolder = new THREE.Group();
    plane.rotation.set(0, Math.PI, 0); // Blender nose is +Y (-Z here); lookAt wants +Z
    planeHolder.add(plane);
    planeHolder.scale.setScalar(0.8);
    planeHolder.visible = false;
    cont.add(planeHolder);
    plane = planeHolder;
    trailPts = new Float32Array(60 * 3);
    const tg = new THREE.BufferGeometry();
    tg.setAttribute('position', new THREE.BufferAttribute(trailPts, 3));
    trail = new THREE.Line(tg, new THREE.LineDashedMaterial({ color: SKY, dashSize: 0.12, gapSize: 0.12, transparent: true, opacity: 0.75 }));
    trail.visible = false;
    trail.frustumCulled = false;
    cont.add(trail);
  }
  // the later scenes load once the visitor starts moving (or after a few idle seconds)
  let rest: Promise<void> | null = null;
  const loadLater = () => {
    if (rest) return;
    rest = loadRest().catch((e) => console.error('scene load failed', e));
    removeEventListener('scroll', onFirstScroll);
  };
  const onFirstScroll = () => { if (scrollY > innerHeight * 0.15) loadLater(); };
  addEventListener('scroll', onFirstScroll, { passive: true });
  setTimeout(loadLater, 3500);
  if (scrollY > innerHeight * 0.15) loadLater();
  const panels = sections.map((s) => s.querySelector<HTMLElement>('.panel'));
  let freeTop = 0.5, panelRight = 0.45; // smoothed layout of the text panel on screen

  /* ---------- loop ---------- */
  const clock = new THREE.Clock();
  let mx = 0, my = 0, tmx = 0, tmy = 0;
  if (matchMedia('(pointer: fine)').matches)
    addEventListener('pointermove', (e) => { tmx = e.clientX / innerWidth - 0.5; tmy = e.clientY / innerHeight - 0.5; }, { passive: true });
  let { t } = sceneT(sections);
  let tSmooth = t, lpS = 0, angS = 0, projC = 0, intro = 0;
  const vP = new THREE.Vector3(), vL = new THREE.Vector3(), tmp = new THREE.Vector3(), tgt = new THREE.Vector3();
  let running = false, first = true;

  function frame() {
    if (!running) return;
    const dt = Math.min(clock.getDelta(), 0.05);
    const time = clock.elapsedTime;
    intro = reduce ? 10 : intro + dt;
    const damp = (k: number) => (reduce ? 1 : 1 - Math.pow(k, dt));
    mx += (tmx - mx) * damp(0.05);
    my += (tmy - my) * damp(0.05);
    const st = sceneT(sections);
    t = st.t;
    tSmooth += (t - tSmooth) * damp(0.025);

    // camera: hold at each scene, glide between them
    const si = Math.min(Math.floor(tSmooth), KEYS.length - 2), sf = tSmooth - si;
    const u = (si + smoother(clamp01(sf))) / (KEYS.length - 1);
    camCurve.getPoint(clamp01(u), vP);
    lookCurve.getPoint(clamp01(u), vL);
    // keep the scene clear of the text: read where the current panel actually is
    const panel = panels[Math.max(0, Math.min(panels.length - 1, Math.round(tSmooth)))];
    if (panel) {
      const r = panel.getBoundingClientRect();
      freeTop += (Math.max(0, r.top) / H - freeTop) * damp(0.02);
      panelRight += (r.right / W - panelRight) * damp(0.02);
    }
    let pull = 1;
    if (phone) {
      // free band between the nav and the text; zoom out so the model fits inside it
      const band = Math.max(0.12, freeTop - 64 / H);
      pull = Math.min(3, Math.max(1.35, 0.5 / band));
    } else {
      pull = Math.min(1.8, Math.max(1, 0.62 / Math.max(0.3, 1 - panelRight - 0.04)));
    }
    tmp.subVectors(vP, vL).multiplyScalar(pull - 1); vP.add(tmp);
    if (phone) { vP.y += 1.0; vL.y += 0.5; }
    const fogK = Math.max(1, pull * 0.9);
    (scene.fog as THREE.Fog).near = 20 * fogK;
    (scene.fog as THREE.Fog).far = 52 * fogK;
    // a slow swing round the subject while the experience and contact scenes hold
    lpS += (st.local - lpS) * damp(0.03);
    const near = Math.round(tSmooth);
    const swing = !reduce && (near === 1 || near === 3) && Math.abs(tSmooth - near) < 0.02;
    angS = swing ? (lpS - 0.5) * 0.3 : angS * 0.96;
    tmp.subVectors(vP, vL);
    const ca = Math.cos(angS), sa = Math.sin(angS);
    vP.set(vL.x + tmp.x * ca - tmp.z * sa, vP.y, vL.z + tmp.x * sa + tmp.z * ca);
    if (!reduce && !phone) { vP.x += Math.sin(time * 0.25) * 0.18 + mx * 0.9; vP.y += Math.sin(time * 0.31) * 0.1 - my * 0.5; }
    camera.position.copy(vP);
    camera.lookAt(vL);
    // shift the picture right on wide screens (text owns the left), up on phones (text owns the bottom)
    const i0 = Math.min(Math.floor(tSmooth), KEYS.length - 1), f = tSmooth - i0;
    const keyOff = KEYS[i0].off * (1 - f) + KEYS[Math.min(i0 + 1, KEYS.length - 1)].off * f;
    // centre the subject in the space right of the text panel (never less than the key's own offset)
    const off = phone ? 0 : tSmooth < 0.5 ? keyOff : Math.max(keyOff, (panelRight + 1) / 2 - 0.5 + 0.01);
    const centreY = (64 / H + freeTop) / 2; // middle of the free band above the text (phones)
    camera.setViewOffset(W, H, -W * off, phone ? H * (0.5 - centreY) : 0, W, H);

    key.position.set(vL.x + 7, 12, vL.z + 8);
    key.target.position.copy(vL);
    rim.position.set(vL.x - 8, 6, vL.z - 10);
    rim.target.position.copy(vL);

    // Delhi: pieces stand up like a pop-up book
    for (const { pivot, delay } of pops) {
      const v = spring(clamp01((intro - 0.4 - delay * 2.2) / 1.1));
      pivot.rotation.x = (1 - v) * -Math.PI / 2;
    }
    delhi.visible = tSmooth < 0.6;
    moon.visible = !phone;

    // experience: blocks rise out of the floor one after another
    const pw = tSmooth - 0.25;
    const stagger = 0.36 / Math.max(1, blocks.length - 1);
    blocks.forEach((b, i) => {
      const p = ease(clamp01((pw - i * stagger) / 0.4));
      b.g.position.y = -(1 - p) * (b.h + 0.05);
      b.g.visible = p > 0.001 && tSmooth < 2.4;
    });
    if (flag && cloth && clothBase) {
      flag.scale.setScalar(Math.max(0.001, ease(clamp01((pw - 0.6) / 0.25))));
      const arr = cloth.geometry.attributes.position.array as Float32Array;
      for (let k = 0; k < arr.length; k += 3) {
        const x = clothBase[k];
        arr[k + 2] = clothBase[k + 2] + (reduce ? 0 : Math.sin(x * 5 + time * 3.2) * 0.06 * -x);
      }
      cloth.geometry.attributes.position.needsUpdate = true;
    }

    // projects: the active one centre stage and turning; next ones wait right and back; passed ones sink away
    const pp = projectProgress(projEl);
    const target = Math.max(0, Math.min(floaters.length - 1, pp * floaters.length - 0.5));
    projC += (target - projC) * damp(0.004);
    const rise = ease(clamp01((tSmooth - 1.25) / 0.6));
    for (const o of floaters) {
      const dist = o.i - projC, k = clamp01(1 - Math.abs(dist));
      if (dist >= 0) tgt.set(dist * 4.4, 2.3, -dist * 3.2);
      else tgt.set(-dist * 1.2, 2.3 + dist * 3.2, dist * 2.4);
      o.g.position.set(tgt.x, tgt.y - (1 - rise) * 6 + (reduce ? 0 : Math.sin(time * 0.9 + o.i * 1.7) * 0.08), tgt.z);
      const sc = o.size * (0.62 + 0.38 * k) * (dist < 0 ? clamp01(1 + dist * 2.2) : 1);
      o.g.scale.setScalar(Math.max(0.001, sc));
      o.g.rotation.y = (reduce ? 0 : Math.sin(time * 0.5 + o.i) * 0.35 * k) + dist * -0.5 + (1 - rise) * 1.4;
      o.g.rotation.x = (1 - rise) * 0.5 + (reduce ? 0 : Math.sin(time * 0.4) * 0.05 * k);
      o.g.visible = rise > 0.001 && dist > -0.45 && dist < 2.2 && tSmooth > 1.2 && tSmooth < 2.12;
    }
    if (cursor) cursor.visible = reduce || Math.floor(time * 1.6) % 2 === 0;

    // contact: the flap opens, the letter slides up, the plane takes off and keeps flying
    if (flap && letter && plane && trail && trailPts) {
      const cp = tSmooth - 2.3 + (near === 3 ? lpS * 0.45 : 0);
      flap.rotation.x = ease(clamp01(cp / 0.35)) * -2.3;
      const lp = ease(clamp01((cp - 0.25) / 0.35));
      letter.position.set(0, -0.85 + lp * 2.05, -0.2 + lp * 0.05);
      letter.rotation.x = -lp * 0.12;
      const fp = clamp01((cp - 0.45) / 0.55);
      plane.visible = fp > 0.001;
      trail.visible = fp > 0.02;
      if (fp > 0) {
        const pt = planePath.getPointAt(fp), ahead = planePath.getPointAt(Math.min(1, fp + 0.01));
        plane.position.copy(pt);
        plane.lookAt(ahead.add(plane.parent!.position));
        plane.rotateZ(reduce ? 0 : Math.sin(time * 2) * 0.15);
        for (let k = 0; k < 60; k++) {
          const q = planePath.getPointAt(Math.max(0, fp - (k * fp) / 60));
          trailPts.set([q.x, q.y, q.z], k * 3);
        }
        trail.geometry.attributes.position.needsUpdate = true;
        trail.computeLineDistances();
      }
    }

    // a phone with almost no room above the text shows the plain ground instead of a squeezed model
    scene.visible = !phone || freeTop - 64 / H > 0.13;
    renderer.render(scene, camera);
    if (first) { first = false; canvas.classList.add('ready'); }
    requestAnimationFrame(frame);
  }

  // render only while the tab is visible
  const run = () => { if (!running && !document.hidden) { running = true; clock.getDelta(); requestAnimationFrame(frame); } };
  document.addEventListener('visibilitychange', () => { if (document.hidden) running = false; else run(); });
  run();
}
