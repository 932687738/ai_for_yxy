"""第 2 课实践任务 1：向量与矩阵（NumPy）。"""
import numpy as np


def main():
    a = np.array([1.0, 2.0, 3.0])
    b = np.array([4.0, 5.0, 6.0])

    print("a =", a, "shape =", a.shape)
    print("b =", b, "shape =", b.shape)
    print("a + b =", a + b)
    print("3 * a =", 3.0 * a)
    print("dot(a, b) =", np.dot(a, b))
    print("||a|| (L2) =", np.linalg.norm(a))
    print("||b|| (L2) =", np.linalg.norm(b))
    print("euclidean(a, b) =", np.linalg.norm(a - b))

    m32 = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
    m21 = np.array([[1.0], [2.0]])
    print("m32 shape =", m32.shape)
    print("m21 shape =", m21.shape)
    prod = m32 @ m21
    print("m32 @ m21 =", prod.flatten(), "shape =", prod.shape)


if __name__ == "__main__":
    main()
