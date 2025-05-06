from palaestrai.experiment import EnvironmentTerminationCondition
from warnings import warn


class VanillaSimControllerTerminationCondition(
    EnvironmentTerminationCondition
):
    def __init__(self, *args, **kwargs):
        warn(
            f"The class {self.__class__.__name__} is deprecated, "
            f"please use "
            f"palaestrai.experiment.EnvironmentTerminationCondition "
            f"instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)
