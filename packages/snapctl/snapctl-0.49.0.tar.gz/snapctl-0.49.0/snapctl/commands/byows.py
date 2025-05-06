"""
  BYOWs CLI commands
"""
import os
import platform
import subprocess
import shutil
import time
import json
from pathlib import Path
from typing import Union
import threading
import requests
from requests.exceptions import RequestException, HTTPError
from rich.progress import Progress, SpinnerColumn, TextColumn
from snapctl.config.constants import SERVER_CALL_TIMEOUT, SNAPCTL_INPUT_ERROR, \
    SNAPCTL_BYOWS_GENERIC_ERROR, SNAPCTL_DEPENDENCY_MISSING
from snapctl.utils.helper import snapctl_error, snapctl_success, get_dot_snapser_dir
from snapctl.utils.echo import info, warning

class Byows:
    """
      CLI commands exposed for a Bring your own Workstation
    """
    SUBCOMMANDS = ['attach']
    SSH_FILE = 'id_snapser_byows_attach_ed25519'
    PORT_FORWARD_TTL = 3600 * 24 * 7
    BYOWS_ENV_FILE = 'byows_env_setup'

    def __init__(
            self, *, subcommand: str, base_url: str, base_snapend_url: str, api_key: Union[str, None],
            snapend_id: Union[str, None] = None, byosnap_id: Union[str, None] = None,
            http_port: Union[int, None] = None, grpc_port: Union[int, None] = None,

    ) -> None:
        self.subcommand: str = subcommand
        self.base_url: str = base_url
        self.base_snapend_url: str = base_snapend_url
        self.api_key: Union[str, None] = api_key
        self.snapend_id: Union[str, None] = snapend_id
        self.byosnap_id: Union[str, None] = byosnap_id
        self.http_port: Union[int, None] = http_port
        self.grpc_port: Union[int, None] = grpc_port
        self.validate_input()

    def validate_input(self) -> None:
        """
          Validator
        """
        # Check API Key and Base URL
        if not self.api_key or self.base_url == '':
            snapctl_error(
                message="Missing API Key.", code=SNAPCTL_INPUT_ERROR)
        # Check subcommand
        if not self.subcommand in Byows.SUBCOMMANDS:
            snapctl_error(
                message="Invalid command. Valid commands are " +
                f"{', '.join(Byows.SUBCOMMANDS)}.",
                code=SNAPCTL_INPUT_ERROR)
        # Check sdk-download commands
        if self.subcommand == 'attach':
            if not shutil.which("ssh"):
                snapctl_error("ssh is not installed or not in PATH",
                              SNAPCTL_DEPENDENCY_MISSING)
            if self.snapend_id is None or self.snapend_id == '':
                snapctl_error(
                    message="Missing Input --snapend-id=$your_snapend_id",
                    code=SNAPCTL_INPUT_ERROR)
            if self.byosnap_id is None or self.byosnap_id == '':
                snapctl_error(
                    message="Missing Input --byosnap-id=$your_byosnap_id",
                    code=SNAPCTL_INPUT_ERROR)
            if self.http_port is None and self.grpc_port is None:
                snapctl_error(
                    message="Missing Input. One of --http-port=$your_local_server_port or --grpc-port=$your_local_server_port is required.",
                    code=SNAPCTL_INPUT_ERROR)
            

    # Static methods
    @staticmethod
    def stream_output(pipe):
        '''
        Stream the output of a subprocess to the console.
        This function reads lines from the pipe and prints them to the console.
        '''
        for line in iter(pipe.readline, b''):
            info(line.decode().rstrip())

    @staticmethod
    def _write_export_command_to_console(snap_ids, port):
        '''
        TODO: This is not used anymore
        Generate export commands for the given snap IDs and port.
        '''
        env_vars = []

        for snap_id in snap_ids:
            upper_id = snap_id.upper()
            env_vars.append(f"SNAPEND_{upper_id}_GRPC_URL=localhost:{port}")
            env_vars.append(
                f"SNAPEND_{upper_id}_HTTP_URL=http://localhost:{port}")

        system = platform.system()

        if system == "Windows":
            # PowerShell syntax
            return "; ".join([f'$env:{env_vars[i].replace("=", " = ")}; $env:{env_vars[i+1].replace("=", " = ")}'
                              for i in range(0, len(env_vars), 2)])
        else:
            # Linux or macOS bash/zsh syntax
            return "export \\\n" + " \\\n".join([f"  {env_vars[i]} {env_vars[i+1]}"
                                                for i in range(0, len(env_vars), 2)])

    @staticmethod
    def _generate_env_file(snap_ids, port):
        '''
        Generate an environment file with the given snap IDs and port.
        '''
        env_lines = []

        for snap_id in snap_ids:
            upper_id = snap_id.upper()
            env_lines.append(
                f"export SNAPEND_{upper_id}_GRPC_URL=localhost:{port}")
            env_lines.append(
                f"export SNAPEND_{upper_id}_HTTP_URL=http://localhost:{port}")

        system = platform.system()
        filename = f"{Byows.BYOWS_ENV_FILE}.ps1" if system == "Windows" else \
            f"{Byows.BYOWS_ENV_FILE}.sh"
        env_file = get_dot_snapser_dir() / filename

        with env_file.open("w") as f:
            if system == "Windows":
                for line in env_lines:
                    var, value = line.replace("export ", "").split("=", 1)
                    f.write(f'$env:{var} = "{value}"\n')
            else:
                for line in env_lines:
                    f.write(f"{line}\n")

        return env_file

    @staticmethod
    def _generate_env(snap_ids, port):
        '''
        Generate environment variables for the given snap IDs and port.
        '''
        env_file = Byows._generate_env_file(snap_ids, port)
        info(f"Environment variables written to {env_file}")
        system = platform.system()
        if system == "Windows":
            info(
                f"Run the following command to set them in your session:\n\n    . {env_file}\n")
        else:
            info(
                f"Run the following command to set them in your shell:\n\n    source {env_file}\n")

    @staticmethod
    def _format_portal_http_error(msg, http_err, response):
        """
        Format a portal HTTP error response for display.
        Args:
            http_err: The HTTPError exception.
            response: The HTTP response object.
        Returns:
            str: A nicely formatted error message.
        """
        try:
            # Check if the response content is JSON-like
            # FIXME: The portal should always return application/json for errors, but doesn't.
            if response.text.strip().startswith('{'):
                error_data = response.json()
                api_error_code = error_data.get(
                    "api_error_code", "Unknown Code")
                message = error_data.get("message", "No message provided")
                details = error_data.get("details", [])
                if details:
                    details_str = "\n  - " + "\n  - ".join(details)
                else:
                    details_str = ""
                return (
                    f"Message: {msg}\n"
                    f"Exception: {http_err}\n"
                    f"Snapser Error Code: {api_error_code}\n"
                    f"Error: {message}{details_str}"
                )
        except Exception:
            pass  # Fallback to default error formatting if parsing fails

        # Default error message if not JSON or parsing fails
        return f"HTTP Error {http_err.response.status_code}: {http_err.response.reason}\nResponse: {response.text.strip()}"

    # Private methods
    def _setup_port_forward(
            self, private_key, public_key, snapend_id, snap_id, port, reverse_port, reverse_grpc_port,
            incoming_http, incoming_grpc, outgoing_http, snap_ids, ssh_connect_addr) -> bool:
        '''
        Setup the SSH port forward
        '''
        dot_snapser_dir = get_dot_snapser_dir()
        id_file = dot_snapser_dir / Byows.SSH_FILE
        pub_file = dot_snapser_dir / f'{Byows.SSH_FILE}.pub'

        # Write public and private key files
        with open(id_file, 'w') as f:
            f.write(private_key)
            if os.name != 'nt':
                # Only chmod on Unix-like systems
                os.chmod(id_file, 0o600)

        # write the public key
        with open(pub_file, 'w') as f:
            f.write(public_key)

        # Let user know about the forwarding
        # TODO: AJ, needs to be the proper base url
        info(f"Forwarding {self.base_snapend_url}/{snapend_id}/v1/{snap_id}" +
             f"-> http://localhost:{incoming_http}/*")
        info(
            f"Your BYOSnap HTTP server should listen on: localhost:{incoming_http}")
        info(
            f"Connect to other snaps over HTTP on: localhost:{outgoing_http}")
        Byows._generate_env(snap_ids, port)
        info('Press <ctrl-c> to stop forwarding')

        # TODO: ??? AJ get the ssh host for the current environ from BYOWS_SSH_HOSTS contact in endpoints.py
        ssh_addr = ssh_connect_addr
        if not ssh_addr:
            snapctl_error(message=f"{env} is missing or empty in BYOWS_SSH_HOSTS", code=SNAPCTL_INPUT_ERROR)

        # Extract the port from the ssh_addr if present, otherwise default to 22
        if ':' in ssh_addr:
            ssh_host, ssh_port = ssh_addr.split(':')
            ssh_port = int(ssh_port)
        else:
            ssh_host = ssh_addr
            ssh_port = 22

        ssh_command = [
            'ssh',
            '-o', 'ServerAliveInterval=60',
            '-o', 'StrictHostKeyChecking=no',
            '-o', 'UserKnownHostsFile=/dev/null',
            '-p', str(ssh_port),
            '-i', str(id_file),
            '-N',
            '-L', f'{outgoing_http}:localhost:{port}',
            '-R', f'{reverse_port}:localhost:{incoming_http}',
        ]
        if incoming_grpc:
            ssh_command += ['-R', f'{reverse_grpc_port}:localhost:{incoming_grpc}']
        ssh_command += [ssh_host]

        # print(f'Running SSH command: {ssh_command}')
        process = None
        try:
            process = subprocess.Popen(
                ssh_command,
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Give it a few seconds to report any immediate errors
            timeout_seconds = 5
            start_time = time.time()
            while True:
                if process.poll() is not None:
                    # Process exited early — likely an error
                    stderr_output = process.stderr.read().decode().strip()
                    if stderr_output:
                        info(f"[SSH Error] {stderr_output}")
                    else:
                        warning("SSH process exited unexpectedly with no output.")
                    return False

                if time.time() - start_time > timeout_seconds:
                    break

                time.sleep(0.2)

            # Start background thread to stream live stderr
            threading.Thread(target=Byows.stream_output, args=(
                process.stderr,), daemon=True).start()

            # Now block for the full tunnel lifetime
            process.wait(timeout=Byows.PORT_FORWARD_TTL)
        except KeyboardInterrupt:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                warning('SSH process did not shut down gracefully.')

            info('Shutting down port forward...')

            try:
                url = f"{self.base_url}/v1/snapser-api/byows/snapends/" + \
                    f"{self.snapend_id}/snaps/{self.byosnap_id}/enabled"
                res = requests.put(
                    url, headers={'api-key': self.api_key}, json=False, timeout=SERVER_CALL_TIMEOUT)
                res.raise_for_status()
                info('Forwarding disabled')
            except HTTPError as http_err:
                snapctl_error(
                    message=Byows._format_portal_http_error(
                        "Unable to disable BYOWs", http_err, res),
                    code=SNAPCTL_BYOWS_GENERIC_ERROR
                )
                return False
            except RequestException as req_err:
                warning(
                    f"Response Status Code: {res.status_code}, Body: {res.text}")
                snapctl_error(
                    message=f"Request Exception: Unable to disable BYOWs {req_err}",
                    code=SNAPCTL_BYOWS_GENERIC_ERROR
                )
                return False
            except Exception as e:
                snapctl_error(
                    message=f"Unexpected error occurred: {e}",
                    code=SNAPCTL_BYOWS_GENERIC_ERROR
                )
                return False

        except Exception as e:
            print('Error running SSH command:', e)
            return False
        finally:
            # Cleanup the SSH key files
            # Only remove the files if they exist
            try:
                id_file.unlink()
                pub_file.unlink()
            except Exception as e:
                warning(
                    f"Cleanup warning: Failed to delete SSH key files – {e}")
        return True

    # Commands
    def attach(self) -> bool:
        """
          BYOWs port forward
        """
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        )
        progress.start()
        progress.add_task(
            description='Setting up BYOWs port forward...', total=None)
        try:
            url = f"{self.base_url}/v1/snapser-api/byows/snapends/" + \
                f"{self.snapend_id}/snaps/{self.byosnap_id}"
            res = requests.put(
                url,
                headers={'api-key': self.api_key},
                json={
                    "snapend_id": self.snapend_id,
                    "snap_id": self.byosnap_id
                },
                timeout=SERVER_CALL_TIMEOUT
            )
            res.raise_for_status()
            response_json = res.json()

            # For debugging
            #print(f"BYOWS Response:\n{json.dumps(response_json, indent=2)}")

            if res.ok and 'workstationPort' in response_json and \
               'workstationReversePort' in response_json and \
               'snapendId' in response_json and \
               'proxyPrivateKey' in response_json and \
               'proxyPublicKey' in response_json:

                # We do not use the workstationReversePort now, we ask the user
                # to provide the port they want to use
                # incoming_http_port = response_json['workstationReversePort']
                incoming_http_port = self.http_port
                incoming_grpc_port = self.grpc_port

                outgoing_http_port = response_json['workstationPort']

                self._setup_port_forward(
                    response_json['proxyPrivateKey'],
                    response_json['proxyPublicKey'],
                    response_json['snapendId'],
                    response_json['snapId'],
                    response_json['workstationPort'],
                    response_json['workstationReversePort'],
                    response_json['workstationReverseGrpcPort'],
                    incoming_http_port,
                    incoming_grpc_port,
                    outgoing_http_port,
                    response_json['snapIds'],
                    response_json['sshConnectAddr'],
                )
                return snapctl_success(
                    message='complete', progress=progress)
            snapctl_error(
                message='Unable to setup port forward.',
                code=SNAPCTL_BYOWS_GENERIC_ERROR, progress=progress)
        except HTTPError as http_err:
            snapctl_error(
                message=Byows._format_portal_http_error(
                    "Unable to setup port forward", http_err, res),
                code=SNAPCTL_BYOWS_GENERIC_ERROR, progress=progress)
            snapctl_error(
                message=f"Server Error: Unable to setup port forward {http_err}",
                code=SNAPCTL_BYOWS_GENERIC_ERROR, progress=progress)
        except RequestException as e:
            snapctl_error(
                message=f"Exception: Unable to setup port forward {e}",
                code=SNAPCTL_BYOWS_GENERIC_ERROR, progress=progress)
        finally:
            progress.stop()
        snapctl_error(
            message='Failed to setup port forward.',
            code=SNAPCTL_BYOWS_GENERIC_ERROR, progress=progress)
