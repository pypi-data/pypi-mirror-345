from typing import Optional, List, Dict, Any, Union
import logging
import os
import requests
from enum import Enum
from bioblend import galaxy
from nbitk.config import Config
from nbitk.logger import get_formatted_logger


class BaseClient:
    """
    Base class for Galaxy tool clients that handles common operations and cleanup.
    Provides standardized interfaces for Galaxy instance management, history handling,
    file uploads and downloads, and job monitoring. Subclasses should implement
    tool-specific methods for running analyses and processing results.
    """

    def __init__(self, config: Config, tool_name: str, logger: Optional[logging.Logger] = None) -> None:
        """
        Initialize the BaseClient with a configuration object and optional logger.
        :param config: A Config object containing Galaxy connection settings. May contain
            the following keys:
            - 'galaxy_api_key' (optional; if absent, must be set as environment variable 'GALAXY_API_KEY')
            - 'galaxy_domain' (optional, default 'galaxy.naturalis.nl')
            - 'log_level' (optional, default 'WARNING')
            - 'preserve_history' (optional, default False)
        :param tool_name:
        :param logger:
        """
        self.config = config
        if config.get('log_level') is None:
            config.set('log_level', 'WARNING')
        self.logger = logger or get_formatted_logger(__name__, config)
        self._preserve_history = config.get('preserve_history', False)
        self._gi = self._initialize_galaxy_instance()
        self._history: Optional[Dict[str, Any]] = None
        self._tool = self._get_tool(tool_name)

    def _initialize_galaxy_instance(self) -> galaxy.GalaxyInstance:
        """
        Initialize connection to Galaxy server using configuration settings.

        :return: Configured bioblend Galaxy instance
        :raises RuntimeError: if unable to establish connection to Galaxy
        """
        domain: str = self.config.get('galaxy_domain', 'https://galaxy.naturalis.nl')
        key: str = self._get_api_key()
        return galaxy.GalaxyInstance(url=domain, key=key)

    def _get_api_key(self) -> str:
        """
        Retrieve Galaxy API key from either config or environment variables.

        :return: Valid Galaxy API key
        :raises RuntimeError: if no API key is found in config or environment
        """
        key: Optional[str] = self.config.get('galaxy_api_key')
        if not key:
            key = os.environ.get('GALAXY_API_KEY')
        if not key:
            raise RuntimeError("No Galaxy API key found in config or environment")
        return key

    def _get_tool(self, name: str) -> Dict[str, Any]:
        """
        Get tool by name from Galaxy. The name is provided in bold at the top of the tool form.
        For example: `Identify reads with blastn and find taxonomy`

        :param name: Name of the tool to retrieve
        :return: Tool dictionary containing at least 'id' key
        :raises RuntimeError: if tool is not found
        """
        tools = self._gi.tools.get_tools(name=name)
        if not tools:
            raise RuntimeError(f"Tool '{name}' not found")
        return tools[0]

    def _ensure_history(self) -> Dict[str, Any]:
        """
        Create a new Galaxy history or return existing one. History names are prefixed
        with 'nbitk_' followed by the object's id for tracking purposes.

        :return: Galaxy history object with at minimum an 'id' key
        """
        if not self._history:
            self._history = self._gi.histories.create_history(f'nbitk_{id(self)}')
            self.logger.debug(f"Created Galaxy history {self._history['id']}")
        return self._history

    def _wait_for_job(self, job_id: str) -> None:
        """
        Poll Galaxy server until specified job completes. This is a blocking operation
        that will not return until the job either completes successfully or fails.

        :param job_id: Galaxy job identifier to monitor
        :raises Exception: if job fails or polling encounters an error
        """
        jc = galaxy.jobs.JobsClient(galaxy_instance=self._gi)
        try:
            jc.wait_for_job(job_id=job_id)
            self.logger.debug(f"Job {job_id} completed")
        except Exception as e:
            self.logger.error(f"Job {job_id} failed: {str(e)}")
            raise

    def _upload_file(self, file_path: str, file_type: str) -> str:
        """
        Upload a file to the current Galaxy history.

        :param file_path: Path to file to upload
        :param file_type: Galaxy datatype for the file (e.g., 'tabular', 'fasta')
        :return: Dataset ID of the uploaded file
        :raises RuntimeError: if upload fails or no history exists
        :raises FileNotFoundError: if file_path does not exist
        """
        history = self._ensure_history()
        try:
            with open(file_path, 'r') as file:
                content = file.read()
            result = self._gi.tools.paste_content(
                content,
                history['id'],
                file_type=file_type
            )
            return result['outputs'][0]['id']
        except Exception as e:
            self.logger.error(f"Failed to upload file {file_path}: {str(e)}")
            raise

    def _download_result(self, output: dict, extension: str) -> str:
        """
        Download a dataset from Galaxy and save to a local file.

        :param output: Output dataset dictionary from Galaxy
        :param extension: File extension to save the dataset as
        :return: Path to downloaded file
        :raises RuntimeError: if download fails
        """
        try:
            # external user URL is different than that inside the GUI
            url = f'{self._gi.base_url}/api/datasets/{output["id"]}/display?to_ext={output["file_ext"]}'
            response = requests.get(
                url,
                headers={"x-api-key": self._gi.key},
                allow_redirects=True
            )
            response.raise_for_status()

            # Save to file
            output_path = f"{output['output_name']}_{output['id']}.{extension}"
            with open(output_path, 'w') as f:
               f.write(response.text)

            return output_path

        except Exception as e:
            self.logger.error(f"Failed to download result {output['id']}: {str(e)}")
            raise

    def export_history_as_rocrate(self, target_path: str, include_hidden: bool = False,
                                  include_deleted: bool = False) -> str:
        """
        Export the current Galaxy history as an RO-crate zip file.

        :param target_path: Local path where the RO-crate zip should be saved
        :param include_hidden: Whether to include hidden datasets
        :param include_deleted: Whether to include deleted datasets
        :return: Path to the downloaded RO-crate file
        :raises RuntimeError: if export fails or no history exists
        """
        if not self._history:
            raise RuntimeError("No active history to export")

        try:
            # Prepare the export request payload
            payload = {
                "model_store_format": "rocrate.zip",
                "include_files": True,
                "include_hidden": include_hidden,
                "include_deleted": include_deleted,
                "target_uri": None  # We'll download directly rather than sending to URI
            }

            # Make the export request
            url = f"{self._gi.base_url}/histories/{self._history['id']}/write_store"
            self.logger.info(f"Initiating RO-crate export for history {self._history['id']}")
            response = self._gi.make_post_request(url, payload=payload) # 404 here

            if response.status_code != 200:
                raise RuntimeError(f"Export failed with status {response.status_code}")

            # Save the response content to the target path
            with open(target_path, 'wb') as f:
                f.write(response.content)

            self.logger.info(f"Successfully exported history to {target_path}")
            return target_path

        except Exception as e:
            self.logger.error(f"Failed to export history as RO-crate: {str(e)}")
            raise

    def __del__(self) -> None:
        """
        Cleanup Galaxy history unless explicitly preserved. This will attempt to delete
        the associated Galaxy history if self._preserve_history is False. Failures to
        delete are logged but do not raise exceptions.
        """
        if self._history and not self._preserve_history:
            try:
                self.logger.debug(f"Going to clean up Galaxy history {self._history['id']}")
                self._gi.histories.delete_history(self._history['id'])
            except Exception as e:
                self.logger.warning(f"Failed to cleanup history: {str(e)}")


