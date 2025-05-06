#  Quapp Platform Project
#  custom_device.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

from abc import ABC, abstractmethod

from quapp_common.model.device.device import Device
from quapp_common.model.provider.provider import Provider
from ...component.callback.update_job_metadata import update_job_metadata
from ...config.logging_config import logger
from ...data.callback.callback_url import CallbackUrl
from ...data.response.job_response import JobResponse
from ...enum.media_type import MediaType
from ...enum.status.job_status import JobStatus
from ...enum.status.status_code import StatusCode
from ...util.json_parser_utils import JsonParserUtils

logger = logger.bind(context='CustomDevice')


class CustomDevice(Device, ABC):
    def __init__(self, provider: Provider, device_specification: str):
        super().__init__(provider, device_specification)
        self.shots = None

    def _on_analysis(self, job_response: JobResponse,
                     analysis_callback: CallbackUrl,
                     original_job_result):
        """

        @param job_response:
        @param analysis_callback:
        @param original_job_result:
        @return:
        """
        logger.debug("On analysis")

        update_job_metadata(job_response=job_response,
                            callback_url=analysis_callback.on_start)

        try:
            job_response.job_histogram = self._produce_histogram_data(original_job_result)

            original_job_result_dict = JsonParserUtils.parse(original_job_result)
            self._calculate_execution_time(original_job_result_dict)
            job_response.execution_time = self.execution_time
            job_response.shots = self._get_shots(original_job_result)

            update_job_metadata(
                job_response=job_response,
                callback_url=analysis_callback.on_done)

            return job_response

        except Exception as exception:
            logger.error("Invocation - Exception when analyst job result : {0}".format(
                str(exception)))

            job_response.status_code = StatusCode.ERROR
            job_response.content_type = MediaType.APPLICATION_JSON
            job_response.job_status = JobStatus.ERROR.value
            job_response.job_result = {"error": str(exception)}

            update_job_metadata(job_response=job_response,
                                callback_url=analysis_callback.on_error)
            return None

    @abstractmethod
    def _get_shots(self, job_result) -> int:
        """
        Retrieve the number of shots from the job result.

        This method extracts the 'shots' value from the provided job result
        dictionary and logs the action for debugging purposes.

        Args:
            job_result (dict): A dictionary containing the results of a job,
                               which is expected to include the key 'shots'.

        Returns:
            int: The number of shots retrieved from the job result.
                 If the key 'shots' does not exist, it will return None.

        Raises:
            KeyError: If the job_result does not contain the 'shots' key
                       and the implementation does not handle it.
        """
        raise NotImplementedError("[CustomDevice] Subclasses must implement this "
                                  "method")
