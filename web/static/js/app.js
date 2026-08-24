const player = document.getElementById("player");
const trackListEl = document.getElementById("track-list");
const statusEl = document.getElementById("status");
const windowTitleEl = document.getElementById("window-title");
const panelTickerEl = document.getElementById("panel-ticker");
const armPivotEl = document.getElementById("arm-pivot");
const playBtn = document.getElementById("play-btn");
const playGlyph = document.getElementById("play-glyph");

let tracks = [];
let currentIndex = -1;

function trackLabel(track) {
  return track.artist ? `${track.artist} - ${track.title}` : track.title;
}

function formatDuration(seconds) {
  if (!seconds || seconds <= 0) return "";
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${String(s).padStart(2, "0")}`;
}

async function loadTracks() {
  const res = await fetch("/api/library/tracks");
  tracks = await res.json();
  renderTrackList();
  statusEl.textContent = `${tracks.length} track(s) in library.`;
}

function renderTrackList() {
  trackListEl.innerHTML = "";
  tracks.forEach((track, index) => {
    const li = document.createElement("li");
    li.className = index === currentIndex ? "playing" : "";
    li.addEventListener("click", () => playTrackAt(index));

    const title = document.createElement("span");
    title.className = "track-title";
    title.textContent = trackLabel(track);
    li.appendChild(title);

    const duration = document.createElement("span");
    duration.className = "track-duration";
    duration.textContent = formatDuration(track.duration_seconds);
    li.appendChild(duration);

    trackListEl.appendChild(li);
  });
}

function playTrackAt(index) {
  if (index < 0 || index >= tracks.length) return;
  currentIndex = index;
  player.src = `/api/library/tracks/${tracks[index].id}/stream`;
  player.play();
  renderTrackList();
  updateNowPlaying();
}

function updateNowPlaying() {
  const track = tracks[currentIndex];
  const label = track ? trackLabel(track).toUpperCase() : "NO SIGNAL";
  windowTitleEl.textContent = track ? `NOW PLAYING — ${label}` : "NO SIGNAL";
  panelTickerEl.textContent = track ? label : "SELECT A TRACK";
}

function updatePlaybackUi() {
  const isPlaying = !player.paused && !player.ended && currentIndex >= 0;
  armPivotEl.classList.toggle("spinning", isPlaying);
  playGlyph.className = `pad-glyph ${isPlaying ? "pause" : "play"}`;
  playBtn.setAttribute("aria-label", isPlaying ? "Pause" : "Play");
}

document.getElementById("rescan-btn").addEventListener("click", async () => {
  statusEl.textContent = "Rescanning...";
  const res = await fetch("/api/library/rescan", {
    method: "POST",
    headers: { "X-IRD-Request": "1" },
  });
  const data = await res.json();
  statusEl.textContent = `Rescan complete: ${data.track_count} track(s) found.`;
  await loadTracks();
});

document.getElementById("prev-btn").addEventListener("click", () => {
  playTrackAt(currentIndex - 1);
});

document.getElementById("next-btn").addEventListener("click", () => {
  playTrackAt(currentIndex + 1);
});

playBtn.addEventListener("click", () => {
  if (currentIndex < 0) {
    playTrackAt(0);
    return;
  }
  if (player.paused) {
    player.play();
  } else {
    player.pause();
  }
});

player.addEventListener("play", updatePlaybackUi);
player.addEventListener("pause", updatePlaybackUi);
player.addEventListener("ended", () => {
  playTrackAt(currentIndex + 1);
});

updatePlaybackUi();
loadTracks();
