from typing import Any, Iterable, List
import cloudpickle as pickle

from armonik.client import ArmoniKEvents
from armonik.common import Result, ResultStatus, EventTypes, Event, NewResultEvent, ResultStatusUpdateEvent
from grpc import RpcError
from typing import Collection, Optional, Set, cast, Union, Tuple

# TODO: Generics for better typing ... ResultHandle[str] for example..
class ResultHandle:
    """A handle to a future result from an ArmoniK task."""

    def __init__(self, result_id: str, session_id: str, pymonik_instance):
        self.result_id = result_id
        self.session_id = session_id
        self._pymonik = pymonik_instance

    def wait(self):
        """Wait for the result to be available."""
        try:
            self._pymonik._events_client.wait_for_result_availability(
                self.result_id, self.session_id
            )
            return self
        except Exception as e:
            print(f"Error waiting for result {self.result_id}: {e}")
            raise

    def get(self):
        """Get the result value."""
        result_data = self._pymonik._results_client.download_result_data(
            self.result_id, self.session_id
        )
        return pickle.loads(result_data)

    def __repr__(self):
        # TODO: more info
        return f"<ResultHandle(id={self.result_id}, session={self.session_id})>"



class MultiResultHandle:
    """A handle to multiple future results from ArmoniK tasks."""

    def __init__(self, result_handles: List[ResultHandle]):
        self.result_handles = result_handles
        if result_handles:
            self._pymonik = result_handles[0]._pymonik
            self.session_id = result_handles[0].session_id
        else:
            self._pymonik = None
            self.session_id = None

    def wait(self):
        """Wait for all results to be available."""
        if not self.result_handles:
            return self

        result_ids = [handle.result_id for handle in self.result_handles]
        try:
            self._pymonik._events_client.wait_for_result_availability(
                result_ids, self.session_id
            )
            return self
        except Exception as e:
            print(f"Error waiting for results: {e}")
            raise
    
    def get(self):
        """Get all result values."""
        # TODO: maybe should cache the get
        return [handle.get() for handle in self.result_handles]


    def __iter__(self):
        # TODO: implement _results_as_completed for retrieving results as they're completed
        # raise NotImplementedError("MultiResultHandle does not support iteration yet.")
        # nvm maybe this is better, it'd be weird to fetch things when you iterate, implicit behavior bad..
        return iter(self.result_handles)
    
    def __getitem__(self, index):
        if isinstance(index, slice):
            return MultiResultHandle(self.result_handles[index])
        elif isinstance(index, int):
            return self.result_handles[index]
        else:
            raise TypeError("Index must be an integer or a slice.")
        

    def __len__(self):
        return len(self.result_handles)

    def __repr__(self):
        return f"<MultiResultHandle(results={self.result_handles})>"
