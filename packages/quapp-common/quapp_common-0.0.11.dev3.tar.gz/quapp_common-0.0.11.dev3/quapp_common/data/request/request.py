"""
    QApp Platform Project request.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from ..response.authentication import Authentication
from ..response.project_header import ProjectHeader
from ...data.callback.callback_url import CallbackUrl


class Request:
    def __init__(self, request_data):
        self.provider_job_id = request_data.get("providerJobId")
        self.authentication: Authentication = Authentication(
            user_token=request_data.get("userToken"),
            user_identity=request_data.get("userIdentity"))
        self.execution = CallbackUrl(request_data.get("execution"))
        self.analysis: CallbackUrl = CallbackUrl(request_data.get("analysis"))
        finalization_callback = request_data.get("finalization")
        self.finalization: CallbackUrl = CallbackUrl(finalization_callback) \
            if finalization_callback \
            else finalization_callback
        project_header = request_data.get("projectHeader")
        self.project_header: ProjectHeader = ProjectHeader(name=project_header.get("name"),
                                                           value=project_header.get("value"))
