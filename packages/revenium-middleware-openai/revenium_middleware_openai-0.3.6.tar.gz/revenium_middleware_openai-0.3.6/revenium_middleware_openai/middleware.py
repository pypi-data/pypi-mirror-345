import datetime
import logging
from typing import Dict, Any, Optional

import wrapt
from revenium_middleware import client, run_async_in_thread, shutdown_event

logger = logging.getLogger("revenium_middleware.extension")


# Utility functions for token usage tracking
def get_stop_reason(openai_finish_reason: Optional[str]) -> str:
    """Map OpenAI finish reasons to Revenium stop reasons."""
    finish_reason_map = {
        "stop": "END",
        "function_call": "END_SEQUENCE",
        "timeout": "TIMEOUT",
        "length": "TOKEN_LIMIT",
        "content_filter": "ERROR"
    }
    return finish_reason_map.get(openai_finish_reason or "", "END")


async def log_token_usage(
        response_id: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
        cached_tokens: int,
        stop_reason: str,
        request_time: str,
        response_time: str,
        request_duration: int,
        usage_metadata: Dict[str, Any],
        system_fingerprint: Optional[str] = None,
        is_streamed: bool = False,
        time_to_first_token: int = 0
) -> None:
    """Log token usage to Revenium."""
    if shutdown_event.is_set():
        logger.warning("Skipping metering call during shutdown")
        return

    logger.debug("Metering call to Revenium for completion %s", response_id)

    # Determine provider based on system fingerprint
    provider = "OLLAMA" if system_fingerprint == "fp_ollama" else "OPENAI"
    logger.debug(f"Determined provider: {provider} based on system_fingerprint: {system_fingerprint}")

    # Prepare arguments for create_completion
    completion_args = {
        "cache_creation_token_count": cached_tokens,
        "cache_read_token_count": 0,
        "input_token_cost": 0.0,
        "output_token_cost": 0.0,
        "total_cost": 0.0,
        "output_token_count": completion_tokens,
        "cost_type": "AI",
        "model": model,
        "input_token_count": prompt_tokens,
        "provider": provider,
        "model_source": provider,
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
        "response_quality_score": usage_metadata.get("response_quality_score"),
        "is_streamed": is_streamed,
        "operation_type": "CHAT",
        "time_to_first_token": time_to_first_token
    }

    # Log the arguments at debug level
    logger.debug("Calling client.ai.create_completion with args: %s", completion_args)

    try:
        # The client.ai.create_completion method is not async, so don't use await
        result = client.ai.create_completion(**completion_args)
        logger.debug("Metering call result: %s", result)
    except Exception as e:
        if not shutdown_event.is_set():
            logger.warning(f"Error in metering call: {str(e)}")
            # Log the full traceback for better debugging
            import traceback
            logger.warning(f"Traceback: {traceback.format_exc()}")


@wrapt.patch_function_wrapper('openai.resources.chat.completions', 'Completions.create')
def create_wrapper(wrapped, _, args, kwargs):
    """
    Wraps the openai.ChatCompletion.create method to log token usage.
    Handles both streaming and non-streaming responses.
    """
    logger.debug("OpenAI chat.completions.create wrapper called")

    # Extract usage metadata and store it for later use
    usage_metadata = kwargs.pop("usage_metadata", {})

    # Check if this is a streaming request
    stream = kwargs.get('stream', False)

    # If streaming, add stream_options to include usage information
    if stream:
        # Initialize stream_options if it doesn't exist
        if 'stream_options' not in kwargs:
            kwargs['stream_options'] = {}
        # Add include_usage flag to get token counts in the response
        kwargs['stream_options']['include_usage'] = True
        logger.debug("Added include_usage to stream_options for accurate token counting in streaming response")

    # Record request time
    request_time_dt = datetime.datetime.now(datetime.timezone.utc)
    request_time = request_time_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    logger.debug(f"Calling wrapped function with args: {args}, kwargs: {kwargs}")

    # Call the original OpenAI function
    response = wrapped(*args, **kwargs)

    # Record time to first token (for non-streaming, this is the same as the full response time)
    first_token_time_dt = datetime.datetime.now(datetime.timezone.utc)
    time_to_first_token = int((first_token_time_dt - request_time_dt).total_seconds() * 1000)

    # Handle based on response type
    if stream:
        # For streaming responses (openai.Stream)
        logger.debug("Handling streaming response")
        return handle_streaming_response(
            response,
            request_time_dt,
            usage_metadata
        )
    else:
        # For non-streaming responses (ChatCompletion)
        logger.debug("Handling non-streaming response: %s", response)
        response_time_dt = datetime.datetime.now(datetime.timezone.utc)
        response_time = response_time_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        request_duration = (response_time_dt - request_time_dt).total_seconds() * 1000

        # Extract token usage information
        response_id = response.id
        prompt_tokens = response.usage.prompt_tokens
        completion_tokens = response.usage.completion_tokens
        total_tokens = response.usage.total_tokens
        cached_tokens = getattr(response.usage.prompt_tokens_details, 'cached_tokens', 0) if hasattr(response.usage,
                                                                                                     'prompt_tokens_details') else 0
        system_fingerprint = getattr(response, 'system_fingerprint', None)

        logger.debug(
            "OpenAI client.ai.create_completion token usage - prompt: %d, completion: %d, total: %d, system_fingerprint: %s",
            prompt_tokens, completion_tokens, total_tokens, system_fingerprint
        )

        # Determine finish reason
        openai_finish_reason = None
        if response.choices:
            openai_finish_reason = response.choices[0].finish_reason
        stop_reason = get_stop_reason(openai_finish_reason)

        # Create and run the metering call in a separate thread
        async def metering_call():
            await log_token_usage(
                response_id=response_id,
                model=response.model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                cached_tokens=cached_tokens,
                stop_reason=stop_reason,
                request_time=request_time,
                response_time=response_time,
                request_duration=int(request_duration),
                usage_metadata=usage_metadata,
                system_fingerprint=system_fingerprint,
                is_streamed=False,
                time_to_first_token=time_to_first_token,
            )

        thread = run_async_in_thread(metering_call())
        logger.debug("Metering thread started: %s", thread)
        return response


def handle_streaming_response(stream, request_time_dt, usage_metadata):
    """
    Handle streaming responses from OpenAI.
    Wraps the stream to collect metrics and log them after completion.
    Similar to the approach used in the Ollama middleware.
    """

    # Create a wrapper for the streaming response
    class StreamWrapper:
        def __init__(self, stream):
            self.stream = stream
            self.chunks = []
            self.response_id = None
            self.model = None
            self.finish_reason = None
            self.system_fingerprint = None
            self.request_time_dt = request_time_dt
            self.usage_metadata = usage_metadata
            self.final_usage = None
            self.completion_text = ""
            self.first_token_time = None

        def __iter__(self):
            return self

        def __next__(self):
            try:
                chunk = next(self.stream)
                self._process_chunk(chunk)
                return chunk
            except StopIteration:
                self._log_usage()
                raise

        def _process_chunk(self, chunk):
            # Extract response ID and model from the chunk if available
            if self.response_id is None and hasattr(chunk, 'id'):
                self.response_id = chunk.id
            if self.model is None and hasattr(chunk, 'model'):
                self.model = chunk.model
            if self.system_fingerprint is None and hasattr(chunk, 'system_fingerprint'):
                self.system_fingerprint = chunk.system_fingerprint
                logger.debug(f"Captured system_fingerprint from stream chunk: {self.system_fingerprint}")
            else:
                logger.debug(f"System fingerprint already set: {self.system_fingerprint}")


            # Check for finish reason in the chunk
            if chunk.choices and chunk.choices[0].finish_reason:
                self.finish_reason = chunk.choices[0].finish_reason

            # Check if this is the special usage chunk (last chunk with empty choices array)
            if hasattr(chunk, 'usage') and chunk.usage and (not chunk.choices or len(chunk.choices) == 0):
                logger.debug(f"Found usage data in final chunk: {chunk.usage}")
                self.final_usage = chunk.usage
                return

            # Collect content for token estimation if needed
            if chunk.choices and hasattr(chunk.choices[0], 'delta') and hasattr(chunk.choices[0].delta, 'content') and \
                    chunk.choices[0].delta.content:
                # Record time of first token if not already set
                if self.first_token_time is None:
                    self.first_token_time = datetime.datetime.now(datetime.timezone.utc)
                self.completion_text += chunk.choices[0].delta.content

            # Store the chunk for later analysis
            self.chunks.append(chunk)

        def _log_usage(self):
            if not self.chunks:
                return

            # Record response time and calculate duration
            response_time_dt = datetime.datetime.now(datetime.timezone.utc)
            response_time = response_time_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            request_duration = (response_time_dt - self.request_time_dt).total_seconds() * 1000

            # Get token usage information
            prompt_tokens = 0
            completion_tokens = 0
            total_tokens = 0
            cached_tokens = 0

            # First check if we have the final usage data from the special chunk
            if self.final_usage:
                prompt_tokens = self.final_usage.prompt_tokens
                completion_tokens = self.final_usage.completion_tokens
                total_tokens = self.final_usage.total_tokens
                # Check if we have cached tokens info
                if hasattr(self.final_usage, 'prompt_tokens_details') and hasattr(
                        self.final_usage.prompt_tokens_details, 'cached_tokens'):
                    cached_tokens = self.final_usage.prompt_tokens_details.cached_tokens
                logger.debug(
                    f"Using token usage from final chunk: prompt={prompt_tokens}, completion={completion_tokens}, total={total_tokens}")
            else:
                # If we don't have usage data, estimate from content
                logger.warning("No usage data found in streaming response!")

            stop_reason = get_stop_reason(self.finish_reason)

            # Log the token usage
            if self.response_id:
                logger.debug(
                    "Streaming token usage - response_id: %s, prompt: %d, completion: %d, total: %d",
                    self.response_id, prompt_tokens, completion_tokens, total_tokens
                )

                # Calculate time to first token if available
                time_to_first_token = 0
                if self.first_token_time:
                    time_to_first_token = int((self.first_token_time - self.request_time_dt).total_seconds() * 1000)
                    logger.debug(f"Time to first token: {time_to_first_token}ms")

                async def metering_call():
                    await log_token_usage(
                        response_id=self.response_id,
                        model=self.model or "unknown",
                        prompt_tokens=prompt_tokens,
                        completion_tokens=completion_tokens,
                        total_tokens=total_tokens,
                        cached_tokens=cached_tokens,
                        stop_reason=stop_reason,
                        request_time=self.request_time_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        response_time=response_time,
                        request_duration=int(request_duration),
                        usage_metadata=self.usage_metadata,
                        system_fingerprint=self.system_fingerprint,
                        is_streamed=True,
                        time_to_first_token=time_to_first_token
                    )

                thread = run_async_in_thread(metering_call())
                logger.debug("Streaming metering thread started: %s", thread)

    # Return the wrapped stream
    return StreamWrapper(iter(stream))
