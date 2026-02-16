# Google Ads Transparency Center Scraping Guide

## Overview

The Google Ads Transparency Center (https://ads.google.com/transparency-center) provides visibility into active ads from any advertiser. While there's no official API, we can scrape the data to monitor competitors and identify Mode B opportunities.

---

## Data Available

### What You CAN See
- **Active ads:** All ads currently running from a specific advertiser
- **Ad format:** Search, Display, Video, Shopping
- **Ad copy:** Headlines, descriptions, CTAs
- **Visuals:** Images, videos, thumbnails
- **Targeting scope:** Countries/regions where ads run
- **Run dates:** First seen and last seen dates (longevity)
- **Platforms:** Which platforms the ad runs on (Search, Display, etc.)

### What You CANNOT See
- **Spend data** — Not available in Transparency Center
- **Performance metrics** — No clicks, impressions, conversions
- **Engagement** — No likes, shares, comments
- **Account information** — No contact details, history, other campaigns
- **Exact audience targeting** — Demographics, interests, keywords

---

## Scraping Strategy

### Search by Advertiser Name

```python
# Method 1: Direct advertiser name search
query = "Nike"
url = f"https://ads.google.com/transparency-center/advertiser/?advertiser={query}"

# Search yields all active ads from that advertiser
```

### Search by Keyword

```python
# Method 2: Keyword-based search (finds advertisers running keyword-related ads)
query = "running shoes"
url = f"https://ads.google.com/transparency-center/search/?q={query}"

# Results show top advertisers running ads related to keyword
```

### Search by Category

```python
# Method 3: Category search
category = "Healthcare"
url = f"https://ads.google.com/transparency-center/advertiser/?category={category}"
```

---

## Data Extraction

### Per-Ad Data Points

For each ad, extract:
```json
{
  "advertiser": "Nike",
  "ad_id": "unique_id",
  "format": "SEARCH|DISPLAY|VIDEO|SHOPPING",
  "headline": "First Text Line",
  "description": "Supporting text",
  "call_to_action": "Learn More",
  "image_url": "url_to_image",
  "video_url": "url_to_video",
  "platforms": ["GOOGLE_SEARCH", "DISPLAY_NETWORK"],
  "countries": ["US", "CA", "GB"],
  "first_seen": "2025-12-01",
  "last_seen": "2026-02-14",
  "days_running": 75
}
```

### Dates

**First Seen:** The earliest date Google detected this ad in the Transparency Center
**Last Seen:** The most recent date the ad appeared
**Days Running:** last_seen - first_seen = longevity

---

## Longevity Calculation

```python
def calculate_longevity(first_seen_date, last_seen_date):
    """Calculate days ad has been running"""
    days = (last_seen_date - first_seen_date).days

    # Longevity score (0-10 scale)
    if days < 14:
        return {"days": days, "score": 2}
    elif days < 30:
        return {"days": days, "score": 4}
    elif days < 60:
        return {"days": days, "score": 6}
    else:
        return {"days": days, "score": min(10, 8 + (days - 60) / 30)}
```

---

## Rate Limiting & Best Practices

### Rate Limits
- Google doesn't officially limit Transparency Center access
- However, aggressive scraping may trigger blocks
- Recommended: 5-second delays between requests

### Best Practices
```python
import time
import requests

def scrape_with_rate_limit(urls, delay=5):
    """Scrape URLs with rate limiting"""
    for url in urls:
        response = requests.get(url)
        # Process response
        yield response
        time.sleep(delay)  # Wait before next request
```

### User-Agent Rotation
Use realistic user agents to avoid blocks:
```python
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}
```

---

## Search Terms

When monitoring a new market, search these terms to identify top advertisers:

```
Primary keywords:
- "[Product name]"
- "[Product name] buy"
- "[Product name] sale"
- "[Category]"

Intent keywords:
- "best [product]"
- "[product] vs."
- "[product] reviews"
- "cheap [product]"
- "[product] discount"

Competitor keywords:
- "alternative to [competitor]"
- "[competitor] vs [product]"
```

---

## Data Storage Format

Store competitor ads in database:

```sql
INSERT INTO g_competitor_ads (
  brand_id,
  competitor_id,
  ad_library_id,
  format,
  copy_headline,
  copy_description,
  copy_cta,
  visual_url,
  video_url,
  platforms,
  countries,
  first_seen,
  last_seen,
  days_running,
  longevity_score
) VALUES (...)
```

---

## Frequency of Updates

### Recommended Schedule
- **Top competitors:** Check weekly
- **Secondary competitors:** Check bi-weekly
- **General market monitoring:** Monthly

---

## Ethical Considerations

### What's Allowed
- ✅ Viewing publicly available ads in Transparency Center
- ✅ Analyzing creative approaches and trends
- ✅ Using insights to inform your own strategy
- ✅ Identifying market opportunities

### What's NOT Allowed
- ❌ Copying exact ad copy word-for-word
- ❌ Using competitor's specific images without modification
- ❌ Impersonating competitors or their ads
- ❌ Using scraped data for non-competitive purposes

---

## Challenges & Limitations

### Challenge 1: Partial Data
Transparency Center may not show ALL ads a competitor is running, particularly older ads or ads with limited geographic scope.

**Mitigation:** Accept 70-80% coverage as sufficient for trend analysis.

### Challenge 2: Fake Ads
Some ads in Transparency Center may be scam ads or ads flagged by Google as misleading.

**Mitigation:** Manually review suspicious ads before including in analysis.

### Challenge 3: Attribution Delay
Last seen date lags by 1-2 days. You won't see today's new ads until tomorrow.

**Mitigation:** Note in reports: "Last update: [date]. Real-time data 1-2 days behind."

---
