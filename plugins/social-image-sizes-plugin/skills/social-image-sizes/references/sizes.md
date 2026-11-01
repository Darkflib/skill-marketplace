# Social Media Image Sizes Reference Guide

Source: https://github.com/chuckreynolds/social-profile-image-sizes (MIT). Last verified 2026-10-06. Units: pixels.

`published: false` (marked † below): published:false means the platform states no such size in any first-party documentation. The value is an observed convention that generally renders well, but it cannot be cited and may drift.

## X (formerly Twitter)

> X retired its Cards documentation when developer.x.com moved to docs.x.com — the old deep links now redirect to a generic overview and no replacement spec page exists. The card values below are the last officially published figures and can no longer be confirmed first-party.

| Asset | Size | Aspect | Notes |
|---|---|---|---|
| Profile Photo | 400 x 400 | 1:1 | max 2MB; JPEG / GIF / PNG, no animated GIFs; formats: jpeg, gif, png |
| Header Image | 1500 x 500 | 3:1 | ~60 px top and bottom can crop depending on monitor/browser |
| Post Image † | 1024 x 512 | 2:1 | displays inline as 506 x 253; 1200 x 675 also common for landscape; display: 506x253; alternate: 1200x675 |
| Article Image † | 5:2 ratio, e.g. 1000 x 400 | 5:2 |  |
| Card `twitter:card = summary` † | 1:1 | 1:1 | 144 x 144 min, 4096 x 4096 max; Last published by developer.x.com before the docs.x.com migration removed the Cards section. |
| Card `twitter:card = summary_large_image` † | 2:1 ratio | 2:1 | 300 x 157 min, 4096 x 4096 max; Last published by developer.x.com before the docs.x.com migration removed the Cards section. |

Sources: [help.x.com — uploading profile photos and headers and best sizes](https://help.x.com/en/managing-your-account/common-issues-when-uploading-profile-photo)

## Facebook

| Asset | Size | Aspect | Notes |
|---|---|---|---|
| Profile Photo † | 320 x 320 | 1:1 | displays as a circle; Facebook no longer states a size |
| Cover Photo | 851 x 315 optimal |  | 400 x 150 min; sRGB JPG under 100KB recommended; Crops to 16:9 on desktop and 2.4:1 on mobile — keep key content centered; formats: jpg |
| Post Link Image (Open Graph) | 1200 x 630 | 1.91:1 | 1.91:1; 600 x 315 min for the large render, 200 x 200 absolute min, 8MB max; minimum-for-feature: 600x315 |
| Event Image † | 1200 x 628 | 1.91:1 |  |
| App Icon † | 1024 x 1024 | 1:1 | PNG, for Facebook Login app config; Required by the app dashboard UI, but not stated in a fetchable public doc.; formats: png |

Sources: [facebook.com/help — cover photo](https://www.facebook.com/help/125379114252045); [developers.facebook.com — sharing best practices](https://developers.facebook.com/docs/sharing/webmasters/images)

## Instagram

| Asset | Size | Aspect | Notes |
|---|---|---|---|
| Profile Photo † | 320 x 320 | 1:1 | displays as circle |
| Feed Posts | upload at 1080 px wide |  | Instagram keeps 320–1080 px wide as-is, downsizes anything larger; Supported aspect range is 1.91:1 to 3:4 — i.e. 1080 x 566 (landscape) through 1080 x 1440 (max portrait); 1080 x 1350 (4:5) and 1080 x 1080 (1:1) are the common picks; anything outside the range gets cropped |
| Stories & Reels | 9:16, min 720 px resolution, min 30 FPS | 9:16 | 1080 x 1920 standard |
| Reel Cover Photo | 420 x 654 | 1:1.55 | 1:1.55 — can't be changed after upload |
| Reel Safe Zone † | 1080 x 1420 |  | top/bottom ~250 px overlaid by UI |

Sources: [help.instagram.com — image resolution](https://help.instagram.com/1631821640426723); [Reel size & aspect ratios](https://help.instagram.com/1038071743007909)

## Threads

> Meta hasn't published first-party Threads media specs, so every value below is unpublished — derived from Instagram parity (Threads runs on IG infrastructure) and observed app behavior.

| Asset | Size | Aspect | Notes |
|---|---|---|---|
| Profile Picture † | 320 x 320 | 1:1 | 1:1, syncs from Instagram |
| Post Image † | 1080 x 1350 | 4:5 | 4:5 portrait recommended; also 1:1 and 1.91:1 |
| Carousel † | up to 10 images |  | ≥1080 px wide each |
| Video † | 1080 x 1920 | 9:16 |  |
| Link Preview † | 1200 x 600 | 2:1 |  |

Sources: 

## LinkedIn

| Asset | Size | Aspect | Notes |
|---|---|---|---|
| Profile Photo | 400 x 400 | 1:1 | 268 x 268 min |
| Profile Background | 1584 x 396 | 4:1 |  |
| Link Preview (Open Graph og:image) | at least 1200 x 627 | 1.91:1 | 1.91:1 recommended, 5MB max; Images less than 401 px wide display as a thumbnail; No file types are published for the sharing module |
| Logo | 400 x 400 | 1:1 | 268 x 268 min |
| Cover Image | 4200 x 700 | 6:1 |  |
| Life Tab Main Image | 1128 x 376 | 3:1 |  |
| Life Tab Custom Modules | 502 x 282 |  |  |
| Life Tab Company Photos | 900 x 600 | 3:2 | 264 x 176 min |
| Company Post Images (with link) | 1200 x 627 | 1.91:1 | 1.91:1, 200 px min width; All page images: PNG or JPEG, 3MB max — LinkedIn recommends a high-res JPEG over PNG; formats: png, jpeg |

Sources: [linkedin.com/help — profile background](https://www.linkedin.com/help/linkedin/answer/a568217); [company & career pages](https://www.linkedin.com/help/linkedin/answer/a563309); [make your website shareable (link previews)](https://www.linkedin.com/help/linkedin/answer/46687)

## YouTube

| Asset | Size | Aspect | Notes |
|---|---|---|---|
| Profile Picture | displays at 98 x 98 | 1:1 | 15MB max; upload 800 x 800 so it stays sharp everywhere; alternate: 800x800 |
| Channel Banner / Cover | 2048 x 1152 min | 16:9 | 16:9 ratio; 2560 x 1440 recommended for TV; safe area 1235 x 338; 6MB max; safe-area: 1235x338 |
| Video Thumbnail | 3840 x 2160 recommended | 16:9 | 16:9, 640 px min width; 2MB max on mobile, 50MB on desktop; 1:1 for podcast playlists. Vertical videos with 16:9 thumbnails get an auto-generated 4:5 replacement in some surfaces.; formats: jpg, gif, png |
| YouTube Shorts Video † | 1080 x 1920 | 9:16 | YouTube documents Shorts as vertical but publishes no pixel dimension. |
| Video Watermark | 150 x 150 min | 1:1 | square, under 1MB |

Sources: [support.google.com/youtube — manage your channel branding](https://support.google.com/youtube/answer/10456525); [video thumbnails](https://support.google.com/youtube/answer/72431)

## TikTok

| Asset | Size | Aspect | Notes |
|---|---|---|---|
| Profile Photo | 20 x 20 min is the *only* size TikTok publishes | 1:1 | upload 400 x 400 or larger square; displays as circle; alternate: 400x400 |
| Video Feed | 9:16 recommended, 540 x 960 min | 9:16 | per TikTok's ad specs; 1080 x 1920 is the practical standard; Also accepted: 16:9 (960 x 540 min) and 1:1 (640 x 640 min) |
| Photo Mode Posts † | 1080 x 1920 | 9:16 | up to 35 photos per post |

Sources: [tiktok.com — adding a profile photo](https://www.tiktok.com/support/faq_detail?id=7581821549855038008); [ads.tiktok.com — in-feed ad video specifications](https://ads.tiktok.com/resources/help/article/tiktok-auction-in-feed-ads)

## Bluesky

> Bluesky publishes no size doc, so the dimensions above are unpublished and derived from the app. The file limits are first-party: the AT Protocol lexicon caps post images at 2,000,000 bytes and the link-card thumbnail at 1,000,000 bytes, and accepts any image type for both.

| Asset | Size | Aspect | Notes |
|---|---|---|---|
| Profile Picture † | 400 x 400 | 1:1 |  |
| Banner Image † | 1500 x 500 | 3:1 |  |
| Post Image † | 1080 x 1080 | 1:1 | max 2MB per image; Any image type, 2,000,000 bytes max (AT Protocol lexicon; formerly 1MB); Dimensions are unpublished. max_bytes and accepted types come from app.bsky.embed.images#image.image (accept image/*, maxSize 2000000), whose description says it was formerly limited to 1 MB. |
| Landscape Link Preview † | 1200 x 627 | 1.91:1 | Thumbnail: any image type, 1,000,000 bytes max (AT Protocol lexicon); Dimensions are unpublished. max_bytes and accepted types come from app.bsky.embed.external#external.thumb (accept image/*, maxSize 1000000). |
| Portrait Link Preview † | 627 x 1200 | 1:1.91 | Thumbnail: any image type, 1,000,000 bytes max (AT Protocol lexicon); Dimensions are unpublished. max_bytes and accepted types come from app.bsky.embed.external#external.thumb (accept image/*, maxSize 1000000). |

Sources: [bsky.app](https://bsky.app/); [AT Protocol lexicon - app.bsky.embed.external (link card)](https://github.com/bluesky-social/atproto/blob/main/lexicons/app/bsky/embed/external.json); [AT Protocol lexicon - app.bsky.embed.images (post images)](https://github.com/bluesky-social/atproto/blob/main/lexicons/app/bsky/embed/images.json)

## Mastodon

> Defaults from the reference Mastodon server software; individual instances can override.

| Asset | Size | Aspect | Notes |
|---|---|---|---|
| Avatar | downscales to 400 x 400 | 1:1 | max 2MB; WEBP/PNG/GIF/JPG; formats: webp, png, gif, jpg |
| Header | downscales to 1500 x 500 | 3:1 | max 2MB; formats: webp, png, gif, jpg |

Sources: [docs.joinmastodon.org — setting up your profile](https://docs.joinmastodon.org/user/profile/)

## Reddit

| Asset | Size | Aspect | Notes |
|---|---|---|---|
| Subreddit (Community) Icon | 300 x 300 | 1:1 |  |
| Subreddit Banner (desktop) | at least 1072 x 128 |  |  |
| Subreddit Banner (mobile) | at least 1080 x 128 |  |  |

Sources: [support.reddithelp.com — community icon](https://support.reddithelp.com/hc/en-us/articles/15484265952660-Community-icon); [banner](https://support.reddithelp.com/hc/en-us/articles/15484339588884-Banner)

## Pinterest

| Asset | Size | Aspect | Notes |
|---|---|---|---|
| Profile Photo † | upload 400 x 400 | 1:1 | displays as 165 x 165 circle; display: 165x165 |
| Profile Cover † | 1920 x 1080 | 16:9 | 16:9; image or video |
| Standard Pin | 1000 x 1500 | 2:3 | 2:3 ratio; larger ratios get cut off in feed; title: 100 char max — text box: 250 char max — description: up to 800 char (first 50–60 show in feed); safe zones: 270 px top, 65 px left, 195 px right, 790 px bottom; file: BMP / JPEG / PNG / TIFF / WEBP, 20MB max on web; formats: bmp, jpeg, png, tiff, webp |
| Video Pin | 1080 x 1920 | 9:16 | 9:16 ratio; 4 seconds to 5 minutes, H.264 or H.265 |
| Board Cover † | 600 x 600 | 1:1 |  |

Sources: [business.pinterest.com — creative best practices](https://business.pinterest.com/creative-best-practices/); [help.pinterest.com — pin specs](https://help.pinterest.com/en/article/review-pin-specs)

## Tumblr

| Asset | Size | Aspect | Notes |
|---|---|---|---|
| Avatar | 128 x 128 | 1:1 | max 10MB; JPEG / PNG / WEBP — GIFs go static; formats: jpeg, png, webp |
| Header Image | 2048 x 1152 | 16:9 | 16:9, max 10MB |
| Post Image | 540 x 810 recommended | 2:3 | 2:3 dashboard view; displays up to 2048 x 3072 on click if no click-through link is set; 20MB per image; 10 images per post in the apps, 30 on web |

Sources: [help.tumblr.com — image & GIF troubleshooting](https://help.tumblr.com/knowledge-base/image-gif-troubleshooting/)

## Medium

> Medium has no published spec for profile or post-cover dimensions; the platform scales images to fit its display contexts.

| Asset | Size | Aspect | Notes |
|---|---|---|---|
| Post Image | at least 1192 px wide |  | below that, the full-width and outset placement options don't appear; Max file size 25MB (.JPG, .JPEG, .GIF, .PNG); formats: jpg, jpeg, gif, png |

Sources: [help.medium.com — using images](https://help.medium.com/hc/en-us/articles/215679797-Using-images)

## GitHub

| Asset | Size | Aspect | Notes |
|---|---|---|---|
| Profile (Identicon) Picture † | 500 x 500 | 1:1 | GitHub publishes no avatar dimension; 500 x 500 is the generated identicon size. |
| Repo Social Preview Image | 1280 x 640 | 2:1 | 640 x 320 min, under 1MB; formats: png, jpg, gif |

Sources: [docs.github.com — repository social preview](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/customizing-your-repositorys-social-media-preview)

## Twitch

> help.twitch.tv is a Salesforce app that frequently fails to render for automated checks; read it in a browser. Re-read in full 2026-08-03: the channel setup article now states dimensions only for the profile banner and info panels. The profile picture and video player banner sizes it used to carry are gone, so those are marked unpublished.

| Asset | Size | Aspect | Notes |
|---|---|---|---|
| Profile Picture † | upload 800 x 800 | 1:1 | max display 256 x 256, 10MB max; display: 256x256; The channel setup article no longer states any profile picture dimensions. As of 2026-08-03 it says only: "Must be JPEG, PNG, or GIF and cannot exceed 10MB." The 800 x 800 upload and 256 x 256 display figures are long-standing convention that Twitch no longer documents. |
| Profile Banner | 1200 x 480 | 5:2 | scales to browser width; images are scaled to 480 high, so keep the artwork weighted left; The 3MB cap previously recorded here is not stated in the article and was dropped 2026-08-03. The article gives the dimension only: "The recommended size for a profile banner is 1200x480px." |
| Panel Images | 320 x 300 max |  | under 2.9MB; larger images are resized to these maximums automatically |
| Video Offline Banner † | 1920 x 1080 | 16:9 | 16:9; 1280 x 720 also accepted; alternate: 1280x720; Twitch documents no size for this. The channel setup article's "Upload a Video Player Banner" section gives steps only — and as of 2026-08-03 those steps are duplicated from the accent-colour section above it, so the article appears to have lost its banner instructions entirely. 1920 x 1080 remains the sensible upload size; it just cannot be cited. |
| Subscriber Emoticons | 28 x 28, 56 x 56, 112 x 112 |  | PNG, under 100KB each in manual mode, or a single 112–4096 px square PNG under 1MB with auto-resize; PNG format and the 112–4096 px auto-resize range come from the Emote Guidelines article; animated emotes are GIF, with a 512KB per-file cap in manual mode.; Corrected 2026-08-03: this entry recorded a 512KB per-file cap, which is the animated-GIF figure. For standard emotes the guide states the three manual-mode files "must each be under 100KB".; formats: png; sizes: 28x28, 56x56, 112x112 |
| Subscriber Badges | 18 x 18, 36 x 36, 72 x 72 |  | PNG, ≤25KB each; formats: png; sizes: 18x18, 36x36, 72x72 |

Sources: [help.twitch.tv — channel page setup](https://help.twitch.tv/s/article/channel-page-setup); [subscriber emote guide](https://help.twitch.tv/s/article/subscriber-emote-guide); [emote formatting & instant emote upload requirements](https://help.twitch.tv/s/article/emote-guidelines); [subscriber badge guide](https://help.twitch.tv/s/article/subscriber-badge-guide)

## SoundCloud

| Asset | Size | Aspect | Notes |
|---|---|---|---|
| Profile Image | square, at least 800 x 800 | 1:1 | max 2MB, .jpg or .png; formats: jpg, png |
| Track Artwork † | 1400 x 1400 | 1:1 | SoundCloud's upload guidance, not in the profile doc |
| Profile Header Banner | at least 2480 x 520 |  | max 2MB — below 1240 x 260 the zoom control is disabled; minimum-for-feature: 1240x260 |

Sources: [help.soundcloud.com — update your profile image and header](https://help.soundcloud.com/hc/en-us/articles/115003450007-Update-Your-Profile-Image-and-Header)

## Nextdoor

> Nextdoor's help article gives only the two values below. The larger figures widely circulated for Nextdoor (500 x 500 profile, 1156 x 650 banner) don't appear in any current first-party doc — use the published sizes.

| Asset | Size | Aspect | Notes |
|---|---|---|---|
| Agency / Business Profile Banner | 580 x 180 |  |  |
| Agency / Business Profile Logo | 120 x 120 | 1:1 |  |

Sources: [help.nextdoor.com — add a banner, photo, or logo to your public agency profile](https://help.nextdoor.com/s/article/How-to-add-a-banner-or-logo?language=en_US)

## Google Business Profile (Formerly "Google My Business" / "Google Local Business Center")

> Google publishes a single set of requirements for logos, cover photos, and additional photos alike. Any per-type dimensions you see elsewhere are convention, not spec.

| Asset | Size | Aspect | Notes |
|---|---|---|---|
| Logo & all photos | 720 x 720 recommended | 1:1 | 250 x 250 min, 10KB–5MB, JPG or PNG; formats: jpg, png |
| Cover Photo † | 1024 x 576 | 16:9 | 16:9 — Google applies one spec to every photo type |

Sources: [support.google.com/business — photos](https://support.google.com/business/answer/6103862)

## Google Workspace (Gmail) Logo

| Asset | Size | Aspect | Notes |
|---|---|---|---|
| Header Logo | 320 x 132 exact |  | PNG / JPG / GIF, non-animated; renders across Gmail, Calendar, Drive; formats: png, jpg, gif |

Sources: [knowledge.workspace.google.com — add your logo to Google Workspace](https://knowledge.workspace.google.com/admin/getting-started/add-your-logo-to-google-workspace)

## WordPress Plugin & Theme Dev

| Asset | Size | Aspect | Notes |
|---|---|---|---|
| Site Icon (Customizer → Site Identity → Site Icon) | square, at least 512 x 512 | 1:1 |  |
| Theme Screenshot | 1200 x 900 | 4:3 | `screenshot.png` or `.jpg` in theme root; must not exceed 1200 x 900; formats: png, jpg |
| Plugin Icons | 256 x 256, and 128 x 128 |  | formats: png; sizes: 256x256, 128x128 |
| Plugin Header Banners | 1544 x 500, and 772 x 250 |  | Plugin images go in an `/assets/` directory: `banner-1544x500.png`, `banner-772x250.png`, `icon-128x128.png`, `icon-256x256.png`; formats: png, jpg; sizes: 1544x500, 772x250 |

Sources: [developer.wordpress.org — plugin assets](https://developer.wordpress.org/plugins/wordpress-org/plugin-assets/); [theme structure (screenshot)](https://developer.wordpress.org/themes/core-concepts/theme-structure/); [wordpress.org — customizer (site icon)](https://wordpress.org/documentation/article/customizer/)

