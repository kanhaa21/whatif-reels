// Painted canvas textures, flat colour with darker seams and speckles.
import * as THREE from 'three';

function rnd(seed) { let s = seed >>> 0; return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296); }
function canvas(w, h) { const c = document.createElement('canvas'); c.width = w; c.height = h; return [c, c.getContext('2d')]; }
function tex(c, rep = 1) {
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace;
  t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(rep, rep); t.anisotropy = 4; return t;
}

export function sand(wet = false, rep = 1) {
  const [c, x] = canvas(512, 512); const r = rnd(wet ? 7 : 3);
  x.fillStyle = wet ? '#c9925a' : '#e8c27e'; x.fillRect(0, 0, 512, 512);
  for (let k = 0; k < 60; k++) {
    x.fillStyle = wet ? 'rgba(120,70,30,0.18)' : 'rgba(190,140,70,0.25)';
    x.beginPath(); x.ellipse(r() * 512, r() * 512, 20 + r() * 60, 10 + r() * 30, r() * 3, 0, 7); x.fill();
  }
  for (let k = 0; k < 2500; k++) { x.fillStyle = r() < 0.5 ? 'rgba(90,50,20,0.35)' : 'rgba(255,240,200,0.35)'; x.fillRect(r() * 512, r() * 512, 2, 2); }
  if (wet) for (let k = 0; k < 40; k++) {
    x.strokeStyle = 'rgba(255,230,180,0.35)'; x.lineWidth = 3;
    x.beginPath(); const cx = r() * 512, cy = r() * 512; x.ellipse(cx, cy, 30 + r() * 40, 12 + r() * 14, 0, 0, 7); x.stroke();
  }
  return tex(c, rep);
}

export function grass(rep = 30) {
  const [c, x] = canvas(256, 256); const r = rnd(11);
  x.fillStyle = '#6fbf4a'; x.fillRect(0, 0, 256, 256);
  for (let k = 0; k < 40; k++) { x.fillStyle = 'rgba(70,140,40,0.35)'; x.beginPath(); x.ellipse(r() * 256, r() * 256, 18 + r() * 30, 10 + r() * 16, 0, 0, 7); x.fill(); }
  for (let k = 0; k < 500; k++) {
    const gx = r() * 256, gy = r() * 256; x.strokeStyle = r() < 0.5 ? 'rgba(40,110,30,0.6)' : 'rgba(170,230,110,0.6)';
    x.lineWidth = 2; x.beginPath(); x.moveTo(gx, gy); x.lineTo(gx + (r() - 0.5) * 6, gy - 6 - r() * 6); x.stroke();
  }
  return tex(c, rep);
}

export function dirt(rep = 8) {
  const [c, x] = canvas(256, 256); const r = rnd(5);
  x.fillStyle = '#9a6a45'; x.fillRect(0, 0, 256, 256);
  for (let k = 0; k < 900; k++) { x.fillStyle = r() < 0.5 ? 'rgba(60,35,20,0.4)' : 'rgba(200,150,100,0.35)'; x.fillRect(r() * 256, r() * 256, 3, 3); }
  return tex(c, rep);
}

export function water(rep = 6) {
  const [c, x] = canvas(256, 256); const r = rnd(9);
  x.fillStyle = '#3f9fd6'; x.fillRect(0, 0, 256, 256);
  for (let k = 0; k < 40; k++) {
    x.strokeStyle = 'rgba(220,245,255,0.55)'; x.lineWidth = 3; const wx = r() * 256, wy = r() * 256;
    x.beginPath(); x.moveTo(wx, wy); x.quadraticCurveTo(wx + 12, wy - 6, wx + 26, wy); x.stroke();
  }
  return tex(c, rep);
}

export function planks(rep = 1) {
  const [c, x] = canvas(256, 256); const r = rnd(13);
  x.fillStyle = '#b07a46'; x.fillRect(0, 0, 256, 256);
  for (let k = 0; k < 4; k++) { x.fillStyle = 'rgba(70,40,20,0.8)'; x.fillRect(0, k * 64, 256, 4); }
  for (let k = 0; k < 60; k++) { x.strokeStyle = 'rgba(80,45,20,0.35)'; x.lineWidth = 2; const y = r() * 256; x.beginPath(); x.moveTo(0, y); x.lineTo(256, y + (r() - 0.5) * 8); x.stroke(); }
  return tex(c, rep);
}

export function signBoard(lines, opts = {}) {
  const [c, x] = canvas(512, 320);
  x.fillStyle = opts.bg || '#f2c84b'; x.fillRect(0, 0, 512, 320);
  x.lineWidth = 18; x.strokeStyle = '#3b1d3f'; x.strokeRect(9, 9, 494, 302);
  x.textAlign = 'center'; x.textBaseline = 'middle'; x.fillStyle = opts.fg || '#3b1d3f';
  const n = lines.length;
  lines.forEach((l, k) => { x.font = `bold ${l[1]}px sans-serif`; x.fillText(l[0], 256, 160 + (k - (n - 1) / 2) * (opts.lh || 110)); });
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
}

export function poster() {
  const [c, x] = canvas(768, 512);
  const g = x.createLinearGradient(0, 0, 0, 512); g.addColorStop(0, '#2b0a2e'); g.addColorStop(1, '#8a1d2b');
  x.fillStyle = g; x.fillRect(0, 0, 768, 512);
  // dunes
  x.fillStyle = '#d6a35a'; x.beginPath(); x.moveTo(0, 400); x.quadraticCurveTo(200, 330, 384, 390); x.quadraticCurveTo(560, 450, 768, 360); x.lineTo(768, 512); x.lineTo(0, 512); x.fill();
  // hand sticking out
  x.fillStyle = '#f2c29a'; x.strokeStyle = '#3b1d3f'; x.lineWidth = 8;
  x.beginPath(); x.moveTo(360, 410); x.lineTo(360, 300); x.lineTo(350, 250); x.lineTo(366, 246); x.lineTo(374, 290); x.lineTo(378, 236); x.lineTo(394, 236);
  x.lineTo(396, 290); x.lineTo(404, 244); x.lineTo(420, 248); x.lineTo(414, 300); x.lineTo(424, 270); x.lineTo(438, 276); x.lineTo(420, 330); x.lineTo(410, 410); x.closePath(); x.fill(); x.stroke();
  x.textAlign = 'center'; x.textBaseline = 'middle';
  x.font = 'bold 110px sans-serif'; x.lineWidth = 14; x.strokeStyle = '#3b1d3f'; x.strokeText('SWALLOWED', 384, 100); x.fillStyle = '#ffd23f'; x.fillText('SWALLOWED', 384, 100);
  x.font = 'bold 54px sans-serif'; x.lineWidth = 10; x.strokeText('BY THE SAND!', 384, 180); x.fillStyle = '#ffffff'; x.fillText('BY THE SAND!', 384, 180);
  x.font = 'bold 30px sans-serif'; x.fillStyle = '#ffd23f'; x.fillText('NOW SHOWING', 384, 478);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
}

export function blueprint() {
  const [c, x] = canvas(512, 512);
  x.fillStyle = '#1d2f63'; x.fillRect(0, 0, 512, 512);
  x.strokeStyle = 'rgba(140,180,255,0.25)'; x.lineWidth = 2;
  for (let k = 0; k <= 512; k += 32) { x.beginPath(); x.moveTo(k, 0); x.lineTo(k, 512); x.moveTo(0, k); x.lineTo(512, k); x.stroke(); }
  return tex(c, 4);
}

export function cloud() {
  const [c, x] = canvas(512, 256);
  x.fillStyle = '#ffffff'; x.strokeStyle = 'rgba(160,140,190,0.6)'; x.lineWidth = 6;
  for (const [cx, cy, r] of [[150, 160, 70], [240, 120, 90], [340, 150, 75], [410, 175, 50], [90, 185, 45]]) { x.beginPath(); x.arc(cx, cy, r, 0, 7); x.fill(); }
  x.fillRect(90, 160, 330, 70);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
}

export function label(text, bg, fg, w = 512, h = 512, size = 120) {
  const [c, x] = canvas(w, h);
  x.fillStyle = bg; x.fillRect(0, 0, w, h);
  x.textAlign = 'center'; x.textBaseline = 'middle'; x.font = `bold ${size}px sans-serif`;
  x.lineWidth = 16; x.strokeStyle = '#3b1d3f'; x.strokeRect(8, 8, w - 16, h - 16);
  x.fillStyle = fg; x.fillText(text, w / 2, h / 2);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
}

export function asphalt(rep = 10) {
  const [c, x] = canvas(256, 256); const r = rnd(21);
  x.fillStyle = '#4a4b57'; x.fillRect(0, 0, 256, 256);
  for (let k = 0; k < 1400; k++) { x.fillStyle = r() < 0.5 ? 'rgba(20,20,30,0.45)' : 'rgba(150,150,170,0.3)'; x.fillRect(r() * 256, r() * 256, 2, 2); }
  return tex(c, rep);
}
export function pavement(rep = 10) {
  const [c, x] = canvas(256, 256);
  x.fillStyle = '#c9c2b8'; x.fillRect(0, 0, 256, 256);
  x.strokeStyle = 'rgba(90,80,80,0.5)'; x.lineWidth = 3;
  for (let k = 0; k <= 256; k += 64) { x.beginPath(); x.moveTo(k, 0); x.lineTo(k, 256); x.moveTo(0, k); x.lineTo(256, k); x.stroke(); }
  return tex(c, rep);
}
export function facade(col, rep = 1) {
  const [c, x] = canvas(256, 512); const r = rnd(col.length * 7);
  x.fillStyle = col; x.fillRect(0, 0, 256, 512);
  for (let row = 0; row < 7; row++) for (let k = 0; k < 4; k++) {
    x.fillStyle = r() < 0.25 ? '#ffe9a8' : '#3f5f8f'; x.fillRect(22 + k * 58, 30 + row * 68, 36, 44);
    x.strokeStyle = '#3b1d3f'; x.lineWidth = 4; x.strokeRect(22 + k * 58, 30 + row * 68, 36, 44);
  }
  return tex(c, rep);
}
export function swirls() {
  const [c, x] = canvas(1024, 512); const r = rnd(33);
  x.clearRect(0, 0, 1024, 512);
  for (let k = 0; k < 60; k++) {
    const cx = r() * 1024, cy = r() * 512, rad = 30 + r() * 120;
    x.strokeStyle = `rgba(235,240,255,${0.35 + r() * 0.5})`; x.lineWidth = 1.5 + r() * 2.5;
    x.beginPath(); x.arc(cx, cy, rad, r() * 6, r() * 6 + 1.5 + r() * 3); x.stroke();
  }
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
}
