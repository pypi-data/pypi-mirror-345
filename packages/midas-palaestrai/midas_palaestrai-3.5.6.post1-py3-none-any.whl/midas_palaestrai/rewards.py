import logging
import math
from typing import List

import numpy as np
from palaestrai.agent import (
    ActuatorInformation,
    RewardInformation,
    SensorInformation,
)
from palaestrai.environment import Reward
from palaestrai.types import Box, Discrete

LOG = logging.getLogger(__name__)


def gauss_norm(
    raw_value: float,
    mu: float = 1,
    sigma: float = 0.1,
    c: float = 0.5,
    a: float = -1,
):
    if not isinstance(raw_value, float):
        try:
            raw_value = sum(raw_value)
        except TypeError:
            return 0
    gaus_reward = a * math.exp(-((raw_value - mu) ** 2) / (2 * sigma**2)) - c
    return gaus_reward


class NoExtGridHealthReward(Reward):
    def __init__(self, **params):
        super().__init__(**params)
        self.grid_health_sensor = params.get(
            "grid_health", "Powergrid-0.Grid-0.health"
        )
        self.ext_grid_sensor = params.get(
            "ext_grid", "Powergrid-0.0-ext_grid-0.p_mw"
        )

    def __call__(self, state, *args, **kwargs):
        rewards = []
        for sensor in state:
            if self.grid_health_sensor == sensor.uid:
                system_health_reward = RewardInformation(
                    sensor.value, Discrete(2), "grid_health_reward"
                )
                rewards.append(system_health_reward)
            elif self.ext_grid_sensor in sensor.uid:
                reward = abs(sensor.value)
                external_grid_penalty_reward = RewardInformation(
                    reward, Discrete(1000), "external_grid_penalty_reward"
                )
                rewards.append(external_grid_penalty_reward)
        return rewards


class GridHealthReward(Reward):
    def _line_load(self, value):
        if not isinstance(value, int):
            return 0
        if value <= 100:
            return 0
        if value > 100 and value <= 120:
            return value - 100
        if value > 120:
            return np.exp((value - 100) / 10)

    def __call__(
        self, state: List[SensorInformation], *arg, **kwargs
    ) -> List[ActuatorInformation]:
        reward = 0
        for sensor in state:
            if "vm_pu" in sensor.uid:
                reward += (gauss_norm(sensor(), 1, 0.02, 1.0, 2)) * 50
            if "line-" in sensor.uid:
                reward -= self._line_load(sensor())
        final_reward = RewardInformation(
            np.array(reward, dtype=np.float32),
            Box(-np.inf, np.inf, shape=()),
            "grid_health_reward",
        )
        return [final_reward]


class ExtendedGridHealthReward(Reward):
    """Standard extended grid state reward

    This reward tries to give a complete overview over the current health of
    a MIDAS power grid.
    It is a *vectorized* reward, meaning that it does not simply provide one
    value, but rather a vector of different values.
    The difference between this reward and the agent's sensors is that the
    *ExtendedGridHealthReward* provides complete information, whereas an
    agent's sensors can be limited in score.
    It encompasses the following values:

    **Voltage Band:**

    * ``vm_pu-min``
    * ``vm_pu-max``
    * ``vm_pu-mean``
    * ``vm_pu-median``
    * ``vm_pu-std``

    **Line Loads:**

    * ``lineload-min``
    * ``lineload-max``
    * ``lineload-mean``
    * ``lineload-median``
    * ``lineload-std``

    **Bus Connection Status:**

    * ``num_in_service``
    * ``num_out_if_service``

    All values are provided as separate ::`RewardInformation` objects with the
    given ID.
    """

    def __call__(
        self, state: List[SensorInformation], *args, **kwargs
    ) -> List[RewardInformation]:
        voltages = np.sort(
            np.array([s() for s in state if "vm_pu" in s.uid]), axis=None
        )
        voltage_rewards = [
            RewardInformation(
                np.array(voltages[0], dtype=np.float32),
                Box(0.0, np.inf, shape=()),
                reward_id="vm_pu-min",
            ),
            RewardInformation(
                np.array(voltages[-1], dtype=np.float32),
                Box(0.0, np.inf, shape=()),
                reward_id="vm_pu-max",
            ),
            RewardInformation(
                np.array(voltages[len(voltages) // 2], dtype=np.float32),
                Box(0.0, np.inf, shape=()),
                reward_id="vm_pu-median",
            ),
            RewardInformation(
                np.array(voltages.mean(), dtype=np.float32),
                Box(0.0, np.inf, shape=()),
                reward_id="vm_pu-mean",
            ),
            RewardInformation(
                np.array(voltages.std(), dtype=np.float32),
                Box(0.0, np.inf, shape=()),
                reward_id="vm_pu-std",
            ),
        ]

        lineloads = np.sort(
            np.array([s() for s in state if ".loading_percent" in s.uid]),
            axis=None,
        )
        lineload_rewards = [
            RewardInformation(
                np.array(lineloads[0], dtype=np.float32),
                Box(0.0, np.inf, shape=()),
                reward_id="lineload-min",
            ),
            RewardInformation(
                np.array(lineloads[-1], dtype=np.float32),
                Box(0.0, np.inf, shape=()),
                reward_id="lineload-max",
            ),
            RewardInformation(
                np.array(lineloads[len(lineloads) // 2], dtype=np.float32),
                Box(0.0, np.inf, shape=()),
                reward_id="lineload-median",
            ),
            RewardInformation(
                np.array(lineloads.mean(), dtype=np.float32),
                Box(0.0, np.inf, shape=()),
                reward_id="lineload-mean",
            ),
            RewardInformation(
                np.array(lineloads.std(), dtype=np.float32),
                Box(0.0, np.inf, shape=()),
                reward_id="lineload-std",
            ),
        ]

        in_service = np.sort(
            np.array([s() for s in state if "in_service" in s.uid]), axis=None
        )
        in_service_unique, in_service_counts = np.unique(
            in_service, return_counts=True
        )
        in_service_dict = dict(zip(in_service_unique, in_service_counts))

        num_in_service = (
            in_service_dict.get(1) if (1 in in_service_dict) else 1
        )

        num_out_of_service = (
            in_service_dict.get(0) if (0 in in_service_dict) else 0
        )

        in_service_rewards = [
            RewardInformation(
                np.array(num_in_service, dtype=np.int32),
                Discrete(len(in_service) + 1),
                reward_id="num_in_service",
            ),
            RewardInformation(
                np.array(num_out_of_service, dtype=np.int32),
                Discrete(len(in_service) + 1),
                reward_id="num_out_of_service",
            ),
        ]

        return voltage_rewards + lineload_rewards + in_service_rewards


class AllesDestroyAllPire2RewardIchWeissNicht(Reward):
    """This is a reward for classic ARL.

    Despite its unique name, this is a serious reward for the use
    with a constrainted power grid model from MIDAS.

    It checks all available power grid sensors and creates a score
    based on the *Technische Anschlussregeln Mittelspannung* (TAR-MS).

    Every component in a healthy state gives one point while each
    component that is out of its usual operation state gives ten minus
    points.

    Additionally, this reward includes everything from the
    :class:`ExtendedGridHealthReward` and can be used instead of that
    reward.

    """

    def __init__(
        self,
        reward_value: int = 1,
        small_penalty_value: int = 10,
        large_penalty_value: int = 100,
    ):
        self._reward_value: int = reward_value
        self._small_penalty_value: int = small_penalty_value
        self._large_penalty_value: int = large_penalty_value

    def __call__(
        self, state: List[SensorInformation], *args, **kwargs
    ) -> List[RewardInformation]:
        points = 0
        min_reward = 0
        max_reward = 0
        for s in state:
            if "Powergrid" not in s.uid:
                continue

            if "in_service" in s.uid:
                min_reward -= self._large_penalty_value
                max_reward += self._reward_value
                if s():
                    points += self._reward_value
                else:
                    points -= self._large_penalty_value

            if "loading_percent" in s.uid:
                min_reward -= self._large_penalty_value
                max_reward += self._reward_value
                if s() < 95:
                    points += self._reward_value
                elif s() < 100:
                    points -= self._reward_value
                else:
                    points -= self._large_penalty_value

            if "vm_pu" in s.uid:
                min_reward -= self._large_penalty_value
                max_reward += self._reward_value
                if 0.95 <= s() <= 1.05:
                    points += self._reward_value
                elif 0.9 <= s() <= 1.1:
                    points -= self._small_penalty_value
                else:
                    points -= self._large_penalty_value

        extgrid_rew = ExtendedGridHealthReward()
        rewards = extgrid_rew(state)

        rewards.append(
            RewardInformation(
                points,
                Box(min_reward, max_reward, (), np.int64),
                reward_id="ErikaReward",
            )
        )
        LOG.info(
            f"Reward ({self.__class__}) gives {points} points (RewardSpace=["
            f"{min_reward}, {max_reward}])"
        )
        return rewards


class RetroPsiReward(Reward):
    def __call__(
        self, state: List[SensorInformation], *args, **kwargs
    ) -> List[RewardInformation]:
        erika_rew = AllesDestroyAllPire2RewardIchWeissNicht()
        rewards = erika_rew(state)

        renewable_energy: float = 0.0
        fossil_energy: float = 0.0
        storage_usage: float = 0.0
        ext_grid_active_usage: float = 0.0
        ext_grid_reactive_usage: float = 0.0
        agent_bids: dict = {}

        for sensor in state:
            if (
                "Photovoltaic" in sensor.uid or "Biogas" in sensor.uid
            ) and "p_mw" in sensor.uid:
                renewable_energy += sensor.value

            if "Diesel" in sensor.uid and "p_mw" in sensor.uid:
                fossil_energy += sensor.value

            if "Battery" in sensor.uid and "p_mw" in sensor.uid:
                storage_usage += sensor.value

            if "ext_grid" in sensor.uid:
                if "p_mw" in sensor.uid:
                    ext_grid_active_usage += sensor.value
                if "q_mvar" in sensor.uid:
                    ext_grid_reactive_usage += sensor.value
            if "MarketAgentModel" in sensor.uid:
                _, eid, attr = sensor.uid.split(".")
                agent_bids.setdefault(eid, {})
                if "price" in attr:
                    agent_bids[eid]["price"] = sensor.value
                if "amount" in attr:
                    agent_bids[eid]["amount"] = sensor.value

        for eid, offer in agent_bids.items():
            rewards.append(
                RewardInformation(
                    offer["price"] * offer["amount"],
                    Box(-100, 100, (), np.double),
                    f"profit_{eid}",
                )
            )
            print(rewards[-1])

        # rewards.append(RewardInformation(sensor.value, Box(-100, 100, (1,)
        # , np.double), f"profit_{sensor.uid.split('.')[1]}"))

        rewards.append(
            RewardInformation(
                renewable_energy,
                Box(0, 1000, (), np.float32),
                "renewable_energy",
            )
        )
        rewards.append(
            RewardInformation(
                fossil_energy, Box(0, 1000, (), np.float32), "fossil_energy"
            )
        )
        rewards.append(
            RewardInformation(
                ext_grid_active_usage,
                Box(-1000, 1000, (), np.float32),
                "ext_grid_active_usage",
            )
        )
        rewards.append(
            RewardInformation(
                ext_grid_reactive_usage,
                Box(-1000, 1000, (), np.float32),
                "ext_grid_reactive_usage",
            )
        )
        rewards.append(
            RewardInformation(
                storage_usage, Box(-1000, 1000, (), np.double), "storage_usage"
            )
        )

        return rewards


class VoltageBandReward(Reward):
    def __call__(
        self, state: List[SensorInformation], *args, **kwargs
    ) -> List[RewardInformation]:
        return [
            RewardInformation(
                reward_id=f"{s.uid}",
                reward_value=s(),
                observation_space=Box(0.0, 2.0, (), np.double),
            )
            for s in state
            if "vm_pu" in s.uid
        ]


class VoltageBandDeviationReward(Reward):
    def __call__(
        self, state: List[SensorInformation], *args, **kwargs
    ) -> List[RewardInformation]:
        return [
            RewardInformation(
                reward_id=f"{s.uid}-dev",
                reward_value=s() - 1.0,
                observation_space=Box(-1.1, 1.1, (), np.double),
            )
            for s in state
            if "vm_pu" in s.uid
        ]
