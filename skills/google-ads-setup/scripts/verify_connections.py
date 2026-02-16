#!/usr/bin/env python3
"""
Google Ads AI System — Connection Verification Script

Verifies connectivity and credentials for Google Ads API, GA4, and Supabase.
Run this during Phase 2 (Credentials Collection) to validate all connections.

Usage:
    python3 verify_connections.py --supabase-url https://project.supabase.co \
        --supabase-key eyJ... --gemini-key AIzaSy... \
        [--google-ads-dev-token xxx] [--google-ads-refresh-token xxx] \
        [--ga4-property-id 123456789]
"""

import sys
import os
import json
import argparse
from typing import Optional, Dict, Tuple
import requests
from datetime import datetime, timedelta

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


class ConnectionVerifier:
    """Verifies connections to Google Ads, GA4, and Supabase."""

    def __init__(self):
        self.results = []
        self.failures = []

    def log_success(self, test_name: str, detail: str = ""):
        """Log successful test."""
        msg = f"{GREEN}✅{RESET} {test_name}"
        if detail:
            msg += f" — {detail}"
        self.results.append(msg)
        print(msg)

    def log_failure(self, test_name: str, detail: str = ""):
        """Log failed test."""
        msg = f"{RED}❌{RESET} {test_name}"
        if detail:
            msg += f" — {detail}"
        self.results.append(msg)
        self.failures.append((test_name, detail))
        print(msg)

    def log_warning(self, test_name: str, detail: str = ""):
        """Log warning."""
        msg = f"{YELLOW}⚠️{RESET}  {test_name}"
        if detail:
            msg += f" — {detail}"
        self.results.append(msg)
        print(msg)

    def log_info(self, message: str):
        """Log informational message."""
        msg = f"{BLUE}ℹ️{RESET}  {message}"
        print(msg)

    # =========================================================================
    # Supabase Tests
    # =========================================================================

    def test_supabase_connection(self, supabase_url: str, service_key: str) -> bool:
        """Test Supabase connection with a simple version query."""
        self.log_info("Testing Supabase connection...")

        try:
            headers = {
                "Authorization": f"Bearer {service_key}",
                "Content-Type": "application/json",
            }

            # Test with a simple REST API call
            response = requests.get(
                f"{supabase_url}/rest/v1/",
                headers=headers,
                timeout=10
            )

            if response.status_code in [200, 401, 403]:  # 401/403 is auth failing, which we handle next
                self.log_success("Supabase connection", f"API reachable (HTTP {response.status_code})")
                return True
            else:
                self.log_failure("Supabase connection", f"Unexpected status {response.status_code}")
                return False

        except requests.exceptions.Timeout:
            self.log_failure("Supabase connection", "Request timeout (10s)")
            return False
        except Exception as e:
            self.log_failure("Supabase connection", str(e))
            return False

    def test_supabase_auth(self, supabase_url: str, service_key: str) -> bool:
        """Test Supabase authentication."""
        self.log_info("Testing Supabase authentication...")

        try:
            headers = {
                "Authorization": f"Bearer {service_key}",
                "Content-Type": "application/json",
            }

            # Try to query a basic table (should have setup_log)
            response = requests.get(
                f"{supabase_url}/rest/v1/setup_log?limit=1",
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                self.log_success("Supabase authentication", "Service role key valid (read access confirmed)")
                return True
            elif response.status_code == 401:
                self.log_failure("Supabase authentication", "Invalid or expired service role key")
                return False
            elif response.status_code == 403:
                self.log_failure("Supabase authentication", "Service role key doesn't have read access")
                return False
            else:
                self.log_warning("Supabase authentication", f"Unexpected status {response.status_code}")
                return response.status_code == 200

        except Exception as e:
            self.log_failure("Supabase authentication", str(e))
            return False

    def test_supabase_write(self, supabase_url: str, service_key: str) -> bool:
        """Test Supabase write permissions."""
        self.log_info("Testing Supabase write permissions...")

        try:
            headers = {
                "Authorization": f"Bearer {service_key}",
                "Content-Type": "application/json",
            }

            # Try to insert a test row into setup_log
            test_data = {
                "phase": 99,
                "phase_name": "__SETUP_TEST__",
                "status": "TESTING"
            }

            response = requests.post(
                f"{supabase_url}/rest/v1/setup_log",
                headers=headers,
                json=test_data,
                timeout=10
            )

            if response.status_code in [200, 201]:
                # Clean up the test row
                requests.delete(
                    f"{supabase_url}/rest/v1/setup_log?phase=eq.99",
                    headers=headers,
                    timeout=10
                )
                self.log_success("Supabase write permissions", "Write access confirmed")
                return True
            elif response.status_code == 403:
                self.log_failure("Supabase write permissions", "Service role key doesn't have write access")
                return False
            else:
                self.log_failure("Supabase write permissions", f"Status {response.status_code}")
                return False

        except Exception as e:
            self.log_failure("Supabase write permissions", str(e))
            return False

    # =========================================================================
    # Gemini API Tests
    # =========================================================================

    def test_gemini_api(self, gemini_key: str) -> bool:
        """Test Gemini API connectivity."""
        self.log_info("Testing Gemini API...")

        try:
            import google.generativeai as genai
        except ImportError:
            self.log_failure("Gemini API", "google-generativeai not installed")
            return False

        try:
            genai.configure(api_key=gemini_key)

            # Try to list available models
            models = genai.list_models()
            model_count = len([m for m in models if "generateContent" in m.supported_generation_methods])

            if model_count > 0:
                self.log_success("Gemini API", f"API key valid, {model_count} generation models available")
                return True
            else:
                self.log_failure("Gemini API", "No generation models available")
                return False

        except Exception as e:
            self.log_failure("Gemini API", str(e))
            return False

    # =========================================================================
    # Google Ads API Tests
    # =========================================================================

    def test_google_ads_connectivity(self) -> bool:
        """Test connectivity to Google Ads API endpoint."""
        self.log_info("Testing Google Ads API connectivity...")

        try:
            response = requests.get(
                "https://googleads.googleapis.com/",
                timeout=10
            )

            # Any response (including 404) means the endpoint is reachable
            if response.status_code in [200, 401, 403, 404]:
                self.log_success("Google Ads API connectivity", "Endpoint reachable")
                return True
            else:
                self.log_failure("Google Ads API connectivity", f"Unexpected status {response.status_code}")
                return False

        except requests.exceptions.Timeout:
            self.log_failure("Google Ads API connectivity", "Request timeout")
            return False
        except Exception as e:
            self.log_failure("Google Ads API connectivity", str(e))
            return False

    def test_google_ads_credentials(self, dev_token: str, refresh_token: str) -> bool:
        """Test Google Ads API credentials (basic validation)."""
        self.log_info("Testing Google Ads API credentials format...")

        if not dev_token or len(dev_token.strip()) == 0:
            self.log_failure("Google Ads developer token", "Token is empty")
            return False

        if not refresh_token or len(refresh_token.strip()) == 0:
            self.log_failure("Google Ads refresh token", "Token is empty")
            return False

        # Basic format validation
        if len(dev_token) < 10:
            self.log_failure("Google Ads developer token", "Token appears too short")
            return False

        if "ya29" not in refresh_token and "1//" not in refresh_token:
            self.log_warning("Google Ads refresh token", "Doesn't look like a standard OAuth refresh token format")

        self.log_success("Google Ads credentials", "Tokens provided in valid format")
        return True

    # =========================================================================
    # GA4 Tests
    # =========================================================================

    def test_ga4_connectivity(self) -> bool:
        """Test connectivity to Google Analytics API."""
        self.log_info("Testing GA4 API connectivity...")

        try:
            response = requests.get(
                "https://analyticsreporting.googleapis.com/",
                timeout=10
            )

            if response.status_code in [200, 401, 403, 404]:
                self.log_success("GA4 API connectivity", "Endpoint reachable")
                return True
            else:
                self.log_failure("GA4 API connectivity", f"Unexpected status {response.status_code}")
                return False

        except requests.exceptions.Timeout:
            self.log_failure("GA4 API connectivity", "Request timeout")
            return False
        except Exception as e:
            self.log_failure("GA4 API connectivity", str(e))
            return False

    def test_ga4_property_id(self, property_id: str) -> bool:
        """Validate GA4 property ID format."""
        self.log_info("Testing GA4 property ID format...")

        if not property_id or len(property_id.strip()) == 0:
            self.log_failure("GA4 property ID", "Property ID is empty")
            return False

        if not property_id.isdigit():
            self.log_failure("GA4 property ID", "Property ID must be numeric")
            return False

        if len(property_id) < 9:
            self.log_failure("GA4 property ID", "Property ID appears too short (should be ~9+ digits)")
            return False

        self.log_success("GA4 property ID", f"Valid format (ID: {property_id})")
        return True

    # =========================================================================
    # Summary
    # =========================================================================

    def print_summary(self):
        """Print test summary."""
        print("\n" + "="*70)

        if self.failures:
            print(f"{RED}VERIFICATION FAILED{RESET}")
            print(f"{len(self.failures)} issue(s) detected:")
            for test_name, detail in self.failures:
                print(f"  • {test_name}: {detail}")
            print("\nPlease fix these issues before proceeding with setup.")
            return False
        else:
            print(f"{GREEN}ALL TESTS PASSED{RESET}")
            print("Your system is ready for Phase 2 credential collection.")
            return True


def main():
    parser = argparse.ArgumentParser(
        description="Verify Google Ads AI System connectivity"
    )

    parser.add_argument(
        "--supabase-url",
        required=False,
        help="Supabase project URL (e.g., https://project.supabase.co)"
    )
    parser.add_argument(
        "--supabase-key",
        required=False,
        help="Supabase service role key"
    )
    parser.add_argument(
        "--gemini-key",
        required=False,
        help="Gemini API key"
    )
    parser.add_argument(
        "--google-ads-dev-token",
        required=False,
        help="Google Ads developer token"
    )
    parser.add_argument(
        "--google-ads-refresh-token",
        required=False,
        help="Google Ads OAuth2 refresh token"
    )
    parser.add_argument(
        "--ga4-property-id",
        required=False,
        help="GA4 property ID (numeric)"
    )

    args = parser.parse_args()

    verifier = ConnectionVerifier()

    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}Google Ads AI System — Connection Verification{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")

    # Run tests based on provided arguments
    if args.supabase_url and args.supabase_key:
        verifier.test_supabase_connection(args.supabase_url, args.supabase_key)
        verifier.test_supabase_auth(args.supabase_url, args.supabase_key)
        verifier.test_supabase_write(args.supabase_url, args.supabase_key)

    if args.gemini_key:
        verifier.test_gemini_api(args.gemini_key)

    # Google Ads tests
    verifier.test_google_ads_connectivity()
    if args.google_ads_dev_token and args.google_ads_refresh_token:
        verifier.test_google_ads_credentials(args.google_ads_dev_token, args.google_ads_refresh_token)

    # GA4 tests
    verifier.test_ga4_connectivity()
    if args.ga4_property_id:
        verifier.test_ga4_property_id(args.ga4_property_id)

    # Print summary
    success = verifier.print_summary()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
