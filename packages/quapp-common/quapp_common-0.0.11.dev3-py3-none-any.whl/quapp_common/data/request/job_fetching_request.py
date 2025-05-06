#  Quapp Platform Project
#  job_fetching_request.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

from .request import Request
from ...config.logging_config import logger

logger = logger.bind(context='JobFetchingRequest')


class JobFetchingRequest(Request):
    def __init__(self, request_data: dict | None):
        if not isinstance(request_data, dict):
            logger.error("Invalid request_data: %s", type(request_data).__name__)
            raise ValueError(
                f"request_data must be a dictionary, got {type(request_data).__name__}")

        # Validate provider_authentication
        provider_authentication = request_data.get("providerAuthentication")
        if provider_authentication is not None and not isinstance(provider_authentication, dict):
            logger.error("Invalid provider_authentication: %s",
                         type(provider_authentication).__name__)
            raise ValueError(
                f"provider_authentication must be a dictionary if provided, got {type(provider_authentication).__name__}")

        super().__init__(request_data)
        self.provider_authentication = provider_authentication
