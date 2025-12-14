"""Data sources package."""

from sentinel.data_sources.base import DataSource
from sentinel.data_sources.mock import MockDataSource

__all__ = ["DataSource", "MockDataSource"]
