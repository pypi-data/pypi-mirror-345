"""
    QApp Platform Project
    qapp_pennylane_provider.py
    Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from quapp_common.config.logging_config import logger
from quapp_common.enum.provider_tag import ProviderTag
from quapp_common.model.provider.provider import Provider

from pyquil import get_qc
from pyquil.api import QuantumComputer


class RigettiPyquilProvider(Provider):
    def __init__(self, ):
        logger.debug('[RigettiPyquilProvider] get_backend()')
        super().__init__(ProviderTag.RIGETTI)

    def get_backend(self, device_specification) -> QuantumComputer:
        logger.debug('[RigettiPyquilProvider] get_backend()')

        try:
            print(device_specification)
            return get_qc(device_specification)
        except Exception as e:
            print(e)
            raise ValueError('[RigettiPyquilProvider] Unsupported device')

    def collect_provider(self):
        logger.debug('[RigettiPyquilProvider] collect_provider()')
        return None