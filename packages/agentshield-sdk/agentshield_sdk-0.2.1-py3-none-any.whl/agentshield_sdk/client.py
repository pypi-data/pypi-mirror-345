# agentshield_sdk/client.py
import os
import httpx
import logging
from urllib.parse import urljoin, urlparse  # Import urlparse as well
from pydantic import HttpUrl, ValidationError

sdk_logger = logging.getLogger("AgentShieldSDK")
if not sdk_logger.hasHandlers():
    logging.basicConfig(level=logging.INFO)


class AgentShieldError(Exception):
    """Custom exception raised when an action is blocked by AgentShield."""

    def __init__(self, message, policy_details=""):
        super().__init__(message)
        self.policy_details = policy_details


class AgentShield:
    def __init__(
        self,
        api_key: str,
        service_url: str,
        agent_id: str = "sdk_agent_default",
        timeout: float = 10.0,
    ):
        if not api_key:
            raise ValueError("API key is required.")
        if not service_url:
            raise ValueError("Service URL is required.")

        # Basic validation for service_url
        parsed_url = urlparse(service_url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError(f"Invalid service_url format: {service_url}")

        self.api_key = api_key
        self.service_url = service_url
        self.agent_id = agent_id
        self.evaluate_endpoint = urljoin(self.service_url, "/api/v1/evaluate/")
        self.timeout = timeout
        self.headers = {"X-API-Key": self.api_key}  # Prepare headers

    async def _evaluate_action(
        self, action_type: str, url: str | None = None, code_snippet: str | None = None
    ) -> tuple[str, str]:
        """Calls the AgentShield backend's /evaluate endpoint."""
        payload = {
            "agent_id": self.agent_id,
            "action_type": action_type,
            "url": url,
            "code_snippet": code_snippet,
        }
        payload = {k: v for k, v in payload.items() if v is not None}

        sdk_logger.debug(
            f"Sending evaluation request to {self.evaluate_endpoint} with payload: {payload}"
        )

        # Use a single client instance potentially, or create per request
        async with httpx.AsyncClient(
            timeout=self.timeout, headers=self.headers
        ) as client:  # Include headers here!
            try:
                response = await client.post(self.evaluate_endpoint, json=payload)
                response.raise_for_status()

                eval_data = response.json()
                decision = eval_data.get("decision")
                policy_details = eval_data.get("policy_details", "No details provided")

                if decision not in ["allow", "block"]:
                    sdk_logger.error(
                        f"Invalid decision received from backend: {decision}"
                    )
                    raise AgentShieldError(
                        "Invalid response from AgentShield backend", policy_details
                    )

                sdk_logger.info(
                    f"Evaluation result: Decision='{decision}', Policy='{policy_details}'"
                )
                return decision, policy_details

            # --- Keep your existing exception handling ---
            except httpx.RequestError as e:
                sdk_logger.error(
                    f"Network error calling AgentShield backend at {self.evaluate_endpoint}: {e}"
                )
                raise AgentShieldError(
                    "Failed to contact AgentShield backend - Blocking action", str(e)
                )
            except httpx.HTTPStatusError as e:
                # Specifically handle 401/403 for bad API keys if desired
                if e.response.status_code in [401, 403]:
                    sdk_logger.error(
                        f"Authentication error calling AgentShield backend (status {e.response.status_code}): Invalid API Key?"
                    )
                    raise AgentShieldError(
                        f"AgentShield authentication error ({e.response.status_code}) - Check API Key",
                        e.response.text,
                    )
                else:
                    sdk_logger.error(
                        f"AgentShield backend returned error status {e.response.status_code}: {e.response.text}"
                    )
                    raise AgentShieldError(
                        f"AgentShield backend error ({e.response.status_code}) - Blocking action",
                        e.response.text,
                    )
            except Exception as e:
                sdk_logger.error(
                    f"Unexpected error during action evaluation: {e}", exc_info=True
                )
                raise AgentShieldError(
                    "Unexpected error during evaluation - Blocking action", str(e)
                )

    async def guarded_get(self, url: str, **kwargs) -> httpx.Response:
        """Performs an HTTP GET request only if allowed by AgentShield policy."""
        sdk_logger.info(f"Agent '{self.agent_id}' attempting GET request to: {url}")
        try:
            HttpUrl(url)  # Pydantic validation
        except ValidationError as e:
            sdk_logger.warning(
                f"Invalid URL format provided to guarded_get: {url} - {e}"
            )
            raise ValueError(f"Invalid URL format: {url}") from e

        decision, policy_details = await self._evaluate_action(
            action_type="api_call", url=url
        )

        if decision == "block":
            sdk_logger.warning(
                f"Action BLOCKED by AgentShield: GET {url}. Policy: {policy_details}"
            )
            raise AgentShieldError(
                f"GET request to {url} blocked by policy.", policy_details
            )

        sdk_logger.debug(f"Action ALLOWED: Proceeding with GET {url}")
        # Use a new client for the actual request to the target URL
        async with httpx.AsyncClient() as client:
            try:
                # Don't pass the agent's API key header to the target URL!
                request_timeout = kwargs.pop(
                    "timeout", self.timeout
                )  # Allow overriding timeout
                response = await client.get(url, timeout=request_timeout, **kwargs)
                response.raise_for_status()
                sdk_logger.info(f"Successfully executed guarded GET request to {url}")
                return response
            # --- Keep your existing exception handling for the actual GET ---
            except httpx.RequestError as e:
                sdk_logger.error(
                    f"Network error during allowed GET request to {url}: {e}"
                )
                raise
            except httpx.HTTPStatusError as e:
                sdk_logger.warning(
                    f"Target server returned error for allowed GET {url}: {e.response.status_code}"
                )
                return e.response

    async def safe_execute(self, code_snippet: str):
        """Checks code snippet execution; DOES NOT EXECUTE."""
        sdk_logger.info(
            f"Agent '{self.agent_id}' attempting to execute code (check only). Preview: {code_snippet[:100]}..."
        )
        decision, policy_details = await self._evaluate_action(
            action_type="code_exec", code_snippet=code_snippet
        )

        if decision == "block":
            sdk_logger.warning(
                f"Action BLOCKED by AgentShield: Execute code. Policy: {policy_details}"
            )
            raise AgentShieldError("Code execution blocked by policy.", policy_details)

        sdk_logger.info(
            f"Action ALLOWED by AgentShield: Execute code (check only). Policy: {policy_details}"
        )
        return  # Or return True to indicate check passed


# --- Example Usage Update ---
async def _sdk_test():
    logging.basicConfig(level=logging.DEBUG)
    sdk_logger.setLevel(logging.DEBUG)
    print("--- SDK Test ---")

    # CONFIGURATION FOR TESTING
    test_api_key = os.environ.get(
        "AGENTSHEILD_API_KEY_TEST", "YOUR_TEST_API_KEY"
    )  # Use a specific test key
    test_service_url = os.environ.get(
        "AGENTSHIELD_BACKEND_URL", "http://127.0.0.1:8000"
    )  # Can still use env var for URL default

    if test_api_key == "YOUR_TEST_API_KEY":
        print("Please set AGENTSHEILD_API_KEY_TEST env var for testing")
        return

    # Instantiate the client
    shield = AgentShield(api_key=test_api_key, service_url=test_service_url)
    print(f"Connecting to AgentShield backend at: {shield.service_url}")
    print(f"Using Agent ID: {shield.agent_id}")

    # Test Allowed URL
    try:
        print("\nTesting allowed URL (example.com)...")
        response = await shield.guarded_get(
            "http://example.com"
        )  # Call method on instance
        print(f"Success! Status: {response.status_code}")
    except AgentShieldError as e:
        print(f"Error (unexpected block): {e} - {e.policy_details}")
    except Exception as e:
        print(f"Error: {e}")

    # --- Update other tests similarly to call methods on the 'shield' instance ---
    # Test Blocked URL
    try:
        print("\nTesting blocked URL (google.com)...")
        await shield.guarded_get("https://google.com")
        print("Error: Request to google.com was unexpectedly allowed!")
    except AgentShieldError as e:
        print(f"Success (correctly blocked): {e} - {e.policy_details}")
    except Exception as e:
        print(f"Error: {e}")

    # Test Blocked Code
    try:
        print("\nTesting blocked code (import os)...")
        code = "import os\nos.listdir('/')"
        await shield.safe_execute(code)
        print("Error: Code execution check for 'import os' was unexpectedly allowed!")
    except AgentShieldError as e:
        print(f"Success (correctly blocked): {e} - {e.policy_details}")
    except Exception as e:
        print(f"Error: {e}")

    # Test Allowed Code
    try:
        print("\nTesting allowed code (print)...")
        code = "print('This should be allowed')"
        await shield.safe_execute(code)
        print("Success (correctly allowed check).")
    except AgentShieldError as e:
        print(f"Error (unexpected block): {e} - {e.policy_details}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(_sdk_test())
