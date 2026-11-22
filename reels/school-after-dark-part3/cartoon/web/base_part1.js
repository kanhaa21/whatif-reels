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

