from __future__ import annotations

import inspect
import logging
import os
import queue
import threading
import uuid
from datetime import datetime
from typing import Dict, Tuple, Union

import numpy as np
import time
import zlib
from elasticsearch import Elasticsearch
from influxdb_client import InfluxDBClient, Point, WriteOptions, WriteApi

import palaestrai.core.MDP as MDP
import palaestrai.core.protocol as proto
from palaestrai.core import RuntimeConfig
from palaestrai.core.serialisation import deserialize
from . import LOG
from . import database_model as dbm


class _Nop:
    """Silencer Dummy that is returned when the store is disabled.

    Guaranteed to do nothing.
    """

    def __init__(*args, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        return self

    def __getattr__(self, *args, **kwargs):
        return self


class TimeSeriesStoreReceiver(threading.Thread):
    """The message receiver of the palaestrAI store.

    The store hooks into the global communication, reading every message that
    is being exchanged between :class:`Executor`, :class:`RunGovernor`,
    :class:`AgentConductor`, :class:`Environment`, :class:`Brain`, and
    :class:`Muscle` instances. From these messages, it reads all relevant
    status information in order to relay them to the store database for later
    analysis of experiments.
    """

    def __init__(self, q, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._queue = q
        self._running = True
        self._uid = uuid.uuid4()
        self._log_store_fh = None
        self._i_client = None
        self._e_client = None
        self.org = None
        self._message_dispatch = {
            v: None
            for k, v in proto.__dict__.items()
            if (
                inspect.isclass(v)
                and (k.endswith("Request") or k.endswith("Response"))
            )
        }
        self._message_dispatch.update(
            {
                proto.ExperimentRunStartRequest: None,
                proto.SimulationStartRequest: None,  # self._write_simulation_data,
                proto.EnvironmentSetupResponse: None,
                proto.EnvironmentStartResponse: None,
                proto.EnvironmentUpdateResponse: self._write_env_update,
                proto.AgentSetupRequest: None,
                proto.AgentSetupResponse: None,
                proto.AgentUpdateRequest: self._write_agent_inputs,
                proto.AgentUpdateResponse: self._write_agent_actions,
                proto.SimulationControllerTerminationResponse: self._invalidate_cache,
            }
        )
        LOG.debug("New store Receiver instance %s ready", self._uid)
        try:
            self._time_series_store_uri = RuntimeConfig().time_series_store_uri
            self._store_uri = RuntimeConfig().store_uri
            if not self._store_uri:
                raise KeyError
        except KeyError:
            LOG.error(
                "StoreReceiver(id=%0xd, uid=%s) "
                "has no time_series_store_uri configured, I'm going to disable myself. :-("
                " If you want to employ me, set the 'time_series_store_uri' runtime "
                "configuration parameter.",
                id(self),
                self._uid,
            )
            self.disable()

        # Cache to avoid lookup queries:
        self._last_known_muscle_actions = {}
        self._environment_ticks: Dict[Tuple, int] = {}
        self._known_agents: Dict[Tuple, dbm.Agent] = {}
        self._known_environments: Dict[Tuple, dbm.Environment] = {}

    def disable(self):
        """Disables the store completely."""
        for k in self._message_dispatch.keys():  # Disable all handlers.
            self._message_dispatch[k] = None
        if self._i_client:
            # Explicitly close session here or we will see "session used in
            # wrong thread" errors, because the garbage collector runs in a
            # different thread.
            self._write_api.close()
            self._i_client.close()
            self._e_client.close()
        self._i_client = None
        self._e_client = None
        if self._log_store_fh:
            self._log_store_fh.flush()
            self._log_store_fh.close()
            self._log_store_fh = None

    @property
    def _influx_client(self) -> WriteApi:
        if self._i_client is None:
            try:
                (
                    db_type,
                    time_series_store_uri,
                ) = self._time_series_store_uri.split("+")
                self.org, token = time_series_store_uri.split("@")[0].split(
                    ":"
                )
                connections = time_series_store_uri.split("@")[1]
                try:
                    self._i_client = InfluxDBClient(
                        url=connections, token=token, org=self.org
                    )
                    self._write_api = self._i_client.write_api(
                        write_options=WriteOptions(
                            batch_size=500,
                            flush_interval=10_000,
                            retry_interval=5_000,
                            max_retries=5,
                            max_retry_delay=30_000,
                            exponential_base=2,
                        )
                    )
                    LOG.debug(
                        "StoreReceiver(id=%0xd, uid=%s) connected to: %s",
                        id(self),
                        self.uid,
                        RuntimeConfig().time_series_store_uri,
                    )
                except Exception as e:
                    LOG.error(
                        "Store could not connect: %s. We can continue, "
                        "but there won't be any data stored. Sorry.",
                        e,
                    )
                    self.disable()
            except ValueError:
                LOG.error(
                    "Invalid time_series_store_uri: %s"
                    % self._time_series_store_uri
                )
                self.disable()
        return self._write_api

    @property
    def _elastic_client(self) -> Union[Elasticsearch, _Nop]:
        store_uri = RuntimeConfig().store_uri.replace("elasticsearch+", "")
        if self._e_client is None:
            try:
                self._e_client = Elasticsearch(
                    hosts=store_uri, verify_certs=False
                )
                LOG.debug(
                    "StoreReceiver(id=%0xd, uid=%s) connected to: %s",
                    id(self),
                    self.uid,
                    RuntimeConfig().store_uri,
                )
            except Exception as e:
                LOG.error(
                    "Store could not connect to Elasticsearch: %s. "
                    "We can continue, but there won't be any data stored. "
                    "Sorry.",
                    e,
                )
                self.disable()
                self._e_client = _Nop()
        return self._e_client

    @property
    def _log_store(self):
        if not self._log_store_fh:
            log_store_dir = os.path.join(os.getcwd(), "store.log")
            os.makedirs(log_store_dir, exist_ok=True)
            log_store_fp = os.path.join(
                log_store_dir, "%s-%s.log" % (int(time.time()), self._uid)
            )
            self._log_store_fh = open(log_store_fp, "w")
            LOG.debug(
                "StoreReceiver(id=%0xd, uid=%s) writing message log to: %s",
                id(self),
                self._uid,
                log_store_fp,
            )
        return self._log_store_fh

    @property
    def uid(self):
        return self._uid

    def run(self):
        """Run the store."""
        LOG.debug(
            "Starting StoreReceiver(id=0x%x, uid=%s)", id(self), self._uid
        )
        while self._running or not self._queue.empty():
            try:
                msg = self._queue.get(timeout=1)
            except queue.Empty:
                time.sleep(1)
                continue
            msg_type, msg_uid, msg_obj = TimeSeriesStoreReceiver._read(msg)
            LOG.debug(
                "%s received message: type=%s, uid=%s, payload=%s; queue "
                "size: %s",
                self,
                msg_type,
                msg_uid,
                msg_obj,
                self._queue.qsize(),
            )
            if msg_type in ("ignore", "error"):
                self._queue.task_done()
                continue
            if isinstance(msg_obj, list):
                LOG.info(
                    "StoreReceiver(id=0x%x, uid=%s) received a list of "
                    "%d messages. Handling all these messages separately.",
                    id(self),
                    self._uid,
                    len(msg_obj),
                )
                for msg in msg_obj:
                    self.write(msg)
            else:
                self.write(msg_obj)
            self._queue.task_done()
        self.disable()
        LOG.info("%s has shut down.", self)

    def shutdown(self):
        LOG.info(
            "%s prepares to shut down: waiting to process %s message in the "
            "queue.",
            self,
            self._queue.qsize(),
        )
        self._running = False

    def write(self, message):
        if LOG.level == logging.DEBUG:
            self._log_store.write(
                "%s StoreReceiver(id=0x%x, uid=%s)[%d] %s %s"
                % (
                    time.time(),
                    id(self),
                    self._uid,
                    os.getpid(),
                    message,
                    (
                        message.__dict__
                        if hasattr(message, "__dict__")
                        else str(message)
                    ),
                )
            )
            self._log_store.flush()
        if message.__class__ not in self._message_dispatch:
            TimeSeriesStoreReceiver._handle_unknown_message(message)
            return
        if self._message_dispatch[message.__class__] is not None:
            try:
                LOG.debug(
                    "StoreReceiver(id=0x%x, uid=%s) dispatching message %s; "
                    "%d messages waiting",
                    id(self),
                    self.uid,
                    message,
                    self._queue.qsize(),
                )
                self._message_dispatch[message.__class__](message)
            except Exception as e:
                LOG.error(
                    "StoreReceiver(id=0x%x, uid=%s) "
                    "notes that the developers are too stupid to get the "
                    "schema right: %s",
                    id(self),
                    self.uid,
                    e,
                )
                self.disable()
                raise

    @staticmethod
    def _handle_unknown_message(message):
        LOG.warning(
            "Store received message %s, but cannot handle it - ignoring",
            message,
        )
        # create a json object with the experiment_run_id, experiment_run_instance_id from the message and
        # send the json object to the elasticsearch server.

    def _write_simulation_data(self, message: proto.SimulationStartRequest):
        """Write simulation data to the log store.

        :param message: The simulation start request message.
        """
        data = {
            "experiment_run_id": message.experiment_run_id,
            "experiment_run_instance_id": message.experiment_run_instance_id,
            "time": datetime.utcnow(),
            "type": "simulation_start",
        }
        resp = self._elastic_client.index(index="palaestrai", document=data)
        LOG.debug("Elasticsearch response: %s", resp)

    def _write_env_update(self, message: proto.EnvironmentUpdateResponse):
        """Write environment update data to the log store.

        :param message: The environment update response message.
        """
        rewards = {}
        for reward in message.rewards:
            rewards[reward.uid] = float(reward.value)
        data = {
            "measurement": message.experiment_run_instance_id,
            "tags": {
                "phase": message.experiment_run_phase,
                "type": "reward",
            },
            "time": datetime.utcnow(),
            # message.walltime,
            "fields": rewards,
        }
        data = Point.from_dict(data)
        self._influx_client.write("palaestrai", self.org, [data])

    def _write_world_state(self, message: proto.EnvironmentUpdateResponse):
        """Write the world state to the elasticsearch server.

        :param message: proto.EnvironmentUpdateResponse
        """
        world_state = None
        for x in message.sensors:
            print(x.uid)
            if "grid_json" in x.uid:
                world_state = x
                data = {
                    "experiment_run_id": message.experiment_run_id,
                    "experiment_run_instance_id": message.experiment_run_instance_id,
                    "time": datetime.utcnow(),
                    "type": "Worldstate",
                    "world_state": world_state.value,
                }
                resp = self._elastic_client.index(
                    index="palaestrai", document=data
                )
                LOG.debug("Elasticsearch response: %s", resp)

    def _write_agent_inputs(self, message: proto.AgentUpdateRequest):
        sensors: dict[
            Union[str, int],
            Union[int, float, str, list[Union[int, float, str]]],
        ] = {}
        for sensor in message.sensors:
            if isinstance(sensor.value, list):
                sensors = self._process_sensorvalue_list(sensor, sensors)
            elif isinstance(sensor.value, (int, float, str)):
                sensors[sensor.uid] = sensor.value
            elif isinstance(sensor.value, (bool, np.bool_)):
                sensors[sensor.uid] = int(sensor.value)
            else:
                LOG.error(
                    "InfluxDB Store received message %s, with sensor %s with a"
                    " value of type %s but cannot handle it - ignoring",
                    message,
                    sensor.uid,
                    type(sensor.value),
                )
        data = {
            "measurement": message.experiment_run_instance_id,
            "tags": {
                "phase": message.experiment_run_phase,
                "agent": message.receiver_rollout_worker_id,
                "type": "sensor",
            },
            "time": datetime.utcnow(),
            "fields": sensors,
        }
        data = Point.from_dict(data)
        self._influx_client.write(
            bucket="palaestrai", org=self.org, record=data
        )

    def _write_agent_actions(self, message: proto.AgentUpdateResponse):
        actuators: dict[
            Union[str, int],
            Union[int, float, str, list[Union[int, float, str]]],
        ] = {}
        for actuator in message.actuators:
            if isinstance(actuator.value, list):
                actuators = self._process_actuatorvalue_list(
                    actuator, actuators
                )
            elif isinstance(actuator.value, (int, float, str)):
                actuators[actuator.uid] = actuator.value
            else:
                LOG.error(
                    "InfluxDB Store received message %s, with actuator %s with a"
                    " value of type %s but cannot handle it - ignoring",
                    message,
                    actuator.uid,
                    type(actuator.value),
                )
        data = {
            "measurement": message.experiment_run_instance_id,
            "tags": {
                "phase": message.experiment_run_phase,
                "agent": message.sender_rollout_worker_id,
                "type": "actuator",
            },
            "time": datetime.utcnow(),
            # message.walltime,
            "fields": actuators,
        }
        data = Point.from_dict(data)
        self._influx_client.write("palaestrai", self.org, [data])

    def _invalidate_cache(
        self, message: proto.SimulationControllerTerminationResponse
    ):
        """Cleans the local cache after a experiment run phase has ended."""
        if message.restart:
            return  # Don't clean on restarts!
        self._environment_ticks = {
            k: v
            for k, v in self._environment_ticks.items()
            if (
                k[0] != message.experiment_run_instance_id
                and k[1] != message.experiment_run_phase
            )
        }
        self._known_environments = {
            k: v
            for k, v in self._known_environments.items()
            if (
                k[0] != message.experiment_run_instance_id
                and k[1] != message.experiment_run_phase
            )
        }
        self._known_agents = {
            k: v
            for k, v in self._known_agents.items()
            if (
                k[0] != message.experiment_run_instance_id
                and k[1] != message.experiment_run_phase
            )
        }

    @staticmethod
    def _read(msg):
        """Unpacks a message, filters ignores"""

        _ = msg.pop(0)
        empty = msg.pop(0)
        assert empty == b""
        _ = msg.pop(0)
        # if len(msg) >= 1:
        #     serv_comm = msg.pop(0)
        if len(msg) > 3:
            sender = msg.pop(0)
            empty = msg.pop(0)
            header = msg.pop(0)
            LOG.debug(
                "Ignored message parts: %s, %s, %s", sender, empty, header
            )

        if msg[0] == MDP.W_HEARTBEAT:
            # We ignore heartbeats
            return "ignore", None, None
        if msg[0] == MDP.W_READY:
            return "ignore", None, None

        if len(msg) == 1:
            # it is a response
            uid = ""
            msg_obj = TimeSeriesStoreReceiver._deserialize(msg.pop(0))
            msg_type = "response"

        elif len(msg) == 2:
            uid = TimeSeriesStoreReceiver._deserialize(msg.pop(0))
            msg_obj = TimeSeriesStoreReceiver._deserialize(msg.pop(0))
            msg_type = "request"
        else:
            uid = ""
            msg_obj = "None"
            msg_type = "error"

        return msg_type, uid, msg_obj

    @staticmethod
    def _deserialize(msg):
        try:
            msg = deserialize([msg])
            return msg
        except zlib.error:
            LOG.debug(
                "StoreReceiver received a message '%s', "
                "which could not be deserialized from zlib.",
                msg,
            )
        try:
            msg = str(msg.decode())
            return msg
        except AttributeError:
            LOG.debug(
                "StoreReceiver received a message '%s', "
                "which could not be str-decoded. ",
                msg,
            )
        return msg

    def __str__(self):
        return "TimeSeriesStoreReceiver(id=0x%x, uid=%s, uri=%s)" % (
            id(self),
            self.uid,
            self._store_uri,
        )

    def _process_sensorvalue_list(self, sensor, sensors):
        if sensor.value_ids is not None:
            for id, value in zip(sensor.value_ids, sensor.value):
                sensors[sensor.uid + "_" + id] = value
        else:
            for idx, value in enumerate(sensor.value):
                sensors[sensor.uid + str(idx)] = value
        return sensors

    def _process_actuatorvalue_list(self, actuator, actuators):
        if actuator.value_ids is not None:
            for id, value in zip(actuator.value_ids, actuator.value):
                actuators[actuator.uid + "_" + id] = value
        else:
            for idx, value in enumerate(actuator.value):
                actuators[actuator.uid + str(idx)] = value
        return actuators
