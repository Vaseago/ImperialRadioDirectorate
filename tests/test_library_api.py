"""
test_library_api.py

FastAPI TestClient coverage for web/routers/library.py - real lifespan
runs (library scan happens for real against an isolated temp dir), no
mocking of the scan itself. Critically asserts Range-request support on
the stream endpoint, complementing the manual browser/desktop-shell
scrubbing checks described in CLAUDE.md.
"""

import os
import shutil
import struct
import tempfile
import wave
from unittest import mock

import config


def _write_silent_wav(path: str, seconds: float = 1.0, sample_rate: int = 8000):
    n_frames = int(seconds * sample_rate)
    with wave.open(path, "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        f.writeframes(struct.pack("<%dh" % n_frames, *([0] * n_frames)))


def check_list_and_stream_and_range_and_rescan():
    isolated_tmp = tempfile.mkdtemp(prefix="ird_api_test_")
    try:
        track_path = os.path.join(isolated_tmp, "test_song.wav")
        _write_silent_wav(track_path, seconds=1.0)

        with mock.patch.object(config, "MUSIC_LIBRARY_DIRS", [isolated_tmp]):
            from fastapi.testclient import TestClient
            from web.server import app

            with TestClient(app) as client:
                resp = client.get("/api/library/tracks")
                assert resp.status_code == 200, f"FAIL: expected 200, got {resp.status_code}"
                tracks = resp.json()
                assert len(tracks) == 1, f"FAIL: expected 1 track from the isolated library dir, got {len(tracks)}"
                assert tracks[0]["title"] == "test song", f"FAIL: unexpected title {tracks[0]['title']!r}"
                print("PASS: GET /api/library/tracks lists the real scanned track with correct fallback title.")

                track_id = tracks[0]["id"]

                full_resp = client.get(f"/api/library/tracks/{track_id}/stream")
                assert full_resp.status_code == 200, f"FAIL: expected 200 for a plain stream request, got {full_resp.status_code}"
                full_size = len(full_resp.content)
                assert full_size > 0, "FAIL: streamed file should not be empty"
                print(f"PASS: GET .../stream returns 200 with the full file ({full_size} bytes).")

                range_resp = client.get(
                    f"/api/library/tracks/{track_id}/stream",
                    headers={"Range": "bytes=0-99"},
                )
                assert range_resp.status_code == 206, f"FAIL: a Range request must return 206, got {range_resp.status_code}"
                assert "content-range" in range_resp.headers, "FAIL: a 206 response must include Content-Range"
                assert len(range_resp.content) == 100, f"FAIL: expected exactly 100 bytes for bytes=0-99, got {len(range_resp.content)}"
                print(f"PASS: Range request returns 206 with Content-Range ({range_resp.headers['content-range']}) and the correct byte count.")

                missing_resp = client.get("/api/library/tracks/doesnotexist/stream")
                assert missing_resp.status_code == 404, f"FAIL: expected 404 for an unknown track id, got {missing_resp.status_code}"
                print("PASS: an unknown track id returns 404, not a crash.")

                no_header_resp = client.post("/api/library/rescan")
                assert no_header_resp.status_code == 403, (
                    f"FAIL: rescan without the CSRF header must be rejected (403), got {no_header_resp.status_code}"
                )
                print("PASS: POST /api/library/rescan without X-IRD-Request is rejected (CSRF guard working).")

                rescan_resp = client.post(
                    "/api/library/rescan", headers={"X-IRD-Request": "1"}
                )
                assert rescan_resp.status_code == 200, f"FAIL: expected 200, got {rescan_resp.status_code}"
                assert rescan_resp.json()["track_count"] == 1, "FAIL: rescan should still report 1 track"
                print("PASS: POST /api/library/rescan with the correct header succeeds and reports the right count.")
    finally:
        shutil.rmtree(isolated_tmp, ignore_errors=True)


def main():
    print("=== Check 1: list/stream/Range/404/rescan+CSRF, against a real isolated library dir ===")
    check_list_and_stream_and_range_and_rescan()

    print("\nALL LIBRARY API CHECKS PASSED.")


if __name__ == "__main__":
    main()
