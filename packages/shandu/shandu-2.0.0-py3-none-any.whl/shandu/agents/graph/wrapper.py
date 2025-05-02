"""
Wrapper functions to handle async functions in LangGraph nodes.
This module provides thread-safe handling of asyncio event loops.
"""
import asyncio
import threading
from typing import Callable, Any, Awaitable, TypeVar, Dict
from concurrent.futures import ThreadPoolExecutor

T = TypeVar('T')

# Thread-local storage for per-thread event loops
_thread_local = threading.local()
# Lock for thread safety when manipulating event loops
_loop_lock = threading.Lock()
# Track active event loops per thread
_thread_loops: Dict[int, asyncio.AbstractEventLoop] = {}

def get_or_create_event_loop():
    """Get the event loop for the current thread or create a new one if it doesn't exist."""
    thread_id = threading.get_ident()
    
    # First check thread-local storage to see if we already have a loop
    if hasattr(_thread_local, 'loop'):
        # Make sure the loop is still valid (not closed)
        if not _thread_local.loop.is_closed():
            return _thread_local.loop
    
    # Try to get the current event loop
    try:
        loop = asyncio.get_event_loop()
        if not loop.is_closed():
            # Store in thread local for faster access next time
            _thread_local.loop = loop
            with _loop_lock:
                _thread_loops[thread_id] = loop
            return loop
    except RuntimeError:
        # No event loop exists for this thread, or it was closed
        pass
    
    # Need to create a new loop
    with _loop_lock:
        # Double-check if we have a valid loop for this thread
        if thread_id in _thread_loops and not _thread_loops[thread_id].is_closed():
            _thread_local.loop = _thread_loops[thread_id]
            return _thread_loops[thread_id]

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        _thread_local.loop = loop
        _thread_loops[thread_id] = loop
        return loop

def run_async_in_new_loop(async_fn, *args, **kwargs):
    """Run an async function in a new event loop in the current thread."""
    loop = get_or_create_event_loop()
    try:
        return loop.run_until_complete(async_fn(*args, **kwargs))
    except Exception as e:

        raise e
    
def create_node_wrapper(async_fn: Callable[..., Awaitable[T]]) -> Callable[..., T]:
    """
    Creates a wrapper that safely executes an async function, ensuring proper event loop handling
    across different threading scenarios.
    """
    def wrapped_function(*args, **kwargs):
        # Use our reliable get_or_create_event_loop function
        loop = get_or_create_event_loop()

        if loop.is_running():
            # We're in a running event loop - create a task in ThreadPoolExecutor
            # This approach prevents nesting of event loops
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(run_async_in_new_loop, async_fn, *args, **kwargs)
                return future.result()
        else:
            # We have an event loop but it's not running, use it directly
            try:
                return loop.run_until_complete(async_fn(*args, **kwargs))
            except Exception as e:
                # Log the error if needed
                from ...utils.logger import log_error
                log_error(f"Error in async execution", e, 
                        context=f"Function: {async_fn.__name__}")
                # Re-raise to maintain original behavior
                raise
    
    return wrapped_function
