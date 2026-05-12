"""第 2 课实践任务 4：从零训练简单线性回归 y = w*x + b。"""
import numpy as np


def main():
    rng = np.random.default_rng(42)
    n = 100
    x = rng.uniform(-2.0, 2.0, size=n)
    noise = rng.normal(0.0, 0.1, size=n)
    y_true_w, y_true_b = 2.0, 1.0
    y = y_true_w * x + y_true_b + noise

    w, b = 0.0, 0.0
    lr = 0.05
    epochs = 1000

    for _ in range(epochs):
        pred = w * x + b
        err = pred - y
        mse = np.mean(err ** 2)
        grad_w = 2.0 * np.mean(err * x)
        grad_b = 2.0 * np.mean(err)
        w -= lr * grad_w
        b -= lr * grad_b

    pred_final = w * x + b
    mse_final = np.mean((pred_final - y) ** 2)
    print("final w =", round(w, 6), "final b =", round(b, 6))
    print("final MSE =", round(mse_final, 6))
    print("(target roughly w=2, b=1)")


if __name__ == "__main__":
    main()
