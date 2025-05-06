"""
Module for everything related to banchmark storage.
"""

from __future__ import annotations
import hashlib
import json
import logging
from pathlib import Path
from typing import Any, Callable, Dict

import pandas as pd
import requests
import keyring
from dotenv import load_dotenv

from pytupli.schema import (
    ArtifactMetadata,
    ArtifactMetadataItem,
    BaseFilter,
    Benchmark,
    BenchmarkHeader,
    BenchmarkQuery,
    User,
    UserOut,
    UserRole,
    Episode,
    EpisodeHeader,
    EpisodeItem,
    FilterType,
)

load_dotenv()

# Set up logger
logger = logging.getLogger(__name__)


class TupliStorageError(Exception):
    """
    Exception raised for errors in the storage operations.
    """

    pass


class TupliStorage:
    """
    Base class for storing StorableObjects.
    """

    def __init__(self):
        raise NotImplementedError

    def store_benchmark(self, benchmark_query: BenchmarkQuery) -> BenchmarkHeader:
        """
        Saves the serialized object to the specified storage.

        Args:
            benchmark_query (BenchmarkQuery): The serialized benchmark object to be saved.

        Returns:
            BenchmarkHeader: The header of the saved benchmark.
        """
        raise NotImplementedError

    def load_benchmark(
        self,
        uri: str,
    ) -> Benchmark:
        """
        Loads data from the specified URI.

        Args:
            uri (str): The URI of the data to be loaded.
        """
        raise NotImplementedError

    def list_benchmarks(self, filter: BaseFilter) -> list[BenchmarkHeader]:
        """
        Lists all benchmarks in the storage that match the specified filter.

        Args:
            filter (BaseFilter): The filter to apply when listing benchmarks.

        Returns:
            list[BenchmarkHeader]: A list of benchmark headers that match the filter.
        """
        raise NotImplementedError

    def delete_benchmark(self, uri: str) -> None:
        """
        Deletes the specified benchmark from the storage.
        """
        raise NotImplementedError

    def store_artifact(self, artifact: bytes, metadata: ArtifactMetadata) -> ArtifactMetadataItem:
        """
        Stores the artifact in the storage.

        Args:
            artifact (bytes): The artifact to store.
            metadata (ArtifactMetadata): Metadata for the artifact.

        Returns:
            ArtifactMetadataItem: Metadata item for the stored artifact.
        """
        raise NotImplementedError

    def load_artifact(self, uri: str, **kwargs) -> pd.DataFrame:
        """
        Loads the artifact from the storage.
        """
        raise NotImplementedError

    def list_artifacts(self, filter: BaseFilter) -> list[ArtifactMetadataItem]:
        """
        Lists all artifacts in the storage that match the specified filter.

        Args:
            filter (BaseFilter): The filter to apply when listing artifacts.

        Returns:
            list[ArtifactMetadataItem]: A list of artifacts that match the filter.
        """
        raise NotImplementedError

    def delete_artifact(self, uri: str) -> None:
        """
        Deletes the specified artifact from the storage.
        """
        raise NotImplementedError

    def record_episode(self, episode: Episode) -> EpisodeHeader:
        """
        Records an episode in the storage.

        Args:
            episode (Episode): The episode to record.

        Returns:
            EpisodeHeader: The header of the recorded episode.
        """
        raise NotImplementedError

    def publish_episode(self, uri: str) -> None:
        """
        Publishes the specified episode in the storage.

        Args:
            uri (str): The URI/ID of the episode to publish.
        """
        raise NotImplementedError

    def list_episodes(
        self, filter: BaseFilter = None, include_tuples: bool = False
    ) -> list[EpisodeHeader] | list[EpisodeItem]:
        """
        Lists all episodes in the storage that match the specified filter.

        Args:
            filter (BaseFilter, optional): The filter to apply when listing episodes.
            include_tuples (bool, optional): Whether to include tuples in the episode data.

        Returns:
            list[EpisodeHeader] | list[EpisodeItem]: A list of episode headers or full episode items with tuples.
        """
        raise NotImplementedError

    def delete_episode(self, uri: str) -> None:
        """
        Deletes the specified episode from the storage.

        Args:
            uri (str): The URI/ID of the episode to delete.
        """
        raise NotImplementedError


class TupliAPIClient(TupliStorage):
    """
    Class for storing StorableObjects in the API.

    Args:
        BenchmarkStorage: Base class for storing StorableObjects.

    Attributes:
        api_user (str): The username for the API.
        api_password (str): The password for the API.
        base_url (str): The base URL for the API.
        related_artifact_sources (List): Data sources loaded with this storage object. Used to remove them later.

    Methods:
        save: Saves the serialized object to the API.
        load: Loads the serialized object from the API.
        delete: Deletes the specified object from the API.
        publish: Publishes the serialized object to the API.

    """

    def __init__(self, base_url: str = 'http://localhost:8080') -> TupliAPIClient:
        self.base_url = base_url

    def _get_bearer_token(self):
        """
        Gets the bearer token for API requests.
        First tries to use the stored access token, and if that fails,
        tries to refresh the token.

        Returns:
            dict: Headers with the bearer token.
        """
        # Try to get the stored access token
        access_token = keyring.get_password('pytupli', 'access_token')

        if access_token:
            # First try to use the existing token
            return {'Authorization': f'Bearer {access_token}'}

        # If no access token stored, refresh token
        return self._refresh_token()

    def _refresh_token(self):
        """
        Refreshes the access token using the stored refresh token.

        Returns:
            dict: Headers with the refreshed bearer token.
        """
        refresh_token = keyring.get_password('pytupli', 'refresh_token')

        if not refresh_token:
            raise TupliStorageError('No refresh token available. Please login first.')

        try:
            response = requests.post(
                f'{self.base_url}/auth/refresh-token',
                headers={'Authorization': f'Bearer {refresh_token}'},
            )
            response.raise_for_status()

            new_access_token = response.json()['access_token']
            # Store the new token
            keyring.set_password('pytupli', 'access_token', new_access_token)

            return {'Authorization': f'Bearer {new_access_token}'}
        except Exception as e:
            # If refresh fails, both tokens might be invalid
            keyring.delete_password('pytupli', 'access_token')
            keyring.delete_password('pytupli', 'refresh_token')
            raise TupliStorageError(f'Token refresh failed: {str(e)}. Please login again.')

    def _authenticated_request(self, method, url, **kwargs):
        """
        Executes an authenticated request to the API.
        Handles token refresh if the access token is expired.

        Args:
            method (str): HTTP method (get, post, put, delete)
            url (str): URL for the request
            **kwargs: Additional arguments for the request

        Returns:
            Response: The response from the request
        """
        # First try with current access token
        try:
            headers = self._get_bearer_token()
            if 'headers' in kwargs:
                kwargs['headers'].update(headers)
            else:
                kwargs['headers'] = headers

            response = getattr(requests, method.lower())(url, **kwargs)
            response.raise_for_status()
            return response
        except requests.HTTPError as e:
            if e.response.status_code == 401:  # Unauthorized, token might be expired
                # Try to refresh token and retry
                headers = self._refresh_token()
                if 'headers' in kwargs:
                    kwargs['headers'].update(headers)
                else:
                    kwargs['headers'] = headers

                response = getattr(requests, method.lower())(url, **kwargs)
                response.raise_for_status()
                return response
            raise TupliStorageError(f'API request failed: {str(e)}')
        except Exception as e:
            raise TupliStorageError(f'Request failed: {str(e)}')

    # User management methods
    def signup(self, username: str, password: str) -> User:
        """
        Creates a new user account.

        Args:
            username (str): The username for the new account
            password (str): The password for the new account

        Returns:
            User: The created user object
        """
        try:  # first try authenticated request
            response = self._authenticated_request(
                'post',
                f'{self.base_url}/auth/signup',
                json={'username': username, 'password': password},
            )
            return UserOut(**response.json())
        except TupliStorageError:  # if that fails, try unauthenticated request
            response = requests.post(
                f'{self.base_url}/auth/signup',
                json={'username': username, 'password': password},
            )
            response.raise_for_status()
            return UserOut(**response.json())

    def login(self, username: str, password: str) -> None:
        """
        Authenticates with the API and stores the access and refresh tokens.

        Args:
            username (str): The username for the API.
            password (str): The password for the API.
        """
        response = requests.post(
            f'{self.base_url}/auth/token',
            json={'username': username, 'password': password},
        )
        response.raise_for_status()

        data = response.json()
        access_token = data['access_token']['token']
        refresh_token = data['refresh_token']['token']

        # Store tokens in keyring
        keyring.set_password('pytupli', 'access_token', access_token)
        keyring.set_password('pytupli', 'refresh_token', refresh_token)

    def list_users(self) -> list[User]:
        """
        Lists all users.

        Returns:
            list[User]: A list of all users
        """
        response = self._authenticated_request('get', f'{self.base_url}/auth/list-users')
        return [UserOut(**user) for user in response.json()]

    def list_roles(self) -> list[UserRole]:
        """
        Lists all user roles.

        Returns:
            list[UserRole]: A list of all user roles
        """
        response = self._authenticated_request('get', f'{self.base_url}/auth/list-roles')
        return [UserRole(**role) for role in response.json()]

    def change_password(self, username: str, new_password: str) -> User:
        """
        Changes a user's password.

        Args:
            username (str): The username of the account to change
            new_password (str): The new password

        Returns:
            User: The updated user object
        """
        response = self._authenticated_request(
            'put',
            f'{self.base_url}/auth/change-password',
            json={'username': username, 'password': new_password},
        )
        return UserOut(**response.json())

    def change_roles(self, username: str, roles: list[str]) -> User:
        """
        Changes a user's roles.

        Args:
            username (str): The username of the account to change
            roles (list[str]): The list of new roles

        Returns:
            User: The updated user object
        """
        response = self._authenticated_request(
            'put',
            f'{self.base_url}/auth/change-roles',
            json={'username': username, 'roles': roles},
        )
        return UserOut(**response.json())

    def delete_user(self, username: str) -> None:
        """
        Deletes a user and all their content.

        Args:
            username (str): The username of the account to delete
        """
        self._authenticated_request(
            'delete', f'{self.base_url}/auth/delete-user', params={'username': username}
        )

    def store_benchmark(self, benchmark_query: BenchmarkQuery) -> BenchmarkHeader:
        """
        Saves the serialized object to the API.

        Args:
            benchmark (Benchmark): The serialized benchmark object to be saved.

        Returns:
            BenchmarkHeader: The header of the saved benchmark.
        """
        response = self._authenticated_request(
            'post', f'{self.base_url}/benchmarks/create', json=benchmark_query.model_dump()
        )
        return BenchmarkHeader(**response.json())

    def load_benchmark(self, uri: str) -> Benchmark:
        """
        Loads the serialized benchmark from the API.

        Args:
            uri (str): hash of the object to be loaded.

        Returns:
            benchmark: The loaded benchmark object.
        """
        response = self._authenticated_request(
            'get', f'{self.base_url}/benchmarks/load?benchmark_id={uri}'
        )
        return Benchmark(**response.json())

    def store_artifact(self, artifact: bytes, metadata: ArtifactMetadata) -> ArtifactMetadataItem:
        """
        Stores the artifact in the API.

        Args:
            artifact (bytes): The artifact to store.
            metadata (dict, optional): Metadata for the artifact.

        Returns:
            ArtifactMetadataItem: Metadata item for the stored artifact.
        """
        response = self._authenticated_request(
            'post',
            f'{self.base_url}/artifacts/upload',
            files={'data': artifact},
            data={'metadata': metadata.model_dump_json(serialize_as_any=True)},
        )
        return ArtifactMetadataItem(**response.json())

    def load_artifact(self, uri: str, **kwargs) -> bytes:
        """
        Load artifact from the API.

        Args:
            uri (str): hash of the object to be loaded.

        Returns:
            bytes: The raw artifact data
        """
        response = self._authenticated_request(
            'get', f'{self.base_url}/artifacts/download?artifact_id={uri}'
        )
        return response.content

    def publish_benchmark(self, uri: str) -> None:
        """
        Publishes the benchmark in the API.
        """
        self._authenticated_request('put', f'{self.base_url}/benchmarks/publish?benchmark_id={uri}')

    def delete_benchmark(self, uri: str) -> None:
        """
        Deletes the specified object from the API.

        Args:
            uri (str): The hash of the object to be deleted.
        """
        self._authenticated_request(
            'delete', f'{self.base_url}/benchmarks/delete?benchmark_id={uri}'
        )

    def delete_artifact(self, uri: str) -> None:
        """
        Deletes the specified artifact from the API.

        Args:
            uri (str): The hash of the artifact to be deleted.
        """
        self._authenticated_request('delete', f'{self.base_url}/artifacts/delete?artifact_id={uri}')

    def publish_artifact(self, uri: str) -> None:
        """
        Publishes the artifact in the API.

        Args:
            uri (str): The hash of the artifact to be published.
        """
        self._authenticated_request('put', f'{self.base_url}/artifacts/publish?artifact_id={uri}')

    def list_benchmarks(self, filter: BaseFilter = None) -> list[BenchmarkHeader]:
        """
        Lists all benchmarks in the storage that match the specified filter.

        Args:
            filter (BaseFilter, optional): The filter to apply when listing benchmarks.

        Returns:
            list[BenchmarkHeader]: A list of benchmark headers that match the filter.
        """
        params = {'filter': filter.model_dump_json()} if filter else {}
        response = self._authenticated_request(
            'get', f'{self.base_url}/benchmarks/list', params=params
        )
        return [BenchmarkHeader(**benchmark) for benchmark in response.json()]

    def list_artifacts(self, filter: BaseFilter = None) -> list[ArtifactMetadataItem]:
        """
        Lists all artifacts in the storage that match the specified filter.

        Args:
            filter (BaseFilter, optional): The filter to apply when listing artifacts.

        Returns:
            list[ArtifactMetadataItem]: A list of artifacts that match the filter.
        """
        params = {'filter': filter.model_dump_json()} if filter else {}
        response = self._authenticated_request(
            'get', f'{self.base_url}/artifacts/list', params=params
        )
        return [ArtifactMetadataItem(**artifact) for artifact in response.json()]

    # Episode-related methods
    def record_episode(self, episode: Episode) -> EpisodeHeader:
        """
        Records an episode in the API.

        Args:
            episode (Episode): The episode to record.

        Returns:
            EpisodeHeader: The header of the recorded episode.
        """
        response = self._authenticated_request(
            'post',
            f'{self.base_url}/episodes/record',
            json=episode.model_dump(),
        )
        episode_data = response.json()
        return EpisodeHeader(**episode_data)

    def publish_episode(self, uri: str) -> None:
        """
        Publishes an episode in the API.

        Args:
            uri (str): The ID of the episode to publish.
        """
        self._authenticated_request(
            'put',
            f'{self.base_url}/episodes/publish?episode_id={uri}',
        )

    def list_episodes(
        self, filter: BaseFilter = None, include_tuples: bool = False
    ) -> list[EpisodeHeader] | list[EpisodeItem]:
        """
        Lists all episodes in the API that match the specified filter.

        Args:
            filter (BaseFilter, optional): The filter to apply when listing episodes.
            include_tuples (bool, optional): Whether to include tuples in the episode data.

        Returns:
            list[EpisodeHeader] | list[EpisodeItem]: A list of episode headers or full episode items.
        """
        params = {}
        if filter:
            params['filter'] = filter.model_dump_json()
        params['include_tuples'] = str(include_tuples).lower()

        response = self._authenticated_request(
            'get',
            f'{self.base_url}/episodes/list',
            params=params,
        )

        if include_tuples:
            return [EpisodeItem(**episode) for episode in response.json()]
        else:
            return [EpisodeHeader(**episode) for episode in response.json()]

    def delete_episode(self, uri: str) -> None:
        """
        Deletes an episode from the API.

        Args:
            uri (str): The ID of the episode to delete.
        """
        self._authenticated_request(
            'delete',
            f'{self.base_url}/episodes/delete?episode_id={uri}',
        )


class FileStorage(TupliStorage):
    """
    Storage class for saving and loading benchmarks to/from files.

    Args:
        BenchmarkStorage: Base class for storing StorableObjects.
    """

    def __init__(
        self,
        storage_base_dir: str = '_local_storage',
    ) -> FileStorage:
        self.storage_dir = Path(storage_base_dir)
        # Create base storage directory if it doesn't exist
        try:
            self.storage_dir.mkdir(exist_ok=True)
        except Exception as e:
            raise TupliStorageError(f'Failed to create storage directory: {str(e)}')

    def store_benchmark(self, benchmark_query: BenchmarkQuery) -> BenchmarkHeader:
        """
        Saves the benchmark object to a file.

        Args:
            benchmark_query (BenchmarkQuery): The benchmark query to be saved.

        Returns:
            BenchmarkHeader: The header of the saved benchmark.
        """
        # Create a directory if it doesn't exist
        directory = self.storage_dir / 'benchmarks'
        try:
            directory.mkdir(exist_ok=True, parents=True)
        except Exception as e:
            raise TupliStorageError(f'Failed to create benchmarks directory: {str(e)}')

        # Create a benchmark from the query
        benchmark = Benchmark.create_new(**benchmark_query.model_dump(), created_by='local_storage')

        # Check if benchmark with the same ID already exists
        for existing_file in directory.glob('*.json'):
            try:
                with open(existing_file, 'r', encoding='UTF-8') as f:
                    existing_benchmark = json.loads(f.read())
                if existing_benchmark['hash'] == benchmark.hash:
                    logger.info('Benchmark with hash %s already exists', benchmark.hash)
                    return BenchmarkHeader(**existing_benchmark)
            except Exception as e:
                logger.warning(f'Error reading benchmark file {existing_file}: {str(e)}')
                continue

        # Create filename based on benchmark ID
        file_name = f'{benchmark.id}.json'
        file_path = directory / file_name

        if file_path.exists():
            raise TupliStorageError(
                f'The file {file_path} already exists and will not be overwritten.'
            )

        # Serialize the benchmark to JSON
        try:
            serialized_object = json.dumps(benchmark.model_dump(), indent=2)
        except Exception as e:
            raise TupliStorageError(f'Failed to serialize benchmark: {str(e)}')

        try:
            with open(file_path, 'w', encoding='UTF-8') as f:
                f.write(serialized_object)

            # Check if the file was saved correctly
            if not file_path.exists():
                raise TupliStorageError(f'Failed to save benchmark to {file_path}')
            else:
                logger.info('Saved benchmark to %s', file_path)
        except Exception as e:
            raise TupliStorageError(f'Failed to write benchmark to file: {str(e)}')

        # Return the benchmark header
        return BenchmarkHeader(**benchmark.model_dump())

    def load_benchmark(self, uri: str) -> Benchmark:
        """
        Loads a benchmark from the file using the benchmark ID.

        Args:
            uri (str): The ID of the benchmark to be loaded.

        Returns:
            Benchmark: The loaded benchmark object.
        """
        # Construct the file path from the benchmark ID
        file_path = self.storage_dir / 'benchmarks' / f'{uri}.json'

        if not file_path.exists():
            raise TupliStorageError(f'Benchmark with ID {uri} does not exist.')

        try:
            with open(file_path, 'r', encoding='UTF-8') as f:
                benchmark_dict = json.loads(f.read())
        except json.JSONDecodeError as e:
            raise TupliStorageError(f'Failed to parse JSON from benchmark {uri}: {str(e)}')
        except Exception as e:
            raise TupliStorageError(f'Failed to read benchmark file for {uri}: {str(e)}')

        try:
            # Create and return a Benchmark object from the loaded JSON
            return Benchmark(**benchmark_dict)
        except Exception as e:
            raise TupliStorageError(f'Invalid benchmark data for {uri}: {str(e)}')

    # Helper methods for artifacts
    def store_artifact(self, artifact: bytes, metadata: ArtifactMetadata) -> ArtifactMetadataItem:
        """
        Stores an artifact as a file and returns its metadata.

        Args:
            artifact (bytes): The artifact data to store.
            metadata (ArtifactMetadata): Metadata for the artifact.

        Returns:
            ArtifactMetadataItem: Metadata for the stored artifact.
        """
        # Create a directory for artifacts if it doesn't exist
        data_dir = self.storage_dir / 'artifacts'
        try:
            data_dir.mkdir(exist_ok=True, parents=True)
        except Exception as e:
            raise TupliStorageError(f'Failed to create artifacts directory: {str(e)}')

        # Generate hash for the artifact
        artifact_hash = hashlib.sha256(artifact).hexdigest()

        # Check if artifact with the same hash already exists
        for metadata_path in data_dir.glob('*.metadata.json'):
            try:
                with open(metadata_path, 'r', encoding='UTF-8') as f:
                    existing_metadata = json.loads(f.read())
                if existing_metadata.get('hash') == artifact_hash:
                    logger.info('Artifact with hash %s already exists', artifact_hash)
                    return ArtifactMetadataItem(**existing_metadata)
            except Exception as e:
                logger.warning(f'Error reading metadata file {metadata_path}: {str(e)}')
                continue

        metadata_item = ArtifactMetadataItem.create_new(
            hash=artifact_hash,
            created_by='local_storage',
            **metadata.model_dump(),
        )

        # Create file path using the artifact ID
        file_path = data_dir / f'{metadata_item.id}'

        if file_path.exists():
            raise TupliStorageError(
                f'The file {file_path} already exists and will not be overwritten.'
            )

        try:
            # Write the artifact data to the file
            with open(file_path, 'wb') as f:
                f.write(artifact)

            # Store the metadata
            metadata_path = file_path.with_suffix('.metadata.json')

            with open(metadata_path, 'w', encoding='UTF-8') as f:
                json.dump(metadata_item.model_dump(serialize_as_any=True), f, indent=2)

            logger.info('Stored artifact to %s with metadata', file_path)
            return metadata_item
        except Exception as e:
            raise TupliStorageError(f'Failed to store artifact: {str(e)}')

    def load_artifact(self, uri: str, **kwargs) -> bytes:
        """
        Loads an artifact from a file.

        Args:
            uri (str): The ID of the artifact to load.
            **kwargs: Additional arguments (ignored in file storage)

        Returns:
            bytes: The raw artifact data
        """
        # Construct file path from artifact ID
        file_path = self.storage_dir / 'artifacts' / uri

        if not file_path.exists():
            raise TupliStorageError(f'Artifact with ID {uri} does not exist.')

        try:
            # Read the file as bytes
            with open(file_path, 'rb') as f:
                data = f.read()

            return data
        except Exception as e:
            raise TupliStorageError(f'Failed to load artifact {uri}: {str(e)}')

    def convert_filter_to_function(
        self, filter_obj: BaseFilter
    ) -> Callable[[Dict[str, Any]], bool]:
        """
        Convert a BaseFilter object to a filter function that can be applied to dictionaries.
        Supports nested dictionary access with keys in the form of "a.b.key".

        Args:
            filter_obj (BaseFilter): The filter object to convert.

        Returns:
            Callable[[Dict[str, Any]], bool]: A function that takes a dictionary and returns True if the dictionary matches the filter.
        """
        if filter_obj is None:
            return lambda item: True

        def get_nested_value(item: Dict[str, Any], key_path: str) -> Any:
            """Get value from nested dictionary using dot notation."""
            keys = key_path.split('.')
            value = item

            for k in keys:
                if not isinstance(value, dict) or k not in value:
                    return None
                value = value[k]

            return value

        def key_exists(item: Dict[str, Any], key_path: str) -> bool:
            """Check if a key path exists in nested dictionary."""
            keys = key_path.split('.')
            value = item

            for k in keys:
                if not isinstance(value, dict) or k not in value:
                    return False
                value = value[k]

            return True

        match filter_obj.type:
            case FilterType.AND:
                sub_filters = [self.convert_filter_to_function(f) for f in filter_obj.filters]
                return lambda item: all(f(item) for f in sub_filters)

            case FilterType.OR:
                sub_filters = [self.convert_filter_to_function(f) for f in filter_obj.filters]
                return lambda item: any(f(item) for f in sub_filters)

            case FilterType.EQ:
                return (
                    lambda item: key_exists(item, filter_obj.key)
                    and get_nested_value(item, filter_obj.key) == filter_obj.value
                )

            case FilterType.GEQ:
                return (
                    lambda item: key_exists(item, filter_obj.key)
                    and get_nested_value(item, filter_obj.key) >= filter_obj.value
                )

            case FilterType.LEQ:
                return (
                    lambda item: key_exists(item, filter_obj.key)
                    and get_nested_value(item, filter_obj.key) <= filter_obj.value
                )

            case FilterType.GT:
                return (
                    lambda item: key_exists(item, filter_obj.key)
                    and get_nested_value(item, filter_obj.key) > filter_obj.value
                )

            case FilterType.LT:
                return (
                    lambda item: key_exists(item, filter_obj.key)
                    and get_nested_value(item, filter_obj.key) < filter_obj.value
                )

            case FilterType.NE:
                return (
                    lambda item: key_exists(item, filter_obj.key)
                    and get_nested_value(item, filter_obj.key) != filter_obj.value
                )

            case _:
                raise TupliStorageError(f'Unknown filter type: {filter_obj.type}')

    def list_benchmarks(self, filter: BaseFilter = None) -> list[BenchmarkHeader]:
        """
        Lists all benchmarks in the storage that match the specified filter.

        Args:
            filter (BaseFilter, optional): The filter to apply when listing benchmarks.

        Returns:
            list[BenchmarkHeader]: A list of benchmark headers that match the filter.
        """
        benchmark_dir = self.storage_dir / 'benchmarks'
        if not benchmark_dir.exists():
            return []

        results = []
        filter_func = self.convert_filter_to_function(filter)

        for file_path in benchmark_dir.glob('*.json'):
            try:
                with open(file_path, 'r', encoding='UTF-8') as f:
                    benchmark_dict = json.loads(f.read())

                # Apply filter function
                if filter_func(benchmark_dict):
                    # Create header from benchmark data
                    header = BenchmarkHeader(**benchmark_dict)
                    results.append(header)

            except Exception as e:
                logger.info('Error loading benchmark header from %s: %s', file_path, str(e))
                continue

        return results

    def list_artifacts(self, filter: BaseFilter = None) -> list[ArtifactMetadataItem]:
        """
        Lists all artifacts in the storage that match the specified filter.

        Args:
            filter (BaseFilter, optional): The filter to apply when listing artifacts.

        Returns:
            list[ArtifactMetadataItem]: A list of artifacts that match the filter.
        """
        artifacts_dir = self.storage_dir / 'artifacts'
        if not artifacts_dir.exists():
            return []

        results = []
        filter_func = self.convert_filter_to_function(filter)

        # Look for files that have an accompanying metadata file
        for metadata_path in artifacts_dir.glob('*.metadata.json'):
            try:
                # Read metadata from JSON file
                with open(metadata_path, 'r', encoding='UTF-8') as f:
                    metadata_dict = json.loads(f.read())

                # Apply filter
                if filter_func(metadata_dict):
                    metadata_item = ArtifactMetadataItem(**metadata_dict)
                    results.append(metadata_item)

            except Exception as e:
                logger.info('Error loading artifact metadata from %s: %s', metadata_path, str(e))
                continue

        return results

    def delete_benchmark(self, uri: str) -> None:
        """
        Deletes the specified benchmark from the storage.

        Args:
            uri (str): The ID of the benchmark to delete.
        """
        # Construct file path from benchmark ID
        file_path = self.storage_dir / 'benchmarks' / f'{uri}.json'

        if not file_path.exists():
            raise TupliStorageError(f'Benchmark with ID {uri} does not exist.')

        try:
            file_path.unlink()
            logger.info('Deleted benchmark with ID %s', uri)
        except Exception as e:
            raise TupliStorageError(f'Failed to delete benchmark {uri}: {str(e)}')

    def delete_artifact(self, uri: str) -> None:
        """
        Deletes the specified artifact from the storage.

        Args:
            uri (str): The ID of the artifact to delete.
        """
        # Construct file path from artifact ID
        file_path = self.storage_dir / 'artifacts' / uri
        metadata_path = file_path.with_suffix('.metadata.json')

        if not file_path.exists():
            raise TupliStorageError(f'Artifact with ID {uri} does not exist.')

        try:
            file_path.unlink()
            if metadata_path.exists():
                metadata_path.unlink()
            logger.info('Deleted artifact with ID %s', uri)
        except Exception as e:
            raise TupliStorageError(f'Failed to delete artifact {uri}: {str(e)}')

    def publish_benchmark(self, uri: str) -> None:
        """
        Publishing functionality is not available in FileStorage.
        This is a placeholder to implement the interface.

        Args:
            uri (str): The URI of the benchmark to publish.

        Returns:
            str: The URI of the benchmark.
        """
        logger.info('Publishing functionality is not available in FileStorage')

    def publish_artifact(self, uri: str) -> None:
        """
        Publishing functionality is not available in FileStorage.
        This is a placeholder to implement the interface.

        Args:
            uri (str): The URI of the artifact to publish.
        """
        logger.info('Publishing functionality is not available in FileStorage')

    # Episode-related methods
    def record_episode(self, episode: Episode) -> EpisodeHeader:
        """
        Records an episode in the local file storage.

        Args:
            episode (Episode): The episode to record.

        Returns:
            EpisodeHeader: The header of the recorded episode.
        """
        # Create a directory for episodes if it doesn't exist
        episodes_dir = self.storage_dir / 'episodes'
        try:
            episodes_dir.mkdir(exist_ok=True, parents=True)
        except Exception as e:
            raise TupliStorageError(f'Failed to create episodes directory: {str(e)}')

        # Check if the referenced benchmark exists
        benchmark_dir = self.storage_dir / 'benchmarks'
        benchmark_found = False
        for file_path in benchmark_dir.glob('*.json'):
            try:
                with open(file_path, 'r', encoding='UTF-8') as f:
                    benchmark_dict = json.loads(f.read())
                if benchmark_dict['id'] == episode.benchmark_id:
                    benchmark_found = True
                    break
            except Exception:
                continue

        if not benchmark_found:
            raise TupliStorageError(
                f'Referenced benchmark with ID {episode.benchmark_id} does not exist'
            )

        # Create a full EpisodeItem with metadata
        episode_item = EpisodeItem.create_new(**episode.model_dump(), created_by='local_storage')

        # Create filename based on episode ID
        file_name = f'{episode_item.id}.json'
        file_path = episodes_dir / file_name

        if file_path.exists():
            raise TupliStorageError(
                f'The file {file_path} already exists and will not be overwritten.'
            )

        # Serialize the episode to JSON
        try:
            serialized_object = json.dumps(episode_item.model_dump(), indent=2)
        except Exception as e:
            raise TupliStorageError(f'Failed to serialize episode: {str(e)}')

        try:
            with open(file_path, 'w', encoding='UTF-8') as f:
                f.write(serialized_object)

            # Check if the file was saved correctly
            if not file_path.exists():
                raise TupliStorageError(f'Failed to save episode to {file_path}')
            else:
                logger.info('Saved episode to %s', file_path)
        except Exception as e:
            raise TupliStorageError(f'Failed to write episode to file: {str(e)}')

        # Return the episode header
        return EpisodeHeader(
            **{k: v for k, v in episode_item.model_dump().items() if k != 'tuples'}
        )

    def publish_episode(self, uri: str) -> None:
        """
        Sets the is_public flag of an episode to True in local file storage.
        This is a placeholder to implement the interface.
        Args:
            uri (str): The ID of the episode to publish.
        """
        logger.info('Publishing functionality is not available in FileStorage')

    def list_episodes(
        self, filter: BaseFilter = None, include_tuples: bool = False
    ) -> list[EpisodeHeader] | list[EpisodeItem]:
        """
        Lists all episodes in the local file storage that match the specified filter.

        Args:
            filter (BaseFilter, optional): The filter to apply when listing episodes.
            include_tuples (bool, optional): Whether to include tuples in the episode data.

        Returns:
            list[EpisodeHeader] | list[EpisodeItem]: A list of episode headers or full episode items.
        """
        episodes_dir = self.storage_dir / 'episodes'
        if not episodes_dir.exists():
            return []

        results = []
        filter_func = self.convert_filter_to_function(filter)

        for file_path in episodes_dir.glob('*.json'):
            try:
                with open(file_path, 'r', encoding='UTF-8') as f:
                    episode_dict = json.loads(f.read())

                # Apply filter function
                if filter_func(episode_dict):
                    # If we don't need to include tuples, create an EpisodeHeader
                    if not include_tuples:
                        # Create episode header object without tuples
                        header_dict = {k: v for k, v in episode_dict.items() if k != 'tuples'}
                        results.append(EpisodeHeader(**header_dict))
                    else:
                        # Include full episode with tuples
                        results.append(EpisodeItem(**episode_dict))

            except Exception as e:
                logger.info('Error loading episode from %s: %s', file_path, str(e))
                continue

        return results

    def delete_episode(self, uri: str) -> None:
        """
        Deletes an episode from the local file storage.

        Args:
            uri (str): The ID of the episode to delete.
        """
        # Construct file path from episode ID
        file_path = self.storage_dir / 'episodes' / f'{uri}.json'

        if not file_path.exists():
            raise TupliStorageError(f'Episode with ID {uri} does not exist.')

        try:
            file_path.unlink()
            logger.info('Deleted episode with ID %s', uri)
        except Exception as e:
            raise TupliStorageError(f'Failed to delete episode {uri}: {str(e)}')
