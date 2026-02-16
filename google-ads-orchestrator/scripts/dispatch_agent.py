#!/usr/bin/env python3
"""
Google Ads Orchestrator — Agent Dispatch Script

Handles SSH-based agent invocation on Machine B and monitors task completion.
Used during optimization cycles to trigger agents in sequence.

Usage:
    python3 dispatch_agent.py --machine-b-host 192.168.1.100 \
        --machine-b-user agent-runner \
        --agent google-ads-data-placement-analyst \
        --cycle 550e8400-e29b-41d4-a716-446655440000 \
        --task 660f8400-e29b-41d4-a716-446655440111 \
        --brand 770g8400-e29b-41d4-a716-446655440222 \
        [--wait] [--timeout 1800] [--poll-interval 30]
"""

import sys
import os
import json
import argparse
import subprocess
import time
from typing import Optional, Tuple
from datetime import datetime, timedelta
import uuid


# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


class AgentDispatcher:
    """Handles agent dispatch and monitoring."""

    AGENT_NAMES = {
        'data-placement': 'google-ads-data-placement-analyst',
        'creative-analyst': 'google-ads-creative-analyst',
        'post-click': 'google-ads-postclick-analyst',
        'competitive-intel': 'google-ads-competitive-intel',
        'creative-producer': 'google-ads-creative-producer',
        'campaign-creator': 'google-ads-campaign-creator',
        'campaign-monitor': 'google-ads-campaign-monitor',
    }

    def __init__(
        self,
        machine_b_host: str,
        machine_b_user: str,
        agent: str,
        cycle_id: str,
        task_id: str,
        brand_id: str,
        timeout: int = 1800,
        poll_interval: int = 30,
    ):
        self.machine_b_host = machine_b_host
        self.machine_b_user = machine_b_user
        self.agent = agent
        self.cycle_id = cycle_id
        self.task_id = task_id
        self.brand_id = brand_id
        self.timeout = timeout
        self.poll_interval = poll_interval

        # Resolve agent short name to full name
        if agent in self.AGENT_NAMES:
            self.agent_full = self.AGENT_NAMES[agent]
        else:
            self.agent_full = agent

        self.start_time = None
        self.end_time = None

    def log_info(self, message: str):
        """Log informational message."""
        msg = f"{BLUE}ℹ️{RESET}  {message}"
        print(msg)

    def log_success(self, message: str):
        """Log success message."""
        msg = f"{GREEN}✅{RESET} {message}"
        print(msg)

    def log_failure(self, message: str):
        """Log failure message."""
        msg = f"{RED}❌{RESET} {message}"
        print(msg)

    def log_warning(self, message: str):
        """Log warning message."""
        msg = f"{YELLOW}⚠️{RESET}  {message}"
        print(msg)

    def validate_inputs(self) -> bool:
        """Validate input parameters."""
        self.log_info("Validating input parameters...")

        # Validate UUIDs
        for uuid_str, name in [
            (self.cycle_id, "cycle_id"),
            (self.task_id, "task_id"),
            (self.brand_id, "brand_id"),
        ]:
            try:
                uuid.UUID(uuid_str)
            except ValueError:
                self.log_failure(f"Invalid {name}: {uuid_str}")
                return False

        # Validate agent name
        if not self.agent_full:
            self.log_failure(f"Unknown agent: {self.agent}")
            return False

        # Validate timeout
        if self.timeout < 60:
            self.log_failure("Timeout must be at least 60 seconds")
            return False

        self.log_success("Input validation passed")
        return True

    def test_ssh_connection(self) -> bool:
        """Test SSH connection to Machine B."""
        self.log_info(f"Testing SSH connection to {self.machine_b_user}@{self.machine_b_host}...")

        cmd = [
            "ssh",
            f"{self.machine_b_user}@{self.machine_b_host}",
            "echo CONNECTION_OK"
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0 and "CONNECTION_OK" in result.stdout:
                self.log_success(f"SSH connection established")
                return True
            else:
                self.log_failure(f"SSH connection test failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            self.log_failure("SSH connection timeout (10s)")
            return False
        except Exception as e:
            self.log_failure(f"SSH connection error: {str(e)}")
            return False

    def trigger_agent(self) -> bool:
        """Trigger agent via SSH."""
        self.log_info(f"Triggering agent: {self.agent_full}")

        cmd = [
            "ssh",
            f"{self.machine_b_user}@{self.machine_b_host}",
            f"openclaw run {self.agent_full} --cycle {self.cycle_id} --task {self.task_id} --brand {self.brand_id}"
        ]

        try:
            self.log_info(f"Executing: {' '.join(cmd[2:])}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30  # Trigger timeout (separate from execution timeout)
            )

            if result.returncode == 0:
                self.log_success(f"Agent triggered successfully")
                self.start_time = datetime.now()
                return True
            else:
                self.log_failure(f"Agent trigger failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            self.log_failure("Agent trigger timeout (30s)")
            return False
        except Exception as e:
            self.log_failure(f"Agent trigger error: {str(e)}")
            return False

    def get_agent_status_ssh(self) -> Optional[str]:
        """Get agent task status via SSH (query Supabase)."""
        # Note: In production, you'd query Supabase directly from the Orchestrator machine
        # This is a placeholder for SSH-based query
        return None

    def print_summary(self, success: bool):
        """Print execution summary."""
        print(f"\n{BLUE}{'='*70}{RESET}")

        if success:
            print(f"{GREEN}AGENT DISPATCH SUCCESSFUL{RESET}")
            print(f"Agent: {self.agent_full}")
            print(f"Cycle: {self.cycle_id}")
            print(f"Task: {self.task_id}")
            print(f"Brand: {self.brand_id}")

            if self.end_time and self.start_time:
                duration = (self.end_time - self.start_time).total_seconds()
                print(f"Duration: {duration:.1f} seconds")

            print(f"\nMonitor task status in Supabase:")
            print(f"  SELECT status FROM agent_deliverables WHERE id = '{self.task_id}';")
        else:
            print(f"{RED}AGENT DISPATCH FAILED{RESET}")
            print(f"Agent: {self.agent_full}")
            print(f"Check Machine B logs for errors:")
            print(f"  ssh {self.machine_b_user}@{self.machine_b_host} 'tail -50 ~/.openclaw/logs/latest.log'")

        print(f"{BLUE}{'='*70}{RESET}\n")

    def run(self) -> bool:
        """Execute the full dispatch workflow."""
        print(f"\n{BLUE}{'='*70}{RESET}")
        print(f"{BLUE}Google Ads Orchestrator — Agent Dispatch{RESET}")
        print(f"{BLUE}{'='*70}{RESET}\n")

        # Step 1: Validate inputs
        if not self.validate_inputs():
            self.print_summary(False)
            return False

        # Step 2: Test SSH connection
        if not self.test_ssh_connection():
            self.print_summary(False)
            return False

        # Step 3: Trigger agent
        if not self.trigger_agent():
            self.print_summary(False)
            return False

        # Step 4: Execution summary
        self.end_time = datetime.now()
        self.print_summary(True)
        return True


def main():
    parser = argparse.ArgumentParser(
        description="Dispatch Google Ads agent to Machine B"
    )

    parser.add_argument(
        "--machine-b-host",
        required=True,
        help="Machine B IP address or hostname"
    )
    parser.add_argument(
        "--machine-b-user",
        required=True,
        help="SSH user for Machine B"
    )
    parser.add_argument(
        "--agent",
        required=True,
        help="Agent to dispatch (e.g., 'data-placement', 'creative-producer', or full name)"
    )
    parser.add_argument(
        "--cycle",
        required=True,
        dest="cycle_id",
        help="Optimization cycle ID (UUID)"
    )
    parser.add_argument(
        "--task",
        required=True,
        dest="task_id",
        help="Task ID (UUID)"
    )
    parser.add_argument(
        "--brand",
        required=True,
        dest="brand_id",
        help="Brand ID (UUID)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=1800,
        help="Task execution timeout in seconds (default: 1800)"
    )
    parser.add_argument(
        "--poll-interval",
        type=int,
        default=30,
        help="Status polling interval in seconds (default: 30)"
    )

    args = parser.parse_args()

    dispatcher = AgentDispatcher(
        machine_b_host=args.machine_b_host,
        machine_b_user=args.machine_b_user,
        agent=args.agent,
        cycle_id=args.cycle_id,
        task_id=args.task_id,
        brand_id=args.brand_id,
        timeout=args.timeout,
        poll_interval=args.poll_interval,
    )

    success = dispatcher.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
