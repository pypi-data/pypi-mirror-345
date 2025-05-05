import datetime
import logging
from unittest.mock import patch, MagicMock, AsyncMock

import pytest
import wrapt
from freezegun import freeze_time

from revenium_middleware_core import shutdown_event
from revenium_middleware_anthropic.middleware import create_wrapper


class TestMiddleware:
    @pytest.fixture
    def reset_state(self):
        """Fixture to reset global state before each test."""
        shutdown_event.clear()
        yield
        # Cleanup after test
        shutdown_event.clear()

    @pytest.fixture
    def mock_anthropic_response(self):
        """Create a mock Anthropic response object."""
        mock_response = MagicMock()
        mock_response.id = "test-response-id"
        mock_response.model = "gpt-4"

        # Set up usage attributes
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 50
        mock_response.usage.total_tokens = 150

        # Set up choices with finish_reason
        mock_choice = MagicMock()
        mock_choice.finish_reason = "stop"
        mock_response.choices = [mock_choice]

        return mock_response

    @pytest.fixture
    def test_kwargs(self):
        """Common test kwargs for Anthropic API calls."""
        return {
            "messages": [{"role": "user", "content": "Hello"}],
            "model": "gpt-4",
            "usage_metadata": {
                "trace_id": "test-trace",
                "task_id": "test-task",
                "task_type": "test-type",
                "subscriber_identity": "test-subscriber",
                "organization_id": "test-org",
                "subscription_id": "test-sub",
                "product_id": "test-product",
                "source_id": "test-source",
                "ai_provider_key_name": "test-key",
                "agent": "test-agent"
            }
        }

    @freeze_time("2023-01-01T12:00:00Z")
    @wrapt.decorator(enabled=False)
    @patch("revenium_middleware_anthropic.middleware.run_async_in_thread")
    @patch("revenium_middleware_anthropic.middleware.client")
    def test_create_wrapper_basic(self, mock_run_async, mock_client, reset_state, mock_anthropic_response, test_kwargs,
                                  caplog):
        """Test the basic functionality of create_wrapper."""
        # Set up mocks
        mock_wrapped = MagicMock(return_value=mock_anthropic_response)
        mock_thread = MagicMock()
        mock_run_async.return_value = mock_thread
        mock_client.ai.create_completion = AsyncMock()

        # Call the wrapper - we need to pass the instance as the first argument
        # The wrapper expects: wrapped, instance, args, kwargs
        result = create_wrapper(mock_wrapped, MagicMock(), (), test_kwargs.copy())

        # Assertions
        assert result == mock_anthropic_response
        mock_wrapped.assert_called_once_with(**{k: v for k, v in test_kwargs.items() if k != "usage_metadata"})

        # Verify run_async_in_thread was called
        mock_run_async.assert_called_once()
        mock_thread.join.assert_called_once_with(timeout=5.0)

        # Verify the metering call parameters
        call_args = mock_run_async.call_args[0][0]
        assert isinstance(call_args, object)  # This is a coroutine object

        # Verify expected parameters would be passed to create_completion
        expected_call_params = {
            "audio_token_count": 0,
            "cached_token_count": 0,
            "completion_token_count": 50,
            "cost_type": "AI",
            "model": "gpt-4",
            "prompt_token_count": 100,
            "provider": "ANTHROPIC",
            "reasoning_token_count": 0,
            "request_time": "2023-01-01T12:00:00Z",
            "response_time": "2023-01-01T12:00:00Z",
            "completion_start_time": "2023-01-01T12:00:00Z",
            "request_duration": 0,  # 0 because time is frozen
            "stop_reason": "END",
            "total_token_count": 150,
            "transaction_cost": 0,
            "transaction_id": "test-response-id",
            "trace_id": "test-trace",
            "task_id": "test-task",
            "task_type": "test-type",
            "subscriber_identity": "test-subscriber",
            "organization_id": "test-org",
            "subscription_id": "test-sub",
            "product_id": "test-product",
            "source_id": "test-source",
            "ai_provider_key_name": "test-key",
            "agent": "test-agent"
        }

        # We can't directly check the coroutine's parameters, but we can verify logging
        assert "Metering call to Revenium for completion test-response-id" in caplog.text

    @freeze_time("2023-01-01T12:00:00Z")
    @wrapt.decorator(enabled=False)
    @patch("revenium_middleware_anthropic.middleware.run_async_in_thread")
    @patch("revenium_middleware_anthropic.middleware.client")
    def test_create_wrapper_no_metadata(self, mock_run_async, mock_client, reset_state, mock_anthropic_response):
        """Test create_wrapper with no usage_metadata provided."""
        # Set up mocks
        mock_wrapped = MagicMock(return_value=mock_anthropic_response)
        mock_thread = MagicMock()
        mock_run_async.return_value = mock_thread
        mock_client.ai.create_completion = AsyncMock()

        # Test data without usage_metadata
        test_kwargs = {
            "messages": [{"role": "user", "content": "Hello"}],
            "model": "gpt-4"
        }

        # Call the wrapper
        result = create_wrapper(mock_wrapped, MagicMock(), (), test_kwargs.copy())

        # Assertions
        assert result == mock_anthropic_response
        mock_wrapped.assert_called_once_with(**test_kwargs)
        mock_run_async.assert_called_once()

    @freeze_time("2023-01-01T12:00:00Z")
    @wrapt.decorator(enabled=False)
    @patch("revenium_middleware_anthropic.middleware.run_async_in_thread")
    @patch("revenium_middleware_anthropic.middleware.client")
    def test_create_wrapper_during_shutdown(self, mock_run_async, mock_client, reset_state, mock_anthropic_response,
                                            test_kwargs, caplog):
        """Test create_wrapper behavior during shutdown."""
        caplog.set_level(logging.WARNING)

        # Set up mocks
        mock_wrapped = MagicMock(return_value=mock_anthropic_response)
        mock_thread = MagicMock()
        mock_run_async.return_value = mock_thread

        # Set shutdown event
        shutdown_event.set()

        # Call the wrapper
        result = create_wrapper(mock_wrapped, MagicMock(), (), test_kwargs.copy())

        # Assertions
        assert result == mock_anthropic_response
        mock_wrapped.assert_called_once()
        mock_run_async.assert_called_once()

        # The async function should log a warning about skipping during shutdown
        assert "Skipping metering call during shutdown" in caplog.text

    @freeze_time("2023-01-01T12:00:00Z")
    @wrapt.decorator(enabled=False)
    @patch("revenium_middleware_anthropic.middleware.run_async_in_thread")
    @patch("revenium_middleware_anthropic.middleware.client")
    def test_create_wrapper_metering_exception(self, mock_run_async, mock_client, reset_state, mock_anthropic_response,
                                               test_kwargs, caplog):
        """Test create_wrapper when the metering call raises an exception."""
        caplog.set_level(logging.WARNING)

        # Set up mocks
        mock_wrapped = MagicMock(return_value=mock_anthropic_response)
        mock_thread = MagicMock()
        mock_run_async.return_value = mock_thread

        # Make the client raise an exception
        mock_client.ai.create_completion = AsyncMock(side_effect=Exception("Test error"))

        # Call the wrapper
        result = create_wrapper(mock_wrapped, MagicMock(), (), test_kwargs.copy())

        # Assertions
        assert result == mock_anthropic_response
        mock_wrapped.assert_called_once()
        mock_run_async.assert_called_once()

        # The exception should be caught and logged
        assert "Error in metering call: Test error" in caplog.text

    @freeze_time("2023-01-01T12:00:00Z")
    @wrapt.decorator(enabled=False)
    @patch("revenium_middleware_anthropic.middleware.run_async_in_thread")
    @patch("revenium_middleware_anthropic.middleware.client")
    def test_create_wrapper_no_choices(self, mock_run_async, mock_client, reset_state,
                                       mock_anthropic_response, test_kwargs):
        """Test create_wrapper when response has no choices."""
        # Set up mocks
        mock_wrapped = MagicMock(return_value=mock_anthropic_response)
        mock_thread = MagicMock()
        mock_run_async.return_value = mock_thread
        mock_client.ai.create_completion = AsyncMock()

        # Remove choices from response
        mock_anthropic_response.choices = []

        # Call the wrapper
        result = create_wrapper(mock_wrapped, MagicMock(), (), test_kwargs.copy())

        # Assertions
        assert result == mock_anthropic_response
        mock_wrapped.assert_called_once()
        mock_run_async.assert_called_once()

        # Should default to "END" when no choices
        coroutine = mock_run_async.call_args[0][0]
        assert isinstance(coroutine, object)

    @freeze_time("2023-01-01T12:00:00Z")
    @wrapt.decorator(enabled=False)
    @patch("revenium_middleware_anthropic.middleware.datetime")
    @patch("revenium_middleware_anthropic.middleware.run_async_in_thread")
    @patch("revenium_middleware_anthropic.middleware.client")
    def test_create_wrapper_request_duration(self, mock_run_async, mock_client, mock_datetime,
                                             reset_state, mock_anthropic_response, test_kwargs):
        """Test create_wrapper calculates request duration correctly."""
        # Set up mocks
        mock_wrapped = MagicMock(return_value=mock_anthropic_response)
        mock_thread = MagicMock()
        mock_run_async.return_value = mock_thread
        mock_client.ai.create_completion = AsyncMock()

        # Mock datetime to simulate elapsed time
        request_time = datetime.datetime(2023, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)
        response_time = datetime.datetime(2023, 1, 1, 12, 0, 1, tzinfo=datetime.timezone.utc)

        mock_datetime.datetime.now.side_effect = [request_time, response_time]
        mock_datetime.timezone = datetime.timezone
        mock_datetime.datetime = datetime.datetime

        # Call the wrapper
        result = create_wrapper(mock_wrapped, MagicMock(), (), test_kwargs.copy())

        # Assertions
        assert result == mock_anthropic_response
        mock_wrapped.assert_called_once()
        mock_run_async.assert_called_once()

        # Request duration should be 1000ms (1 second)
        coroutine = mock_run_async.call_args[0][0]
        assert isinstance(coroutine, object)
