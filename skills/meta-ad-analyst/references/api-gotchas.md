# Meta & GA4 API Gotchas

## Meta Ads API (v21.0)

### Breakdowns That Don't Return Offsite Conversions
- `region`, `dma`, `country` breakdowns do NOT return purchase/ATC actions
- Use GA4 for geographic conversion data instead

### Breakdowns That Fail or Return Empty
- `frequency_value` returns empty for ASC (Advantage+) campaign types
- `body_asset`, `image_asset`, `title_asset`, `description_asset` only work for Dynamic Creative ads; deprecated as `action_breakdowns` in v21+
- Campaign-level hourly breakdown often hits "please reduce data" error — split into quarterly time_range windows

### Rate Limits
- Default: 200 calls per hour per ad account
- Batch requests when possible; add `time.sleep(0.3)` between sequential calls
- If rate limited, wait 60 seconds then retry

### Creative Fields
- `object_story_spec.link_data` contains body (as `message`), title (as `name`), link, and `child_attachments` for carousels
- `object_story_spec.video_data` contains video body (as `message`), title
- `asset_feed_spec` contains multi-asset variants (bodies[], titles[], descriptions[], images[], videos[])
- Image URLs from `creative.image_url` may return 403 when fetched directly — use the Graph API endpoint with token instead

### Pagination
- Always check `paging.next` — large result sets are paginated
- `limit` max is 500 for insights

## GA4 Data API

### Dimension Scope Incompatibility
- `userAgeBracket` and `userGender` are USER-scoped dimensions
- `sessionSource`, `sessionMedium`, `sessionCampaignName` are SESSION-scoped
- **These cannot be combined in the same report** — the API returns empty or errors
- Workaround: Use Meta's own age/gender breakdowns for demographic analysis

### Session Source Mapping
- Facebook ad traffic source name varies per account (check UTM setup)
- Common values: `facebook_ads_ppm`, `facebook`, `fb`
- GA4 may classify paid social as "Organic Social" if UTMs aren't standard `utm_source/utm_medium`
- Verify by checking `sessionSource` dimension values in GA4

### Working Dimension Combos (with sessionSource filter)
- region, city, deviceCategory, hour, dayOfWeekName
- sessionCampaignName, sessionMedium, landingPage
- All session-scoped or event-scoped dimensions work fine

### Auth
- Service account JSON key + google-auth library
- Scopes: `https://www.googleapis.com/auth/analytics.readonly`
- GA4 Data API must be enabled in Google Cloud console
