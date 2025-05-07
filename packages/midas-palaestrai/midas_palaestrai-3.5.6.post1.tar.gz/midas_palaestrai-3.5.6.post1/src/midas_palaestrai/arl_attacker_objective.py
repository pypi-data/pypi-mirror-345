from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Dict, Optional, Union

import numpy as np

from .arl_defender_objective import ArlDefenderObjective

if TYPE_CHECKING:
    from palaestrai.agent import Memory
LOG = logging.getLogger("palaestrai.agent.objective")


class ArlAttackerObjective(ArlDefenderObjective):
    def __init__(
        self, params: Dict = dict(), alpha=1 / 3, beta=1 / 3, gamma=1 / 3
    ):
        super().__init__(params, alpha, beta, gamma)

    def internal_reward(
        self, memory: Memory, **kwargs
    ) -> Optional[Union[np.ndarray, float]]:
        return super().internal_reward(memory) * -1.0 + 1.0
