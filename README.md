<p align="right"><b>English</b> | <a href="README.zh.md">简体中文</a></p>

# UJMouse

A human-like mouse movement library built on **real human trajectories**. Zero training, no deep-learning framework, pure Python.

Each move = pick 3 real trajectories at random → blend with weights → stretch to the target. Different every time, and it keeps the micro-jitter and acceleration of a real human. Simple enough to read once and reproduce.

> ⚠️ Built for automation testing, demos, and lightweight cases where mouse behavior **isn't strictly analyzed**. Does **not** claim to bypass industrial anti-bot systems (reCAPTCHA v3, DataDome, etc.). See [Limitations](#limitations).

---

## How it works

<p align="center">
  <img src="images/principle.png" width="780" alt="Principle diagram">
</p>

Most mouse simulators use **Bézier curves**. The problem: too smooth, too regular — clearly function-drawn. This project doesn't synthesize from scratch. It **reuses real human trajectories**:

1. Pick **3** real trajectories at random, each with a random weight (summing to 1);
2. Weighted sum point-by-point gives a new trajectory, then stretch it by the direction and distance to the target.

Since the source is human-drawn, the micro-jitter, acceleration, and end-of-move deceleration carry over. The repo ships **402** real trajectories (19 points each), all recorded by hand by one person.

## Install

```bash
git clone https://github.com/<your-name>/UJMouse.git
cd UJMouse
pip install -r requirements.txt
```

Only two deps: `pyautogui` and `pandas` (the latter only for rebuilding data from CSV the first time).

## Quick start

```python
from ujmouse import UJMouse

mouse = UJMouse()
mouse.Move(800, 600)                    # human-like move
mouse.Move(400, 300, need_Click=True)   # move and click

mouse.IterMode = True                   # enable roaming mode
mouse.Move(1200, 200)
```

## Comparison

**Normal mode** — straight to the target along one blended trajectory, decelerating at the end. Same start/end, 5 runs each, real cursor sampled live during the move (left: Bézier, right: UJMouse):

<p align="center">
  <img src="images/traj_bl_to_tr.png" width="780" alt="bottom-left to top-right">
</p>
<p align="center">
  <img src="images/traj_br_to_tl.png" width="780" alt="bottom-right to top-left">
</p>

Bézier (left) is smooth like a compass drew it. UJMouse (right) has the irregular jitter and acceleration of real human data.

**Roaming mode** — with `IterMode` on, long moves recursively fill the middle. A high-variance segment now and then pulls the cursor away, giving a "wander, then snap back" effect (UJMouse only, 3 runs):

<p align="center">
  <img src="images/traj_iter_bl_to_tr.png" width="560" alt="roaming mode">
</p>

**Duration vs distance** — UJMouse vs Bézier (error bars = std):

<p align="center">
  <img src="images/timing_distance.png" width="620" alt="distance vs duration">
</p>

## File structure

```
UJMouse/
├── ujmouse.py            # core library (UJMouse class)
├── requirements.txt      # dependencies
├── Document/
│   └── UJ_Infor.json     # encrypted trajectory data (402 entries)
├── mouse_data.csv        # raw trajectories (optional, rebuilds the json if lost)
└── images/               # README figures
```

On init it reads the encrypted `UJ_Infor.json`, or rebuilds from `mouse_data.csv` if missing. Data is decrypted in memory, never written as plaintext. Decrypted it's a dict: `size` (points per trajectory), `dataSize` (total count), `data` (per-point displacement), `time` (duration), `end` (endpoint).

**Custom data**: record new trajectories into a CSV and delete the old json to trigger a rebuild; or decode the json with the key, edit, and overwrite. More people = better results.

## Main methods

| Method | What it does |
|---|---|
| `Move(x, y, need_Click=False)` | Core: move to target along a human-like trajectory, optional click |
| `Locate(x, y)` | Teleport to target (no trajectory) |
| `Drag(x1, y1, x2, y2)` | Press → human-like move → release |
| `hotKey(key=[...])` | Hotkey combo (1–3 keys) |
| `IterMode` / `IterDis` | Roaming toggle / distance threshold for recursion |

## Vs. similar projects

| Route | Method | Difference |
|---|---|---|
| ghost-cursor, etc. | Bézier curves | Pure math, no real data |
| sigma-lognormal | Fit a math motion model | Abstracts to params; this uses raw trajectories |
| GAN / neural nets | Train a model | Needs training; this is training-free |
| HumanMoveMouse, etc. | Statistical features + interpolation | Abstracts first; this blends raw segments |
| **UJMouse** | **Random convex combination + recursive filling** | Reuses raw segments, simple, training-free |

## Limitations

- **No anti-bot guarantee.** Only does single-move visual realism — not trajectory-to-element relationships or cross-session consistency.
- **Single-person data.** Output carries one person's motion style; may be identifiable at scale or across accounts.
- **Roaming has no intent.** The wandering is data-driven and may head into empty screen areas, which looks suspicious under strict analysis.

## License

MIT. For learning, research, and lawful automation testing. Follow the terms of target sites/software and your local laws.
