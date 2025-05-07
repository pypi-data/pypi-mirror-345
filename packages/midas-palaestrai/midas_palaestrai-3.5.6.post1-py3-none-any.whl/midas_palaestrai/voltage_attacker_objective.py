import logging
from typing import Dict, Optional

import numpy as np
from palaestrai.agent.objective import Objective

from .gauss import normal_distribution_pdf

LOG = logging.getLogger("palaestrai.agent.objective")


class VoltageBandViolationPendulum(Objective):
    VM_PU_LOW = 0.85
    VM_PU_HIGH = 1.15
    SIGMA = -0.05
    C = -10.0
    A = -12.0

    def __init__(self, params: Dict = dict()):
        super().__init__(params)
        self._sigma = params.get("sigma", VoltageBandViolationPendulum.SIGMA)
        self._c = params.get("c", VoltageBandViolationPendulum.C)
        self._a = params.get("a", VoltageBandViolationPendulum.A)
        self.step = 0

    def internal_reward(self, memory, **kwargs) -> Optional[float]:
        """Expect Voltage values and reward voltage band violations."""
        try:
            vm_pu = (
                memory.tail(1)
                .rewards.filter(like="vm_pu-median", axis=1)
                .iloc[-1]
                .item()
            )
        except TypeError:  # No such column (yet)
            return None
        except IndexError:  # Out-of-bounds: not enough data
            return None

        objective = normal_distribution_pdf(
            x=vm_pu, mu=1.0, sigma=self._sigma, c=self._c, a=self._a
        )
        objective += normal_distribution_pdf(
            x=vm_pu, mu=0.83, sigma=0.01, c=0.0, a=self._a
        )
        objective += normal_distribution_pdf(
            x=vm_pu, mu=1.16, sigma=0.01, c=0.0, a=self._a
        )

        self.step += 1
        # This rounds the objective to a float32
        return np.array(objective, dtype=np.float32).item()
