// Black-car cartoon reel: toon street with ink hulls, billboard cartoon cards, keyframed cameras, burned-in captions.
// window.renderFrame(f) draws frame f (30 fps). Everything is a pure function of f.
import * as THREE from 'three';
import { mergeVertices } from 'three/addons/utils/BufferGeometryUtils.js';
import * as P from './paint.js';
import { drawStudent, drawGuard } from './cast.js';

const W = 1080, H = 1920, FPS = 30;
const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(1); renderer.setSize(W, H);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(40, W / H, 0.05, 900);

// ---------- toon materials + ink ----------
const grad = new THREE.DataTexture(new Uint8Array([90, 90, 90, 255, 170, 170, 170, 255, 255, 255, 255, 255]), 3, 1);
grad.minFilter = grad.magFilter = THREE.NearestFilter; grad.needsUpdate = true;
function toon(color, map, extra = {}) { return new THREE.MeshToonMaterial({ color, map: map || null, gradientMap: grad, ...extra }); }
const inkUniforms = () => THREE.UniformsUtils.merge([THREE.UniformsLib.fog, { px: { value: 2.6 }, res: { value: new THREE.Vector2(W, H) }, col: { value: new THREE.Color(0x2a1630) } }]);
function inkMat(px = 2.6) {
  const m = new THREE.ShaderMaterial({
    uniforms: inkUniforms(), side: THREE.BackSide, fog: true,
    vertexShader: `uniform float px; uniform vec2 res;
#include <common>
#include <fog_pars_vertex>
void main(){
  vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
  vec4 clip = projectionMatrix * mvPosition;
  vec3 n = normalize(normalMatrix * normal);
  vec4 cn = projectionMatrix * vec4(n, 0.0);
  vec2 d = cn.xy; float l = length(d); d = l > 1e-5 ? d / l : vec2(0.0);
  clip.xy += d * px * 2.0 / res * clip.w;
  gl_Position = clip;
#include <fog_vertex>
}`,
    fragmentShader: `uniform vec3 col;
#include <common>
#include <fog_pars_fragment>
void main(){
  gl_FragColor = vec4(col, 1.0);
#include <fog_fragment>
}`,
  });
  m.uniforms.px.value = px; return m;
}
const INK = inkMat(2.6), INK_THIN = inkMat(1.6);
function hull(geo) { const g = geo.clone(); g.deleteAttribute('uv'); g.deleteAttribute('normal'); const m = mergeVertices(g, 1e-3); m.computeVertexNormals(); return m; }
function add(geo, mat, parent = scene, o = {}) {
  const mesh = new THREE.Mesh(geo, mat);
  mesh.castShadow = o.shadow !== false; mesh.receiveShadow = true;
  if (o.ink !== false) { const h = new THREE.Mesh(hull(geo), o.thin ? INK_THIN : INK); h.castShadow = false; mesh.add(h); }
  parent.add(mesh); return mesh;
}
function at(m, x, y, z, rx = 0, ry = 0, rz = 0, s = 1) { m.position.set(x, y, z); m.rotation.set(rx, ry, rz); if (typeof s === 'number') m.scale.setScalar(s); else m.scale.set(...s); return m; }

// ---------- sky ----------
const skyU = { top: { value: new THREE.Color() }, hor: { value: new THREE.Color() }, bot: { value: new THREE.Color() } };
const sky = new THREE.Mesh(new THREE.SphereGeometry(800, 32, 16), new THREE.ShaderMaterial({
  uniforms: skyU, side: THREE.BackSide, depthWrite: false, fog: false,
  vertexShader: `varying vec3 vp; void main(){ vp = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }`,
  fragmentShader: `uniform vec3 top; uniform vec3 hor; uniform vec3 bot; varying vec3 vp;
void main(){ float h = vp.y; vec3 c = h > 0.0 ? mix(hor, top, pow(clamp(h*1.6,0.0,1.0), 0.8)) : mix(hor, bot, clamp(-h*4.0,0.0,1.0)); gl_FragColor = vec4(c,1.0);
#include <colorspace_fragment>
}`,
}));
scene.add(sky);

// ---------- lights ----------
const hemi = new THREE.HemisphereLight(0xffffff, 0x664433, 1.0); scene.add(hemi);
const sun = new THREE.DirectionalLight(0xffffff, 2.2); sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048); sun.shadow.bias = -0.0004; sun.shadow.normalBias = 0.02;
const sc = sun.shadow.camera; sc.left = -8; sc.right = 8; sc.top = 8; sc.bottom = -8; sc.near = 1; sc.far = 80;
scene.add(sun); scene.add(sun.target);
scene.fog = new THREE.Fog(0xffffff, 8, 60);
const LIGHTS = {
  lit: { sun: 0xfff2dc, si: 0.6, az: 20, el: 60, hs: 0xfff6e6, hg: 0x8a8090, hi: 1.25, fog: 0x2a2440, top: 0x1a1830, hor: 0x2a2440, bot: 0x101020, card: 0xffffff },
  night: { sun: 0x8fa8ff, si: 0.55, az: -40, el: 35, hs: 0x5a6ab0, hg: 0x1a1830, hi: 0.32, fog: 0x0c1028, top: 0x05081a, hor: 0x0c1028, bot: 0x05060f, card: 0x8d9bd0 },
};
const cards = [];
function lerpC(a, b, t) { return new THREE.Color(a).lerp(new THREE.Color(b), t); }
function applyLight(a, b = a, t = 0, center = new THREE.Vector3()) {
  const A = LIGHTS[a], B = LIGHTS[b];
  sun.color.copy(lerpC(A.sun, B.sun, t)); sun.intensity = A.si + (B.si - A.si) * t;
  const az = THREE.MathUtils.degToRad(A.az + (B.az - A.az) * t), el = THREE.MathUtils.degToRad(A.el + (B.el - A.el) * t);
  sun.position.set(center.x + 30 * Math.cos(el) * Math.sin(az), center.y + 30 * Math.sin(el), center.z + 30 * Math.cos(el) * Math.cos(az));
  sun.target.position.copy(center);
  hemi.color.copy(lerpC(A.hs, B.hs, t)); hemi.groundColor.copy(lerpC(A.hg, B.hg, t)); hemi.intensity = A.hi + (B.hi - A.hi) * t;
  scene.fog.color.copy(lerpC(A.fog, B.fog, t));
  skyU.top.value.copy(lerpC(A.top, B.top, t)); skyU.hor.value.copy(lerpC(A.hor, B.hor, t)); skyU.bot.value.copy(lerpC(A.bot, B.bot, t));
  const cc = lerpC(A.card, B.card, t); for (const c of cards) c.mesh.material.color.copy(cc);
}



// ---------- world ----------
// hallway along -z at x = 0
const HALL_L = 40;
const floorH = add(new THREE.PlaneGeometry(3.6, HALL_L), toon(0xffffff, P.tiles('#c9c6d6', '#b4b0c6', 1)), scene, { ink: false, shadow: false });
at(floorH, 0, 0, -HALL_L / 2 + 2, -Math.PI / 2); floorH.material.map.repeat.set(2, 22);
const ceilH = add(new THREE.PlaneGeometry(3.6, HALL_L), toon(0xd8d4e4), scene, { ink: false, shadow: false });
at(ceilH, 0, 3.2, -HALL_L / 2 + 2, Math.PI / 2);
for (const sx of [-1, 1]) {
  const w = add(new THREE.BoxGeometry(0.2, 3.2, HALL_L), toon(0xffffff, P.plaster('#d9d2c0', 1)), scene, { ink: false });
  at(w, sx * 1.9, 1.6, -HALL_L / 2 + 2); w.material.map.repeat.set(10, 1);
  for (let k = 0; k < 9; k++) {
    const z = -3 - k * 3.8;
    const mats = Array(6).fill(toon(0x2f6f6b)); mats[sx < 0 ? 0 : 1] = toon(0xffffff, P.lockers());
    at(add(new THREE.BoxGeometry(0.45, 1.9, 2.6), mats, scene), sx * 1.55, 0.95, z);
  }
  // classroom doors along the hall
  for (let k = 0; k < 5; k++) at(add(new THREE.BoxGeometry(0.08, 2.1, 1.0), toon(0xffffff, P.doorTex()), scene), sx * 1.78, 1.05, -4.9 - k * 7.6);
}
at(add(new THREE.BoxGeometry(3.6, 3.2, 0.2), toon(0xffffff, P.plaster('#cfc8b6', 1)), scene), 0, 1.6, -HALL_L + 2);
const exitSign = new THREE.Mesh(new THREE.PlaneGeometry(0.7, 0.28), new THREE.MeshBasicMaterial({ map: P.label('EXIT', '#1f9e4a', '#ffffff', 512, 200, 140), fog: false }));
at(exitSign, 0, 2.7, -HALL_L + 2.12); scene.add(exitSign);
const panels = [];
for (let k = 0; k < 12; k++) {
  const m = new THREE.Mesh(new THREE.BoxGeometry(0.9, 0.06, 1.5), new THREE.MeshBasicMaterial({ color: 0xffffff }));
  at(m, 0, 3.15, -1.5 - k * 3); scene.add(m); panels.push(m);
}

// classroom at x = 16..24, z = -8..0
const RX = 20, RZ = -4;
const roomFloor = add(new THREE.PlaneGeometry(8, 8), toon(0xffffff, P.planks(1)), scene, { ink: false, shadow: false });
at(roomFloor, RX, 0.001, RZ, -Math.PI / 2); roomFloor.material.map.repeat.set(4, 4);
const wallMat = toon(0xffffff, P.plaster('#cfd6c4', 1));
at(add(new THREE.BoxGeometry(8, 3.2, 0.2), wallMat, scene, { ink: false }), RX, 1.6, -8.1);           // back (board) wall
at(add(new THREE.BoxGeometry(8, 3.2, 0.2), wallMat, scene, { ink: false }), RX, 1.6, 0.1);            // front wall
// window wall x = 24 with three moonlit windows
at(add(new THREE.BoxGeometry(0.2, 3.2, 8), wallMat, scene, { ink: false }), 24.1, 1.6, RZ);
const winMat = new THREE.MeshBasicMaterial({ color: 0x31407a, fog: false });
for (const z of [-1.8, -4, -6.2]) {
  at(add(new THREE.BoxGeometry(0.06, 1.5, 1.5), winMat, scene, { thin: true }), 23.98, 1.75, z);
  const moon = new THREE.Mesh(new THREE.CircleGeometry(0.12, 16), new THREE.MeshBasicMaterial({ color: 0xe8ecff, fog: false }));
  if (z === -4) { at(moon, 23.93, 2.2, -4.3, 0, -Math.PI / 2); scene.add(moon); }
}
// door wall x = 16 with the door at z = -2
at(add(new THREE.BoxGeometry(0.2, 3.2, 1.45), wallMat, scene, { ink: false }), 15.9, 1.6, -0.73);
at(add(new THREE.BoxGeometry(0.2, 3.2, 5.55), wallMat, scene, { ink: false }), 15.9, 1.6, -5.23);
at(add(new THREE.BoxGeometry(0.2, 1.1, 1.1), wallMat, scene, { ink: false }), 15.9, 2.65, -2.0);
const doorPivot = new THREE.Group(); at(doorPivot, 15.92, 0, -1.47); scene.add(doorPivot);
const doorMesh = add(new THREE.BoxGeometry(0.07, 2.1, 1.05), toon(0xffffff, P.doorTex()), doorPivot);
at(doorMesh, 0, 1.05, -0.53);
const doorWin = new THREE.Mesh(new THREE.PlaneGeometry(0.34, 0.5), new THREE.MeshBasicMaterial({ color: 0x223050 }));
at(doorWin, 0.04, 1.6, -0.53, 0, Math.PI / 2); doorPivot.add(doorWin);
const lever = new THREE.Group(); at(lever, 0.06, 1.0, -0.95); doorPivot.add(lever);
at(add(new THREE.CylinderGeometry(0.035, 0.035, 0.06, 12), toon(0xc8ccd8), lever, { thin: true }), 0.0, 0, 0, 0, 0, Math.PI / 2);
const leverArm = add(new THREE.BoxGeometry(0.035, 0.035, 0.16), toon(0xd8dce8), lever, { thin: true }); at(leverArm, 0.04, 0, 0.08);
at(add(new THREE.BoxGeometry(0.02, 0.2, 0.06), toon(0xb8bcc8), lever, { thin: true }), -0.01, -0.02, 0);
const underDoor = new THREE.Mesh(new THREE.PlaneGeometry(0.02, 0.95), new THREE.MeshBasicMaterial({ color: 0xffd9a0, fog: false }));
at(underDoor, 15.98, 0.012, -2.0, 0, Math.PI / 2); scene.add(underDoor);
const underShadow = new THREE.Mesh(new THREE.PlaneGeometry(0.025, 0.3), new THREE.MeshBasicMaterial({ color: 0x050508, fog: false }));
at(underShadow, 15.975, 0.013, -2.0, 0, Math.PI / 2); scene.add(underShadow);
const moon = new THREE.PointLight(0xa8b8ff, 0, 4, 1.2); moon.position.set(16.7, 1.5, -1.5); scene.add(moon);
// chalkboard
const board = new THREE.Mesh(new THREE.PlaneGeometry(4.2, 1.6), new THREE.MeshToonMaterial({ map: P.chalkboard(), gradientMap: grad }));
at(board, RX, 1.7, -7.99); scene.add(board);
// student desks and chairs
function desk(x, z, w = 1.1, d = 0.6, h = 0.75, panel = false) {
  const g = new THREE.Group(); at(g, x, 0, z); scene.add(g);
  at(add(new THREE.BoxGeometry(w, 0.05, d), toon(0xc89a62), g), 0, h, 0);
  for (const [lx, lz] of [[-w / 2 + 0.05, -d / 2 + 0.05], [w / 2 - 0.05, -d / 2 + 0.05], [-w / 2 + 0.05, d / 2 - 0.05], [w / 2 - 0.05, d / 2 - 0.05]])
    at(add(new THREE.BoxGeometry(0.05, h, 0.05), toon(0x5a5a68), g, { thin: true }), lx, h / 2, lz);
  if (panel) at(add(new THREE.BoxGeometry(w, h - 0.05, 0.04), toon(0x9a6a3a), g), 0, (h - 0.05) / 2 + 0.03, d / 2 - 0.02);
  return g;
}
function chair(x, z) {
  const g = new THREE.Group(); at(g, x, 0, z); scene.add(g);
  at(add(new THREE.BoxGeometry(0.45, 0.04, 0.42), toon(0x3f6fd1), g), 0, 0.45, 0);
  at(add(new THREE.BoxGeometry(0.45, 0.38, 0.04), toon(0x3f6fd1), g), 0, 0.68, 0.2);
  for (const [lx, lz] of [[-0.2, -0.18], [0.2, -0.18], [-0.2, 0.18], [0.2, 0.18]]) at(add(new THREE.BoxGeometry(0.03, 0.45, 0.03), toon(0x5a5a68), g, { thin: true }), lx, 0.225, lz);
}
for (const x of [18.2, 20.2, 22.2]) for (const z of [-1.4, -3.0, -4.6]) { desk(x, z); chair(x, z + 0.55); }
const TD = V3(20, 0, -6.0);   // teacher's desk, front panel faces the class (+z)
desk(TD.x, TD.z, 1.6, 0.8, 0.76, true);
function V3(x, y, z) { return new THREE.Vector3(x, y, z); }

// ---------- flashlight ----------
const torch = new THREE.SpotLight(0xfff2c8, 0, 22, 0.3, 0.55, 1.2);
torch.castShadow = true; torch.shadow.mapSize.set(1024, 1024); torch.shadow.bias = -0.0005; torch.shadow.camera.near = 0.2;
scene.add(torch); scene.add(torch.target);
const beamGeo = new THREE.ConeGeometry(1.6, 6, 32, 1, true); beamGeo.translate(0, -3, 0); beamGeo.rotateX(-Math.PI / 2);
const beam = new THREE.Mesh(beamGeo, new THREE.MeshBasicMaterial({ color: 0xfff0c0, transparent: true, opacity: 0.06, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide, fog: false }));
scene.add(beam);
function aimTorch(from, to, on = 1) {
  torch.position.copy(from); torch.target.position.copy(to); torch.intensity = 60 * on;
  beam.visible = on > 0.05; beam.position.copy(from); beam.lookAt(to); beam.material.opacity = 0.07 * on;
}

// ---------- cards ----------
class Card {
  constructor(draw, h = 2.25, w = 1.35, cw = 600, ch = 1000) {
    this.draw = draw; this.cv = document.createElement('canvas'); this.cv.width = cw; this.cv.height = ch;
    this.ctx = this.cv.getContext('2d'); this.tex = new THREE.CanvasTexture(this.cv); this.tex.colorSpace = THREE.SRGBColorSpace;
    const g = new THREE.PlaneGeometry(w, h); g.translate(0, h / 2, 0);
    this.mesh = new THREE.Mesh(g, new THREE.MeshBasicMaterial({ map: this.tex, alphaTest: 0.5, side: THREE.DoubleSide }));
    this.mesh.castShadow = true;
    this.mesh.customDepthMaterial = new THREE.MeshDepthMaterial({ depthPacking: THREE.RGBADepthPacking, map: this.tex, alphaTest: 0.5 });
    this.key = null; scene.add(this.mesh); cards.push(this);
  }
  set(p) { const k = JSON.stringify(p); if (k !== this.key) { this.draw(this.ctx, p); this.tex.needsUpdate = true; this.key = k; } }
}
const kid = new Card(drawStudent);
const guard = new Card(drawGuard);

// ---------- story (frames at 30 fps; voice is placed to these beats) ----------
const END = 1065;
const SH = [['hook', 0], ['desk', 180], ['corridor', 310], ['sweep', 414], ['enter', 470], ['stop', 500], ['look', 560], ['leave', 610],
  ['silence', 750], ['handle', 875], ['black', 945]];
function shotAt(f) { let i = 0; for (let k = 0; k < SH.length; k++) if (f >= SH[k][1]) i = k; return { name: SH[i][0], f0: SH[i][1], f1: i + 1 < SH.length ? SH[i + 1][1] : END, i }; }
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const sstep = x => { x = clamp(x); return x * x * x * (x * (x * 6 - 15) + 10); };
const V = (x, y, z) => new THREE.Vector3(x, y, z);
function keys(f, ks) {
  if (f <= ks[0][0]) return ks[0];
  for (let k = 0; k < ks.length - 1; k++) {
    const a = ks[k], b = ks[k + 1];
    if (f <= b[0]) { const t = sstep((f - a[0]) / (b[0] - a[0])); return [f, a[1].clone().lerp(b[1], t), a[2].clone().lerp(b[2], t), a[3] + (b[3] - a[3]) * t, (a[4] || 0) + ((b[4] || 0) - (a[4] || 0)) * t]; }
  }
  return ks[ks.length - 1];
}
const KID = V(20.0, 0, -6.55);   // under the teacher's desk, behind the panel
function camFor(sh, f) {
  switch (sh.name) {
    case 'hook': return keys(f, [[0, V(0.25, 1.6, 1.2), V(0, 1.5, -20), 44, 0], [179, V(0.2, 1.55, -0.6), V(0, 1.45, -20), 44, 0]]);
    case 'desk': return keys(f, [[180, V(21.6, 0.95, -7.75), V(20.0, 0.5, -6.45), 44, 0], [309, V(21.4, 0.9, -7.75), V(20.0, 0.5, -6.45), 44, -2]]);
    case 'corridor': return keys(f, [[310, V(0.5, 1.5, -4.0), V(0, 1.1, -18), 42, 0], [413, V(0.45, 1.45, -5.0), V(0, 1.1, -14), 42, 0]]);
    case 'sweep': return keys(f, [[414, V(23.2, 2.3, -0.6), V(19.5, 0.6, -4.8), 44, 0], [469, V(23.0, 2.2, -0.9), V(19.5, 0.6, -4.8), 44, 0]]);
    case 'enter': return keys(f, [[470, V(19.6, 1.5, -3.2), V(16.2, 1.3, -2.0), 44, 0], [499, V(19.4, 1.5, -3.0), V(16.2, 1.3, -2.0), 44, 0]]);
    case 'stop': return keys(f, [[500, V(23.4, 1.1, -5.6), V(20.0, 0.45, -6.1), 42, 0], [559, V(23.1, 1.05, -5.7), V(20.0, 0.45, -6.1), 42, 2]]);
    case 'look': return keys(f, [[560, V(19.0, 1.5, -2.9), V(16.9, 1.45, -2.0), 40, 0], [609, V(18.8, 1.5, -2.85), V(16.9, 1.45, -2.0), 40, 0]]);
    case 'leave': return keys(f, [[610, V(19.8, 1.5, -3.4), V(16.2, 1.25, -2.0), 44, 0], [749, V(19.4, 1.45, -3.1), V(16.2, 1.25, -2.0), 44, 0]]);
    case 'silence': return keys(f, [[750, V(20.95, 0.62, -7.75), V(20.0, 0.48, -6.55), 40, 0], [874, V(20.8, 0.6, -7.7), V(20.0, 0.52, -6.55), 40, 0]]);
    case 'handle': return keys(f, [[875, V(16.75, 1.08, -1.25), V(15.98, 1.0, -2.42), 36, 0], [944, V(16.6, 1.06, -1.4), V(15.98, 1.0, -2.42), 36, 0]]);
    case 'black': return [f, V(0, 1, 5), V(0, 1, 0), 40, 0];
  }
}
function kidPose(f, sh) {
  const p = { expr: 'smile', arms: 'hang', look: 0, sit: true };
  if (sh.name === 'desk') { if (f < 266) { p.expr = 'grin'; p.arms = Math.floor(f / 9) % 2 ? 'cheer' : 'up'; } else { p.expr = 'worry'; p.arms = 'knees'; } }
  else if (sh.name === 'stop') { p.expr = 'scared'; p.arms = 'mouth'; }
  else if (sh.name === 'silence') { p.expr = 'scared'; p.arms = f < 800 ? 'knees' : 'mouth'; p.look = f < 800 ? 6 : -6; }
  else { p.expr = 'scared'; p.arms = 'knees'; }
  return p;
}

// ---------- overlay text ----------
const outCv = document.createElement('canvas'); outCv.width = W; outCv.height = H; const outCtx = outCv.getContext('2d');
function bigText(ctx, lines, y, alpha, size = 120, col = '#ffffff') {
  ctx.save(); ctx.globalAlpha = alpha; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  lines.forEach((ln, k) => {
    ctx.font = `800 ${size}px Poppins, sans-serif`;
    const yy = y + k * size * 1.15;
    ctx.lineJoin = 'round'; ctx.lineWidth = 16; ctx.strokeStyle = 'rgba(0,0,0,0.85)'; ctx.strokeText(ln, W / 2, yy);
    ctx.fillStyle = k === 1 && lines.length > 1 && col === '#ffffff' ? '#ff4a4a' : col; ctx.fillText(ln, W / 2, yy);
  });
  ctx.restore();
}

window.renderFrame = function (f) {
  const sh = shotAt(f);
  if (sh.name === 'black') {
    outCtx.fillStyle = '#000'; outCtx.fillRect(0, 0, W, H);
    { const z = 1 + 0.0009 * (f - 945); outCtx.save(); outCtx.translate(W / 2, 930); outCtx.scale(z, z); outCtx.translate(-W / 2, -930); }
    if (f >= 958 && f < 1018) bigText(outCtx, ['THEN WHO', 'KNOCKED?'], 880, clamp((f - 958) / 12) * (f > 1008 ? clamp((1018 - f) / 10) : 1), 130, '#ffffff');
    if (f >= 1018) { bigText(outCtx, ['PART 2'], 840, clamp((f - 1018) / 10), 140, '#ffffff'); bigText(outCtx, ['FOLLOW TO FIND OUT'], 1010, clamp((f - 1024) / 10), 70, '#ff4a4a'); }
    outCtx.restore();
    return outCv.toDataURL('image/jpeg', 0.93);
  }
  // hallway lights: switch off one by one, far to near
  let on = 0;
  panels.forEach((p, k) => { const off = 12 + (11 - k) * 11; const lit = f < off; p.material.color.set(lit ? 0xffffff : 0x2a2a36); if (lit) on++; });
  const litFrac = sh.name === 'hook' ? on / panels.length : 0;
  // cards
  kid.mesh.visible = ['desk', 'stop', 'silence'].includes(sh.name);
  kid.set(kidPose(f, sh));
  const kidScale = 0.55;
  kid.mesh.scale.setScalar(kidScale);
  let rise = 0; if (sh.name === 'silence') rise = 0.06 * sstep((f - 760) / 40);
  const bounce = sh.name === 'desk' && f < 266 ? 0.02 * Math.abs(Math.sin(f * 0.35)) : 0;
  kid.mesh.position.set(KID.x, -0.24 + rise + bounce, KID.z);
  guard.mesh.visible = false; aimTorch(V(0, 0, 0), V(0, 0, -1), 0);
  if (sh.name === 'corridor') {
    const z = -24 + (f - 310) * 0.14, step = Math.round(Math.sin((f - 310) * 0.28) * 10) / 10;
    guard.mesh.visible = true; guard.set({ step }); guard.mesh.position.set(0.2, 0.0, z);
    const sw = 0.6 * Math.sin((f - 310) * 0.05);
    aimTorch(V(0.75, 1.15, z + 0.3), V(sw, 0, z + 5), 1);
  }
  if (sh.name === 'sweep') { const u = (f - 414) / 55; aimTorch(V(16.2, 1.6, -2.0), V(22.5 - 4.0 * sstep(u), 0.2, -1.5 - 4.5 * sstep(u)), 1); }
  if (sh.name === 'enter' || sh.name === 'stop' || sh.name === 'look' || sh.name === 'leave') {
    guard.mesh.visible = true;
    let gx = 16.9, gz = -2.0, back = false, look = 0, step = 0;
    if (sh.name === 'enter') { gx = 15.2 + 1.7 * sstep((f - 470) / 25); step = Math.round(Math.sin(f * 0.3) * 10) / 10; }
    if (sh.name === 'look') { look = f < 590 ? Math.round(clamp((f - 565) / 20) * 10) / 10 : 0; back = f >= 594; }
    if (sh.name === 'leave') { back = true; gx = 16.9 - 2.4 * sstep((f - 615) / 45); step = f < 660 ? Math.round(Math.sin(f * 0.3) * 10) / 10 : 0; guard.mesh.visible = f < 662; }
    guard.set({ step, back, look }); guard.mesh.position.set(gx, 0, gz);
    // torch: sweeps the desks, stops on the teacher's desk panel for about a second, then leaves
    let tgt;
    if (sh.name === 'enter') tgt = V(21, 0.2, -1.2);
    else if (sh.name === 'stop') { const u = clamp((f - 500) / 20); tgt = V(23 - 3.0 * sstep(u), 0.45, -3.4 - 2.1 * sstep(u)); }
    else if (sh.name === 'look') tgt = f < 590 ? V(20.0, 0.45, -5.5) : V(18, 0.2, -1.0 + (f - 590) * 0.05);
    else tgt = V(14, 0.2, -2.0);
    aimTorch(V(gx + 0.45, 1.15, gz + 0.1), tgt, sh.name === 'leave' ? (f < 662 ? 1 : 0) : 1);
  }
  // door: closes behind the guard and the lever turns from the other side
  const doorAng = sh.name === 'leave' ? -1.35 * (1 - sstep((f - 655) / 15)) : ['enter', 'stop', 'look'].includes(sh.name) ? -1.35 : 0;
  doorPivot.rotation.y = doorAng;
  lever.rotation.x = sh.name === 'handle' ? 0.6 * sstep((f - 885) / 55) : 0;
  underDoor.visible = underShadow.visible = sh.name === 'handle' || (sh.name === 'silence' && f > 780);
  moon.intensity = sh.name === 'handle' ? 0.9 : 0;
  underShadow.position.z = -2.2 + 0.25 * sstep((f - 790) / 60);
  // camera
  let [, cp, ct, fov, roll] = camFor(sh, f);
  let shake = 0;
  for (const kf of [786, 828, 843]) if (f >= kf && f < kf + 6) shake += 0.008 * (1 + (kf - 786) / 60) * (1 - (f - kf) / 6);
  camera.position.copy(cp).add(V(Math.sin(f * 2.3) * shake + 0.008 * Math.sin(f * 0.04), Math.cos(f * 1.7) * shake + 0.006 * Math.sin(f * 0.031), 0));
  camera.fov = fov; camera.updateProjectionMatrix(); camera.up.set(0, 1, 0); camera.lookAt(ct);
  camera.rotateZ(THREE.MathUtils.degToRad(roll || 0));
  for (const c of cards) { const m = c.mesh; m.rotation.set(0, Math.atan2(camera.position.x - m.position.x, camera.position.z - m.position.z), 0); }
  // light: hallway fades from lit to night as the panels go out
  const center = sh.name === 'hook' || sh.name === 'corridor' ? V(0, 0, -10) : V(RX, 0, RZ);
  applyLight('night', 'lit', litFrac, center);
  // the kid catches a little torch spill only when the beam is right on the desk
  if (sh.name === 'stop' && f > 515 && f < 548) kid.mesh.material.color.lerp(new THREE.Color(0xd6dcff), 0.5);
  renderer.render(scene, camera);
  outCtx.drawImage(renderer.domElement, 0, 0);
  // grade: cold vignette, slight darkening
  const g = outCtx.createRadialGradient(W / 2, H / 2, H * 0.25, W / 2, H / 2, H * 0.72);
  g.addColorStop(0, 'rgba(0,0,10,0)'); g.addColorStop(1, 'rgba(0,0,12,0.6)'); outCtx.fillStyle = g; outCtx.fillRect(0, 0, W, H);
  if (sh.name === 'hook' && f < 172) bigText(outCtx, ['EVERYONE LEFT', 'EXCEPT YOU'], 1010, f < 160 ? 1 : clamp((172 - f) / 12), 118);
  if (sh.name === 'handle' && f >= 940) { outCtx.fillStyle = `rgba(0,0,0,${clamp((f - 940) / 4)})`; outCtx.fillRect(0, 0, W, H); }
  return outCv.toDataURL('image/jpeg', 0.93);
};
window.FRAMES = END;
window.ready = true;
