import threading
import uuid
import os # Import os for environment variables
import logging # Import logging

# Define thread-local storage
_thread_local = threading.local()

# Generate a default session ID for the process
_process_default_session_id = str(uuid.uuid4())

def get_session_id():
    """Get the current session ID, falling back to the process default."""
    return getattr(_thread_local, 'session_id', None) or _process_default_session_id

def set_session_id(session_id):
    """Set the session ID for the current thread."""
    _thread_local.session_id = session_id

def clear_session_id():
    """Clear the session ID for the current thread."""
    if hasattr(_thread_local, 'session_id'):
        del _thread_local.session_id 

def prepare_request_headers(headers: dict):
    """Adds X-Session-ID and X-TROPIR-API-KEY (if available) to the headers dict."""
    # Add Session ID header
    session_id = get_session_id()
    headers["X-Session-ID"] = str(session_id)
    logging.debug(f"Utils: Added Session ID to headers: {session_id}")

    # Add Tropir API key if available
    tropir_api_key = os.environ.get("TROPIR_API_KEY")
    if tropir_api_key:
        headers["X-TROPIR-API-KEY"] = tropir_api_key
        logging.debug("Utils: Added X-TROPIR-API-KEY to headers.")
    else:
        logging.debug("Utils: TROPIR_API_KEY not found, skipping header.") 