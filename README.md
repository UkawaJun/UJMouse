<p align="right"><b>English</b> | <a href="README.zh.md">简体中文</a></p>

# UJMouse

A human-like cursor movement library built on **real human mouse trajectories**. Zero training, no deep-learning framework, runs in pure Python.

Core idea: randomly blend pre-recorded real human mouse trajectories with weighted averaging, then stretch toward the target, producing a movement path that differs every time and looks close to a real human's. The whole approach is simple and easy to learn — read through it once and you can reproduce the simulated-mouse effect.

> ⚠️ This is a **trajectory generation / visual realism** project, suited for automation testing, teaching demos, and lightweight scenarios where mouse behavior is not strictly analyzed. It does **not** claim to reliably bypass industrial-grade behavioral anti-bot systems (reCAPTCHA v3, DataDome, etc.). See [Limitations](#limitations).

---

## What problem it solves

Most mouse simulations use **Bézier curves**. The problem with Bézier isn't that it looks unlike a human — it's that it's too regular: smooth curves, lacking the micro-jitter and irregular acceleration/deceleration of a real human, recognizable at a glance as function-generated.

This project takes a different route: **don't synthesize from scratch — reuse trajectories actually drawn by humans.** The repo ships 402 real human trajectory samples (19 sampled points each), **all recorded manually by one person**.

## How it works

<p align="center">
  <img src="images/principle.png" width="820" alt="Principle diagram">
</p>

Each move has two steps:

1. **Randomly pick 3** real human trajectories from the sample library, each assigned a random weight (the three sum to 1);
2. **Weighted sum point-by-point** of the three trajectories yields a new trajectory, which is then stretched by the direction and distance from the current start to the target; time is also weighted by the same weights.

Because the source material is human-drawn, the blended result largely preserves micro-jitter, asymmetric acceleration/deceleration, and end-of-move deceleration — so it looks more natural than a pure curve. Mathematically, the blended trajectory lies within the **convex hull** spanned by the three chosen real trajectories — which is both why it looks real and where its capability ends (see Limitations).

## Installation

After cloning the repo, install dependencies in one step with `requirements.txt`:

```bash
git clone https://github.com/<your-name>/UJMouse.git
cd UJMouse
pip install -r requirements.txt
```

`requirements.txt` contains only two third-party libraries: `pyautogui` (drives the mouse) and `pandas` (used only when rebuilding data from CSV for the first time). Everything else is Python standard library and needs no installation.

## Project files & data format

```
UJMouse/
├── ujmouse.py            # Core library (UJMouse class)
├── requirements.txt      # Dependencies
├── Document/
│   └── UJ_Infor.json     # Encrypted real-trajectory data (402 entries)
├── mouse_data.csv        # Raw trajectories (optional; used to rebuild the json if data is lost)
└── images/               # README figures
```

**Data loading logic** (already implemented): on init it first reads the encrypted file `Document/UJ_Infor.json`; if absent, it falls back to `mouse_data.csv` and rebuilds. Data is decrypted in memory with a fixed key and never written to disk as plaintext.

**Data format**: after decryption it's a dictionary with the following fields:

| Field | Meaning |
|---|---|
| `size` | Number of sampled points per trajectory (19) |
| `dataSize` | Total number of trajectories (402) |
| `data` | Per-point relative-displacement sequence of each trajectory |
| `time` | Total duration of each trajectory |
| `end` | End coordinates of each trajectory |

## Custom data

The bundled data is all personally recorded real mouse paths. To replace it with your own: record new trajectories into a CSV with the capture script and delete the old `UJ_Infor.json` to let the program rebuild automatically; or decode the existing json with the key above, modify it, and overwrite. **Recording data from more people improves diversity and realism.**

## Quick start

```python
from ujmouse import UJMouse

mouse = UJMouse()
mouse.Move(800, 600)                    # human-like move to (800, 600)
mouse.Move(400, 300, need_Click=True)   # move and click

mouse.IterMode = True                   # enable iterative / roaming mode
mouse.Move(1200, 200)
```

## The UJMouse class

```
UJMouse
├── Movement
│   ├── Move(x, y, need_Click=False)   Core: move to target along a human-like trajectory, optional click
│   └── Locate(x, y, delta=0.0)        Teleport to target (no trajectory)
├── Drag
│   └── Drag(x1, y1, x2, y2)           Press → human-like move → release
├── Keyboard
│   └── hotKey(key=[...])              Hotkey combo (supports 1–3 keys)
├── Position
│   ├── UpdateMouseLoc()               Refresh current mouse position
│   └── GetMouseLoc(loc)               Read current mouse position
├── Timing
│   └── Delta(t=1.5)                   Delay
└── Config
    ├── IterMode                       Whether iterative/roaming mode is on (default False)
    └── IterDis                        Distance threshold that triggers recursive filling (default 100)
```

> The above are the public methods. The class also has several `_`-prefixed low-level wrappers (click, scroll, distance calc, bounds protection, etc.) called internally by methods like `Move`.

## Comparison

### Normal mode

In normal mode the cursor moves straight toward the target along one blended trajectory, decelerating to finish near the target. Same start/end run 5 times, with the real cursor position sampled live during movement; left is Bézier, right is this method:

<p align="center">
  <img src="images/traj_bl_to_tr.png" width="820" alt="Bottom-left to top-right comparison">
</p>

<p align="center">
  <img src="images/traj_br_to_tl.png" width="820" alt="Bottom-right to top-left comparison">
</p>

Bézier (left) is smooth as if drawn with a compass; this method (right) carries the irregular micro-jitter and acceleration/deceleration characteristic of real human data.

### Iterative / roaming mode

With `IterMode` on, long-distance moves recursively fill the middle segments. Since the fill also uses real segments, occasionally picking a high-variance segment pulls the cursor toward a farther direction, producing a "wander midway, then return to target" effect. This method only, bottom-left → top-right, 3 runs:

<p align="center">
  <img src="images/traj_iter_bl_to_tr.png" width="620" alt="Iterative roaming mode">
</p>

> This is an interesting showcase feature, but the roaming path is driven by data variance — the cursor may move toward empty areas of the screen, which is actually suspicious under strict behavioral analysis. Recommended for demo use only.

### Move duration vs distance

Duration of this method vs Bézier across distances (repeated multiple times each, error bars are standard deviation):

<p align="center">
  <img src="images/timing_distance.png" width="680" alt="Distance vs duration comparison">
</p>

## Related projects

This direction is already fairly well studied, with many public implementations on different routes. This project doesn't claim to be stronger — just a different route:

| Route | Method | Difference from this project |
|---|---|---|
| ghost-cursor, etc. | Bézier curves | Pure math synthesis, no real data |
| sigma-lognormal | Fit a mathematical motion model to real data | Abstracts into model parameters; this project uses raw trajectories directly |
| GAN / neural nets | Train a model to learn and generate | Requires training; this project is training-free |
| HumanMoveMouse, etc. | Extract statistical features from real data + interpolate | Abstracts into statistics first; this project blends raw segments directly |
| **UJMouse** | **Random convex combination of multiple real trajectories + stretch + optional recursive filling** | Reuses raw segments directly, simple, training-free |

## Limitations

1. **No guarantee of bypassing anti-bot systems.** Modern behavioral risk control also examines the relationship between the trajectory and page elements, cross-session consistency, and more; this project only handles the visual realism of a single move.
2. **Convex-combination boundary.** The blended trajectory lies within the convex hull of the source data, so it cannot generate moves more extreme than the samples, and the overall direction across runs is fairly consistent (visible in the comparison figures).
3. **Samples from a single person.** All output carries one person's motion style, which may become an identifiable feature in multi-account / large-scale scenarios.
4. **Roaming mode has no intent.** The midway wandering is driven by data variance and may move toward empty screen areas, which is suspicious under strict analysis.
5. **Execution layer is based on pyautogui.** Synthetic events may be flagged as non-genuine input under some detection viewpoints.

## License

MIT

## Disclaimer

For learning, research, and lawful automation testing only. Please comply with the terms of service of target websites / software and the laws of your region. The author is not responsible for any misuse.
