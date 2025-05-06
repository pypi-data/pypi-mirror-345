"""Wrapper for executing shell commands using Python's subprocess library.



This module provides a streamlined interface for constructing and executing
command-line processes. It simplifies handling subprocess calls by dynamically
building command-line arguments from configuration parameters (e.g., `config.json`),
managing environment variables, and providing structured error handling.

Features:
- Builds command-line arguments dynamically from key-value parameter mappings.
- Executes shell commands with logging, error handling, and real-time output streaming.
- Supports dry-run mode for debugging without executing commands.
- Captures `stdout` and `stderr`, raising an exception for non-zero exit codes.

Examples:
    >>> command = ["ls"]
    >>> param_list = {"l": True, "a": True, "h": True}
    >>> command = build_command_list(command, param_list)
    >>> command
    ["ls", "-l", "-a", "-h"]
    >>> exec_command(command)

    Another example using parameters with values:
    >>> command = ["du"]
    >>> params = {"a": True, "human-readable": True, "max-depth": 3}
    >>> command = build_command_list(command, params)
    >>> command
    ["du", "-a", "--human-readable", "--max-depth=3"]
    >>> params = {"dir1": ".", "dir2": "/tmp"}
    >>> command = build_command_list(command, params, include_keys=False)
    >>> command
    ["du", ".", "/tmp"]
    >>> exec_command(command)

These examples demonstrate how command-line parameters can be dynamically
constructed and executed from gear configuration options.
"""

import logging
import shlex
import subprocess as sp
import typing as t

log = logging.getLogger(__name__)


def _remove_prohibited_values(param_list: t.Dict[str, any]) -> t.Dict[str, any]:
    """
    Removes `None` values and empty strings from a parameter dictionary.

    Args:
        param_list (Dict[str, any]): Dictionary of command-line parameters.

    Returns:
        Dict[str, any]: A cleaned dictionary with empty values removed.
    """
    param_list_new = param_list.copy()
    for key, value in param_list.items():
        if not value or value == "":
            param_list_new.pop(key)
            log.warning(f'Removing parameter with empty value for key "{key}".')
    return param_list_new


def build_command_list(
    command: t.List[str], param_list: t.Dict[str, any], include_keys: bool = True
) -> t.List[str]:
    """Constructs a command-line argument list for subprocess execution.

    Args:
        command (List[str]): Base command (e.g., `["ls"]`), including required parameters.
        param_list (Dict[str, any]): Dictionary of key-value pairs representing command-line arguments.
            - Boolean values (`True`) result in flags (`-k` or `--key`).
            - String/integer values are formatted as `--key=value` or `-k value`.
            - `None` or empty strings are ignored.
        include_keys (bool, optional): Whether to include parameter keys in the command list. Defaults to True.

    Returns:
        List[str]: A formatted command list suitable for `subprocess.Popen`.

    Example:
        >>> command = ["du"]
        >>> params = {"a": True, "human-readable": True, "max-depth": 3}
        >>> command = build_command_list(command, params)
        >>> command
        ["du", "-a", "--human-readable", "--max-depth=3"]
    """
    param_list = _remove_prohibited_values(param_list)
    for key in param_list.keys():
        # Single character command-line parameters are preceded by a single "-"
        if len(key) == 1:
            # If Param is boolean and true, include, else exclude
            if isinstance(param_list[key], bool) and param_list[key]:
                command.append("-" + key)
            else:
                if include_keys:
                    command.append("-" + key)
                if str(param_list[key]):
                    command.append(str(param_list[key]))
        # Multi-Character command-line parameters are preceded by a double "--"
        # If Param is boolean and true include, else exclude
        elif isinstance(param_list[key], bool):
            if param_list[key] and include_keys:
                command.append("--" + key)
        else:
            item = ""
            if include_keys:
                item = "--" + key
                item = item + "="
            item = item + str(param_list[key])
            command.append(item)
    return command


def exec_command(
    command: t.List[str],
    dry_run: bool = False,
    environ: t.Optional[t.Dict[str, str]] = None,
    shell: bool = False,
    stdout_msg: t.Optional[str] = None,
    cont_output: bool = False,
) -> t.Tuple[str, str, int]:
    """
    Executes a shell command using the subprocess module.

    Args:
        command (List[str]): List of command-line arguments, starting with the command itself.
        dry_run (bool, optional): If True, prints the command without executing it. Defaults to False.
        environ (Optional[Dict[str, str]], optional): Environment variables for the command. Defaults to None.
        shell (bool, optional): If True, runs the command as a single shell string (enables redirects). Defaults to False.
        stdout_msg (Optional[str], optional): Custom log message for stdout redirection. Defaults to None.
        cont_output (bool, optional): If True, streams stdout in real-time. Defaults to False.

    Returns:
        Tuple[str, str, int]: Tuple containing:
            - stdout (str): Standard output from the command.
            - stderr (str): Standard error output.
            - returncode (int): Command exit status.

    Raises:
        RuntimeError: If the command returns a non-zero exit code.

    Example:
            >>> command = ["du"]
            >>> params = {"a": True, "human-readable": True, "max-depth":3}
            >>> command = build_command_list(command, params)
            >>> params = {"dir1":".","dir2":"/tmp"}
            >>> command = build_command_list(command, params, include_keys=False)
            >>> exec_command(command)
    """
    log.info(f"Executing command: \n {' '.join(command)} \n\n")
    if not dry_run:
        # use shlex to sanitize the command
        sanitized_command = [
            shlex.quote(arg) if ">" not in arg else arg for arg in command
        ]

        # The "shell" parameter is needed for bash output redirects
        # (e.g. >,>>,&>)
        if shell:
            run_command = " ".join(sanitized_command)
        else:
            run_command = sanitized_command

        result = sp.Popen(
            run_command,
            stdout=sp.PIPE,
            stderr=sp.PIPE,
            universal_newlines=True,
            env=environ,
            shell=shell,
        )

        # log that we are using an alternate stdout message
        if stdout_msg is not None:
            log.info(stdout_msg)

        # if continuous stdout is desired... and we are not redirecting output
        if cont_output and not (shell and (">" in command)) and (stdout_msg is None):
            while True:
                stdout = result.stdout.readline()
                if stdout == "" and result.poll() is not None:
                    break
                if stdout:
                    print(stdout.rstrip())

            returncode = result.poll()
            stderr = "".join(result.stderr.readlines())
        else:
            stdout, stderr = result.communicate()

            returncode = result.returncode
            if stdout_msg is None:
                log.info(stdout)

        log.info(f"Command return code: {returncode}")

        if returncode != 0:
            log.error(stderr)
            raise RuntimeError(f"The following command has failed: \n{command}")

        return stdout, stderr, returncode
