"""
    QApp Platform Project export_circuit.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from io import BytesIO

import requests

from .async_task import AsyncTask
from ..config.logging_config import logger
from ..data.async_task.circuit_export.backend_holder import BackendDataHolder
from ..data.async_task.circuit_export.circuit_holder import CircuitDataHolder
from ..enum.media_type import MediaType
from ..util.file_utils import FileUtils
from ..util.http_utils import HttpUtils

logger = logger.bind(context='CircuitExportTask')


class CircuitExportTask(AsyncTask):
    MAX_CIRCUIT_IMAGE_SIZE = 5 * (1024 ** 2)

    def __init__(self,
                 circuit_data_holder: CircuitDataHolder,
                 backend_data_holder: BackendDataHolder):
        super().__init__()
        self.circuit_data_holder = circuit_data_holder
        self.backend_data_holder = backend_data_holder

    def do(self):
        """
          Export circuit to svg file then send to QuaO server for saving
        """
        logger.debug("Start")

        circuit_export_url = self.circuit_data_holder.export_url

        if circuit_export_url is None or len(circuit_export_url) < 1:
            return

        figure_buffer = self.__convert()

        io_buffer_value, content_type = self.__determine_zip(figure_buffer=figure_buffer)

        self.__send(io_buffer_value=io_buffer_value,
                    content_type=content_type)

    def __convert(self):
        """

        @return:
        """
        logger.debug("Preparing circuit figure...")
        transpiled_circuit = self._transpile_circuit()
        circuit_figure = transpiled_circuit.draw(output='mpl', fold=-1)

        logger.debug("Converting circuit figure to svg file...")
        figure_buffer = BytesIO()
        circuit_figure.savefig(figure_buffer, format='svg', bbox_inches='tight')

        return figure_buffer

    @staticmethod
    def __determine_zip(figure_buffer):
        """

        @param figure_buffer:
        @return:
        """
        buffer_value = figure_buffer.getvalue()
        content_type = MediaType.SVG_XML

        logger.debug("Checking max file size")
        estimated_file_size = len(buffer_value)

        if estimated_file_size > CircuitExportTask.MAX_CIRCUIT_IMAGE_SIZE:
            logger.debug("Zip file")
            zip_file_buffer = FileUtils.zip(io_buffer_value=buffer_value,
                                            file_name="circuit_image.svg")

            buffer_value = zip_file_buffer.getvalue()
            content_type = MediaType.APPLICATION_ZIP

        return buffer_value, content_type

    def __send(self, io_buffer_value, content_type: MediaType):
        """

        @param io_buffer_value:
        @param content_type:
        """
        url = self.circuit_data_holder.export_url

        logger.debug(
            "Sending circuit svg image to [{0}] with POST method ...".format(
                url))

        payload = {'circuit': (
            'circuit_image.svg',
            io_buffer_value,
            content_type.value)}

        response = requests.post(
            url=url,
            headers=HttpUtils.create_bearer_header(self.backend_data_holder.user_token),
            files=payload)

        if response.ok:
            logger.debug("Sending request to QuaO backend successfully!")
        else:
            logger.error("Sending request to QuaO backend failed with status {0}!".format(
                response.status_code))

        logger.debug("Finish")

    def _transpile_circuit(self):
        """

        @return: Transpiled circuit
        """

        raise NotImplemented('[CircuitExportTask] __transpile_circuit() method must be implemented')
