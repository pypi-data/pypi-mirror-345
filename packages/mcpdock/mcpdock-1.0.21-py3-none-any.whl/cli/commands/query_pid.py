from cli.utils.logger import verbose
import click
import json
import sys
from ..utils.run_query_pid_by_packagename import query_pid_by_packagename


@click.command("query-pid")
@click.argument("package_names", type=click.STRING, nargs=-1, required=True)
@click.option("--json-output", is_flag=True, help="Output results in JSON format")
def query_pid(package_names, json_output):
    """
    Check if the processes for the specified package names are running.

    PACKAGE_NAMES: One or more package names to check.
    Returns the running status for each package name. If the --json-output option is used, outputs the result in JSON format.
    """
    try:
        # Get the running status for each package name
        status_dict = query_pid_by_packagename(list(package_names))

        if json_output:
            # Output results in JSON format
            print(json.dumps(status_dict))
        else:
            # Output results in plain text format
            for package_name, is_running in status_dict.items():
                status = "Running" if is_running else "Not running"
                verbose(f"Package name '{package_name}': {status}")

        # Check if any process is running
        any_running = any(status_dict.values())
        exit(0 if any_running else 1)
    except Exception as e:
        print(f"Error occurred while executing query-pid command: {e}", file=sys.stderr)
        exit(1)  # Return 1 to indicate an error
