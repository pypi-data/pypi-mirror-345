from loguru import logger
import sys
import json
from eth_utils import to_checksum_address


def init_evm_address(addr: str):
    return to_checksum_address(addr)


def set_log_level(level: str):
    logger.remove()
    logger.add(sys.stdout, level=level.upper())


def normalize_json(data):
    return json.dumps(data, sort_keys=True, indent=4, separators=(',', ':'))


if __name__ == '__main__':
    set_log_level("INFO")

    logger.info("info")
    logger.debug("debug")
    logger.error("error")
    logger.warning("warning")

    logger.info(
        to_checksum_address('0xB1256D6b31E4Ae87DA1D56E5890C66be7f1C038e'))
