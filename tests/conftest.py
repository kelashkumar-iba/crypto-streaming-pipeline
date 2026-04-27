"""Shared pytest fixtures and module-level mocks."""

import sys
from unittest.mock import MagicMock

# Mock the kafka library before any test imports producer/consumer.
# Tests don't need real Kafka — they test pure logic.
sys.modules["kafka"] = MagicMock()
sys.modules["kafka.KafkaProducer"] = MagicMock()
sys.modules["kafka.KafkaConsumer"] = MagicMock()

# Same for psycopg2 (consumer imports it at module level)
sys.modules["psycopg2"] = MagicMock()
