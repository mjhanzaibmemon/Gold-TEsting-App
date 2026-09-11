# Jugar Bazar — Complete Setup & Migration Guide

**Last Updated:** September 11, 2026
**Business:** Jugar Bazar (Pakistan's Pre-Owned Athletic Footwear Marketplace)
**Website:** [jugarbazar.com](https://jugarbazar.com)
**Owners:** Muhammad Jahanzaib Memon + Rasikh Ikram

> **PURPOSE:** This document captures EVERYTHING done to build the Jugar Bazar Shopify store, Meta ads, integrations, and customizations — so if we ever need to migrate to a new Shopify account or restart, we don't lose any work.

---

## 📋 TABLE OF CONTENTS

1. [Business Overview](#business-overview)
2. [Current Stack](#current-stack)
3. [Credentials & IDs](#credentials--ids)
4. [Shopify Store Setup](#shopify-store-setup)
5. [Theme Customizations (Kalles)](#theme-customizations-kalles)
6. [Shipping & Discount Rules](#shipping--discount-rules)
7. [Meta Business Setup](#meta-business-setup)
8. [Meta Ads Campaign](#meta-ads-campaign)
9. [Google Sheets Integration](#google-sheets-integration)
10. [Cloudflare DNS Setup](#cloudflare-dns-setup)
11. [Judge.me Reviews](#judgeme-reviews)
12. [Scripts Documentation](#scripts-documentation)
13. [Product Data](#product-data)
14. [Migration Steps for New Shopify](#migration-steps-for-new-shopify)
15. [Troubleshooting Notes](#troubleshooting-notes)

---

## 🏪 BUSINESS OVERVIEW

**Jugar Bazar** = Pakistan's pre-owned athletic footwear marketplace.

- **Products:** Preloved shoes — Nike, Adidas, Puma, Asics, Brooks, Hoka, New Balance, Skechers, Tommy Hilfiger, Artengo
- **Total SKUs:** 116 active products (as of Sept 2026)
- **Payment:** Cash on Delivery (COD) + card via checkout
- **Shipping:** Nationwide Pakistan, Rs 300 flat (FREE on orders Rs 5,000+)
- **Return Policy:** 7-day return
- **Address:** 1/6 Street Number 2, Karachi 74600, Pakistan
- **WhatsApp:** +92 325 2564235

### Business Structure
- **Capital Contributions:** Rs 320,000 total (60k+60k initial from each partner, then 130k+70k additional)
- **Legal:** Individual partnership between Jahanzaib + Rasikh
- **Migration Origin:** Previous store was moved TO current Shopify (r7tara-19)

---

## 🛠️ CURRENT STACK

| Component | Service | Notes |
|-----------|---------|-------|
| E-commerce | Shopify Advanced Plan | r7tara-19.myshopify.com |
| Theme | Kalles v13jul2026 | Theme ID: `163629334585` |
| Domain | jugarbazar.com | Managed via Cloudflare |
| Customer Accounts | account.jugarbazar.com | Cloudflare DNS → Shopify |
| Accounts Domain (Old) | hisab.jugarbazar.com | → Google Sheets iframe |
| Reviews | Judge.me (Free Plan) | 12 reviews imported |
| Ads | Meta Marketing API | FB Page + IG Shopping |
| Analytics | Meta Pixel + Shopify Analytics | Pixel ID: 1370254398539834 |
| Product Catalog | Meta Product Catalog | 116 products synced from Shopify |
| Automation | Python scripts | See [Scripts Documentation](#scripts-documentation) |
| Sheets Sync | Google Sheets API | Service account |

---

## 🔐 CREDENTIALS & IDs

**⚠️ SECURITY NOTE:** Raw secrets stored in `C:/Users/MUHAMMAD JAHANZEB/Desktop/shopify-sync/.env` — NEVER commit this file to public git.

### Shopify

```
SHOP_NAME=r7tara-19
Store URL=https://r7tara-19.myshopify.com
Custom Domain=https://jugarbazar.com
Admin URL=https://admin.shopify.com/store/r7tara-19
Business ID=80885317689
Theme ID=163629334585
Plan=Advanced Shopify
```

**Access Token:** stored as `SHOPIFY_TOKEN` in .env (rotate periodically for security).

### Meta (Facebook + Instagram)

```
FB_APP_ID=1766918834644138
FB_BUSINESS_ID=866855339853221
FB_PAGE_ID=866853269853428
FB_AD_ACCOUNT_ID=1687138489175349
PIXEL_ID=1370254398539834
INSTAGRAM=@jugarbazar
```

**Sensitive (in .env):** `FB_APP_SECRET`, `FB_ACCESS_TOKEN` (System User token, never expires)

**Facebook App:** "Jugar Bazaar API" — https://developers.facebook.com/apps/1766918834644138/
**System User:** "Shopify Sync Bot" (Admin role)

### Google

```
Service Account: sheets-sync-bot@jugar-bazaar.iam.gserviceaccount.com
Project: jugar-bazaar
Sheet ID: 1TIX2SP_oFa_KjLwboE1dARdFBK0U9XYqppUa5w4aIJk
```

**Credentials file:** `google-credentials.json` (in shopify-sync folder — do NOT commit)

### Cloudflare

- Domain: jugarbazar.com (Free Plan)
- All DNS managed via Cloudflare
- DNS records added: `hisab`, `account` subdomains → various targets

---

## 🛒 SHOPIFY STORE SETUP

### Products
- **Total:** 116 active products, ~50 archived (sold pairs)
- **Categories:** Running, Casual/Lifestyle, Tennis/Court, Trail, Racing
- **Vendors:** Nike, Adidas, Puma, Asics, Brooks, Hoka, New Balance, Skechers, Artengo, Tommy Hilfiger
- **SKU Format:** `JB-XXXX` prefix for old batch, `JB2-XXXX` for new batch
- **Cost basis:** Old batch Rs 1,700; New batch Rs 2,000
- **All images:** Compressed to 2048px, JPEG Q85 (~184MB total from original 987MB)

### Pages
- Home
- Contact (**IMPORTANT:** Karachi address, NOT Australia — was fixed)
- About (Pre-owned marketplace narrative — was fixed for Google Merchant Center)
- Refund Policy (Rewritten via GraphQL for Google Merchant Center compliance)
- Privacy Policy
- Terms of Service
- Recently Sold (custom showcase page with grid of sold items)

### Checkout Configuration
- **Customer contact method:** Phone number or Email
- **Phone number field:** REQUIRED (critical fix — was optional)
- **Full name:** Required first + last
- **Company:** Don't include
- **Address line 2:** Optional
- **Email marketing opt-in:** ON (Checkout + sign-in)
- **WhatsApp opt-in:** ON (Pakistan region-specific)
- **SMS opt-in:** ON (Checkout only, requires app)
- **Tipping:** OFF

### Order Notifications (Automatic, FREE)
- Order confirmation → Customer (email)
- Order confirmation → mjhanzaibmemon37@gmail.com (owner)
- Shipping confirmation → Customer
- Order canceled → Customer
- Refund confirmation → Customer

---

## 🎨 THEME CUSTOMIZATIONS (Kalles)

### Product Page — Custom Blocks Added

Custom blocks added via `templates/product.json` → `main-product` section:

1. **jdgm_preview_badge** — Judge.me star rating near title (custom_liquid)
2. **stock_urgency** — "Hurry! Only X left" red styled box (custom_liquid)
3. **delivery_promise** — Fast Delivery + COD grid badge (custom_liquid)
4. **free_shipping_progress** — Dynamic "Rs X more for FREE shipping" bar (custom_liquid)
5. **reviews_carousel** — Custom auto-rotating carousel showing all 11 reviews across products (custom_liquid + JS)

**Free Shipping Progress Logic (Liquid):**
```liquid
{%- assign threshold_cents = 500000 -%}
{%- assign price_cents = product.selected_or_first_available_variant.price -%}
{%- if price_cents >= threshold_cents -%}
  🎉 This product qualifies for FREE Shipping!
{%- else -%}
  {%- assign needed_cents = threshold_cents | minus: price_cents -%}
  📦 Add Rs {{ needed_cents | money_without_currency }} more for FREE shipping!
{%- endif -%}
```

**Disabled blocks:**
- `custom_liquid_bhNa9U`, `sold_A9xmrH`, `live_view_XDrHtz`, `order_chNprL`, `inventory_qty_WNcnXq`, `custom_liquid_iTFEff` (all fake trust badges — REMOVED for Google Merchant compliance)

### Cart Page — Custom Injection

**File:** `sections/main-cart.liquid`
- Injected `{% render 'free-shipping-progress' %}` at top
- Marker comment: `<!-- JB_FREE_SHIP_INJECTED -->`

**Snippet:** `snippets/free-shipping-progress.liquid`
Shows:
- Free shipping progress bar (yellow → green gradient)
- Dynamic "Rs X more for FREE shipping" message
- 4-badge trust grid: COD, 7-day return, Nationwide delivery, Quality checked

### Recently Sold Page
- Custom Shopify page with grid of sold products
- Each card: image + product name + variant + "SOLD" badge
- Info banner explaining trust
- CTA to `/collections/all`

### Reviews Carousel (Custom, FREE alternative to Judge.me paid features)
- 11 reviews scraped from Judge.me via Python script
- Auto-rotating with 5-second interval
- Manual nav (←/→ buttons + dots)
- Touch/swipe support
- Responsive: 3 cards desktop, 2 tablet, 1 mobile
- Shuffled on each page load
- Gradient avatars with initials
- Product name clickable to product page

---

## 🚚 SHIPPING & DISCOUNT RULES

### Shipping (Delivery Profile ID: `114280300601`)

| Rate Name | Price | Applies To |
|-----------|-------|------------|
| Standard Shipping | Rs 300 | Orders Rs 0 – Rs 4,999.99 |
| FREE Shipping | Rs 0 | Orders Rs 5,000+ (auto-applied) |

**Zone:** Domestic (Pakistan only)

### Discount Codes (Live)

| Code | Discount | Purpose | Usage Limit |
|------|----------|---------|-------------|
| `BAZAR5` | 5% off entire order | Abandoned cart recovery | 100 uses |
| `BAZAR300` | FREE shipping | Abandoned cart recovery | 100 uses |
| `WELCOME10` | 10% off entire order | Old customer recovery | 50 uses |

All codes: **once per customer**, no expiry.

---

## 📱 META BUSINESS SETUP

### Business Manager
- **URL:** https://business.facebook.com/latest/settings/?business_id=866855339853221
- **Owners:** Rasikh Ikram (You) + Ehsaan Ahmed (old marketing agent — retained for legacy access)
- **Assets:** Ad Account, FB Page, Instagram, Pixel, Catalog

### Facebook App
- **Name:** Jugar Bazaar API
- **App ID:** 1766918834644138
- **Type:** Business
- **Products enabled:** Marketing API, Conversions API
- **Mode:** Development (not Live — but sufficient for our API needs)

### System User
- **Name:** Shopify Sync Bot
- **Role:** Admin
- **Token expiration:** Never
- **Permissions granted:**
  - `ads_management`, `ads_read`
  - `business_management`
  - `catalog_management`
  - `pages_read_engagement`, `pages_manage_ads`, `pages_show_list`
  - `public_profile`, `threads_business_basic`

### Meta Pixel
- **ID:** 1370254398539834
- **Name:** "Jugar bazar new data"
- **Status:** Active, firing regularly
- **Events tracked:** PageView, ViewContent, AddToCart, InitiateCheckout, Purchase (via Shopify auto-integration)

### Product Catalog
- **Name:** "Shopify Product Catalog (r7tara-19.myshopify.com) - 2026-07-16 System User"
- **ID:** 3539723762877196
- **Products:** 116 (auto-synced from Shopify)

### Instagram Business Account
- **Username:** @jugarbazar
- **Followers:** 38 (as of Sept 2026)
- **Connected to:** FB Page + Business Manager
- **Assets:** Content, Messages, Community, Ads, Insights — all granted to Shopify Sync Bot

---

## 🎯 META ADS CAMPAIGN

### Campaign Structure

**Campaign:** Jugar Bazar — Sales — Sept 2026 (Draft)
- **ID:** 52540414698950
- **Objective:** OUTCOME_SALES
- **Status:** ACTIVE
- **Budget:** Ad set level (not campaign level)

**Ad Set 1 — Broad (Cold Prospecting)**
- ID: `52540414702350`
- Budget: Rs 700/day
- Duration: Sept 3–11 (~7 days)
- **Age:** 20-45 (both genders)
- **Cities (11):** Karachi, Lahore, Islamabad, Rawalpindi, Faisalabad, Multan, Hyderabad, Peshawar, Sialkot, Gujranwala, Bahawalpur
- **Interests (11):** Nike, Adidas, Puma, Asics, New Balance, Brooks, Skechers, Physical fitness, Running (sport), Trainers (footwear), Women's clothing
- **Placements:** FB Feed, Marketplace, Story, Reels; IG Feed, Story, Reels
- **Optimization:** Purchase (OFFSITE_CONVERSIONS)
- **Exclusions:** All Site Visitors 180d, Ehsaan Ahmed

**Ad Set 2 — Retargeting (Warm Audience)**
- ID: `52541380147950`
- Budget: Rs 300/day
- Duration: Sept 9–13 (5 days)
- **Age:** 18-55 (both genders)
- **Geo:** All Pakistan
- **Includes:** All Visitors 180d + Add to Cart 180d + Initiate Checkout 180d
- **Excludes:** Purchasers 180d, Ehsaan Ahmed

### Ads (13 Total)

**Active (1):**
- Carousel - 10 Products Mega (10 slides: 10 different products)

**Paused (12 — backup):**
- Individual ads for: Adidas Tensaur, Adidas Cloudfoam, Adidas LightMotion, Artengo Fast Pro, Asics Trabuco 11, Asics Windhawk 4, Asics GT-2000 12, Brooks Adrenaline GTS 22, Brooks Ghost 14, Hoka Arahi 6, Tommy Hilfiger, Recently Sold Showcase

### Ad Creatives
- **Design:** Professional AI-designed in Canva/similar tool
- **Style:** Green/black Jugar Bazar branding, "STEP INTO COMFORT & STYLE" headlines, trust badges (Cash on Delivery, Nationwide Delivery, Quality Checked, Clean Tested Trusted), shoe on grass/lifestyle backgrounds
- **Location:** `C:\Users\MUHAMMAD JAHANZEB\Desktop\shopify ad\` (12 JPEGs, named with product URL slug in filename)
- **AI Variations:** Meta's Advantage+ Creative Enhancements enabled (adds AI variants automatically)

### Custom Audiences

| Audience Name | ID | Type | Purpose |
|---------------|-----|------|---------|
| All Site Visitors 180d | (see .env or Meta dashboard) | Website pixel | Retargeting include |
| Add to Cart 180d | ↑ | Website pixel | Retargeting include |
| Initiate Checkout 180d | ↑ | Website pixel | Retargeting include |
| Purchasers 180d | ↑ | Website pixel | Exclusion (don't retarget existing buyers) |
| Ehsaan Ahmed | ↑ | Customer List (email hash) | Exclusion (old marketing agent) |

### Historical Performance (Sept 4–11)
- Total spent: Rs 3,619+
- Impressions: 5,547+
- Clicks: 516
- CTR: 9.30% (excellent — industry avg 1-2%)
- Purchases: 4 (Meta pixel tracked)
- Real ROAS: ~7-10x
- Revenue attributed: ~Rs 25,894

---

## 📊 GOOGLE SHEETS INTEGRATION

### Sheet Structure
**Sheet ID:** 1TIX2SP_oFa_KjLwboE1dARdFBK0U9XYqppUa5w4aIJk
**URL:** hisab.jugarbazar.com (Cloudflare redirect)

### Tabs
1. **DASHBOARD** — Overview with capital, sales, expenses, profit/loss
2. **CAPITAL** — Partner contributions log
3. **SALES** — Auto-synced from Shopify via `sync.py` (order details, customer, product, price, status)
4. **EXPENSES** — Manual entry (Meta Ads, Shopify subscription, food, petrol, misc)
5. **PURCHASES** — Manual entry (inventory bought)
6. **STARTUP COSTS** — One-time (domain, migration, equipment)
7. **RETURNS** — Auto-synced from Shopify cancelled orders

### Sync Script
- **File:** `sync.py`
- **Runs:** Manually or via scheduler
- **Function:** Fetches Shopify orders → updates SALES sheet + reconciles cancellations in RETURNS

---

## ☁️ CLOUDFLARE DNS SETUP

### Domain: jugarbazar.com (Free Plan)

**DNS Records:**
```
Type   | Name    | Target                          | Purpose
-------|---------|--------------------------------|-----------
A      | @       | Shopify IP (23.227.38.65)       | Main store
CNAME  | www     | shops.myshopify.com             | www redirect
CNAME  | account | shops.myshopify.com             | Customer accounts
CNAME  | hisab   | (Google Sheets embed)           | Accounts sheet
```

### Redirect Rules
- `hisab.jugarbazar.com` → Google Sheet iframe

---

## ⭐ JUDGE.ME REVIEWS

- **Plan:** Free
- **Total reviews imported:** 12 (via CSV upload)
- **Distribution:** 8 products with reviews (1-2 each)
- **Widgets used:**
  - Preview badge (near product title) — Free
  - Reviews widget (on product page bottom) — Free
- **Duplicate widget FIX applied:** Removed 1 duplicate `apps` section from `templates/product.json`

### Custom Solution for Missing Features
Judge.me Free plan doesn't include "Reviews Carousel" — so we built a **custom carousel** via Python script (`build_custom_carousel.py`) that:
1. Scrapes all reviews from products
2. Deduplicates
3. Generates HTML+CSS+JS carousel
4. Injects into `templates/product.json` as custom_liquid block

**Re-run script anytime new reviews are added** to refresh the carousel.

---

## 🐍 SCRIPTS DOCUMENTATION

**Location:** `C:\Users\MUHAMMAD JAHANZEB\Desktop\shopify-sync\`

**Python:** `C:\Users\MUHAMM~1\AppData\Local\Programs\Python\Python313\python.exe`

### Setup
```bash
pip install requests python-dotenv gspread google-auth Pillow openpyxl
```

### Core Scripts

| Script | Purpose |
|--------|---------|
| `sync.py` | Main Shopify→Google Sheets sync (SALES + RETURNS tabs) |
| `upload_images_only.py` | Bulk upload product images from local folders |
| `upload_batch_26p.py` | Upload 26 additional products with metadata |
| `bulk_update_existing.py` | Bulk set SKUs, costs, alt-text on existing products |
| `rename_local_folders.py` | Rename local product folders for consistency |
| `compress_images.py` | Compress images to 2048px + JPEG Q85 (saved 800+ MB) |
| `replace_shopify_images.py` | Replace uncompressed images on Shopify with compressed versions |
| `fix_misrepresentation.py` | Fix Google Merchant Center misrepresentation issues (product descriptions, About, Refund policy, Contact) |
| `hide_sold_and_showcase.py` | Archive sold products + create "Recently Sold" page |
| `inject_jdgm.py` | Inject Judge.me widgets into theme |
| `remove_duplicate_reviews.py` | Remove duplicate review sections |
| `enable_real_features.py` | Enable real conversion features (stock counter, delivery, free shipping progress) |
| `fix_layout.py` | Fix product page layout bugs (free shipping calculation, stock urgency styling) |
| `add_reviews_carousel.py` | Add Judge.me carousel widget (paid feature — replaced) |
| `build_custom_carousel.py` | Build CUSTOM reviews carousel (free alternative — scrapes + generates HTML) |
| `fix_all_checkout_issues.py` | Fix shipping + cart page enhancements |
| `fix_shipping_and_cart_v2.py` | GraphQL-based Delivery Profile update (FREE shipping Rs 5,000+) |
| `fb_audit.py` | Full audit of Meta Ads account (campaigns, spend, insights) |
| `create_ad_campaign.py` | Create Meta ad campaign with 12 individual ads |
| `create_ads_v2.py` | v2 with better creative formats |
| `create_retargeting.py` / `_v2.py` | Create retargeting campaign with custom audiences |
| `update_campaign.py` | Update ad set budget, targeting, duration |
| `full_verification.py` | Full verification of all setup (Shopify + Meta + shipping + discount codes) |

### Environment Variables (.env)

```
SHOPIFY_TOKEN=<shopify_admin_api_token>
SHOP_NAME=r7tara-19
SHEET_ID=1TIX2SP_oFa_KjLwboE1dARdFBK0U9XYqppUa5w4aIJk

FB_APP_ID=1766918834644138
FB_APP_SECRET=<facebook_app_secret>
FB_ACCESS_TOKEN=<system_user_access_token>
FB_AD_ACCOUNT_ID=1687138489175349
FB_BUSINESS_ID=866855339853221
```

---

## 📦 PRODUCT DATA

### Categories with product counts
- **Running Shoes:** ~70 (Nike, Adidas, Asics, Brooks, Hoka, New Balance, Puma)
- **Casual/Lifestyle:** ~25 (Adidas LightMotion, Tommy Hilfiger, Skechers)
- **Tennis/Court:** ~10 (Artengo, Asics Gel Resolution, Adidas Gamecourt)
- **Trail:** ~8 (Asics Trabuco, Hoka Speedgoat)
- **Racing:** ~3 (Asics Windhawk)

### Pricing Range
- Low: Rs 1,999
- Mid: Rs 2,999 – Rs 3,999 (most common)
- High: Rs 4,999 – Rs 7,999
- Premium: Rs 8,000+

### Vendor Fix
- **Original mistake:** Vendor field was "Jugar Bazar" on all products
- **Correction:** Fixed to actual brand names (Nike, Adidas, etc.) — required for Google Merchant Center compliance

---

## 🔄 MIGRATION STEPS FOR NEW SHOPIFY

If you ever need to migrate to a new Shopify account, follow this order:

### Phase 1: New Shopify Account Setup
1. Create new Shopify account (choose Basic Shopify plan, NOT Advanced — save $270/mo)
2. Connect domain `jugarbazar.com` (transfer Cloudflare DNS)
3. Install Kalles theme (or new theme)
4. Set up plan payment method

### Phase 2: Data Export/Import
1. **Products:** Export from old Shopify (`/admin/products?export=1`) → import to new
2. **Customers:** Export customer list → import to new
3. **Orders:** Export historical orders (for records only, can't import active)
4. **Discount codes:** Re-create BAZAR5, BAZAR300, WELCOME10 (use `create_discount_codes.py` or manual)
5. **Pages:** Copy About, Contact, Refund Policy, Privacy Policy, Recently Sold
6. **Shipping rules:** Re-create FREE shipping Rs 5,000+ + Standard Rs 300 (use GraphQL script or manual)
7. **Theme customizations:** Re-apply blocks in `templates/product.json` + `sections/main-cart.liquid` (see [Theme Customizations](#theme-customizations-kalles))

### Phase 3: Integrations
1. **Judge.me:** Reinstall app, import review CSV
2. **Meta Ads:** Update Ad Account to point to new store (`shop_id` in Meta Pixel)
3. **Meta Pixel:** Update Pixel ID in Shopify admin → Preferences
4. **Product Catalog:** Reconnect via Meta Business Suite → Sales channels
5. **Google Sheets:** Update `SHOP_NAME` in .env, re-run `sync.py`
6. **Cloudflare DNS:** Update A record if store IP changes

### Phase 4: Content Restoration
1. Upload product images (from `C:\Users\MUHAMMAD JAHANZEB\Desktop\shopify-sync\new stock\`)
2. Re-run `bulk_update_existing.py` for SKUs, costs, alt-text
3. Re-inject theme customizations via Python scripts
4. Rebuild reviews carousel: `build_custom_carousel.py`
5. Set up checkout settings (Phone required, WhatsApp opt-in)

### Phase 5: Verify
Run `full_verification.py` — this checks 35+ setup items and reports what's OK vs missing.

---

## 🐛 TROUBLESHOOTING NOTES

### Common Issues Faced (Documented for Future)

1. **Google Merchant Center Misrepresentation** (Aug 2026)
   - Cause: Australian address in Contact page + Footer, missing pre-owned disclosure in product descriptions
   - Fix: Updated 115 product descriptions to include "Preloved" tag, changed all addresses to Karachi, rewrote Refund Policy + About page
   - Script: `fix_misrepresentation.py`

2. **Cart Abandonment 83%** (Sept 2026)
   - Cause: Phone number OPTIONAL at checkout, FREE shipping promise not configured in Shopify shipping rules
   - Fix: Made phone REQUIRED, added FREE shipping rule Rs 5,000+
   - Result: Expected conversion drop from 83% to 40-50%

3. **Judge.me Reviews Duplicated**
   - Cause: 2 identical `apps` sections in `templates/product.json`
   - Fix: Removed duplicate section `1788290300c138765a`

4. **App in Development Mode blocks ad creative creation**
   - Cause: Meta Business apps have restrictions on creative creation while in Dev mode
   - Workaround: Manual ad creation via Ads Manager UI (structure via API, content via UI)

5. **Instagram not showing in Meta API**
   - Cause: Token missing `instagram_basic` permission
   - Impact: NON-BLOCKING — ads still show on IG via automatic placement via FB Page link
   - Fix (optional): Regenerate token with instagram_basic + instagram_manage_insights

6. **Custom Audiences ToS separate acceptance**
   - Cause: Meta has 2 separate ToS — one for general Custom Audiences, one for Customer Lists
   - Fix: User must accept both at https://business.facebook.com/customaudiences/app/tos/

7. **Ehsaan Ahmed (old marketing agent) — Exclude from retargeting**
   - Custom audience created from email: `ahmedehsaan56@gmail.com` (SHA256 hashed)
   - Added to both broad + retargeting ad set exclusions

---

## 📞 CONTACT & OWNERSHIP

**Business Owners:**
- Muhammad Jahanzaib Memon (`mjhanzaibmemon37@gmail.com`)
- Rasikh Ikram (`rasikhikram06@gmail.com`)

**Store Contact:**
- WhatsApp: +92 325 2564235
- Instagram: @jugarbazar
- Facebook: Jugar Bazar

**Service Providers:**
- Shopify Support: help.shopify.com
- Meta Business Support: business.facebook.com/business/help
- Cloudflare: dash.cloudflare.com
- Judge.me: help.judge.me

---

## 📈 KEY METRICS (as of Sept 11, 2026)

| Metric | Value |
|--------|-------|
| Total orders | 30+ (all-time) |
| Recent orders (Sept 5-8) | 5 |
| Total revenue (recent) | Rs 27,793 |
| Meta ad spend total | Rs 7,000+ |
| Best ROAS achieved | 10x |
| Products | 116 active |
| Reviews | 12 (Judge.me) |
| Followers (IG) | 38 |
| Followers (FB) | 38 |
| Customer Acquisition Cost | Rs 250-900 |
| Best Selling Category | Running shoes |

---

## 🎓 LESSONS LEARNED

1. **Don't fake trust badges** — Google Merchant Center bans stores with fake "10,898 trusted customers" numbers. Use REAL: actual reviews (Judge.me), real stock counter, honest shipping promises.

2. **Phone number MUST be required for COD** — Pakistan customers give phone but courier can't deliver without it.

3. **Follow through on promises** — If ad says "FREE shipping over Rs 5,000", make sure Shopify shipping rules actually deliver FREE at Rs 5,000+.

4. **Test checkout end-to-end** — Weekly test order (incognito) catches issues before customers do.

5. **Weekend timing matters** — Pakistan online shopping peaks Thu-Sat evenings. Payday (1st, 15th) sees spike.

6. **Cheap CTR ≠ conversions** — 8-11% CTR is excellent but doesn't guarantee sales if store has friction.

7. **Retargeting > Broad** for existing traffic — But zero-overlap is critical (exclude past visitors from broad campaigns).

8. **Advanced Shopify plan is overkill** for small stores — Basic ($29/mo) does everything most stores need.

---

## 🔜 PENDING / TODO

- [ ] Rotate Shopify Admin API token (created Jul 2026)
- [ ] Rotate FB App Secret (was shared in chat)
- [ ] Decide whether to keep Advanced plan or downgrade to Basic (~Rs 76,000/mo saving)
- [ ] Install WhatsApp automation app (Interakt or SuperLemon) when order volume justifies
- [ ] Set up abandoned checkout auto-emails (10 hours)
- [ ] Set customer accounts domain as primary (currently redirects to shopify.com)
- [ ] Contact Junaid Hassan for Rs 14,596 recovery (was abandoned 2x due to shipping bug)

---

## 📄 FILE MANIFEST

Backup these before ANY migration:

**shopify-sync/ folder:**
- `.env` (SENSITIVE — don't commit)
- `google-credentials.json` (SENSITIVE — don't commit)
- `sync.py` and all other `.py` scripts
- `campaign_ids.json`, `retargeting_ids_v2.json` (Meta IDs)

**Local folders:**
- `Desktop\shopify-sync\new stock\` (product images, compressed)
- `Desktop\shopify ad\` (12 ad creatives)
- `JUGAR BAZAAR.xlsx` (original accounting file)

---

**End of Migration Guide** — Keep this file updated as new work is done.

*Generated: September 11, 2026*
