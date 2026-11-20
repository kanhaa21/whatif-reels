// Black-car cartoon reel: toon street with ink hulls, billboard cartoon cards, keyframed cameras, burned-in captions.
// window.renderFrame(f) draws frame f (30 fps). Everything is a pure function of f.
import * as THREE from 'three';
import { mergeVertices } from 'three/addons/utils/BufferGeometryUtils.js';
import * as P from './paint.js';
import { drawGuy, drawNaan, drawStar, drawSign, drawQuestion } from './cast.js';

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
  day: { sun: 0xfff0d6, si: 2.4, az: 30, el: 42, hs: 0xdcecff, hg: 0x8a7a6a, hi: 1.1, fog: 0xbfdcff, top: 0x4f93ea, hor: 0xcfe6ff, bot: 0xa0b0c0, card: 0xffffff },
  hot: { sun: 0xffc27a, si: 2.9, az: 10, el: 65, hs: 0xffd2a0, hg: 0x8a5a3a, hi: 1.15, fog: 0xffc890, top: 0xff9a4a, hor: 0xffd59a, bot: 0xd99060, card: 0xfff0e0 },
  golden: { sun: 0xffd9a0, si: 2.3, az: 35, el: 24, hs: 0xffe2bf, hg: 0x7a5a3a, hi: 1.05, fog: 0xf7c99a, top: 0x6fa6f0, hor: 0xffd3a0, bot: 0xd9a070, card: 0xfff3e2 },
}
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
const grass = add(new THREE.PlaneGeometry(400, 400), toon(0xffffff, P.grass(80)), scene, { ink: false, shadow: false });
at(grass, 0, -0.01, 0, -Math.PI / 2);
const road = add(new THREE.PlaneGeometry(400, 8), toon(0xffffff, P.asphalt(1)), scene, { ink: false, shadow: false });
at(road, 0, 0.0, 0, -Math.PI / 2); road.material.map.repeat.set(60, 1.2);
for (let k = -40; k <= 40; k++) at(add(new THREE.BoxGeometry(1.6, 0.02, 0.16), new THREE.MeshBasicMaterial({ color: 0xf4f0e0 }), scene, { ink: false, shadow: false }), k * 3.4, 0.01, 0);
const walk = add(new THREE.BoxGeometry(400, 0.16, 5), toon(0xffffff, P.pavement(1)), scene, { ink: false, shadow: false });
at(walk, 0, 0.08, -6.5); walk.material.map.repeat.set(80, 1);
const walk2 = add(new THREE.BoxGeometry(400, 0.16, 3), toon(0xffffff, P.pavement(1)), scene, { ink: false, shadow: false });
at(walk2, 0, 0.08, 5.5); walk2.material.map.repeat.set(80, 0.6);
const FAC = ['#f2b5a0', '#a8d8c8', '#f6d38a', '#b9b4f0', '#f0a7c4', '#9fc6f2'];
for (let k = 0; k < 26; k++) {
  const x = -70 + k * 5.6, h = 7 + ((k * 37) % 11), col = FAC[k % FAC.length];
  const mats = Array(6).fill(toon(new THREE.Color(col).multiplyScalar(0.85))); mats[4] = toon(0xffffff, P.facade(col)); mats[4].map.repeat.set(1, h / 10);
  at(add(new THREE.BoxGeometry(5.2, h, 5), mats, scene), x, h / 2, -12);
  at(add(new THREE.BoxGeometry(5.5, 0.4, 5.3), toon(0x6a5a7a), scene), x, h + 0.2, -12);
}
function tree(x, z, s = 1) {
  at(add(new THREE.CylinderGeometry(0.12, 0.16, 2.2, 7), toon(0x7a4a2a), scene), x, 1.1 * s, z, 0, 0, 0, s);
  at(add(new THREE.IcosahedronGeometry(1.1, 2), toon(0x4fae4a), scene), x, 2.8 * s, z, 0, 0, 0, s);
}
for (let k = -8; k <= 8; k++) tree(k * 7 + 2.5, -8.2, 1);
for (const [x, z, r, col] of [[-60, -120, 40, 0x58a548], [40, -140, 55, 0x4e9a44], [110, -120, 45, 0x5aa84c]]) at(add(new THREE.SphereGeometry(r, 32, 16), toon(col), scene, { shadow: false }), x, -r * 0.5, z);
const cloudTex = P.cloud();
for (const [x, y, z, s] of [[-50, 60, -200, 60], [40, 75, -230, 75], [110, 55, -180, 50], [-120, 70, -150, 55]]) {
  const m = new THREE.Mesh(new THREE.PlaneGeometry(s, s / 2), new THREE.MeshBasicMaterial({ map: cloudTex, transparent: true, depthWrite: false, fog: false })); m.position.set(x, y, z); scene.add(m);
}
// sun disc (heat shots)
const sunDisc = new THREE.Mesh(new THREE.CircleGeometry(6, 32), new THREE.MeshBasicMaterial({ color: 0xfff2a8, fog: false }));
scene.add(sunDisc);

// ---------- cars ----------
function makeCar(col, glass = 0x6a8fb8, o = {}) {
  const g = new THREE.Group(); scene.add(g);
  const sh = new THREE.Shape();
  sh.moveTo(-2.2, 0.35); sh.lineTo(2.25, 0.35); sh.quadraticCurveTo(2.35, 0.8, 2.1, 0.95); sh.lineTo(0.9, 1.05);
  sh.quadraticCurveTo(0.5, 1.55, 0.0, 1.58); sh.lineTo(-1.0, 1.58); sh.quadraticCurveTo(-1.5, 1.5, -1.8, 1.05); sh.lineTo(-2.2, 1.0); sh.closePath();
  const body = new THREE.ExtrudeGeometry(sh, { depth: 1.7, bevelEnabled: true, bevelThickness: 0.08, bevelSize: 0.06, bevelSegments: 2, curveSegments: 10 });
  body.translate(0, 0, -0.85);
  const paint = o.mat || toon(col, null, { emissive: 0x000000 });
  const b = add(body, paint, g); b.userData.paint = paint;
  g.userData.paint = paint;
  // windows (both sides) + windscreen
  const ws = new THREE.Shape(); ws.moveTo(0.75, 1.08); ws.quadraticCurveTo(0.42, 1.48, 0.0, 1.5); ws.lineTo(-0.95, 1.5); ws.quadraticCurveTo(-1.35, 1.43, -1.6, 1.08); ws.closePath();
  const glassMat = new THREE.MeshToonMaterial({ color: glass, gradientMap: grad, transparent: true, opacity: 0.55 });
  for (const z of [0.94, -0.94]) { const w = new THREE.Mesh(new THREE.ShapeGeometry(ws), glassMat); w.position.z = z; w.renderOrder = 3; g.add(w); }
  g.userData.glass = glassMat;
  for (const [x, z] of [[-1.35, 0.9], [1.4, 0.9], [-1.35, -0.9], [1.4, -0.9]]) {
    at(add(new THREE.CylinderGeometry(0.4, 0.4, 0.3, 16), toon(0x22222a), g), x, 0.4, z, Math.PI / 2);
    at(add(new THREE.CylinderGeometry(0.2, 0.2, 0.32, 10), toon(0xc8ccd8), g, { thin: true }), x, 0.4, z, Math.PI / 2);
  }
  for (const z of [0.55, -0.55]) at(add(new THREE.BoxGeometry(0.08, 0.14, 0.4), new THREE.MeshBasicMaterial({ color: 0xfff6c0 }), g, { thin: true }), 2.32, 0.75, z);
  // gloss streak
  const streak = new THREE.Mesh(new THREE.PlaneGeometry(2.6, 0.06), new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: o.gloss || 0.0 }));
  at(streak, 0.1, 0.86, 0.94); g.add(streak); g.userData.streak = streak;
  return g;
}
const BLACK = 0x1d1e26;
const blackCar = makeCar(BLACK, 0x55708f, { gloss: 0.55 });
const silverCar = makeCar(0xc4cad6, 0x6a8fb8, { gloss: 0.3 });
const whiteCar = makeCar(0xf6f6f8, 0x6a8fb8, { gloss: 0.3 });
const redCar = makeCar(0xe23b4e);
// thermometers above the roofs
function thermo() {
  const g = new THREE.Group(); scene.add(g);
  at(add(new THREE.CylinderGeometry(0.17, 0.17, 1.6, 12), new THREE.MeshToonMaterial({ color: 0xffffff, gradientMap: grad, transparent: true, opacity: 0.6 }), g), 0, 0.8, 0);
  at(add(new THREE.SphereGeometry(0.22, 16, 10), toon(0xe0302f), g), 0, 0, 0);
  const fill = add(new THREE.CylinderGeometry(0.12, 0.12, 1, 10), new THREE.MeshBasicMaterial({ color: 0xff2a2a }), g, { ink: false }); fill.renderOrder = 6; g.userData.fill = fill;
  return g;
}
const thermoB = thermo(), thermoS = thermo();
// swirl decals on doors
const swirlTex = P.swirls();
function swirlDecal(car) {
  const m = new THREE.Mesh(new THREE.PlaneGeometry(3.2, 0.62), new THREE.MeshBasicMaterial({ map: swirlTex, transparent: true, opacity: 0, depthWrite: false }));
  at(m, 0.0, 0.66, 0.95); m.renderOrder = 4; car.add(m); return m;
}
const swirlB = swirlDecal(blackCar), swirlS = swirlDecal(silverCar); swirlS.position.z = -0.95; swirlS.rotation.y = Math.PI;
// wash bucket
const bucket = new THREE.Group(); scene.add(bucket);
at(add(new THREE.CylinderGeometry(0.28, 0.22, 0.5, 16), toon(0x3f8fe0), bucket), 0, 0.25, 0);
at(add(new THREE.CylinderGeometry(0.25, 0.25, 0.04, 16), new THREE.MeshBasicMaterial({ color: 0xffffff }), bucket, { ink: false }), 0, 0.47, 0);
// building shadow over the road (safety scene)
const shade = new THREE.Mesh(new THREE.PlaneGeometry(9, 8), new THREE.MeshBasicMaterial({ color: 0x0a0c20, transparent: true, opacity: 0.55, depthWrite: false }));
at(shade, 36, 0.03, 0, -Math.PI / 2); scene.add(shade);
// heat blobs and steam
const blobs = [];
for (let k = 0; k < 14; k++) { const b = new THREE.Mesh(new THREE.SphereGeometry(1, 10, 8), new THREE.MeshBasicMaterial({ color: 0xff8a3a, transparent: true, opacity: 0.35, depthWrite: false })); scene.add(b); blobs.push(b); }

// ---------- cards ----------
class Card {
  constructor(draw, h = 2.25, w = 1.35, cw = 600, ch = 1000) {
    this.draw = draw; this.cv = document.createElement('canvas'); this.cv.width = cw; this.cv.height = ch;
    this.ctx = this.cv.getContext('2d'); this.tex = new THREE.CanvasTexture(this.cv); this.tex.colorSpace = THREE.SRGBColorSpace;
    const g = new THREE.PlaneGeometry(w, h); g.translate(0, h / 2, 0);
    this.mesh = new THREE.Mesh(g, new THREE.MeshBasicMaterial({ map: this.tex, alphaTest: 0.5, side: THREE.DoubleSide }));
    this.mesh.castShadow = true;
    this.mesh.customDepthMaterial = new THREE.MeshDepthMaterial({ depthPacking: THREE.RGBADepthPacking, map: this.tex, alphaTest: 0.5 });
    this.key = null; scene.add(this.mesh); cards.push(this); this.bill = true;
  }
  set(p) { const k = JSON.stringify(p); if (k !== this.key) { this.draw(this.ctx, p); this.tex.needsUpdate = true; this.key = k; } }
}
const guy = new Card(drawGuy);
const driver = new Card(drawGuy, 1.6, 0.96);
const naan = new Card(drawNaan, 0.75, 0.45);
const sign = new Card(drawSign, 2.6, 1.56);
const qmark = new Card(drawQuestion, 1.2, 0.72);
const stars = []; for (let k = 0; k < 6; k++) stars.push(new Card(drawStar, 0.5, 0.3));

// ---------- story ----------
const END = 1083;
const SH = [
  ['hook', 0], ['watch', 58], ['cool', 103], ['oneday', 148], ['p1', 193], ['thermo', 238], ['tandoor', 346], ['p2', 418], ['wash', 443],
  ['silver', 526], ['blackdoor', 562], ['p3', 625], ['road', 650], ['cool2', 832], ['touch', 868], ['end', 940],
];
function shotAt(f) { let i = 0; for (let k = 0; k < SH.length; k++) if (f >= SH[k][1]) i = k; return { name: SH[i][0], f0: SH[i][1], f1: i + 1 < SH.length ? SH[i + 1][1] : END, i }; }
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const sstep = x => { x = clamp(x); return x * x * x * (x * (x * 6 - 15) + 10); };
const back_ = x => { x = clamp(x); const c = 1.7; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); };
const V = (x, y, z) => new THREE.Vector3(x, y, z);
function keys(f, ks) {
  if (f <= ks[0][0]) return ks[0];
  for (let k = 0; k < ks.length - 1; k++) {
    const a = ks[k], b = ks[k + 1];
    if (f <= b[0]) { const t = sstep((f - a[0]) / (b[0] - a[0])); return [f, a[1].clone().lerp(b[1], t), a[2].clone().lerp(b[2], t), a[3] + (b[3] - a[3]) * t, (a[4] || 0) + ((b[4] || 0) - (a[4] || 0)) * t]; }
  }
  return ks[ks.length - 1];
}
// staging (x along the street, z toward camera; cars parked at z = 2 facing +x)
const BC = V(0, 0, 2), SC = V(0, 0, -2.2), WC = V(4.9, 0, 2);
const GUY0 = V(1.0, 0.16, 4.3);
function camFor(sh, f) {
  switch (sh.name) {
    case 'hook': return keys(f, [[0, V(6.6, 1.5, 8.6), V(0.6, 0.9, 2.3), 40, 0], [57, V(5.9, 1.45, 8.0), V(0.6, 0.95, 2.4), 40, 0]]);
    case 'watch': return keys(f, [[58, V(1.4, 1.7, 7.4), V(1.0, 1.55, 4.3), 40, 0], [70, V(1.1, 1.75, 6.2), V(1.0, 1.6, 4.3), 40, 3], [102, V(1.1, 1.75, 6.0), V(1.0, 1.6, 4.3), 40, 3]]);
    case 'cool': return keys(f, [[103, V(4.5, 0.5, 7.2), V(0.4, 0.95, 2.4), 42, -3], [147, V(2.6, 0.55, 7.8), V(0.4, 1.0, 2.6), 42, 0]]);
    case 'oneday': return keys(f, [[148, V(1.6, 1.6, 7.6), V(0.8, 1.3, 3.4), 40, 0], [192, V(1.5, 1.6, 7.2), V(0.8, 1.3, 3.4), 40, 0]]);
    case 'p1': return keys(f, [[193, V(-1.5, 1.6, 8.6), V(-1.0, 3.2, 2.0), 44, 0], [237, V(-1.4, 1.7, 8.0), V(-1.0, 3.4, 2.0), 44, 0]]);
    case 'thermo': return keys(f, [[238, V(7.0, 3.6, 10.0), V(-0.4, 1.9, 0.0), 42, 0], [345, V(6.4, 3.4, 9.2), V(-0.4, 1.9, 0.0), 42, 0]]);
    case 'tandoor': return keys(f, [[346, V(2.2, 1.7, 10.0), V(0.2, 1.0, 2.4), 42, 0], [417, V(2.0, 1.65, 9.2), V(0.2, 1.0, 2.4), 42, 2]]);
    case 'p2': return keys(f, [[418, V(1.4, 1.7, 8.4), V(1.2, 1.9, 3.6), 44, 0], [442, V(1.3, 1.7, 8.0), V(1.2, 1.9, 3.6), 44, 0]]);
    case 'wash': return keys(f, [[443, V(1.9, 1.3, 6.9), V(0.5, 0.95, 3.0), 40, 0], [525, V(1.6, 1.25, 6.4), V(0.4, 0.9, 3.0), 40, 0]]);
    case 'silver': return keys(f, [[526, V(4.6, 1.7, -9.0), V(0.0, 0.8, -2.6), 40, 0], [561, V(4.2, 1.65, -8.4), V(0.0, 0.8, -2.6), 40, 0]]);
    case 'blackdoor': return keys(f, [[562, V(0.3, 0.9, 4.7), V(0.0, 0.66, 2.9), 38, 0], [624, V(0.2, 0.85, 4.2), V(0.0, 0.66, 2.9), 38, -2]]);
    case 'p3': return keys(f, [[625, V(1.3, 1.7, 8.2), V(1.1, 1.9, 3.6), 44, 0], [649, V(1.25, 1.7, 7.9), V(1.1, 1.9, 3.6), 44, 0]]);
    case 'road': return keys(f, [[650, V(33, 12, 16), V(33, 0, -0.3), 50, 0], [831, V(33, 11, 15), V(33, 0, -0.3), 50, 0]]);
    case 'cool2': return keys(f, [[832, V(3.4, 1.2, 8.0), V(0.9, 1.1, 3.2), 40, 0], [867, V(3.0, 1.2, 7.4), V(0.9, 1.1, 3.2), 40, 0]]);
    case 'touch': return keys(f, [[868, V(2.1, 1.7, 7.0), V(0.9, 1.4, 3.6), 40, 0], [895, V(1.9, 1.7, 6.3), V(0.9, 1.4, 3.6), 40, 0], [939, V(1.8, 1.65, 5.9), V(0.9, 1.4, 3.6), 40, 3]]);
    case 'end': return keys(f, [[940, V(2.6, 3.4, 23.0), V(2.6, 1.2, 2.0), 46, 0], [1082, V(2.6, 3.2, 21.5), V(2.6, 1.2, 2.0), 46, 0]]);
  }
  return [f, V(0, 2, 10), V(0, 1, 0), 40, 0];
}
function flashAt(f) { for (const c of [193, 418, 625, 650, 832, 940]) { const d = f - c; if (d >= 0 && d < 6) return 0.55 * (1 - d / 6); } return 0; }
function guyPose(f, sh) {
  const p = { expr: 'smile', arms: 'hang', blink: ((f + 30) % 89) < 3, kick: 0 };
  switch (sh.name) {
    case 'hook': p.expr = 'love'; p.arms = 'hips'; break;
    case 'watch': p.expr = 'shock'; p.arms = 'up'; break;
    case 'cool': p.expr = 'cool'; p.shades = true; p.arms = 'thumbs'; break;
    case 'oneday': p.expr = 'deadpan'; p.arms = 'hang'; break;
    case 'p1': case 'p2': case 'p3': p.expr = 'worry'; p.arms = 'pointL'; break;
    case 'thermo': p.expr = 'shock'; p.arms = 'hang'; break;
    case 'tandoor': p.expr = 'hot'; p.hot = true; p.sweat = true; p.arms = 'fan'; p.wave = Math.round(f * 0.6 % 6.28 * 10) / 10; break;
    case 'wash': p.expr = 'smile'; p.arms = 'wipe'; p.wave = Math.round(f * 0.35 % 6.28 * 10) / 10; break;
    case 'blackdoor': p.expr = 'shock'; p.arms = 'head'; break;
    case 'cool2': p.expr = 'cool'; p.shades = true; p.arms = 'hips'; break;
    case 'touch': if (f < 895) { p.expr = 'cool'; p.shades = true; p.arms = 'touch'; } else { p.expr = 'hot'; p.hot = true; p.sweat = true; p.arms = 'up'; } break;
    case 'end': p.expr = 'smile'; p.arms = f < 994 ? 'pointL' : 'point'; break;
  }
  if (p.expr === 'love' || p.expr === 'cool' || p.expr === 'hot') p.blink = false;
  return p;
}

// captions (white, current word on a red pill), like the owner's edit
let TL = null;
fetch('./timeline.json').then(r => r.json()).then(j => { TL = j; window.ready = true; });
const outCv = document.createElement('canvas'); outCv.width = W; outCv.height = H; const outCtx = outCv.getContext('2d');
function drawCaptions(ctx, t) {
  if (!TL) return;
  const cur = TL.chunks.find(c => c.s <= t && t < c.e); if (!cur) return;
  const words = cur.words.map(w => w.w);
  const size = 66; ctx.font = `800 ${size}px Poppins, sans-serif`; ctx.textBaseline = 'middle';
  const sp = 18, widths = words.map(w => ctx.measureText(w).width);
  let tot = widths.reduce((a, b) => a + b, 0) + sp * (words.length - 1);
  const sc = Math.min(1, 960 / tot); const y = 1440; const pop = 0.9 + 0.1 * back_((t - cur.s) / 0.15);
  ctx.save(); ctx.translate(W / 2, y); ctx.scale(sc * pop, sc * pop);
  let x = -tot / 2;
  cur.words.forEach((wd, k) => {
    const nxt = cur.words[k + 1]; const active = t >= wd.s - 0.03 && (!nxt || t < nxt.s - 0.03);
    if (active) { ctx.fillStyle = '#e8283f'; ctx.beginPath(); ctx.roundRect(x - 12, -size * 0.62, widths[k] + 24, size * 1.24, 16); ctx.fill(); }
    ctx.lineJoin = 'round'; ctx.lineWidth = 12; ctx.strokeStyle = 'rgba(20,10,30,0.9)'; ctx.strokeText(words[k], x, 4);
    ctx.fillStyle = '#ffffff'; ctx.fillText(words[k], x, 4);
    x += widths[k] + sp;
  });
  ctx.restore();
}

window.renderFrame = function (f) {
  const sh = shotAt(f), t = f / 30;
  const hot = ['p1', 'thermo', 'tandoor'].includes(sh.name);
  // cars
  blackCar.position.copy(BC); silverCar.position.copy(SC); whiteCar.position.copy(WC);
  blackCar.rotation.set(0, 0, 0); redCar.visible = false; whiteCar.visible = ['road', 'end'].includes(sh.name);
  blackCar.userData.paint.emissive.setRGB(0, 0, 0);
  // guy
  guy.mesh.visible = true; guy.mesh.position.copy(GUY0); guy.set(guyPose(f, sh));
  let bob = 0;
  if (sh.name === 'watch') bob = 0.12 * Math.max(0, Math.sin(Math.min(1, (f - 58) / 8) * Math.PI));
  if (sh.name === 'touch' && f >= 895) bob = 0.3 * Math.abs(Math.sin((f - 895) * 0.35)) * Math.exp(-(f - 895) / 30);
  guy.mesh.position.y += bob;
  driver.mesh.visible = false; naan.mesh.visible = false; qmark.mesh.visible = false;
  // problem signs
  const signShot = { p1: ['#1', 'HEAT', '#ff8a3a'], p2: ['#2', 'SWIRLS', '#7fc8ff'], p3: ['#3', 'VISIBILITY', '#ffd23f'], oneday: ['DAY 2', '', '#ffffff'] }[sh.name];
  sign.mesh.visible = !!signShot;
  if (signShot) {
    sign.set({ text: signShot[0], sub: signShot[1], bg: signShot[2], size: signShot[1] ? 170 : 150 });
    const k = back_((f - sh.f0 - (sh.name === 'oneday' ? 6 : 0)) / 8);
    sign.mesh.scale.setScalar(Math.max(0.001, k));
    if (sh.name === 'oneday') { sign.mesh.position.set(0.55, 1.75, 3.6); sign.mesh.scale.multiplyScalar(0.5); }
    else if (sh.name === 'p1') sign.mesh.position.set(-1.0, 1.9, 2.6);
    else sign.mesh.position.set(1.2, 0.95, 3.4);
  }
  if (['p1', 'p2', 'p3'].includes(sh.name)) guy.mesh.position.set(2.2, 0.16, 3.9);
  // thermometers
  const thOn = sh.name === 'thermo';
  thermoB.visible = thermoS.visible = thOn;
  if (thOn) {
    const u = clamp((f - 250) / 50);
    thermoB.position.set(BC.x - 0.4, 2.0, BC.z); thermoS.position.set(SC.x - 0.4, 2.0, SC.z);
    for (const [th, lvl] of [[thermoB, 0.15 + 0.85 * sstep(u)], [thermoS, 0.15 + 0.25 * sstep(u)]]) { const fl = th.userData.fill; fl.scale.set(1, 1.5 * lvl, 1); fl.position.y = 0.75 * lvl; }
    sign.mesh.visible = f >= 293; if (f >= 293) { sign.set({ text: '+25°C', sub: 'ROOF', bg: '#ff5a3a', fg: '#ffffff', size: 140 }); sign.mesh.position.set(BC.x + 1.3, 2.1, BC.z + 0.4); sign.mesh.scale.setScalar(Math.max(0.001, back_((f - 293) / 8)) * 0.85); }
    guy.mesh.position.set(3.7, 0.16, 4.6);
  }
  // heat blobs over the black roof
  blobs.forEach((b, k) => {
    const on = hot || (sh.name === 'touch' && f >= 895);
    b.visible = on;
    const ph = ((f * 0.025) + k / blobs.length) % 1;
    const base = sh.name === 'touch' ? V(GUY0.x - 0.4, 1.6, 3.4) : V(BC.x - 0.4 + Math.sin(k * 2.3) * 1.0, 1.65, BC.z + Math.cos(k * 1.7) * 0.5);
    b.position.set(base.x + 0.15 * Math.sin(f * 0.1 + k), base.y + ph * 1.6, base.z);
    b.scale.setScalar(0.12 + 0.18 * ph); b.material.opacity = 0.4 * (1 - ph);
    b.material.color.set(sh.name === 'touch' ? 0xdddddd : 0xff8a3a);
  });
  // tandoor: guy inside the black car, the car glows, a naan slaps onto the window
  if (sh.name === 'tandoor') {
    guy.mesh.position.set(1.15, 0.16, 3.9);
    const u = clamp((f - 346) / 50); blackCar.userData.paint.emissive.setRGB(0.22 * u, 0.04 * u, 0);
    if (f >= 372) { naan.mesh.visible = true; naan.set({}); naan.mesh.position.set(0.35, 0.95, BC.z + 1.08); naan.mesh.scale.setScalar(Math.max(0.001, back_((f - 372) / 6))); }
  } else guy.mesh.scale.setScalar(1);
  // wash
  bucket.visible = ['wash', 'silver', 'blackdoor'].includes(sh.name);
  bucket.position.set(1.9, 0.16, 3.6);
  swirlB.material.opacity = sh.name === 'wash' ? clamp((f - 460) / 60) * 0.55 : sh.name === 'blackdoor' ? 0.95 : 0;
  swirlS.material.opacity = sh.name === 'silver' ? 0.07 : 0;
  if (sh.name === 'wash') guy.mesh.position.set(0.9, 0.16, 3.25);
  if (sh.name === 'blackdoor' || sh.name === 'silver') guy.mesh.visible = false;
  // sparkles: hook/cool on the paint, blackdoor on the swirls
  stars.forEach((s, k) => {
    s.set({});
    const on = ['hook', 'cool'].includes(sh.name) || sh.name === 'blackdoor';
    s.mesh.visible = on;
    const ph = ((f * 0.05) + k / stars.length) % 1;
    const pos = sh.name === 'blackdoor' ? V(-1.2 + k * 0.5, 0.45 + (k % 3) * 0.14, BC.z + 0.98) : V(-1.8 + k * 0.75, 1.0 + (k % 2) * 0.55, BC.z + 1.0);
    s.mesh.position.copy(pos); s.mesh.scale.setScalar(Math.max(0.001, Math.sin(Math.PI * ph)) * (sh.name === 'blackdoor' ? 0.6 : 1));
  });
  blackCar.userData.streak.material.opacity = sh.name === 'oneday' ? 0.55 * (1 - clamp((f - 160) / 12)) : 0.55;
  // safety scene on the street at x = 34: black car pulls out of the shadow, red car brakes, white car in the sun
  if (sh.name === 'road') {
    guy.mesh.visible = false;
    blackCar.position.set(36, 0, -1.9); whiteCar.position.set(30.2, 0, -1.9);
    redCar.visible = true;
    const brakeAt = 785;
    const x = f < brakeAt ? 22 + (f - 650) * 0.075 : 22 + (brakeAt - 650) * 0.075 + 0.6 * sstep((f - brakeAt) / 10);
    redCar.position.set(x, 0, 1.9); redCar.rotation.set(0, 0, f >= brakeAt && f < brakeAt + 12 ? -0.05 * Math.sin((f - brakeAt) * 0.5) : 0);
    blackCar.position.z = -1.9 + 1.2 * sstep((f - 760) / 30); blackCar.rotation.y = 0.35 * sstep((f - 760) / 30);
    driver.mesh.visible = true; driver.set({ expr: f < brakeAt ? 'side' : 'shock', arms: 'hang' });
    driver.mesh.position.set(redCar.position.x - 0.2, 0.15, 1.9);
    qmark.mesh.visible = f > 700 && f < brakeAt; if (qmark.mesh.visible) { qmark.set({}); qmark.mesh.position.set(36, 1.9, -1.4); qmark.mesh.scale.setScalar(Math.max(0.001, back_((f - 700) / 8)) * 1.6); }
    sign.mesh.visible = f >= 748; if (sign.mesh.visible) { sign.set({ text: 'UP TO 10%', sub: 'CRASH RISK', bg: '#ffd23f', size: 96 }); sign.mesh.position.set(34.6, 2.0, 2.6); sign.mesh.scale.setScalar(Math.max(0.001, back_((f - 748) / 8)) * 1.5); }
  }
  shade.visible = sh.name === 'road';
  // end: black vs white side by side, guy between them
  if (sh.name === 'end') { guy.mesh.position.set(2.45, 0.16, 4.2); qmark.mesh.visible = true; qmark.set({}); qmark.mesh.position.set(2.45, 2.5, 4.0); qmark.mesh.scale.setScalar(Math.max(0.001, back_((f - 950) / 8))); }
  if (sh.name === 'touch' || sh.name === 'cool2') guy.mesh.position.set(1.4, 0.16, 3.25);
  if (sh.name === 'hook') guy.mesh.position.set(2.7, 0.16, 4.1);
  // camera
  let [, cp, ct, fov, roll] = camFor(sh, f);
  const local = f - sh.f0;
  let shake = 0;
  if (sh.name === 'watch') shake = 0.03 * Math.exp(-(f - 58) / 6);
  if (sh.name === 'touch' && f >= 895) shake = 0.03 * Math.exp(-(f - 895) / 8);
  if (sh.name === 'road' && f >= 785) shake = 0.05 * Math.exp(-(f - 785) / 6);
  camera.position.copy(cp).add(V(Math.sin(f * 2.3) * shake + 0.02 * Math.sin(local * 0.05), Math.cos(f * 1.7) * shake, 0));
  camera.fov = fov; camera.updateProjectionMatrix(); camera.up.set(0, 1, 0); camera.lookAt(ct);
  camera.rotateZ(THREE.MathUtils.degToRad(roll || 0));
  for (const c of cards) { const m = c.mesh; m.rotation.set(0, Math.atan2(camera.position.x - m.position.x, camera.position.z - m.position.z), 0); }
  // light
  const center = sh.name === 'road' ? V(32, 0, 0) : V(0, 0, 2);
  if (hot) applyLight('hot', 'hot', 0, center); else if (sh.name === 'cool2' || sh.name === 'touch') applyLight('golden', 'golden', 0, center); else applyLight('day', 'day', 0, center);
  sunDisc.visible = hot; sunDisc.position.copy(camera.position).add(V(-8, 30, -60)); sunDisc.lookAt(camera.position);
  renderer.render(scene, camera);
  outCtx.drawImage(renderer.domElement, 0, 0);
  const fl = flashAt(f); if (fl > 0) { outCtx.fillStyle = `rgba(255,255,255,${fl})`; outCtx.fillRect(0, 0, W, H); }
  const g = outCtx.createRadialGradient(W / 2, H / 2, H * 0.35, W / 2, H / 2, H * 0.75);
  g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(20,0,30,0.3)'); outCtx.fillStyle = g; outCtx.fillRect(0, 0, W, H);
  drawCaptions(outCtx, t);
  return outCv.toDataURL('image/jpeg', 0.93);
};
window.FRAMES = END;
