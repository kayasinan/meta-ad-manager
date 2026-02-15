#!/usr/bin/env python3
"""
Dispatch agent to Machine B and monitor completion

Orchestrator utility to:
  1. Trigger an agent on Machine B via SSH
  2. Poll for completion by monitoring agent_deliverables table
  3. Report success/failure/timeout

Usage:
  python3 dispatch_agent.py \
    --agent data_placement \
    --cycle a1b2c3d4-e5f6-7890-abcd-ef1234567890 \
    --task a1b2c3d4-e5f6-7890-abcd-ef9876543210 \
    --brand a1b2c3d4-e5f6-7890-abcd-efaabbccddee \
    --host 192.168.1.100 \
    --supabase-url https://project.supabase.co \
    --supabase-key eyJ...

Or with environment variables:
  export SUPABASE_URL=https://project.supabase.co
  export SUPABASE_SERVICE_KEY=eyJ...
  python3 dispatch_agent.py \
    --agent data_placement \
    --cycle $CYCLE_ID \
    --task $TASK_ID \
    --brand $BRAND_ID \
    --host 192.168.1.100
"""

import argparse
import os
import sys
import subprocess
import time
import requests
import json
from typing import Tuple, Dict, Optional

# Agent name to skill name mapping
AGENT_SKILL_MAP = {
    "data_placement": "meta-ads-data-placement-analyst",
    "creative_analyst": "meta-ads-creative-analyst",
    "post_click": "meta-ads-postclick-analyst",
    "competitive_intel": "meta-ads-competitive-intel",
    "creative_producer": "meta-ads-creative-producer",
    "campaign_creator": "meta-ads-campaign-creator",
    "campaign_monitor": "meta-ads-campaign-monitor",
}

AGENT_PRIORITY = {
    "data_placement": 1,
    "creative_analyst": 2,
    "post_click": 3,
    "competitive_intel": 4,
    "creative_producer": 5,
    "campaign_creator": 6,
    "campaign_monitor": 7,
}

class AgentDispatcher:
    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase_url = supabase_url.rstrip('/')
        self.supabase_key = supabase_key
        self.headers = {
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json",
            "apikey": supabase_key,
            "Prefer": "return=representation",
        }

    def get_deliverable_status(self, task_id: str) -> Optional[Dict]:
        """Get current status of a task from agent_deliverables."""
        try:
            response = requests.get(
                f"{self.supabase_url}/rest/v1/agent_deliverables?id=eq.{task_id}",
                headers=self.headers,
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                if data:
                    return data[0]
            return None
        except Exception as e:
            print(f"❌ Error querying deliverable status: {str(e)[:100]}")
            return None

    def update_deliverable_to_in_progress(self, task_id: str) -> bool:
        """Mark task as IN_PROGRESS before dispatching."""
        try:
            update_payload = {
                "status": "IN_PROGRESS",
                "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }
            response = requests.patch(
                f"{self.supabase_url}/rest/v1/agent_deliverables?id=eq.{task_id}",
                headers=self.headers,
                json=update_payload,
                timeout=5
            )
            return response.status_code in [200, 204]
        except Exception as e:
            print(f"⚠️  Could not mark task as IN_PROGRESS: {str(e)[:100]}")
            return False

    def trigger_agent_ssh(self, agent_name: str, cycle_id: str, task_id: str,
                         brand_id: str, host: str) -> Tuple[bool, str]:
        """Trigger agent on Machine B via SSH."""
        skill_name = AGENT_SKILL_MAP.get(agent_name)
        if not skill_name:
            return False, f"Unknown agent: {agent_name}"

        # Build SSH command
        cmd = [
            "ssh",
            host,
            f"openclaw run {skill_name} --cycle {cycle_id} --task {task_id} --brand {brand_id}"
        ]

        try:
            print(f"🚀 Triggering {agent_name} on {host}...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                return True, f"Agent {agent_name} triggered successfully"
            else:
                error = result.stderr or result.stdout
                return False, f"SSH failed: {error[:200]}"

        except subprocess.TimeoutExpired:
            return False, f"SSH to {host} timed out (>30s)"
        except FileNotFoundError:
            return False, "SSH client not found on this machine"
        except Exception as e:
            return False, f"SSH trigger failed: {str(e)[:100]}"

    def poll_for_completion(self, task_id: str, timeout_seconds: int = 3600,
                          poll_interval: int = 5) -> Tuple[str, str]:
        """
        Poll agent_deliverables for task completion.
        Returns: (status, summary)
          - status: 'DELIVERED', 'BLOCKED', 'TIMEOUT', 'IN_PROGRESS'
          - summary: human-readable result
        """
        start_time = time.time()
        poll_count = 0

        while True:
            elapsed = time.time() - start_time
            poll_count += 1

            # Check timeout
            if elapsed > timeout_seconds:
                return "TIMEOUT", f"Agent did not complete within {timeout_seconds}s ({poll_count} polls)"

            # Query status
            deliverable = self.get_deliverable_status(task_id)

            if not deliverable:
                if elapsed > 30:
                    return "TIMEOUT", "Task not found in database (possible SSH failure)"
                print(f"  [Poll {poll_count}] Task not yet visible in database, waiting...")
                time.sleep(poll_interval)
                continue

            status = deliverable.get("status", "UNKNOWN")
            print(f"  [Poll {poll_count}] Status: {status} (elapsed: {int(elapsed)}s)")

            if status == "DELIVERED":
                summary = deliverable.get("summary", "[no summary]")
                delivered_at = deliverable.get("delivered_at", "")
                return "DELIVERED", f"Completed at {delivered_at}. Summary: {summary[:200]}"

            elif status == "BLOCKED":
                blocked_reason = deliverable.get("blocked_reason", "Unknown reason")
                return "BLOCKED", f"Agent blocked: {blocked_reason}"

            elif status == "IN_PROGRESS":
                runner_picked = deliverable.get("runner_picked_at", "")
                print(f"    → Running since: {runner_picked}")
                time.sleep(poll_interval)

            elif status == "PENDING":
                print(f"    → Task still pending (may not have started yet)")
                time.sleep(poll_interval)

            else:
                print(f"    → Unknown status: {status}")
                time.sleep(poll_interval)

    def dispatch_and_monitor(self, agent_name: str, cycle_id: str, task_id: str,
                            brand_id: str, host: str, timeout_seconds: int = 3600) -> int:
        """
        Full dispatch workflow:
        1. Mark task as IN_PROGRESS
        2. Trigger agent via SSH
        3. Poll for completion
        4. Report results
        """
        print("=" * 60)
        print(f"Agent Dispatch: {agent_name}")
        print("=" * 60)
        print(f"Cycle: {cycle_id}")
        print(f"Task:  {task_id}")
        print(f"Brand: {brand_id}")
        print(f"Host:  {host}")
        print()

        # Step 1: Mark as IN_PROGRESS
        print("Step 1: Updating task status to IN_PROGRESS...")
        self.update_deliverable_to_in_progress(task_id)
        time.sleep(0.5)  # Let DB update settle
        print()

        # Step 2: Trigger agent
        print("Step 2: Triggering agent via SSH...")
        success, message = self.trigger_agent_ssh(agent_name, cycle_id, task_id, brand_id, host)
        print(f"{'✅' if success else '❌'} {message}")
        print()

        if not success:
            print("❌ SSH trigger failed. Aborting.")
            return 1

        # Step 3: Poll for completion
        print("Step 3: Polling for completion...")
        print(f"(timeout: {timeout_seconds}s, polling every 5s)")
        print()

        status, summary = self.poll_for_completion(task_id, timeout_seconds=timeout_seconds)
        print()

        # Step 4: Report results
        print("=" * 60)
        print("RESULT")
        print("=" * 60)
        print(f"Status:  {status}")
        print(f"Summary: {summary}")
        print()

        if status == "DELIVERED":
            print("✅ Agent completed successfully.")
            return 0
        elif status == "BLOCKED":
            print("⚠️  Agent blocked (possibly waiting for dependencies or input).")
            return 2
        elif status == "TIMEOUT":
            print("❌ Agent did not complete within timeout period.")
            return 1
        else:
            print("❌ Unknown result.")
            return 1

def main():
    parser = argparse.ArgumentParser(
        description="Dispatch agent to Machine B and monitor completion"
    )
    parser.add_argument("--agent", required=True,
                       choices=list(AGENT_SKILL_MAP.keys()),
                       help="Agent to dispatch")
    parser.add_argument("--cycle", required=True, help="Cycle ID (UUID)")
    parser.add_argument("--task", required=True, help="Task ID (UUID)")
    parser.add_argument("--brand", required=True, help="Brand ID (UUID)")
    parser.add_argument("--host", required=True, help="Machine B hostname or IP")
    parser.add_argument("--supabase-url", help="Supabase URL (or use SUPABASE_URL env var)")
    parser.add_argument("--supabase-key", help="Supabase service role key (or use SUPABASE_SERVICE_KEY env var)")
    parser.add_argument("--timeout", type=int, default=3600, help="Polling timeout in seconds (default: 3600 = 1 hour)")

    args = parser.parse_args()

    # Get Supabase credentials from args or env
    supabase_url = args.supabase_url or os.getenv("SUPABASE_URL")
    supabase_key = args.supabase_key or os.getenv("SUPABASE_SERVICE_KEY")

    if not supabase_url:
        print("❌ Missing Supabase URL. Provide via --supabase-url or SUPABASE_URL env var.")
        sys.exit(1)
    if not supabase_key:
        print("❌ Missing Supabase service key. Provide via --supabase-key or SUPABASE_SERVICE_KEY env var.")
        sys.exit(1)

    # Create dispatcher and run
    dispatcher = AgentDispatcher(supabase_url, supabase_key)
    exit_code = dispatcher.dispatch_and_monitor(
        args.agent, args.cycle, args.task, args.brand, args.host,
        timeout_seconds=args.timeout
    )
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
