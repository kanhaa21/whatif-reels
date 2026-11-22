// School After Dark Part 3: same toon school, cards and grade as Parts 1-2; picture locked to work/phrases.json.
// window.renderFrame(f) draws frame f (30 fps). Everything is a pure function of f.
import * as THREE from 'three';
import { mergeVertices } from 'three/addons/utils/BufferGeometryUtils.js';
import * as P from './paint.js';
import { drawStudent, drawGuard, drawEntity, drawPrint, drawGhost } from './cast.js';

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
at(underDoor, 15.98, 0.012, -2.0, -Math.PI / 2, 0); scene.add(underDoor);
const underShadow = new THREE.Mesh(new THREE.PlaneGeometry(0.025, 0.3), new THREE.MeshBasicMaterial({ color: 0x050508, fog: false }));
at(underShadow, 15.975, 0.013, -2.0, -Math.PI / 2, 0); scene.add(underShadow);
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


// ======================= Part 3 story (appended to base_part1.js by build) =======================
const PH = (await (await fetch('./phrases.json')).json());
const Ph = i => PH.phrases[i], C = (i, j) => PH.phrases[i].chunks[j];
const TOTAL = PH.duration, END = Math.round(TOTAL * 30);
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const sstep = x => { x = clamp(x); return x * x * x * (x * (x * 6 - 15) + 10); };
const V = (x, y, z) => new THREE.Vector3(x, y, z);
const KNOCKS = [0.25, 0.65, 1.05];
let NOW = 0;

// ---------- extra props ----------
const entity = new Card(drawEntity);
const outside = new THREE.Mesh(new THREE.PlaneGeometry(4, 3.4), new THREE.MeshBasicMaterial({ color: 0x060914, fog: false }));
at(outside, 15.0, 1.6, -2.0, 0, Math.PI / 2); scene.add(outside);
doorPivot.rotation.y = -1.35;                       // the classroom door stays open from Part 2
// frosty prints looping around the locker (it walked circles around him all night)
const printTex = (() => { const cv = document.createElement('canvas'); cv.width = cv.height = 256; drawPrint(cv.getContext('2d')); const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace; return t; })();
const prints = [];
function addPrint(x, z, yaw, ring) {
  const m = new THREE.Mesh(new THREE.PlaneGeometry(0.18, 0.42), new THREE.MeshBasicMaterial({ map: printTex, transparent: true, depthWrite: false, color: 0xeef5ff, fog: false }));
  m.rotation.order = 'YXZ'; m.rotation.set(-Math.PI / 2, yaw, 0); m.position.set(x, 0.006 + 0.0005 * prints.length, z); scene.add(m);
  const g = new THREE.Mesh(new THREE.PlaneGeometry(0.34, 0.7), new THREE.MeshBasicMaterial({ map: printTex, transparent: true, depthWrite: false, color: 0x8fb4ff, blending: THREE.AdditiveBlending, fog: false }));
  g.position.set(0, 0, 0.002); m.add(g); prints.push({ m, g, ring });
}
{
  const cx = -0.55, cz = -10.0;
  [[0.75, 0.0, 0], [1.05, 0.5, 1], [1.4, 1.1, 2], [1.75, 0.3, 2]].forEach(([r, ph, ring]) => {
    const n = Math.round(r * 13);
    for (let k = 0; k < n; k++) {
      const a = ph + (k / n) * Math.PI * 2, x = cx + r * Math.cos(a) * 0.75, z = cz + r * Math.sin(a);
      if (x < -1.25) continue;                                     // not inside the lockers
      const dx = -Math.sin(a) * 0.75, dz = Math.cos(a), sd = k % 2 ? 0.09 : -0.09;
      addPrint(x + dz * sd, z - dx * sd, Math.atan2(-dx, -dz), ring);
    }
  });
}
// the classroom doors along the hallway, now hinged, each with a dark doorway behind it
const hallDoors = [];
scene.traverse(o => { const g = o.geometry; if (o.isMesh && g && g.parameters && g.parameters.width === 0.08 && g.parameters.height === 2.1 && g.parameters.depth === 1.0 && Math.abs(Math.abs(o.position.x) - 1.78) < 0.01) hallDoors.push(o); });
const doorPivots = hallDoors.map(o => {
  const sx = Math.sign(o.position.x), pv = new THREE.Group(); pv.position.set(o.position.x, 0, o.position.z + 0.5); scene.add(pv);
  scene.remove(o); o.position.set(0, 1.05, -0.5); pv.add(o);
  const hole = new THREE.Mesh(new THREE.PlaneGeometry(1.0, 2.1), new THREE.MeshBasicMaterial({ color: 0x0b1024, fog: false }));
  at(hole, sx * 1.795, 1.05, pv.position.z - 0.5, 0, -sx * Math.PI / 2); scene.add(hole);
  const glow = new THREE.Mesh(new THREE.PlaneGeometry(1.0, 2.1), new THREE.MeshBasicMaterial({ color: 0x7f95d8, transparent: true, opacity: 0, fog: false, blending: THREE.AdditiveBlending, depthWrite: false }));
  at(glow, sx * 1.79, 1.05, pv.position.z - 0.5, 0, -sx * Math.PI / 2); scene.add(glow);
  return { pv, sx, glow };
});
function setHallDoors(u) { for (const d of doorPivots) { d.pv.rotation.y = d.sx * 1.25 * u; d.glow.material.opacity = 0.6 * u; } }
// school bell, loudspeaker and wall clock high on the hallway walls
const bellG = new THREE.Group(); at(bellG, -1.74, 2.55, -7.0); scene.add(bellG);
at(add(new THREE.SphereGeometry(0.16, 20, 12, 0, Math.PI * 2, 0, Math.PI / 2), toon(0xd8343a), bellG), 0.06, 0, 0, 0, 0, -Math.PI / 2);
at(add(new THREE.CylinderGeometry(0.03, 0.03, 0.1, 10), toon(0x3a3a44), bellG, { thin: true }), 0.0, 0, 0, 0, 0, Math.PI / 2);
at(add(new THREE.TorusGeometry(0.16, 0.018, 8, 32), toon(0x8a1a20), bellG, { thin: true }), 0.06, 0, 0, 0, Math.PI / 2, 0);
const hammer = new THREE.Group(); at(hammer, 0.12, -0.24, 0); bellG.add(hammer);
at(add(new THREE.CylinderGeometry(0.012, 0.012, 0.2, 8), toon(0x3a3a44), hammer, { thin: true }), 0, 0.1, 0);
at(add(new THREE.SphereGeometry(0.035, 12, 8), toon(0x2a2a30), hammer, { thin: true }), 0, 0.2, 0);
const spk = add(new THREE.BoxGeometry(0.1, 0.42, 0.42), toon(0xffffff, (() => {
  const cv = document.createElement('canvas'); cv.width = cv.height = 256; const x = cv.getContext('2d');
  x.fillStyle = '#c8c2b0'; x.fillRect(0, 0, 256, 256); x.fillStyle = '#2a2622';
  for (let r = 0; r < 9; r++) for (let q = 0; q < 9; q++) { x.beginPath(); x.arc(34 + q * 24, 34 + r * 24, 7, 0, 6.3); x.fill(); }
  const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace; return t; })()));
at(spk, 1.74, 2.6, -9.0);
const spkLed = new THREE.Mesh(new THREE.CircleGeometry(0.025, 12), new THREE.MeshBasicMaterial({ color: 0xff2a2a, fog: false }));
at(spkLed, 1.685, 2.37, -9.0, 0, -Math.PI / 2); scene.add(spkLed);
const clockTex = (() => {
  const cv = document.createElement('canvas'); cv.width = cv.height = 256; const x = cv.getContext('2d');
  x.fillStyle = '#f4f1e8'; x.beginPath(); x.arc(128, 128, 120, 0, 6.3); x.fill(); x.lineWidth = 12; x.strokeStyle = '#2a2026'; x.stroke();
  for (let k = 0; k < 12; k++) { const a = k / 12 * 6.283; x.lineWidth = 7; x.beginPath(); x.moveTo(128 + 92 * Math.sin(a), 128 - 92 * Math.cos(a)); x.lineTo(128 + 106 * Math.sin(a), 128 - 106 * Math.cos(a)); x.stroke(); }
  const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace; return t; })();
const clockG = new THREE.Group(); at(clockG, -1.785, 2.5, -12.0, 0, Math.PI / 2); scene.add(clockG);
clockG.add(new THREE.Mesh(new THREE.CircleGeometry(0.22, 32), new THREE.MeshBasicMaterial({ map: clockTex })));
const hands = [[0.13, 0.024], [0.18, 0.016]].map(([l, w]) => { const g = new THREE.PlaneGeometry(w, l); g.translate(0, l / 2, 0); const m = new THREE.Mesh(g, new THREE.MeshBasicMaterial({ color: 0x2a2026 })); m.position.z = 0.003; clockG.add(m); return m; });
// the faceless class: eight of nine seats taken; the empty one is the front-middle seat
const ghosts = [];
for (const x of [18.2, 20.2, 22.2]) for (const z of [-1.4, -3.0, -4.6]) {
  if (x === 20.2 && z === -4.6) continue;
  const g = new Card(drawGhost); g.mesh.scale.setScalar(0.6); g.mesh.position.set(x, 0.22, z + 0.55); ghosts.push(g);
}
const lateTex = (() => {
  const cv = document.createElement('canvas'); cv.width = 1024; cv.height = 512; const x = cv.getContext('2d');
  x.fillStyle = '#2f4a3c'; x.fillRect(0, 0, 1024, 512); x.strokeStyle = '#6b4a2a'; x.lineWidth = 30; x.strokeRect(15, 15, 994, 482);
  x.fillStyle = 'rgba(245,245,235,0.95)'; x.font = 'bold 150px sans-serif'; x.textAlign = 'center'; x.textBaseline = 'middle';
  x.save(); x.translate(470, 260); x.rotate(-0.04); x.fillText("YOU'RE", 0, -75); x.fillText('LATE', 0, 75); x.restore();
  const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace; return t; })();
const oldBoard = board.material.map;
const pools = panels.map(p => { const l = new THREE.PointLight(0xe6eeff, 0, 6.5, 1.4); l.position.set(0, 2.9, p.position.z); scene.add(l); return l; });
function hallLights(onFn, flick = 0) {
  panels.forEach((p, k) => {
    let lv = onFn(k); if (lv > 0 && flick) lv *= (Math.sin(NOW * 37 + k * 5.1) > -0.6 ? 1 : 0.25);
    p.material.color.set(lv > 0.5 ? 0xffffff : 0x22222c); pools[k].intensity = 3.2 * lv;
  });
}

// ---------- shots ----------
const SH = [
  ['knock', 0], ['name', C(0, 1).s - 0.1], ['away', Ph(1).s - 0.2], ['open', Ph(2).s - 0.2], ['circle', C(2, 1).s - 0.1], ['circleUp', C(2, 2).s - 0.1],
  ['phone', Ph(3).s - 0.25], ['bell', Ph(4).s - 0.3], ['clock', C(4, 1).s - 0.1], ['pa', Ph(5).s - 0.2], ['paHall', C(5, 1).s - 0.1],
  ['doors', Ph(6).s - 0.1], ['class', Ph(7).s - 0.1], ['except', Ph(8).s - 0.15], ['behind', Ph(9).s - 0.2], ['mom', Ph(10).s - 0.25],
  ['which', Ph(11).s - 0.2], ['black', Ph(11).e + 0.05],
];
function shotAt(t) { let i = 0; for (let k = 0; k < SH.length; k++) if (t >= SH[k][1]) i = k; return { name: SH[i][0], t0: SH[i][1], t1: i + 1 < SH.length ? SH[i + 1][1] : TOTAL }; }
function lerpCam(t, t0, t1, a, b) { const u = sstep((t - t0) / (t1 - t0)); return [a[0].clone().lerp(b[0], u), a[1].clone().lerp(b[1], u), a[2] + (b[2] - a[2]) * u]; }
const LOCKCAM = [V(-1.18, 1.55, -10.0), V(2, 1.45, -10.0), 52];

function setScene(sh, t) {
  const L = t - sh.t0;
  kid.mesh.visible = false; entity.mesh.visible = false; guard.mesh.visible = false; aimTorch(V(0, 0, 0), V(0, 0, -1), 0);
  ghosts.forEach(g => g.mesh.visible = false);
  prints.forEach(p => { p.m.visible = false; });
  hallLights(() => 0); setHallDoors(0); board.material.map = oldBoard; board.material.needsUpdate = true;
  moon.intensity = 0.9; underDoor.visible = underShadow.visible = false; lever.rotation.x = 0;
  hands[0].rotation.z = -0.0; hands[1].rotation.z = -0.0;   // both hands on twelve
  spkLed.visible = false; bellG.visible = true;
  let cam = [V(0, 1, 5), V(0, 1, 0), 40];
  switch (sh.name) {
    case 'knock': case 'name': case 'away': {
      hallLights(k => (k === 3 ? 0.6 : 0), 1);
      entity.mesh.visible = true; entity.mesh.scale.setScalar(1.25);
      let lean = sh.name === 'knock' ? 0.55 : sh.name === 'name' ? 0.55 + 0.45 * sstep((t - C(0, 1).s) / 0.8) : 1 - sstep((t - Ph(1).s) / 0.9);
      let zoff = 0;
      if (sh.name === 'away') zoff = -3.5 * sstep((t - Ph(1).s - 0.5) / 1.6);   // walks off down the hall
      entity.set({ tilt: 0.25, reach: Math.round((sh.name === 'knock' ? 0.6 : 0.4) * 10) / 10 });
      entity.mesh.position.set(0.9 - 0.7 * lean, -0.81 * lean + 0.015 * Math.sin(t * 2.1), -10.0 + zoff + 0.05 * Math.sin(t * 0.9));
      cam = LOCKCAM;
      break;
    }
    case 'open': cam = [V(-1.18, 1.55, -10.0), V(2, 1.3, -10.3), 54]; hallLights(k => (k === 3 ? 0.4 : 0), 1); break;
    case 'circle': case 'circleUp': {
      prints.forEach(p => { const tr = C(2, 1).s + 0.3 + p.ring * 0.55; const a = clamp((t - tr) / 0.25); p.m.visible = a > 0 && (sh.name === 'circleUp' || p.ring < 2 || t > tr); p.m.material.opacity = 0.9 * a; p.g.material.opacity = 0.35 * a; });
      cam = sh.name === 'circle' ? lerpCam(t, sh.t0, sh.t1, [V(-0.55, 2.4, -8.4), V(-0.55, 0, -10.0), 50], [V(-0.55, 2.6, -8.6), V(-0.55, 0, -10.0), 50])
        : lerpCam(t, sh.t0, sh.t1, [V(-0.55, 2.9, -8.2), V(-0.5, 0, -10.0), 54], [V(-0.4, 3.05, -7.6), V(-0.45, 0, -10.0), 60]);
      break;
    }
    case 'bell': case 'clock': case 'pa': case 'paHall': {
      hallLights(k => 0.7, 1);
      if (sh.name === 'bell') { bellG.visible = false; cam = lerpCam(t, sh.t0, sh.t1, [V(0, 1.6, -2.0), V(0, 1.3, -30), 44], [V(0, 1.55, -3.0), V(0, 1.3, -30), 42]); }
      if (sh.name === 'clock') cam = lerpCam(t, sh.t0, sh.t1, [V(-0.9, 2.45, -12.0), V(-1.785, 2.5, -12.0), 34], [V(-1.15, 2.48, -12.0), V(-1.785, 2.5, -12.0), 32]);
      if (sh.name === 'pa') { spkLed.visible = Math.floor(t * 4) % 2 === 0; cam = lerpCam(t, sh.t0, sh.t1, [V(0.6, 2.2, -8.0), V(1.7, 2.6, -9.0), 38], [V(0.9, 2.35, -8.4), V(1.7, 2.6, -9.0), 34]); }
      if (sh.name === 'paHall') { spkLed.visible = Math.floor(t * 4) % 2 === 0; cam = lerpCam(t, sh.t0, sh.t1, [V(0, 1.5, -1.5), V(0, 1.4, -30), 40], [V(0, 1.5, -3.5), V(0, 1.4, -30), 40]); }
      break;
    }
    case 'doors': {
      hallLights(k => 0.6, 1);
      const u = sstep((t - C(6, 1).s + 0.05) / 0.35);
      setHallDoors(u);
      cam = lerpCam(t, sh.t0, sh.t1, [V(0, 1.45, -1.0), V(0, 1.3, -30), 44], [V(0, 1.45, -2.5), V(0, 1.3, -30), 44]);
      break;
    }
    case 'class': case 'except': {
      ghosts.forEach(g => { g.mesh.visible = true; });
      const tl = sstep((t - C(7, 1).s - 0.1) / 0.25) * 0.38;
      ghosts.forEach((g, k) => g.set({ tilt: Math.round((k % 2 ? tl : -tl) * 50) / 50 }));
      entity.mesh.visible = true; entity.mesh.scale.setScalar(1.25); entity.set({ tilt: 0.2 }); entity.mesh.position.set(21.3, 0, -7.3);
      if (sh.name === 'except' || t > C(7, 1).s) board.material.map = lateTex; board.material.needsUpdate = true;
      if (sh.name === 'class' && t >= C(7, 1).s - 0.1) entity.mesh.visible = false;
      if (sh.name === 'class' && t < C(7, 1).s - 0.1) cam = lerpCam(t, sh.t0, C(7, 1).s, [V(16.6, 1.7, -0.9), V(20.6, 0.8, -3.4), 54], [V(17.0, 1.65, -1.2), V(20.6, 0.8, -3.4), 50]);
      else if (sh.name === 'class') cam = lerpCam(t, C(7, 1).s - 0.1, sh.t1, [V(23.3, 1.55, -5.7), V(19.2, 0.85, -1.6), 56], [V(23.1, 1.5, -5.5), V(19.2, 0.85, -1.6), 52]);
      else cam = lerpCam(t, sh.t0, sh.t1, [V(18.75, 1.4, -1.5), V(19.8, 1.15, -5.6), 56], [V(18.8, 1.35, -1.9), V(19.8, 1.1, -5.6), 52]);
      break;
    }
    case 'behind': {
      kid.mesh.visible = true; kid.set({ expr: 'scared', arms: 'hang', look: t > C(9, 1).s ? 4 : 0, sit: false });
      kid.mesh.scale.setScalar(0.6); kid.mesh.position.set(16.95 + 0.003 * Math.sin(NOW * 47), 0, -2.0);
      cam = lerpCam(t, sh.t0, sh.t1, [V(18.6, 1.05, -3.0), V(16.95, 0.75, -2.0), 40], [V(18.2, 1.0, -2.75), V(16.95, 0.78, -2.0), 36]);
      break;
    }
    case 'mom': case 'which':
      cam = lerpCam(t, sh.t0, sh.t1, [V(19.4, 1.3, -2.4), V(15.0, 1.15, -2.0), 44], [V(18.6, 1.3, -2.3), V(15.0, 1.15, -2.0), 40]);
      break;
  }
  return cam;
}

// ---------- 2D overlays ----------
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
// locker door from inside: four vent slits; `open` swings the whole door away to the left
function lockerMask(ctx, open = 0) {
  if (open >= 1) return;
  const dx = -W * sstep(open);
  ctx.save(); ctx.translate(dx, 0); ctx.beginPath(); ctx.rect(0, -10, W + 4, H + 20);
  for (let k = 0; k < 4; k++) ctx.roundRect(120, 650 + k * 120, 840, 62, 18);
  ctx.fillStyle = '#07070b'; ctx.fill('evenodd');
  for (let k = 0; k < 4; k++) { ctx.strokeStyle = 'rgba(120,130,150,0.35)'; ctx.lineWidth = 4; ctx.beginPath(); ctx.roundRect(120, 650 + k * 120, 840, 62, 18); ctx.stroke(); }
  ctx.restore();
}
function wrap(ctx, text, maxW) {
  const words = text.split(' '), lines = []; let cur = '';
  for (const w of words) { const s = cur ? cur + ' ' + w : w; if (ctx.measureText(s).width > maxW && cur) { lines.push(cur); cur = w; } else cur = s; }
  if (cur) lines.push(cur); return lines;
}
function bubble(ctx, text, x, y, w, mine, a, status) {
  ctx.save(); ctx.globalAlpha = a; ctx.font = '500 36px Poppins, sans-serif';
  const lines = wrap(ctx, text, w - 56), bw = Math.min(w, Math.max(...lines.map(l => ctx.measureText(l).width)) + 56), h = 34 + lines.length * 46;
  const bx = mine ? x + w - bw : x;
  ctx.fillStyle = mine ? '#2f7cf6' : 'rgba(235,238,248,0.95)'; ctx.beginPath(); ctx.roundRect(bx, y, bw, h, 30); ctx.fill();
  ctx.fillStyle = mine ? '#fff' : '#111'; ctx.textAlign = 'left'; ctx.textBaseline = 'middle';
  lines.forEach((ln, k) => ctx.fillText(ln, bx + 28, y + 40 + k * 46));
  if (status) { ctx.font = '600 28px Poppins, sans-serif'; ctx.fillStyle = '#ff4a4a'; ctx.textAlign = 'right'; ctx.fillText(status, x + w, y + h + 32); }
  ctx.restore(); return h;
}
function phoneShell(ctx, t, t0) {
  ctx.fillStyle = '#020204'; ctx.fillRect(0, 0, W, H);
  const g = ctx.createRadialGradient(540, 860, 50, 540, 860, 700); g.addColorStop(0, 'rgba(90,130,220,0.35)'); g.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  const z = 1 + 0.03 * (t - t0), jx = 3 * Math.sin(t * 7.3) + 2 * Math.sin(t * 13.1), jy = 3 * Math.cos(t * 6.1);
  ctx.save(); ctx.translate(540 + jx, 880 + jy); ctx.scale(z, z); ctx.translate(-540, -880);
  const pw = 600, ph = 900, px = 540 - pw / 2, py = 430;
  ctx.fillStyle = '#15161d'; ctx.beginPath(); ctx.roundRect(px - 18, py - 18, pw + 36, ph + 36, 70); ctx.fill();
  const sg = ctx.createLinearGradient(0, py, 0, py + ph); sg.addColorStop(0, '#141a2e'); sg.addColorStop(1, '#0a0d18');
  ctx.fillStyle = sg; ctx.beginPath(); ctx.roundRect(px, py, pw, ph, 56); ctx.fill();
  return { px, py, pw, ph };
}
function chat(ctx, t) {
  const { px, py, pw } = phoneShell(ctx, t, Ph(3).s);
  ctx.fillStyle = '#eef2ff'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.font = '700 38px Poppins, sans-serif'; ctx.fillText('Mom', 540, py + 70);
  ctx.font = '400 26px Poppins, sans-serif'; ctx.fillStyle = '#ff6b6b'; ctx.fillText('No service', 540, py + 112);
  ctx.fillStyle = 'rgba(255,255,255,0.12)'; ctx.fillRect(px, py + 150, pw, 2);
  let y = py + 190;
  y += bubble(ctx, "I'm at the school gate. Where are you?", px + 30, y, pw - 140, false, 1) + 24;
  const a1 = clamp((t - (Ph(3).s + 0.25)) / 0.2);
  y += bubble(ctx, "I'm coming inside to find you.", px + 30, y + 30 * (1 - a1), pw - 140, false, a1) + 40;
  // the kid types, sends, and it fails
  const tt = C(3, 1).s, typed = "DON'T COME IN", n = Math.floor(typed.length * clamp((t - tt - 0.2) / 1.0));
  const sent = t > C(3, 1).e + 0.1;
  if (sent) bubble(ctx, typed, px + 110, y, pw - 140, true, 1, t > C(3, 2).s ? '! Not delivered' : 'Sending...');
  // input bar
  const iy = py + 900 - 110;
  ctx.fillStyle = 'rgba(255,255,255,0.10)'; ctx.beginPath(); ctx.roundRect(px + 24, iy, pw - 48, 76, 38); ctx.fill();
  ctx.font = '500 34px Poppins, sans-serif'; ctx.textAlign = 'left'; ctx.fillStyle = sent || n === 0 ? 'rgba(255,255,255,0.4)' : '#fff';
  ctx.fillText(sent || n === 0 ? 'Message' : typed.slice(0, n) + (Math.floor(t * 3) % 2 ? '|' : ''), px + 56, iy + 40);
  ctx.restore();
}
function lockScreen(ctx, t) {
  // the last beat: a text arrives from the Mom outside while "Mom" is behind him
  const { px, py, pw } = phoneShell(ctx, t, Ph(11).s);
  ctx.fillStyle = '#eef2ff'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.font = '300 130px Poppins, sans-serif'; ctx.fillText('12:03', 540, py + 170);
  ctx.font = '400 30px Poppins, sans-serif'; ctx.fillText('1 bar', 540, py + 70);
  const a = clamp((t - C(11, 1).s + 0.1) / 0.18);
  ctx.save(); ctx.globalAlpha = a; const x = px + 24, y = py + 300 + 30 * (1 - a), w = pw - 48;
  ctx.font = '500 34px Poppins, sans-serif'; const lines = wrap(ctx, "The gate is locked. I can't get in. Where are you??", w - 60); const h = 120 + lines.length * 46;
  ctx.fillStyle = 'rgba(235,238,248,0.95)'; ctx.beginPath(); ctx.roundRect(x, y, w, h, 34); ctx.fill();
  ctx.fillStyle = '#2fbf5a'; ctx.beginPath(); ctx.roundRect(x + 28, y + 26, 54, 54, 14); ctx.fill();
  ctx.fillStyle = '#111'; ctx.textAlign = 'left'; ctx.font = '700 36px Poppins, sans-serif'; ctx.fillText('Mom', x + 100, y + 54);
  ctx.font = '400 28px Poppins, sans-serif'; ctx.fillStyle = '#666'; ctx.textAlign = 'right'; ctx.fillText('now', x + w - 30, y + 54);
  ctx.textAlign = 'left'; ctx.fillStyle = '#111'; ctx.font = '500 34px Poppins, sans-serif'; lines.forEach((ln, k) => ctx.fillText(ln, x + 30, y + 120 + k * 46));
  ctx.restore(); ctx.restore();
}
// red typewriter captions, up to three words; the other voices in white italics
const CAPS = [];
for (const ph of PH.phrases) for (const ch of ph.chunks) {
  const words = ch.text.split(' '); const groups = [];
  for (let k = 0; k < words.length; k += 3) groups.push(words.slice(k, k + 3).join(' '));
  const tot = groups.reduce((a, g) => a + g.length, 0); let s = ch.s;
  groups.forEach(g => { const d = (ch.e - ch.s) * g.length / tot; CAPS.push({ text: g, s, e: s + d, who: ph.who }); s += d; });
}
function captions(ctx, t) {
  let cur = null;
  for (let k = 0; k < CAPS.length; k++) { const c = CAPS[k], nx = CAPS[k + 1]; const hold = nx ? Math.min(nx.s, c.e + 0.35) : c.e + 0.35; if (t >= c.s && t < hold) cur = c; }
  if (!cur) return;
  const other = cur.who !== 'n', txt = cur.text;
  const n = Math.max(1, Math.ceil(txt.length * clamp((t - cur.s) / Math.max(0.12, (cur.e - cur.s) * 0.6))));
  ctx.save(); ctx.textBaseline = 'middle';
  ctx.font = `${other ? 'italic ' : ''}700 66px "FreeMono", "Courier 10 Pitch", monospace`;
  const x0 = W / 2 - ctx.measureText(txt).width / 2; ctx.textAlign = 'left';
  ctx.lineJoin = 'round'; ctx.lineWidth = 10; ctx.strokeStyle = 'rgba(0,0,0,0.9)'; ctx.strokeText(txt.slice(0, n), x0, 1470);
  ctx.fillStyle = other ? '#f2f0ff' : '#ff3b3b'; ctx.fillText(txt.slice(0, n), x0, 1470);
  ctx.restore();
}

// ---------- render ----------
const STINGS = [...KNOCKS, C(0, 1).s, Ph(2).s, C(2, 1).s + 0.3, C(3, 2).s, Ph(4).s, C(5, 1).s, C(6, 1).s, C(7, 1).s + 0.1, Ph(8).s, C(9, 1).s, C(11, 1).s];
window.renderFrame = function (n) {
  const t = n / 30; NOW = t;
  const sh = shotAt(t);
  if (sh.name === 'black') {
    outCtx.fillStyle = '#000'; outCtx.fillRect(0, 0, W, H);
    const z = 1 + 0.02 * (t - sh.t0); outCtx.save(); outCtx.translate(W / 2, 930); outCtx.scale(z, z); outCtx.translate(-W / 2, -930);
    bigText(outCtx, ['WHICH MOM', 'IS REAL?'], 760, clamp((t - sh.t0) / 0.3), 130);
    const tp = sh.t0 + 0.6;
    if (t >= tp) { bigText(outCtx, ['PART 4'], 1110, clamp((t - tp) / 0.25), 100); bigText(outCtx, ['FOLLOW TO FIND OUT'], 1220, clamp((t - tp - 0.1) / 0.25), 64, '#ff4a4a'); }
    outCtx.restore(); captions(outCtx, t);
    return outCv.toDataURL('image/jpeg', 0.93);
  }
  if (sh.name === 'phone') { chat(outCtx, t); captions(outCtx, t); return outCv.toDataURL('image/jpeg', 0.93); }
  if (sh.name === 'which' && t > C(11, 1).s - 0.2) { lockScreen(outCtx, t); captions(outCtx, t); return outCv.toDataURL('image/jpeg', 0.93); }
  let [cp, ct, fov] = setScene(sh, t);
  let shake = 0;
  for (const ts of STINGS) if (t >= ts && t < ts + 0.25) shake += 0.012 * (1 - (t - ts) / 0.25);
  if (sh.name === 'bell') shake += 0.006;
  camera.position.copy(cp).add(V(Math.sin(t * 69) * shake + 0.008 * Math.sin(t * 1.2), Math.cos(t * 51) * shake + 0.006 * Math.sin(t * 0.93), 0));
  camera.fov = fov; camera.updateProjectionMatrix(); camera.up.set(0, 1, 0); camera.lookAt(ct);
  for (const c of cards) { const m = c.mesh; m.rotation.set(0, Math.atan2(camera.position.x - m.position.x, camera.position.z - m.position.z), 0); }
  const inHall = ['knock', 'name', 'away', 'open', 'circle', 'circleUp', 'bell', 'clock', 'pa', 'paHall', 'doors'].includes(sh.name);
  applyLight('night', 'night', 0, inHall ? V(0, 0, -12) : V(RX, 0, RZ));
  if (inHall) hemi.intensity = 0.22;
  renderer.render(scene, camera);
  outCtx.drawImage(renderer.domElement, 0, 0);
  const g = outCtx.createRadialGradient(W / 2, H / 2, H * 0.25, W / 2, H / 2, H * 0.72);
  g.addColorStop(0, 'rgba(0,0,10,0)'); g.addColorStop(1, 'rgba(0,0,12,0.6)'); outCtx.fillStyle = g; outCtx.fillRect(0, 0, W, H);
  if (['knock', 'name', 'away'].includes(sh.name)) lockerMask(outCtx, 0);
  if (sh.name === 'open') lockerMask(outCtx, clamp((t - Ph(2).s) / 0.9));
  // "Mom" in the corridor: a phone light far down the dark doorway, coming closer
  if (sh.name === 'mom' || sh.name === 'which') {
    const u = clamp((t - Ph(10).s + 0.3) / 3.5), r = 30 + 220 * u, cx = 540 + 25 * Math.sin(t * 1.3);
    const gg = outCtx.createRadialGradient(cx, 930, 0, cx, 930, r); gg.addColorStop(0, `rgba(235,240,255,${0.85 * u + 0.1})`); gg.addColorStop(1, 'rgba(120,140,220,0)');
    outCtx.fillStyle = gg; outCtx.beginPath(); outCtx.arc(cx, 930, r, 0, 6.3); outCtx.fill();
  }
  if (t < 2.3) bigText(outCtx, ['IT KNOWS', 'MY NAME...'], 1010, t < 2.0 ? 1 : clamp((2.3 - t) / 0.3), 118);
  captions(outCtx, t);
  return outCv.toDataURL('image/jpeg', 0.93);
};
window.FRAMES = END;
window.ready = true;
