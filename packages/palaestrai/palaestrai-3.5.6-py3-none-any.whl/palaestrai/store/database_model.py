from __future__ import annotations

import io
from typing import TYPE_CHECKING

import ruamel.yaml
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql
from sqlalchemy import func
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlite3 import Connection as SQLite3Connection

from palaestrai.store.database_base import Base

if TYPE_CHECKING:
    import palaestrai.experiment

yaml = ruamel.yaml.YAML(typ="safe")


@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()


class Experiment(Base):
    """A whole experiment, including Design of Experiments

    Experiments are the master objects of the palaestrAI store. Experiments
    define a study. This includes variations over parameters as the user
    wishes. An experiment spawns any number of concrete ::`ExperimentRun`
    objects.
    """

    __tablename__ = "experiments"
    id = sa.Column(sa.INTEGER, primary_key=True, unique=True, index=True)
    name = sa.Column(sa.String, nullable=True)
    _document = sa.Column("document", sa.TEXT)
    _document_json = sa.Column(
        "document_json",
        sa.JSON().with_variant(
            sqlalchemy.dialects.postgresql.JSONB(), "postgresql"
        ),
    )
    experiment_runs = relationship(
        "ExperimentRun",
        back_populates="experiment",
        cascade="all, delete",
        passive_deletes=True,
    )

    @hybrid_property
    def document(self):
        return self._document_json

    @document.setter  # type:ignore[no-redef]
    def document(self, experiment):
        self._document_json = experiment
        self._document = repr(experiment)

    def __str__(self):
        return '<Experiment(id=%s, name="%s")>' % (self.id, self.name)


class ExperimentRun(Base):
    """A concrete experiment run created from an experiment

    An experiment run is a concrete instance of an experiment. In it, any
    parameter variation is replaced by actual parameter settings. An
    experiment can spawn as many experiment runs as the user wishes. I.e., an
    experiment run is a concrete configuration.
    """

    __tablename__ = "experiment_runs"
    id = sa.Column(sa.Integer, primary_key=True, unique=True, index=True)
    uid = sa.Column(sa.String(255), unique=True, index=True)
    hash = sa.Column(sa.String(255), unique=True, index=True)
    experiment_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("experiments.id", ondelete="CASCADE"),
        index=True,
    )
    _document = sa.Column("document", sa.TEXT)
    _document_json = sa.Column(
        "document_json",
        sa.JSON().with_variant(
            sqlalchemy.dialects.postgresql.JSONB(), "postgresql"
        ),
    )
    experiment = relationship("Experiment", back_populates="experiment_runs")
    experiment_run_instances = relationship(
        "ExperimentRunInstance",
        back_populates="experiment_run",
        cascade="all, delete",
        passive_deletes=True,
    )

    @hybrid_property
    def document(self) -> palaestrai.experiment.ExperimentRun:
        return self._document_json

    @document.setter  # type:ignore[no-redef]
    def document(self, experiment_run: palaestrai.experiment.ExperimentRun):
        er_dict = experiment_run.__getstate__()
        del er_dict["_rng"]
        del er_dict["_instance_uid"]
        self._document_json = er_dict

        # NOTE: We don't need to register the class here anymore,
        #   since the ExperimentRun can now supply us with its dict state via
        #   __getstate__().

        sio = io.StringIO()
        yaml.dump(er_dict, sio)
        self._document = sio.getvalue()

    def __str__(self):
        return (
            '<ExperimentRun(id=%s, uid="%s", experiment_id=%s, '
            "document=%s>"
            % (self.id, self.uid, self.experiment_id, self.document)
        )


class ExperimentRunInstance(Base):
    """An execution of an experiment run

    Each experiment run can be executed as many times as a user wishes.
    This does not change its outcome, but for reproducibility, such re-runs
    are sensible. When an experiment run is actually executed - the experiment
    run being the blue print of an actual execution -, an experiment run
    instance is created.
    """

    __tablename__ = "experiment_run_instances"
    id = sa.Column(sa.Integer, primary_key=True, unique=True, index=True)
    uid = sa.Column(sa.String(196), unique=True, index=True)
    created_at = sa.Column(sa.DateTime, default=func.now())
    experiment_run_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(ExperimentRun.id, ondelete="CASCADE"),
        index=True,
    )
    experiment_run = relationship(
        "ExperimentRun", back_populates="experiment_run_instances"
    )
    experiment_run_phases = relationship(
        "ExperimentRunPhase",
        back_populates="experiment_run_instance",
        cascade="all, delete",
        passive_deletes=True,
    )


class ExperimentRunPhase(Base):
    __tablename__ = "experiment_run_phases"
    id = sa.Column(sa.INTEGER, primary_key=True, unique=True, index=True)
    uid = sa.Column(sa.String(255), index=True, nullable=False)
    number = sa.Column(sa.INTEGER, nullable=False)
    mode = sa.Column(sa.String(128), nullable=True)
    configuration = sa.Column(
        "configuration",
        sa.JSON().with_variant(
            sqlalchemy.dialects.postgresql.JSONB(), "postgresql"
        ),
        nullable=True,
    )
    experiment_run_instance_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(ExperimentRunInstance.id, ondelete="CASCADE"),
        index=True,
    )
    experiment_run_instance = relationship(
        "ExperimentRunInstance", back_populates="experiment_run_phases"
    )
    environments = relationship(
        "Environment",
        back_populates="experiment_run_phase",
        cascade="all, delete",
        passive_deletes=True,
    )
    agents = relationship(
        "Agent",
        back_populates="experiment_run_phase",
        cascade="all, delete",
        passive_deletes=True,
    )
    __table_args__ = (
        sa.UniqueConstraint("uid", "experiment_run_instance_id"),
        sa.UniqueConstraint("number", "experiment_run_instance_id"),
    )


class Environment(Base):
    __tablename__ = "environments"
    id = sa.Column(sa.Integer, primary_key=True, unique=True, index=True)
    uid = sa.Column(sa.String(255), nullable=False, index=True)
    worker_uid = sa.Column(sa.String(255), nullable=False, index=True)
    environment_conductor_uid = sa.Column(sa.String(255), nullable=False)
    type = sa.Column(sa.String(255), nullable=True)
    parameters = sa.Column("parameters", sa.JSON, nullable=True)
    experiment_run_phase_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(ExperimentRunPhase.id, ondelete="CASCADE"),
        index=True,
    )
    experiment_run_phase = relationship(
        "ExperimentRunPhase", back_populates="environments"
    )
    world_states = relationship(
        "WorldState",
        back_populates="environment",
        cascade="all, delete",
        passive_deletes=True,
    )
    __table_args__ = (
        sa.UniqueConstraint("uid", "worker_uid", "experiment_run_phase_id"),
    )

    def __str__(self):
        return (
            f'<Environment(id={self.id}, uid="{self.uid}", type="'
            f'{self.type}", parameters=({len(self.parameters)} chars))>'
        )


class WorldState(Base):
    __tablename__ = "world_states"
    id = sa.Column(
        sa.Integer,
        autoincrement=True,
        primary_key=True,
        unique=True,
        index=True,
    )
    walltime = sa.Column(
        sa.TIMESTAMP(timezone=True),
        default=func.now(),
        primary_key=False,
        nullable=False,
    )
    simtime_ticks = sa.Column(sa.Integer)
    simtime_timestamp = sa.Column(sa.TIMESTAMP)
    episode = sa.Column("episode", sa.Integer, default=1)
    state_dump = sa.Column(
        "state_dump",
        sa.JSON().with_variant(
            sqlalchemy.dialects.postgresql.JSONB(), "postgresql"
        ),
    )
    done = sa.Column(
        sa.Boolean,
        unique=False,
        nullable=False,
        default=bool(False),
    )
    environment_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(Environment.id, ondelete="CASCADE"),
        index=True,
    )
    environment = relationship("Environment", back_populates="world_states")

    def __str__(self):
        return (
            f"<WorldState id={self.id}, "
            f"walltime={self.walltime}, "
            f"simtime_ticks={self.simtime_ticks}, "
            f"simtime_timestamp={self.simtime_timestamp} "
            f"done={self.done}>"
        )


class Agent(Base):
    __tablename__ = "agents"
    id = sa.Column(sa.Integer, primary_key=True, unique=True, index=True)
    uid = sa.Column(sa.String(255), nullable=False, index=True)
    name = sa.Column(sa.String(255), nullable=True)
    muscles = sa.Column(
        "muscles",
        sa.JSON().with_variant(
            sqlalchemy.dialects.postgresql.JSONB(), "postgresql"
        ),
        nullable=False,
        default=list(),
    )
    configuration = sa.Column(
        "configuration",
        sa.JSON().with_variant(
            sqlalchemy.dialects.postgresql.JSONB(), "postgresql"
        ),
        nullable=True,
    )
    experiment_run_phase_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(ExperimentRunPhase.id, ondelete="CASCADE"),
        nullable=False,
    )
    experiment_run_phase = relationship(
        "ExperimentRunPhase", back_populates="agents"
    )
    brain_states = relationship(
        "BrainState",
        back_populates="agent",
        cascade="all, delete",
        passive_deletes=True,
    )
    muscle_actions = relationship(
        "MuscleAction",
        order_by="MuscleAction.id",
        back_populates="agent",
        cascade="all, delete",
        passive_deletes=True,
    )
    __table_args__ = (sa.UniqueConstraint("uid", "experiment_run_phase_id"),)


class BrainState(Base):
    __tablename__ = "brain_states"
    id = sa.Column(
        sa.Integer,
        autoincrement=True,
        primary_key=True,
        unique=True,
        index=True,
    )
    walltime = sa.Column(
        sa.TIMESTAMP(timezone=True),
        default=func.now(),
        primary_key=False,
        nullable=False,
    )
    state = sa.Column(sa.LargeBinary, nullable=True)
    tag = sa.Column(sa.String(96))
    simtime_ticks = sa.Column(sa.Integer, nullable=True)
    simtime_timestamp = sa.Column(sa.TIMESTAMP, nullable=True)
    agent_id = sa.Column(
        sa.Integer, sa.ForeignKey(Agent.id, ondelete="CASCADE"), index=True
    )
    agent = relationship("Agent", back_populates="brain_states")


class MuscleAction(Base):
    __tablename__ = "muscle_actions"
    id = sa.Column(
        sa.Integer,
        autoincrement=True,
        primary_key=True,
        unique=True,
        index=True,
    )
    walltime = sa.Column(
        sa.TIMESTAMP(timezone=True),
        default=func.now(),
        primary_key=False,
        nullable=False,
    )
    agent_id = sa.Column(
        sa.Integer, sa.ForeignKey(Agent.id, ondelete="CASCADE"), index=True
    )
    episode = sa.Column("episode", sa.Integer, default=1)
    simtimes = sa.Column(
        "simtimes",
        sa.JSON().with_variant(
            sqlalchemy.dialects.postgresql.JSONB(), "postgresql"
        ),
        nullable=False,
        default=list(),
    )
    sensor_readings = sa.Column(
        "sensor_readings",
        sa.JSON().with_variant(
            sqlalchemy.dialects.postgresql.JSONB(), "postgresql"
        ),
        nullable=True,
    )
    actuator_setpoints = sa.Column(
        "actuator_setpoints",
        sa.JSON().with_variant(
            sqlalchemy.dialects.postgresql.JSONB(), "postgresql"
        ),
        nullable=True,
    )
    rewards = sa.Column(
        "rewards",
        sa.JSON().with_variant(
            sqlalchemy.dialects.postgresql.JSONB(), "postgresql"
        ),
        nullable=True,
    )
    objective = sa.Column("objective", sa.Float, default=0.0)
    done = sa.Column("done", sa.Boolean, default=False)
    statistics = sa.Column(
        "statistics",
        sa.JSON().with_variant(
            sqlalchemy.dialects.postgresql.JSONB(), "postgresql"
        ),
        nullable=True,
    )
    rollout_worker_uid = sa.Column(
        "rollout_worker_uid", sa.String(255), default=None
    )
    agent = relationship("Agent", back_populates="muscle_actions")

    def __str__(self):
        return (
            f"<MuscleAction(id={self.id}, "
            f"agent_id={self.agent_id}, "
            f"walltime={self.walltime}, "
            f"simtime_ticks={self.simtime_ticks}, "
            f"simtime_timestamp={self.simtime_timestamp}, "
            f"sensor_readings={self.sensor_readings}, "
            f"actuator_setpoints={self.actuator_setpoints}, "
            f"rewards={self.rewards}>"
        )


Model = Base
