from __future__ import annotations
from copy import deepcopy
from typing import Callable, Generator, List
import random
import numpy as np

from pytupli.schema import (
    BaseFilter,
    BenchmarkHeader,
    EpisodeHeader,
    EpisodeItem,
    FilterOR,
    RLTuple,
)
from pytupli.storage import TupliStorage


class TupliDataset:
    def __init__(self, storage: TupliStorage):
        self.storage = storage

        self._benchmark_filter: BaseFilter = None
        self._episode_filter: BaseFilter = None
        self._tuple_filter_fcn: Callable = None

        self.benchmarks: list[BenchmarkHeader] = []
        self.episodes: list[EpisodeHeader] | list[EpisodeItem] = []
        self.tuples: list[RLTuple] = []

        self._refetch_benchmarks_flag = True
        self._refetch_episodes_flag = True
        self._refetch_tuples_flag = True
        self._refilter_tuples_flag = True

    def _fetch_episodes(self, with_tuples: bool = False) -> None:
        if self._refetch_benchmarks_flag:
            self.benchmarks = self.storage.list_benchmarks(self._benchmark_filter)
            self._refetch_benchmarks_flag = False

        if self._refetch_episodes_flag or (self._refetch_tuples_flag and with_tuples):
            episode_filter = FilterOR.from_list(
                self.benchmarks, on_key='benchmark_id', from_key='id'
            )
            if self._episode_filter:
                episode_filter = episode_filter & self._episode_filter

            self.episodes = self.storage.list_episodes(episode_filter, include_tuples=with_tuples)
            self._refetch_episodes_flag = False
            self._refetch_tuples_flag = not with_tuples

    def with_benchmark_filter(self, filter: BaseFilter) -> TupliDataset:
        new_dataset = deepcopy(self)
        new_dataset._benchmark_filter = filter
        new_dataset._refetch_benchmarks_flag = True
        return new_dataset

    def with_episode_filter(self, filter: BaseFilter) -> TupliDataset:
        new_dataset = deepcopy(self)
        new_dataset._episode_filter = filter
        new_dataset._refetch_episodes_flag = True
        return new_dataset

    def with_tuple_filter(self, filter_fcn: Callable) -> TupliDataset:
        new_dataset = deepcopy(self)
        new_dataset._tuple_filter_fcn = filter_fcn
        new_dataset._refilter_tuples_flag = True
        return new_dataset

    def preview(self) -> list[EpisodeHeader]:
        self._fetch_episodes(with_tuples=False)
        return self.episodes

    def load(self) -> None:
        self._fetch_episodes(with_tuples=True)
        if self._refilter_tuples_flag:
            self.tuples = [
                rl_tuple
                for episode in self.episodes
                for rl_tuple in episode.tuples
                if not self._tuple_filter_fcn or self._tuple_filter_fcn(rl_tuple)
            ]
            self._refilter_tuples_flag = False

    def set_seed(self, seed: int) -> None:
        """
        Sets the random seed for reproducibility.

        Args:
            seed: The random seed to set
        """
        random.seed(seed)

    def as_batch_generator(
        self, batch_size: int, shuffle: bool = False
    ) -> Generator[List[RLTuple], None, None]:
        """
        Returns a generator that yields batches of tuples from the dataset.

        Args:
            batch_size: The size of each batch
            shuffle: Whether to shuffle the tuples before creating batches

        Yields:
            Batches of tuples
        """
        # Make sure tuples are loaded
        self.load()

        # Create a copy of the tuples list that we can shuffle if needed
        tuples_to_batch = list(self.tuples)

        # Shuffle if requested
        if shuffle:
            random.shuffle(tuples_to_batch)

        # Yield batches
        for i in range(0, len(tuples_to_batch), batch_size):
            yield tuples_to_batch[i : i + batch_size]

    def sample_episodes(self, n_samples: int) -> list[EpisodeItem]:
        """
        Samples a number of episodes from the dataset.

        Args:
            n_samples: The number of episodes to sample

        Returns:
            A list of sampled episodes
        """
        self._fetch_episodes(with_tuples=False)
        return random.sample(self.episodes, min(n_samples, len(self.episodes)))

    def convert_to_numpy(self) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        observations = np.array([tuple.state for tuple in self.tuples], dtype=np.float64)
        actions = np.array([tuple.action for tuple in self.tuples], dtype=np.float64)
        rewards = np.array([tuple.reward for tuple in self.tuples], dtype=np.float64)
        terminals = np.array([tuple.terminal for tuple in self.tuples], dtype=np.float64)
        timeouts = np.array([tuple.timeout for tuple in self.tuples], dtype=np.float64)
        return observations, actions, rewards, terminals, timeouts
