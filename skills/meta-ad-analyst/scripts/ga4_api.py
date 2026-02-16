#!/usr/bin/env python3
"""GA4 Data API helper — pull reports with dimensions/metrics/filters."""
import json, subprocess, sys, time
from datetime import datetime, timedelta

def get_access_token(sa_path):
    """Get OAuth2 token from service account JSON using gcloud or manual JWT."""
    try:
        result = subprocess.run(
            ["python3", "-c", f"""
import json, time, urllib.request, urllib.parse
from hashlib import sha256
import hmac, base64, struct

sa = json.load(open("{sa_path}"))
# Use google.auth if available
try:
    from google.oauth2 import service_account
    from google.auth.transport.requests import Request
    creds = service_account.Credentials.from_service_account_file(
        "{sa_path}", scopes=["https://www.googleapis.com/auth/analytics.readonly"])
    creds.refresh(Request())
    print(creds.token)
except ImportError:
    # Manual JWT approach
    import jwt as pyjwt
    now = int(time.time())
    payload = {{
        "iss": sa["client_email"],
        "scope": "https://www.googleapis.com/auth/analytics.readonly",
        "aud": "https://oauth2.googleapis.com/token",
        "iat": now, "exp": now + 3600
    }}
    signed = pyjwt.encode(payload, sa["private_key"], algorithm="RS256")
    data = urllib.parse.urlencode({{"grant_type": "urn:ietf:params:oauth:grant_type:jwt-bearer", "assertion": signed}}).encode()
    resp = urllib.request.urlopen("https://oauth2.googleapis.com/token", data)
    print(json.loads(resp.read())["access_token"])
"""],
            capture_output=True, text=True, timeout=30
        )
        return result.stdout.strip()
    except Exception as e:
        raise RuntimeError(f"Failed to get GA4 token: {e}")

def run_report(token, property_id, dimensions, metrics, date_start=None, date_end=None,
               dimension_filter=None, limit=10000):
    """Run a GA4 Data API report."""
    import urllib.request
    
    if not date_start:
        date_start = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    if not date_end:
        date_end = datetime.now().strftime("%Y-%m-%d")
    
    body = {
        "dateRanges": [{"startDate": date_start, "endDate": date_end}],
        "dimensions": [{"name": d} for d in dimensions],
        "metrics": [{"name": m} for m in metrics],
        "limit": limit,
    }
    if dimension_filter:
        body["dimensionFilter"] = dimension_filter
    
    url = f"https://analyticsdata.googleapis.com/v1beta/properties/{property_id}:runReport"
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                 headers={"Authorization": f"Bearer {token}",
                                          "Content-Type": "application/json"})
    resp = urllib.request.urlopen(req, timeout=60)
    return json.loads(resp.read().decode())

def parse_report(response):
    """Parse GA4 report response into list of dicts."""
    rows = []
    dim_headers = [h['name'] for h in response.get('dimensionHeaders', [])]
    met_headers = [h['name'] for h in response.get('metricHeaders', [])]
    
    for row in response.get('rows', []):
        entry = {}
        for i, d in enumerate(row.get('dimensionValues', [])):
            entry[dim_headers[i]] = d['value']
        for i, m in enumerate(row.get('metricValues', [])):
            entry[met_headers[i]] = m['value']
        rows.append(entry)
    return rows

def make_source_filter(source_value):
    """Create a dimensionFilter for sessionSource."""
    return {
        "filter": {
            "fieldName": "sessionSource",
            "stringFilter": {"matchType": "EXACT", "value": source_value}
        }
    }

if __name__ == "__main__":
    sa_path = sys.argv[1] if len(sys.argv) > 1 else "/root/clawd/.ga4_service_account.json"
    prop_id = sys.argv[2] if len(sys.argv) > 2 else "323020098"
    token = get_access_token(sa_path)
    resp = run_report(token, prop_id, ["deviceCategory"], ["sessions", "purchases"], limit=10)
    print(json.dumps(parse_report(resp), indent=2))
