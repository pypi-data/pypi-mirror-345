import wrapt
import logging
import datetime
from revenium_middleware import client, run_async_in_thread, shutdown_event

logger = logging.getLogger("revenium_middleware.extension")


@wrapt.patch_function_wrapper('litellm', 'completion')
def completion_wrapper(wrapped, _, args, kwargs):
    """
    Wraps the litellm.completion method to log token usage.
    Handles both streaming and non-streaming responses.
    """
    logger.debug("LiteLLM completion wrapper called")
    usage_metadata = kwargs.pop("usage_metadata", {}) if "usage_metadata" in kwargs else {}
    logger.debug("Usage metadata: {}".format(usage_metadata))

    request_time_dt = datetime.datetime.now(datetime.timezone.utc)
    logger.debug(f"Calling chat function with args: {args}, kwargs: {kwargs}")

    is_streaming = kwargs.get("stream", False)
    logger.debug(f"is_streaming: {is_streaming}")

    response = wrapped(*args, **kwargs)
    if is_streaming:
        return handle_streaming_response(response, request_time_dt, usage_metadata)
    else:
        return handle_response(response, request_time_dt, usage_metadata, False)


def handle_streaming_response(generator, request_time_dt, usage_metadata):
    """
    Handles streaming responses by collecting all chunks and processing the final state.
    Returns a new generator that yields the same chunks.
    """
    chunks = []
    final_response = None

    def wrapped_generator():
        nonlocal chunks, final_response

        # Collect all chunks
        for chunk in generator:
            chunks.append(chunk)
            yield chunk

        # After all chunks are processed, construct the final response
        if chunks:
            # The last chunk should contain the complete response data
            final_response = chunks[-1]
            handle_response(final_response, request_time_dt, usage_metadata, True)

    return wrapped_generator()


def handle_response(response, request_time_dt, usage_metadata, is_streaming):
    """
    Process a complete response (either streaming or non-streaming) and send metering data.
    """

    async def metering_call():
        response_time_dt = datetime.datetime.now(datetime.timezone.utc)
        response_time = response_time_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        request_duration = (response_time_dt - request_time_dt).total_seconds() * 1000
        request_time = request_time_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

        # Generate a unique ID if not present in response
        response_id = getattr(response, 'id', f"litellm_client-{datetime.datetime.now().timestamp()}")

        # Extract token counts from LiteLLM response
        prompt_tokens = getattr(response.usage, 'prompt_tokens', 0)
        completion_tokens = getattr(response.usage, 'completion_tokens', 0)
        cached_tokens = getattr(response.usage, 'cached_tokens', 0)
        total_tokens = prompt_tokens + completion_tokens + cached_tokens

        logger.debug(
            "LiteLLM completion token usage - prompt: %d, completion: %d, cached: %d, total: %d",
            prompt_tokens, completion_tokens, cached_tokens, total_tokens
        )

        finish_reason = getattr(response, 'finish_reason', None)

        finish_reason_map = {
            "stop": "END",
            "length": "TOKEN_LIMIT",
            "error": "ERROR",
            "cancelled": "CANCELLED",
            "tool_calls": "END_SEQUENCE",
            "function_calls": "END_SEQUENCE"
        }

        stop_reason = finish_reason_map.get(finish_reason, "END")  # type: ignore
        try:
            if shutdown_event.is_set():
                logger.warning("Skipping metering call during shutdown")
                return
            logger.debug("Metering call to Revenium for completion %s", response_id)

            # Prepare arguments for create_completion
            completion_args = {
                "cache_creation_token_count": cached_tokens,
                "cache_read_token_count": 0,
                "output_token_count": completion_tokens,
                "cost_type": "AI",
                "model": getattr(response, 'model', 'litellm-model'),
                "input_token_count": prompt_tokens,
                "provider": "LITELLM",
                "model_source": "LITELLM",
                "reasoning_token_count": 0,
                "request_time": request_time,
                "response_time": response_time,
                "completion_start_time": response_time,
                "request_duration": int(request_duration),
                "stop_reason": stop_reason,
                "total_token_count": total_tokens,
                "transaction_id": response_id,
                "trace_id": usage_metadata.get("trace_id"),
                "task_type": usage_metadata.get("task_type"),
                "subscriber_credential_name": usage_metadata.get("subscriber_credential_name"),
                "subscriber_credential": usage_metadata.get("subscriber_credential"),
                "subscriber_email": usage_metadata.get("subscriber_email"),
                "subscriber_id": usage_metadata.get("subscriber_id"),
                "organization_id": usage_metadata.get("organization_id"),
                "subscription_id": usage_metadata.get("subscription_id"),
                "product_id": usage_metadata.get("product_id"),
                "agent": usage_metadata.get("agent"),
                "is_streamed": is_streaming,
                "system_fingerprint": getattr(response, 'system_fingerprint', None)
            }

            # Log the arguments at debug level
            logger.debug("Arguments for create_completion: %s", completion_args)

            # The client.ai.create_completion method is not async, so don't use await
            result = client.ai.create_completion(**completion_args)
            logger.debug("Metering call result: %s", result)
        except Exception as e:
            if not shutdown_event.is_set():
                logger.warning(f"Error in metering call: {str(e)}")
                # Log the full traceback for better debugging
                import traceback
                logger.warning(f"Traceback: {traceback.format_exc()}")

    logger.debug("Handling LiteLLM response: {}".format(response))
    thread = run_async_in_thread(metering_call())
    logger.debug("Metering thread started: %s", thread)
