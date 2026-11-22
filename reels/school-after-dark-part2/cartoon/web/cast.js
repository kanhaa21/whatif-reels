// Flat 2D bean-head cartoon cards, drawn on a 600x1000 design canvas with soles at y=975.
// Card is 2.25 m tall, so 1 canvas unit = 0.00225 m. Plum outlines.
export const PLUM = '#3b1d3f';
const SKIN = '#f2c29a', SKIN_D = '#d89a72', SHIRT = '#ff8a2a', SHIRT_D = '#e06b12',
  JEANS = '#3f6fd1', JEANS_D = '#2d55a8', CAP = '#e23b4e', PACK = '#2f9e6a', SHOE = '#8a4b2a', SOCK = '#f4f1e8';

function ol(c, w = 9) { c.lineWidth = w; c.strokeStyle = PLUM; c.lineJoin = 'round'; c.lineCap = 'round'; c.stroke(); }
function fillOl(c, col, w = 9) { c.fillStyle = col; c.fill(); ol(c, w); }
function rr(c, x, y, w, h, r) { c.beginPath(); c.roundRect(x, y, w, h, r); }
function ell(c, x, y, rx, ry, rot = 0) { c.beginPath(); c.ellipse(x, y, rx, ry, rot, 0, Math.PI * 2); }

function limb(c, x0, y0, x1, y1, w, col) {
  c.beginPath(); c.moveTo(x0, y0); c.lineTo(x1, y1);
  c.lineCap = 'round'; c.lineWidth = w + 18; c.strokeStyle = PLUM; c.stroke();
  c.lineWidth = w; c.strokeStyle = col; c.stroke();
}

const ARMS = {
  hang: [[178, 700], [422, 700]],
  up: [[95, 280], [505, 280]],
  pull: [[238, 790], [292, 810]],
  lift: [[205, 150], [395, 150]],
  wave: [[178, 700], [520, 300]],
  spread: [[50, 470], [550, 470]],
  hips: [[150, 640], [450, 640]],
  head: [[205, 210], [395, 210]],
};

// p: {expr, arms, kick (-1..1), blink, sweat, oneShoe, wave (phase), mouthOpen}
export function drawHero(c, p) {
  c.clearRect(0, 0, 600, 1000);
  const kick = p.kick || 0;
  // backpack behind
  rr(c, 175, 440, 250, 260, 50); fillOl(c, PACK);
  // legs
  const legs = [[255, -1], [345, 1]];
  for (const [lx, side] of legs) {
    const a = (side < 0 ? kick : -kick) * 0.35;
    c.save(); c.translate(lx, 720); c.rotate(a);
    rr(c, -40, -10, 80, 245, 34); fillOl(c, side < 0 ? JEANS : JEANS_D);
    if (p.oneShoe && side > 0) { ell(c, 8, 238, 46, 22); fillOl(c, SOCK); }
    else { ell(c, 14, 240, 58, 28); fillOl(c, SHOE); }
    c.restore();
  }
  // torso
  rr(c, 190, 450, 220, 290, 70); fillOl(c, SHIRT);
  c.beginPath(); c.moveTo(250, 470); c.lineTo(235, 720); c.moveTo(350, 470); c.lineTo(365, 720);
  c.lineWidth = 16; c.strokeStyle = PACK; c.stroke();
  // arms
  let arms = ARMS[p.arms || 'hang'];
  if (p.arms === 'wave') arms = [arms[0], [520 + 30 * Math.sin(p.wave || 0), 300 + 20 * Math.cos(p.wave || 0)]];
  const sh = [[205, 500], [395, 500]];
  for (let k = 0; k < 2; k++) {
    limb(c, sh[k][0], sh[k][1], arms[k][0], arms[k][1], 42, SHIRT);
    ell(c, arms[k][0], arms[k][1], 30, 30); fillOl(c, SKIN, 8);
  }
  // head (bean)
  ell(c, 300, 330, 128, 142); fillOl(c, SKIN, 10);
  ell(c, 172, 345, 22, 34); fillOl(c, SKIN, 8); ell(c, 428, 345, 22, 34); fillOl(c, SKIN, 8);
  // cap
  c.beginPath(); c.ellipse(300, 250, 132, 92, 0, Math.PI, 0); c.closePath(); fillOl(c, CAP);
  c.beginPath(); c.ellipse(372, 252, 98, 22, 0.05, 0, Math.PI * 2); fillOl(c, CAP, 8);
  ell(c, 300, 168, 14, 10); fillOl(c, '#ffffff', 6);
  face(c, p);
  if (p.sweat) {
    for (const [sx, sy] of [[150, 270], [460, 300]]) {
      c.beginPath(); c.moveTo(sx, sy - 26); c.quadraticCurveTo(sx + 18, sy, sx, sy + 12); c.quadraticCurveTo(sx - 18, sy, sx, sy - 26);
      c.fillStyle = '#8fd3ff'; c.fill(); ol(c, 5);
    }
  }
}

function eyes(c, rx, ry, pupil, dx = 0, dy = 0) {
  for (const ex of [252, 348]) {
    ell(c, ex, 330, rx, ry); fillOl(c, '#ffffff', 7);
    ell(c, ex + dx, 334 + dy, pupil, pupil); c.fillStyle = PLUM; c.fill();
    ell(c, ex + dx - pupil * 0.35, 330 + dy - pupil * 0.35, pupil * 0.3, pupil * 0.3); c.fillStyle = '#fff'; c.fill();
  }
}
function brows(c, lift, tilt) {
  c.lineWidth = 10; c.strokeStyle = PLUM; c.lineCap = 'round';
  for (const [ex, s] of [[252, -1], [348, 1]]) {
    c.beginPath(); c.moveTo(ex - 30, 282 - lift + s * tilt); c.lineTo(ex + 30, 282 - lift - s * tilt); c.stroke();
  }
}
function face(c, p) {
  const e = p.expr || 'smile';
  if (p.blink || e === 'relief') {
    c.lineWidth = 9; c.strokeStyle = PLUM;
    for (const ex of [252, 348]) { c.beginPath(); c.arc(ex, 338, 24, Math.PI * 1.1, Math.PI * 1.9); c.stroke(); }
  } else if (e === 'strain') {
    c.lineWidth = 10; c.strokeStyle = PLUM;
    for (const [ex, s] of [[252, 1], [348, -1]]) { c.beginPath(); c.moveTo(ex - 24, 318); c.lineTo(ex + 6 * s, 332); c.lineTo(ex - 24 * -1, 346 - 28); c.stroke(); }
  } else if (e === 'shock' || e === 'panic') eyes(c, 34, 40, 10);
  else if (e === 'puzzled') eyes(c, 28, 32, 13, 6, -4);
  else if (e === 'worry') eyes(c, 30, 34, 13, 0, 8);
  else if (e === 'calm') { eyes(c, 28, 30, 13); c.fillStyle = SKIN; c.fillRect(215, 296, 170, 20); }
  else eyes(c, 28, 32, 14);
  // brows
  if (e === 'shock' || e === 'panic') brows(c, 30, 6);
  else if (e === 'strain') brows(c, 0, -10);
  else if (e === 'worry') brows(c, 18, 9);
  else if (e === 'puzzled') { brows(c, 10, 0); c.beginPath(); c.moveTo(320, 262); c.lineTo(378, 248); c.stroke(); }
  else brows(c, 14, 0);
  // cheeks
  if (e === 'strain' || e === 'relief' || e === 'smile') {
    c.globalAlpha = e === 'strain' ? 0.7 : 0.45;
    ell(c, 222, 382, 26, 16); c.fillStyle = '#ff6f7a'; c.fill(); ell(c, 378, 382, 26, 16); c.fill(); c.globalAlpha = 1;
  }
  // mouth
  c.lineWidth = 9; c.strokeStyle = PLUM;
  if (e === 'shock') { ell(c, 300, 410, 26, 34); fillOl(c, '#7a2033', 8); }
  else if (e === 'panic') {
    c.beginPath(); c.moveTo(260, 412);
    for (let k = 1; k <= 6; k++) c.lineTo(260 + k * 13.3, 412 + (k % 2 ? -10 : 10));
    c.stroke();
  } else if (e === 'strain') { rr(c, 258, 396, 84, 34, 10); fillOl(c, '#ffffff', 8); c.beginPath(); c.moveTo(258, 413); c.lineTo(342, 413); c.lineWidth = 5; c.stroke(); }
  else if (e === 'puzzled') { c.beginPath(); c.moveTo(280, 414); c.quadraticCurveTo(305, 402, 326, 418); c.stroke(); }
  else if (e === 'calm') { c.beginPath(); c.arc(300, 392, 30, 0.2 * Math.PI, 0.8 * Math.PI); c.stroke(); }
  else if (e === 'worry') { c.beginPath(); c.arc(300, 440, 30, 1.2 * Math.PI, 1.8 * Math.PI); c.stroke(); }
  else { c.beginPath(); c.arc(300, 380, 44, 0.15 * Math.PI, 0.85 * Math.PI); c.closePath(); fillOl(c, '#7a2033', 8); }
}

export function drawBird(c, p) {
  c.clearRect(0, 0, 600, 1000);
  const fl = Math.sin(p.flap || 0);
  c.save(); c.translate(300, 700);
  ell(c, 0, 0, 90, 60); fillOl(c, '#3d4a6b');
  c.beginPath(); c.moveTo(-20, -10); c.lineTo(-150, -10 - 120 * fl); c.lineTo(-60, 30); c.closePath(); fillOl(c, '#2c3756');
  c.beginPath(); c.moveTo(20, -10); c.lineTo(150, -10 - 120 * fl); c.lineTo(60, 30); c.closePath(); fillOl(c, '#2c3756');
  ell(c, 70, -40, 38, 34); fillOl(c, '#3d4a6b');
  c.beginPath(); c.moveTo(100, -40); c.lineTo(140, -30); c.lineTo(100, -24); c.closePath(); fillOl(c, '#ffb020', 6);
  ell(c, 80, -48, 7, 7); c.fillStyle = '#fff'; c.fill();
  c.restore();
}

export function drawShoe(c) {
  c.clearRect(0, 0, 600, 1000);
  c.save(); c.translate(300, 800);
  c.beginPath(); c.moveTo(-160, 40); c.lineTo(-150, -70); c.quadraticCurveTo(-60, -110, -10, -60); c.quadraticCurveTo(60, -30, 170, -10);
  c.quadraticCurveTo(200, 30, 170, 50); c.closePath(); fillOl(c, SHOE, 12);
  rr(c, -170, 40, 360, 34, 14); fillOl(c, '#f4f1e8', 10);
  c.lineWidth = 8; c.strokeStyle = '#f4f1e8';
  for (let k = 0; k < 3; k++) { c.beginPath(); c.moveTo(-100 + k * 40, -70 + k * 10); c.lineTo(-60 + k * 40, -80 + k * 10); c.stroke(); }
  c.restore();
}

export function drawQuestion(c) {
  c.clearRect(0, 0, 600, 1000);
  c.font = 'bold 420px sans-serif'; c.textAlign = 'center'; c.textBaseline = 'middle';
  c.lineWidth = 26; c.strokeStyle = PLUM; c.strokeText('?', 300, 650); c.fillStyle = '#ffd23f'; c.fillText('?', 300, 650);
}

// sulking face painted on the sand surface (viewed from above, top of canvas = far side)
export function drawSandFace(c, p) {
  c.clearRect(0, 0, 1000, 1000);
  const m = p.mood || 0; // 0 pout, 1 burp
  c.save(); c.translate(500, 500);
  for (const ex of [-170, 170]) {
    ell(c, ex, -90, 80, 60); c.fillStyle = '#fff6e0'; c.fill(); c.lineWidth = 14; c.strokeStyle = PLUM; c.stroke();
    ell(c, ex + 10, -70, 30, 30); c.fillStyle = PLUM; c.fill();
    c.beginPath(); c.moveTo(ex - 90, -190 + (ex < 0 ? 0 : 30)); c.lineTo(ex + 90, -160 - (ex < 0 ? -30 : 0)); c.lineWidth = 22; c.stroke();
  }
  c.lineWidth = 18;
  if (m > 0.5) { ell(c, 0, 140, 120, 90); c.fillStyle = '#5a2a1a'; c.fill(); c.stroke(); }
  else { c.beginPath(); c.moveTo(-130, 170); c.quadraticCurveTo(0, 60, 130, 170); c.stroke(); }
  c.restore();
}

// ---------- young car enthusiast: purple hoodie, dark quiff, white sneakers, optional shades ----------
const HOOD = '#7b4bd6', HOOD_D = '#5f37b3', HAIR = '#2a1a22', PANTS = '#2b2f45', SNEAK = '#f4f4f4';
const GUY_ARMS = {
  hang: [[178, 700], [422, 700]], up: [[95, 280], [505, 280]], point: [[178, 700], [560, 470]],
  pointL: [[40, 470], [422, 700]], touch: [[178, 700], [565, 640]], hips: [[150, 640], [450, 640]],
  fan: [[178, 700], [470, 330]], wipe: [[178, 700], [560, 600]], cheer: [[95, 280], [505, 280]],
  thumbs: [[178, 700], [470, 470]], head: [[205, 210], [395, 210]],
};
export function drawGuy(c, p) {
  c.clearRect(0, 0, 600, 1000);
  const kick = p.kick || 0;
  for (const [lx, side] of [[255, -1], [345, 1]]) {
    const a = (side < 0 ? kick : -kick) * 0.35;
    c.save(); c.translate(lx, 720); c.rotate(a);
    rr(c, -40, -10, 80, 245, 34); fillOl(c, PANTS);
    ell(c, 14, 240, 60, 28); fillOl(c, SNEAK);
    c.beginPath(); c.moveTo(-30, 246); c.lineTo(60, 246); c.lineWidth = 8; c.strokeStyle = '#e23b4e'; c.stroke();
    c.restore();
  }
  rr(c, 185, 440, 230, 300, 72); fillOl(c, HOOD);
  rr(c, 240, 600, 120, 70, 20); fillOl(c, HOOD_D, 7);              // pocket
  c.beginPath(); c.moveTo(280, 470); c.lineTo(276, 540); c.moveTo(320, 470); c.lineTo(324, 540); c.lineWidth = 7; c.strokeStyle = '#f4f4f4'; c.stroke();
  let arms = GUY_ARMS[p.arms || 'hang'];
  const sh = [[205, 500], [395, 500]];
  for (let k = 0; k < 2; k++) {
    let [hx, hy] = arms[k];
    if (p.arms === 'wipe' && k === 1) { hx += 40 * Math.sin(p.wave || 0); hy += 30 * Math.cos(p.wave || 0); }
    if (p.arms === 'fan' && k === 1) { hx += 30 * Math.sin(p.wave || 0); }
    limb(c, sh[k][0], sh[k][1], hx, hy, 44, HOOD);
    ell(c, hx, hy, 30, 30); fillOl(c, SKIN, 8);
    if (p.arms === 'thumbs' && k === 1) { rr(c, hx - 8, hy - 62, 18, 40, 9); fillOl(c, SKIN, 6); }
    if (p.arms === 'wipe' && k === 1) { rr(c, hx - 45, hy - 30, 90, 60, 18); fillOl(c, '#ffd23f', 8); }
  }
  // head
  ell(c, 300, 330, 128, 142); fillOl(c, SKIN, 10);
  ell(c, 172, 345, 22, 34); fillOl(c, SKIN, 8); ell(c, 428, 345, 22, 34); fillOl(c, SKIN, 8);
  // quiff
  c.beginPath(); c.moveTo(175, 300); c.quadraticCurveTo(170, 175, 290, 170); c.quadraticCurveTo(420, 120, 440, 250);
  c.quadraticCurveTo(400, 215, 330, 225); c.quadraticCurveTo(250, 230, 175, 300); c.closePath(); fillOl(c, HAIR, 9);
  if (p.hot) { c.globalAlpha = 0.35; ell(c, 300, 340, 128, 142); c.fillStyle = '#ff3b2b'; c.fill(); c.globalAlpha = 1; }
  guyFace(c, p);
  if (p.sweat) for (const [sx, sy] of [[150, 270], [460, 300], [440, 420]]) {
    c.beginPath(); c.moveTo(sx, sy - 26); c.quadraticCurveTo(sx + 18, sy, sx, sy + 12); c.quadraticCurveTo(sx - 18, sy, sx, sy - 26);
    c.fillStyle = '#8fd3ff'; c.fill(); ol(c, 5);
  }
}
function heart(c, x, y, s) {
  c.beginPath(); c.moveTo(x, y + s * 0.9);
  c.bezierCurveTo(x - s * 1.4, y - s * 0.1, x - s * 0.6, y - s * 1.1, x, y - s * 0.35);
  c.bezierCurveTo(x + s * 0.6, y - s * 1.1, x + s * 1.4, y - s * 0.1, x, y + s * 0.9); c.closePath(); fillOl(c, '#ff3b6b', 7);
}
function guyFace(c, p) {
  const e = p.expr || 'smile';
  if (p.shades || e === 'cool') {
    rr(c, 205, 300, 90, 56, 18); fillOl(c, '#1b1b22', 7); rr(c, 305, 300, 90, 56, 18); fillOl(c, '#1b1b22', 7);
    c.beginPath(); c.moveTo(295, 318); c.lineTo(305, 318); c.lineWidth = 8; c.strokeStyle = PLUM; c.stroke();
    c.beginPath(); c.moveTo(220, 314); c.lineTo(250, 340); c.lineWidth = 6; c.strokeStyle = 'rgba(255,255,255,0.7)'; c.stroke();
  } else if (e === 'love') { heart(c, 252, 330, 30); heart(c, 348, 330, 30); }
  else if (e === 'shock' || e === 'hot') eyes(c, 34, 40, 10);
  else if (p.blink) { c.lineWidth = 9; c.strokeStyle = PLUM; for (const ex of [252, 348]) { c.beginPath(); c.arc(ex, 338, 24, Math.PI * 1.1, Math.PI * 1.9); c.stroke(); } }
  else if (e === 'worry') eyes(c, 30, 34, 13, 0, 8);
  else if (e === 'side') eyes(c, 28, 32, 13, 12, 0);
  else eyes(c, 28, 32, 14);
  if (e === 'shock' || e === 'hot') brows(c, 30, 6); else if (e === 'worry' || e === 'deadpan') brows(c, 8, 0); else if (!(p.shades || e === 'cool')) brows(c, 16, 0);
  if (e === 'love' || e === 'smile' || e === 'cool') {
    c.globalAlpha = 0.45; ell(c, 222, 382, 26, 16); c.fillStyle = '#ff6f7a'; c.fill(); ell(c, 378, 382, 26, 16); c.fill(); c.globalAlpha = 1;
  }
  c.lineWidth = 9; c.strokeStyle = PLUM;
  if (e === 'shock') { ell(c, 300, 412, 26, 34); fillOl(c, '#7a2033', 8); }
  else if (e === 'hot') { ell(c, 300, 410, 34, 26); fillOl(c, '#7a2033', 8); rr(c, 286, 412, 28, 40, 12); fillOl(c, '#ff6f8a', 6); }
  else if (e === 'deadpan') { c.beginPath(); c.moveTo(265, 412); c.lineTo(335, 412); c.stroke(); }
  else if (e === 'worry') { c.beginPath(); c.arc(300, 440, 30, 1.2 * Math.PI, 1.8 * Math.PI); c.stroke(); }
  else if (e === 'cool') { c.beginPath(); c.moveTo(262, 405); c.quadraticCurveTo(310, 430, 345, 395); c.stroke(); }
  else { c.beginPath(); c.arc(300, 380, 44, 0.15 * Math.PI, 0.85 * Math.PI); c.closePath(); fillOl(c, '#7a2033', 8); }
}

export function drawNaan(c) {
  c.clearRect(0, 0, 600, 1000);
  c.save(); c.translate(300, 500); c.rotate(-0.2);
  c.beginPath(); c.ellipse(0, 0, 200, 300, 0, 0, Math.PI * 2); fillOl(c, '#f3cf8c', 12);
  for (const [x, y, r] of [[-60, -120, 30], [70, -40, 36], [-30, 90, 28], [60, 170, 24], [-90, 10, 22]]) { ell(c, x, y, r, r * 0.7); c.fillStyle = '#b8743a'; c.fill(); }
  c.restore();
}
export function drawStar(c) {
  c.clearRect(0, 0, 600, 1000);
  c.save(); c.translate(300, 500); c.beginPath();
  for (let k = 0; k < 8; k++) { const r = k % 2 ? 70 : 260, a = k * Math.PI / 4; c.lineTo(Math.sin(a) * r, -Math.cos(a) * r); }
  c.closePath(); c.fillStyle = '#ffffff'; c.fill(); c.lineWidth = 10; c.strokeStyle = '#ffe27a'; c.stroke(); c.restore();
}
export function drawSign(c, p) {
  c.clearRect(0, 0, 600, 1000);
  rr(c, 40, 380, 520, 300, 40); c.fillStyle = p.bg || '#ffd23f'; c.fill(); ol(c, 14);
  c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillStyle = p.fg || PLUM;
  c.font = `bold ${p.size || 150}px sans-serif`; c.fillText(p.text, 300, p.sub ? 500 : 530);
  if (p.sub) { c.font = 'bold 70px sans-serif'; c.fillText(p.sub, 300, 615); }
}

// ---------- student narrator (school uniform) and night guard ----------
const SHIRT_W = '#f2f2f4', TIE = '#2b3f8a', TROUS = '#2b2f45', SHOE_B = '#2a2026';
export function drawStudent(c, p) {
  c.clearRect(0, 0, 600, 1000);
  if (!p.sit) for (const [lx, sd] of [[255, -1], [345, 1]]) {
    c.save(); c.translate(lx, 720); c.rotate(sd * (p.run || 0) * 0.35);
    rr(c, -40, -10, 80, 245, 34); fillOl(c, TROUS); ell(c, 14, 230, 58, 26); fillOl(c, SHOE_B); c.restore();
  }
  rr(c, 190, 440, 220, 300, 70); fillOl(c, SHIRT_W);
  if (p.sit) { for (const lx of [245, 355]) { ell(c, lx, 770, 42, 24); fillOl(c, SHOE_B); ell(c, lx, 700, 62, 70); fillOl(c, TROUS); } }
  c.beginPath(); c.moveTo(300, 455); c.lineTo(280, 600); c.lineTo(300, 640); c.lineTo(320, 600); c.closePath(); fillOl(c, TIE, 6);
  const A = { hang: [[178, 700], [422, 700]], cheer: [[120, 330], [480, 330]], knees: [[250, 660], [350, 660]], mouth: [[270, 430], [330, 430]], up: [[150, 420], [450, 420]],
    run: [[150 + 60 * (p.run || 0), 640], [450 + 60 * (p.run || 0), 600]], phone: [[262, 560], [338, 560]] }[p.arms || 'hang'];
  const sh = [[205, 500], [395, 500]];
  for (let k = 0; k < 2; k++) { limb(c, sh[k][0], sh[k][1], A[k][0], A[k][1], 42, SHIRT_W); }
  ell(c, 300, 330, 128, 142); fillOl(c, SKIN, 10);
  ell(c, 172, 345, 22, 34); fillOl(c, SKIN, 8); ell(c, 428, 345, 22, 34); fillOl(c, SKIN, 8);
  c.beginPath(); c.moveTo(172, 300); c.quadraticCurveTo(180, 170, 300, 178); c.quadraticCurveTo(420, 170, 428, 300); c.quadraticCurveTo(380, 240, 300, 240); c.quadraticCurveTo(220, 240, 172, 300); c.closePath(); fillOl(c, '#2a1a22', 9);
  const e = p.expr || 'smile', ly = p.look || 0;
  if (e === 'grin') { c.lineWidth = 9; c.strokeStyle = PLUM; for (const ex of [252, 348]) { c.beginPath(); c.arc(ex, 338, 24, Math.PI * 1.1, Math.PI * 1.9); c.stroke(); } }
  else if (e === 'scared') eyes(c, 34, 40, 9, 0, ly);
  else if (e === 'worry') eyes(c, 30, 34, 12, 0, ly);
  else eyes(c, 28, 32, 13, 0, ly);
  if (e === 'scared') brows(c, 26, 8); else if (e === 'worry') brows(c, 18, 9); else brows(c, 16, 0);
  c.lineWidth = 9; c.strokeStyle = PLUM;
  if (p.arms === 'mouth') { /* hands cover the mouth */ for (const hx of [270, 330]) { ell(c, hx, 420, 34, 30); fillOl(c, SKIN, 8); } }
  else if (e === 'grin') { c.beginPath(); c.arc(300, 380, 46, 0.12 * Math.PI, 0.88 * Math.PI); c.closePath(); fillOl(c, '#7a2033', 8); }
  else if (e === 'scared') { ell(c, 300, 414, 14, 18); fillOl(c, '#7a2033', 7); }
  else if (e === 'worry') { c.beginPath(); c.arc(300, 440, 28, 1.2 * Math.PI, 1.8 * Math.PI); c.stroke(); }
  else { c.beginPath(); c.arc(300, 385, 30, 0.2 * Math.PI, 0.8 * Math.PI); c.stroke(); }
  if (p.arms === 'cheer' || p.arms === 'knees' || p.arms === 'up') for (let k = 0; k < 2; k++) { ell(c, A[k][0], A[k][1], 30, 30); fillOl(c, SKIN, 8); }
  if (p.arms === 'hang' || p.arms === 'run') for (let k = 0; k < 2; k++) { ell(c, A[k][0], A[k][1], 30, 30); fillOl(c, SKIN, 8); }
  if (p.arms === 'phone') {
    // phone held at the chest, screen facing the kid; its glow lights the face from below
    const g = c.createRadialGradient(300, 470, 10, 300, 470, 260); g.addColorStop(0, 'rgba(170,210,255,0.55)'); g.addColorStop(1, 'rgba(170,210,255,0)');
    c.fillStyle = g; c.fillRect(40, 200, 520, 520);
    rr(c, 262, 500, 76, 110, 12); fillOl(c, '#1b1d2a', 7); rr(c, 270, 508, 60, 94, 8); c.fillStyle = '#bfe0ff'; c.fill();
    for (let k = 0; k < 2; k++) { ell(c, A[k][0], A[k][1], 28, 28); fillOl(c, SKIN, 8); }
  }
}

// ---------- the thing in the school: very tall, faded old uniform, pale blank face ----------
// p: {tilt (rad), reach 0..1, fade 0..1}
export function drawEntity(c, p) {
  c.clearRect(0, 0, 600, 1000);
  const INK = '#120a16', OLDSH = '#8d8a92', OLDSH_D = '#6d6a74', TR = '#15141c', FACE = '#dcd9e2';
  c.save(); c.globalAlpha = 1 - (p.fade || 0);
  // long thin legs
  for (const lx of [262, 338]) { rr(c, lx - 26, 560, 52, 420, 22); fillOl(c, TR, 8); }
  // narrow torso in a faded school shirt and a torn tie
  rr(c, 205, 250, 190, 340, 50); fillOl(c, OLDSH, 9);
  c.beginPath(); c.moveTo(300, 262); c.lineTo(284, 400); c.lineTo(300, 440); c.lineTo(310, 400); c.closePath(); fillOl(c, '#3a2430', 6);
  c.globalAlpha *= 0.5; for (const [x, y, r] of [[250, 470, 22], [345, 330, 16], [330, 520, 26]]) { ell(c, x, y, r, r * 0.7); c.fillStyle = OLDSH_D; c.fill(); }
  c.globalAlpha = 1 - (p.fade || 0);
  // arms far too long: hands hang below the knees, reaching forward a little with p.reach
  const r = p.reach || 0;
  for (const [sx, d] of [[218, -1], [382, 1]]) {
    const hx = sx + d * (18 - 40 * r), hy = 860 - 260 * r;
    limb(c, sx, 290, hx, hy, 26, OLDSH);
    c.beginPath(); c.moveTo(hx - 14, hy); for (let k = 0; k < 4; k++) { c.lineTo(hx - 18 + k * 12, hy + 70); c.lineTo(hx - 12 + k * 12, hy + 8); }
    c.closePath(); fillOl(c, '#cfcad6', 6);
  }
  // neck and blank oval face, tilted
  rr(c, 285, 200, 30, 60, 10); fillOl(c, FACE, 7);
  c.save(); c.translate(300, 150); c.rotate(p.tilt || 0);
  ell(c, 0, 0, 82, 112); fillOl(c, FACE, 10);
  // the faint suggestion of where eyes should be: two shallow shadows, nothing in them
  c.globalAlpha *= 0.22; ell(c, -32, -10, 22, 12); c.fillStyle = '#5b5068'; c.fill(); ell(c, 32, -10, 22, 12); c.fill();
  c.restore();
  // short wet hair stuck to the top of the head
  c.globalAlpha = 1 - (p.fade || 0);
  c.save(); c.translate(300, 150); c.rotate(p.tilt || 0);
  c.beginPath(); c.moveTo(-84, -10); c.quadraticCurveTo(-80, -118, 0, -114); c.quadraticCurveTo(80, -118, 84, -10);
  c.quadraticCurveTo(70, -70, 40, -60); c.lineTo(20, -20); c.lineTo(0, -64); c.lineTo(-24, -14); c.lineTo(-44, -62); c.quadraticCurveTo(-70, -70, -84, -10);
  c.closePath(); fillOl(c, INK, 8);
  c.restore(); c.restore();
}

// bare footprint (top view, heel at the bottom), pale and frosty
export function drawPrint(c) {
  c.clearRect(0, 0, 256, 256);
  c.fillStyle = 'rgba(214,232,255,0.95)';
  ell(c, 128, 150, 46, 78); c.fill();
  ell(c, 128, 210, 40, 34); c.fill();
  for (const [x, y, r] of [[96, 62, 15], [120, 52, 13], [141, 54, 11], [158, 62, 10], [172, 74, 9]]) { ell(c, x, y, r, r * 1.2); c.fill(); }
}
const UNI = '#1f2a44', UNI_D = '#151c30';
export function drawGuard(c, p) {
  c.clearRect(0, 0, 600, 1000);
  const step = p.step || 0;
  for (const [lx, sd] of [[255, -1], [345, 1]]) {
    c.save(); c.translate(lx, 720); c.rotate(sd * step * 0.25);
    rr(c, -42, -10, 84, 245, 30); fillOl(c, UNI_D); ell(c, 12, 240, 60, 26); fillOl(c, '#111118'); c.restore();
  }
  rr(c, 180, 440, 240, 300, 60); fillOl(c, UNI);
  if (!p.back) { rr(c, 215, 480, 40, 30, 6); fillOl(c, '#d8b84a', 6); c.beginPath(); c.moveTo(300, 450); c.lineTo(300, 740); c.lineWidth = 6; c.strokeStyle = UNI_D; c.stroke(); }
  // arms: left hangs, right holds the torch forward
  limb(c, 205, 500, 175, 710, 44, UNI); ell(c, 175, 710, 30, 30); fillOl(c, SKIN, 8);
  const tx = p.back ? 470 : 460, ty = p.back ? 560 : 600;
  limb(c, 395, 500, tx, ty, 44, UNI);
  rr(c, tx - 12, ty - 70, 36, 90, 10); fillOl(c, '#3a3a44', 7); ell(c, tx + 6, ty - 72, 24, 12); c.fillStyle = '#fff6c0'; c.fill();
  ell(c, tx, ty, 30, 30); fillOl(c, SKIN, 8);
  // head
  ell(c, 300, 330, 128, 142); fillOl(c, p.back ? '#3a2a22' : SKIN, 10);
  // cap with a low visor: eyes stay in shadow
  c.beginPath(); c.ellipse(300, 245, 136, 70, 0, Math.PI, 0); c.closePath(); fillOl(c, UNI);
  if (!p.back) {
    rr(c, 160, 236, 280, 40, 18); fillOl(c, '#0f1424', 8);
    c.globalAlpha = 0.55; ell(c, 300, 300, 118, 40); c.fillStyle = '#0a0d1a'; c.fill(); c.globalAlpha = 1;
    const dx = p.look || 0;
    for (const ex of [258, 342]) { ell(c, ex + dx * 14, 312, 9, 6); c.fillStyle = '#f4f0d8'; c.fill(); }
    c.beginPath(); c.moveTo(270, 410); c.lineTo(330, 410); c.lineWidth = 8; c.strokeStyle = PLUM; c.stroke();
  } else { ell(c, 300, 300, 30, 8); c.fillStyle = UNI_D; c.fill(); }
  ell(c, 300, 200, 18, 12); fillOl(c, '#d8b84a', 6);
}
