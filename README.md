# Tracking and Reconstruction of Bi-Manual Object Handling Task Using RGB-D Sensing

This undergraduate thesis reconstructs a person's upper-body motion and the object they handle from one depth camera. It places the person, object and surrounding surfaces together in a calibrated 3D scene, and uses the object's motion to help recover wrists hidden from view.

The Python implementation combines Intel RealSense D435 RGB-D sensing, MediaPipe Pose landmarks, OpenCV ArUco marker tracking, swing-twist arm kinematics and object-assisted two-link inverse kinematics. Unity displays the reconstructed body and object in their shared coordinate frame.

```text
RealSense RGB-D -> synchronized frame broker
                    |                   |
              MediaPipe Pose       ArUco + IPPE pose
                    |                   |
              depth + kinematics <-- object pose + grasp offset
                    |                   |
                    +---- time-aligned merger ----+
                                                  |
                                      shared memory (PSI2)
                                                  |
                                        Unity reconstruction
```

## Thesis and defence

- [Final thesis PDF](Thesis_V9.pdf): methods, experiments, results and limitations.
- [Final defence presentation](Thesis_Defence_2026.pptx): original PowerPoint, including embedded videos and backup slides.

The thesis reports a median wrist discrepancy of 1.03 cm per arm against accepted depth-derived landmarks in the handover task (Section 7.3.2). This is consistency with the observed landmarks, rather than independent motion-capture accuracy. The synchronized implementation processed all 900 input frames at approximately 29 FPS in the recorded replay reported in Chapter 8. These conditions do not establish performance for every live scene.

## Repository contents

| Path | Contents |
| --- | --- |
| `Python/runtime/` | Synchronized capture, person and object pipelines, recovery, calibration and stream merger. |
| `Python/core/` | Shared landmark, kinematics, ArUco, filtering and transport code used by the runtime. |
| `Unity/` | Rig scene, receivers, required model and rendering assets, project settings and package dependencies. |
| `Thesis_V9.pdf` | Final thesis. |
| `Thesis_Defence_2026.pptx` | Final defence presentation. |

The runtime is the synchronized implementation described in the thesis. Names such as `v2_person.py` and `IntegratedSceneReceiverV2` identify its existing stream implementation; their names and shared-memory protocol remain compatible.

## Run

Use Linux: the Python and Unity processes communicate through files in `/dev/shm`. The project targets Unity **6000.3.19f1**. Python dependencies are pinned in `Python/requirements.txt` to the versions available in the thesis environment; Python 3.11 is recommended for this package set.

From the repository root:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r Python/requirements.txt
python Python/runtime/integration/run_v2.py --help
```

For a recorded session, supply a RealSense `.bag` file and its scene-calibration JSON:

```bash
python Python/runtime/integration/run_v2.py \
  --source bag --bag /path/to/session.bag \
  --calib /path/to/scene_calibration.json \
  --object-recovery --plausibility-gate --display-lpf
```

For a connected D435, use `--source live` with a calibration JSON for the current camera and marker arrangement. `--calibrate` can generate a new calibration from visible wall, desk and object markers; see `Python/runtime/calibration/live_calibrate.py --help` for capture requirements. The first person-pipeline run downloads the MediaPipe heavy pose model if it is absent.

Open `Unity/` in Unity Hub, open `Assets/Scenes/rig.unity`, and enter Play mode after the Python stream starts. The integrated receiver starts automatically when the scene and PSI2 shared-memory files exist. Stop Python with Ctrl+C. Runtime logs are generated locally and ignored by Git.

Calibration must use the actual printed marker dimensions. Marker IDs and calibration defaults are in `Python/core/aruco/frames.py`; its original desk/object defaults are 50 mm. The thesis measurements used a corrected 45 mm scale. Set marker dimensions to match your own prints before generating calibration; do not apply an extra scale correction to a JSON that is already corrected.

## Scope and limitations

This repository contains the thesis implementation and final submission documents. Recordings, participant-specific calibration files, evaluation programs, writing sources and exploratory projects are not distributed here. Experiments and their conditions are documented in the thesis PDF.

Object-assisted recovery assumes a valid tracked object pose and a previously observed grasp offset. Long occlusion, changing grasps and unreliable depth remain limitations. Displayed held or reconstructed joints are distinguished from directly observed joints; the system does not provide independent ground truth.
