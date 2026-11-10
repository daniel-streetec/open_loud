"""Strict source-driven assembly mapping and recursive leaf traversal."""
import re
def classify(name,structure):
    matches=[r['path'] for r in structure['rules'] if re.fullmatch(r['pattern'],name)]
    if len(matches)!=1:raise ValueError(f'{name}: expected exactly one assembly rule, got {matches}')
    return matches[0]
def leaf_occurrences(root):
    return [o for o in root.allOccurrences if o.component.bRepBodies.count]
