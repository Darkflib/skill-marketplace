---
name: social-image-sizes
description: Reference for social media and web platform image dimensions, aspect ratios, file size limits and formats. Use when creating, resizing, cropping or reviewing images for X/Twitter, Facebook, Instagram, Threads, LinkedIn, YouTube, TikTok, Bluesky, Mastodon, Reddit, Pinterest, Tumblr, Medium, GitHub, Twitch, SoundCloud, Nextdoor, Google Business Profile, Gmail logos or WordPress plugins/themes. Also use for Open Graph og:image and Twitter Card meta images, profile pictures, banners, headers, cover photos, thumbnails and link previews. Prevents guessing sizes from stale training data.
---

# Social Image Sizes

## Overview

Bundled, sourced dimensions for 77 image assets across 20 platforms, from the
[social-profile-image-sizes](https://github.com/chuckreynolds/social-profile-image-sizes)
dataset (MIT, Chuck Reynolds). Check this data before answering. Don't go from
memory, because platforms change these sizes often.

## When to Use This Skill

- Generating or resizing an image for a profile, banner, header, cover, post or thumbnail
- Writing `og:image` / `twitter:image` meta tags or a social card generator
- Reviewing whether an existing image will crop or render badly
- Answering "what size should X be for Y"

## Reference Files

### references/sizes.md
Human-readable tables, one section per platform, with notes and sources.
**Read when** you need a quick answer or want to compare across platforms.

### references/sizes.json
The raw dataset. **Read or parse when** you need exact fields: `width`, `height`,
`aspect`, `min`, `max`, `max_bytes`, `formats`, `sizes` (multiple required sizes),
`also` (alternate sizes), `published`, `verified`, `source_url`.

## Script

`scripts/sizes.py` (stdlib only) queries the JSON:

```bash
python3 scripts/sizes.py list                          # platforms + asset ids
python3 scripts/sizes.py show linkedin                 # everything for a platform
python3 scripts/sizes.py show twitter header           # one asset (aliases work)
python3 scripts/sizes.py search banner                 # find assets by keyword
python3 scripts/sizes.py check youtube video-thumbnail 1280 720   # exit 1 if it won't fit
python3 scripts/sizes.py markdown > references/sizes.md           # rebuild the tables
python3 scripts/sizes.py refresh                       # pull latest data from upstream
```

Run it from the skill directory, or give the full path to the script.

## Rules When Answering

1. **Report the `published` status.** `published: false` (marked † in the tables)
   means the platform documents no such size. The value is a working convention
   that renders well, but you can't cite it and it may change. Say so.
2. **Give the source** (`source_url` or the platform's `sources`) when the user
   needs something authoritative.
3. **Mention crop and safe-zone notes** (`detail`, `notes`, `qualifier`). Covers and
   banners often crop differently on desktop and mobile, so keep key content centred.
4. **Respect file limits.** Check `max_bytes` and `formats` before choosing an
   export format or quality.
5. **Note the data date.** `meta.last_verified` gives the date of the snapshot. If
   it is more than a few months old, or the user reports a mismatch, offer to run
   `refresh`.
6. **One image for many platforms:** 1200 x 630 (1.91:1) is the usual shared
   `og:image`. Run `check` against each target to confirm.

## Example

> "Make a LinkedIn banner for my profile"

1. `python3 scripts/sizes.py show linkedin profile-background`
2. Use the returned dimensions and crop notes for the canvas.
3. After generating, `check linkedin profile-background W H` to confirm.
