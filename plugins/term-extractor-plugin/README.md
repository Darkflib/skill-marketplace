# Term Extractor - Usage Guide

Extracts technical terms, acronyms, proper nouns, and domain-specific vocabulary from text and maintains them in structured YAML format.

## Use Cases

- **Book writing**: Extract terms from each chapter, build comprehensive index
- **Documentation**: Maintain glossary of technical terms across docs
- **Standards**: Document domain vocabulary for team alignment
- **Learning**: Build personal knowledge base of concepts and terminology

## Workflow

1. **Extract**: Run the extraction script on your text
2. **Review**: Remove false positives and validate categorization
3. **Enrich**: Add definitions, variations, and page references
4. **Merge**: Combine with existing term databases without duplicates
5. **Process**: Use the YAML for downstream glossary/index generation

## Quick Usage

Once installed, you can ask Claude things like:

- "Extract terms from this chapter and add them to my glossary YAML"
- "Help me build a glossary from this documentation"
- "Identify all the technical terms in this text"
- "Update my terms.yaml file with new terms from this article"

## YAML Format

```yaml
terms:
  - term: "Kubernetes"
    category: name
    definition: "Open-source container orchestration platform"
    variations: ["K8s", "k8s"]
    references: ["Chapter 3", "p. 45-52"]
```

## Categories

| Category | Description | Examples |
|----------|-------------|----------|
| `acronym` | Uppercase abbreviations | SRE, API, HTTP |
| `proper_noun` | Multi-word names | Site Reliability Engineering |
| `name` | Single-word names | Kubernetes, Python |
| `technical` | Domain vocabulary | observability, idempotency |
| `concept` | Abstract terms | eventual consistency |

## CLI Usage

```bash
# Extract terms from a file
python3 scripts/extract_terms.py input.txt > terms.yaml

# Merge with existing terms
python3 scripts/extract_terms.py new_chapter.txt existing_terms.yaml > updated_terms.yaml
```

## Tips

- The script extracts candidates; manual review improves quality
- Run on chapter/section boundaries for better reference tracking
- Add variations users might search for
- Keep definitions concise (one sentence usually suffices)
