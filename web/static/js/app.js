// Sent on every fetch() to a route that requires it server-side (see
// web/security.py's require_same_origin_header) - ported from the
// sibling apps' identical convention, header renamed X-IRD-Request.
const SAME_ORIGIN_HEADERS = { "X-IRD-Request": "1" };

const player = document.getElementById("player");
const statusEl = document.getElementById("status");
const restartBannerEl = document.getElementById("restart-banner");
const appUpdateBtnEl = document.getElementById("app-update-btn");
const nowPlayingEl = document.getElementById("now-playing");
const dialSvg = document.getElementById("dial-svg");
const ticksG = document.getElementById("ticks");
const knurlG = document.getElementById("knurl");
const markersG = document.getElementById("station-markers");
const needleEl = document.getElementById("needle");
const freqReadoutEl = document.getElementById("freq-readout");
const barsWrap = document.getElementById("signal-bars");
const signalLabelEl = document.getElementById("signal-label");
const lockStateEl = document.getElementById("lock-state");
const playStateEl = document.getElementById("play-state");
const volumeSlider = document.getElementById("volume-slider");

const cx = 150, cy = 150, r = 92;
const ARC_MIN = -70, ARC_MAX = 70;
const FREQ_MIN = 88.1, FREQ_MAX = 108.3;
const CENTER_RADIUS = 20;

// A commercial plays instead of the next station pick roughly this
// often, whenever the pool isn't empty - a real, working mechanism from
// day one even with zero ad files present (it simply never fires).
const AD_CHANCE = 0.25;

let stations = []; // [{ name, angle, freq, tracks: [track,...] }]
let commercials = [];
let currentIndex = 0;
let playing = false;
let lastTrackId = null;
let playingAd = false;

// Real tracks run ~30s - looping the same track for a full 1-1.5 minute
// "airtime" before moving on reads much more like a real station than
// advancing every 30s would. Randomized per track (not a fixed 60s) so
// consecutive plays don't all feel identically timed. Commercials are
// deliberately NOT looped - a real ad break is short and singular, not
// repeated back-to-back. trackElapsedSeconds accumulates real elapsed
// time across loops (via player.duration each time a loop completes,
// not assumed/hardcoded), so this works correctly regardless of a
// track's own real length.
const TRACK_AIRTIME_MIN_SECONDS = 60;
const TRACK_AIRTIME_MAX_SECONDS = 90;
let trackAirtimeTargetSeconds = 0;
let trackElapsedSeconds = 0;

function polar(angleDeg, radius) {
  const a = (angleDeg - 90) * Math.PI / 180;
  return { x: cx + radius * Math.cos(a), y: cy + radius * Math.sin(a) };
}

function buildTicks() {
  ticksG.innerHTML = "";
  for (let a = -80; a <= 80; a += 4) {
    const major = a % 20 === 0;
    const p1 = polar(a, r + (major ? 14 : 8));
    const p2 = polar(a, r + 20);
    const el = document.createElementNS("http://www.w3.org/2000/svg", "line");
    el.setAttribute("x1", p1.x); el.setAttribute("y1", p1.y);
    el.setAttribute("x2", p2.x); el.setAttribute("y2", p2.y);
    el.setAttribute("class", "tick" + (major ? " major" : ""));
    ticksG.appendChild(el);
  }
}

function buildKnurl() {
  knurlG.innerHTML = "";
  for (let a = 0; a < 360; a += 12) {
    const p1 = { x: cx + 40 * Math.cos(a * Math.PI / 180), y: cy + 40 * Math.sin(a * Math.PI / 180) };
    const p2 = { x: cx + 46 * Math.cos(a * Math.PI / 180), y: cy + 46 * Math.sin(a * Math.PI / 180) };
    const el = document.createElementNS("http://www.w3.org/2000/svg", "line");
    el.setAttribute("x1", p1.x); el.setAttribute("y1", p1.y);
    el.setAttribute("x2", p2.x); el.setAttribute("y2", p2.y);
    el.setAttribute("class", "knurl");
    knurlG.appendChild(el);
  }
}

function buildStationMarkers() {
  markersG.innerHTML = "";
  stations.forEach((st, i) => {
    const dotPos = polar(st.angle, r);
    const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
    g.setAttribute("class", "station-marker");
    g.dataset.index = i;
    g.innerHTML = `<circle class="hit" cx="${dotPos.x}" cy="${dotPos.y}" r="12"/><circle class="dot" cx="${dotPos.x}" cy="${dotPos.y}" r="3.4"/>`;
    g.addEventListener("click", () => tuneByIndex(i));
    markersG.appendChild(g);
  });
}

function groupIntoStations(tracks) {
  const byStation = new Map();
  for (const t of tracks) {
    if (!byStation.has(t.station)) byStation.set(t.station, []);
    byStation.get(t.station).push(t);
  }
  const names = Array.from(byStation.keys()).sort((a, b) => a.localeCompare(b));
  const real = names.map(name => ({ name, tracks: byStation.get(name) }));

  const all = [];
  if (real.length > 1) {
    all.push({ name: "All Stations", tracks: tracks.slice() });
  }
  all.push(...real);

  const n = all.length;
  return all.map((st, i) => {
    const angle = n <= 1 ? 0 : ARC_MIN + (i * (ARC_MAX - ARC_MIN)) / (n - 1);
    const freq = n <= 1 ? FREQ_MIN : FREQ_MIN + (i * (FREQ_MAX - FREQ_MIN)) / (n - 1);
    return { ...st, angle, freq: freq.toFixed(1) };
  });
}

function pickRandomTrack(pool) {
  if (pool.length === 0) return null;
  if (pool.length === 1) return pool[0];
  let pick;
  do { pick = pool[Math.floor(Math.random() * pool.length)]; } while (pick.id === lastTrackId);
  return pick;
}

function playTrack(track, isAd) {
  if (!track) return;
  lastTrackId = track.id;
  playingAd = isAd;
  player.src = `/api/library/tracks/${track.id}/stream`;
  player.play();
  nowPlayingEl.textContent = track.title;
  nowPlayingEl.classList.toggle("ad", isAd);
  nowPlayingEl.classList.remove("paused");
  trackElapsedSeconds = 0;
  trackAirtimeTargetSeconds = isAd
    ? 0
    : TRACK_AIRTIME_MIN_SECONDS + Math.random() * (TRACK_AIRTIME_MAX_SECONDS - TRACK_AIRTIME_MIN_SECONDS);
}

function playNext() {
  if (stations.length === 0) return;
  if (!playingAd && commercials.length > 0 && Math.random() < AD_CHANCE) {
    playTrack(pickRandomTrack(commercials), true);
    return;
  }
  playTrack(pickRandomTrack(stations[currentIndex].tracks), false);
}

function randomizeStatic() {
  Array.from(barsWrap.children).forEach(b => {
    b.className = "";
    b.style.height = (6 + Math.random() * 18) + "px";
    b.style.background = "var(--static)";
    b.style.opacity = 0.35 + Math.random() * 0.3;
  });
}
function lockSignal() {
  barsWrap.classList.add("locked");
  Array.from(barsWrap.children).forEach((b, i) => {
    b.style.height = (8 + Math.abs(Math.sin(i * 0.7)) * 24) + "px";
    b.className = "on" + (i % 3 === 0 ? " gold" : "");
  });
}
function unlockSignal() {
  barsWrap.classList.remove("locked");
}

function tune(index, autoplay = true) {
  if (stations.length === 0) return;
  currentIndex = Math.max(0, Math.min(stations.length - 1, index));
  const st = stations[currentIndex];
  needleEl.style.transform = `rotate(${st.angle}deg)`;
  freqReadoutEl.textContent = st.freq;
  document.querySelectorAll(".station-marker").forEach(m => m.classList.toggle("active", Number(m.dataset.index) === currentIndex));
  signalLabelEl.textContent = "SIGNAL LOCKED";
  lockStateEl.textContent = "LOCKED";
  lockStateEl.classList.add("locked");
  lockSignal();
  if (!autoplay) {
    // Initial page load only - show the tuned state without triggering
    // playback the browser would silently block anyway (no user
    // gesture yet), which would otherwise desync "PLAYING" from what's
    // actually audible.
    nowPlayingEl.textContent = st.name;
    nowPlayingEl.classList.remove("ad");
    return;
  }
  // Turning the dial always produces sound, like a real radio - it
  // doesn't matter whether playback was already running; picking a
  // station is itself a "play this now" action, distinct from the
  // hub's dedicated center-click pause/resume toggle below.
  playing = true;
  playStateEl.textContent = "PLAYING";
  playStateEl.classList.add("playing");
  playNext();
}

function tuneByIndex(i) { tune(i); }

// Generated white noise (no audio file needed) for the "empty library,
// no signal" case - a real radio hisses static between stations rather
// than going silent. Only ever started from a real user gesture (the
// hub's center click via setPlaying), same autoplay-policy reasoning
// as real track playback.
let audioCtx = null;
let noiseSource = null;

function startStatic() {
  if (noiseSource) return;
  if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  const bufferSeconds = 2;
  const buffer = audioCtx.createBuffer(1, audioCtx.sampleRate * bufferSeconds, audioCtx.sampleRate);
  const data = buffer.getChannelData(0);
  for (let i = 0; i < data.length; i++) data[i] = Math.random() * 2 - 1;

  const source = audioCtx.createBufferSource();
  source.buffer = buffer;
  source.loop = true;
  const gain = audioCtx.createGain();
  gain.gain.value = 0.06;
  source.connect(gain).connect(audioCtx.destination);
  source.start();
  noiseSource = source;
  nowPlayingEl.textContent = "STATIC";
  nowPlayingEl.classList.remove("paused", "ad");
}

function stopStatic() {
  if (!noiseSource) return;
  noiseSource.stop();
  noiseSource.disconnect();
  noiseSource = null;
}

function setPlaying(next) {
  playing = next;
  playStateEl.textContent = playing ? "PLAYING" : "PAUSED";
  playStateEl.classList.toggle("playing", playing);
  nowPlayingEl.classList.toggle("paused", !playing);
  if (!playing) {
    player.pause();
    stopStatic();
    if (stations.length === 0) nowPlayingEl.textContent = "NO SIGNAL";
    return;
  }
  if (stations.length === 0) {
    startStatic();
    return;
  }
  if (player.src) {
    player.play();
  } else {
    playNext();
  }
}

function svgPoint(evt) {
  const pt = dialSvg.createSVGPoint();
  pt.x = evt.clientX;
  pt.y = evt.clientY;
  return pt.matrixTransform(dialSvg.getScreenCTM().inverse());
}

document.getElementById("hub-hit").addEventListener("click", (evt) => {
  const p = svgPoint(evt);
  const dist = Math.hypot(p.x - cx, p.y - cy);
  if (dist <= CENTER_RADIUS) {
    // Center always works, even with an empty library - it's the only
    // way to ever hear the static cue.
    setPlaying(!playing);
  } else if (stations.length === 0) {
    // Nothing to step between yet.
  } else if (p.x > cx) {
    tuneByIndex(currentIndex + 1);
  } else {
    tuneByIndex(currentIndex - 1);
  }
});

player.addEventListener("ended", () => {
  if (!playing) return;
  if (!playingAd) {
    trackElapsedSeconds += player.duration || 0;
    if (trackElapsedSeconds < trackAirtimeTargetSeconds) {
      player.currentTime = 0;
      player.play();
      return;
    }
  }
  playNext();
});

// Volume - persisted per-browser (localStorage, not server-side - this
// is a local listening preference, not app state) so it survives a
// reload/restart instead of always resetting to the 70 default.
const SAVED_VOLUME = localStorage.getItem("ird_volume");
const initialVolume = SAVED_VOLUME !== null ? Number(SAVED_VOLUME) : 70;
volumeSlider.value = String(initialVolume);
player.volume = initialVolume / 100;
volumeSlider.addEventListener("input", () => {
  const v = Number(volumeSlider.value);
  player.volume = v / 100;
  localStorage.setItem("ird_volume", String(v));
});

document.getElementById("rescan-btn").addEventListener("click", async () => {
  statusEl.textContent = "Rescanning...";
  const res = await fetch("/api/library/rescan", { method: "POST", headers: { "X-IRD-Request": "1" } });
  const data = await res.json();
  statusEl.textContent = `Rescan complete: ${data.track_count} track(s), ${data.commercial_count} commercial(s).`;
  await loadLibrary();
});

async function loadLibrary() {
  const [tracksRes, commercialsRes] = await Promise.all([
    fetch("/api/library/tracks"),
    fetch("/api/library/commercials"),
  ]);
  const tracks = await tracksRes.json();
  commercials = await commercialsRes.json();

  buildTicks();
  buildKnurl();
  stations = groupIntoStations(tracks);
  buildStationMarkers();

  if (stations.length === 0) {
    statusEl.textContent = "No tracks found. Drop audio files into music_library/ and rescan.";
    nowPlayingEl.textContent = "NO SIGNAL";
    unlockSignal();
    signalLabelEl.textContent = "NO SIGNAL";
    lockStateEl.textContent = "NO LOCK";
    lockStateEl.classList.remove("locked");
    return;
  }
  statusEl.textContent = `${tracks.length} track(s) across ${stations.length} station(s).`;
  tune(0, false);
}

for (let i = 0; i < 16; i++) barsWrap.appendChild(document.createElement("i"));
randomizeStatic();
setInterval(() => { if (!barsWrap.classList.contains("locked")) randomizeStatic(); }, 220);

setPlaying(false);
loadLibrary();

// ---------- Check for App Update (added 2026-08-30, ported from the
// sibling apps once IRD joined the Pi's always-on supervisor - user's
// own request: "lets get an update button on it that auto restarts the
// app [server]") ----------

let appUpdatePending = null;

// Only ever starts right after a supervised pull, never as a permanent
// background heartbeat.
let restartPollTimer = null;

function showRestartBanner() {
  restartBannerEl.hidden = false;
  if (!restartPollTimer) restartPollTimer = setInterval(pollForRestartRecovery, 1000);
}

function hideRestartBanner() {
  restartBannerEl.hidden = true;
  if (restartPollTimer) {
    clearInterval(restartPollTimer);
    restartPollTimer = null;
  }
}

async function pollForRestartRecovery() {
  try {
    const res = await fetch("/api/app-update/status");
    if (res.ok) hideRestartBanner();
  } catch (e) {
    // still down - keep polling
  }
}

function applyAppUpdateStatus() {
  if (appUpdatePending) {
    appUpdateBtnEl.textContent = `Update Available (${appUpdatePending.commits_behind})`;
    appUpdateBtnEl.classList.add("pending");
  } else {
    appUpdateBtnEl.textContent = "Check for App Update";
    appUpdateBtnEl.classList.remove("pending");
  }
}

async function loadAppUpdateStatus() {
  const res = await fetch("/api/app-update/status");
  const data = await res.json();
  // A packaged build has no git checkout to pull against - hide the
  // control entirely rather than showing a button that can only ever
  // 404 (see web/routers/app_update.py's own _AVAILABLE gate).
  if (data.available === false) {
    appUpdateBtnEl.style.display = "none";
    return;
  }
  appUpdatePending = data.pending;
  applyAppUpdateStatus();
}

appUpdateBtnEl.addEventListener("click", async () => {
  if (!appUpdatePending) {
    appUpdateBtnEl.textContent = "Checking...";
    const res = await fetch("/api/app-update/check", { method: "POST", headers: SAME_ORIGIN_HEADERS });
    const data = await res.json();
    appUpdatePending = data.pending;
    applyAppUpdateStatus();
    statusEl.textContent = appUpdatePending
      ? `Update found (${appUpdatePending.commits_behind} commit(s) behind) - click "Check for App Update" again to pull it.`
      : "Already up to date.";
    if (!appUpdatePending) setTimeout(() => { statusEl.textContent = ""; }, 3000);
    return;
  }

  // Plain native confirm() here, not a custom modal like the sibling
  // apps (which avoid it specifically to hide the page's real origin/IP
  // in a shared-device confirm dialog) - this app is a single-user
  // personal device, and a whole modal system is disproportionate scope
  // just for this one button.
  const ok = confirm(
    `${appUpdatePending.commits_behind} commit(s) behind:\n\n${appUpdatePending.log}\n\nPull now? You'll need to restart the server afterward.`
  );
  if (!ok) return;

  appUpdateBtnEl.textContent = "Pulling...";
  const res = await fetch("/api/app-update/pull", { method: "POST", headers: SAME_ORIGIN_HEADERS });
  if (!res.ok) {
    const err = await res.json();
    statusEl.textContent = `Update failed: ${err.detail}`;
    await loadAppUpdateStatus();
    return;
  }
  const data = await res.json();
  appUpdatePending = null;
  applyAppUpdateStatus();
  if (data.self_restarting) {
    showRestartBanner();
    statusEl.textContent = "Decree received - the Directorate is realigning its systems.";
  } else {
    statusEl.textContent = "Update pulled - restart the server for the change to take effect.";
  }
});

loadAppUpdateStatus();
