from __future__ import annotations

import functools
import logging
from typing import TYPE_CHECKING, Dict, Optional, Union

import numpy as np
from palaestrai.agent import Objective

from .gauss import normal_distribution_pdf

if TYPE_CHECKING:
    from palaestrai.agent import Memory

LOG = logging.getLogger("palaestrai.agent.objective")


class ArlDefenderObjective(Objective):
    """Objective function for the ARL Defender

    This objective takes the environment's reward as well as the agent's
    sensor readings into account.
    It considers the overall mean voltage, the agent's voltage sensor values,
    as well as the number of buses in service.
    """

    def __init__(
        self, params: Dict = dict(), alpha=1 / 3, beta=1 / 3, gamma=1 / 3
    ):
        super().__init__(params)
        self._weight_alpha = alpha
        self._weight_beta = beta
        self._weight_gamma = gamma
        self._mu = 1.0
        self._sigma = 0.032
        self._c = 0.0
        self._a = 1.0
        self._gauss_fc = functools.partial(
            normal_distribution_pdf,
            mu=self._mu,
            sigma=self._sigma,
            c=self._c,
            a=self._a,
        )

    def _reward_voltage_objective(self, memory: Memory) -> float:
        vm_pu = (
            memory.tail(1)
            .rewards.filter(like="vm_pu-mean", axis=1)
            .sum(axis=1)  # Coerce to 0.0 if empty
        )
        try:
            return self._gauss_fc(vm_pu.item())
        except ValueError:
            return 0.0

    def _observable_voltages_objective(self, memory: Memory):
        vm_pu_gaussed = (
            memory.tail(1)
            .sensor_readings.filter(like="vm_pu", axis=1)
            .apply(self._gauss_fc)
        )
        try:
            return vm_pu_gaussed.mean(axis=1).item()
        except ValueError:
            return 0.0

    def _in_service_objective(self, memory: Memory) -> float:
        obs_in_service = memory.tail(1).sensor_readings.filter(
            like="in_service", axis=1
        )
        try:
            num_in_service = float(obs_in_service.sum(axis=1).item())
            count_in_service = int(obs_in_service.count(axis=1).item())
            if count_in_service == 0:
                LOG.error(
                    "There are no 'in_service' sensors specified, "
                    "but this objective needs them! Throwing an error and "
                    "terminating gracefully"
                )
            return num_in_service / float(count_in_service)
        except ValueError:
            return 0.0

    def internal_reward(
        self, memory: Memory, **kwargs
    ) -> Optional[Union[np.ndarray, float]]:
        try:
            reward_vm_objective = self._reward_voltage_objective(memory)
            obs_vm_objective = self._observable_voltages_objective(memory)
            in_service = self._in_service_objective(memory)
            return (
                self._weight_alpha * reward_vm_objective
                + self._weight_beta * obs_vm_objective
                + self._weight_gamma * in_service
            )
        except TypeError:  # No such column (yet)
            return 0.0
        except IndexError:  # Out-of-bounds: not enough data
            return 0.0
