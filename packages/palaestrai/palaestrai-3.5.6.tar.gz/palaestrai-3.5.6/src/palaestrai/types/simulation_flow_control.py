from enum import Enum, auto


class SimulationFlowControl(Enum):
    """Simulation flow control indication

    Allows components to indicate flow control of a simulation.

    Attributes
    ----------

    CONTINUE:
        Continue the simulation
    RESET:
        Reset the simulation/worker (i.e., restart it, but try to keep the
        memory of the last run).
        Increments the episode counter of the current phase.
    RESTART:
        Shutdown the simulation/worker and restart; increments the episode
        counter of the current phase
    STOP_SIMULATION:
        End the current simulation, but only for the current worker, not for
        all workers.
    STOP_PHASE:
        End the current phase for all workers/simulations in it
    SHUTDOWN:
        Shutdown of a whole experiment run
    """

    CONTINUE = auto()
    RESET = auto()
    RESTART = auto()
    STOP_SIMULATION = auto()
    STOP_PHASE = auto()
    SHUTDOWN = auto()
