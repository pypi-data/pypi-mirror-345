# --- File: agentshield_cli/main.py --- CORRECTED AGAIN & REFINED ---
# Command-line interface for AgentShield user and API key management

import click
import httpx
import os
import json
from pathlib import Path
import sys  # For exiting on critical errors
import datetime  # For date parsing/formatting in list_keys

# --- Configuration ---
# Try to get backend URL from env var, fallback to default public URL
DEFAULT_SERVICE_URL = os.environ.get(
    "AGENTSHEILD_SERVICE_URL",
    "https://agentshield-api-service-338863748406.us-central1.run.app",
)
# Configuration file path (~/.agentshield/config.json)
CONFIG_DIR = Path.home() / ".agentshield"
CONFIG_FILE = CONFIG_DIR / "config.json"
SESSION_TOKEN_KEY = "session_token"  # Key within the JSON config file

# --- Helper Functions ---


def _ensure_config_dir():
    """Creates the config directory (~/.agentshield) if it doesn't exist."""
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        # Attempt to set restrictive permissions (owner rwx only)
        if sys.platform != "win32":
            CONFIG_DIR.chmod(0o700)
    except OSError as e:
        click.echo(
            f"Warning: Could not create or set permissions on config directory {CONFIG_DIR}. Error: {e}",
            err=True,
        )
    except Exception as e:
        click.echo(
            f"Warning: Unexpected error handling config directory {CONFIG_DIR}. Error: {e}",
            err=True,
        )


def save_token(token: str):
    """Saves the session token securely to ~/.agentshield/config.json."""
    _ensure_config_dir()
    config_data = {SESSION_TOKEN_KEY: token}
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config_data, f, indent=2)
        # Attempt to set restrictive permissions (owner rw only)
        if sys.platform != "win32":
            CONFIG_FILE.chmod(0o600)
        click.echo(f"✅ Session token saved successfully to {CONFIG_FILE}")
    except IOError as e:
        click.echo(
            f"❌ Error: Could not write token to {CONFIG_FILE}. Check permissions. Error: {e}",
            err=True,
        )
        sys.exit(1)  # Exit if token cannot be saved
    except Exception as e:
        click.echo(f"❌ Error: Unexpected error saving token. Error: {e}", err=True)
        sys.exit(1)


def load_token() -> str | None:
    """Loads the session token from ~/.agentshield/config.json."""
    if not CONFIG_FILE.is_file():
        return None
    try:
        # Optional: Check permissions before reading (best effort)
        if sys.platform != "win32":
            current_mode = CONFIG_FILE.stat().st_mode
            # Check if permissions are broader than owner read-write (0o600)
            if current_mode & 0o077:  # Checks group/other permissions
                click.echo(
                    f"Warning: Config file {CONFIG_FILE} has potentially insecure permissions ({oct(current_mode)}). Recommended: 600.",
                    err=True,
                )

        with open(CONFIG_FILE, "r") as f:
            config_data = json.load(f)
            token = config_data.get(SESSION_TOKEN_KEY)
            if not token:
                click.echo(
                    f"Warning: Token file exists but key '{SESSION_TOKEN_KEY}' not found or empty.",
                    err=True,
                )
                return None
            return token
    except (IOError, json.JSONDecodeError) as e:
        click.echo(
            f"Error loading token from {CONFIG_FILE}: {e}. Please try logging in again.",
            err=True,
        )
        return None
    except Exception as e:
        click.echo(f"Error: Unexpected error loading token. Error: {e}", err=True)
        return None


def clear_token():
    """Removes the stored token file ~/.agentshield/config.json."""
    if CONFIG_FILE.is_file():
        try:
            CONFIG_FILE.unlink()
            click.echo("Session token cleared (logged out).")
        except OSError as e:
            click.echo(f"Error removing token file {CONFIG_FILE}: {e}", err=True)
    else:
        click.echo("Already logged out (no token file found).")


def get_auth_headers() -> dict:
    """Loads the token and prepares the Authorization header."""
    token = load_token()
    if not token:
        click.echo(
            "❌ Error: Not logged in. Please run 'agentshield login' first.", err=True
        )
        sys.exit(1)  # Exit if not logged in for commands requiring auth
    return {"Authorization": f"Bearer {token}"}


def handle_api_error(response: httpx.Response, context: str):
    """Provides user-friendly output for HTTP errors."""
    click.echo(
        f"❌ Error during {context}: {response.status_code} {response.reason_phrase}",
        err=True,
    )
    try:
        error_data = response.json()
        detail = error_data.get("detail", "No details provided.")
        # Handle validation errors specifically if they have a known structure
        # Assuming FastAPI's default validation error structure
        if response.status_code == 422 and isinstance(detail, list):
            click.echo("   Validation Errors:", err=True)
            for err in detail:
                loc = " -> ".join(
                    map(str, err.get("loc", ["body"])[1:])
                )  # Clean up location
                msg = err.get("msg", "")
                click.echo(f"    - Field '{loc}': {msg}", err=True)
        elif isinstance(detail, str):
            click.echo(f"   Detail: {detail}", err=True)
        else:  # Handle unexpected detail format
            click.echo(f"   Detail: {json.dumps(detail)}", err=True)

    except json.JSONDecodeError:
        # Handle non-JSON error responses
        error_text = response.text[:500]  # Limit output length
        click.echo(
            f"   Response: {error_text}{'...' if len(response.text) > 500 else ''}",
            err=True,
        )
    except Exception as e:
        click.echo(f"   Could not parse error response body: {e}", err=True)


# --- Base Client for API Calls ---
def get_api_client(requires_auth=False) -> httpx.Client:
    headers = {}
    if requires_auth:
        headers = get_auth_headers()  # Exits if not logged in
    client = httpx.Client(base_url=DEFAULT_SERVICE_URL, timeout=20.0, headers=headers)
    return client


# --- CLI Command Group ---
@click.group()
@click.version_option(
    package_name="agentshield-sdk"
)  # Assumes package name in pyproject.toml
def cli():
    """
    AgentShield CLI for user account and API key management.

    Connects to the AgentShield backend service.
    Default URL: {}
    Set AGENTSHEILD_SERVICE_URL environment variable to override.
    """.format(
        DEFAULT_SERVICE_URL
    )
    pass


# --- Registration Command ---
@cli.command()
@click.option("--username", prompt="Username", help="Desired username (unique).")
@click.option("--email", prompt="Email", help="Your email address.")
@click.option(
    "--password",
    prompt="Password (min 8 chars)",
    help="Your desired password.",
    hide_input=True,
    confirmation_prompt=True,
)
def register(username, email, password):
    """Register a new AgentShield user account."""
    click.echo(f"Attempting to register user '{username}'...")
    payload = {"username": username, "email": email, "password": password}
    signup_url = "/signup"  # Relative path

    try:
        with get_api_client() as client:  # No auth needed for signup
            response = client.post(signup_url, json=payload)

        # --- Use integer status codes ---
        if response.status_code == 201:  # <<< CORRECTED (was status.HTTP_201_CREATED)
            user_data = response.json()
            click.echo(
                f"✅ Registration successful for user '{user_data.get('username', username)}'!"
            )
            click.echo("   You can now log in using 'agentshield login'.")
        elif (
            response.status_code == 409
        ):  # <<< CORRECTED (was status.HTTP_409_CONFLICT)
            # Conflict (email/username exists)
            error_data = response.json()
            click.echo(
                f"❌ Registration failed: {error_data.get('detail', 'Conflict - Email or Username already exists')}",
                err=True,
            )
        elif response.status_code == 422:
            # Validation error (e.g., short password, invalid email format handled by Pydantic)
            handle_api_error(response, "registration validation")
        else:
            # Use helper for other errors (like 500 Internal Server Error)
            handle_api_error(response, "registration")

    except httpx.RequestError as e:
        click.echo(
            f"❌ Network error during registration: Cannot connect to {DEFAULT_SERVICE_URL}. Details: {e}",
            err=True,
        )
    except Exception as e:
        click.echo(
            f"❌ An unexpected error occurred during registration: {e}", err=True
        )


# --- Login Command ---
@cli.command()
@click.option("--email", prompt="Email", help="Your account email.")
@click.option(
    "--password", prompt="Password", help="Your account password.", hide_input=True
)
def login(email, password):
    """Log in to AgentShield and save the session token."""
    click.echo(f"Attempting to log in as {email}...")
    login_url = "/login"
    # Backend /login expects Form data, with 'username' field holding the email
    data = {"email": email, "password": password}

    try:
        with get_api_client() as client:  # No auth needed for login itself
            response = client.post(login_url, data=data)  # Send as form data

        # --- Use integer status codes ---
        if response.status_code == 200:  # <<< CORRECTED (was status.HTTP_200_OK)
            login_data = response.json()
            session_token = login_data.get("session_token")
            user_info = login_data.get("user", {})
            if session_token:
                save_token(session_token)  # Securely save the extracted token
                click.echo(f"   Logged in as: {user_info.get('username', email)}")
            else:
                click.echo(
                    "❌ Login request succeeded but no session token found in response body.",
                    err=True,
                )
                click.echo(f"   Response: {login_data}")
        elif (
            response.status_code == 401
        ):  # <<< CORRECTED (was status.HTTP_401_UNAUTHORIZED)
            # Incorrect credentials or inactive account
            error_data = response.json()
            click.echo(
                f"❌ Login failed: {error_data.get('detail', 'Incorrect email/password or inactive account')}",
                err=True,
            )
        else:
            # Use helper for other errors
            handle_api_error(response, "login")

    except httpx.RequestError as e:
        click.echo(
            f"❌ Network error during login: Cannot connect to {DEFAULT_SERVICE_URL}. Details: {e}",
            err=True,
        )
    except Exception as e:
        click.echo(f"❌ An unexpected error occurred during login: {e}", err=True)


# --- Logout Command ---
@cli.command()
def logout():
    """Log out by clearing the saved session token."""
    clear_token()


# --- API Key Commands Group ---
@cli.group()
def keys():
    """Manage your AgentShield API keys."""
    pass


@keys.command(name="list")
def list_keys():
    """List your existing API keys."""
    click.echo("Fetching your API keys...")
    keys_url = "/api/v1/user/apikeys"  # Relative path

    try:
        with get_api_client(requires_auth=True) as client:
            response = client.get(keys_url)
            # raise_for_status will handle 4xx/5xx errors, including 401 if auth fails
            response.raise_for_status()

        key_list = response.json()
        if not key_list:
            click.echo("No API keys found.")
            return

        click.echo("-" * 80)
        click.echo(
            f"{'ID':<6} {'Prefix':<13} {'Status':<10} {'Created (UTC)':<20} {'Description'}"
        )
        click.echo("-" * 80)
        for key in key_list:
            status_str = "Active" if key.get("is_active") else "Inactive"
            desc = key.get("description") or ""
            created_at_str = key.get("created_at", "N/A")
            created_display = created_at_str  # Default display
            # Attempt basic date formatting (input format should be ISO 8601 from FastAPI)
            if created_at_str != "N/A":
                try:
                    # Handle potential 'Z' timezone indicator
                    created_at_str_norm = created_at_str.replace("Z", "+00:00")
                    # Parse ISO format
                    dt_obj = datetime.datetime.fromisoformat(created_at_str_norm)
                    # Format for display (you can choose timezone handling - here naive UTC)
                    created_display = dt_obj.strftime("%Y-%m-%d %H:%M:%S")
                except (ValueError, TypeError):
                    pass  # Keep original string if parse fails

            click.echo(
                f"{key.get('id', ''):<6} {key.get('prefix', ''):<13} {status_str:<10} {created_display:<20} {desc}"
            )
        click.echo("-" * 80)

    except httpx.RequestError as e:
        click.echo(f"❌ Network error fetching keys: {e}", err=True)
    except httpx.HTTPStatusError as e:
        # raise_for_status() converts errors to this exception
        # Specific handling for 401 could be added here if needed, but get_auth_headers usually exits first
        handle_api_error(e.response, "fetching keys")
    except Exception as e:
        click.echo(f"❌ An unexpected error occurred fetching keys: {e}", err=True)


@keys.command(name="create")
@click.option("--description", "-d", help="Optional description for the new key.")
def create_key(description):
    """Generate a new API key."""
    click.echo("Generating new API key...")
    if description:
        click.echo(f"  Description: {description}")

    keys_url = "/api/v1/user/apikeys"
    payload = {"description": description}  # Backend expects JSON

    try:
        with get_api_client(requires_auth=True) as client:
            response = client.post(keys_url, json=payload)
            # Check for errors (4xx/5xx)
            response.raise_for_status()

        # Success (usually 201 Created)
        new_key_data = response.json()
        click.echo("✅ Successfully generated new API key!")
        click.echo("=" * 60)
        click.echo(
            click.style("IMPORTANT:", fg="yellow")
            + " Copy your new API key now. You cannot retrieve it again."
        )
        click.echo(
            f"  {click.style('API Key:', bold=True)} {new_key_data.get('full_key', 'ERROR - KEY NOT RETURNED')}"
        )
        click.echo("=" * 60)
        click.echo(
            f"Details: ID={new_key_data.get('id')}, Prefix={new_key_data.get('prefix')}, Description='{new_key_data.get('description', '')}'"
        )

    except httpx.RequestError as e:
        click.echo(f"❌ Network error generating key: {e}", err=True)
    except httpx.HTTPStatusError as e:
        handle_api_error(e.response, "generating key")
    except Exception as e:
        click.echo(f"❌ An unexpected error occurred generating key: {e}", err=True)


@keys.command(name="delete")
@click.argument("key_id", type=int)
def delete_key(key_id):
    """Delete an API key by its ID."""
    click.confirm(
        f"Are you sure you want to PERMANENTLY delete API key ID {key_id}?", abort=True
    )

    click.echo(f"Attempting to delete API key ID {key_id}...")
    delete_url = f"/api/v1/user/apikeys/{key_id}"  # Relative path

    try:
        with get_api_client(requires_auth=True) as client:
            response = client.delete(delete_url)
            # Check for errors, raise_for_status handles 4xx/5xx but we want specific 404 message
            if response.status_code == 404:  # <<< Use integer
                click.echo(
                    f"❌ Error: API Key ID {key_id} not found or you do not own it.",
                    err=True,
                )
                return  # Exit after specific 404 handling
            # Raise for other errors (like 401, 403, 500)
            response.raise_for_status()

        # If raise_for_status didn't trigger and it wasn't 404, it should be 204
        # Status code 204 No Content indicates success
        click.echo(f"✅ Successfully deleted API key ID {key_id}.")

    except httpx.RequestError as e:
        click.echo(f"❌ Network error deleting key: {e}", err=True)
    except httpx.HTTPStatusError as e:
        # 404 handled above, this handles other errors raised by raise_for_status
        handle_api_error(e.response, "deleting key")
    except Exception as e:
        click.echo(f"❌ An unexpected error occurred deleting key: {e}", err=True)


# --- Main entry point ---
if __name__ == "__main__":
    cli()
