"""Recorded .bag playback, paced or as-fast-as-possible.

Copy-adapted from v1 (realtime/person/realtime_person.py
open_bag_realtime and mediapipe/extract_landmarks_to_csv.py open_bag)
with v2's prompt end-of-source lesson: a 1 s wait timeout plus a
playback-status check, so the exit tail never inflates sustained-fps
figures.

paced=True plays at the recorded pacing (set_real_time(True)) -- the
live-camera stand-in for latency measurement; paced=False processes
every frame as fast as possible -- extraction and deterministic
grading.
"""
import numpy as np
import pyrealsense2 as rs


class BagSource:
    def __init__(self, bag_path, paced):
        self.pipeline = rs.pipeline()
        config = rs.config()
        config.enable_device_from_file(str(bag_path), repeat_playback=False)
        self.profile = self.pipeline.start(config)
        self._playback = self.profile.get_device().as_playback()
        self._playback.set_real_time(bool(paced))
        self.intrinsics = (self.profile.get_stream(rs.stream.color)
                           .as_video_stream_profile().get_intrinsics())
        self.depth_scale = (self.profile.get_device().first_depth_sensor()
                            .get_depth_scale())
        self._align = rs.align(rs.stream.color)
        self._t0_ms = None

    def frames(self, max_frames=None):
        """Yield (frame_idx, t_s, color_bgr, depth_u16). t_s is the
        session clock: hardware timestamp minus the first frame's."""
        idx = 0
        while max_frames is None or idx < max_frames:
            try:
                fr = self.pipeline.wait_for_frames(timeout_ms=1000)
            except RuntimeError:
                break                            # timeout = end of bag
            if (self._playback.current_status()
                    == rs.playback_status.stopped):
                break
            fr = self._align.process(fr)
            color = fr.get_color_frame()
            depth = fr.get_depth_frame()
            if not color or not depth:
                continue
            ts = color.get_timestamp()
            if self._t0_ms is None:
                self._t0_ms = ts
            yield (idx, (ts - self._t0_ms) / 1000.0,
                   np.asanyarray(color.get_data()),
                   np.asanyarray(depth.get_data()))
            idx += 1

    def close(self):
        self.pipeline.stop()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
        return False
