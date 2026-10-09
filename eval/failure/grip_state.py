"""Grip-episode state machine for object-conditioned recovery (E-014).

The instantaneous holding classifier (eval/offset/carry.holding_mask)
requires a MEASURED wrist, so during exactly the frames the recovery
targets (wrist lost or corrupt) it cannot answer "is this hand still
holding". This module turns the instantaneous classifier into a
causal per-hand state machine with rigid-grasp persistence:

  ENTER   the hand has been cleanly holding (holding_mask true) for
          ENTER_FRAMES consecutive frames;
  STAY    through any wrist failure, as long as the object remains
          carried (rest_referenced_carried) - the rigid-grasp
          persistence assumption: a moving object that nobody
          visible released is still in the hand that held it;
  EXIT    the object comes to rest, or the wrist is again cleanly
          measured farther than RELEASE_RADIUS from the box center,
          sustained EXIT_FRAMES frames (hysteresis: RELEASE_RADIUS
          0.35 m > HOLD_RADIUS 0.25 m).

Both hands may hold simultaneously (hand-over = two overlapping
episodes; E-005 precedent). All state is causal (no lookahead).

Per-episode grip offsets: the global R5 grip fit is loose (residual
median ~8 cm) because the operator regrasps between stations; the
offset is near-constant WITHIN an episode. fit_episode_mu therefore
fits mu on each episode's clean held frames and falls back to the
global fit only when an episode has too few clean frames.
"""
import numpy as np

ENTER_FRAMES = 5         # consecutive clean-holding frames to enter
EXIT_FRAMES = 5          # consecutive release-condition frames to exit
RELEASE_RADIUS = 0.35    # m, clean wrist farther than this = released
MIN_EP_FRAMES = 15       # clean frames needed for a per-episode mu
MU_ALPHA = 0.02          # per-frame EMA gain of the time-local mu
                         # (~1.7 s memory at 30 fps)
MU_WARMUP = 5            # clean frames of plain averaging before the
                         # EMA value is considered usable


def grip_episodes(hold_clean, carried, wrist_center_dist, wrist_clean):
    """Causal holding state for one hand.

    hold_clean        instantaneous clean holding classification
    carried           object-carried mask (rest-referenced)
    wrist_center_dist |wrist - box center| per frame (NaN ok)
    wrist_clean       wrist measured and trusted this frame

    Returns (holding bool array, [(start, stop) inclusive], ...).
    """
    n = len(hold_clean)
    holding = np.zeros(n, bool)
    episodes = []
    on = False
    enter_ctr = exit_ctr = 0
    start = 0
    for f in range(n):
        if not on:
            enter_ctr = enter_ctr + 1 if hold_clean[f] else 0
            if enter_ctr >= ENTER_FRAMES:
                on = True
                start = f - ENTER_FRAMES + 1
                holding[start:f + 1] = True
                exit_ctr = 0
        else:
            released = (not carried[f]) or (
                wrist_clean[f]
                and np.isfinite(wrist_center_dist[f])
                and wrist_center_dist[f] > RELEASE_RADIUS)
            exit_ctr = exit_ctr + 1 if released else 0
            if exit_ctr >= EXIT_FRAMES:
                on = False
                stop = f - EXIT_FRAMES
                episodes.append((start, stop))
                holding[stop + 1:f + 1] = False
                enter_ctr = 0
            else:
                holding[f] = True
    if on:
        episodes.append((start, n - 1))
    return holding, episodes


def fit_episode_mu(episodes, d_loc, hold_clean, mu_global,
                   min_frames=MIN_EP_FRAMES):
    """Per-episode object-frame grip vector.

    d_loc      per-frame object-frame wrist offset R_obj^T (w - obj)
    hold_clean clean instantaneous holding mask
    mu_global  fallback offset (recording-wide fit), may be None

    Returns list of dicts per episode: start, stop, n_clean, mu,
    sd, source ("episode" or "global").
    """
    out = []
    for start, stop in episodes:
        m = np.zeros(len(hold_clean), bool)
        m[start:stop + 1] = True
        m &= hold_clean & np.isfinite(d_loc).all(axis=1)
        if m.sum() >= min_frames:
            mu = d_loc[m].mean(axis=0)
            sd = d_loc[m].std(axis=0)
            src = "episode"
        else:
            mu, sd, src = mu_global, None, "global"
        out.append({"start": int(start), "stop": int(stop),
                    "n_clean": int(m.sum()),
                    "mu": None if mu is None else np.asarray(mu, float),
                    "sd": None if sd is None else np.asarray(sd, float),
                    "source": src})
    return out


def per_frame_mu(n, episode_fits):
    """Expand episode fits to a per-frame (n, 3) mu array (NaN when
    not holding or no usable mu)."""
    mu = np.full((n, 3), np.nan)
    for ep in episode_fits:
        if ep["mu"] is not None:
            mu[ep["start"]:ep["stop"] + 1] = ep["mu"]
    return mu


def time_local_mu(d_loc, hold_clean, episodes, alpha=MU_ALPHA,
                  warmup=MU_WARMUP):
    """Causal time-local grip offset per frame.

    The operator regrips DURING long episodes (measured drift up to
    13 cm between an episode's mean and the offset in force at a
    given moment), so a constant per-episode mu carries that drift
    into every recovered wrist. This estimator tracks the offset with
    a short memory instead: within each episode, clean held frames
    update an EMA of d_loc (gain alpha, ~1.7 s memory); frames
    without a clean update (a failure window) FREEZE the estimate, so
    the value used for recovery is the offset in force immediately
    before tracking was lost. The EMA restarts at each episode
    boundary (a new grasp is a new offset) with `warmup` frames of
    plain averaging before the value becomes usable.

    Returns an (n, 3) array, NaN where no usable estimate exists.
    """
    n = len(hold_clean)
    out = np.full((n, 3), np.nan)
    for start, stop in episodes:
        est = None
        acc = []
        for f in range(start, stop + 1):
            if hold_clean[f] and np.isfinite(d_loc[f]).all():
                if est is None:
                    acc.append(d_loc[f])
                    if len(acc) >= warmup:
                        est = np.mean(acc, axis=0)
                else:
                    est = (1.0 - alpha) * est + alpha * d_loc[f]
            if est is not None:
                out[f] = est
    return out
