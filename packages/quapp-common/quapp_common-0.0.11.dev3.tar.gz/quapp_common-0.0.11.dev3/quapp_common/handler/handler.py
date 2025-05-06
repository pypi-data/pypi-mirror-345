"""
    QApp Platform Project handler.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from abc import ABC, abstractmethod


class Handler(ABC):

    def __init__(self,
                 request_data: dict,
                 post_processing_fn):
        self.request_data = request_data
        self.post_processing_fn = post_processing_fn

    @abstractmethod
    def handle(self):
        """

        """
        raise NotImplemented('[Handler] handle() method must be implemented')
