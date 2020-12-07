"""
This module should contain all common json based operations
"""
import json
import logging

logger = logging.getLogger(__name__)


def write(filepath, content: dict) -> None:
    """
    Write a json file
    :param filepath: Path create
    :param content: content of the created file
    :return: None
    """
    logger.info("Writing in file %s", filepath)
    with open(filepath, mode="w") as f:
        json.dump(content, f)
