from contextlib import contextmanager
import threading
from pathlib import Path
import shutil
import os

# Thread-local storage to track active transactions
_local = threading.local()
cache_path = Path.home() / ".cache" / "antelop"

IN_CONTAINER = os.environ.get("IN_CONTAINER") == "True"

def clear_dir(path: Path):
    for item in path.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

def is_transaction_active():
    """
    Check if a transaction is currently active for this thread.
    
    Returns:
        bool: True if a transaction is active, False otherwise
    """
    return getattr(_local, 'transaction_active', False)

@contextmanager
def transaction_context(connection):
    """
    Context manager that wraps a connection's transaction while handling query cache state.
    
    This utility ensures that the query cache is disabled during the transaction and
    properly restored after the transaction completes or if an exception occurs.
    It also sets a flag to indicate an active transaction.
    
    Args:
        connection: The database connection object that has transaction and set_query_cache methods
        
    Yields:
        None: This context manager doesn't provide any value to the with-block
        
    Example:
        ```python
        from antelop.connection.transaction import cache_transaction
        
        # Inside a method with access to connection
        with cache_transaction(connection):
            # Perform database operations
            table.insert(data)
        ```
    """
    if IN_CONTAINER:
        # If running in a container, just yield control
            # Yield control back to the with-block
        with connection.transaction:
            yield
    else:
        # Disable query cache before transaction
        connection.purge_query_cache()
        clear_dir(cache_path)
        connection.set_query_cache()
        
        # Set transaction active flag
        _local.transaction_active = True
        
        try:
            # Start transaction
            with connection.transaction:
                # Yield control back to the with-block
                yield
        finally:
            # Restore the query cache, regardless of whether an exception occurred
            connection.set_query_cache(query_cache="main")
            # Clear transaction active flag
            _local.transaction_active = False

@contextmanager
def operation_context(connection):
    """
    Context manager that wraps a connection's operation while handling query cache state.
    
    This utility ensures that the query cache is disabled during the operation and
    properly restored after the operation completes or if an exception occurs.
    
    Args:
        connection: The database connection object that has transaction and set_query_cache methods
        
    Yields:
        None: This context manager doesn't provide any value to the with-block
        
    Example:
        ```python
        from antelop.connection.transaction import cache_transaction
        
        # Inside a method with access to connection
        with cache_transaction(connection):
            # Perform database operations
            table.insert(data)
        ```
    """
    if IN_CONTAINER:
        # If running in a container, just yield control
        yield
        return
    else:
        if is_transaction_active():
            # If a transaction is active, just yield control
            yield
            return
        else:
            # Disable query cache before transaction
            connection.purge_query_cache()
            clear_dir(cache_path)
            connection.set_query_cache()
            
            try:
                # Start transaction
                with connection.transaction:
                    # Yield control back to the with-block
                    yield
            finally:
                # Restore the query cache, regardless of whether an exception occurred
                connection.set_query_cache(query_cache="main")