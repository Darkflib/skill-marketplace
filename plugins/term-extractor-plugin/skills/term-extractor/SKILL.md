---
name: term-extractor
description: Extract technical terms, acronyms, proper nouns, and domain vocabulary from text and maintain them in structured YAML format for glossary and index generation. Use when the user needs to identify important terms from documentation, books, articles, or technical content, or when building/updating glossaries, indexes, or term databases.
---

# Term Extractor

Extract and manage terminology from text in YAML format for downstream processing into glossaries and indexes.

## Quick Start

Extract terms from a text file:

```bash
python3 scripts/extract_terms.py input.txt > terms.yaml
```

Merge with existing YAML:

```bash
python3 scripts/extract_terms.py input.txt existing_terms.yaml > updated_terms.yaml
```

## Extraction Process

The script automatically identifies:

- **Acronyms**: Uppercase 2+ letter abbreviations (SRE, API, CI/CD)
- **Proper nouns**: Capitalized multi-word phrases (Site Reliability Engineering)
- **Names**: Single capitalized terms (Kubernetes, Python)
- **Technical terms**: Domain vocabulary with context indicators

## Manual Review Required

Automated extraction produces candidates that need human review:

1. **False positives**: Remove sentence starters, common words, irrelevant terms
2. **Missing terms**: Add domain-specific vocabulary the script missed
3. **Definitions**: Fill in the `definition` field for each term
4. **Variations**: Add alternative spellings, abbreviations, case variants
5. **References**: Add page numbers, section references, or citations

## YAML Structure

See `references/schema.md` for complete schema documentation and examples.

Basic structure:

```yaml
terms:
  - term: "Term Name"
    category: acronym | proper_noun | name | technical | concept
    definition: "Brief definition or explanation"
    variations: ["alt1", "alt2"]
    references: ["Chapter 3", "p. 45"]
    context: "optional contextual note"
```

## Workflow

1. **Extract**: Run script on source text to generate candidate terms
2. **Review**: Remove false positives, validate categories
3. **Enrich**: Add definitions, variations, and reference locations
4. **Merge**: Combine with existing term database
5. **Process**: Use YAML as input for glossary/index generation tools

## Categories

- `acronym`: Uppercase abbreviations (HTTP, JSON)
- `proper_noun`: Multi-word names (Amazon Web Services)
- `name`: Single-word names (Docker, Redis)
- `technical`: Domain-specific vocabulary (idempotency, telemetry)
- `concept`: Abstract/theoretical terms (eventual consistency)

## Tips

- Run extraction on chapter/section boundaries for better reference tracking
- Review acronyms carefully - many are context-dependent
- Consider variations users might search for (singular/plural, with/without hyphens)
- Keep definitions concise - one sentence is usually sufficient
- Group related terms in the same file for logical organization

## Schema Reference

For detailed YAML schema, examples, and field descriptions, see `references/schema.md`.
