# Andromeda Cluster Classification Guide

## Overview

Meta's Andromeda algorithm groups similar creatives into clusters to detect creative diversity and optimize ad delivery. Your job is to classify each ad into one of 7 visual style clusters and 5 color sub-clusters. This is a forensic practice — understand what your winning ads look like visually, ensure you're not over-indexing on one style, and identify gaps where you could differentiate.

## The 7 Visual Style Clusters

### 1. Product-Only
**Characteristics:**
- Focuses exclusively on the product
- Clean, minimal composition
- Product fills most of the frame
- Plain background (white, solid color, or simple)
- Professional, catalog-style presentation
- No people, no lifestyle context

**When to use:** E-commerce, tech products, high-SKU catalogs
**Performance:** Good for conversion optimization, often underperforms on engagement

**Examples:**
- Single product shot on white background
- Product photography on studio backdrop
- Product close-up with no context

---

### 2. Lifestyle
**Characteristics:**
- Product shown in real-world context
- People using the product
- Natural environment or home setting
- Focus on experience, not just the object
- Aspirational tone
- Often includes people's faces/emotions

**When to use:** Consumer goods, fashion, home products, wellness
**Performance:** High engagement, strong emotional connection, good ROAS

**Examples:**
- Woman using skincare product at home
- Friends wearing athletic gear outdoors
- Family cooking with kitchen appliance

---

### 3. UGC-Style (User-Generated Content)
**Characteristics:**
- Looks unpolished, authentic, "real"
- Hand-held camera effect or casual framing
- Natural lighting, not studio lit
- Visible imperfections
- Often features ordinary people, not models
- "Influencer" aesthetic without professional production

**When to use:** Direct-to-consumer, niche brands, Gen Z audiences
**Performance:** High engagement, high trust signal, very strong on Reels/Stories

**Examples:**
- Someone casually showing off a product on phone
- Blurry shot of a product with overlaid text
- Selfie-style testimonial video

---

### 4. Studio/Polished
**Characteristics:**
- Professional production value
- Studio lighting, controlled environment
- High-end aesthetic
- Expensive-looking, premium feel
- Perfect composition, color grading
- Often includes brand logo or branding elements

**When to use:** Luxury brands, premium positioning, B2B
**Performance:** Good for brand awareness, sometimes underperforms on direct response

**Examples:**
- High-end product photography with professional lighting
- Cinematic video with color grading
- Premium brand showcase

---

### 5. Text-Heavy/Graphic
**Characteristics:**
- Dominated by text overlays and graphics
- Large headlines, pricing, claims
- Often has discount badges, urgency text
- Heavy use of design elements
- Attention-grabbing text design
- Minimal or simple imagery

**When to use:** Performance marketing, urgency/scarcity offers, direct response
**Performance:** High direct response, but often triggers Meta's >20% text rule (lower delivery)

**Examples:**
- Deal banner: "50% OFF" with small product image
- Testimonial with large quote overlay
- Limited-time offer with countdown timer

---

### 6. Illustration/Graphic Design
**Characteristics:**
- Custom illustrations or graphics
- Cartoon or stylized artwork
- Designed/created, not photographed
- Often includes brand characters or custom art
- Abstract or conceptual visual approach
- Unique visual identity

**When to use:** Tech startups, educational content, abstract concepts
**Performance:** High brand recognition, good for awareness, variable ROAS

**Examples:**
- Custom illustrated character promoting app
- Abstract geometric design
- Infographic about product benefits

---

### 7. Video-Native
**Characteristics:**
- Designed specifically for video (not just a static image)
- Dynamic motion, animation, or video sequence
- Text, graphics, and motion elements integrated
- Often short-form vertical video (Reels/Stories)
- Motion-based storytelling
- May include transitions, cuts, quick pacing

**When to use:** Reels, Stories, social-first campaigns
**Performance:** Very high engagement on Reels, strong ROAS in video-optimized campaigns

**Examples:**
- Animated product demo video
- Quick-cut transitions showing product benefits
- Trending audio with product visuals

---

## The 5 Color Sub-Clusters

Within each visual style, further classify by color palette:

### 1. Warm Colors
**Palette:** Reds, oranges, yellows, warm browns
**Mood:** Energetic, exciting, urgency
**Best for:** Action, excitement, immediate response
**Example:** Red/orange discount banner

---

### 2. Cool Colors
**Palette:** Blues, teals, greens, cool purples
**Mood:** Calm, trust, professionalism
**Best for:** Premium, health, trust-focused messaging
**Example:** Blue sky lifestyle photo

---

### 3. Neutral/Grayscale
**Palette:** Whites, blacks, grays, earth tones
**Mood:** Clean, minimal, sophisticated
**Best for:** Premium brands, minimalist approach
**Example:** White background product shot

---

### 4. High-Contrast
**Palette:** Bold color combinations, black+neon, stark contrasts
**Mood:** Attention-grabbing, trendy, bold
**Best for:** Youthful audiences, disruptive brands
**Example:** Black background with neon pink text

---

### 5. Monochrome
**Palette:** Single color or variations (all reds, all blues, etc.)
**Mood:** Cohesive, brand-consistent, minimalist
**Best for:** Strong brand identity, visual consistency
**Example:** All-blue aesthetic with different shades

---

## Classification Process

### Step 1: Identify Visual Style
Look at each ad and ask:
- Is it just a product? → Product-Only (1)
- Is someone using it in a real setting? → Lifestyle (2)
- Does it look unpolished/authentic? → UGC-Style (3)
- Is it high-end professional production? → Studio/Polished (4)
- Is there more text than image? → Text-Heavy (5)
- Is it an illustration or custom graphic? → Illustration (6)
- Is this a video designed specifically for motion? → Video-Native (7)

### Step 2: Identify Color Palette
Once you've identified the style, determine the color palette:
- Dominant colors: red/orange/yellow? → Warm (1)
- Dominant colors: blue/teal/green? → Cool (2)
- Mostly white/gray/black? → Neutral (3)
- High contrast between very different colors? → High-Contrast (4)
- One color throughout? → Monochrome (5)

### Step 3: Assign Classification
Combine: `[Style]_[Color]`

**Examples:**
- Product-Only with white background → Product-Only_Neutral
- Lifestyle photo with warm sunset tones → Lifestyle_Warm
- UGC video with high-contrast editing → Video-Native_HighContrast
- Studio shot with cool blue tones → Studio_Cool

---

## Diversity Scoring

### Healthy Diversity
- At least 4-5 of the 7 visual styles represented
- Color palettes distributed across warm, cool, and neutral
- No single style >25% of active ad count
- Mix of high-engagement and high-conversion styles

### Warning Signs
- >25% of ads are Product-Only → Risk of fatigue
- >40% of ads are same color palette → Brand becomes predictable
- Only 2-3 visual styles represented → Not testing enough variety
- Zero Video-Native creatives → Missing high-engagement opportunity

### Diversity Score Calculation
```
Diversity Score = (Number of unique [Style]_[Color] combinations) / (Ideal number of combinations) × 100

Ideal = ~8-10 different [Style]_[Color] combinations across your ad portfolio
Score >70 = Healthy diversity
Score 40-70 = Some gaps, need new directions
Score <40 = Critical gaps, over-dependent on few styles
```

---

## Common Patterns in High-Performing Accounts

### Pattern 1: Lifestyle Dominates
- Lifestyle_Warm and Lifestyle_Cool combined = 40-50% of winners
- Why: Emotional connection drives conversions
- Action: Keep 30-40% lifestyle, fill rest with other styles

### Pattern 2: UGC + Text-Heavy Together
- UGC-Style_HighContrast (8-10%) + Text-Heavy_Warm (6-8%) = high ROAS
- Why: Authenticity + urgency
- Action: Ensure you have at least 3-4 variants of this combination

### Pattern 3: Video-Native Dominance on Reels
- Video-Native (in all color palettes) = 70%+ of top performers on Reels
- Why: Motion advantage in Reels algorithm
- Action: If running on Reels, prioritize Video-Native format

### Pattern 4: Color Matters Less Than Style for ROAS
- Within Lifestyle style, warm and cool perform similarly
- Within Text-Heavy, warm dramatically outperforms cool
- Action: Optimize color within the dominant winning style

---

## What NOT to Do

### Over-Clustering on One Style
- **Wrong:** 60% of ads are Product-Only
- **Result:** Creative fatigue, algorithm sees repetition, lower delivery
- **Right:** Max 25% in any single style; rotate new styles monthly

### Confusing UGC with Video-Native
- **UGC:** Could be static image that looks unpolished (UGC_Neutral)
- **Video-Native:** Motion-based, designed for video
- **Different:** UGC is about authenticity; Video-Native is about motion

### Forgetting Illustration/Graphic Cluster
- **Common mistake:** Never testing illustration style
- **Opportunity:** Unique visual differentiation; high brand recall
- **Action:** Test 1-2 illustration ads per campaign

---

## By Vertical Examples

### E-Commerce (Fashion)
**Diversity target:**
- 30% Lifestyle_Warm (aspirational)
- 20% Lifestyle_Cool (clean aesthetic)
- 15% UGC_HighContrast (trendy feel)
- 15% Product-Only_Neutral (product focus)
- 10% Video-Native_Warm (motion hook)
- 10% Studio_Cool (premium positioning)

### SaaS (Software)
**Diversity target:**
- 25% Studio_Cool (professional)
- 20% Video-Native_Cool (demo video)
- 20% Illustration_Neutral (concept explanation)
- 15% Text-Heavy_Cool (claims/benefits)
- 10% Lifestyle_Cool (user testimonial)
- 10% UGC_Neutral (authentic use case)

### Health & Wellness
**Diversity target:**
- 30% Lifestyle_Warm (transformation, energy)
- 25% UGC_HighContrast (authentic testimonial)
- 15% Studio_Cool (premium feel)
- 15% Text-Heavy_Warm (benefit claims)
- 10% Video-Native_Warm (transformation video)
- 5% Product-Only_Neutral (product focus)

---

## Quarterly Audit Checklist

Every 90 days, review your ad portfolio:

- [ ] Count ads per visual style. Any >25%?
- [ ] Count ads per color palette. Any >40%?
- [ ] How many unique [Style]_[Color] combinations exist? <8 = gap
- [ ] Which styles are MISSING entirely? Plan one test per gap.
- [ ] Do your top 20 performers match the diversified portfolio? If not, why?
- [ ] Has the algorithm changed (e.g., Reels algo favoring Video-Native)? Adjust.
- [ ] Are you testing new styles monthly? If not, start.
