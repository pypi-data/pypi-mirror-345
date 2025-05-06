"""
    QApp Platform Project job_fetching.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from abc import ABC, abstractmethod
from typing import Dict

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

logger = logger.bind(context='JobFetcher')


class JobFetcher(ABC):
    """
       Abstract base class for fetching job results from different providers.
       """

    def __init__(self, request_data: JobFetchingRequest):
        """Initializes the JobFetcher with request data."""
        self.provider_authentication: Dict = request_data.provider_authentication
        self.provider_job_id: str = request_data.provider_job_id
        self.backend_authentication: Authentication = request_data.authentication
        self.project_header: ProjectHeader = request_data.project_header
        self.callback_urls: Dict[InvocationStep, CallbackUrl] = {
            InvocationStep.EXECUTION: request_data.execution,
            InvocationStep.ANALYSIS: request_data.analysis,
            InvocationStep.FINALIZATION: request_data.finalization
        }

        logger.debug(f"[{self.provider_job_id}] Initialized JobFetcher")

    @abstractmethod
    def _collect_provider(self):
        """Abstract method to create and return the provider client."""
        raise NotImplementedError('[JobFetcher] _collect_provider() method must be implemented')

    @abstractmethod
    def _retrieve_job(self, provider):
        """Abstract method to retrieve the job object from the provider."""
        raise NotImplementedError('[JobFetcher] _retrieve_job() method must be implemented')

    @abstractmethod
    def _get_job_status(self, job):
        """Abstract method to extract the job status from the provider's job object."""
        raise NotImplementedError('[JobFetcher] _get_job_status() method must be implemented')

    @abstractmethod
    def _get_job_result(self, job):
        """Abstract method to extract the raw job result from the provider's job object."""
        raise NotImplementedError('[JobFetcher] _get_job_result() method must be implemented')

    @abstractmethod
    def _produce_histogram_data(self, job_result) -> dict | None:
        """Abstract method to produce histogram data from the raw job result."""
        raise NotImplementedError(
            '[JobFetcher] _produce_histogram_data() method must be implemented')

    @abstractmethod
    def _get_execution_time(self, job_result):
        """Abstract method to extract the execution time from the raw job result."""
        raise NotImplementedError('[JobFetcher] _get_execution_time() method must be implemented')

    @abstractmethod
    def _get_shots(self, job_result):
        """Abstract method to extract the number of shots from the raw job result."""
        raise NotImplementedError('[JobFetcher] _get_shots() method must be implemented')

    def fetch(self, post_processing_fn):
        """Fetches the job, handles different job statuses, and initiates post-processing."""
        logger.debug(f'[{self.provider_job_id}] Fetch job')
        job_response = JobResponse(
            provider_job_id=self.provider_job_id,
            authentication=self.backend_authentication,
            project_header=self.project_header,
            status_code=StatusCode.DONE
        )

        try:
            logger.debug(f'[{self.provider_job_id}] Collecting provider')
            provider = self._collect_provider()

            logger.debug(
                f'[{self.provider_job_id}] Retrieving job from provider')
            job = self._retrieve_job(provider)

            logger.debug(f'[{self.provider_job_id}] Getting job status')
            job_status = self._get_job_status(job)

            logger.debug(
                f'[{self.provider_job_id}] Getting original job result')
            original_job_result = self._get_job_result(job)

            logger.info(f'[{self.provider_job_id}] Job status: {job_status}')
            job_response.job_status = job_status

            if job_status == JobStatus.DONE.value:
                self._handle_successful_job(original_job_result, job_response, post_processing_fn)
                update_job_metadata(job_response=job_response, callback_url=self.callback_urls[
                    InvocationStep.EXECUTION].on_done)
            elif job_status == JobStatus.ERROR.value:
                self._handle_failed_job(original_job_result, job_response)
                update_job_metadata(job_response=job_response, callback_url=self.callback_urls[
                    InvocationStep.EXECUTION].on_error)
            else:
                logger.info(
                    f'[{self.provider_job_id}] Job is in {job_status}, setting status to POLLING')
                job_response.status_code = StatusCode.POLLING

        except Exception as e:
            self._handle_fetch_exception(job_response, e)
            update_job_metadata(job_response=job_response,
                                callback_url=self.callback_urls[InvocationStep.EXECUTION].on_error)

        logger.debug(f'[{self.provider_job_id}] Returning response')
        return ResponseUtils.generate_response(job_response)

    def _handle_successful_job(self, original_job_result, job_response: JobResponse,
                               post_processing_fn):
        """Handles the job result when the job is successfully completed."""
        logger.debug(
            f'[{self.provider_job_id}] Handling successful job')
        circuit_running_pool.submit(
            self._process_job_result,
            original_job_result,
            job_response,
            self.callback_urls,
            post_processing_fn
        )

    def _handle_failed_job(self, original_job_result, job_response: JobResponse):
        """Handles the job result when the job has encountered an error."""
        logger.error(f'[{self.provider_job_id}] Handling failed job')
        job_response.job_result = JsonParserUtils.parse(original_job_result)

    def _handle_fetch_exception(self, job_response: JobResponse, exception: Exception):
        """Handles exceptions that occur during the job fetching process."""
        logger.error(
            f'[{self.provider_job_id}] Exception when fetching job: {exception}')
        job_response.job_result = {
            'error': f'Exception when fetching job: {exception}',
            'exception': str(exception),
        }
        job_response.status_code = StatusCode.ERROR
        job_response.job_status = JobStatus.ERROR.value

    def _process_job_result(self, original_job_result, job_response: JobResponse,
                            callback_urls: Dict[InvocationStep, CallbackUrl], post_processing_fn):
        """Processes the job result through analysis and finalization steps."""
        logger.debug(
            f'[{self.provider_job_id}] Processing job result')

        job_response = self._on_analysis(
            callback_url=callback_urls[InvocationStep.ANALYSIS],
            job_response=job_response,
            original_job_result=original_job_result
        )

        if job_response:
            self._on_finalization(
                post_processing_fn=post_processing_fn,
                callback_url=callback_urls[InvocationStep.FINALIZATION],
                original_job_result=original_job_result
            )

    def _on_analysis(self, callback_url: CallbackUrl, job_response: JobResponse,
                     original_job_result) -> JobResponse | None:
        """Handles the analysis step of the job result."""
        logger.debug(f'[{self.provider_job_id}] On analysis')
        update_job_metadata(job_response=job_response, callback_url=callback_url.on_start)
        logger.debug(
            f'[{self.provider_job_id}] Calling update_job_metadata on_start')

        try:
            job_response.content_type = MediaType.APPLICATION_JSON

            logger.debug(f'[{self.provider_job_id}] Producing histogram data')
            job_response.job_histogram = self._produce_histogram_data(original_job_result)

            logger.debug(f'[{self.provider_job_id}] Getting execution time')
            job_response.execution_time = self._get_execution_time(original_job_result)

            logger.debug(f'[{self.provider_job_id}] Getting shots')
            job_response.shots = self._get_shots(original_job_result)

            update_job_metadata(job_response=job_response, callback_url=callback_url.on_done)
            logger.debug(
                f'[{self.provider_job_id}] Calling update_job_metadata on_done')

            return job_response

        except Exception as e:
            logger.error(
                f'[{self.provider_job_id}] Exception during analysis: {e}')
            job_response.status_code = StatusCode.ERROR
            job_response.job_status = JobStatus.ERROR.value
            job_response.job_result = {
                "error": f'Exception during analysis: {e}',
                "exception": str(e),
            }

            update_job_metadata(job_response=job_response, callback_url=callback_url.on_error)
            logger.debug(
                f'[{self.provider_job_id}] Calling update_job_metadata on_error')
            return None

    def _on_finalization(self, post_processing_fn, callback_url: CallbackUrl, original_job_result):
        """Handles the finalization step of the job result."""
        logger.debug(f'[{self.provider_job_id}] On finalization')
        promise = PostProcessingPromise(
            callback_url=callback_url,
            authentication=self.backend_authentication,
            job_result=original_job_result,
            project_header=self.project_header
        )

        logger.debug(f'[{self.provider_job_id}]Creating PostProcessingTask')
        PostProcessingTask(post_processing_fn=post_processing_fn, promise=promise).do()
