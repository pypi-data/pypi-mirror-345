import numpy as np


def normal_distribution_pdf(
    x: float, mu: float, sigma: float, c: float, a: float
) -> float:
    return (
        a
        * np.exp(
            -((np.array(x).astype(np.float64) - mu) ** 2) / (2 * sigma**2)
        )
        - c
    )
