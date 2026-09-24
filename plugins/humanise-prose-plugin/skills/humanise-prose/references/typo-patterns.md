# Typo Patterns Catalogue

Realistic typing errors that read as speed, not ignorance.

The core distinction:
- **Spelling mistake**: writer doesn't know correct spelling → implies ignorance
- **Typo**: writer knows, finger slipped → implies speed, carelessness, human

A good typo is one where a reader sees it and thinks "they were typing fast",
not "they don't know how to spell that word."

---

## Pattern 1: Transpositions

Adjacent characters swapped. The most universal typing error — happens on
any keyboard, any speed. Very high plausibility.

Common examples:
| Original | Typo |
|----------|------|
| the | teh |
| and | adn |
| with | wiht |
| have | ahve |
| that | taht |
| from | form (careful — also a real word; only use if context is clear) |
| work | wrok |
| just | jsut |
| received | recevied |
| their | thier |
| being | bieng |
| some | smoe |

**Usage**: Safe in most registers. Very common in casual and professional email-style prose.

---

## Pattern 2: Missing Apostrophes in Contractions

The writer knows the contraction is "don't" but types "dont". This is
extremely common in fast typing and informal digital writing.

| Correct | Typo |
|---------|------|
| don't | dont |
| can't | cant |
| it's | its (careful — ambiguous with possessive) |
| I'm | Im |
| they're | theyre |
| we're | were (careful — ambiguous with past tense) |
| won't | wont (careful — real word meaning "accustomed to") |
| you're | youre |
| didn't | didnt |
| isn't | isnt |
| hasn't | hasnt |
| wouldn't | wouldnt |

**Usage**: Most plausible in casual and informal professional prose. Less
plausible in academic or formal writing. Avoid "its" for "it's" as it
introduces genuine ambiguity. "we're" → "were" and "won't" → "wont" also
introduce ambiguity; prefer others.

---

## Pattern 3: Adjacent Key Errors

Hitting a key next to the intended one. Particularly common when typing fast.

Keyboard adjacency reference (QWERTY):
- q: w, a
- w: q, e, s
- e: w, r, d
- r: e, t, f
- t: r, y, g
- o: i, p, l
- p: o, [, ;
- s: a, d, w
- d: s, f, e
- f: d, g, r
- g: f, h, t
- h: g, j, y
- n: b, m, h
- m: n, ,, j

Examples:
| Original | Typo | Key error |
|----------|------|-----------|
| here | herd | e→d adjacent |
| note | mote | n→m adjacent |
| thing | thong | i→o adjacent |
| work | work (or worm) | k→, adjacent |

**Usage**: Moderate plausibility. More convincing in casual prose. Less common
than transpositions. Use sparingly — one per piece if at all.

---

## Pattern 4: Doubled Characters

A key bounces or is pressed twice. Very common on laptop keyboards.

| Original | Typo |
|----------|------|
| the | thhe |
| and | annd |
| that | thaat |
| have | havve |
| this | thiis |

**Usage**: Low frequency in practice. Plausible but less common than
transpositions. Use maximum once per piece, only in very common words.

---

## Pattern 5: Missing Final Character

The finger lifts slightly early on the last character. More common in
casual/fast typing and on mobile.

| Original | Typo |
|----------|------|
| something | somethin |
| thinking | thinkin |
| going | goin |
| getting | gettin |
| working | workin |
| having | havin |

**Usage**: Only in casual register. Reads like mobile typing or texting pace.
Do not use in professional or academic register.

---

## Pattern 6: Missing Space

The spacebar is missed between two words. Very common.

| Original | Typo |
|----------|------|
| in the | inthe |
| of the | ofthe |
| at the | atthe |
| on the | onthe |
| to the | tothe |
| with the | withthe |

**Usage**: High plausibility. Works in any register. Use only between
short, common words. Avoid if it creates an ambiguous compound word.

---

## Pattern 7: Shorthand Creep (casual register only)

The writer slips into informal shorthand they'd use in texts. Only plausible
in casual or conversational prose — reads out of place in professional writing.

| Standard | Shorthand |
|----------|-----------|
| though | tho |
| through | thru |
| because | cuz / cos |
| you | u (very casual only) |
| to | 2 (very casual only; use sparingly) |

**Usage**: Casual register only. Reads as someone who codes-switches between
formal and informal writing. One instance per piece maximum.

---

## Placement Rules (summary)

1. **Not in the first or last sentence** — higher reader attention there
2. **Not in technical terms, proper nouns, brand names, or code**
3. **Not two typos in the same sentence**
4. **Prefer high-frequency words** — typo in "the" = speed; typo in "photosynthesis" = ignorance
5. **Distribute across the text** — not in the same paragraph twice
6. **Prefer transpositions and missing apostrophes** — highest universality
7. **Match to register**: Missing apostrophes and shorthand → casual/professional;
   doubled chars and transpositions → any register

## Density Guidelines

| Setting | Target | Cap |
|---------|--------|-----|
| `subtle` | 1 per 300 words | 3 per piece |
| `moderate` | 1 per 150 words | ~1 per paragraph |
| `none` | 0 | 0 |
