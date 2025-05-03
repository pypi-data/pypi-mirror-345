# Tropir Session Utilities

This utility helps manage session IDs for tracking requests and automatically injects relevant headers into your HTTP requests.

## Installation

Install the package using pip:

```bash
pip install tropir
```

## Purpose

When making requests to backend services (like LLM APIs or tracking endpoints), it's often useful to include:

1.  **A Session ID (`X-Session-ID`):** To group related requests within a single user interaction or process run.
2.  **An API Key (`X-TROPIR-API-KEY`):** To authenticate requests with a specific service (like a Tropir backend).

This utility provides a simple way to manage session IDs and automatically add these headers to your request dictionaries.

## Basic Usage: Automatic Header Injection

The primary way to use this utility is via the `prepare_request_headers` function. It takes your existing `headers` dictionary for an HTTP request and modifies it in place.

```python
import requests
import os
from tropir.session_utils import prepare_request_headers

# Set the Tropir API key in your environment variables (optional)
# export TROPIR_API_KEY='your_api_key_here'

# Example API call
api_url = "https://example.com/api/resource"
payload = {"data": "some_value"}

# Initial headers (e.g., for authentication or content type)
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer some_other_token"
}

# Prepare the headers: This adds X-Session-ID and potentially X-TROPIR-API-KEY
prepare_request_headers(headers)

# Now the 'headers' dictionary contains the added keys:
# {
#     "Content-Type": "application/json",
#     "Authorization": "Bearer some_other_token",
#     "X-Session-ID": "<generated_or_thread_local_uuid>",
#     "X-TROPIR-API-KEY": "your_api_key_here" # (If env var was set)
# }

print(f"Sending request with headers: {headers}")

response = requests.post(api_url, headers=headers, json=payload)

# Handle response...
print(response.status_code)

```

**How it works:**

*   **`X-Session-ID`:**
    *   It first checks if a session ID has been explicitly set for the current thread using `set_session_id()` (see Advanced Usage).
    *   If no thread-specific ID is found, it falls back to a default UUID generated once when the process started. This ensures all requests within the same process run (that don't have overrides) share the same default session ID.
*   **`X-TROPIR-API-KEY`:**
    *   It checks for the environment variable `TROPIR_API_KEY`.
    *   If the environment variable is set, its value is added to the headers.
    *   If not set, the header is simply omitted.

## Advanced Usage: Manual Session ID Control

While `prepare_request_headers` is sufficient for most use cases, you can manually control the session ID on a per-thread basis if needed:

```python
from tropir.session_utils import get_session_id, set_session_id, clear_session_id
import threading

def worker_task(custom_id):
    print(f"[{threading.current_thread().name}] Default Session ID: {get_session_id()}")

    # Set a custom session ID for this thread
    set_session_id(custom_id)
    print(f"[{threading.current_thread().name}] Thread-specific Session ID: {get_session_id()}")

    # ... make requests using prepare_request_headers ...
    # Headers will now use 'custom_id' for X-Session-ID

    # Clear the thread-specific ID, falling back to the default
    clear_session_id()
    print(f"[{threading.current_thread().name}] Session ID after clear: {get_session_id()}")

# Create and run threads with custom IDs
thread1 = threading.Thread(target=worker_task, args=("session-abc",), name="Worker-1")
thread2 = threading.Thread(target=worker_task, args=("session-xyz",), name="Worker-2")

thread1.start()
thread2.start()

thread1.join()
thread2.join()

print(f"[Main Thread] Session ID: {get_session_id()}") # Will show the process default ID
```

*   `set_session_id(your_id)`: Overrides the session ID for the current thread.
*   `get_session_id()`: Retrieves the current effective session ID (thread-local or process default).
*   `clear_session_id()`: Removes the thread-local override, causing `get_session_id()` to return the process default again for this thread.