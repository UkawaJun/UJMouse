<p align="right"><b>English</b> | <a href="README.zh.md">简体中文</a></p>


# UJMouse

> A human-like mouse movement implementation without Bézier curves · zero training · pure Python

This project offers one way to do human-like mouse movement: instead of Bézier curves or other synthesis methods, it reuses pre-recorded real human mouse trajectories. Each move picks 3 real trajectories at random, blends them with weights, and stretches them to the target. The implementation is simple and mainly meant for learning.

<sub>📌 This is one module from a set of personal practice projects built between Jul–Nov 2025.</sub>

> ⚠️ Built for automation testing, demos, and lightweight cases where mouse behavior isn't strictly analyzed. Does not claim to bypass industrial anti-bot systems (reCAPTCHA v3, DataDome, etc.). See [Limitations](#limitations).

---

## How it works

<p align="center">
  <img src="https://github.com/user-attachments/assets/3aedb01d-93d1-451e-b451-a7a015bec227" width="780" alt="bottom-left to top-right">
</p>


Most mouse simulators generate trajectories with Bézier curves. This project uses a different approach: instead of synthesizing from scratch, it reuses real human trajectories.

1. Pick 3 real trajectories at random, each with a random weight (summing to 1);
2. Weighted sum point-by-point gives a new trajectory, then stretch it by the direction and distance to the target.

Because the trajectories come from real recordings, the blended result keeps the micro-jitter and acceleration of real human movement. The repo ships 402 real trajectories (19 points each), all recorded by hand by one person.

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
  <img src="https://github.com/user-attachments/assets/80547cc2-4c54-480d-afe5-2471e531a463" width="780" alt="bottom-left to top-right">
</p>
<p align="center">
  <img src="https://github.com/user-attachments/assets/6c2f976d-fd39-4401-b892-c4b9f0bf6c12" width="780" alt="bottom-right to top-left">
</p>


The Bézier trajectories (left) are smooth; this method (right) carries the micro-jitter and acceleration present in the recorded human data.

**Roaming mode** — with `IterMode` on, long moves recursively fill the middle. A high-variance segment now and then pulls the cursor away, giving a "wander, then snap back" effect (UJMouse only, 3 runs):

<p align="center">
  <img src="https://github.com/user-attachments/assets/313e8b50-91a9-47a5-b052-ca25f3c750e4" width="560" alt="roaming mode">
</p>


**Duration vs distance** — UJMouse vs Bézier (error bars = std):

<p align="center">
  <img src="https://github.com/user-attachments/assets/382af3bb-ee07-413c-acaa-876ab4244a19" width="620" alt="distance vs duration">
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
