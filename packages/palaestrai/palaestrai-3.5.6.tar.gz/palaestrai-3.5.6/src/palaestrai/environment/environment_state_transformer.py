from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .environment_state import EnvironmentState


class EnvironmentStateTransformer(ABC):
    """Transforms environment state data before transmitting it to the store

    The WorldStateTransformer is a way to tranform the data that is stored as
    world state. Any world state transformer must be a callable that receives
    an ::`EnvironmentState` object and is expected to return it after the
    transformation.
    """

    def __init__(self, **params):
        self._params = params

    @abstractmethod
    def __call__(
        self, environment_state: EnvironmentState
    ) -> EnvironmentState:
        """Transforms an environment state.

        Parameters
        ----------
        environment_state: ::`EnvironmentState`
            The current state of the environment as represented by an
            ::`EnvironmentState` object. This includes all sensor readings,
            rewards, and whatever the environment thinks its state is.

        Returns
        -------
        ::`EnvironmentState`
            The modified environment state object for storage.
        """
        pass

    def __str__(self):
        return f"{self.__class__.__name__}(id={id(self):x})"
