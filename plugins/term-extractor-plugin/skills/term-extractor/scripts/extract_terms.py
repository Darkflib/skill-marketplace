#!/usr/bin/env python3
"""
Term Extraction Script

Extracts technical terms, acronyms, and domain-specific vocabulary from text
and outputs them in YAML format for glossary/index generation.
"""

import re
import sys
from collections import defaultdict
from typing import Dict, List, Set
import yaml


class TermExtractor:
    """Extract and categorize terms from text."""
    
    def __init__(self):
        # Patterns for different term types
        self.acronym_pattern = re.compile(r'\b[A-Z]{2,}s?\b')
        self.capitalized_pattern = re.compile(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b')
        self.technical_indicators = {
            'protocol', 'algorithm', 'architecture', 'pattern', 'system',
            'service', 'platform', 'framework', 'library', 'tool',
            'method', 'function', 'class', 'interface', 'api'
        }
        
    def extract_acronyms(self, text: str) -> Set[str]:
        """Extract acronyms (2+ consecutive uppercase letters)."""
        return set(self.acronym_pattern.findall(text))
    
    def extract_capitalized_phrases(self, text: str) -> Set[str]:
        """Extract capitalized multi-word phrases (likely proper nouns)."""
        matches = self.capitalized_pattern.findall(text)
        # Filter out sentence starters (first word after period)
        filtered = []
        sentences = text.split('. ')
        sentence_starters = {s.split()[0] for s in sentences if s.split()}
        
        for match in matches:
            first_word = match.split()[0]
            if len(match.split()) > 1 or first_word not in sentence_starters:
                filtered.append(match)
        
        return set(filtered)
    
    def extract_technical_terms(self, text: str) -> Set[str]:
        """Extract technical terms with context indicators."""
        terms = set()
        words = text.lower().split()
        
        for i, word in enumerate(words):
            # Check for technical indicators
            if word in self.technical_indicators:
                # Look ahead for term
                if i + 1 < len(words):
                    next_word = words[i + 1].strip('.,;:!?')
                    if len(next_word) > 3:  # Minimum length
                        terms.add(next_word)
        
        return terms
    
    def categorize_term(self, term: str) -> str:
        """Determine term category."""
        if term.isupper() and len(term) >= 2:
            return 'acronym'
        elif term[0].isupper() and ' ' in term:
            return 'proper_noun'
        elif term[0].isupper():
            return 'name'
        else:
            return 'technical'
    
    def extract_from_text(self, text: str) -> Dict[str, List[Dict]]:
        """Extract all terms from text and return structured data."""
        terms_data = defaultdict(list)
        
        # Extract different types of terms
        acronyms = self.extract_acronyms(text)
        capitalized = self.extract_capitalized_phrases(text)
        technical = self.extract_technical_terms(text)
        
        # Combine and structure
        all_terms = acronyms | capitalized | technical
        
        for term in sorted(all_terms):
            category = self.categorize_term(term)
            term_entry = {
                'term': term,
                'category': category,
                'definition': '',  # To be filled in manually
                'variations': [],
                'references': []
            }
            terms_data['terms'].append(term_entry)
        
        return dict(terms_data)


def merge_with_existing(new_terms: Dict, existing_yaml: str = None) -> Dict:
    """Merge new terms with existing YAML content."""
    if not existing_yaml:
        return new_terms
    
    try:
        existing = yaml.safe_load(existing_yaml)
        if not existing or 'terms' not in existing:
            return new_terms
        
        # Create lookup of existing terms
        existing_terms = {t['term']: t for t in existing['terms']}
        
        # Merge: keep existing entries, add new ones
        for new_term in new_terms['terms']:
            term_name = new_term['term']
            if term_name not in existing_terms:
                existing['terms'].append(new_term)
        
        return existing
    except Exception as e:
        print(f"Warning: Could not parse existing YAML: {e}", file=sys.stderr)
        return new_terms


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: extract_terms.py <input_file> [existing_yaml_file]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    existing_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Read input text
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found", file=sys.stderr)
        sys.exit(1)
    
    # Extract terms
    extractor = TermExtractor()
    terms_data = extractor.extract_from_text(text)
    
    # Merge with existing if provided
    if existing_file:
        try:
            with open(existing_file, 'r', encoding='utf-8') as f:
                existing_yaml = f.read()
            terms_data = merge_with_existing(terms_data, existing_yaml)
        except FileNotFoundError:
            print(f"Warning: Existing file '{existing_file}' not found, creating new", 
                  file=sys.stderr)
    
    # Output YAML
    yaml_output = yaml.dump(terms_data, 
                           default_flow_style=False,
                           sort_keys=False,
                           allow_unicode=True)
    print(yaml_output)


if __name__ == '__main__':
    main()
