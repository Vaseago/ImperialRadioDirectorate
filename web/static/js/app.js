const player = document.getElementById("player");
const trackListEl = document.getElementById("track-list");
const statusEl = document.getElementById("status");

let tracks = [];
let currentIndex = -1;

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
    const label = track.artist ? `${track.artist} - ${track.title}` : track.title;
    li.textContent = label;
    li.className = index === currentIndex ? "playing" : "";
    li.addEventListener("click", () => playTrackAt(index));
    trackListEl.appendChild(li);
  });
}

function playTrackAt(index) {
  if (index < 0 || index >= tracks.length) return;
  currentIndex = index;
  player.src = `/api/library/tracks/${tracks[index].id}/stream`;
  player.play();
  renderTrackList();
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

player.addEventListener("ended", () => {
  playTrackAt(currentIndex + 1);
});

loadTracks();
