# -*- coding: utf-8 -*-
"""
ujmouse_core.py  —  UJMouse 鼠标类（从原 UJMouse.py 提炼）

把原库的 UJMouse 类**原样搬出来**，行为与原库一致：
  · Move(x, y) 会真正驱动系统鼠标，走一条拟人轨迹移动过去；
  · 点击、滚轮、拖拽、热键等方法都保留。
只去掉了与鼠标无关、且依赖重型库的部分（图像识别 OCR / 截图 / 剪贴板图片 /
微信 WeChatMessage / 链式语言 CJProgram），这些仍保留在原 Document/UJMouse.py 里。

数据来源 / data:
  直接读取原加密文件 UJ_Infor.json（402 条真人轨迹，每条 19 点），
  用与原库完全一致的密钥在内存中解密，不另存明文。
"""

import os
import ast
import time
import random

import pyautogui
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.00001   # 与原库一致

# ---- 与原 UJMouse.py 完全一致的常量 ----
INFOR_KEY = "154588351489562315151976216765192376"
_N = 0x110000

_HERE = os.path.dirname(os.path.abspath(__file__))
_CANDIDATES = [
    os.path.join(_HERE, "..", "Document", "UJ_Infor.json"),
    os.path.join(_HERE, "UJ_Infor.json"),
    os.path.join(_HERE, "..", "UJ_Infor.json"),
    "Document/UJ_Infor.json",
]
INFOR_NAME = next((p for p in _CANDIDATES if os.path.exists(p)), _CANDIDATES[0])


def EndeCrypt(text, key, decode=False):
    """字符位移加/解密，与原库 EndeCrypt 等价。"""
    if not key:
        return text
    mode = -1 if decode else 1
    ki = [ord(k) for k in key]
    kl = len(ki)
    return "".join(chr((ord(c) + mode * ki[i % kl]) % _N) for i, c in enumerate(text))


def File_EnDeRead(fileName, SigmaKey, encoding="utf-8"):
    """解密读入数据并返回 dict（对应原库同名函数）。
    原库用 json_repair.loads 解析 str(dict)，这里用标准库 ast.literal_eval，
    结果一致且无第三方依赖。"""
    with open(fileName, "r", encoding=encoding) as f:
        box = f.read()
    box = EndeCrypt(box, SigmaKey, decode=True)
    return ast.literal_eval(box)


# ---- 模块级全局量（对应原 UJMouse.py 顶部）----
DATA = {"size": 0, "data": [], "time": [], "end": [], "dataSize": 0}
_SatrtTime = time.time()
try:
    _SCREEN = pyautogui.size()
except Exception:
    _SCREEN = (1920, 1080)
PV = {
    "time": 0.0,
    "screenSize": _SCREEN,
    "mousePos": [0, 0],
    "Key": None,
    "MouseScoll": [False, 0],
}


class UJMouse(object):
    def __init__(self):
        global DATA
        try:
            open(INFOR_NAME, "r", encoding="utf-8")
        except FileNotFoundError:
            print("[修复]损失信息文件")
            self._updatacsv_()
        else:
            DATA = File_EnDeRead(INFOR_NAME, INFOR_KEY)

        self.IterDis = 100          # IterationDistance
        self.IterMode = False
        self._ImageFontMemory = []
        self._ImagePath = None

    # 检查如果不存在文件，则更新文件（数据重建路径；pandas 延迟导入）
    def _updatacsv_(self, defName="mouse_data"):
        from pandas import read_csv
        from sys import exit as sysExit
        try:
            read_csv(defName + ".csv")
        except FileNotFoundError:
            print("[错误]丢失数据，请修复！")
            sysExit(0)
        _dfd = read_csv(defName + ".csv").values
        dumpJsonData = {"size": 0, "data": [], "time": [], "end": [],
                        "dataSize": len(_dfd)}
        dumpJsonData["time"] = [float(a) for a in list(_dfd[:, -1:])]
        dumpJsonData["end"] = [str(a)[2:-2] for a in list(_dfd[:, :1])]
        _l = []
        for _a in list(_dfd[:, 2:-1]):
            _l.append([str(_b) for _b in list(_a)])
        dumpJsonData["data"] = _l
        dumpJsonData["size"] = len(_l[0])
        global DATA
        DATA = dumpJsonData

    # 求取两点的距离
    def _distance_(self, x1, y1, x2, y2):
        return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

    # 调用 pyauto 基础库
    def _MoveTo_(self, x, y, delta=0.2):
        pyautogui.moveTo(x, y, duration=delta)

    # 点击
    def _Click_(self, times=1, delta=0.3):
        pyautogui.click(clicks=times, interval=delta)

    def _LeftClick(self):
        pyautogui.leftClick()

    def _RightClick(self):
        pyautogui.rightClick()

    def _MiddleClick(self):
        pyautogui.middleClick()

    def _MouseDown(self):
        pyautogui.mouseDown()

    def _MouseUP(self):
        pyautogui.mouseUp()

    def _DragTo(self, x, y, delta=0.5):
        pyautogui.dragTo(x, y, duration=delta)

    def _Scroll(self, roll, delta=1.5):
        from math import sin
        if roll == 0:
            return
        _t = abs(delta / roll)
        for a in range(0, abs(roll)):
            k = (sin(a * 0.7) + 1) / 2 + 0.1
            pyautogui.scroll(120 * (-1 if roll < 0 else 1))
            self.Delta(_t * k / 2)
            if k <= 0.15:
                self.Delta(0.2)

    # 热键
    def _HotKey1(self, Key):
        pyautogui.hotkey(Key)

    def _HotKey2(self, Key1, key2):
        pyautogui.hotkey(Key1, key2)

    def _HotKey3(self, Key1, key2, key3):
        pyautogui.hotkey(Key1, key2, key3)

    # 分割数字
    def _NumDivide(self, s):
        _a = s.split(",")
        return int(_a[0]), int(_a[1])

    # 位置测试，防止越界
    def _CALDATA_Test(self, CALDATA):
        llo = [0, 1]
        for _a in range(0, len(CALDATA)):
            for _s in llo:
                CALDATA[_a][_s] = CALDATA[_a][_s] if CALDATA[_a][_s] > 0 else 1
                CALDATA[_a][_s] = (CALDATA[_a][_s] if CALDATA[_a][_s] < PV["screenSize"][_s]
                                   else PV["screenSize"][_s] - 1)
        llo.clear()

    # [功能]更新鼠标位置
    def UpdateMouseLoc(self):
        PV["time"] = time.time() - _SatrtTime
        PV["mousePos"][0] = pyautogui.position()[0]
        PV["mousePos"][1] = pyautogui.position()[1]

    # [功能]延迟更新
    def Delta(self, t=1.5):
        pyautogui.sleep(t)

    # [功能]走拟合路线到对应路径（真正移动鼠标）
    def Move(self, x, y, need_Click=False):
        global DATA

        CALDATA = []
        for a in range(0, DATA["size"]):
            CALDATA.append([0, 0])
        x = 1 if x < 1 else x
        y = 1 if y < 1 else y
        x = x if x < PV["screenSize"][0] else PV["screenSize"][0] - 1
        y = y if y < PV["screenSize"][1] else PV["screenSize"][1] - 1

        # 生成三个随机性的编号
        _randint3 = [random.randint(0, DATA["dataSize"] - 1)]
        while True:
            _c = random.randint(0, DATA["dataSize"] - 1)
            if _c in _randint3:
                continue
            else:
                _randint3.append(_c)
                if len(_randint3) >= 3:
                    break

        # 生成随机的三个线性拟合值
        _randWeight = []
        _MaxValue = 1000
        _randWeight.append(random.randint(1, int(_MaxValue / 2)))
        _randWeight.append(random.randint(1, _MaxValue - _randWeight[0]))
        _randWeight.append(_MaxValue - _randWeight[0] - _randWeight[1])
        for _a in range(0, len(_randWeight)):
            _randWeight[_a] = _randWeight[_a] / _MaxValue

        _index = [0, 0]
        CauTime = [0.0]
        CauEnd = [0.0]

        self.UpdateMouseLoc()
        _direction_x = x - PV["mousePos"][0]
        _direction_y = y - PV["mousePos"][1]

        for _a in _randint3:
            _x, _y = self._NumDivide(DATA["end"][_a])
            CauTime[0] += DATA["time"][_a] * _randWeight[_index[0]]
            CauEnd[0] += self._distance_(0, 0, _x, _y) * _randWeight[_index[0]]
            self.UpdateMouseLoc()

            _x = 1 if _x == 0 else _x
            _y = 1 if _y == 0 else _y
            wx = _direction_x / _x
            wy = _direction_y / _y
            _index[1] = 0

            for _b in DATA["data"][_a]:
                _x2, _y2 = self._NumDivide(_b)
                CALDATA[_index[1]][0] += int(_x2 * wx * _randWeight[_index[0]])
                CALDATA[_index[1]][1] += int(_y2 * wy * _randWeight[_index[0]])
                _index[1] += 1

            _index[0] += 1

        for _a in range(0, len(CALDATA)):
            CALDATA[_a][0] += PV["mousePos"][0]
            CALDATA[_a][1] += PV["mousePos"][1]
        self._CALDATA_Test(CALDATA)

        _dis1 = CauEnd[0]
        _dis2 = self._distance_(0, 0, _direction_x, _direction_y)
        CauTime[0] = CauTime[0] * (_dis2 / _dis1) ** (1 / 4)
        _t = CauTime[0] / len(CALDATA)

        for _a in CALDATA:
            self.UpdateMouseLoc()
            _NowDistance = self._distance_(PV["mousePos"][0], PV["mousePos"][1], _a[0], _a[1])
            if _NowDistance > self.IterDis:
                if self.IterMode:
                    self.Move(_a[0], _a[1])
                else:
                    self._MoveTo_(_a[0], _a[1], _t)
            else:
                self._MoveTo_(_a[0], _a[1], _t)

        CALDATA.clear()
        self.UpdateMouseLoc()
        if self._distance_(PV["mousePos"][0], PV["mousePos"][1], x, y) > self.IterDis / 2:
            self.Move(x, y)
        else:
            self._MoveTo_(x, y, _t + 0.2)
            if need_Click:
                self._Click_()

    # [功能]直接把鼠标移动过去
    def Locate(self, x, y, delta=0.0):
        _s = [[x, y]]
        self._CALDATA_Test(_s)
        self.Delta(delta)
        pyautogui.moveTo(_s[0][0], _s[0][1])
        _s.clear()

    # [功能]获取并更新一次鼠标位置
    def GetMouseLoc(self, Loc):
        self.UpdateMouseLoc()
        Loc[0] = PV["mousePos"][0]
        Loc[1] = PV["mousePos"][1]
        return Loc

    # 拖拽
    def Drag(self, x1, y1, x2, y2):
        self.Move(x1, y1)
        self._MouseDown()
        self.Move(x2, y2)
        self._MouseUP()

    # 热键封装
    def hotKey(self, key=["a"]):
        if len(key) == 1:
            self._HotKey1(key[0])
        elif len(key) == 2:
            self._HotKey2(key[0], key[1])
        elif len(key) == 3:
            self._HotKey3(key[0], key[1], key[2])


if __name__ == "__main__":
    # 直接运行：3 秒后用拟人轨迹把鼠标移动到目标（默认左上角 (20,20)）。
    # 也可传坐标： python ujmouse_core.py 800 400
    import sys
    nums = [a for a in sys.argv[1:] if a.lstrip("-").isdigit()]
    target = (int(nums[0]), int(nums[1])) if len(nums) >= 2 else (20, 20)

    m = UJMouse()
    print("已载入真人轨迹:", DATA["dataSize"], "条，每条", DATA["size"], "点")
    print("3 秒后开始移动鼠标到", target, " ...（把手从鼠标上拿开）")
    time.sleep(3)
    m.Move(*target)
    print("移动完成。")
