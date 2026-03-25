"""
Structured logging configuration using structlog.

Outputs JSON lines to stdout for easy ingestion by log aggregators.
"""

import logging
import sys

import structlog


def setup_logging(service_name: str, log_level: str = "INFO") -> structlog.BoundLogger:
    """
    Configure structured logging with JSON output.
    
    Args:
        service_name: Name of the service for log context
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger instance
    """
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper())
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Get logger with service context
    logger = structlog.get_logger()
    logger = logger.bind(service=service_name)
    
    return logger
