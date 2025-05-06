from __future__ import annotations
from typing import Union, List, Callable

import numpy as np

from palaestrai.agent import (
    SensorInformation,
    ActuatorInformation,
    RewardInformation,
)


def concat_flattened_values(
    information_classes: Union[
        List[SensorInformation],
        List[ActuatorInformation],
        List[RewardInformation],
    ]
):
    return np.concatenate(
        [
            (
                information_class.value.flatten()
                if information_class.space.shape  # type: ignore[union-attr]
                else np.array([information_class.value])
            )
            for information_class in information_classes
        ]
    )


def concat_flattened_act_scale_bias(
    actuator_informations: List[ActuatorInformation],
    np_fun: Callable,
):
    assert np_fun is np.add or np_fun is np.subtract

    values = np.concatenate(
        [
            (
                (
                    np_fun(
                        actuator_information.space.high,  # type: ignore[attr-defined]
                        actuator_information.space.low,  # type: ignore[attr-defined]
                    )
                    / 2
                ).flatten()
                if actuator_information.space.shape  # type: ignore[attr-defined]
                else np.array(
                    [
                        np_fun(
                            actuator_information.space.high,  # type: ignore[attr-defined]
                            actuator_information.space.low,  # type: ignore[attr-defined]
                        )
                        / 2
                    ]
                )
            )
            for actuator_information in actuator_informations
        ]
    )

    return values
