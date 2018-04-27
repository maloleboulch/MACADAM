from typing import Dict


def lineages_by_taxonomy_id(taxonomies) -> Dict[int, str]:
    dict = {}
    for t in taxonomies:
        dict[t.id] = t.taxonomy
    return dict
