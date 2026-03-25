# Term YAML Schema Reference

## Structure

Terms are stored in a YAML document with the following structure:

```yaml
terms:
  - term: string          # The term itself
    category: string      # Category: acronym, proper_noun, name, technical, concept
    definition: string    # Definition or explanation (can be empty initially)
    variations: list      # Alternative forms, abbreviations, etc.
    references: list      # Page numbers, section references, or citations
    context: string       # Optional: context where term is used
```

## Categories

- **acronym**: Uppercase abbreviations (e.g., SRE, API, HTTP)
- **proper_noun**: Multi-word capitalized phrases (e.g., "Site Reliability Engineering")
- **name**: Single capitalized words that are names (e.g., Kubernetes, Python)
- **technical**: Domain-specific technical vocabulary
- **concept**: Abstract or theoretical terms

## Example YAML

```yaml
terms:
  - term: Kubernetes
    category: name
    definition: Open-source container orchestration platform
    variations:
      - K8s
      - k8s
    references:
      - "Chapter 3"
      - "p. 45-52"
    context: cloud infrastructure

  - term: SRE
    category: acronym
    definition: Site Reliability Engineering - discipline incorporating software engineering to operations
    variations:
      - Site Reliability Engineering
    references:
      - "Introduction"
      - "p. 12"

  - term: Circuit Breaker Pattern
    category: concept
    definition: Design pattern that prevents cascading failures in distributed systems
    variations:
      - circuit breaker
      - Circuit Breaker
    references:
      - "Chapter 7, p. 134"

  - term: observability
    category: technical
    definition: Ability to understand system internal state from external outputs
    variations:
      - observable
    references: []
```

## Workflow

1. **Extract**: Use `extract_terms.py` to automatically extract candidate terms
2. **Review**: Manually review extracted terms, remove false positives
3. **Enrich**: Add definitions, variations, and references
4. **Merge**: Update existing YAML file with new terms
5. **Process**: Use the YAML as input for glossary/index generation

## Notes

- The script extracts candidate terms; manual review is always recommended
- Terms can be added manually if the automated extraction misses them
- Keep variations in a consistent order (most formal to most casual)
- References should be specific enough to locate the term's usage
- Empty definitions can be filled in during editing passes
