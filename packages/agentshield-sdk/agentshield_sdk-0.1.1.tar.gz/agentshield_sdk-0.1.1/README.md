# AgentShield SDK

[![PyPI version](https://badge.fury.io/py/agentshield-sdk.svg)](https://badge.fury.io/py/agentshield-sdk)

Python SDK for the AgentShield API - Runtime security for agentic AI applications.

AgentShield provides a backend service that AI agents can query *before* performing potentially risky actions (like external API calls or code execution). It checks the proposed action against configurable security policies and returns an "allow" or "block" decision. This SDK provides convenient Python functions for agents to interact with a deployed AgentShield API.

## Getting Started

### 1. Installation

Install the SDK using pip:

```bash
pip install agentshield-sdk
```

### 2. Get an API Key

AgentShield requires an API key for authenticating requests to its `/evaluate` endpoint. We are testing this currently with 50 test users.

**To obtain your API key, please contact the administrator:**

➡️ **hello@sanjayck.com** ⬅️

You will receive an API key string (likely starting with `ask_...`). Keep this key secure, as it cannot be retrieved again.

### 3. Basic Usage

Here's a minimal example of how to configure the client and use it to guard an API call:

Python

```
import os
import asyncio
import httpx  # SDK uses httpx; import it if handling its specific exceptions
from agentshield_sdk.client import AgentShield, AgentShieldError

# --- Configuration ---

# Your unique API Key obtained from the administrator
# Best practice: Load key from environment variable or secure storage
api_key = os.environ.get("AGENTSHEILD_API_KEY", "YOUR_API_KEY_HERE")

# The URL where the AgentShield API service is deployed
# Use the official public URL provided
service_url = "https://agentshield-api-service-338863748406.us-central1.run.app"

# Optional: An identifier for the agent using the SDK
agent_id = "my_example_agent_v1"

if api_key == "YOUR_API_KEY_HERE":
    print("ERROR: Please set the AGENTSHEILD_API_KEY environment variable or replace the placeholder in the script.")
    exit()

# --- Initialize Client ---
# You only need to do this once for your agent instance
shield = AgentShield(
    api_key=api_key,
    service_url=service_url,
    agent_id=agent_id,
    timeout=15.0 # Optional: Default timeout for API calls to AgentShield (seconds)
)

# --- Example: Guarded GET request ---
async def make_guarded_request():
    url_to_check = "https://api.thirdparty.com/some/data" # The URL your agent wants to call
    print(f"\nChecking if GET request to {url_to_check} is allowed...")

    try:
        # This method first calls AgentShield's /evaluate endpoint.
        # If allowed, it then performs the actual GET request using httpx.
        response = await shield.guarded_get(
            url_to_check,
            headers={"Authorization": "Bearer SOME_OTHER_TOKEN"}, # Example: Headers for the *target* URL
            timeout=20.0 # Optional: Timeout for the call to the *target* URL
        )

        # If we reach here, the request was allowed by AgentShield
        print(f"Request allowed by AgentShield! Status Code from target: {response.status_code}")

        # Process the actual response from api.thirdparty.com
        # data = response.json()
        # print(f"Data received: {data}")

    except AgentShieldError as e:
        # If blocked by AgentShield policy or API communication fails
        print(f"Request BLOCKED or SDK Error! Reason: {e} (Details: {e.policy_details})")
        # Agent should NOT proceed with the request
    except ValueError as e:
        # Handle invalid input like bad URLs passed to the SDK
        print(f"Input Error: {e}")
    except httpx.TimeoutException:
        # Handle timeout contacting the *target* URL (after allow)
        print(f"Request to {url_to_check} timed out.")
    except httpx.RequestError as e:
        # Handle network errors contacting the *target* URL (after allow)
        print(f"Network error contacting {url_to_check}: {e}")
    except Exception as e:
        # Handle any other unexpected errors
        print(f"An unexpected error occurred: {e}")

# Run the example
# Note: This requires an event loop running, common in async applications.
# If running standalone, use asyncio.run()
if __name__ == "__main__":
    # Ensure you have a valid API key set before running the test
    if api_key != "YOUR_API_KEY_HERE":
        asyncio.run(make_guarded_request())
    else:
        print("Skipping example run: API key not configured.")

```

## **SDK Client Reference**

### **Initialization**

Instantiate the client with your API key and the service URL.

Python

```
from agentshield_sdk.client import AgentShield

shield = AgentShield(
    api_key: str,          # Your mandatory API key from the admin
    service_url: str,      # Mandatory URL of the AgentShield API service
    agent_id: str = "sdk_agent_default", # Optional identifier for your agent
    timeout: float = 10.0  # Optional default timeout for calls TO the AgentShield API itself
)
```

### **`async guarded_get(url: str, **kwargs) -> httpx.Response`**

Checks if a GET request to the specified `url` is permitted by AgentShield policies *before* executing it using `httpx`.

* **Parameters:**  
  * `url` (str): The target URL the agent intends to call.  
  * `**kwargs`: Any additional keyword arguments accepted by `httpx.get` (e.g., `headers`, `params`, `timeout`). The `timeout` kwarg here applies to the request to the *target* URL.  
* **Returns:** An `httpx.Response` object from the target URL if the request is allowed by AgentShield and the request to the target is successful.  
* **Raises:**  
  * `AgentShieldError`: If the action is blocked by an AgentShield policy or if communication with the AgentShield API fails (check `policy_details` attribute for more info).  
  * `ValueError`: If the provided `url` format is invalid.  
  * `httpx.TimeoutException`: If the request to the target URL times out.  
  * `httpx.RequestError`: For other network errors contacting the target URL (after being allowed).

### **`async safe_execute(code_snippet: str)`**

Checks if executing a Python `code_snippet` (string) is permitted by AgentShield policies.

* **Warning:** This SDK function **DOES NOT EXECUTE** the code for safety reasons. It only performs the security check against the AgentShield API. The calling agent is responsible for execution *after* this check passes.  
* **Parameters:**  
  * `code_snippet` (str): The Python code the agent intends to execute.  
* **Returns:** `None` if the check indicates the code is allowed.  
* **Raises:**  
  * `AgentShieldError`: If code execution is blocked by an AgentShield policy or if communication with the AgentShield API fails.
