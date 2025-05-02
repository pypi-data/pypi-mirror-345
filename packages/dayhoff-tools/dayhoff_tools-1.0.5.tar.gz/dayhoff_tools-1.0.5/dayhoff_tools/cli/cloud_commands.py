"""CLI commands for cloud provider authentication and management.

This module provides commands for authenticating with GCP and AWS from within
development containers. It handles both immediate shell environment configuration
via the --export flag and persistent configuration via shell RC files.

The implementation focuses on:
1. Unifying cloud authentication with the `dh` CLI tool
2. Maintaining persistence across shell sessions via RC file modifications
3. Providing similar capabilities to the shell scripts it replaces
"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Tuple

import questionary
import typer

# --- Configuration ---
GCP_DEVCON_SA = "devcon@enzyme-discovery.iam.gserviceaccount.com"
GCP_PROJECT_ID = "enzyme-discovery"
AWS_DEFAULT_PROFILE = "dev-devaccess"
AWS_CONFIG_FILE = Path.home() / ".aws" / "config"
SHELL_RC_FILES = [
    Path.home() / ".bashrc",
    Path.home() / ".bash_profile",
    Path.home() / ".profile",
]

# --- Color constants for formatted output ---
RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
BLUE = "\033[0;36m"
NC = "\033[0m"  # No Color


# --- Common Helper Functions ---
def _find_executable(name: str) -> str:
    """Find the full path to an executable in PATH."""
    path = shutil.which(name)
    if not path:
        raise FileNotFoundError(
            f"{name} command not found. Please ensure it's installed."
        )
    return path


def _run_command(
    cmd_list: List[str],
    capture: bool = False,
    check: bool = True,
    suppress_output: bool = False,
) -> Tuple[int, str, str]:
    """Run a command and return its result.

    Args:
        cmd_list: List of command arguments
        capture: Whether to capture output
        check: Whether to raise on non-zero exit code
        suppress_output: Whether to hide output even if not captured

    Returns:
        Tuple of (return_code, stdout_str, stderr_str)
    """
    stdout_opt = (
        subprocess.PIPE if capture else subprocess.DEVNULL if suppress_output else None
    )
    stderr_opt = (
        subprocess.PIPE if capture else subprocess.DEVNULL if suppress_output else None
    )

    try:
        result = subprocess.run(
            cmd_list, stdout=stdout_opt, stderr=stderr_opt, check=check, text=True
        )
        return (
            result.returncode,
            result.stdout if capture else "",
            result.stderr if capture else "",
        )
    except subprocess.CalledProcessError as e:
        if capture:
            return (e.returncode, e.stdout or "", e.stderr or "")
        return (e.returncode, "", "")


def _modify_rc_files(variable: str, value: Optional[str]) -> None:
    """Add or remove an export line from RC files.

    Args:
        variable: Environment variable name
        value: Value to set, or None to remove
    """
    for rc_file in SHELL_RC_FILES:
        if not rc_file.exists():
            continue

        try:
            # Read existing content
            with open(rc_file, "r") as f:
                lines = f.readlines()

            # Filter out existing exports for this variable
            pattern = re.compile(f"^export {variable}=")
            new_lines = [line for line in lines if not pattern.match(line.strip())]

            # Add new export if value is provided
            if value is not None:
                new_lines.append(f"export {variable}={value}\n")

            # Write back to file
            with open(rc_file, "w") as f:
                f.writelines(new_lines)

        except (IOError, PermissionError) as e:
            print(f"Warning: Could not update {rc_file}: {e}", file=sys.stderr)


def _get_env_var(variable: str) -> Optional[str]:
    """Safely get an environment variable."""
    return os.environ.get(variable)


# --- GCP Functions ---
def _is_gcp_user_authenticated() -> bool:
    """Check if a user is authenticated with GCP (not a compute service account)."""
    gcloud_path = _find_executable("gcloud")
    cmd = [
        gcloud_path,
        "auth",
        "list",
        "--filter=status:ACTIVE",
        "--format=value(account)",
    ]
    _, stdout, _ = _run_command(cmd, capture=True, check=False)

    account = stdout.strip()
    return bool(account) and "compute@developer.gserviceaccount.com" not in account


def _get_current_gcp_user() -> str:
    """Get the currently authenticated GCP user."""
    gcloud_path = _find_executable("gcloud")
    cmd = [
        gcloud_path,
        "auth",
        "list",
        "--filter=status:ACTIVE",
        "--format=value(account)",
    ]
    _, stdout, _ = _run_command(cmd, capture=True, check=False)

    account = stdout.strip()
    if account:
        if "compute@developer.gserviceaccount.com" in account:
            return "Not authenticated (using VM service account)"
        return account
    return "Not authenticated"


def _get_current_gcp_impersonation() -> str:
    """Get the current impersonated service account, if any."""
    sa = _get_env_var("CLOUDSDK_AUTH_IMPERSONATE_SERVICE_ACCOUNT")
    return sa if sa else "None"


def _run_gcloud_login() -> None:
    """Run the gcloud auth login command."""
    gcloud_path = _find_executable("gcloud")
    print(f"{BLUE}Authenticating with Google Cloud...{NC}")
    _run_command([gcloud_path, "auth", "login"])
    print(f"{GREEN}Authentication complete.{NC}")


def _test_gcp_credentials(user: str, impersonation_sa: str) -> None:
    """Test GCP credentials with and without impersonation."""
    gcloud_path = _find_executable("gcloud")

    print(f"\n{BLUE}Testing credentials...{NC}")

    if user != "Not authenticated" and "Not authenticated" not in user:
        if impersonation_sa != "None":
            # Test user account first by temporarily unsetting impersonation
            orig_impersonation = _get_env_var(
                "CLOUDSDK_AUTH_IMPERSONATE_SERVICE_ACCOUNT"
            )
            if orig_impersonation:
                del os.environ["CLOUDSDK_AUTH_IMPERSONATE_SERVICE_ACCOUNT"]

            print(f"First with user account {user}:")
            cmd = [gcloud_path, "compute", "zones", "list", "--limit=1"]
            returncode, _, _ = _run_command(cmd, suppress_output=True, check=False)

            if returncode == 0:
                print(f"{GREEN}✓ User has direct GCP access{NC}")
            else:
                print(f"{YELLOW}✗ User lacks direct GCP access{NC}")

            # Restore impersonation and test with it
            if orig_impersonation:
                os.environ["CLOUDSDK_AUTH_IMPERSONATE_SERVICE_ACCOUNT"] = (
                    orig_impersonation
                )

            print(f"Then impersonating {impersonation_sa}:")
            returncode, _, _ = _run_command(cmd, suppress_output=True, check=False)

            if returncode == 0:
                print(f"{GREEN}✓ Successfully using devcon service account{NC}")
            else:
                print(
                    f"{RED}Failed to access GCP resources with impersonation. Check permissions.{NC}"
                )
        else:
            # Test user account directly (no impersonation)
            print(f"Using user account {user} (no impersonation):")
            cmd = [gcloud_path, "compute", "zones", "list", "--limit=1"]
            returncode, _, _ = _run_command(cmd, suppress_output=True, check=False)

            if returncode == 0:
                print(f"{GREEN}✓ Successfully using personal account{NC}")
            else:
                print(f"{RED}Failed to access GCP resources. Check permissions.{NC}")


# --- AWS Functions ---
def _unset_aws_static_creds() -> None:
    """Unset static AWS credential environment variables."""
    _modify_rc_files("AWS_ACCESS_KEY_ID", None)
    _modify_rc_files("AWS_SECRET_ACCESS_KEY", None)
    _modify_rc_files("AWS_SESSION_TOKEN", None)


def _set_aws_profile(profile: str) -> None:
    """Set and persist AWS profile in environment and RC files."""
    _modify_rc_files("AWS_PROFILE", profile)
    _unset_aws_static_creds()


def _get_current_aws_profile() -> str:
    """Get the current AWS profile."""
    # Check environment variable first
    profile = _get_env_var("AWS_PROFILE")
    if profile:
        return profile

    # Try using aws command to check
    aws_path = _find_executable("aws")
    try:
        cmd = [aws_path, "configure", "list", "--no-cli-pager"]
        _, stdout, _ = _run_command(cmd, capture=True, check=False)

        # Extract profile from output
        profile_match = re.search(r"profile\s+(\S+)", stdout)
        if profile_match and profile_match.group(1) not in ("<not", "not"):
            return profile_match.group(1)
    except:
        pass

    # Default if nothing else works
    return AWS_DEFAULT_PROFILE


def _is_aws_profile_authenticated(profile: str) -> bool:
    """Check if an AWS profile has valid credentials."""
    aws_path = _find_executable("aws")
    cmd = [
        aws_path,
        "sts",
        "get-caller-identity",
        "--profile",
        profile,
        "--no-cli-pager",
    ]
    returncode, _, _ = _run_command(cmd, suppress_output=True, check=False)
    return returncode == 0


def _run_aws_sso_login(profile: str) -> None:
    """Run the AWS SSO login command for a specific profile."""
    aws_path = _find_executable("aws")
    print(f"{BLUE}Running 'aws sso login --profile {profile}'...{NC}")
    _run_command([aws_path, "sso", "login", "--profile", profile])
    print(f"{GREEN}Authentication complete.{NC}")


def _get_available_aws_profiles() -> List[str]:
    """Get list of available AWS profiles from config file."""
    profiles = []

    if not AWS_CONFIG_FILE.exists():
        return profiles

    try:
        with open(AWS_CONFIG_FILE, "r") as f:
            lines = f.readlines()

        for line in lines:
            # Match [profile name] or [name] if default profile
            match = re.match(r"^\[(?:profile\s+)?([^\]]+)\]", line.strip())
            if match:
                profiles.append(match.group(1))
    except:
        pass

    return profiles


# --- Typer Applications ---
gcp_app = typer.Typer(help="Manage GCP authentication and impersonation.")
aws_app = typer.Typer(help="Manage AWS SSO authentication.")


# --- GCP Commands ---
@gcp_app.command("status")
def gcp_status():
    """Show current GCP authentication and impersonation status."""
    user_account = _get_current_gcp_user()
    impersonated_sa = _get_current_gcp_impersonation()

    print(f"{BLUE}GCP Status:{NC}")
    print(f"User account:       {GREEN}{user_account}{NC}")
    print(f"Service account:    {GREEN}{impersonated_sa}{NC}")
    print(f"Project:            {GREEN}{GCP_PROJECT_ID}{NC}")
    print(
        f"Mode:               {GREEN}{'Service account impersonation' if impersonated_sa != 'None' else 'Personal account'}{NC}"
    )

    _test_gcp_credentials(user_account, impersonated_sa)


@gcp_app.command("login")
def gcp_login():
    """Authenticate with GCP using your Google account."""
    _run_gcloud_login()
    print("\nTo activate devcon service account impersonation, run:")
    print(f'  {YELLOW}eval "$(dh gcp use-devcon --export)"{NC}')
    print("To use your personal account permissions, run:")
    print(f'  {YELLOW}eval "$(dh gcp use-user --export)"{NC}')


@gcp_app.command("use-devcon")
def gcp_use_devcon(
    export: bool = typer.Option(
        False, "--export", "-x", help="Print export commands for the current shell."
    ),
    auth_first: bool = typer.Option(
        False, "--auth", "-a", help="Authenticate user first if needed."
    ),
):
    """Switch to devcon service account impersonation mode."""
    if not _is_gcp_user_authenticated():
        if auth_first:
            print(
                f"{YELLOW}You need to authenticate first. Running authentication...{NC}",
                file=sys.stderr,
            )
            _run_gcloud_login()
        else:
            print(
                f"{RED}Error: Not authenticated with GCP. Run 'dh gcp login' first or use --auth flag.{NC}",
                file=sys.stderr,
            )
            sys.exit(1)

    # Modify RC files to persist across sessions
    _modify_rc_files("CLOUDSDK_AUTH_IMPERSONATE_SERVICE_ACCOUNT", f"'{GCP_DEVCON_SA}'")
    _modify_rc_files("GOOGLE_CLOUD_PROJECT", f"'{GCP_PROJECT_ID}'")

    if export:
        # Print export commands for the current shell to stdout
        print(f"export CLOUDSDK_AUTH_IMPERSONATE_SERVICE_ACCOUNT='{GCP_DEVCON_SA}'")
        print(f"export GOOGLE_CLOUD_PROJECT='{GCP_PROJECT_ID}'")

        # Print confirmation to stderr so it doesn't affect eval
        print(
            f"{GREEN}GCP service account impersonation for '{GCP_DEVCON_SA}' set up successfully.{NC}",
            file=sys.stderr,
        )
        print(f"{GREEN}You now have standard devcon permissions.{NC}", file=sys.stderr)
    else:
        # Just print confirmation
        print(
            f"{GREEN}Switched to devcon service account impersonation. You now have standard devcon permissions.{NC}"
        )
        print(
            f"Changes will take effect in new shell sessions. To apply in current shell, run:"
        )
        print(f'  {YELLOW}eval "$(dh gcp use-devcon --export)"{NC}')


@gcp_app.command("use-user")
def gcp_use_user(
    export: bool = typer.Option(
        False, "--export", "-x", help="Print export commands for the current shell."
    ),
    auth_first: bool = typer.Option(
        False, "--auth", "-a", help="Authenticate user first if needed."
    ),
):
    """Switch to personal account mode (no impersonation)."""
    if not _is_gcp_user_authenticated():
        if auth_first:
            print(
                f"{YELLOW}You need to authenticate first. Running authentication...{NC}",
                file=sys.stderr,
            )
            _run_gcloud_login()
        else:
            print(
                f"{RED}Error: Not authenticated with GCP. Run 'dh gcp login' first or use --auth flag.{NC}",
                file=sys.stderr,
            )
            sys.exit(1)

    # Modify RC files to persist across sessions
    _modify_rc_files("CLOUDSDK_AUTH_IMPERSONATE_SERVICE_ACCOUNT", None)
    _modify_rc_files("GOOGLE_CLOUD_PROJECT", f"'{GCP_PROJECT_ID}'")

    if export:
        # Print export commands for the current shell to stdout
        print(f"unset CLOUDSDK_AUTH_IMPERSONATE_SERVICE_ACCOUNT")
        print(f"export GOOGLE_CLOUD_PROJECT='{GCP_PROJECT_ID}'")

        # Print confirmation to stderr so it doesn't affect eval
        print(
            f"{GREEN}Switched to personal account mode. You are now using your own permissions.{NC}",
            file=sys.stderr,
        )
    else:
        # Just print confirmation
        print(
            f"{GREEN}Switched to personal account mode. You are now using your own permissions.{NC}"
        )
        print(
            f"Changes will take effect in new shell sessions. To apply in current shell, run:"
        )
        print(f'  {YELLOW}eval "$(dh gcp use-user --export)"{NC}')


# --- AWS Commands ---
@aws_app.command("status")
def aws_status(
    profile: Optional[str] = typer.Option(
        None, "--profile", "-p", help="Check specific profile instead of current."
    )
):
    """Show current AWS authentication status."""
    target_profile = profile or _get_current_aws_profile()
    print(f"{BLUE}AWS profile:{NC} {GREEN}{target_profile}{NC}")

    if _is_aws_profile_authenticated(target_profile):
        print(f"Credential status: {GREEN}valid{NC}")
        # Get detailed identity information
        aws_path = _find_executable("aws")
        _run_command(
            [aws_path, "sts", "get-caller-identity", "--profile", target_profile]
        )
    else:
        print(f"Credential status: {RED}not authenticated{NC}")
        print(f"\nTo authenticate, run:")
        print(f"  {YELLOW}dh aws login --profile {target_profile}{NC}")


@aws_app.command("login")
def aws_login(
    profile: Optional[str] = typer.Option(
        None, "--profile", "-p", help="Login to specific profile instead of current."
    )
):
    """Login to AWS SSO with the specified or current profile."""
    target_profile = profile or _get_current_aws_profile()
    _run_aws_sso_login(target_profile)
    print(f"\nTo activate profile {target_profile} in your current shell, run:")
    print(f'  {YELLOW}eval "$(dh aws use-profile {target_profile} --export)"{NC}')


@aws_app.command("use-profile")
def aws_use_profile(
    profile: str = typer.Argument(..., help="AWS profile name to activate."),
    export: bool = typer.Option(
        False, "--export", "-x", help="Print export commands for the current shell."
    ),
    auto_login: bool = typer.Option(
        False, "--auto-login", "-a", help="Run 'aws sso login' if needed."
    ),
):
    """Switch to a specific AWS profile."""
    # Modify RC files to persist across sessions
    _set_aws_profile(profile)

    if auto_login and not _is_aws_profile_authenticated(profile):
        print(
            f"{YELLOW}Profile '{profile}' not authenticated. Running 'aws sso login'...{NC}",
            file=sys.stderr,
        )
        _run_aws_sso_login(profile)

    if export:
        # Print export commands for the current shell to stdout
        print(f"export AWS_PROFILE='{profile}'")
        print("unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN")

        # Print confirmation to stderr so it doesn't affect eval
        print(
            f"{GREEN}AWS profile '{profile}' exported successfully.{NC}",
            file=sys.stderr,
        )
    else:
        # Just print confirmation
        print(f"{GREEN}AWS profile set to '{profile}' and persisted to RC files.{NC}")
        print(
            f"Changes will take effect in new shell sessions. To apply in current shell, run:"
        )
        print(f'  {YELLOW}eval "$(dh aws use-profile {profile} --export)"{NC}')


@aws_app.command("interactive")
def aws_interactive():
    """Launch interactive AWS profile management menu."""
    current_profile = _get_current_aws_profile()

    print(f"{BLUE}AWS SSO helper – current profile: {GREEN}{current_profile}{NC}")

    while True:
        choice = questionary.select(
            "Choose an option:",
            choices=[
                f"Authenticate current profile ({current_profile})",
                "Switch profile",
                "Show status",
                "Exit",
            ],
        ).ask()

        if choice == f"Authenticate current profile ({current_profile})":
            _run_aws_sso_login(current_profile)
            print(f"{GREEN}Authentication complete.{NC}")
            print(f"To activate in your current shell, run:")
            print(
                f'  {YELLOW}eval "$(dh aws use-profile {current_profile} --export)"{NC}'
            )

        elif choice == "Switch profile":
            available_profiles = _get_available_aws_profiles()

            if not available_profiles:
                print(f"{RED}No AWS profiles found. Check your ~/.aws/config file.{NC}")
                continue

            for i, prof in enumerate(available_profiles, 1):
                print(f"{i}) {prof}")

            # Get profile selection by number or name
            sel = questionary.text("Select profile number or name:").ask()

            if sel.isdigit() and 1 <= int(sel) <= len(available_profiles):
                new_profile = available_profiles[int(sel) - 1]
            elif sel in available_profiles:
                new_profile = sel
            else:
                print(f"{RED}Invalid selection{NC}")
                continue

            _set_aws_profile(new_profile)
            print(f"{GREEN}Switched to profile {new_profile}{NC}")
            print(f"To activate in your current shell, run:")
            print(f'  {YELLOW}eval "$(dh aws use-profile {new_profile} --export)"{NC}')

            # Ask if they want to authenticate now
            if questionary.confirm(
                "Authenticate this profile now?", default=False
            ).ask():
                _run_aws_sso_login(new_profile)
                print(f"{GREEN}Authentication complete.{NC}")
                print(f"To activate in your current shell, run:")
                print(
                    f'  {YELLOW}eval "$(dh aws use-profile {new_profile} --export)"{NC}'
                )

        elif choice == "Show status":
            # Fix: Explicitly pass None for the profile parameter
            aws_status(profile=None)

        elif choice == "Exit":
            print(f"To activate profile {current_profile} in your current shell, run:")
            print(
                f'  {YELLOW}eval "$(dh aws use-profile {current_profile} --export)"{NC}'
            )
            break

        print()  # Add newline between iterations
