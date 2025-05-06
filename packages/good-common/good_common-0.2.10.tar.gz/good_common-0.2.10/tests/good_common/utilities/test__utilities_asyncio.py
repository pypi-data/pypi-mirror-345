import pytest
import asyncio
import time
from unittest.mock import patch, MagicMock
from good_common.utilities._asyncio import (
    run_async,
    retry_async,
    gather_with_concurrency,
    timeout_scope,
    AsyncBatcher,
    periodic,
    AsyncRateLimiter,
)


def test_run_async_with_existing_loop():
    def sample_function():
        return "Hello, World!"

    with patch("asyncio.get_event_loop") as mock_get_loop:
        mock_loop = MagicMock()
        mock_loop.run_until_complete.return_value = "Hello, World!"
        mock_get_loop.return_value = mock_loop

        result = run_async(sample_function())

        mock_get_loop.assert_called_once()
        mock_loop.run_until_complete.assert_called_once()
        assert result == "Hello, World!"


def test_run_async_without_existing_loop():
    def sample_function():
        return "Hello, World!"

    with (
        patch("asyncio.get_event_loop", side_effect=[RuntimeError, MagicMock()]),
        patch("asyncio.new_event_loop") as mock_new_loop,
        patch("asyncio.set_event_loop") as mock_set_loop,
    ):
        mock_loop = MagicMock()
        mock_loop.run_until_complete.return_value = "Hello, World!"
        mock_new_loop.return_value = mock_loop

        result = run_async(sample_function())

        mock_new_loop.assert_called_once()
        mock_set_loop.assert_called_once_with(mock_loop)
        mock_loop.run_until_complete.assert_called_once()
        assert result == "Hello, World!"


def test_run_async_in_jupyter():
    def sample_function():
        return "Hello, Jupyter!"

    with (
        patch.dict("sys.modules", {"IPython": MagicMock()}),
        patch("nest_asyncio.apply") as mock_apply,
        patch("asyncio.get_event_loop") as mock_get_loop,
    ):
        mock_loop = MagicMock()
        mock_loop.run_until_complete.return_value = "Hello, Jupyter!"
        mock_get_loop.return_value = mock_loop

        result = run_async(sample_function())

        mock_apply.assert_called_once()
        assert result == "Hello, Jupyter!"


def test_run_async_with_exception():
    def sample_function():
        raise ValueError("Test exception")

    with patch("asyncio.get_event_loop") as mock_get_loop:
        mock_loop = MagicMock()
        mock_loop.run_until_complete.side_effect = ValueError("Test exception")
        mock_get_loop.return_value = mock_loop

        with pytest.raises(ValueError, match="Test exception"):
            run_async(sample_function())


def test_run_async_with_real_coroutine():
    async def sample_coroutine():
        await asyncio.sleep(0.1)
        return "Hello, Async World!"

    # Create a new event loop for this test
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        result = run_async(sample_coroutine())
        assert result == "Hello, Async World!"
    finally:
        # Clean up the event loop
        loop.close()


# Helper functions and fixtures
async def sleep_and_return(value: int, sleep_time: float = 0.1) -> int:
    await asyncio.sleep(sleep_time)
    return value


class TestRetryAsync:
    @pytest.mark.asyncio
    async def test_successful_execution(self):
        counter = 0

        @retry_async(retries=3)
        async def success():
            nonlocal counter
            counter += 1
            return "success"

        result = await success()
        assert result == "success"
        assert counter == 1  # Should only execute once

    @pytest.mark.asyncio
    async def test_retry_on_failure(self):
        attempts = 0

        @retry_async(retries=3, delay=0.1)
        async def fail_twice():
            nonlocal attempts
            attempts += 1
            if attempts < 3:
                raise ValueError("Temporary failure")
            return "success"

        result = await fail_twice()
        assert result == "success"
        assert attempts == 3

    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self):
        @retry_async(retries=2, delay=0.1)
        async def always_fail():
            raise ValueError("Always fails")

        with pytest.raises(ValueError):
            await always_fail()


class TestGatherWithConcurrency:
    @pytest.mark.asyncio
    async def test_concurrency_limit(self):
        start_time = time.time()
        tasks = [sleep_and_return(i, 0.1) for i in range(4)]

        # With concurrency of 2, should take about 0.2 seconds
        results = await gather_with_concurrency(2, *tasks)

        duration = time.time() - start_time
        assert 0.2 <= duration <= 0.3  # Allow some margin
        assert results == list(range(4))

    @pytest.mark.asyncio
    async def test_error_propagation(self):
        async def fail():
            raise ValueError("Task failed")

        tasks = [sleep_and_return(1), fail(), sleep_and_return(2)]

        with pytest.raises(ValueError):
            await gather_with_concurrency(2, *tasks)


class TestTimeoutScope:
    @pytest.mark.asyncio
    async def test_completion_within_timeout(self):
        async def fast_operation():
            await asyncio.sleep(0.1)
            return "done"

        async with timeout_scope(1.0):
            result = await fast_operation()
            assert result == "done"

    @pytest.mark.asyncio
    async def test_timeout_with_cleanup(self):
        cleanup_called = False

        async def cleanup():
            nonlocal cleanup_called
            cleanup_called = True

        async def slow_operation():
            await asyncio.sleep(0.2)

        with pytest.raises(asyncio.TimeoutError):
            async with timeout_scope(0.1, cleanup):
                await slow_operation()

        assert cleanup_called


class TestAsyncBatcher:
    @pytest.mark.asyncio
    async def test_batch_size_trigger(self):
        # Create a class to hold our state
        class BatchState:
            def __init__(self):
                self.processed_batches: list[list[int]] = []

            async def process_batch(self, items):
                self.processed_batches.append(items)

        state = BatchState()

        async with AsyncBatcher(batch_size=3, processor=state.process_batch) as batcher:
            # Add items one by one
            for i in range(5):
                await batcher.add(i)
                # Allow time for processing
                await asyncio.sleep(0.05)

            # First batch should be processed automatically when size = 3 was reached
            assert len(state.processed_batches) >= 1, (
                f"Got batches: {state.processed_batches}"
            )
            assert state.processed_batches[0] == [0, 1, 2]

            # Let context manager cleanup process remaining items

        # Verify final state after context exit
        assert len(state.processed_batches) == 2, (
            f"Got batches: {state.processed_batches}"
        )
        assert state.processed_batches[0] == [0, 1, 2]
        assert state.processed_batches[1] == [3, 4]

    @pytest.mark.asyncio
    async def test_timeout_trigger(self):
        processed_batches: list[list[int]] = []

        async def process_batch(items):
            processed_batches.append(items)

        async with AsyncBatcher(
            batch_size=5, processor=process_batch, timeout=0.1
        ) as batcher:
            # Add first item
            await batcher.add(1)

            # Wait for timeout - should trigger processing of first item
            await asyncio.sleep(0.15)

            # Verify first batch was processed due to timeout
            assert len(processed_batches) == 1
            assert processed_batches[0] == [1]

            # Add second item
            await batcher.add(2)

            # Let it process at context exit

        # Verify second item was processed
        assert len(processed_batches) == 2
        assert processed_batches[0] == [1]


class TestPeriodic:
    @pytest.mark.asyncio
    async def test_periodic_execution(self):
        counter = 0

        async def increment():
            nonlocal counter
            counter += 1

        gen = periodic(0.1, increment)
        async for interval in gen:
            if counter >= 3:
                break
            assert 0.08 <= interval <= 0.12

        assert counter == 3

    @pytest.mark.asyncio
    async def test_max_delay_skip(self):
        """Test that periodic skips iterations when max_delay is exceeded"""
        executions = []
        delay_triggered = False

        async def record_time():
            executions.append(time.time())

        gen = periodic(0.1, record_time, max_delay=0.15)

        # Run for a few iterations
        for _ in range(3):
            if len(executions) == 2:
                # After 2 executions, introduce a delay
                await asyncio.sleep(0.2)
                delay_triggered = True
            try:
                interval = await gen.__anext__()
                if delay_triggered:
                    # If we got here after the delay, the interval should be large
                    assert interval > 0.15
                    break
            except StopAsyncIteration:
                break

        assert len(executions) >= 2
        assert delay_triggered


class TestAsyncRateLimiter:
    @pytest.mark.asyncio
    async def test_rate_limiting(self):
        limiter = AsyncRateLimiter(rate=10, burst=1)  # 10 ops/second
        start_time = time.time()

        for _ in range(5):
            await limiter.acquire()

        duration = time.time() - start_time
        assert (
            duration >= 0.4
        )  # Should take at least 0.4 seconds for 5 operations at 10 ops/second

    @pytest.mark.asyncio
    async def test_burst_capacity(self):
        limiter = AsyncRateLimiter(rate=10, burst=3)
        start_time = time.time()

        # First 3 operations should be immediate due to burst capacity
        for _ in range(3):
            await limiter.acquire()

        duration = time.time() - start_time
        assert duration < 0.1  # Should be nearly instant
