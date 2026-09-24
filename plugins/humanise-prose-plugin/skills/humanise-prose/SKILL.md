---
name: humanise-prose
description: >
  Remove AI writing tells from prose and make it read as naturally human-authored.
  Use this skill whenever the user asks to: "humanise this", "de-AI this text",
  "make this sound less like ChatGPT/Claude/AI", "remove AI tells", "make this
  sound more natural/human", "add some typos", "this reads too polished",
  "clean up AI writing", or any variant of wanting prose to pass as human-written.
  Also trigger when the user asks to improve the voice or naturalness of a draft
  they've described as AI-generated or AI-assisted.
---

# Humanise Prose

Transforms AI-generated or AI-assisted text to remove detectable tells and
produce prose that reads as naturally human-authored. Configurable by intensity,
register, and typo density.

---

## Parameters

Establish these before transforming. Infer from context if obvious; ask if not.

| Parameter | Options | Default |
|-----------|---------|---------|
| **Intensity** | `light` · `medium` · `heavy` | `medium` |
| **Register** | `casual` · `professional` · `academic` | infer from text |
| **Typos** | `none` · `subtle` · `moderate` | `subtle` |
| **Persona hint** | Optional free-text description of a voice to aim for | none |

- `light`: Remove lexical tells and obvious hedging only. Minimal restructuring.
- `medium`: Lexical + structural. Vary sentence rhythm. Flatten excessive parallelism.
- `heavy`: Full rewrite pass. Inject perspective, elision, and assumed context.
- `subtle` typos: 1–2 per ~300 words.
- `moderate` typos: ~1 per paragraph.

---

## Transformation Pipeline

Execute passes in order. Later passes depend on earlier ones.

### Pass 1 — Lexical Scrub

Replace or delete AI-signature vocabulary. See `references/ai-tells-taxonomy.md`
for the full list, but key targets:

**Filler intensifiers** (delete or replace with concrete language):
- crucial / essential / vital / key → use specific language or cut entirely
- robust / seamless / holistic / comprehensive → cut or replace with specific adjective
- innovative / cutting-edge / game-changer / paradigm shift → usually just cut

**Filler transitions** (cut or replace with natural connectives):
- Furthermore / Moreover / Additionally → start new sentence or use "also", "and"
- In conclusion / To summarise / In summary → cut entirely — end the point, don't restate it
- It's worth noting that / It's important to note → cut the preamble, state the fact

**AI vocabulary flags** (high-signal tells):
- "delve" / "delve into" → look at, dig into, examine
- "tapestry" (metaphorically) → cut or find specific alternative
- "nuanced" (as filler) → specify the nuance or cut
- "leverage" (as verb) → use
- "I cannot stress enough" → cut

**Hedging stacks** (trim to single hedge at most):
- "may potentially", "could possibly", "might perhaps" → pick one or cut the hedge

### Pass 2 — Structural Flatten

Targets structural patterns that betray generation rather than composition.

**The restatement sandwich**: If the intro paragraph and conclusion paragraph
say essentially the same thing, cut or substantially rewrite one of them.
Humans end when they've made the point.

**Exhaustive enumeration**: AI lists every case. Humans pick the important ones
and gesture at the rest ("among other things", "and so on"). Cut repeated or
filler items, not a fixed percentage. Where the list is requirements,
instructions or anything else the reader must act on, keep every item that
carries distinct information.

**Bullet point collapse**: If bullet points could be a sentence or short
paragraph without losing clarity, collapse them. Reserve bullets for genuinely
list-shaped content.

**Excessive parallelism**: "X does A, Y does B, and Z does C" — fine once.
Three times in a row: break the pattern. Vary sentence shape.

**Topic sentence rigidity**: Not every paragraph needs to open with its
thesis statement. Start one or two with the second thought or a bridging
observation instead.

### Pass 3 — Rhythm and Voice

**Sentence length variation**: Check if sentence lengths are suspiciously
uniform. Deliberately vary — short punch after long build, long trailing
clause after short declarative. Read a paragraph aloud mentally; if the
cadence is metronomic, break it.

**Elision and contraction**: At `casual` and `professional` register, use
contractions. Humans write "it's", "don't", "can't". AI-generated prose
often avoids them. Academic register: contractions less common, but still
not zero.

**Assumed context**: AI explains everything. Humans assume shared knowledge
with their audience. For the target register, trim any explanation that the
intended reader would already know. Replace with a brief reference rather
than a definition.

**Opinions and takes**: For `medium` and `heavy` intensity, where the draft
hedges but already leans one way, commit to that lean. Humans usually have a
view. Don't invent one the draft doesn't support: if it is genuinely balanced,
keep the balance or ask the user which position they hold.

**Self-interruption**: Occasional parenthetical, dash-aside, or trailing
qualifier reads as natural thought. AI produces clean complete sentences.
Add one or two per page where natural.

### Pass 4 — Typo Injection (skip if `none`)

**Read `references/typo-patterns.md` for the full catalogue.**

Core rules:
1. **Never in technical terms, proper nouns, or code.** A typo in "Kubernetes"
   reads as ignorance, not speed.
2. **Never in the first or last sentence of the piece** — readers notice more.
3. **Never two typos in the same sentence.**
4. **Prefer high-frequency words** — typos in common words (the, and, that,
   with, have) look like speed errors. Typos in rare words look like ignorance.
5. **Transpositions and missing apostrophes are safest** — universally
   recognisable as typing errors.
6. **Distribute across the text**, not clustered.
7. **`subtle` density**: 1 typo per ~300 words, maximum 3 in any piece.
8. **`moderate` density**: 1 typo per ~150 words, roughly one per paragraph.

---

## Output Format

- Return the transformed text in full.
- At `medium` / `heavy` intensity, include a brief **Change Log** after the
  text (collapsible if the interface supports it) noting:
  - AI tells removed
  - Structural changes made
  - Typos injected (location + type) — so the user can audit them
- At `light` intensity, change log is optional unless the user asks.

---

## Reference Files

- `references/ai-tells-taxonomy.md` — Full vocabulary and pattern list with examples
- `references/typo-patterns.md` — Typo catalogue with examples and frequency notes

Read these when working on a substantial transformation or when you need
to make a judgment call about whether something is an AI tell.
