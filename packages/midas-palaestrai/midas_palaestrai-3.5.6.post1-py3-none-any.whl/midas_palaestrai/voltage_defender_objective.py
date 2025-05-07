import logging
from enum import Enum
from typing import Dict, Optional

import numpy as np
from palaestrai.agent.objective import Objective

from .gauss import normal_distribution_pdf

LOG = logging.getLogger("palaestrai.agent.objective")


class _State(Enum):
    LOW = 0
    NOMINAL = 1
    HIGH = 2


class VoltageDefenderObjective(Objective):
    BETA = 2
    VM_PU_LOW = 0.98
    VM_PU_HIGH = 1.02
    OBJECTIVE_PARAMS = {
        _State.LOW: {"mu": 1.0, "sigma": 0.12, "c": 0.0, "a": 10.0},
        _State.NOMINAL: {"mu": 1.0, "sigma": 0.032, "c": 0.0, "a": 10.0},
        _State.HIGH: {"mu": 1.0, "sigma": 0.032, "c": 0.0, "a": 10.0},
    }

    def __init__(
        self,
        params: Dict = dict(),
        beta=BETA,
        vm_pu_low=VM_PU_LOW,
        vm_pu_high=VM_PU_HIGH,
    ):
        super().__init__(params)
        self._beta = beta
        self._vm_pu_low = vm_pu_low
        self._vm_pu_high = vm_pu_high
        self._state = _State.NOMINAL
        self._steps_in_state = 0
        self._previous_vm_pu = None

    def _vm_to_state(self, vm: float):
        if vm <= self._vm_pu_low:
            return _State.LOW
        if vm >= self._vm_pu_high:
            return _State.HIGH
        return _State.NOMINAL

    def internal_reward(self, memory, **kwargs) -> Optional[float]:
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

        current_state = self._vm_to_state(vm_pu)

        if self._state == current_state:
            self._steps_in_state += 1
        else:
            self._steps_in_state = 0

        delta = 0.0
        if self._previous_vm_pu is not None:
            delta = vm_pu - self._previous_vm_pu

        if self._steps_in_state > self._beta:
            current_state = _State.NOMINAL
        if current_state == _State.LOW and delta > 0:
            current_state = _State.NOMINAL
        if current_state == _State.HIGH and delta < 0:
            current_state = _State.NOMINAL

        objective = normal_distribution_pdf(
            vm_pu, **VoltageDefenderObjective.OBJECTIVE_PARAMS[current_state]
        )

        self._previous_vm_pu = vm_pu
        self._state = current_state

        # This rounds the objective to a float32
        return np.array(objective, dtype=np.float32).item()
