# AI Tells Taxonomy

Comprehensive catalogue of patterns that signal AI authorship, with notes on
register applicability and suggested replacements.

---

## Category 1: Vocabulary Flags

High-confidence single-word signals. Any one of these in isolation is
ambiguous; clusters are diagnostic.

### The Delve Cluster
Words AI uses to signal engagement with a topic:
- delve (into) → examine, look at, dig into, get into
- explore (as filler) → only use when the text genuinely hasn't decided
- unpack → explain, break down
- examine (the nuances of) → usually just "look at X"

### The Importance Stack
Words AI uses to signal that something matters:
- crucial → usually cut; if needed, "important" once
- essential → same
- vital → same
- paramount → cut
- imperative → cut unless legal/procedural
- key (as adjective) → specific adjective or cut
- fundamental → usually cut; if needed, rephrase

### The Quality Cluster
Words AI uses to signal that something is good:
- robust → specify what you mean (reliable, fast, well-tested, etc.)
- seamless → cut or specify
- comprehensive → if truly comprehensive, say what it covers
- holistic → cut; specify what dimensions are included
- cutting-edge → say what's new about it
- state-of-the-art → same
- innovative → say what's novel
- sophisticated → say what's complex about it

### The Business Cliché Cluster
Words AI absorbed from business writing:
- leverage (verb) → use
- utilise → use
- synergy / synergistic → cut; describe the actual relationship
- ecosystem (metaphorical) → network, set of tools, community, etc.
- landscape (metaphorical, "the AI landscape") → field, space, area, world
- game-changer → describe the actual impact
- paradigm shift → describe what changed
- disruption / disruptive → describe what it displaces

### The Uncertainty Cluster
Words AI uses to avoid commitment:
- nuanced → specify the nuance or cut
- multifaceted → say which facets
- complex (as empty qualifier) → either explain the complexity or cut
- intricate → same as complex
- dynamic (as empty qualifier, "the dynamic nature of") → cut

---

## Category 2: Phrase Patterns

Multi-word constructions that are near-certain AI signals.

### Setup Phrases (preambles that delay the point)
These should almost always be cut — just make the claim directly:
- "It's worth noting that…" → [state the thing]
- "It's important to note that…" → [state the thing]
- "It's crucial to understand that…" → [state the thing]
- "One thing to keep in mind is…" → [state the thing]
- "It should be noted that…" → [state the thing]
- "Needless to say…" → [cut, or if genuinely needed, just say it]
- "I cannot stress enough…" → cut; if it's important, the content will show it

### Conclusion Signals
AI loves to announce it's concluding:
- "In conclusion,…" → just end the piece
- "To summarise,…" → just end the piece
- "In summary,…" → just end the piece
- "Ultimately,…" → sometimes OK, but often a setup for restating the thesis
- "All in all,…" → cut
- "At the end of the day,…" → cut (cliché in all writing)

### Transition Starters
AI starts paragraphs and sentences with these at unnatural frequency:
- "Furthermore,…" → "Also", or start a new sentence without a connector
- "Moreover,…" → same
- "Additionally,…" → same
- "In addition,…" → same
- "However,…" (overused) → fine once, not as a default contrast marker
- "Nevertheless,…" → fine occasionally
- "Subsequently,…" → "Then", "After that", or restructure
- "Consequently,…" → "So", "As a result", or restructure

### The Balanced-Take Formula
AI hedges everything to avoid taking a position:
- "While X has benefits, it also has drawbacks" → take a position; say which outweighs
- "On one hand… on the other hand…" → fine once; AI uses it as a template
- "X can be both A and B depending on context" → specify what context

### The Rhetorical Question Setup
AI uses rhetorical questions to introduce sections:
- "So what does this mean for…?" followed by the answer
- "But why does this matter?" followed by the answer
- "How can we address this?" followed by the answer
Humans use rhetorical questions less formulaically. If present, rewrite the
transition as a direct statement or a more natural bridge.

---

## Category 3: Structural Patterns

Patterns visible at the paragraph or document level.

### The Five-Paragraph Essay Ghost
Intro that states the thesis → Three body paragraphs → Conclusion that
restates the intro. This is the default AI document shape. Cut the restatement
conclusion. Consider merging short body paragraphs.

### The Exhaustive List
AI enumerates all cases; humans enumerate important ones:
- "There are five key considerations: A, B, C, D, and E."
- Humans: "The main thing is A. B also matters, and there's a minor wrinkle around C."
Trim lists by removing the least important items; gesture at remainder if needed.

### Perfect Parallel Structure
Every item in every list has the same grammatical shape, same approximate length,
and a tidy closing period. One or two should be a fragment. One should be shorter.
The rhythm should not be metronomic.

### The Section Header for Everything
AI puts a header on every paragraph or thought. In prose, this reads as
over-organised. Remove headers from shorter pieces; consolidate sections.

### Symmetrical Paragraphs
When every paragraph in a piece is 3–5 sentences, suspicion is warranted.
Some paragraphs should be one sentence. Some should be eight.

---

## Category 4: Voice Patterns

### The Absent Author
AI writes without a subject — no "I", no perspective, no ownership of the view.
In appropriate register, injecting first person ("I think", "in my experience",
"my read on this is") reads as more human. Even in professional contexts,
hedged personal perspective ("tends to work better in my experience") is normal.

### The Explained Audience
AI writes as though the reader knows nothing. For a technical audience, AI
still explains what TCP is, what version control does, what a filesystem is.
Identify the target reader and trim explanations they wouldn't need.

### The Perfect Citation
Humans get things slightly wrong, cite from memory, attribute imprecisely.
AI produces perfectly attributed, perfectly phrased references to concepts.
In informal prose, loosen precise attributions: "somewhere in the TCP spec"
rather than "according to RFC 9293, section 3.4".

### The Emotional Flatline
AI prose has no affect — no mild irritation, no enthusiasm, no dry observation.
A single wry parenthetical or one mildly opinionated aside reads as far more human
than pages of neutral competent prose.
