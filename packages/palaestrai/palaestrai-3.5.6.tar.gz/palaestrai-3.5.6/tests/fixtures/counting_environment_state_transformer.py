from palaestrai.environment import (
    EnvironmentStateTransformer,
    EnvironmentState,
)


class CountingWorldStateTransformer(EnvironmentStateTransformer):
    """Replaces the current world state with am incremented number."""

    def __init__(self):
        self.count = 0
        super().__init__()

    def __call__(
        self, environment_state: EnvironmentState
    ) -> EnvironmentState:
        self.count += 1
        environment_state.world_state = self.count
        return environment_state
