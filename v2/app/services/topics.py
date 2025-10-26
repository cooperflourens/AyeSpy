from typing import List, Dict


class TopicService:
    """Simple topic expansion using a built-in synonym map.

    This is a lightweight baseline; can be replaced with a richer ontology later.
    """

    def __init__(self):
        self._synonyms: Dict[str, List[str]] = {
            "ally": ["allies", "partner", "partners", "allied", "nato", "coalition"],
            "allies": ["ally", "partner", "partners", "allied", "nato", "coalition"],
            "defense": ["defence", "security", "military", "armed forces"],
            "security": ["national security", "defense", "homeland", "counterterrorism"],
            "immigration": ["migrant", "migrants", "border", "asylum", "refugee"],
            "economy": ["economic", "jobs", "inflation", "gdp", "recession"],
            "healthcare": ["health care", "medicare", "medicaid", "insurance", "patient"],
        }

    def expand(self, query: str) -> List[str]:
        q = (query or "").strip().lower()
        if not q:
            return []
        terms = {q}
        for key, syns in self._synonyms.items():
            if q == key or q in syns:
                terms.update(syns)
                terms.add(key)
        # Split query to catch multi-word expansions
        for part in q.split():
            for key, syns in self._synonyms.items():
                if part == key or part in syns:
                    terms.update(syns)
                    terms.add(key)
        return sorted(terms)


