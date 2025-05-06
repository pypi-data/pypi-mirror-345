"""
See https://github.com/Zhaopudark/pandoc-filter for documentation.
"""
import logging

from . import filters

from .scripts import run_filters_pyio

from .version import __version__

from .utils.logging_helper import TracingLogger

logger = TracingLogger("./logs/pandoc_filter_log",level=logging.DEBUG)