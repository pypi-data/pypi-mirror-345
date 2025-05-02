import boto3
import sys
import argparse
from typing import Dict, Tuple, Optional
from botocore.exceptions import ClientError
import subprocess


class AWSEC2:
    def __init__(
        self,
        profile_name: Optional[str] = None,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        region: Optional[str] = None
    ):
        """Initialize AWSEC2 with AWS credentials or profile."""
        if profile_name:
            self.session = boto3.Session(profile_name=profile_name, region_name=region)
        elif access_key and secret_key:
            self.session = boto3.Session(
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region
            )
        else:
            raise ValueError("Either profile_name or access_key/secret_key must be provided.")

        self.ec2_resource = self.session.resource('ec2')
        self.ec2_client = self.session.client('ec2')
        self.ssm_client = self.session.client('ssm')
        self.profile_name = profile_name if profile_name else "custom_credentials"

    def get_instances(self) -> Tuple[Dict[str, str], Dict[str, str]]:
        """Get running and stopped instances."""
        instances = {}
        instances_off = {}
        try:
            for instance in self.ec2_resource.instances.all():
                name = next((tag['Value'] for tag in instance.tags or [] if tag['Key'] == 'Name'), '')
                if instance.state['Name'] == 'running':
                    instances[name] = instance.id
                else:
                    instances_off[name] = instance.id
        except ClientError as e:
            print(f"Error fetching instances: {e}")
            sys.exit(1)
        return instances, instances_off

    def list_instances(self):
        """List all running and stopped instances."""
        running, stopped = self.get_instances()
        print("Running instances:")
        for name, instance_id in running.items():
            print(f"\tId: {instance_id}, Name: {name}")
        print("Stopped instances:")
        for name, instance_id in stopped.items():
            print(f"\tId: {instance_id}, Name: {name}")

    def kill_tunnels(self):
        """Terminate all active SSM sessions."""
        try:
            active_sessions = self.ssm_client.describe_sessions(State='Active')
            sessions = active_sessions.get('Sessions', [])
            if sessions:
                print(f"There are {len(sessions)} active sessions, killing now...", end='')
                for session in sessions:
                    session_id = session['SessionId']
                    self.ssm_client.terminate_session(SessionId=session_id)
                print("DONE!")
            else:
                print("No active sessions found.")
        except ClientError as e:
            print(f"Error killing tunnels: {e}")

    def start_instance(self, name: str):
        """Start a stopped EC2 instance."""
        _, stopped = self.get_instances()
        if name not in stopped:
            print(f"Instance {name} not found or already running.")
            return
        try:
            print(f"Starting instance {name}...")
            response = self.ec2_client.start_instances(InstanceIds=[stopped[name]])
            print(response)
        except ClientError as e:
            print(f"Error starting instance: {e}")

    def stop_instance(self, name: str):
        """Stop a running EC2 instance."""
        running, _ = self.get_instances()
        if name not in running:
            print(f"Instance {name} not found or already stopped.")
            return
        try:
            print(f"Stopping instance {name}...")
            response = self.ec2_client.stop_instances(InstanceIds=[running[name]])
            print(response)
        except ClientError as e:
            print(f"Error stopping instance: {e}")

    def sso_login(self):
        """Perform AWS SSO login using subprocess."""
        if not self.profile_name or self.profile_name == "custom_credentials":
            print("SSO login requires a profile name. Explicit credentials don't support SSO login.")
            return

        command = f"aws sso login --profile {self.profile_name}"
        process = subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )
        codeline = False
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output and output.strip():
                if codeline:
                    code = output.strip()
                    print(f"This is the code: {code}")
                else:
                    print(output.strip())
                if output.strip() == 'Then enter the code:':
                    codeline = True
        if process.poll() == 0:
            print("Login successful!")

    def open_tunnel(self, target: str, local_port: int, remote_port: int):
        """Open an SSM port forwarding tunnel."""
        running, _ = self.get_instances()
        if target not in running:
            print(f"Instance {target} not found or not running.")
            return

        command = (
            f"aws ssm start-session --target {running[target]} "
            f"--document-name AWS-StartPortForwardingSession "
            f"--parameters localPortNumber={local_port},portNumber={remote_port} "
            f"--profile {self.profile_name if self.profile_name != 'custom_credentials' else ''}"
        ).strip()

        print(f"Opening tunnel to {target}\nLocal Port: {local_port}\nRemote Port: {remote_port}\n")
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
        )

        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output and output.strip():
                print(output.strip())
        print("Port forwarding terminated!")


def parse_arguments():
    """Parse command-line arguments using argparse with default ordering."""
    parser = argparse.ArgumentParser(
        description="AWS EC2 Management and SSM Tunnel Tool",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # Global credential arguments (must be before subcommand)
    credential_group = parser.add_argument_group("AWS Credentials")
    credential_group.add_argument("--profile", type=str, help="AWS profile name to use")
    credential_group.add_argument("--access-key", type=str, help="AWS access key ID")
    credential_group.add_argument("--secret-key", type=str, help="AWS secret access key")
    credential_group.add_argument("--region", type=str, help="AWS region (e.g., us-east-1)")

    # Subparsers for commands
    subparsers = parser.add_subparsers(dest="command", help="Available commands", required=True)

    # List instances
    subparsers.add_parser("list", help="List all EC2 instances")

    # Kill tunnels
    subparsers.add_parser("kill", help="Kill all active SSM sessions")

    # Start instance
    parser_start = subparsers.add_parser("start", help="Start a stopped EC2 instance")
    parser_start.add_argument("instance_name", type=str, help="Name of the instance to start")

    # Stop instance
    parser_stop = subparsers.add_parser("stop", help="Stop a running EC2 instance")
    parser_stop.add_argument("instance_name", type=str, help="Name of the instance to stop")

    # SSO login
    subparsers.add_parser("login", help="Perform AWS SSO login")

    # Open tunnel
    parser_tunnel = subparsers.add_parser("tunnel", help="Open an SSM port forwarding tunnel")
    parser_tunnel.add_argument("target", type=str, help="Target instance name")
    parser_tunnel.add_argument("local_port", type=int, help="Local port number")
    parser_tunnel.add_argument("remote_port", type=int, help="Remote port number")

    return parser.parse_args()


def main():
    args = parse_arguments()

    # Initialize AWSEC2 with provided credentials or default profile
    try:
        if args.profile:
            aws_manager = AWSEC2(profile_name=args.profile, region=args.region)
        elif args.access_key and args.secret_key:
            aws_manager = AWSEC2(
                access_key=args.access_key,
                secret_key=args.secret_key,
                region=args.region
            )
        else:
            aws_manager = AWSEC2(profile_name="default")
    except ValueError as e:
        print(f"Error initializing AWS session: {e}")
        sys.exit(1)

    # Execute the requested command
    if args.command == "list":
        aws_manager.list_instances()
    elif args.command == "kill":
        aws_manager.kill_tunnels()
    elif args.command == "start":
        aws_manager.start_instance(args.instance_name)
    elif args.command == "stop":
        aws_manager.stop_instance(args.instance_name)
    elif args.command == "login":
        aws_manager.sso_login()
    elif args.command == "tunnel":
        aws_manager.open_tunnel(args.target, args.local_port, args.remote_port)


if __name__ == "__main__":
    main()