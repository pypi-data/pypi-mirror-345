from __future__ import annotations

from datetime import timedelta
import hashlib
from typing import Any, SupportsFloat
from gymnasium import Env, Wrapper
import jsonpickle
import numpy as np

from pytupli.schema import Benchmark, BenchmarkMetadata, BenchmarkQuery, RLTuple, Episode, FilterEQ
from pytupli.storage import TupliStorage


class TupliBenchmark(Wrapper):
    def __init__(
        self,
        env: Env,
        storage: TupliStorage,
        benchmark_id: str | None = None,
    ):
        super().__init__(env)
        self.storage = storage
        self.tuple_buffer = []  # list of RLTuples
        self._record_episodes = True  # whether to record tuples or not

        self.id = benchmark_id  # Benchmark ID once stored

    def activate_recording(self):
        """
        Activate recording of tuples.
        """
        self._record_episodes = True

    def deactivate_recording(self):
        """
        Deactivate recording of tuples.
        """
        self._record_episodes = False

    def _get_hash(self, obj: Any) -> str:
        # Compute a hash for the benchmark environment
        return hashlib.sha256(jsonpickle.encode(obj).encode('utf-8')).hexdigest()

    def serialize_env(self, env: Env) -> str:
        env, related_artifacts = self._serialize(env)
        setattr(env.unwrapped, 'related_artifacts', related_artifacts)
        # Compute a serialized version of the benchmark environment
        serialized_env = jsonpickle.encode(env, indent=4, warn=True)
        return serialized_env

    @classmethod
    def deserialize_env(cls, serialized_env: str, storage: TupliStorage) -> Env:
        # Deserialize the benchmark environment
        env = jsonpickle.decode(serialized_env)
        env = cls._deserialize(env, storage)
        return env

    def _serialize(self, env: Env) -> tuple[Env, list]:
        # Custom operations like removing artifacts that has to be implemented by subclasses
        related_artifacts = []
        return env, related_artifacts

    @classmethod
    def _deserialize(cls, env: Env, storage: TupliStorage) -> Env:
        # Custom operations like adding artifacts that has to be implemented by subclasses
        return env

    def _convert_to_tuple(
        self,
        obs: np.ndarray,
        reward: float,
        terminated: bool,
        truncated: bool,
        info: dict[str, Any],
        action: np.ndarray,
    ) -> RLTuple:
        # might have to be overwritten for some custom environments
        return RLTuple(
            state=obs.tolist(),
            action=action.tolist(),
            reward=reward,
            terminal=terminated,
            timeout=truncated,
            info=info,
        )

    def reset(
        self, *, seed: int | None = None, options: dict[str, Any] | None = None
    ) -> tuple[Any, dict[str, Any]]:
        """Uses the :meth:`reset` of the :attr:`env` that can be overwritten to change the returned data."""
        return self.env.reset(seed=seed, options=options)

    def step(self, action: Any) -> tuple[Any, SupportsFloat, bool, bool, dict[str, Any]]:
        """Uses the :meth:`step` of the :attr:`env` that can be overwritten to change the returned data."""
        obs, reward, terminated, truncated, info = self.env.step(action)
        self.tuple_buffer.append(
            self._convert_to_tuple(obs, reward, terminated, truncated, info, action)
        )
        if (terminated or truncated) and self._record_episodes:
            episode = Episode(benchmark_id=self.id, metadata={}, tuples=self.tuple_buffer)
            self.storage.record_episode(episode)
            self.tuple_buffer = []
        return obs, reward, terminated, truncated, info

    def _prepare_storage(self, metadata: BenchmarkMetadata) -> tuple[str, str]:
        """
        Prepare the storage by serializing the environment and computing the hash.
        """
        serialized_env = self.serialize_env(self.env)
        benchmark_hash = self._get_hash([self.env, metadata])  # ToDo: What to include in the hash?
        return benchmark_hash, serialized_env

    def store(
        self,
        name: str,
        description: str = '',
        difficulty: str | None = None,
        version: str | None = None,
        metadata: dict[str, Any] = {},
    ) -> str:
        """
        Store the benchmark.
        Reuturn the benchmark ID.
        """
        metadata = BenchmarkMetadata(
            name=name,
            description=description,
            difficulty=difficulty,
            version=version,
            extra=metadata,
        )
        benchmark_hash, serialized_env = self._prepare_storage(metadata=metadata)
        object_metadata = self.storage.store_benchmark(
            benchmark_query=BenchmarkQuery(
                hash=benchmark_hash, serialized=serialized_env, metadata=metadata
            )
        )
        self.id = object_metadata.id

    def publish(self) -> None:
        """
        Publish the benchmark.
        """
        self.storage.publish(self.id)

    @classmethod
    def load(
        cls,
        storage: TupliStorage,
        benchmark_id: str | None = None,
    ) -> TupliBenchmark:
        """
        Load the benchmark from storage.
        """

        stored_benchmark: Benchmark = storage.load_benchmark(benchmark_id)
        env: Env = cls.deserialize_env(stored_benchmark.serialized, storage)

        return cls(env, storage, benchmark_id)

    def delete(self, delete_artifacts: bool = False, delete_episodes: bool = True):
        """
        Delete the scenario from storage. (API only)

        Args:
            delete_data_sources (bool, optional): Automatically delete related data sources. Defaults to False.
        """
        if delete_episodes:
            try:
                episode_filter = FilterEQ(key='benchmark_id', value=self.id)
                episodes = self.storage.list_episodes(episode_filter, include_tuples=True)
                for eps in episodes:
                    self.storage.delete_episode(eps.id)
            except Exception as e:
                raise e
        try:
            self.storage.delete_benchmark(self.id)
        except Exception as e:
            raise e
        if delete_artifacts:
            try:
                for ds_id in self.env.unwrapped.related_artifacts:
                    self.storage.delete_artifact(ds_id)
            except Exception as e:
                raise e


class TimedeltaHandler(jsonpickle.handlers.BaseHandler):
    """
    A custom handler for serializing and deserializing\
        timedelta objects to and from JSON.

    This handler is used by the jsonpickle library to handle serialization and deserialization
    of timedelta objects.

    Attributes:
        None

    Methods:
        flatten(obj, data): Flattens the timedelta object into a dictionary representation.
        restore(obj): Restores the object from a dictionary representation.

    Usage:
        This handler should be registered with the jsonpickle library to enable serialization
        and deserialization of timedelta objects.

    """

    def flatten(self, obj, data: dict):
        return data | {'days': obj.days, 'seconds': obj.seconds, 'microseconds': obj.microseconds}

    def restore(self, obj):
        return timedelta(days=obj['days'], seconds=obj['seconds'], microseconds=obj['microseconds'])


TimedeltaHandler.handles(timedelta)
