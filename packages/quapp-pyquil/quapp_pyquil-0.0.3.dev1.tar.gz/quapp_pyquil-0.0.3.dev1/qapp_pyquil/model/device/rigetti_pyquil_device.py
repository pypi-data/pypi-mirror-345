"""
    QApp Platform Project
    qapp_pyquil_device.py
    Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
import time
import math

from quapp_common.data.response.authentication import Authentication
from quapp_common.data.response.project_header import ProjectHeader
from quapp_common.model.device.device import Device
from quapp_common.config.logging_config import logger
from quapp_common.data.device.circuit_running_option import CircuitRunningOption
from quapp_common.model.provider.provider import Provider
from quapp_common.enum.invocation_step import InvocationStep

import pickle


class RigettiPyquilDevice(Device):
    def __init__(self, provider: Provider, device_specification: str):
        super().__init__(provider, device_specification)
        logger.debug('[RigettiPyquilDevice] Initializing device specification')
        self.device_specification = device_specification

    def _create_job(self, circuit, options: CircuitRunningOption):
        logger.debug(
            '[RigettiPyquilDevice] Creating job with {0} shots'.format(
                options.shots))
        
        circuit.wrap_in_numshots_loop(options.shots)
        executable = self.device.compile(circuit)

        return self.device.qam.execute(executable)

    def _is_simulator(self) -> bool:
        logger.debug('[RigettiPyquilDevice] is quantum machine')
        return False

    def _get_provider_job_id(self, job) -> str:
        logger.debug('[PyquilDevice] Getting job id')

        job_id = job.job_id

        with open(job_id + ".pkl", "wb") as f:
            pickle.dump(job,f)

        print("Job ID: ", job_id)

        return job_id

    def _get_job_status(self, job) -> str:
        logger.debug('[PyquilDevice] Getting job status')

        return "RUNNING"

    def _calculate_execution_time(self, job_result):

        logger.debug('[PyquilDevice] Getting execution time')
        return None

    def _get_job_result(self, job) -> dict:
        
        return None

    def _produce_histogram_data(self, job_result) -> dict | None:
        logger.info('[PyquilDevice] Producing histogram data')

        return None

