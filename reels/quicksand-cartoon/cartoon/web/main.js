// Quicksand cartoon short: toon world with ink hulls, billboard cartoon cards, keyframed cameras.
// window.renderFrame(f) draws frame f (30 fps). Everything is a pure function of f.
import * as THREE from 'three';
import { mergeVertices } from 'three/addons/utils/BufferGeometryUtils.js';
import * as P from './paint.js';
import { drawHero, drawBird, drawShoe, drawQuestion, drawSandFace } from './cast.js';

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
scene.fog = new THREE.Fog(0xffffff, 25, 260);
const LIGHTS = {
  golden: { sun: 0xffd9a0, si: 2.3, az: 35, el: 28, hs: 0xffe2bf, hg: 0x7a5a3a, hi: 1.05, fog: 0xf7c99a, top: 0x6fa6f0, hor: 0xffd3a0, bot: 0xd9a070, card: 0xfff3e2 },
  night: { sun: 0x9fb7ff, si: 1.2, az: -30, el: 40, hs: 0x6f86d8, hg: 0x2b2550, hi: 0.95, fog: 0x2a3f7a, top: 0x0c1840, hor: 0x2f4d8c, bot: 0x1a2048, card: 0xc9d6ff },
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
const SAND_R = 3.2;
const ground = add(new THREE.PlaneGeometry(400, 212), toon(0xffffff, P.grass(80)), scene, { ink: false, shadow: false });
at(ground, 0, 0, 94, -Math.PI / 2); ground.material.map.repeat.set(80, 42);
const farGround = add(new THREE.PlaneGeometry(400, 360), toon(0xffffff, P.grass(80)), scene, { ink: false, shadow: false });
at(farGround, 0, 0, -219, -Math.PI / 2);
const riverBed = add(new THREE.PlaneGeometry(400, 30), toon(0x2f6f9a), scene, { ink: false, shadow: false });
at(riverBed, 0, -0.6, -26, -Math.PI / 2);
// muddy rim + sand pit with live ripples
add(new THREE.RingGeometry(SAND_R - 0.05, SAND_R + 0.45, 64), toon(0xffffff, P.dirt(3)), scene, { ink: false, shadow: false }).rotation.x = -Math.PI / 2;
scene.children[scene.children.length - 1].position.y = 0.004;
const sandGeo = new THREE.CircleGeometry(SAND_R, 96, 0, Math.PI * 2);
// subdivide radially for ripples
const pitGeo = new THREE.RingGeometry(0.0, SAND_R, 96, 40);
const pit = add(pitGeo, toon(0xffffff, P.sand(true, 2)), scene, { ink: false, shadow: false });
pit.rotation.x = -Math.PI / 2; pit.position.y = 0.06; pit.receiveShadow = true;
const pitBase = pitGeo.attributes.position.array.slice();
function ripple(f, cx, cz, amp, calm) {
  const a = pitGeo.attributes.position.array;
  for (let i = 0; i < a.length; i += 3) {
    const x = pitBase[i], y = pitBase[i + 1]; // local plane coords (y local = -z world)
    const dx = x - cx, dz = -y - cz; const r = Math.hypot(dx, dz);
    const edge = Math.min(1, (SAND_R - Math.hypot(x, y)) / 0.6);
    let z = amp * Math.exp(-r * 0.9) * Math.sin(r * 9 - f * 0.35) + calm * 0.012 * Math.sin(x * 3 + f * 0.05) * Math.cos(y * 2.6 - f * 0.04);
    a[i + 2] = z * Math.max(0, edge);
  }
  pitGeo.attributes.position.needsUpdate = true; pitGeo.computeVertexNormals();
}
// river and its banks
const river = add(new THREE.PlaneGeometry(400, 26), toon(0xffffff, P.water(1)), scene, { ink: false, shadow: false });
at(river, 0, -0.12, -26, -Math.PI / 2); river.material.map.repeat.set(40, 3);
add(new THREE.PlaneGeometry(400, 3), toon(0xffffff, P.dirt(40)), scene, { ink: false, shadow: false }).position.set(0, 0.003, -12.4);
scene.children[scene.children.length - 1].rotation.x = -Math.PI / 2;
// reeds
const reedMat = toon(0x5c9b3a), reedTop = toon(0x7a4a2a);
for (let k = 0; k < 70; k++) {
  const r = Math.sin(k * 12.9898) * 43758.5453; const fr = r - Math.floor(r);
  const x = -18 + (k * 0.53) % 36 + fr * 0.4, z = -11.2 - fr * 1.6, h = 1.0 + fr * 0.9;
  const reed = add(new THREE.CylinderGeometry(0.018, 0.03, h, 5), reedMat, scene, { thin: true, shadow: false });
  at(reed, x, h / 2, z, 0, 0, (fr - 0.5) * 0.25);
  if (k % 2 === 0) at(add(new THREE.CapsuleGeometry(0.05, 0.22, 3, 6), reedTop, reed, { thin: true }), 0, h / 2, 0);
}
// pines, bushes, hills, mountains
function pine(x, z, s) {
  const g = new THREE.Group(); at(g, x, 0, z, 0, 0, 0, s); scene.add(g);
  at(add(new THREE.CylinderGeometry(0.12, 0.16, 1.2, 7), toon(0x7a4a2a), g), 0, 0.6, 0);
  for (let k = 0; k < 3; k++) at(add(new THREE.ConeGeometry(1.1 - k * 0.25, 1.5, 9), toon(k % 2 ? 0x2f8a4a : 0x3aa257), g), 0, 1.4 + k * 0.75, 0);
}
function bush(x, z, s, col = 0x4fae4a) { at(add(new THREE.IcosahedronGeometry(1, 2), toon(col), scene), x, s * 0.45, z, 0, 0, 0, [s * 1.2, s * 0.8, s]); }
[[-7, -6, 1.3], [-9.5, -3, 1.6], [-12, -8, 1.9], [-10, 3.5, 1.5], [-13, 6, 1.8], [-6, 6, 1.2], [7.5, 5, 1.4], [16, -9, 2.2], [-15, -2, 2.0], [20, 2, 2.4], [-20, 4, 2.3], [5, -9, 1.2]].forEach(a => pine(...a));
[[-4.8, -2.6, 0.9], [4.9, -3.2, 1.0], [-5.6, 2.4, 0.8], [6.2, 1.6, 0.7], [-3.2, -6.5, 0.8], [2.4, -7.2, 0.9]].forEach(a => bush(...a));
for (const [x, z, r, col] of [[-60, -90, 40, 0x58a548], [20, -110, 55, 0x4e9a44], [90, -95, 45, 0x5aa84c], [-120, -120, 60, 0x4a9442]]) {
  at(add(new THREE.SphereGeometry(r, 32, 16), toon(col), scene, { shadow: false }), x, -r * 0.55, z);
}
for (const [x, z, h] of [[-40, -190, 90], [30, -210, 120], [100, -200, 80]]) {
  at(add(new THREE.ConeGeometry(h * 0.7, h, 8), toon(0x7d84a8), scene, { shadow: false }), x, h / 2 - 5, z);
  at(add(new THREE.ConeGeometry(h * 0.25, h * 0.36, 8), toon(0xffffff), scene, { shadow: false }), x, h - 5 - h * 0.18 + 0.5, z);
}
const cloudTex = P.cloud();
for (const [x, y, z, s] of [[-50, 55, -200, 60], [40, 70, -230, 75], [110, 50, -180, 50], [-120, 65, -150, 55]]) {
  const m = new THREE.Mesh(new THREE.PlaneGeometry(s, s / 2), new THREE.MeshBasicMaterial({ map: cloudTex, transparent: true, depthWrite: false, fog: false }));
  m.position.set(x, y, z); scene.add(m);
}
// warning sign half-tilted at the pit edge (text on the +z face)
const signG = new THREE.Group(); at(signG, -3.0, 0, 0.9, 0, 0.35, -0.12); scene.add(signG);
at(add(new THREE.BoxGeometry(0.1, 1.5, 0.1), toon(0xffffff, P.planks()), signG), 0, 0.75, 0);
const signMats = Array(6).fill(toon(0xb07a46)); signMats[4] = toon(0xffffff, P.signBoard([['DANGER', 100], ['QUICKSAND', 82]]));
at(add(new THREE.BoxGeometry(1.1, 0.68, 0.06), signMats, signG), 0, 1.35, 0.06);
// drive-in screen with the B-movie poster
const screenG = new THREE.Group(); at(screenG, 12, 0, -6, 0, -0.5); scene.add(screenG);
for (const sx of [-2.6, 2.6]) at(add(new THREE.BoxGeometry(0.25, 3.0, 0.25), toon(0x6a4a3a), screenG), sx, 1.5, 0);
at(add(new THREE.BoxGeometry(5.8, 3.6, 0.25), toon(0x2a2a3a), screenG), 0, 4.5, -0.05);
const posterMesh = new THREE.Mesh(new THREE.PlaneGeometry(5.4, 3.6 * 5.4 / 5.4 * 0.95), new THREE.MeshBasicMaterial({ map: P.poster() }));
posterMesh.scale.set(1, 0.66 / 0.95 * 5.4 / 3.6 * 0.95, 1); at(posterMesh, 0, 4.5, 0.09); screenG.add(posterMesh);
for (let k = 0; k < 14; k++) { const bx = -2.8 + k * 0.43; at(add(new THREE.SphereGeometry(0.08, 8, 6), new THREE.MeshBasicMaterial({ color: 0xfff1a0 }), screenG, { thin: true }), bx, 6.4, 0.12); }

// ---------- diagram stage (x = 60): balance scale and cross-section tank ----------
const STAGE = 60;
const back = new THREE.Mesh(new THREE.PlaneGeometry(40, 20), new THREE.MeshBasicMaterial({ map: P.blueprint(), fog: false }));
at(back, STAGE + 5, 8, -4); scene.add(back);
const stageFloor = add(new THREE.PlaneGeometry(40, 16), toon(0x2a3b78), scene, { ink: false, shadow: false });
at(stageFloor, STAGE + 5, 0.01, 2, -Math.PI / 2);
// balance
const bal = new THREE.Group(); at(bal, STAGE, 0, 0); scene.add(bal);
at(add(new THREE.CylinderGeometry(0.12, 0.2, 2.2, 10), toon(0xc9a24a), bal), 0, 1.1, 0);
at(add(new THREE.CylinderGeometry(0.6, 0.7, 0.15, 16), toon(0xc9a24a), bal), 0, 0.075, 0);
const beam = new THREE.Group(); at(beam, 0, 2.25, 0); bal.add(beam);
at(add(new THREE.BoxGeometry(2.9, 0.12, 0.14), toon(0xe0b64e), beam), 0, 0, 0);
at(add(new THREE.SphereGeometry(0.14, 12, 8), toon(0xe0b64e), beam), 0, 0, 0);
const pans = [];
const sandBoxMats = Array(6).fill(new THREE.MeshBasicMaterial({ map: P.sand(true, 1) })); sandBoxMats[4] = new THREE.MeshBasicMaterial({ map: P.label('QUICKSAND', '#e0a868', '#3b1d3f', 512, 512, 86) });
const youBoxMats = Array(6).fill(new THREE.MeshBasicMaterial({ color: 0xff8a2a })); youBoxMats[4] = new THREE.MeshBasicMaterial({ map: P.label('YOU', '#ff8a2a', '#ffffff', 512, 512, 170) });
for (const [sx, mats] of [[-1.3, sandBoxMats], [1.3, youBoxMats]]) {
  const pan = new THREE.Group(); beam.add(pan); pan.position.set(sx, 0, 0);
  at(add(new THREE.CylinderGeometry(0.012, 0.012, 0.9, 4), toon(0x888888), pan, { thin: true }), 0, -0.45, 0);
  at(add(new THREE.CylinderGeometry(0.6, 0.5, 0.1, 16), toon(0xe0b64e), pan), 0, -0.9, 0);
  at(add(new THREE.BoxGeometry(0.9, 0.9, 0.9), mats, pan), 0, -0.4, 0);
  pans.push(pan);
}
const flag = new THREE.Mesh(new THREE.PlaneGeometry(1.1, 0.7), new THREE.MeshBasicMaterial({ map: P.label('2x', '#ffd23f', '#3b1d3f', 512, 320, 230), transparent: true }));
scene.add(flag);
// tank (x = STAGE + 10)
const TANK = STAGE + 10, TANK_TOP = 2.4;
const tankBack = add(new THREE.BoxGeometry(3.4, TANK_TOP, 0.3), toon(0xffffff, P.sand(true, 1)), scene);
at(tankBack, TANK, TANK_TOP / 2, -0.75);
for (const sx of [-1.75, 1.75]) at(add(new THREE.BoxGeometry(0.12, TANK_TOP + 0.2, 1.6), toon(0x8fa3d6), scene), TANK + sx, TANK_TOP / 2, 0);
at(add(new THREE.BoxGeometry(3.6, 0.15, 1.6), toon(0x8fa3d6), scene), TANK, 0.07, 0);
const tankFront = new THREE.Mesh(new THREE.BoxGeometry(3.4, TANK_TOP, 1.3),
  new THREE.MeshToonMaterial({ color: 0xe6b072, map: P.sand(true, 1), gradientMap: grad, transparent: true, opacity: 0.55, depthWrite: false }));
at(tankFront, TANK, TANK_TOP / 2, 0); tankFront.renderOrder = 5; scene.add(tankFront);
const waistLine = new THREE.Group(); scene.add(waistLine);
for (let k = 0; k < 9; k++) at(add(new THREE.BoxGeometry(0.22, 0.05, 0.02), new THREE.MeshBasicMaterial({ color: 0xffffff }), waistLine, { ink: false }), -1.6 + k * 0.4, 0, 0);
waistLine.position.set(TANK, TANK_TOP, 0.67);
const drops = [];
for (let k = 0; k < 10; k++) { const d = new THREE.Mesh(new THREE.SphereGeometry(0.05, 10, 8), new THREE.MeshBasicMaterial({ color: 0x6fd0ff })); d.renderOrder = 6; scene.add(d); drops.push(d); }

// ---------- sand bubbles ----------
const bubbles = [];
for (let k = 0; k < 10; k++) { const b = add(new THREE.SphereGeometry(1, 12, 8), toon(0xb07a46), scene, { thin: true, shadow: false }); bubbles.push(b); }
// ---------- ghost car ----------
const car = new THREE.Group(); scene.add(car);
const carRed = toon(0xe23b4e), carGlass = toon(0x9fe0ff), tire = toon(0x2a2a33);
at(add(new THREE.BoxGeometry(3.6, 0.7, 1.7), carRed, car), 0, 0.55, 0);
at(add(new THREE.BoxGeometry(2.0, 0.6, 1.5), carGlass, car), -0.2, 1.15, 0);
for (const [x, z] of [[-1.2, 0.85], [1.2, 0.85], [-1.2, -0.85], [1.2, -0.85]]) at(add(new THREE.CylinderGeometry(0.35, 0.35, 0.25, 14), tire, car), x, 0.3, z, Math.PI / 2);

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
const hero = new Card(drawHero);
const bird = new Card(drawBird, 0.5, 0.3);
const shoe = new Card(drawShoe, 0.5, 0.3);
const qmark = new Card(drawQuestion, 0.9, 0.54);
// sulking face on the sand
const faceCv = document.createElement('canvas'); faceCv.width = faceCv.height = 1000;
const faceTex = new THREE.CanvasTexture(faceCv); faceTex.colorSpace = THREE.SRGBColorSpace;
const sandFace = new THREE.Mesh(new THREE.PlaneGeometry(5.2, 5.2), new THREE.MeshBasicMaterial({ map: faceTex, transparent: true, depthWrite: false }));
sandFace.rotation.x = -Math.PI / 2; sandFace.position.set(0, 0.13, 0); scene.add(sandFace);
let faceKey = '';

// ---------- story ----------
const SH = [
  ['hook', 0], ['wide', 93], ['soup', 165], ['pull', 228], ['stuck', 279], ['harder', 321], ['car', 360], ['kick', 427],
  ['movie', 503], ['secret', 565], ['dense', 612], ['waist', 705], ['stop', 778], ['wiggle', 824], ['float', 874], ['safe', 936], ['panic', 1033],
];
const END = 1093;
function shotAt(f) { let i = 0; for (let k = 0; k < SH.length; k++) if (f >= SH[k][1]) i = k; return { name: SH[i][0], f0: SH[i][1], f1: i + 1 < SH.length ? SH[i + 1][1] : END, i }; }
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const sstep = x => { x = clamp(x); return x * x * x * (x * (x * 6 - 15) + 10); };
const easeOut = x => 1 - Math.pow(1 - clamp(x), 3);
const back_ = x => { x = clamp(x); const c = 1.7; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); };
const V = (x, y, z) => new THREE.Vector3(x, y, z);
function keys(f, ks) { // ks: [[frame, pos, target, fov, roll]]
  if (f <= ks[0][0]) return ks[0];
  for (let k = 0; k < ks.length - 1; k++) {
    const a = ks[k], b = ks[k + 1];
    if (f <= b[0]) { const t = sstep((f - a[0]) / (b[0] - a[0])); return [f, a[1].clone().lerp(b[1], t), a[2].clone().lerp(b[2], t), a[3] + (b[3] - a[3]) * t, (a[4] || 0) + ((b[4] || 0) - (a[4] || 0)) * t]; }
  }
  return ks[ks.length - 1];
}

// hero state: sink depth (m), x position, tilt
function sinkAt(f) {
  const pts = [[0, 0.1], [18, 0.12], [56, 0.14], [64, 0.32], [228, 0.48], [321, 0.52], [360, 0.55], [430, 0.55], [442, 0.7], [462, 0.7], [474, 0.84], [490, 0.84], [500, 0.98], [874, 0.98]];
  for (let k = 0; k < pts.length - 1; k++) { const [a, va] = pts[k], [b, vb] = pts[k + 1]; if (f <= b) return va + (vb - va) * sstep((f - a) / (b - a)); }
  return 0.98;
}
function heroPose(f, s) {
  const blink = ((f + 50) % 97) < 3;
  const p = { expr: 'smile', arms: 'hang', blink, kick: 0, sweat: false, oneShoe: f >= 874 };
  if (f < 56) { p.expr = 'worry'; p.kick = Math.sin(f * 0.15) * 0.3; }
  else if (f < 93) p.expr = 'shock', p.arms = 'up';
  else if (f < 165) { p.expr = f < 138 ? 'shock' : 'panic'; p.arms = 'hang'; }
  else if (f < 228) { p.expr = 'shock'; p.arms = 'hang'; }
  else if (f < 321) { p.expr = 'panic'; p.arms = 'pull'; p.sweat = true; }
  else if (f < 360) { p.expr = 'strain'; p.arms = 'pull'; p.sweat = true; }
  else if (f < 427) { p.expr = 'strain'; p.arms = 'lift'; }
  else if (f < 503) { p.expr = 'panic'; p.arms = 'up'; p.kick = Math.sin(f * 0.5); p.sweat = true; }
  else if (f < 612) { p.expr = 'puzzled'; p.arms = 'hang'; }
  else if (f < 778) { p.expr = f < 760 ? 'shock' : 'relief'; p.arms = f < 740 ? 'up' : 'spread'; }
  else if (f < 824) { p.expr = 'calm'; p.arms = 'hang'; }
  else if (f < 874) { p.expr = 'calm'; p.arms = 'spread'; p.kick = Math.sin(f * 0.18) * 0.6; }
  else if (f < 936) { p.expr = f < 898 ? 'calm' : 'smile'; p.arms = 'spread'; }
  else if (f < 1033) { p.expr = 'smile'; p.arms = 'wave'; p.wave = f * 0.4; }
  else { p.expr = f < 1066 ? 'smile' : 'shock'; p.arms = f < 1066 ? 'hips' : 'head'; }
  if (p.blink && p.expr !== 'relief') p.blink = true; else p.blink = false;
  p.wave = p.wave ? Math.round(p.wave * 10) / 10 : 0; p.kick = Math.round(p.kick * 20) / 20;
  return p;
}

function camFor(sh, f) {
  const H0 = V(0, 0, 0); // eslint-disable-line
  switch (sh.name) {
    case 'hook': return keys(f, [[0, V(0.55, 0.62, 2.9), V(0, 0.85, 0), 40, 0], [92, V(0.35, 0.55, 2.25), V(0, 0.75, 0), 40, 0]]);
    case 'wide': return keys(f, [[93, V(0.9, 1.4, 3.6), V(0, 0.9, 0), 42, 0], [140, V(3.2, 5.2, 13.5), V(0, 0.4, -4), 45, 0], [164, V(3.4, 5.4, 14), V(0, 0.4, -4), 45, 0]]);
    case 'soup': return keys(f, [[165, V(1.6, 1.15, 2.9), V(0, 0.5, 0), 42, 0], [227, V(1.4, 1.05, 2.6), V(0, 0.47, 0), 42, 0]]);
    case 'pull': return keys(f, [[228, V(-0.6, 1.25, 2.4), V(0, 0.75, 0), 40, 0], [278, V(-0.5, 1.2, 2.2), V(0, 0.72, 0), 40, 0]]);
    case 'stuck': return keys(f, [[279, V(0.9, 0.95, 2.2), V(0, 0.35, 0), 40, 0], [320, V(0.8, 0.9, 2.0), V(0, 0.33, 0), 40, 0]]);
    case 'harder': return keys(f, [[321, V(0, 1.2, 2.3), V(0, 1.0, 0), 40, 0], [345, V(0, 1.2, 1.6), V(0, 1.0, 0), 40, 3], [359, V(0, 1.2, 1.5), V(0, 1.0, 0), 40, 3]]);
    case 'car': return keys(f, [[360, V(1.4, 1.8, 7.4), V(0, 1.45, 0), 44, 0], [426, V(1.2, 1.75, 6.9), V(0, 1.45, 0), 44, 0]]);
    case 'kick': return keys(f, [[427, V(3.0, 0.95, 2.3), V(0, 0.55, 0), 40, 0], [502, V(2.6, 0.9, 2.0), V(0, 0.45, 0), 40, 0]]);
    case 'movie': {
      const sp = screenG.position; const tgt = V(sp.x, 4.4, sp.z);
      return keys(f, [[503, V(1.5, 1.6, 4.5), V(1.0, 1.4, 0), 44, 0], [511, V(3.0, 2.2, 4.8), tgt, 44, -4], [564, V(4.0, 2.6, 4.0), tgt, 44, 0]]);
    }
    case 'secret': return keys(f, [[565, V(0, 0.95, 3.0), V(0, 0.55, 0), 40, 0], [611, V(0, 0.9, 1.9), V(0, 0.6, 0), 40, 4]]);
    case 'dense': return keys(f, [[612, V(STAGE, 2.1, 10.6), V(STAGE, 1.8, 0), 40, 0], [704, V(STAGE + 0.2, 2.0, 10.0), V(STAGE, 1.75, 0), 40, 0]]);
    case 'waist': return keys(f, [[705, V(TANK, 2.3, 6.2), V(TANK, 2.1, 0), 40, 0], [777, V(TANK, 2.25, 5.6), V(TANK, 2.0, 0), 40, 0]]);
    case 'stop': return keys(f, [[778, V(0.4, 1.0, 2.9), V(0, 0.55, 0), 40, 0], [823, V(0.3, 0.95, 2.6), V(0, 0.55, 0), 40, 0]]);
    case 'wiggle': return keys(f, [[824, V(TANK, 2.0, 5.6), V(TANK, 1.8, 0), 40, 0], [873, V(TANK, 1.95, 5.2), V(TANK, 1.75, 0), 40, 0]]);
    case 'float': return keys(f, [[874, V(3.2, 1.6, 2.6), V(0.2, 0.2, 0.4), 42, 0], [935, V(3.6, 1.5, 5.6), V(1.5, 0.7, 3.4), 42, 0]]);
    case 'safe': return keys(f, [[936, V(0.9, 4.8, 9.8), V(0.3, 0.4, 0.8), 44, 0], [1032, V(0.9, 4.5, 9.2), V(0.3, 0.4, 0.8), 44, 0]]);
    case 'panic': return keys(f, [[1033, V(1.4, 1.7, 7.6), V(1.5, 1.2, 3.6), 42, 0], [1092, V(1.55, 1.6, 6.3), V(1.6, 1.3, 3.6), 42, 0]]);
  }
  return [f, V(0, 1, 4), H0, 40, 0];
}

function flashAt(f) {
  for (const c of [503, 612, 705, 778, 824, 874]) { const d = f - c; if (d >= 0 && d < 6) return 0.6 * (1 - d / 6); }
  return 0;
}
const flashEl = document.createElement('div');
Object.assign(flashEl.style, { position: 'fixed', inset: 0, background: '#fff', opacity: 0, pointerEvents: 'none' }); document.body.appendChild(flashEl);
// flash/vignette are applied in the frame grab by drawing on a 2D overlay of the WebGL canvas
const outCv = document.createElement('canvas'); outCv.width = W; outCv.height = H; const outCtx = outCv.getContext('2d');

window.renderFrame = function (f) {
  const sh = shotAt(f);
  const diagram = ['dense', 'waist', 'wiggle'].includes(sh.name);
  const nightBlend = sh.name === 'secret' ? clamp((f - 565) / 10) : diagram ? 1 : 0;
  const s = sinkAt(f);
  // hero placement
  let hx = 0, hy = -s, hz = 0, tilt = 0;
  if (sh.name === 'stuck') { const tug = [285, 298, 311].reduce((a, t) => a + Math.max(0, 1 - Math.abs(f - t) / 4), 0); hy += 0.035 * tug; }
  if (f >= 874 && f < 936) {
    const u = (f - 874) / 62;
    tilt = -1.25 * sstep(u / 0.25) * (1 - sstep((u - 0.82) / 0.18));
    hy = -0.98 * (1 - sstep((u - 0.05) / 0.45)) + 0.0;
    const mv = sstep((u - 0.35) / 0.55); hx = 1.6 * mv; hz = 3.6 * mv;
    if (tilt < -0.2) hy = Math.max(hy, -0.25);
  }
  if (f >= 936) { hx = 1.6; hy = 0; hz = 3.6; }
  if (diagram) {
    if (sh.name === 'dense') { hx = 9999; }
    else {
      const floatY = TANK_TOP - 0.98;
      let y = floatY;
      if (sh.name === 'waist') { const u = (f - 705) / 60; y = floatY + (TANK_TOP - floatY) * (1 - sstep(u)) + 0.12 * Math.exp(-Math.max(0, u - 0.8) * 6) * Math.sin(Math.max(0, u - 0.8) * 30); }
      hx = TANK; hy = y; hz = 0;
    }
  }
  hero.set(heroPose(f, s));
  hero.mesh.position.set(hx, hy, hz);
  // camera
  let [, cp, ct, fov, roll] = camFor(sh, f);
  if (sh.name === 'float') { ct = V(hx, Math.max(0.2, hy + 0.5), hz); cp = ct.clone().add(V(2.4, 1.1, 2.6)); }
  const local = f - sh.f0;
  let shake = 0;
  if (sh.name === 'hook' && f >= 60) shake = 0.03 * Math.exp(-(f - 60) / 6);
  if (sh.name === 'pull') shake = 0.012;
  if (sh.name === 'kick') shake = [442, 474, 500].reduce((a, t) => a + (f >= t ? 0.025 * Math.exp(-(f - t) / 4) : 0), 0);
  if (sh.name === 'panic' && f >= 1066) shake = 0.02 * Math.exp(-(f - 1066) / 5);
  const creep = 0.015 * Math.sin(local * 0.05);
  camera.position.copy(cp).add(V(Math.sin(f * 2.3) * shake + creep, Math.cos(f * 1.7) * shake, 0));
  camera.fov = fov; camera.updateProjectionMatrix();
  camera.up.set(0, 1, 0); camera.lookAt(ct);
  camera.rotateZ(THREE.MathUtils.degToRad(roll || 0));
  // billboards
  for (const c of cards) { const m = c.mesh; m.rotation.set(0, Math.atan2(camera.position.x - m.position.x, camera.position.z - m.position.z), 0); }
  if (tilt) { hero.mesh.rotation.x = tilt; }
  // lights
  const center = diagram ? V(STAGE + 5, 1, 0) : sh.name === 'movie' ? screenG.position.clone() : V(hx, 0, hz);
  applyLight('golden', 'night', nightBlend, center);
  // sand ripples
  const amp = f < 60 ? 0.02 : f < 503 ? 0.05 : f < 778 ? 0.03 : f < 874 ? 0.01 : 0.004;
  ripple(f, f < 874 ? hx : 0, 0, amp, 1);
  river.material.map.offset.x = f * 0.002;
  bubbles.forEach((b, k) => {
    const on = f >= 150 && f < 503;
    const ph = ((f * (0.03 + 0.01 * (k % 3)) + k * 0.37) % 1);
    const a = k * 2.399, r = 0.35 + 0.45 * ((k * 0.618) % 1);
    b.visible = on && ph < 0.85;
    b.position.set(hx + r * Math.cos(a), 0.06, r * Math.sin(a) + 0.15);
    b.scale.setScalar(0.07 * Math.sin(Math.PI * ph / 0.85) + 0.001);
  });
  // bird flies off on "alone"
  if (f >= 128 && f < 200) { const u = (f - 128) / 40; bird.mesh.visible = true; bird.set({ flap: Math.round((f * 0.9) % 6.28 * 10) / 10 }); bird.mesh.position.set(-4 + u * 8, 1.2 + u * 6, -10.5 + u * 2); }
  else bird.mesh.visible = false;
  // ghost car lifted over his head
  car.visible = sh.name === 'car';
  if (car.visible) { const u = (f - 360) / 30; const k = back_(u); car.position.set(-0.05, 1.84 + hy + 0.0 * k - 0.04 * Math.max(0, Math.sin((f - 405) * 0.5)) * (f > 405 ? 1 : 0), 0); car.rotation.set(0, 0.5, 0.06 * Math.sin(f * 0.2)); car.scale.setScalar(0.7 * k + 0.001); }
  // question mark
  qmark.mesh.visible = sh.name === 'secret' && f > 575;
  if (qmark.mesh.visible) { qmark.set({}); qmark.mesh.position.set(0.3, 1.6 + hy + 0.05 * Math.sin(f * 0.3), 0.1); qmark.mesh.scale.setScalar(back_((f - 575) / 8)); }
  // balance: tips on "twice"
  const tipT = clamp((f - 640) / 14);
  const ang = -0.32 * back_(tipT) * (sh.name === 'dense' ? 1 : 0) + 0.02 * Math.sin(f * 0.15) * (1 - tipT);
  beam.rotation.z = -ang;
  pans.forEach(p => p.rotation.z = ang);
  flag.visible = sh.name === 'dense' && f > 648;
  if (flag.visible) { const k = back_((f - 648) / 8); flag.position.set(STAGE - 1.3, 3.3 + 0.05 * Math.sin(f * 0.2), 0.6); flag.scale.setScalar(k + 0.001); }
  waistLine.visible = sh.name === 'waist' && f > 740;
  drops.forEach((d, k) => {
    d.visible = sh.name === 'wiggle';
    const ph = ((f - 824) * 0.02 + k / drops.length) % 1;
    d.position.set(TANK + (k % 2 ? 0.2 : -0.2) + 0.05 * Math.sin(k + f * 0.1), TANK_TOP - 0.1 - ph * 0.9, 0.35);
  });
  // shoe: left in the sand, burped out in the last shot, lands on his head on "can"
  if (f >= 1046) {
    shoe.mesh.visible = true; shoe.set({});
    const u = clamp((f - 1046) / 20); const p0 = V(0.2, 0.1, 0.4), p1 = V(1.6, 1.8, 3.62);
    const pos = p0.clone().lerp(p1, u); pos.y += Math.sin(Math.PI * u) * 2.2 * (u < 1 ? 1 : 0);
    shoe.mesh.position.copy(pos); shoe.mesh.rotation.z = (1 - u) * 6;
  } else shoe.mesh.visible = false;
  // sulking sand face
  sandFace.visible = f >= 936;
  if (sandFace.visible) {
    const mood = f >= 1040 && f < 1056 ? 1 : 0; const k = `${mood}`;
    if (k !== faceKey) { drawSandFace(faceCv.getContext('2d'), { mood }); faceTex.needsUpdate = true; faceKey = k; }
    sandFace.material.opacity = clamp((f - 936) / 8);
  }
  renderer.render(scene, camera);
  // overlay: flash + vignette
  outCtx.drawImage(renderer.domElement, 0, 0);
  const fl = flashAt(f);
  if (fl > 0) { outCtx.fillStyle = `rgba(255,255,255,${fl})`; outCtx.fillRect(0, 0, W, H); }
  const g = outCtx.createRadialGradient(W / 2, H / 2, H * 0.35, W / 2, H / 2, H * 0.75);
  g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(20,0,30,0.35)'); outCtx.fillStyle = g; outCtx.fillRect(0, 0, W, H);
  return outCv.toDataURL('image/jpeg', 0.93);
};
window.FRAMES = END;
window.ready = true;
