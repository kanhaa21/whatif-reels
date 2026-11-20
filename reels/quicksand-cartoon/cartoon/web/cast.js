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
