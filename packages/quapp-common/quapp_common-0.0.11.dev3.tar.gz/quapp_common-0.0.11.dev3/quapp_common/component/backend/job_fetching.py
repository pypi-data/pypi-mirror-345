"""
    QApp Platform Project job_fetching.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from abc import ABC, abstractmethod
from typing import Any

from ..callback.update_job_metadata import update_job_metadata
from ...async_tasks.post_processing_task import PostProcessingTask
from ...config.logging_config import logger
from ...config.thread_config import circuit_running_pool
from ...data.callback.callback_url import CallbackUrl
from ...data.promise.post_processing_promise import PostProcessingPromise
from ...data.request.job_fetching_request import JobFetchingRequest
from ...data.response.authentication import Authentication
from ...data.response.job_response import JobResponse
from ...data.response.project_header import ProjectHeader
from ...enum.invocation_step import InvocationStep
from ...enum.media_type import MediaType
from ...enum.status.job_status import JobStatus
from ...enum.status.status_code import StatusCode
from ...util.json_parser_utils import JsonParserUtils
from ...util.response_utils import ResponseUtils

logger = logger.bind(context='JobFetching')


class JobFetching(ABC):
    def __init__(self, request_data: JobFetchingRequest):
        self.provider_authentication: dict = request_data.provider_authentication
        self.provider_job_id: str = request_data.provider_job_id
        self.backend_authentication: Authentication = request_data.authentication
        self.project_header: ProjectHeader = request_data.project_header
        self.callback_dict: dict = {
            InvocationStep.EXECUTION: request_data.execution,
            InvocationStep.ANALYSIS: request_data.analysis,
            InvocationStep.FINALIZATION: request_data.finalization
        }

    def fetch(self, post_processing_fn):
        """

        @param post_processing_fn:
        @return:
        """
        logger.debug("Fetch job")

        job_response = JobResponse(
            provider_job_id=self.provider_job_id,
            authentication=self.backend_authentication,
            project_header=self.project_header,
            status_code=StatusCode.DONE)

        try:
            provider = self._collect_provider()

            job = self._retrieve_job(provider)
            job_status = self._get_job_status(job)
            original_job_result = self._get_job_result(job)

            job_response.job_status = job_status

            if JobStatus.DONE.value.__eq__(job_response.job_status):
                circuit_running_pool.submit(self.__handle_job_result,
                                            original_job_result,
                                            job_response,
                                            self.callback_dict,
                                            post_processing_fn)

                update_job_metadata(
                    job_response=job_response,
                    callback_url=self.callback_dict.get(InvocationStep.EXECUTION).on_done)

            elif JobStatus.ERROR.value.__eq__(job_response.job_status):
                job_response.job_result = JsonParserUtils.parse(original_job_result)

                update_job_metadata(
                    job_response=job_response,
                    callback_url=self.callback_dict.get(InvocationStep.EXECUTION).on_error)

            else:
                job_response.status_code = StatusCode.POLLING

        except Exception as exception:
            logger.debug("Exception when fetch job with provider_job_id {0}: {1}".format(
                self.provider_job_id, str(exception)))

            job_response.job_result = {
                "error": "Exception when fetch job with provider_job_id {0}: {1}".format(
                    self.provider_job_id, str(exception)),
                "exception": str(exception),
            }
            job_response.status_code = StatusCode.ERROR
            job_response.job_status = JobStatus.ERROR.value

            update_job_metadata(
                job_response=job_response,
                callback_url=self.callback_dict.get(InvocationStep.EXECUTION).on_error)

        return ResponseUtils.generate_response(job_response)

    def __handle_job_result(self,
                            original_job_result,
                            job_response: JobResponse,
                            callback_dict: dict,
                            post_processing_fn):
        """
        Fetch job from IBM Quantum

        @return: Job status
        """

        job_response = self.__on_analysis(
            callback_url=callback_dict.get(InvocationStep.ANALYSIS),
            job_response=job_response,
            original_job_result=original_job_result)

        if job_response is None:
            return

        self.__on_finalization(post_processing_fn=post_processing_fn,
                               callback_url=callback_dict.get(InvocationStep.FINALIZATION),
                               original_job_result=original_job_result)

    def __on_analysis(self,
                      callback_url: CallbackUrl,
                      job_response: JobResponse,
                      original_job_result):
        """

        @param callback_url:
        @param job_response:
        @param original_job_result:
        @return:
        """
        logger.debug("On analysis")

        update_job_metadata(job_response=job_response,
                            callback_url=callback_url.on_start)

        try:
            job_response.content_type = MediaType.APPLICATION_JSON

            job_response.job_histogram = self.__produce_histogram_data(original_job_result)

            job_result_parse = JsonParserUtils.parse(original_job_result.result())

            job_response.execution_time = self.__get_execution_time(original_job_result)

            update_job_metadata(
                job_response=job_response,
                callback_url=callback_url.on_done)

            return job_response

        except Exception as exception:
            logger.error("Exception when analyst job result with provider_job_id {0}: {1}".format(
                self.provider_job_id, str(exception)))

            job_response.status_code = StatusCode.ERROR
            job_response.job_status = JobStatus.ERROR.value
            job_response.job_result = {
                "error": "Exception when analyst job result with provider_job_id {0}".format(
                    self.provider_job_id),
                "exception": str(exception),
            }

            update_job_metadata(
                job_response=job_response,
                callback_url=callback_url.on_error)

            return None

    def __on_finalization(self,
                          post_processing_fn,
                          callback_url: CallbackUrl,
                          original_job_result):
        """

        @param post_processing_fn:
        @param callback_url:
        @param original_job_result:
        """
        logger.debug("On finalization")

        promise = PostProcessingPromise(callback_url=callback_url,
                                        authentication=self.backend_authentication,
                                        job_result=original_job_result.result(),
                                        project_header=self.project_header)

        PostProcessingTask(post_processing_fn=post_processing_fn,
                           promise=promise).do()

    @staticmethod
    def __produce_histogram_data(job_result) -> Any | None:
        """

        @param job_result:
        @return:
        """
        logger.debug("Produce histogram")

        try:
            histogram_data = job_result.result()[0].data.meas.get_counts()

        except Exception as e:
            logger.debug("[QiskitDevice] Can't produce histogram with error: {0}".format(str(e)))
            histogram_data = None

        return histogram_data

    @staticmethod
    def __get_execution_time(job_result):
        """

        @param job_result:
        @return:
        """
        return job_result.usage()

    @abstractmethod
    def _collect_provider(self, ):
        """
        Create provider with ProviderFactory
        """

        raise NotImplemented('[Invocation] _create_provider() method must be implemented')

    @abstractmethod
    def _retrieve_job(self, provider):
        """
        Retrieve job from provider
        """

        raise NotImplemented('[Invocation] _retrieve_job() method must be implemented')

    @abstractmethod
    def _get_job_status(self, job):
        """
        Get job status
        """

        raise NotImplemented('[Invocation] _get_job_status() method must be implemented')

    @abstractmethod
    def _get_job_result(self, job):
        """
        Get job result
        """

        raise NotImplemented('[Invocation] _get_job_result() method must be implemented')
