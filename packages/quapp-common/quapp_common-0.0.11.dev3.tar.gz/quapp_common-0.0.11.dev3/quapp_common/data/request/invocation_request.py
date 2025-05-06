"""
    QApp Platform Project invocation_request.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
#  Quapp Platform Project
#  invocation_request.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

from urllib.parse import urlparse

from ..callback.callback_url import CallbackUrl
from ..request.request import Request
from ...config.logging_config import logger
from ...enum.processing_unit import ProcessingUnit
from ...enum.sdk import Sdk
logger = logger.bind(context='InvocationRequest')


class InvocationRequest(Request):
    def __init__(self, request_data: dict):
        if not isinstance(request_data, dict):
            raise ValueError(
                f"request_data must be a dictionary, got {type(request_data).__name__}")

        # Validate required URL fields
        required_urls = {"serverUrl": "device_selection_url",
                         "circuitExportUrl": "circuit_export_url"}

        for key, field_name in required_urls.items():
            validate_url_field(request_data, key, field_name)

        event_urls = {"preparation": "preparation", "execution": "execution",
                      "analysis": "analysis", "finalization": "finalization"}

        callback_urls = {"onStartCallbackUrl": "onStartCallbackUrl",
                         "onErrorCallbackUrl": "onErrorCallbackUrl",
                         "onDoneCallbackUrl": "onDoneCallbackUrl"}

        for key, field_name in event_urls.items():
            for key_url, field_name_url in callback_urls.items():
                validate_url_field(request_data.get(key), key_url, field_name_url)

        # Validate sdk
        sdk_value = request_data.get("sdk").lower()
        if sdk_value is not None:
            try:
                Sdk.resolve(sdk_value)
            except Exception:
                raise ValueError(f"sdk must be a valid Sdk value, got {sdk_value!r}")

        # Validate authentication (if provided)
        authentication = request_data.get("authentication")
        if authentication is not None and not isinstance(authentication, dict):
            raise ValueError(
                f"authentication must be a dictionary if provided, got {type(authentication).__name__}")

        super().__init__(request_data)
        self.input = request_data.get("input")
        self.shots = request_data.get("shots")
        self.device_id = request_data.get("deviceId")
        self.device_selection_url = request_data["serverUrl"]
        self.sdk = sdk_value or None
        self.circuit_export_url = request_data["circuitExportUrl"]
        self.processing_unit = (
            ProcessingUnit.GPU if request_data.get("processingUnit") == ProcessingUnit.GPU.value
            else ProcessingUnit.CPU
        )
        self.preparation = CallbackUrl(request_data["preparation"])
        self.invoke_authentication = authentication


def validate_url_field(request_data: dict, key: str, field_name: str) -> None:
    value = request_data.get(key)
    if value is None or not isinstance(value, str) or not value.strip():
        raise ValueError(
            f"{field_name} (key: {key}) is required, must be a non-empty string, got {value!r}")
    parsed = urlparse(value)
    if not (parsed.scheme and parsed.netloc):
        raise ValueError(f"{field_name} (key: {key}) must be a valid URL, got {value!r}")
