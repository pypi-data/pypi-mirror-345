"""
    QApp Platform Project async_task.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from abc import abstractmethod


class AsyncTask:

    @abstractmethod
    def do(self):
        pass
