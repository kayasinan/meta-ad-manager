#!/usr/bin/env python3
"""Meta Ads API helper — pull insights with breakdowns, ad sets, creatives."""
import json, urllib.request, urllib.parse, sys, os, time

def load_token(creds_path):
    with open(creds_path) as f:
        for line in f:
            if 'USER_ACCESS_TOKEN=' in line:
                return line.split('USER_ACCESS_TOKEN=', 1)[1].strip().strip('"').strip("'")
    raise ValueError("No USER_ACCESS_TOKEN found in " + creds_path)

def api_get(url, retries=2):
    for attempt in range(retries + 1):
        try:
            resp = urllib.request.urlopen(url, timeout=60)
            return json.loads(resp.read().decode())
        except Exception as e:
            if attempt < retries:
                time.sleep(2 ** attempt)
            else:
                raise

def get_insights(token, account_id, level="account", breakdowns=None, action_breakdowns=None,
                 date_preset="maximum", time_range=None, filtering=None,
                 fields="spend,impressions,reach,frequency,cpm,actions,action_values,cost_per_action_type,purchase_roas",
                 sort="spend_descending", limit=500):
    """Pull insights from Meta Ads API with optional breakdowns."""
    params = {
        "fields": fields,
        "level": level,
        "sort": sort,
        "limit": str(limit),
        "access_token": token,
    }
    if date_preset and not time_range:
        params["date_preset"] = date_preset
    if time_range:
        params["time_range"] = json.dumps(time_range)
    if breakdowns:
        params["breakdowns"] = ",".join(breakdowns) if isinstance(breakdowns, list) else breakdowns
    if action_breakdowns:
        params["action_breakdowns"] = ",".join(action_breakdowns) if isinstance(action_breakdowns, list) else action_breakdowns
    if filtering:
        params["filtering"] = json.dumps(filtering) if isinstance(filtering, list) else filtering

    url = f"https://graph.facebook.com/v21.0/act_{account_id}/insights?{urllib.parse.urlencode(params)}"
    
    all_data = []
    while url:
        data = api_get(url)
        if 'error' in data:
            print(f"API Error: {data['error'].get('message', data['error'])}", file=sys.stderr)
            return all_data
        all_data.extend(data.get('data', []))
        url = data.get('paging', {}).get('next')
    return all_data

def get_adsets(token, account_id, status_filter=None):
    """Pull ad sets with targeting details."""
    statuses = status_filter or ["ACTIVE"]
    status_param = urllib.parse.quote(json.dumps(statuses))
    url = (f"https://graph.facebook.com/v21.0/act_{account_id}/adsets"
           f"?fields=id,name,campaign{{name}},targeting,optimization_goal,daily_budget,status"
           f"&effective_status={status_param}&limit=100&access_token={token}")
    return api_get(url).get('data', [])

def get_ads_with_creative(token, account_id, limit=200):
    """Pull all ads with creative details."""
    url = (f"https://graph.facebook.com/v21.0/act_{account_id}/ads"
           f"?fields=id,name,status,effective_status,"
           f"creative{{id,body,title,image_url,thumbnail_url,video_id,call_to_action_type,link_url,object_story_spec}}"
           f"&limit={limit}&access_token={token}")
    return api_get(url).get('data', [])

def get_ad_creative_detail(token, ad_id):
    """Pull full creative details for a single ad."""
    url = (f"https://graph.facebook.com/v21.0/{ad_id}"
           f"?fields=name,creative{{effective_object_story_id,body,title,image_url,thumbnail_url,"
           f"video_id,link_url,object_story_spec,asset_feed_spec,call_to_action_type}}"
           f"&access_token={token}")
    return api_get(url)

# Helpers for parsing Meta response data
def get_action(row, action_type, field='actions'):
    for a in row.get(field, []):
        if a['action_type'] == action_type:
            return float(a['value'])
    return 0

def get_action_value(row, action_type):
    return get_action(row, action_type, 'action_values')

def get_cost(row, action_type):
    return get_action(row, action_type, 'cost_per_action_type')

if __name__ == "__main__":
    # Quick test
    creds = sys.argv[1] if len(sys.argv) > 1 else "/root/clawd/.meta_ads_credentials"
    token = load_token(creds)
    data = get_insights(token, "23987596", date_preset="last_30d", limit=1)
    print(json.dumps(data[:1], indent=2))
