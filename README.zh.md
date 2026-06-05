<p align="right"><a href="README.md">English</a> | <b>简体中文</b></p>

# UJMouse

> 一种不用贝塞尔曲线的拟人化鼠标移动实现 · 零训练 · 纯 Python

本项目提供了一种实现拟人化鼠标移动的方法:不用贝塞尔曲线或其他合成方法,而是复用预先录制的真人鼠标轨迹。每次移动随机抽取 3 条真人轨迹,加权混合后拉伸到目标点。实现简单,主要供学习参考。

<sub>📌 本项目是 2025 年 7–11 月期间个人练手项目中的一个模块。</sub>

> ⚠️ 适合自动化测试、教学演示等不严格分析鼠标行为的场景。不声称能绕过 reCAPTCHA v3、DataDome 等工业级风控。详见[局限性](#局限性)。

---

## 原理

<p align="center">
  <img src="images/principle.png" width="780" alt="原理示意图">
</p>

常见的鼠标模拟多用贝塞尔曲线生成轨迹。本项目改用另一种方式:不从零合成,而是复用真人轨迹。

1. 从样本库随机抽 3 条真人轨迹,各给一个随机权重(和为 1);
2. 逐点加权求和得到新轨迹,再按起点到目标的方向、距离拉伸。

因为轨迹来自真人录制,混合后保留了真人移动的微抖和加减速。仓库附带 402 条真人轨迹(每条 19 点),全部为个人手动录制。

## 安装

```bash
git clone https://github.com/<your-name>/UJMouse.git
cd UJMouse
pip install -r requirements.txt
```

依赖只有 `pyautogui` 和 `pandas`(后者仅首次从 CSV 重建数据时用到)。

## 快速使用

```python
from ujmouse import UJMouse

mouse = UJMouse()
mouse.Move(800, 600)                    # 拟人化移动
mouse.Move(400, 300, need_Click=True)   # 移动并点击

mouse.IterMode = True                   # 开启迭代/漫游模式
mouse.Move(1200, 200)
```

## 效果对比

**普通模式** — 沿一条混合轨迹直奔目标,末端减速。同样起止点各跑 5 次,移动中实时采样真实光标(左:贝塞尔,右:本方法):

<p align="center">
  <img src="images/traj_bl_to_tr.png" width="780" alt="左下→右上">
</p>
<p align="center">
  <img src="images/traj_br_to_tl.png" width="780" alt="右下→左上">
</p>

左侧贝塞尔轨迹平滑;右侧本方法的轨迹带有真人录制数据中的微抖和加减速。

**迭代/漫游模式** — 开启 `IterMode`,长距离移动会递归填充中间段,偶尔抽到大波动片段就把光标带远,形成"中途游走、最后归位"的效果(仅本方法,3 条):

<p align="center">
  <img src="images/traj_iter_bl_to_tr.png" width="560" alt="迭代漫游模式">
</p>

**耗时随距离变化** — 本方法 vs 贝塞尔(误差棒为标准差):

<p align="center">
  <img src="images/timing_distance.png" width="620" alt="距离-耗时">
</p>

## 文件结构

```
UJMouse/
├── ujmouse.py            # 核心库(UJMouse 类)
├── requirements.txt      # 依赖
├── Document/
│   └── UJ_Infor.json     # 加密的真人轨迹数据(402 条)
├── mouse_data.csv        # 原始轨迹(可选,数据丢失时用来重建)
└── images/               # README 配图
```

初始化时优先读加密文件 `UJ_Infor.json`,不存在则用 `mouse_data.csv` 重建。数据在内存中解密,不落地明文。解密后是字典,字段:`size`(每条点数)、`dataSize`(总条数)、`data`(逐点位移)、`time`(耗时)、`end`(终点)。

**自定义数据**:录新轨迹存成 CSV、删掉旧 json 让程序重建;或按密钥解码现有 json 改完覆盖。多采几个人,效果更好。

## 主要方法

| 方法 | 说明 |
|---|---|
| `Move(x, y, need_Click=False)` | 核心:走拟人轨迹移动到目标,可附带点击 |
| `Locate(x, y)` | 瞬移到目标(不走轨迹) |
| `Drag(x1, y1, x2, y2)` | 按下 → 拟人移动 → 松开 |
| `hotKey(key=[...])` | 组合键(1~3 个) |
| `IterMode` / `IterDis` | 漫游模式开关 / 触发递归的距离阈值 |

## 与同类项目的区别

| 路线 | 方法 | 区别 |
|---|---|---|
| ghost-cursor 等 | 贝塞尔曲线 | 纯数学,不用真实数据 |
| sigma-lognormal | 拟合数学运动模型 | 抽象成参数;本项目直接用原始轨迹 |
| GAN / 神经网络 | 训练模型生成 | 需训练;本项目零训练 |
| HumanMoveMouse 等 | 提取统计特征 + 插值 | 先抽象;本项目直接混合原始片段 |
| **UJMouse** | **真实轨迹随机凸组合 + 递归填充** | 直接复用原始片段,简单、零训练 |

## 局限性

- **不保证过反爬。** 只做单次移动的视觉拟真,不涉及轨迹与页面元素的关系、跨会话一致性等。
- **数据来自单人。** 输出带同一人的运动风格,大规模/多账号下可能成为可识别特征。
- **漫游模式无意图。** 游走由数据波动驱动,可能移向屏幕空白处,严格分析下反而可疑。

## 许可证

MIT。仅供学习、研究和合法的自动化测试,请遵守目标网站/软件条款及当地法律。
