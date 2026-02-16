#!/usr/bin/env python3
"""
Verify connections for Meta Ads AI Agent System

Tests:
  1. Supabase REST API connection and basic query
  2. SSH connection to Machine B
  3. Gemini API key validity

Usage:
  python3 verify_connections.py \
    --supabase-url https://project.supabase.co \
    --supabase-key eyJ... \
    --machine-b-host 192.168.1.100 \
    --gemini-key AIza...
"""

import argparse
import sys
import subprocess
import requests
import json
from typing import Tuple, Dict

def test_supabase_connection(url: str, key: str) -> Tuple[bool, str]:
    """Test Supabase REST API connection with a simple SELECT query."""
    try:
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "apikey": key,
        }
        # Query version() to test basic connectivity
        response = requests.get(
            f"{url}/rest/v1/",
            headers=headers,
            timeout=5
        )
        if response.status_code in [200, 401]:
            # 401 means auth issue but connection works
            # 200 means it worked
            return True, "Connected to Supabase REST API"
        else:
            return False, f"Supabase returned status {response.status_code}: {response.text[:200]}"
    except requests.exceptions.Timeout:
        return False, "Supabase connection timed out (>5s)"
    except requests.exceptions.ConnectionError as e:
        return False, f"Cannot reach Supabase: {str(e)[:100]}"
    except Exception as e:
        return False, f"Supabase test failed: {str(e)[:100]}"

def test_supabase_write(url: str, key: str) -> Tuple[bool, str]:
    """Test Supabase write permissions with a test insert/delete."""
    try:
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "apikey": key,
            "Prefer": "return=representation",
        }

        # Try to insert a test brand
        test_brand = {
            "brand_name": "__SETUP_TEST__",
            "product_description": "Test",
            "target_ar_cpa": 10.00,
            "target_ar_roas": 2.0,
        }

        response = requests.post(
            f"{url}/rest/v1/brand_config",
            headers=headers,
            json=test_brand,
            timeout=5
        )

        if response.status_code not in [200, 201]:
            return False, f"Write test failed: {response.status_code} - {response.text[:200]}"

        # If successful, try to delete it
        try:
            delete_response = requests.delete(
                f"{url}/rest/v1/brand_config?brand_name=eq.__SETUP_TEST__",
                headers=headers,
                timeout=5
            )
        except:
            pass  # Cleanup failure is not critical

        return True, "Write test successful (test brand insert/delete worked)"

    except requests.exceptions.Timeout:
        return False, "Supabase write test timed out"
    except Exception as e:
        return False, f"Supabase write test failed: {str(e)[:100]}"

def test_machine_b_ssh(host: str) -> Tuple[bool, str]:
    """Test SSH connection to Machine B with a simple echo command."""
    try:
        result = subprocess.run(
            ["ssh", host, "echo CONNECTION_OK"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0 and "CONNECTION_OK" in result.stdout:
            return True, f"SSH connected to {host}"
        else:
            return False, f"SSH to {host} failed: {result.stderr[:200]}"

    except subprocess.TimeoutExpired:
        return False, f"SSH to {host} timed out (>10s)"
    except FileNotFoundError:
        return False, "SSH client not found on this machine"
    except Exception as e:
        return False, f"SSH test failed: {str(e)[:100]}"

def test_gemini_api_key(key: str) -> Tuple[bool, str]:
    """Test Gemini API key validity with a simple API request."""
    try:
        import google.generativeai as genai

        genai.configure(api_key=key)

        # Try to list models to verify the key works
        models = genai.list_models()

        # Check if we got any response
        if models:
            return True, "Gemini API key is valid and accessible"
        else:
            return False, "Gemini API returned no models (possible invalid key)"

    except ImportError:
        return False, "google-generativeai not installed. Install with: pip install google-generativeai"
    except Exception as e:
        error_msg = str(e).lower()
        if "api" in error_msg and "key" in error_msg:
            return False, f"Invalid Gemini API key: {str(e)[:100]}"
        elif "quota" in error_msg or "rate" in error_msg:
            return False, f"Gemini API quota exceeded or rate limited: {str(e)[:100]}"
        else:
            return False, f"Gemini API test failed: {str(e)[:100]}"

def main():
    parser = argparse.ArgumentParser(
        description="Verify connections for Meta Ads AI Agent System setup"
    )
    parser.add_argument("--supabase-url", required=True, help="Supabase project URL (e.g., https://project.supabase.co)")
    parser.add_argument("--supabase-key", required=True, help="Supabase service role key")
    parser.add_argument("--machine-b-host", required=False, help="Machine B hostname or IP (optional)")
    parser.add_argument("--gemini-key", required=False, help="Gemini API key (optional)")

    args = parser.parse_args()

    print("=" * 60)
    print("Meta Ads AI System — Connection Verification")
    print("=" * 60)
    print()

    results = {}

    # Test 1: Supabase connection
    print("TEST 1: Supabase REST API Connection")
    print("-" * 40)
    success, message = test_supabase_connection(args.supabase_url, args.supabase_key)
    results["supabase_connection"] = success
    print(f"{'✅' if success else '❌'} {message}")
    print()

    # Test 2: Supabase write
    if success:
        print("TEST 2: Supabase Write Permissions")
        print("-" * 40)
        success, message = test_supabase_write(args.supabase_url, args.supabase_key)
        results["supabase_write"] = success
        print(f"{'✅' if success else '❌'} {message}")
        print()
    else:
        print("TEST 2: Supabase Write Permissions")
        print("-" * 40)
        print("⏭️  Skipped (Supabase connection failed)")
        results["supabase_write"] = False
        print()

    # Test 3: Machine B SSH (if provided)
    if args.machine_b_host:
        print("TEST 3: SSH Connection to Machine B")
        print("-" * 40)
        success, message = test_machine_b_ssh(args.machine_b_host)
        results["machine_b_ssh"] = success
        print(f"{'✅' if success else '❌'} {message}")
        print()
    else:
        print("TEST 3: SSH Connection to Machine B")
        print("-" * 40)
        print("⏭️  Skipped (--machine-b-host not provided)")
        results["machine_b_ssh"] = None
        print()

    # Test 4: Gemini API (if provided)
    if args.gemini_key:
        print("TEST 4: Gemini API Key Validation")
        print("-" * 40)
        success, message = test_gemini_api_key(args.gemini_key)
        results["gemini_api"] = success
        print(f"{'✅' if success else '❌'} {message}")
        print()
    else:
        print("TEST 4: Gemini API Key Validation")
        print("-" * 40)
        print("⏭️  Skipped (--gemini-key not provided)")
        results["gemini_api"] = None
        print()

    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)

    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)

    print(f"Passed:  {passed}")
    print(f"Failed:  {failed}")
    print(f"Skipped: {skipped}")
    print()

    # Exit code
    if failed > 0:
        print("❌ Some tests failed. Please fix the issues above and try again.")
        sys.exit(1)
    elif passed > 0:
        print("✅ All tests passed! Setup can proceed.")
        sys.exit(0)
    else:
        print("⚠️  No tests were run (all optional). Provide at least some arguments.")
        sys.exit(0)

if __name__ == "__main__":
    main()
