#!/usr/bin/env python3
"""Detect audience overlap / cannibalization between ad sets."""
import json, sys
sys.path.insert(0, __import__('os').path.dirname(__file__))
from meta_api import load_token, get_adsets

def analyze_overlap(adsets):
    """Detect overlap between ad sets and classify risk."""
    overlaps = []
    for i, a in enumerate(adsets):
        for j, b in enumerate(adsets):
            if i >= j: continue
            
            ta = a.get('targeting', {})
            tb = b.get('targeting', {})
            
            # Country overlap
            ca = set(ta.get('geo_locations', {}).get('countries', []))
            cb = set(tb.get('geo_locations', {}).get('countries', []))
            shared_countries = ca & cb
            if not shared_countries: continue
            
            # Classify targeting type
            def get_type(t):
                if t.get('flexible_spec'):
                    interests = []
                    for fs in t['flexible_spec']:
                        interests.extend([i['name'] for i in fs.get('interests', [])])
                    return 'interest', set(interests)
                elif t.get('custom_audiences'):
                    return 'custom', set(ca['name'] for ca in t['custom_audiences'] if 'name' in ca)
                return 'broad', set()
            
            a_type, a_targets = get_type(ta)
            b_type, b_targets = get_type(tb)
            
            risk = 'LOW'
            reasons = []
            
            if a_type == 'broad' and b_type == 'broad':
                risk = 'HIGH'
                reasons.append('Both broad/ASC targeting same country')
            elif a_type == b_type == 'interest' and a_targets & b_targets:
                risk = 'HIGH'
                reasons.append(f'Shared interests: {a_targets & b_targets}')
            elif 'broad' in (a_type, b_type):
                risk = 'MEDIUM'
                reasons.append('Broad targeting overlaps with everything')
            
            if ta.get('age_min') == tb.get('age_min') and ta.get('age_max') == tb.get('age_max'):
                reasons.append('Same age range')
            
            # Check exclusion gaps
            a_excl = len(ta.get('excluded_custom_audiences', []))
            b_excl = len(tb.get('excluded_custom_audiences', []))
            if a_excl == 0 or b_excl == 0:
                reasons.append('Missing exclusions on one or both')
            
            if risk in ('HIGH', 'MEDIUM'):
                overlaps.append({
                    'risk': risk,
                    'adset_a': a.get('name', a.get('id')),
                    'adset_b': b.get('name', b.get('id')),
                    'campaign_a': a.get('campaign', {}).get('name', '?'),
                    'campaign_b': b.get('campaign', {}).get('name', '?'),
                    'countries': list(shared_countries),
                    'reasons': reasons,
                })
    
    return overlaps

if __name__ == "__main__":
    creds = sys.argv[1] if len(sys.argv) > 1 else "/root/clawd/.meta_ads_credentials"
    account_id = sys.argv[2] if len(sys.argv) > 2 else "23987596"
    token = load_token(creds)
    adsets = get_adsets(token, account_id)
    overlaps = analyze_overlap(adsets)
    
    high = [o for o in overlaps if o['risk'] == 'HIGH']
    med = [o for o in overlaps if o['risk'] == 'MEDIUM']
    print(f"Ad sets: {len(adsets)} | HIGH overlaps: {len(high)} | MEDIUM: {len(med)}")
    for o in high[:10]:
        print(f"  🔴 {o['adset_a']} <-> {o['adset_b']}: {'; '.join(o['reasons'])}")
    for o in med[:5]:
        print(f"  🟡 {o['adset_a']} <-> {o['adset_b']}: {'; '.join(o['reasons'])}")
