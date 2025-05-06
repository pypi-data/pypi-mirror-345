from __future__ import annotations

import os
import uuid
import enum
import signal
import weakref
import asyncio
import logging
import inspect
import multiprocessing
import aiomultiprocess
from collections import defaultdict
from collections.abc import Iterable
from typing import (
    Dict,
    Set,
    Tuple,
    Any,
    Union,
    Callable,
    Optional,
    DefaultDict,
)

from palaestrai.core.protocol import (
    DelayedResultResponse,
    DelayedResultRequest,
    ErrorIndicator,
)
from palaestrai.core import RuntimeConfig, MajorDomoClient, MajorDomoWorker

LOG = logging.getLogger(__name__)


class Flags(enum.Enum):
    """Flags to force custom behavior of the EventStateMachine

    Usually, the EventStateMachine tries to get the behavior right.
    But sometimes, there are edge cases in which the wanted behavior derives
    from the defaults of the ESM.
    For this, these flags exist. They can be returned additionally from event
    handlers, e.g., a method decorated with ``@spawns`` would then not only
    return a process, but a tuple of process and flag.

    Attributes
    ----------
    KEEPALIVE :
        Usually, the ESM stops the MDP transceiving loop when a response
        object ends with ``ShutdownResponse``. If this behavior is not desired,
        supply this keepalive flag.
    """

    KEEPALIVE = enum.auto()


class EventStateMachine:
    """An event-triggered state machine

    The EventStateMachine (ESM) can be used to transparently handle events
    within palaestrAI. An ESM wraps another class and callbacks can be defined
    with method decorators for events. Events are:

    * A message received,
    * a signal received (SIGCHLD, SIGTERM, etc.)
    * setup
    * enter (the initial event)
    * teardown

    The initial event *enter* is issued immediately after the main event/state
    loop commences in order to provide an entrypoint for operation.
    The *enter* event can be used to, e.g., send out the first request.
    For example::

        @ESM.monitor()
        class Foo:

            @ESM.enter
            async def _enter(self):
                _ = await self._request_initialization()

            @ESM.requests
            async def _request_initialization(self):
                # ...
                return InitRequest(
                    # ...
                )

    It is not strictly necessary to provide an *enter* event.
    If the monitored class is exclusively an MDP worker, then there is no need
    for the *enter* event, because the worker reacts on the first request it
    receives and not on its own volition.

    In order to make a class use the ESM, you must decorate it with
    ::`~.monitor`. The ``monitor`` decorator can also inject all necessary
    code to handle ZMQ MDP workers.

    If the monitored class does not have a ``run`` method, the ESM will also
    inject it. The ``run`` method then serves as an event/state loop that
    continues until it is stopped. At the start of the ``run`` method, the
    target objects ``setup`` method is called if it exists. Likewise,
    a ``teardown`` method will be called immediately after the loop ends.

    The ESM also adds a ``stop`` method to the target object. It serves to
    terminate the event/state loop.

    In order to react to a specific event, users of the ESM can decorate their
    methods with ``on(event)``. The ::`~.on` decorator takes as parameter
    the class of what is handled. E.g., the class of a particular message, or
    ``signal.SIGCHLD`` to react to a process that has ended. For example::

        from palaestrai.core import EventStateMachine as ESM
        import signal

        @ESM.monitor()
        class Foo:

            @ESM.on(SomeRequest)
            async def handle_some_request(self, request):
                 # ...
                 pass

            @ESM.on(signal.SIGCHLD)
            async def handle_process_termination(self, process):
                # ...
                pass

    Spawning processes is also handled through a decorator: ``spawns``. If a
    method decorated with ``spawns`` returns a ::`Process` object, this
    process will automatically be monitored. E.g.,::

        # ...
        @ESM.spawns
        def start_some_fancy_process(self):
            p = multiprocessing.Process(target=somefunc)
            p.start()
            return p

    The ESM also handles the sending of requests. ESM-monitored classes do not
    need to instantiate and monitor MDP client objects themselves. Instead,
    they simply need methods to be decorated with ``requests``. The so
    decorated method must return a message object that has the ``receiver``
    property, so that ::`~.requests` can handle sending. E.g.,::

        # ...
        @ESM.requests
        def get_something_from_a_worker(self):
            req = SomeRequest()
            req.receiver = "Foo"
            return req

        @ESM.on(SomeResponse)    # also handle the response!
        def handle_response_from_worker(self, response):
            # ...
            pass

    The ESM also supports classes that act as workers. For this, the ESM's
    ``monitor`` decorator needs the flag ``is_mdp_worker=True``. Then, the
    ESM injects the property ``mdp_service``. Setting this property connects
    the MDP worker, and ``ESM.on`` can be used to handle requests from clients.
    For example::

        @ESM.monitor(is_mdp_worker=True)
        class Foo:
            async def setup(self):
                self.mdp_service = "Foo"

            @ESM.on(SomeRequest)
            def handle_request_from_client(self, req):
                do_something_with(request)
                rsp = SomeResponse()
                rsp.receiver = req.sender
                return rsp
    """

    _decorated_methods: Dict[Callable, Any] = dict()
    _monitored_objects: Dict[Tuple[int, weakref.ref], EventStateMachine] = (
        dict()
    )

    @staticmethod
    def _cleanup_monitored_objects(ref: weakref.ref):
        pid = os.getpid()
        LOG.debug("EventStateMachine cleaning %s", (pid, ref))
        del EventStateMachine._monitored_objects[(pid, ref)]

    @staticmethod
    def esm_for(monitored: Any) -> EventStateMachine:
        """Returns the ESM instance for any monitored object.

        This method retrieves the ESM instance responsible for a monitored
        object. It does not check whether the object has been decoreted with
        ::`~.monitored`, though.

        Parameters
        ----------

        monitored : Any
            A monitored object

        Returns
        -------
        EventStateMachine
            The ESM instance responsible for the monitored object. A new
            instance will be created if it does not already exist.
        """
        pid = os.getpid()
        ref = weakref.ref(
            monitored, EventStateMachine._cleanup_monitored_objects
        )
        try:
            esm = EventStateMachine._monitored_objects[(pid, ref)]
        except KeyError:
            esm = EventStateMachine(monitored)
            EventStateMachine._monitored_objects[(pid, ref)] = esm
        return esm

    @staticmethod
    def _make_mdp_service_property():
        @property
        def mdp_service(self) -> str:
            return self.__esm__._mdp_worker_service

        @mdp_service.setter
        def mdp_service(self, value: str):
            self.__esm__._mdp_worker_service = value
            self.__esm__._connect_worker_and_listen()

        return mdp_service

    @staticmethod
    def monitor(is_mdp_worker=False):
        """Decorates a class to monitor instances of it with the ESM.

        This decorator is the minimal required decoration of any class that
        makes use of the ESM. It injects the ESM instance into new objects of
        that class, and also adds relevant methods. The usage is::

            from palaestrai.core import EventStateMachine as ESM

            @ESM.monitor()
            class Foo:
                pass

            @ESM.monitor(is_mdp_worker=True)
            class Bar:
                pass

        The ``@monitor`` decorator injects methods to the target class, namely:

        * ``run()``: The default run method that kicks off the event/state
           loop of the target class.
        * ``stop()``: Stops the event/state loop of the class and can be
          called from any handler.

        If ``is_mdp_worker=True`` was given, then the ESM also takes care of
        handling MDP requests for the target class. Then, another property
        is injected: ``mdp_service``. This is then the service name the worker
        will listen on. Setting the property instanciates a ::`MajorDomoWorker`
        and connects it to the broker.

        Parameters
        ----------
        is_mdp_worker : bool
            If ``True``, the monitored class will act as MDP worker. The ESM
            will inject a property ``mdp_service``. Setting the property will
            create a ::`MajorDomoWorker` instance and connect it to the broker.
        """

        def _wraps(clazz):
            attrs = dir(clazz)
            setattr(
                clazz,
                "__esm__",
                property(lambda self: EventStateMachine.esm_for(self)),
            )
            if is_mdp_worker:
                setattr(
                    clazz,
                    "mdp_service",
                    EventStateMachine._make_mdp_service_property(),
                )
            if "run" not in attrs:
                setattr(clazz, "run", EventStateMachine.run)
                setattr(clazz, "stop", EventStateMachine.stop)
            return clazz

        return _wraps

    @staticmethod
    def on(sig_or_msg_or_str):
        """Register an event/state transition handler.

        ``on`` is a decorator used to register handlers for any kind of event.
        Typical usage is::

            from palaestrai.core import EventStateMachine as ESM

            @ESM.monitor()
            class Foo:
                @ESM.on(SomeRequest)
                def bar(self, req):
                    pass  # ...

        Typical arguments to ``on`` are:

        * A class: When the ESM receives an MDP request or response, it will
          check whether the message's class has a handler registered. The
          registered method is then called and the message passed.
        * An exception class: The handler is triggered when the exception is
          thrown.
        * A signal: Handles signals such as ``SIGCHLD`` (when a child process
          terminates), ``SIGINT``, or ``SIGTERM``.
        """
        try:
            sig_or_msg_or_str = sig_or_msg_or_str.__name__
        except AttributeError:
            pass

        def _register_func(func):
            EventStateMachine._decorated_methods[func] = sig_or_msg_or_str
            return func

        return _register_func

    @staticmethod
    def enter(func):
        """Decorates a method to be the very first state

        Each state machine needs an initial state; the ESM is no exception. A
        method decorated with ``enter`` is called immediately at the beginning
        of the event/state loop.

        Usage example::

            @ESM.monitor()
            class Foo:
                @ESM.enter
                def _enter(self):
                    pass   # Do something, like launching a process.

        ``enter`` is not used for setup purposes: If the target class has a
        ``setup`` method, this one is called immediately *before* the
        event/state loop commences. Thus, the enter method is optional. E.g.,
        a class that simply acts as MDP worker does not need it; it is
        sufficient to set the MDP service name in the ``setup`` method.
        """
        EventStateMachine._decorated_methods[func] = "ENTER"
        return func

    def _handle_enter(self):
        pass  # Intentional a noop to suppress a warning for the ENTER event.

    def _handle_terminated_child(
        self, process: Union[aiomultiprocess.Process, multiprocessing.Process]
    ):
        LOG.debug(
            "%s saw termination of process: %s. No other handler is "
            "installed.",
            self,
            process,
        )
        if process.exitcode != 0:
            LOG.error(
                "Process %s died with exit code %d",
                process,
                process.exitcode,
            )

    def _handle_sigint(self):
        LOG.debug("%s handles SIGINT for %s", self, self._monitored)
        self.stop(self._monitored)

    def _handle_sigterm(self):
        LOG.debug("%s handles SIGTERM for %s", self, self._monitored)
        self.stop(self._monitored)

    @staticmethod
    def spawns(func):
        """Signify that a method creates (spawns) new sub-processes

        Child processes are also monitored by the ESM. In order to find out
        which processes to monitor, the ESM checks the return values of all
        methods that are decorated with ``@spawns``. For example::

            from palaestrai.core import EventStateMachine as ESM

            @ESM.monitor()
            class Foo:
                @ESM.spawns
                async def some_method(self):
                    p = multiprocessing.Process(target=foofunc)
                    p.start()
                    return p

                @ESM.enter
                def _enter(self):
                    _= await self.spawns()

        **Note:** Processes that are returned from a spawning function are not
        automatically started, just monitored.
        """

        def _wraps(self, *args, **kwargs):
            ret = func(self, *args, **kwargs)
            for process in [
                x
                for x in (ret if isinstance(ret, Iterable) else [ret])
                if isinstance(x, multiprocessing.Process)
                or isinstance(x, aiomultiprocess.Process)
            ]:
                self.__esm__.monitor_process(process)
            return ret

        async def _awraps(self, *args, **kwargs):
            ret = await func(self, *args, **kwargs)
            for process in [
                x
                for x in (ret if isinstance(ret, Iterable) else [ret])
                if isinstance(x, multiprocessing.Process)
                or isinstance(x, aiomultiprocess.Process)
            ]:
                self.__esm__.monitor_process(process)
            return ret

        return _awraps if asyncio.iscoroutinefunction(func) else _wraps

    @staticmethod
    def requests(func):
        """Signify that the returned request message object awaits an  answer.

        When the object monitored by the ESM sends out requests, it will
        also want to react to responses. In order to manage tracking of
        requests and responses, the ESM uses the ``requests`` method decorator.
        For example,::

            from palaestrai.core import EventStateMachine as ESM

            @ESM.monitor()
            class Foo:
                @ESM.requests
                def send_some_request(self):
                    # ...
                    return SomeRequest(receiver="SomeWorker")

                @ESM.on(SomeResponse)
                def handle_some_response(self, response):
                    # ...
                    pass

        The message object's class needs to end with ``Request``. It can be
        passed along with other objects as well. So if the method returns
        a tuple or a list, the ESM will inspect each object to be a message
        object, and track that.
        """

        def _wraps(self, *args, **kwargs):
            ret = func(self, *args, **kwargs)
            for mdp_request in [
                x
                for x in (ret if isinstance(ret, Iterable) else [ret])
                if type(x).__name__.endswith("Request")
            ]:
                self.__esm__._tasks.add(
                    asyncio.create_task(self.__esm__.send_request(mdp_request))
                )
            return ret

        return _wraps

    @staticmethod
    async def run(monitored):
        """Main event/state loop of the ESM

        This ``run`` method is injected into monitored classes if they do not
        have one already. The structure of ``run`` is as follows:

        1. It resets the handlers for SIGCHLD, SIGINT, and SIGTERM to the OS'
           default.
        2. It calls ``monitored.setup()``, if it exists.
        3. It creates an ESM instance for the monitored object and adds signal
           handlers for SIGCHLD, SIGINT, and SIGTERM according to what the
           monitored class defines (via ``@ESM.on(signal.SIGINT)``, etc.)
        4. It transides to the first state, defined by ``@ESM.enter``. It then
           waits for state changes/events until ``monitored.stop()`` is called.
        5. Finally, once the main event/state loop concludes,
           ``monitored.teardown()`` is called (if present).
        """
        signal.signal(signal.SIGCHLD, signal.SIG_DFL)
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        signal.signal(signal.SIGTERM, signal.SIG_DFL)

        if "setup" in dir(monitored):
            LOG.debug("Running %s.setup()...", monitored)
            try:
                if asyncio.iscoroutinefunction(monitored.setup):
                    await monitored.setup()
                else:
                    monitored.setup()
            except Exception as e:
                LOG.exception("%s.setup() failed with %s", monitored, e)
                return

        esm = EventStateMachine.esm_for(monitored)
        asyncio.get_running_loop().add_signal_handler(
            signal.SIGINT,
            lambda loop: loop.create_task(esm._handle_event(signal.SIGINT)),
        )
        asyncio.get_running_loop().add_signal_handler(
            signal.SIGTERM,
            lambda loop: loop.create_task(esm._handle_event(signal.SIGTERM)),
        )
        esm._future = asyncio.get_running_loop().create_future()

        LOG.debug("%s commencing loop: Waiting for my own future…", esm)
        asyncio.create_task(esm._handle_event("ENTER"))
        await esm._future
        LOG.debug("%s: The future is now!", esm)

        if "teardown" in dir(monitored):
            try:
                if asyncio.iscoroutinefunction(monitored.teardown):
                    await monitored.teardown()
                else:
                    monitored.teardown()
            except Exception as e:
                LOG.exception("%s.teardown() failed with %s", monitored, e)
        await esm._cleanup()
        if esm._future.exception() is not None:
            raise esm._future.exception()

    @staticmethod
    def stop(monitored, error=None):
        """Stops the ESM.

        Stopping the ESM also means shutting down all running processes and
        cancelling all outstanding tasks (e.g., request monitors).

        Paramters
        ---------
        error : Exception
            If given, the ESM will raise this after cleaning up.
        """
        esm = EventStateMachine.esm_for(monitored)
        esm._stop(error)

    def __init__(self, monitored: Any):
        self._future: Optional[asyncio.Future] = None

        self._monitored = monitored
        self._monitored_processes: Dict[
            Union[aiomultiprocess.Process, multiprocessing.Process],
            asyncio.Task,
        ] = dict()
        self._tasks: Set[asyncio.Task] = {
            asyncio.create_task(self._watch_tasks(), name="Tasks Watcher")
        }
        self._pending_tasks: Dict[str, asyncio.Task] = {}  # If worker pending

        self._handlers = {
            signal.SIGCHLD: self._handle_terminated_child,
            signal.SIGINT: self._handle_sigint,
            signal.SIGTERM: self._handle_sigterm,
            "ENTER": self._handle_enter,
            DelayedResultRequest.__name__: self._try_get_delayed_result,
            DelayedResultResponse.__name__: self._retry_delayed_request,
            Any: None,
        }

        self._mdp_worker_service: Optional[str] = None
        self._mdp_worker: Optional[MajorDomoWorker] = None
        self._mdp_clients: DefaultDict[
            str, Tuple[MajorDomoClient, asyncio.Lock]
        ] = defaultdict(
            lambda: (
                MajorDomoClient(
                    f"tcp://127.0.0.1:{RuntimeConfig().executor_bus_port}"
                ),
                asyncio.Lock(),
            )
        )

        # Update handlers, match to methods of the _monitored object:

        injected_methods = [  # These are injected by us, ignore them here:
            "__esm__",
            "mdp_service",
            "run",
        ]
        directory = dir(self._monitored)
        all_attributes = [
            getattr(self._monitored, x, None)  # None instead of AttributeError
            for x in directory
            if not x in injected_methods
        ]
        self._handlers.update(
            {
                EventStateMachine._decorated_methods[x.__func__]: x
                for x in all_attributes
                if x is not None
                and inspect.ismethod(x)
                and x.__func__ in EventStateMachine._decorated_methods
            }
        )
        self._handlers.update(
            {
                EventStateMachine._decorated_methods[x]: x
                for x in all_attributes
                if inspect.isfunction(x)
                and x in EventStateMachine._decorated_methods
            }
        )

    async def _watch_tasks(self):
        while self._tasks:
            done, pending = await asyncio.wait(
                self._tasks, return_when=asyncio.FIRST_COMPLETED
            )
            exceptionals = [t for t in done if t.exception() is not None]
            for e in exceptionals:
                LOG.error(
                    "%s saw task %s raise exception: %s",
                    self,
                    e,
                    e.exception(),
                )
                await self._handle_event(
                    type(e.exception()).__name__, e.exception()
                )
            self._tasks = pending

    async def _handle_event(self, event: Any, *args, **kwargs) -> Any:
        try:
            handler: Any = self._handlers[event]
        except KeyError:
            handler = self._handlers[Any]
        if handler is None:  # Default handler
            LOG.warning("%s has no handler for %s", self._monitored, event)
            return
        try:
            if asyncio.iscoroutinefunction(handler):
                return await handler(*args, **kwargs)
            else:
                return handler(*args, **kwargs)
        except Exception as e:
            LOG.exception(
                "%s encountered exception from the handler for %s", self, event
            )
            # Perhaps there is a handler for the exception...?
            # Except, of course, we're already trying to handle the
            # exception...
            if (
                not isinstance(event, Exception)
                and type(e).__name__ in self._handlers
            ):
                await self._handle_event(type(e).__name__, e)
            else:
                assert self._future is not None
                self._future.set_exception(e)

    def monitor_process(
        self, process: Union[aiomultiprocess.Process, multiprocessing.Process]
    ):
        task = asyncio.create_task(
            self._watch_process(process),
            name=f"Process watcher for child {process.pid}",
        )
        self._monitored_processes[process] = task
        LOG.debug("%s now monitors process %s", self, process)

    async def _watch_process(
        self, process: Union[aiomultiprocess.Process, multiprocessing.Process]
    ):
        LOG.debug("%s starts to watch process: %s", self, process)
        if isinstance(process, aiomultiprocess.Process):
            await process.join()
        else:
            process.join()
        LOG.debug(
            "%s saw a process end: %s, calling handler...", self, process.name
        )
        await self._handle_event(signal.SIGCHLD, process)
        del self._monitored_processes[process]  # Cleanup.

    async def _wait_for_response(self, service: str, request: Any):
        mdp_client, mdp_client_lock = self._mdp_clients[service]
        try:
            await mdp_client_lock.acquire()
            resp = await mdp_client.send(service, request)
        except Exception as e:
            LOG.exception("Sending request failed: %s", e)
        finally:
            mdp_client_lock.release()
        await self._handle_event(type(resp).__name__, resp)

    async def send_request(self, request: Any):
        try:
            service = request.receiver
            self._tasks.add(
                asyncio.create_task(
                    self._wait_for_response(service, request),
                    name=f"Wait for response to {request} to {service}",
                )
            )
        except ValueError:
            LOG.error(
                "%s cannot determine target service for %s. Please "
                "extend %s to provide the 'receiver' property.",
                self,
                request,
                type(request),
            )

    async def _mdp_worker_transceive(self):
        reply = None
        flags = None
        while True:
            if isinstance(reply, tuple):
                reply, flags = reply
            else:
                flags = None
            if type(reply).__name__.endswith("ShutdownResponse") and (
                flags is None
                or (flags is not None and flags != Flags.KEEPALIVE)
            ):
                LOG.debug("%s giving final %s", self, reply)
            req = await self._mdp_worker.transceive(
                reply,
                skip_recv=(
                    type(reply).__name__.endswith("ShutdownResponse")
                    and (
                        flags is None
                        or (flags is not None and flags != Flags.KEEPALIVE)
                    )
                ),
            )
            if req is None:
                break
            if type(reply).__name__.endswith("ShutdownRequest"):
                LOG.debug("%s got %s", self, reply)
            worker_task = asyncio.create_task(
                self._handle_event(type(req).__name__, req)
            )
            done, pending = await asyncio.wait(
                [worker_task],
                timeout=max(1, RuntimeConfig().major_domo_client_timeout // 2),
            )
            if done:
                reply = worker_task.result()
                continue
            assert len(pending) == 1
            task_uuid = str(uuid.uuid4())
            t = pending.pop()
            self._pending_tasks[task_uuid] = t
            self._tasks.add(t)
            reply = DelayedResultResponse(
                sender=req.receiver, receiver=req.sender, task_uuid=task_uuid
            )

    def _connect_worker_and_listen(self):
        if self._mdp_worker_service is None:
            raise ValueError(f"{self}._mdp_worker_service string unset")
        if self._mdp_worker is not None:
            raise RuntimeError(f"{self} already has an MDP Worker")
        self._mdp_worker = MajorDomoWorker(
            f"tcp://127.0.0.1:{RuntimeConfig().executor_bus_port}",
            self._mdp_worker_service,
        )
        self._tasks.add(
            asyncio.create_task(
                self._mdp_worker_transceive(), name="Transceiver"
            )
        )

    def _try_get_delayed_result(self, req: DelayedResultRequest):
        try:
            task = self._pending_tasks[req.task_uuid]
        except KeyError as e:
            return ErrorIndicator(
                sender=req.receiver,
                receiver=req.sender,
                error_message=f"Task UUID {req.task_uuid} unknown.",
                exception=e,
            )
        if task.done():
            del self._pending_tasks[req.task_uuid]
            return task.result()
        return DelayedResultResponse(
            sender=req.receiver,
            receiver=req.sender,
            task_uuid=req.task_uuid,
        )

    async def _retry_delayed_request(self, rsp: DelayedResultResponse):
        LOG.debug(
            "%s was notified that a worker needs some more time: "
            "sleeping and retrying.",
            self,
        )
        await asyncio.sleep(1.0)
        await self.send_request(  # Creates a task to wait for the response
            DelayedResultRequest(
                sender=rsp.receiver,
                receiver=rsp.sender,
                task_uuid=rsp.task_uuid,
            )
        )

    def _stop(self, error: Optional[BaseException] = None):
        if self._future is None:
            return
        try:
            if error is not None:
                self._future.set_exception(error)
            else:
                self._future.set_result(True)
        except asyncio.exceptions.InvalidStateError:
            # Doubly-stop.
            pass

    async def _cleanup(self):
        LOG.debug(
            "%s cleaning up: tasks %s; processes %s",
            self,
            self._tasks,
            self._monitored_processes,
        )
        await self._stop_all_processes()

        # Now give all tasks a reasonable amount of time to finish.
        # All should terminate by themselves, except for the task watcher,
        # which terminates when there's nothing left in self._tasks.

        watcher = next(
            t for t in self._tasks if t.get_name() == "Tasks Watcher"
        )
        self._tasks -= {watcher}
        if not self._tasks:  # Oh, already done...
            return
        _, pending = await asyncio.wait(self._tasks, timeout=5)

        for task in pending:  # Now cancel what is left
            if task.get_name() != "Transceiver":
                # The transceiver might linger (e.g., during error state, or
                # when the RunGovernor shuts down), so don't print a warning
                # for the Transceiver task, just cancel it silently.
                LOG.warning("%s: Task %s did not end, terminating", self, task)
            task.cancel()
        if self._mdp_worker is not None:
            await self._mdp_worker.disconnect()
        LOG.debug("%s: done cleaning up.", self)

    async def _stop_all_processes(self):
        all_processes = list(self._monitored_processes.keys())  # Dict changes
        for process in all_processes:
            # First see whether the process exits all by itself:
            if process.is_alive():
                if asyncio.iscoroutinefunction(process.join):
                    try:
                        await process.join(3.0)
                    except asyncio.CancelledError:
                        pass  # This is okay
                    except asyncio.TimeoutError:
                        # The process seems unwilling to terminate, but no
                        # worries, we're not done yet...
                        pass
                else:
                    process.join(3.0)
            if not process.is_alive():
                continue  # Yay, it ended as we wished.

            # Then, send SIGTERM and wait for it to finish:
            LOG.warning(
                "Process %s did not exit by itself, sending SIGTERM.",
                process.name,
            )
            process.terminate()
            if asyncio.iscoroutinefunction(process.join):
                try:
                    await process.join(3.0)
                except asyncio.CancelledError:
                    pass
                except asyncio.TimeoutError:
                    pass  # Same as above, but now we kill
            else:
                process.join(3.0)
            if not process.is_alive():
                continue  # Okay, not as nice as it could be, but still...
        if all(
            not process.is_alive() for process in self._monitored_processes
        ):
            return  # Don't wait

        # Still someone here? Let's draw the big friggin' gun:
        for process in all_processes:
            if process.is_alive():
                LOG.error(
                    "Process %s is still there, killing it.", process.name
                )
                process.kill()
                if asyncio.iscoroutinefunction(process.join):
                    try:
                        await process.join()  # This has to terminate.
                    except asyncio.CancelledError:
                        pass
                    except asyncio.TimeoutError:
                        pass  # Yeah, well, we tried. Hand it to the reaper.
                else:
                    process.join()
        for task in self._monitored_processes.values():
            if not task.done():
                task.cancel()

    def __str__(self):
        return (
            f"EventStateMachine(pid={os.getpid()}, "
            f"monitored={self._monitored})"
        )

    def __del__(self):
        if not hasattr(self, "_tasks"):
            return
        for t in self._tasks:
            t.cancel()
