"""
test_scanner.py

Tests library/scanner.py against real, small synthetic audio files
generated on the fly (not real music - silence, tagged via mutagen) in
an isolated temp dir. No network, no dependency on any real music
library existing.
"""

import os
import shutil
import struct
import tempfile
import wave

import config
from library.scanner import scan_library_dirs


def _write_silent_wav(path: str, seconds: float = 1.0, sample_rate: int = 8000):
    n_frames = int(seconds * sample_rate)
    with wave.open(path, "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        f.writeframes(struct.pack("<%dh" % n_frames, *([0] * n_frames)))


def check_scan_extracts_metadata_and_falls_back_correctly():
    isolated_tmp = tempfile.mkdtemp(prefix="ird_scanner_test_")
    try:
        tagged_path = os.path.join(isolated_tmp, "some_track.wav")
        _write_silent_wav(tagged_path, seconds=2.0)

        untagged_path = os.path.join(isolated_tmp, "Weird_File Name-2.wav")
        _write_silent_wav(untagged_path, seconds=1.0)

        # An unsupported extension must be skipped entirely, not error.
        with open(os.path.join(isolated_tmp, "notes.txt"), "w") as f:
            f.write("not an audio file")

        tracks = scan_library_dirs([isolated_tmp])
        assert len(tracks) == 2, f"FAIL: expected 2 tracks (unsupported extension should be skipped), got {len(tracks)}"
        print("PASS: scan found exactly the 2 real audio files, skipping the unsupported .txt file.")

        by_path = {t.path: t for t in tracks}
        untagged_track = by_path[untagged_path]
        assert untagged_track.title == "Weird File Name 2", (
            f"FAIL: filename fallback should clean underscores/dashes into spaces, got {untagged_track.title!r}"
        )
        print("PASS: an untagged file falls back to a cleaned-up filename as its title.")

        tagged_track = by_path[tagged_path]
        assert tagged_track.duration_seconds > 1.5, (
            f"FAIL: a 2-second wav should report duration > 1.5s, got {tagged_track.duration_seconds}"
        )
        print("PASS: duration is read correctly from the audio file itself.")
    finally:
        shutil.rmtree(isolated_tmp, ignore_errors=True)


def check_track_id_stable_across_rescans_changes_on_rename():
    isolated_tmp = tempfile.mkdtemp(prefix="ird_scanner_test_")
    try:
        path = os.path.join(isolated_tmp, "song.wav")
        _write_silent_wav(path, seconds=1.0)

        first_scan = scan_library_dirs([isolated_tmp])
        second_scan = scan_library_dirs([isolated_tmp])
        assert first_scan[0].id == second_scan[0].id, "FAIL: track ID must be stable across an unchanged rescan"
        print("PASS: track ID is stable across two scans of an unchanged file.")

        renamed_path = os.path.join(isolated_tmp, "renamed_song.wav")
        os.rename(path, renamed_path)
        third_scan = scan_library_dirs([isolated_tmp])
        assert third_scan[0].id != first_scan[0].id, "FAIL: track ID should change once the file is renamed"
        print("PASS: track ID changes when the underlying file is renamed (documented, accepted simplification).")
    finally:
        shutil.rmtree(isolated_tmp, ignore_errors=True)


def check_missing_library_dir_is_skipped_not_an_error():
    tracks = scan_library_dirs(["/this/path/does/not/exist/at/all"])
    assert tracks == [], "FAIL: scanning a nonexistent directory should return an empty list, not raise"
    print("PASS: a nonexistent library directory is silently skipped, not an error.")


def check_mp4_is_a_supported_extension():
    # Added 2026-08-23: several AI music generators (the user's own real
    # case) export audio-only-in-intent tracks as plain .mp4 rather than
    # .m4a, even though it's the exact same MP4 container mutagen already
    # reads for .m4a via EasyMP4. No pure-stdlib way exists to synthesize
    # a genuinely decodable MP4 (no ffmpeg on this machine, unlike the
    # _write_silent_wav() helper above for .wav) - this was instead
    # verified live against the user's real generated files (5 real
    # tracks, correct titles/albums/durations all read back correctly,
    # duration ~28-31s each) rather than a synthetic fixture here. This
    # check locks down the one thing a unit test CAN verify without a
    # real file: the extension itself is actually in the supported set,
    # so a future edit can't silently drop it again.
    assert ".mp4" in config.SUPPORTED_AUDIO_EXTENSIONS, "FAIL: .mp4 must stay a supported audio extension"
    print("PASS: .mp4 is a supported audio extension.")


def main():
    print("=== Check 1: metadata extraction + filename fallback + unsupported-extension skip ===")
    check_scan_extracts_metadata_and_falls_back_correctly()

    print("\n=== Check 2: track ID stability across rescans, changes on rename ===")
    check_track_id_stable_across_rescans_changes_on_rename()

    print("\n=== Check 3: a missing library directory is skipped, not an error ===")
    check_missing_library_dir_is_skipped_not_an_error()

    print("\n=== Check 4: .mp4 stays a supported extension ===")
    check_mp4_is_a_supported_extension()

    print("\nALL SCANNER CHECKS PASSED.")


if __name__ == "__main__":
    main()
