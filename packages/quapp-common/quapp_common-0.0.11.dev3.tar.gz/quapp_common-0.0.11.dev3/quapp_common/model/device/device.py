"""
    QApp Platform Project device.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from abc import abstractmethod, ABC

from ...async_tasks.post_processing_task import PostProcessingTask
from ...component.callback.update_job_metadata import update_job_metadata
from ...config.logging_config import logger
from ...data.callback.callback_url import CallbackUrl
from ...data.device.circuit_running_option import CircuitRunningOption
from ...data.promise.post_processing_promise import PostProcessingPromise
from ...data.response.authentication import Authentication
from ...data.response.job_response import JobResponse
from ...data.response.project_header import ProjectHeader
from ...enum.invocation_step import InvocationStep
from ...enum.media_type import MediaType
from ...enum.status.job_status import JobStatus
from ...enum.status.status_code import StatusCode
from ...model.provider.provider import Provider
from ...util.json_parser_utils import JsonParserUtils


class Device(ABC):
    def __init__(self, provider: Provider, device_specification: str):
        self.provider = provider
        self.device = provider.get_backend(device_specification)
        self.execution_time = None

    def run_circuit(self,
                    circuit,
                    post_processing_fn,
                    options: CircuitRunningOption,
                    callback_dict: dict,
                    authentication: Authentication,
                    project_header: ProjectHeader):
        """

        @param project_header: project header
        @param callback_dict: callback url dictionary
        @param options: Options for run circuit
        @param authentication: Authentication for calling quao server
        @param post_processing_fn: Post-processing function
        @param circuit: Circuit was run
        """

        original_job_result, job_response = self._on_execution(
            authentication=authentication,
            project_header=project_header,
            execution_callback=callback_dict.get(InvocationStep.EXECUTION),
            circuit=circuit,
            options=options)

        if original_job_result is None:
            return

        job_response = self._on_analysis(
            job_response=job_response,
            original_job_result=original_job_result,
            analysis_callback=callback_dict.get(InvocationStep.ANALYSIS))

        if job_response is None:
            return

        self._on_finalization(job_result=original_job_result,
                               authentication=authentication,
                               post_processing_fn=post_processing_fn,
                               finalization_callback=callback_dict.get(InvocationStep.FINALIZATION),
                               project_header=project_header)

    def _on_execution(self, authentication: Authentication,
                       project_header: ProjectHeader,
                       execution_callback: CallbackUrl,
                       circuit,
                       options: CircuitRunningOption):
        """

        @param authentication: authentication information
        @param project_header: project header information
        @param execution_callback: execution step callback urls
        @param circuit: circuit will be run
        @param options: options will use for running
        @return: job and job response
        """
        logger.debug("[Invocation] On execution")

        job_response = JobResponse(authentication=authentication,
                                   project_header=project_header,
                                   status_code=StatusCode.DONE)

        update_job_metadata(job_response=job_response,
                            callback_url=execution_callback.on_start)
        try:
            job = self._create_job(circuit=circuit, options=options)
            job_response.provider_job_id = self._get_provider_job_id(job)
            job_response.job_status = self._get_job_status(job)
            original_job_result = None

            if self._is_simulator():
                job_result = self._get_job_result(job)
                job_response.job_status = self._get_job_status(job)

                if JobStatus.ERROR.value.__eq__(job_response.job_status):
                    job_response.job_result = job_result
                    job_response.content_type = MediaType.APPLICATION_JSON
                else:
                    original_job_result = job_result
            else:
                job_response.status_code = StatusCode.POLLING

            update_job_metadata(job_response=job_response,
                                callback_url=execution_callback.on_done)

            return original_job_result, job_response

        except Exception as exception:
            logger.debug("Execute job failed with error {}".format(str(exception)))

            job_response.status_code = StatusCode.ERROR
            job_response.content_type = MediaType.APPLICATION_JSON
            job_response.job_status = JobStatus.ERROR.value
            job_response.job_result = {"error": str(exception)}

            update_job_metadata(job_response=job_response,
                                callback_url=execution_callback.on_error)
            return None, None

    def _on_analysis(self, job_response: JobResponse,
                      analysis_callback: CallbackUrl,
                      original_job_result):
        """

        @param job_response:
        @param analysis_callback:
        @param original_job_result:
        @return:
        """
        logger.debug("[Invocation] On analysis")

        update_job_metadata(job_response=job_response,
                            callback_url=analysis_callback.on_start)

        try:
            job_response.job_histogram = self._produce_histogram_data(original_job_result)

            original_job_result_dict = JsonParserUtils.parse(original_job_result)
            self._calculate_execution_time(original_job_result_dict)
            job_response.execution_time = self.execution_time

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

    @staticmethod
    def _on_finalization(job_result,
                          finalization_callback: CallbackUrl,
                          post_processing_fn,
                          authentication: Authentication,
                          project_header: ProjectHeader):
        """

        @param job_result: final job result
        @param finalization_callback: callback for update job result
        @param post_processing_fn: post processing function
        @param authentication: authentication of quao
        @param project_header: project header
        """

        if finalization_callback is None:
            return

        logger.info("[Invocation] On finalization")

        post_processing_promise = PostProcessingPromise(
            callback_url=finalization_callback,
            authentication=authentication,
            job_result=job_result,
            project_header=project_header)

        PostProcessingTask(post_processing_fn=post_processing_fn,
                           promise=post_processing_promise).do()

    @abstractmethod
    def _create_job(self, circuit, options: CircuitRunningOption):
        """

        @param circuit: Circuit for create job
        @param options:
        """

        raise NotImplemented('[Device] _create_job() method must be implemented')

    @abstractmethod
    def _is_simulator(self) -> bool:
        """

        """

        raise NotImplemented('[Device] _is_simulator() method must be implemented')

    @abstractmethod
    def _produce_histogram_data(self, job_result) -> dict | None:
        """

        @param job_result:
        """

        raise NotImplemented('[Device] _produce_histogram_data() method must be implemented')

    @abstractmethod
    def _get_provider_job_id(self, job) -> str:
        """

        """

        raise NotImplemented('[Device] _get_provider_job_id() method must be implemented')

    @abstractmethod
    def _get_job_status(self, job) -> str:
        """

        """

        raise NotImplemented('[Device] _get_job_status() method must be implemented')

    @abstractmethod
    def _calculate_execution_time(self, job_result) -> float:
        """

        """

        raise NotImplemented('[Device] _calculate_execution_time() method must be implemented')

    @abstractmethod
    def _get_job_result(self, job):
        """

        @param job:
        @return:
        """
        logger.debug('[Device] Get job result')

        return job.result()
