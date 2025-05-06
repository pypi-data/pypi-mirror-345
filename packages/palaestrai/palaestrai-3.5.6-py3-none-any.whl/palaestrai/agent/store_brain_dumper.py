from __future__ import annotations

from io import BytesIO
from typing import TYPE_CHECKING, BinaryIO, Optional

import sqlalchemy as sa
import sqlalchemy.exc

import palaestrai.store.database_model as dbm
from palaestrai.store import Session
from .brain_dumper import BrainDumper, NoBrainFoundError

if TYPE_CHECKING:
    from .brain_dumper import BrainLocation


class StoreBrainDumper(BrainDumper):
    """Dumps the state of a ::`Brain` to the store."""

    def __init__(
        self, dump_to: BrainLocation, load_from: Optional[BrainLocation] = None
    ):
        super().__init__(dump_to, load_from)
        self._db_session = None

    @property
    def _dbh(self):
        if not self._db_session:
            self._db_session = Session()
        return self._db_session

    def save(self, brain_state: BinaryIO, tag: Optional[str] = None):
        query = (
            sa.select(dbm.Agent)
            .join(dbm.ExperimentRunPhase)
            .join(dbm.ExperimentRunInstance)
            .join(dbm.ExperimentRun)
            .where(
                dbm.Agent.name == self._brain_destination.agent_name,
                dbm.ExperimentRun.uid
                == self._brain_destination.experiment_run_uid,
                dbm.ExperimentRunPhase.number
                == self._brain_destination.experiment_run_phase,
            )
            .order_by(dbm.ExperimentRunInstance.id.desc())
        )
        result = self._dbh.execute(query).first()
        if not result:
            raise NoBrainFoundError(self._brain_destination)
        agent_record: dbm.Agent = result[dbm.Agent]
        try:
            agent_record.brain_states.append(
                dbm.BrainState(tag=tag, state=brain_state.read())
            )
            self._dbh.commit()
        except sqlalchemy.exc.OperationalError:
            self._dbh.rollback()
            raise

    def _load(
        self, source_locator: BrainLocation, tag: Optional[str] = None
    ) -> BinaryIO:
        query = (
            sa.select(dbm.BrainState)
            .join(dbm.Agent)
            .join(dbm.ExperimentRunPhase)
            .join(dbm.ExperimentRunInstance)
            .join(dbm.ExperimentRun)
            .where(
                dbm.Agent.name == source_locator.agent_name,
                dbm.ExperimentRun.uid == source_locator.experiment_run_uid,
                dbm.ExperimentRunPhase.number
                == source_locator.experiment_run_phase,
                dbm.BrainState.tag == tag,
            )
            .order_by(dbm.BrainState.id.desc())
        )
        result = self._dbh.execute(query).first()
        if not result:
            raise NoBrainFoundError(source_locator)
        brain_state_record: dbm.BrainState = result[dbm.BrainState]
        bio = BytesIO()
        bio.write(brain_state_record.state)
        return bio
