"""
    QApp Platform Project response_utils.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from ..data.response.job_response import JobResponse


class ResponseUtils:

    @staticmethod
    def generate_response(job_response: JobResponse) -> dict:
        if job_response:
            status_code = job_response.status_code.value
            body = {
                "providerJobId": job_response.provider_job_id,
                "jobStatus": job_response.job_status,
                "jobResult": job_response.job_result,
                "contentType": job_response.content_type.value,
                "histogram": job_response.job_histogram,
                "executionTime": job_response.execution_time
            }

            # Add 'shots' only if it exists in the job_response
            if hasattr(job_response, 'shots'):
                body["shots"] = job_response.shots

        else:
            status_code = job_response.status_code.value
            body = "Error in function code. Please contact the developer."

        return {
            "statusCode": status_code,
            "body": body,
            "userIdentity": job_response.user_identity,
            "userToken": job_response.user_token,
            "projectId": job_response.project_header.value
        }
