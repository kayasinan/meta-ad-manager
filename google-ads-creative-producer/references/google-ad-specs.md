# Google Ads Format Specifications & Character Limits

Complete reference for all Google Ads creative formats supported by the Creative Producer.

---

## SEARCH — Responsive Search Ads (RSA)

### Overview
RSAs allow dynamic headline and description combinations. Google tests different permutations to find the best performers.

### Character Limits
- **Headlines:** 30 characters each (max 15 headlines)
- **Descriptions:** 90 characters each (max 4 descriptions)
- **Display Path 1:** 15 characters max
- **Display Path 2:** 15 characters max (optional)
- **Final URL:** Use full URL with UTM parameters

### Structure Requirements
```
Headline 1: "Organic Skincare Solutions" (25 chars)
Headline 2: "Shop High-Quality Products" (25 chars)
Headline 3: "30-Day Money-Back Guarantee" (27 chars)
... (up to 15)

Description 1: "Dermatologist-approved skincare for all skin types. Free shipping on orders over $50. Shop now." (97 chars — exceeds 90, fix to 90)
Description 1 (fixed): "Dermatologist-approved skincare for all skin types. Free shipping on orders over $50." (87 chars)
Description 2: "Natural ingredients, cruelty-free, and eco-friendly. Trusted by thousands of customers." (88 chars)
Description 3: "Learn which products work best for your skin type. Take our free quiz today." (76 chars)
Description 4: "Join our loyalty program and earn rewards on every purchase. Exclusive member deals." (85 chars)

Path 1: skincare
Path 2: shop
```

### Quality Targets
- **Ad Strength:** GOOD or EXCELLENT (recommended minimum)
- **Minimum asset count:** 8+ unique headlines, 4 descriptions
- **Best practices:**
  - Pin top 3 performing headlines (Google will still test unpinned)
  - Include primary keyword in 3+ headlines
  - Vary messaging: benefit-driven, urgency, social proof, value prop
  - First headline should grab attention
  - Descriptions should support/expand on headlines

### Example Ad Strength Progression
- **Poor:** 3 headlines, 2 descriptions → Ad Strength: Low
- **Fair:** 5 headlines, 3 descriptions → Ad Strength: Average
- **Good:** 8+ headlines, 4 descriptions with variety → Ad Strength: Good
- **Excellent:** 12+ headlines, 4 descriptions with strong variety and pinning → Ad Strength: Excellent

---

## DISPLAY — Responsive Display Ads (RDA)

### Overview
RDAs automatically adjust size, appearance, and format to fit available ad spaces across the Display Network.

### Image Requirements
- **Landscape image:** 1200x628 pixels (1.91:1 aspect ratio)
  - Use for banner placements, feed ads, top of page
  - Include product/lifestyle image, text overlay minimal

- **Square image:** 1200x1200 pixels (1:1 aspect ratio)
  - Use for sidebar placements, square feeds
  - Center product, ensure text readable at small sizes

- **Recommend:** Provide both landscape and square (system uses based on placement)

### Headline & Description Requirements
- **Short headlines:** 25 characters max, up to 5
  - Example: "Premium Skincare", "All Natural", "Shop Now"

- **Long headline:** 90 characters max, 1 required
  - Example: "Discover dermatologist-approved skincare that works for all skin types"

- **Descriptions:** 90 characters max, up to 5
  - Description 1: "Natural ingredients, dermatologist-tested, cruelty-free."
  - Description 2: "Free shipping on all orders. 30-day satisfaction guarantee."
  - Description 3: "Join 50,000+ happy customers. Shop premium skincare today."

### Additional Required Fields
- **Business name:** "Skincare Co" (max 25 chars)
- **Logo:** 128x128 pixels minimum (1:1 square)
  - High contrast, recognizable at small sizes

- **Final URL:** Full URL with UTM parameters

### Design Best Practices
- **Color contrast:** 4.5:1 minimum for text legibility (WCAG AA)
- **Text overlay:** Max 20% of image area (Google policy)
- **Brand presence:** Logo visible, brand colors used
- **Product visibility:** Primary product clearly visible in image
- **Mobile-optimized:** Readable on devices as small as 200px width

### Quality Targets
- Professional photo/design quality
- Clear call-to-action visible
- Text readable at all sizes
- Consistent with brand visual identity

---

## YOUTUBE VIDEO — In-Stream & Bumper Ads

### Overview
Google Ads supports multiple YouTube video formats. Each has specific requirements.

### 1. Bumper Ads (6 seconds)
- **Duration:** Exactly 6 seconds (±100ms acceptable, aim for 5.5-6 seconds)
- **Resolution:** 1920x1080 (16:9) OR 1280x720 (16:9)
- **Codec:** H.264 video, AAC audio
- **Format:** MP4 container
- **File size:** Max 100 MB
- **Maximum word count:** ~50-55 words (roughly 10 words/second)

**Script example (6 seconds):**
"Introducing Skincare Pro — the all-in-one solution for your skin care needs. Our dermatologist-approved formula works for all skin types. Get 30% off your first order. Shop Skincare Pro today. Limited time offer."

### 2. In-Stream Non-Skippable Ads (15 seconds)
- **Duration:** Exactly 15 seconds (±100ms acceptable)
- **Resolution:** 1920x1080 (16:9) OR 1280x720 (16:9)
- **Codec:** H.264 video, AAC audio
- **Format:** MP4 container
- **File size:** Max 1 GB
- **Maximum word count:** ~75-85 words

**Script example (15 seconds):**
"Tired of skincare products that don't work? Introducing Skincare Pro — formulated by dermatologists for all skin types. Our customers see results in just two weeks. Natural ingredients, cruelty-free, and eco-friendly. Get 20% off your first order at SkincarePro.com. Use code FIRST20 at checkout. Shop now."

### 3. In-Stream Skippable Ads (15-30 seconds)
- **Duration:** 15-30 seconds (most effective: 20-25 seconds)
- **Resolution:** 1920x1080 (16:9) OR 1280x720 (16:9)
- **Codec:** H.264 video, AAC audio
- **Format:** MP4 container
- **File size:** Max 1 GB
- **Maximum word count:** 150-180 words for 30 seconds

**Hook requirement:** First 3 seconds MUST grab attention (viewers can skip after 5 seconds)

**Structure (20-25 sec example):**
- 0-3 sec: Hook (problem statement or intriguing visual)
- 3-8 sec: Solution intro (product reveal)
- 8-15 sec: Benefit/social proof
- 15-20 sec: Call-to-action
- 20-25 sec: Final CTA + offer

**Script example (20 seconds):**
"Are you struggling with acne-prone skin? [Hook, 0-3s] Skincare Pro is formulated to target breakouts at the source. [Product reveal, 3-8s] 87% of customers saw clearer skin in 2 weeks. Dermatologist-recommended, natural ingredients. [Proof, 8-15s] Visit SkincarePro.com and use code CLEAR15 for 15% off. [CTA, 15-20s] Order today." [20s]

### 4. Thumbnail (Video Discovery/Remarketing)
- **Resolution:** 1280x720 pixels (16:9 aspect ratio)
- **File format:** JPG or PNG
- **Max file size:** 10 MB
- **Recommended:** Include text overlay with product/offer to increase CTR

**Thumbnail design best practices:**
- Text overlay: "50% OFF", "Shop Now", or product name (readable at small sizes)
- High contrast colors
- Clear product visibility
- Brand logo corner
- Engaging visuals (faces, motion, product close-ups)

### Video Specifications Summary

| Spec | 6s Bumper | 15s Non-Skip | 15-30s Skippable | Thumbnail |
|------|-----------|--------------|------------------|-----------|
| Duration | 6 sec | 15 sec | 15-30 sec | N/A |
| Resolution | 1920x1080 or 1280x720 | 1920x1080 or 1280x720 | 1920x1080 or 1280x720 | 1280x720 |
| Aspect ratio | 16:9 | 16:9 | 16:9 | 16:9 |
| Max word count | 50-55 | 75-85 | 150-180 | N/A |
| Hook timing | 0-3 sec | 0-5 sec | 0-3 sec critical | N/A |
| File size | Max 100 MB | Max 1 GB | Max 1 GB | Max 10 MB |

---

## SHOPPING — Product Listing Ads (PLAs)

### Overview
Shopping ads pull data from your Google Merchant Center feed. Your role is to optimize the data and ensure feed health.

### Product Title Requirements
- **Max length:** 150 characters
- **Best practice:** Front-load keywords (most important keywords first)
- **Include:** Product type, brand, key features (color, size, material)

**Example:**
- Poor: "Red Dress"
- Better: "Women's Red Cotton Summer Dress Size M"
- Excellent: "Womens Premium Red Cotton Summer Dress, Size M, Machine Washable, Red Casual Sundress"

### Product Description
- **Max length:** 5000 characters (but typically 100-250 chars for effective ads)
- **Include:** Key selling points, unique features, material, care instructions
- **Optimize for:** Readability, keyword inclusion, benefit-driven messaging

**Example:**
"Premium red cotton summer dress perfect for casual outings. Features: breathable cotton fabric, flattering A-line cut, adjustable straps, machine washable. Available in sizes XS-XL. Free shipping on orders over $50."

### Product Images
- **Minimum resolution:** 400x400 pixels
- **Recommended:** 1200x1200 pixels (for clarity)
- **Aspect ratio:** 1:1 (square) preferred
- **Max image file size:** 20 MB
- **Number of images:** 1-10 variants recommended
- **File format:** JPG, PNG, GIF, BMP, TIFF

**Image best practices:**
- Primary image: Product on white background, front-facing
- Secondary images: Different angles, worn/lifestyle photos, detail shots
- Clear product visibility (not obscured by models or backgrounds)
- No text overlays or watermarks
- High quality, professional photography

### Price Requirements
- **Format:** ISO 4217 currency code (USD, EUR, GBP, etc.)
- **Example:** "USD 49.99"
- **Best practice:** Keep prices in sync with website (update feed daily if prices change)

### Product Categories
- Use Google's standard product categories
- **Example:** "Apparel & Accessories > Clothing > Dresses"

### Availability
- Options: "in stock", "out of stock", "preorder"
- Update regularly based on inventory

### Condition
- Options: "new", "refurbished", "used"

### Ad Examples by Category

**Electronics (Headphones):**
- Title: "Sony WH-1000XM5 Wireless Noise-Canceling Headphones, Black"
- Description: "Industry-leading noise cancellation, 30-hour battery life, premium sound quality. Comfortable for long wear. Includes carrying case."
- Price: USD 349.99

**Fashion (Shoes):**
- Title: "Adidas Ultraboost 22 Running Shoes, Black/White, Size 10"
- Description: "Responsive cushioning for comfort and energy return. Lightweight design. Durable rubber outsole. Perfect for running or casual wear."
- Price: USD 179.99

**Beauty (Skincare):**
- Title: "CeraVe Moisturizing Cream, 16 oz, Fragrance-Free"
- Description: "Dermatologist-recommended formula with ceramides and hyaluronic acid. Oil-free, suitable for sensitive skin. Recommended by dermatologists worldwide."
- Price: USD 25.99

---

## PERFORMANCE MAX (PMax) — Asset Groups

### Overview
Performance Max campaigns use multiple asset types across Google's channels (Search, Display, Shopping, YouTube, Gmail). Your role is to provide complete, diverse assets.

### Asset Group Components

#### Headlines (15 total required)
- **Max length:** 30 characters each
- **Requirement:** All 15 required for full asset coverage
- **Variety:** Mix benefit-driven, feature-driven, urgency, social proof
- **Pinning:** Pin top 3-5 headlines (recommendations from historical performance)

**Example headlines:**
1. "Dermatologist-Approved Skincare"
2. "Shop Premium Natural Products"
3. "30-Day Money-Back Guarantee"
4. "Free Shipping on Orders $50+"
5. "Join 50,000+ Happy Customers"
6. "Organic Ingredients, Cruelty-Free"
7. "Solve Your Skin Problems Today"
8. "Trusted Skincare Since 2010"
9. "Expert-Formulated Skincare"
10. "Beautiful Skin Starts Here"
11. "Science-Backed Formulations"
12. "Your Skin's New Best Friend"
13. "Visible Results in 2 Weeks"
14. "Premium Quality, Affordable Prices"
15. "Transform Your Skincare Routine"

#### Long Headlines (5 total required)
- **Max length:** 90 characters each
- **Requirement:** All 5 required
- **Purpose:** Primary messaging, benefit-focused, detailed
- **Variety:** Different angles (results, trust, uniqueness, value, social proof)

**Example long headlines:**
1. "Discover dermatologist-approved skincare formulated for all skin types"
2. "Shop premium natural skincare products backed by 10 years of research"
3. "Get visible skin improvements in just 2 weeks or your money back"
4. "Join thousands of customers who've transformed their skin with our products"
5. "Award-winning skincare line trusted by dermatologists and beauty experts"

#### Descriptions (5 total required)
- **Max length:** 90 characters each
- **Requirement:** All 5 required
- **Variety:** Different benefits, proof, or value props

**Example descriptions:**
1. "Natural ingredients, dermatologist-tested, cruelty-free, eco-friendly."
2. "Free shipping on all orders. 30-day satisfaction guarantee. No questions asked."
3. "Clinically proven to reduce acne, wrinkles, and dark spots. Visible results."
4. "Trusted by 50,000+ customers. Average rating: 4.8/5 stars. Shop with confidence."
5. "Affordable luxury skincare. Premium formulations at accessible prices. Quality matters."

#### Images (required: 1 landscape, 1 square, plus variants)
- **Landscape (1.91:1 aspect ratio):** 1200x628 pixels minimum
  - Use for Display banners, top-of-page placements
  - Include product, lifestyle imagery, text overlay minimal

- **Square (1:1 aspect ratio):** 1200x1200 pixels minimum
  - Use for feed ads, gallery placements
  - Center product, readable at small sizes

- **Portrait (4:5 aspect ratio):** 960x1200 pixels minimum (optional but recommended)
  - Use for mobile feeds, Pinterest-style placements

- **Tall (9:16 aspect ratio):** 1080x1920 pixels minimum (optional)
  - Use for Stories-style placements

**Recommended image count:** 5-8 total (1-2 per aspect ratio)

#### Logos (optional but recommended)
- **Resolution:** 128x128 pixels minimum
- **Aspect ratio:** 1:1 (square)
- **Format:** PNG (transparent background) preferred
- **Count:** 1-2 logos

#### Videos (optional)
- **Format:** MP4, MOV, AVI
- **Duration:** 15-30 seconds optimal
- **Resolution:** 1920x1080 (1080p) or 1280x720 (720p)
- **Count:** 1-3 videos (optional, but improves asset diversity score)

#### Final URL
- **Required:** 1 final URL (with UTM parameters)
- **Display URL:** Optional (rarely used, auto-generated from final URL)

### PMax Completeness Requirements
| Asset Type | Minimum | Recommended | Required? |
|-----------|---------|-------------|-----------|
| Headlines | 10 | 15 | ✅ |
| Long Headlines | 3 | 5 | ✅ |
| Descriptions | 3 | 5 | ✅ |
| Landscape images | 1 | 2-3 | ✅ |
| Square images | 1 | 2-3 | ✅ |
| Portrait images | 0 | 1-2 | ⬡ |
| Tall images | 0 | 1 | ⬡ |
| Logo | 0 | 1 | ⬡ |
| Video | 0 | 1-2 | ⬡ |

### PMax Quality Metrics
- **Ad Strength:** Target GOOD or EXCELLENT
- **Asset diversity score:** Higher diversity = better performance (mix of promotional, educational, lifestyle imagery)
- **Headline variety:** Benefit-driven, feature-driven, urgency, social proof, value prop
- **Image quality:** Professional, high-resolution, brand-consistent
- **Audience signals:** Provide at least 1 audience signal (remarketing list, customer match, interest segment) for better targeting

---

## DEMAND GEN — Responsive Demand Gen Ads

### Overview
Demand Gen campaigns use responsive ads across Discover, Gmail, and YouTube feeds. Similar to PMax but simpler asset structure.

### Required Assets
- **Headlines:** 10-15 (max 30 chars each)
- **Descriptions:** 5-10 (max 90 chars each)
- **Landscape image:** 1200x628 (1.91:1)
- **Square image:** 1200x1200 (1:1)
- **Logo:** 128x128 (1:1, optional but recommended)
- **Final URL:** With UTM parameters

### Audience & Keyword Targeting
- **Audiences:** In-market segments, affinity audiences, custom audiences (from customer email lists)
- **Keywords:** Intent-focused keywords (5-20 recommended)
- **Topics:** Content topics (up to 3 recommended)

### Best Practices
- Focus on awareness and lead generation, not direct sales
- Use storytelling imagery (lifestyle, use cases)
- Headline should encourage discovery ("Learn more", "Discover", "Find out")
- Lower CPA targets than conversion campaigns (discovery is higher funnel)

---

## Summary Comparison Table

| Format | Headlines | Descriptions | Images | Videos | Aspect Ratios | Primary Use |
|--------|-----------|--------------|--------|--------|---------------|------------|
| RSA | 15 × 30ch | 4 × 90ch | N/A | N/A | N/A | Google Search |
| RDA | 5 × 25ch + 1 × 90ch | 5 × 90ch | 2 required | N/A | 1.91:1, 1:1 | Google Display |
| Video | N/A | N/A | 1 thumbnail | 1 required | 16:9 | YouTube In-Stream |
| Shopping | 1 title (150ch) | 1 desc (5000ch) | 1-10 | N/A | 1:1 | Google Shopping |
| PMax | 15 × 30ch | 5 × 90ch | 4-8 | 1-3 optional | Multiple | Multi-channel |
| Demand Gen | 10-15 × 30ch | 5-10 × 90ch | 2 required | N/A | 1.91:1, 1:1 | Discover/Gmail/YouTube |

---

## References
- [Google Ads Help: RSA Specs](https://support.google.com/google-ads/)
- [Google Ads Help: RDA Specs](https://support.google.com/google-ads/)
- [Google Ads Help: Video Ads](https://support.google.com/google-ads/)
- [Google Merchant Center Product Data Specs](https://support.google.com/merchants/)
- [Google Ads Help: PMax Assets](https://support.google.com/google-ads/)
