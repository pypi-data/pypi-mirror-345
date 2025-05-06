"""
    QApp Platform Project post_processing_task.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from .async_task import AsyncTask
from ..component.callback.update_job_metadata import update_job_metadata
from ..config.logging_config import logger
from ..data.promise.post_processing_promise import PostProcessingPromise
from ..data.response.job_response import JobResponse
from ..enum.media_type import MediaType
from ..enum.status.job_status import JobStatus
from ..enum.status.status_code import StatusCode
from ..util.json_parser_utils import JsonParserUtils

logger = logger.bind(context='PostProcessingTask')


class PostProcessingTask(AsyncTask):
    def __init__(self,
                 post_processing_fn,
                 promise: PostProcessingPromise):
        self.post_processing_fn = post_processing_fn
        self.promise = promise

    def do(self):
        """
           Execute post_processing and send to backend
        """

        job_response = JobResponse(
            authentication=self.promise.authentication,
            project_header=self.promise.project_header,
            job_status=JobStatus.DONE.value,
            status_code=StatusCode.DONE)

        update_job_metadata(job_response=job_response,
                            callback_url=self.promise.callback_url.on_start)

        job_response.content_type = MediaType.APPLICATION_JSON

        try:

            logger.info("Execute post_processing ...")
            job_result_post_processing = self.post_processing_fn(self.promise.job_result)

            logger.debug("Parsing job result....")
            print(job_result_post_processing)
            job_response.job_result = JsonParserUtils.parse(job_result_post_processing)

            update_job_metadata(job_response=job_response,
                                callback_url=self.promise.callback_url.on_done)

        except Exception as exception:
            job_response.job_result = {
                "error": "Error when execute post_processing(): ",
                "exception": str(exception),
            }
            job_response.status_code = StatusCode.ERROR
            job_response.job_status = JobStatus.ERROR.value

            update_job_metadata(job_response=job_response,
                                callback_url=self.promise.callback_url.on_error)
