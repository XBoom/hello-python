"""第 01 课：Python 核心习惯（AI 代码里天天见）

目标：跑通本文件，理解列表推导、字典、类型标注、简单函数。
有其他语言底子的话，重点看「写法差异」，不用纠结「什么是循环」。

运行（在仓库根目录）:
    source .venv/bin/activate
    python lessons/01_core_habits.py
"""

from __future__ import annotations


# --- 1. 列表推导：一行生成数据 ---
xs = [x * 2 for x in range(5)]
assert xs == [0, 2, 4, 6, 8], xs


# --- 2. 字典：配置、超参、样本字段都很常见 ---
cfg = {"lr": 1e-3, "epochs": 10}
assert cfg["lr"] == 0.001
assert "epochs" in cfg


# --- 3. 函数 + 类型标注（读库文档会轻松很多） ---
def normalize(x: list[float]) -> list[float]:
    """减去均值，得到「零均值」向量（很多特征预处理的第一步）。"""
    if not x:
        return []
    mean = sum(x) / len(x)
    return [v - mean for v in x]


out = normalize([1.0, 2.0, 3.0])
assert out == [-1.0, 0.0, 1.0], out


# --- 4. 小练习（改下面的 TODO，让 assert 通过） ---
def squared_evens(n: int) -> list[int]:
    """返回 0..n-1 里所有偶数的平方。

    例子: squared_evens(6) -> [0, 4, 16]
    提示: 列表推导 + % 2 == 0
    """
    return [x ** 2 for x in range(n) if x % 2 == 0]


def main() -> None:
    print("01_core_habits: 前半部分已通过 ✓")
    print("cfg =", cfg)
    print("normalize([1,2,3]) =", out)

    # 完成 TODO 后取消下一行注释，再跑一次
    result = squared_evens(6)
    assert result == [0, 4, 16], result
    print("练习也通过 ✓", result)
    print("下一步：实现 squared_evens，取消 main 里的注释后再跑。")


if __name__ == "__main__":
    main()
