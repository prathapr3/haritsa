"""
Expands a free-text topic into multiple arxiv search queries.
Uses the raw input + n-gram decomposition for broad coverage.
The expansion map is only used as an optional boost — not a gate.
"""

EXPANSION_MAP = {
    "enterprise agent": [
        "enterprise agent orchestration",
        "enterprise AI agent",
        "agent cloud deployment",
        "agent authentication",
        "agent governance",
    ],
    "agent evaluation": [
        "agent evaluation",
        "evaluating AI agents",
        "agent benchmark",
        "agent reliability",
    ],
    "agentic ai": [
        "agentic AI",
        "autonomous agent",
        "multi-agent system",
        "web agent",
        "tool use LLM",
    ],
    "multi-agent": [
        "multi-agent system",
        "multi-agent orchestration",
        "multi-agent framework",
    ],
    "llm evaluation": [
        "LLM evaluation",
        "LLM-as-judge",
        "automated evaluation",
    ],
    "web agent": [
        "web agent",
        "browser agent",
        "web automation LLM",
        "GUI agent",
    ],
    "agent memory": [
        "agent memory",
        "retrieval augmented agent",
        "episodic memory agent",
    ],
    "agent creation": [
        "agent creation automation",
        "no-code agent",
        "agent development platform",
    ],
    "self-improving": [
        "self-improving agent",
        "agent self-reflection",
        "experiential learning agent",
    ],
    "nlu": [
        "natural language understanding",
        "intent classification",
        "named entity recognition",
    ],
    "rlhf": [
        "RLHF",
        "direct preference optimization",
        "preference learning LLM",
    ],
    "data generation": [
        "synthetic data generation LLM",
        "instruction tuning data",
    ],
    "weak supervision": [
        "weak supervision",
        "programmatic labeling",
    ],
    "rag": [
        "retrieval augmented generation",
        "RAG LLM",
    ],
}

STOPWORDS = {"for", "the", "a", "an", "in", "on", "of", "to", "and", "with", "at", "by", "is", "are", "that", "this"}


def expand_query(user_input):
    """
    Takes any free-text input and returns arxiv search queries.

    Strategy:
    1. Always search the full input as-is
    2. Generate bigrams and trigrams as additional queries
    3. If any part of the input loosely matches the expansion map, add those too (bonus coverage)

    This means ANY input works — the expansion map just adds breadth for known domains.
    """
    input_lower = user_input.lower().strip()
    words = [w for w in input_lower.split() if w not in STOPWORDS and len(w) > 2]
    queries = set()

    # 1. Always include the full raw input
    queries.add(user_input.strip())

    # 2. Generate meaningful n-grams from the input
    # Bigrams
    for i in range(len(words) - 1):
        queries.add(" ".join(words[i:i+2]))
    # Trigrams
    for i in range(len(words) - 2):
        queries.add(" ".join(words[i:i+3]))

    # 3. Bonus: if anything loosely matches expansion map, add those queries
    for key, expansions in EXPANSION_MAP.items():
        key_terms = set(key.split())
        input_terms = set(words)
        # If at least one meaningful word overlaps
        overlap = key_terms.intersection(input_terms)
        # Also check stems (naive plural handling)
        if not overlap:
            key_stems = {w.rstrip("s").rstrip("ing") for w in key_terms}
            input_stems = {w.rstrip("s").rstrip("ing") for w in input_terms}
            overlap = key_stems.intersection(input_stems)
        if overlap:
            queries.update(expansions)

    return list(queries)
