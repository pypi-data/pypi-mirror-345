import logging
import datetime
import wrapt
from revenium_middleware import client, run_async_in_thread, shutdown_event
import time
import contextvars

logger = logging.getLogger("revenium_middleware.extension")

usage_context = contextvars.ContextVar("usage_metadata", default={})


@wrapt.patch_function_wrapper('anthropic.resources.messages', 'Messages.create')
def create_wrapper(wrapped, _, args, kwargs):
    """
    Wraps the anthropic.ChatCompletion.create method to log token usage.
    """
    logger.debug("Anthropic client.messages.create wrapper called: %s: %s", wrapped, args)
    usage_metadata = kwargs.pop("usage_metadata", {})
    logger.debug("Usage metadata: %s", usage_metadata)

    request_time_dt = datetime.datetime.now(datetime.timezone.utc)
    request_time = request_time_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    logger.debug(f"Calling wrapped function with args: {args}, kwargs: {kwargs}")

    response = wrapped(*args, **kwargs)
    logger.debug(
        "Anthropic client.messages.create response: %s",
        response)
    response_time_dt = datetime.datetime.now(datetime.timezone.utc)
    response_time = response_time_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    request_duration = (response_time_dt - request_time_dt).total_seconds() * 1000
    response_id = response.id

    prompt_tokens = response.usage.input_tokens
    completion_tokens = response.usage.output_tokens
    cache_creation_input_tokens = response.usage.cache_creation_input_tokens
    cache_read_input_tokens = response.usage.cache_read_input_tokens

    logger.debug(
        "Anthropic client.ai.create_completion token usage - prompt: %d, completion: %d, "
        "cache_creation_input_tokens: %d,cache_read_input_tokens: %d",
        prompt_tokens, completion_tokens, cache_creation_input_tokens, cache_read_input_tokens
    )

    anthropic_finish_reason = None
    if response.stop_reason:
        anthropic_finish_reason = response.stop_reason

    finish_reason_map = {
        "end_turn": "END",
        "tool_use": "END_SEQUENCE",
        "max_tokens": "TOKEN_LIMIT",
        "content_filter": "ERROR"
    }
    stop_reason = finish_reason_map.get(anthropic_finish_reason, "end_turn")  # type: ignore

    async def metering_call():
        try:
            if shutdown_event.is_set():
                logger.warning("Skipping metering call during shutdown")
                return
            logger.debug("Metering call to Revenium for completion %s with usage_metadata: %s", response_id,
                         usage_metadata)
            result = client.ai.create_completion(
                cache_creation_token_count=cache_creation_input_tokens,
                cache_read_token_count=cache_read_input_tokens,
                input_token_cost=0.0,
                output_token_cost=0.0,
                total_cost=0.0,
                output_token_count=completion_tokens,
                cost_type="AI",
                model=response.model,
                input_token_count=prompt_tokens,
                provider="ANTHROPIC",
                model_source="ANTHROPIC",
                reasoning_token_count=0,
                request_time=request_time,
                response_time=response_time,
                completion_start_time=response_time,
                request_duration=int(request_duration),
                time_to_first_token=int(request_duration),  # For non-streaming, use the full request duration
                stop_reason=stop_reason,
                total_token_count=prompt_tokens + completion_tokens,
                transaction_id=response_id,
                trace_id=usage_metadata.get("trace_id"),
                task_type=usage_metadata.get("task_type"),
                subscriber_credential_name=usage_metadata.get("subscriber_credential_name"),
                subscriber_credential=usage_metadata.get("subscriber_credential"),
                subscriber_email=usage_metadata.get("subscriber_email"),
                subscriber_id=usage_metadata.get("subscriber_id"),
                organization_id=usage_metadata.get("organization_id"),
                subscription_id=usage_metadata.get("subscription_id"),
                product_id=usage_metadata.get("product_id"),
                agent=usage_metadata.get("agent"),
                response_quality_score=usage_metadata.get("response_quality_score"),
                is_streamed=False,
                operation_type="CHAT",
            )
            logger.debug("Metering call result: %s", result)
        except Exception as e:
            if not shutdown_event.is_set():
                logger.warning(f"Error in metering call: {str(e)}")
                # Log the full traceback for better debugging
                import traceback
                logger.warning(f"Traceback: {traceback.format_exc()}")

    thread = run_async_in_thread(metering_call())
    logger.debug("Metering thread started: %s", thread)
    return response


@wrapt.patch_function_wrapper('anthropic.resources.messages', 'Messages.stream')
def stream_wrapper(wrapped, _, args, kwargs):
    """
    Wraps the anthropic.resources.messages.Messages.stream method to log token usage.
    Extracts usage data from the final message of the stream.
    """
    logger.debug("Anthropic client.messages.stream wrapper called")
    usage_metadata = usage_context.get()
    logger.debug("Usage metadata: %s", usage_metadata)

    request_time_dt = datetime.datetime.now(datetime.timezone.utc)
    request_time = request_time_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    logger.debug(f"Calling wrapped stream function with args: {args}, kwargs: {kwargs}")

    stream = wrapped(*args, **kwargs)

    # Create a wrapper for the stream that will capture the final message
    class StreamWrapper:
        def __init__(self, stream):
            self.stream = stream
            self.response_time_dt = None
            self.response_id = None
            self.collected_content = []
            self.final_message = None
            self.first_token_time = None
            self.request_start_time = time.time() * 1000  # Convert to milliseconds

        def __enter__(self):
            self.stream_context = self.stream.__enter__()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            result = self.stream.__exit__(exc_type, exc_val, exc_tb)

            # Get the final message with usage information
            try:
                self.final_message = self.stream_context.get_final_message()
                self.response_time_dt = datetime.datetime.now(datetime.timezone.utc)
                self.response_time = self.response_time_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
                request_duration = (self.response_time_dt - request_time_dt).total_seconds() * 1000

                self.response_id = self.final_message.id

                prompt_tokens = self.final_message.usage.input_tokens
                completion_tokens = self.final_message.usage.output_tokens
                cache_creation_input_tokens = self.final_message.usage.cache_creation_input_tokens
                cache_read_input_tokens = self.final_message.usage.cache_read_input_tokens

                logger.debug(
                    "Anthropic client.messages.stream token usage - prompt: %d, completion: %d, "
                    "cache_creation_input_tokens: %d, cache_read_input_tokens: %d",
                    prompt_tokens, completion_tokens, cache_creation_input_tokens, cache_read_input_tokens
                )

                anthropic_finish_reason = None
                if self.final_message.stop_reason:
                    anthropic_finish_reason = self.final_message.stop_reason

                finish_reason_map = {
                    "end_turn": "END",
                    "tool_use": "END_SEQUENCE",
                    "max_tokens": "TOKEN_LIMIT",
                    "content_filter": "ERROR"
                }
                stop_reason = finish_reason_map.get(anthropic_finish_reason, "end_turn")  # type: ignore

                async def metering_call():
                    try:
                        if shutdown_event.is_set():
                            logger.warning("Skipping metering call during shutdown")
                            return
                        logger.debug("Metering call to Revenium for stream completion %s", self.response_id)
                        result = client.ai.create_completion(
                            cache_creation_token_count=cache_creation_input_tokens,
                            cache_read_token_count=cache_read_input_tokens,
                            input_token_cost=0.0,
                            output_token_cost=0.0,
                            total_cost=0.0,
                            output_token_count=completion_tokens,
                            cost_type="AI",
                            model=self.final_message.model,
                            input_token_count=prompt_tokens,
                            provider="ANTHROPIC",
                            model_source="ANTHROPIC",
                            reasoning_token_count=0,
                            request_time=request_time,
                            response_time=self.response_time,
                            completion_start_time=self.response_time,
                            request_duration=int(request_duration),
                            time_to_first_token=int(
                                self.first_token_time - self.request_start_time) if self.first_token_time else 0,
                            stop_reason=stop_reason,
                            total_token_count=prompt_tokens + completion_tokens,
                            transaction_id=self.response_id,
                            trace_id=usage_metadata.get("trace_id"),
                            task_type=usage_metadata.get("task_type"),
                            subscriber_credential_name = usage_metadata.get("subscriber_credential_name"),
                            subscriber_credential=usage_metadata.get("subscriber_credential"),
                            subscriber_email=usage_metadata.get("subscriber_email"),
                            subscriber_id=usage_metadata.get("subscriber_id"),
                            organization_id=usage_metadata.get("organization_id"),
                            subscription_id=usage_metadata.get("subscription_id"),
                            product_id=usage_metadata.get("product_id"),
                            agent=usage_metadata.get("agent"),
                            is_streamed=True,
                            operation_type="CHAT",
                            response_quality_score=usage_metadata.get("response_quality_score"),
                        )
                        logger.debug("Metering call result for stream: %s", result)
                    except Exception as e:
                        if not shutdown_event.is_set():
                            logger.warning(f"Error in metering call for stream: {str(e)}")
                            # Log the full traceback for better debugging
                            import traceback
                            logger.warning(f"Traceback: {traceback.format_exc()}")

                thread = run_async_in_thread(metering_call())
                logger.debug("Metering thread started for stream: %s", thread)

            except Exception as e:
                logger.warning(f"Error processing final message from stream: {str(e)}")
                import traceback
                logger.warning(f"Traceback: {traceback.format_exc()}")

            return result

        @property
        def text_stream(self):
            # Create a wrapper for the text_stream that doesn't consume it
            original_text_stream = self.stream_context.text_stream
            wrapper_self = self

            class TextStreamWrapper:
                def __iter__(self):
                    return self

                def __next__(self):
                    try:
                        chunk = next(original_text_stream)
                        # Record the time of the first token
                        if wrapper_self.first_token_time is None and chunk:
                            wrapper_self.first_token_time = time.time() * 1000  # Convert to milliseconds
                        return chunk
                    except StopIteration:
                        raise

            return TextStreamWrapper()

        def get_final_message(self):
            if self.final_message:
                return self.final_message
            return self.stream_context.get_final_message()

        def __getattr__(self, name):
            return getattr(self.stream_context, name)

    return StreamWrapper(stream)
