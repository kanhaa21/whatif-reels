
// ======================= Part 2 story (appended to base.js by build) =======================
const PH = (await (await fetch('./phrases.json')).json());
const Ph = i => PH.phrases[i], C = (i, j) => PH.phrases[i].chunks[j];
const TOTAL = PH.duration, END = Math.round(TOTAL * 30);
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const sstep = x => { x = clamp(x); return x * x * x * (x * (x * 6 - 15) + 10); };
const V = (x, y, z) => new THREE.Vector3(x, y, z);
const KID = V(20.0, 0, -6.55);

// ---------- extra props ----------
const entity = new Card(drawEntity);
// darkness beyond the classroom door (the corridor outside, unlit)
const outside = new THREE.Mesh(new THREE.PlaneGeometry(4, 3.4), new THREE.MeshBasicMaterial({ color: 0x060914, fog: false }));
at(outside, 15.0, 1.6, -2.0, 0, Math.PI / 2); scene.add(outside);
// frosty bare footprints from the door to the teacher's desk
const printTex = (() => { const cv = document.createElement('canvas'); cv.width = cv.height = 256; drawPrint(cv.getContext('2d')); const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace; return t; })();
const prints = [];
{
  const path = [V(16.45, 0, -2.05), V(16.95, 0, -2.75), V(17.15, 0, -3.45), V(17.2, 0, -4.15), V(17.35, 0, -4.85), V(17.9, 0, -5.25), V(18.6, 0, -5.3), V(19.3, 0, -5.3)];
  path.forEach((p, k) => {
    const q = path[Math.min(k + 1, path.length - 1)], o = path[Math.max(k - 1, 0)], d = q.clone().sub(o).normalize(), side = V(-d.z, 0, d.x);
    prints.push({ p: p.clone().add(side.multiplyScalar(k % 2 ? 0.12 : -0.12)), yaw: Math.atan2(-d.x, -d.z) });
  });
  // the last two, side by side, right in front of the desk panel, facing the desk
  prints.push({ p: V(19.86, 0, -5.12), yaw: 0 }); prints.push({ p: V(20.14, 0, -5.12), yaw: 0 });
}
for (const pr of prints) {
  const m = new THREE.Mesh(new THREE.PlaneGeometry(0.18, 0.42), new THREE.MeshBasicMaterial({ map: printTex, transparent: true, depthWrite: false, color: 0xeef5ff, fog: false }));
  m.rotation.order = 'YXZ'; m.rotation.set(-Math.PI / 2, pr.yaw, 0); m.position.set(pr.p.x, 0.006, pr.p.z); scene.add(m); pr.m = m;
  const glow = new THREE.Mesh(new THREE.PlaneGeometry(0.34, 0.7), new THREE.MeshBasicMaterial({ map: printTex, transparent: true, depthWrite: false, color: 0x8fb4ff, blending: THREE.AdditiveBlending, fog: false }));
  glow.position.set(0, 0, 0.002); m.add(glow); pr.g = glow;
}
// print times: eight steps across the footprints line, the last pair on "They stopped"
const tStep0 = Ph(2).s + 0.45, tStep1 = C(2, 2).e - 0.05;
prints.forEach((pr, k) => { pr.t = k < 8 ? tStep0 + (tStep1 - tStep0) * k / 7 : C(3, 0).s + 0.05 + (k - 8) * 0.22; });
// pools of light under each hallway panel
const pools = panels.map(p => { const l = new THREE.PointLight(0xe6eeff, 0, 6.5, 1.4); l.position.set(0, 2.9, p.position.z); scene.add(l); return l; });
function hallLights(onFn, flick = 0) {
  panels.forEach((p, k) => {
    let lv = onFn(k); if (lv > 0 && flick) lv *= (Math.sin(NOW * 37 + k * 5.1) > -0.6 ? 1 : 0.25);
    p.material.color.set(lv > 0.5 ? 0xffffff : 0x22222c); pools[k].intensity = 3.2 * lv;
  });
}

// ---------- shots ----------
const SH = [
  ['open', 0], ['doorwide', C(0, 1).s - 0.1], ['nobody', Ph(1).s - 0.25], ['prints', Ph(2).s - 0.2], ['printsLow', C(2, 2).s - 0.1],
  ['stop', Ph(3).s - 0.15], ['kidfear', C(3, 1).s - 0.05], ['voice', Ph(4).s - 0.3], ['realize', Ph(5).s - 0.1], ['hallEmpty', C(5, 1).s - 0.1],
  ['run', Ph(6).s - 0.2], ['exitLong', Ph(7).s - 0.15], ['noface', C(7, 2).s - 0.1], ['lights', Ph(8).s - 0.1], ['locker', Ph(9).s - 0.1],
  ['phone', C(9, 1).s - 0.05], ['slits', Ph(10).s - 0.2], ['phone2', Ph(11).s - 0.15], ['kidend', C(11, 1).e + 0.15], ['end', Ph(12).s - 0.3],
  ['black', Ph(12).e + 0.05],
];
function shotAt(t) { let i = 0; for (let k = 0; k < SH.length; k++) if (t >= SH[k][1]) i = k; return { name: SH[i][0], t0: SH[i][1], t1: i + 1 < SH.length ? SH[i + 1][1] : TOTAL }; }
function lerpCam(t, t0, t1, a, b) { const u = sstep((t - t0) / (t1 - t0)); return [a[0].clone().lerp(b[0], u), a[1].clone().lerp(b[1], u), a[2] + (b[2] - a[2]) * u]; }
const HALLX = 0, EXITZ = -36.2;
let NOW = 0;

function setScene(sh, t) {
  const L = t - sh.t0, D = sh.t1 - sh.t0;
  // defaults
  kid.mesh.visible = false; entity.mesh.visible = false; guard.mesh.visible = false; aimTorch(V(0, 0, 0), V(0, 0, -1), 0);
  prints.forEach(pr => { const a = clamp((t - pr.t) / 0.18); pr.m.visible = a > 0; pr.m.material.opacity = 0.9 * a; pr.g.material.opacity = 0.35 * a * (1 + 2.5 * Math.exp(-(t - pr.t) * 4)); });
  hallLights(() => 0);
  moon.intensity = 0.9; underDoor.visible = underShadow.visible = false;
  lever.rotation.x = 0;
  // the door: closed until it opens on "slowly opened", then stays open
  doorPivot.rotation.y = -1.35 * sstep((t - C(0, 2).s + 0.2) / 2.0);
  let cam;
  switch (sh.name) {
    case 'open':
      lever.rotation.x = 0.6 * sstep((t - 0.25) / 1.1);
      cam = lerpCam(t, 0, sh.t1, [V(16.75, 1.08, -1.25), V(15.98, 1.0, -2.42), 36], [V(16.6, 1.06, -1.4), V(15.98, 1.0, -2.42), 34]);
      break;
    case 'doorwide':
      lever.rotation.x = 0.6 * (1 - sstep((t - 3.6) / 0.6));
      cam = lerpCam(t, sh.t0, sh.t1, [V(19.2, 1.05, -5.4), V(15.95, 1.1, -2.0), 38], [V(18.7, 1.05, -4.9), V(15.95, 1.1, -2.0), 36]);
      break;
    case 'nobody': case 'realize':
      cam = lerpCam(t, sh.t0, sh.t1, [V(19.2, 1.0, -5.3), V(15.95, 1.05, -2.0), 34], [V(18.6, 1.0, -4.7), V(15.95, 1.05, -2.0), 32]);
      break;
    case 'prints':
      cam = lerpCam(t, sh.t0, sh.t1, [V(16.35, 2.5, -2.3), V(17.4, 0, -4.4), 50], [V(16.4, 2.35, -2.6), V(17.6, 0, -4.6), 48]);
      break;
    case 'printsLow':
      cam = lerpCam(t, sh.t0, sh.t1, [V(20.5, 0.3, -5.25), V(17.2, 0.0, -4.5), 46], [V(20.45, 0.28, -5.25), V(17.2, 0.0, -4.5), 44]);
      break;
    case 'stop':
      cam = lerpCam(t, sh.t0, sh.t1, [V(18.7, 0.32, -4.35), V(20.0, 0.18, -5.4), 40], [V(18.85, 0.3, -4.5), V(20.0, 0.18, -5.4), 38]);
      break;
    case 'kidfear': case 'voice': {
      kid.mesh.visible = true;
      const fear = sh.name === 'voice';
      kid.set({ expr: 'scared', arms: fear && t > Ph(4).e ? 'knees' : 'mouth', look: fear ? -6 : 0, sit: true });
      const tremble = fear ? 0.004 * Math.sin(NOW * 47) : 0.002 * Math.sin(NOW * 31);
      kid.mesh.scale.setScalar(0.55); kid.mesh.position.set(KID.x + tremble, -0.24, KID.z);
      cam = fear ? lerpCam(t, sh.t0, sh.t1, [V(20.55, 0.6, -7.35), V(20.0, 0.52, -6.55), 36], [V(20.4, 0.58, -7.1), V(20.0, 0.52, -6.55), 34])
        : lerpCam(t, sh.t0, sh.t1, [V(20.95, 0.62, -7.75), V(20.0, 0.48, -6.55), 40], [V(20.75, 0.6, -7.5), V(20.0, 0.5, -6.55), 38]);
      // while it speaks, the moonlight from the door is cut off: something is standing in it
      if (fear && t > Ph(4).s - 0.1 && t < Ph(4).e + 0.5) moon.intensity = 0.15;
      break;
    }
    case 'hallEmpty':
      cam = lerpCam(t, sh.t0, sh.t1, [V(0.5, 1.5, -4.0), V(0, 1.1, -18), 42], [V(0.45, 1.45, -5.0), V(0, 1.1, -14), 42]);
      break;
    case 'run': {
      kid.mesh.visible = true; const u = sstep(L / (D * 0.95));
      kid.set({ expr: 'scared', arms: 'run', run: Math.round(Math.sin(NOW * 16) * 10) / 10, sit: false });
      hallLights(k => (k === 2 ? 0.6 : 0), 1);
      kid.mesh.scale.setScalar(0.6); kid.mesh.position.set(0.15, 0, -15.5 + 9.0 * u);
      cam = [V(0.1, 1.2, -3.2), V(0, 0.9, -14), 42];
      break;
    }
    case 'exitLong': {
      const show = t > C(7, 1).s + 0.15;
      hallLights(k => (k >= 10 ? 1 : 0), 1);
      entity.mesh.visible = show && !(t < C(7, 1).s + 0.45 && Math.floor(NOW * 20) % 2);
      entity.set({ tilt: 0 }); entity.mesh.scale.setScalar(1.25); entity.mesh.position.set(HALLX, 0, EXITZ);
      cam = lerpCam(t, sh.t0, sh.t1, [V(0, 1.45, -6.0), V(0, 1.6, -37), 40], [V(0, 1.45, -16.0), V(0, 1.7, -37), 38]);
      break;
    }
    case 'noface': {
      hallLights(k => (k >= 10 ? 1 : 0), 1);
      entity.mesh.visible = true; entity.mesh.scale.setScalar(1.25); entity.mesh.position.set(HALLX, 0, EXITZ);
      const tilt = 0.32 * sstep((t - sh.t0) / 1.2) + (t > Ph(7).e + 0.2 ? 0.35 * sstep((t - Ph(7).e - 0.2) / 0.08) : 0);
      entity.set({ tilt: Math.round(tilt * 50) / 50 });
      cam = lerpCam(t, sh.t0, sh.t1, [V(0, 1.7, -31.6), V(0, 2.25, -36.2), 38], [V(0, 1.75, -32.5), V(0, 2.3, -36.2), 34]);
      break;
    }
    case 'lights': {
      // all lights flick back on, then die from the far end towards me; it is always standing in the last light
      const tOff = k => sh.t0 + 0.45 + (11 - k) * ((C(8, 1).e - sh.t0 - 0.6) / 11);
      hallLights(k => (t < tOff(k) ? 1 : 0), 0);
      let front = -1; for (let k = 11; k >= 0; k--) if (t < tOff(k)) { front = k; break; }
      entity.mesh.visible = front >= 0 && t > sh.t0 + 0.45;
      if (front >= 0) entity.mesh.position.set(HALLX, 0, panels[front].position.z - 0.6);
      entity.set({ tilt: 0.3, reach: Math.round(clamp((t - C(8, 1).s) / 0.8) * 10) / 10 }); entity.mesh.scale.setScalar(1.25);
      cam = [V(0, 1.45, 1.0), V(0, 1.65, -30), 40];
      break;
    }
    case 'locker': case 'slits': case 'end': {
      const flick = sh.name === 'locker' ? 1 : 0;
      hallLights(k => (k === 3 ? (sh.name === 'end' ? 0.3 : sh.name === 'slits' ? 1.2 : 0.7) : 0), flick);
      if (sh.name === 'slits') {
        entity.mesh.visible = t > Ph(10).s - 0.1;
        const lean = sstep((t - C(10, 1).s + 0.6) / 0.6);
        entity.set({ tilt: 0.25, reach: 0.4 }); entity.mesh.scale.setScalar(1.25);
        entity.mesh.position.set(0.9 - 0.7 * lean, -0.81 * lean + 0.015 * Math.sin(t * 2.1), -10.0 + 0.06 * Math.sin(t * 0.9));
      }
      cam = [V(-1.18, 1.55, -10.0), V(2, 1.45, -10.0), 52];
      break;
    }
    default:
      cam = [V(0, 1, 5), V(0, 1, 0), 40];
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
// locker door seen from inside: black metal with five horizontal vent slits
function lockerMask(ctx, cover = 0) {
  ctx.save(); ctx.beginPath(); ctx.rect(0, 0, W, H);
  const n = 4;
  for (let k = 0; k < n; k++) { if (k < cover) continue; const y = 650 + k * 120; ctx.roundRect(120, y, 840, 62, 18); }
  ctx.fillStyle = '#07070b'; ctx.fill('evenodd');
  for (let k = 0; k < n; k++) {
    const y = 650 + k * 120; ctx.strokeStyle = 'rgba(120,130,150,0.35)'; ctx.lineWidth = 4; ctx.beginPath(); ctx.roundRect(120, y, 840, 62, 18); ctx.stroke();
  }
  ctx.restore();
}
function wrap(ctx, text, maxW) {
  const words = text.split(' '), lines = []; let cur = '';
  for (const w of words) { const s = cur ? cur + ' ' + w : w; if (ctx.measureText(s).width > maxW && cur) { lines.push(cur); cur = w; } else cur = s; }
  if (cur) lines.push(cur); return lines;
}
function notif(ctx, x, y, w, title, msg, a) {
  ctx.save(); ctx.globalAlpha = a;
  ctx.font = '500 34px Poppins, sans-serif'; const lines = wrap(ctx, msg, w - 60); const h = 120 + lines.length * 46;
  ctx.fillStyle = 'rgba(235,238,248,0.92)'; ctx.beginPath(); ctx.roundRect(x, y, w, h, 34); ctx.fill();
  ctx.fillStyle = '#2fbf5a'; ctx.beginPath(); ctx.roundRect(x + 28, y + 26, 54, 54, 14); ctx.fill();
  ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.ellipse(x + 55, y + 51, 16, 12, 0, 0, Math.PI * 2); ctx.fill();
  ctx.fillStyle = '#111'; ctx.textAlign = 'left'; ctx.textBaseline = 'middle';
  ctx.font = '700 36px Poppins, sans-serif'; ctx.fillText(title, x + 100, y + 54);
  ctx.font = '400 28px Poppins, sans-serif'; ctx.fillStyle = '#666'; ctx.textAlign = 'right'; ctx.fillText('now', x + w - 30, y + 54);
  ctx.textAlign = 'left'; ctx.fillStyle = '#111'; ctx.font = '500 34px Poppins, sans-serif';
  lines.forEach((ln, k) => ctx.fillText(ln, x + 30, y + 120 + k * 46));
  ctx.restore(); return h;
}
function phoneScreen(ctx, t, second) {
  ctx.fillStyle = '#020204'; ctx.fillRect(0, 0, W, H);
  // slow push-in and a hand that can't keep still
  const z = 1 + 0.035 * (t - (second ? Ph(11).s : C(9, 1).s)), jx = 3 * Math.sin(t * 7.3) + 2 * Math.sin(t * 13.1), jy = 3 * Math.cos(t * 6.1);
  ctx.save(); ctx.translate(540 + jx, 880 + jy); ctx.scale(z, z); ctx.translate(-540, -880);
  const g = ctx.createRadialGradient(540, 860, 50, 540, 860, 700); g.addColorStop(0, 'rgba(90,130,220,0.35)'); g.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  const pw = 600, ph = 900, px = 540 - pw / 2, py = 430;
  ctx.fillStyle = '#15161d'; ctx.beginPath(); ctx.roundRect(px - 18, py - 18, pw + 36, ph + 36, 70); ctx.fill();
  const sg = ctx.createLinearGradient(0, py, 0, py + ph); sg.addColorStop(0, '#1d2a55'); sg.addColorStop(1, '#0b1026');
  ctx.fillStyle = sg; ctx.beginPath(); ctx.roundRect(px, py, pw, ph, 56); ctx.fill();
  ctx.fillStyle = '#eef2ff'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.font = '300 130px Poppins, sans-serif'; ctx.fillText('11:47', 540, py + 170);
  ctx.font = '400 32px Poppins, sans-serif'; ctx.fillText('No service', 540, py + 70);
  const a1 = clamp((t - (C(9, 1).s + 0.35)) / 0.2);
  let y = py + 300;
  if (second) {
    const a2 = clamp((t - C(11, 1).s) / 0.18), dy = 40 * (1 - sstep(a2));
    const h2 = notif(ctx, px + 24, y + dy, pw - 48, 'Mom', "Why aren't you answering?? I'm STILL at the gate.", a2);
    y += (h2 + 22) * sstep(a2);
  }
  notif(ctx, px + 24, y, pw - 48, 'Mom', "I'm at the school gate. Where are you?", second ? 1 : a1);
  ctx.restore();
}
function kidClose(ctx, t) {
  // the kid inside the locker, lit only by the phone
  ctx.fillStyle = '#030306'; ctx.fillRect(0, 0, W, H);
  for (let k = 0; k < 4; k++) { ctx.fillStyle = 'rgba(140,160,200,0.10)'; ctx.fillRect(60 + k * 16, 650 + k * 120, 6, 62); }
  kid.set({ expr: 'scared', arms: 'phone', look: -4, sit: false });
  const s = 1.9, jit = 2 * Math.sin(NOW * 41);
  ctx.save(); ctx.translate(540 + jit, 1010); ctx.scale(s, s);
  ctx.drawImage(kid.cv, 60, 150, 480, 560, -240, -340, 480, 560);
  ctx.restore();
  const g = ctx.createRadialGradient(540, 900, 100, 540, 900, 760); g.addColorStop(0, 'rgba(0,0,10,0)'); g.addColorStop(1, 'rgba(0,0,8,0.9)');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
}
// red typewriter captions (Part 1 look), up to three words at a time; the mimic voices in white italics with quotes
const CAPS = [];
for (const ph of PH.phrases) for (const ch of ph.chunks) {
  const words = ch.text.split(' '); const groups = [];
  for (let k = 0; k < words.length; k += 3) groups.push(words.slice(k, k + 3).join(' '));
  const tot = groups.reduce((a, g) => a + g.length, 0); let s = ch.s;
  groups.forEach((g, k) => { const d = (ch.e - ch.s) * g.length / tot; CAPS.push({ text: g, s, e: s + d, who: ph.who, last: k === groups.length - 1 }); s += d; });
}
function captions(ctx, t) {
  let cur = null;
  for (let k = 0; k < CAPS.length; k++) { const c = CAPS[k], nx = CAPS[k + 1]; const hold = nx ? Math.min(nx.s, c.e + 0.35) : c.e + 0.35; if (t >= c.s && t < hold) cur = c; }
  if (!cur) return;
  const mimic = cur.who !== 'n';
  const txt = cur.text;
  const n = Math.max(1, Math.ceil(txt.length * clamp((t - cur.s) / Math.max(0.12, (cur.e - cur.s) * 0.6))));
  const shown = txt.slice(0, n);
  ctx.save(); ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.font = `${mimic ? 'italic ' : ''}700 66px "FreeMono", "Courier 10 Pitch", monospace`;
  const full = ctx.measureText(txt).width, x0 = W / 2 - full / 2;
  ctx.textAlign = 'left';
  ctx.lineJoin = 'round'; ctx.lineWidth = 10; ctx.strokeStyle = 'rgba(0,0,0,0.9)'; ctx.strokeText(shown, x0, 1470);
  ctx.fillStyle = mimic ? '#f2f0ff' : '#ff3b3b'; ctx.fillText(shown, x0, 1470);
  ctx.restore();
}

// ---------- render ----------
const STINGS = [C(0, 2).s, Ph(3).s, Ph(4).s, C(7, 1).s + 0.15, Ph(7).e + 0.2, C(8, 1).s, C(10, 1).s, C(11, 1).s, Ph(12).s + 0.5];
window.renderFrame = function (n) {
  const t = n / 30; NOW = t;
  const sh = shotAt(t);
  if (sh.name === 'black') {
    outCtx.fillStyle = '#000'; outCtx.fillRect(0, 0, W, H);
    const z = 1 + 0.02 * (t - sh.t0); outCtx.save(); outCtx.translate(W / 2, 930); outCtx.scale(z, z); outCtx.translate(-W / 2, -930);
    bigText(outCtx, ['THEN WHO IS', 'OUTSIDE?'], 760, clamp((t - sh.t0) / 0.3), 130);
    const tp = sh.t0 + 0.6;
    if (t >= tp) { bigText(outCtx, ['PART 3'], 1110, clamp((t - tp) / 0.25), 100); bigText(outCtx, ['FOLLOW TO FIND OUT'], 1220, clamp((t - tp - 0.1) / 0.25), 64, '#ff4a4a'); }
    outCtx.restore();
    captions(outCtx, t);
    return outCv.toDataURL('image/jpeg', 0.93);
  }
  if (sh.name === 'phone' || sh.name === 'phone2' || sh.name === 'kidend') {
    if (sh.name === 'kidend' || (sh.name === 'phone' && t < C(9, 1).s + 0.3)) kidClose(outCtx, t);
    else phoneScreen(outCtx, t, sh.name === 'phone2');
    captions(outCtx, t);
    return outCv.toDataURL('image/jpeg', 0.93);
  }
  let [cp, ct, fov] = setScene(sh, t);
  let shake = 0;
  for (const ts of STINGS) if (t >= ts && t < ts + 0.25) shake += 0.012 * (1 - (t - ts) / 0.25);
  if (sh.name === 'end') shake += 0.003 + 0.01 * sstep((t - Ph(12).s) / 0.5);
  camera.position.copy(cp).add(V(Math.sin(t * 69) * shake + 0.008 * Math.sin(t * 1.2), Math.cos(t * 51) * shake + 0.006 * Math.sin(t * 0.93), 0));
  camera.fov = fov; camera.updateProjectionMatrix(); camera.up.set(0, 1, 0); camera.lookAt(ct);
  for (const c of cards) { const m = c.mesh; m.rotation.set(0, Math.atan2(camera.position.x - m.position.x, camera.position.z - m.position.z), 0); }
  const inHall = ['hallEmpty', 'exitLong', 'noface', 'lights', 'locker', 'slits', 'end'].includes(sh.name);
  applyLight('night', 'night', 0, inHall ? V(0, 0, -12) : V(RX, 0, RZ));
  if (inHall) hemi.intensity = 0.22;
  renderer.render(scene, camera);
  outCtx.drawImage(renderer.domElement, 0, 0);
  const g = outCtx.createRadialGradient(W / 2, H / 2, H * 0.25, W / 2, H / 2, H * 0.72);
  g.addColorStop(0, 'rgba(0,0,10,0)'); g.addColorStop(1, 'rgba(0,0,12,0.6)'); outCtx.fillStyle = g; outCtx.fillRect(0, 0, W, H);
  if (['locker', 'slits', 'end'].includes(sh.name)) {
    const cover = sh.name === 'end' ? Math.floor(clamp((t - Ph(12).s - 0.3) / (Ph(12).e - Ph(12).s - 0.3)) * 4.99) : 0;
    lockerMask(outCtx, cover);
  }
  // all the lights gone: a beat of total dark before the locker
  if (sh.name === 'lights' && t > C(8, 1).e + 0.05) { outCtx.fillStyle = '#000'; outCtx.fillRect(0, 0, W, H); }
  if (t < 2.3) bigText(outCtx, ['THE LOCKED DOOR', 'OPENED...'], 1010, t < 2.0 ? 1 : clamp((2.3 - t) / 0.3), 112);
  captions(outCtx, t);
  return outCv.toDataURL('image/jpeg', 0.93);
};
window.FRAMES = END;
window.ready = true;
