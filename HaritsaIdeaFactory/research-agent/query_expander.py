"""
Expands a free-text topic into multiple arxiv search queries via semantic expansion.
No LLM needed — uses a curated synonym/expansion map + the raw input itself.
"""

EXPANSION_MAP = {
    "enterprise agent": [
        "enterprise agent orchestration",
        "enterprise AI agent",
        "agent cloud deployment",
        "agent authentication",
        "multi-agent enterprise",
        "agent governance",
        "agent runtime security",
    ],
    "agent evaluation": [
        "agent evaluation",
        "evaluating AI agents",
        "agent benchmark",
        "agent reliability",
        "multi-agent evaluation",
        "agent testing framework",
        "agent failure analysis",
    ],
    "agentic ai": [
        "agentic AI",
        "autonomous agent",
        "multi-agent system",
        "web agent",
        "tool use LLM",
        "agent planning",
        "agent memory",
    ],
    "multi-agent": [
        "multi-agent system",
        "multi-agent orchestration",
        "multi-agent collaboration",
        "multi-agent framework",
        "agent coordination",
    ],
    "llm evaluation": [
        "LLM evaluation",
        "LLM-as-judge",
        "automated evaluation",
        "benchmark LLM",
        "red teaming LLM",
    ],
    "web agent": [
        "web agent",
        "browser agent",
        "web automation LLM",
        "GUI agent",
        "web navigation agent",
    ],
    "agent memory": [
        "agent memory",
        "agent long-term memory",
        "retrieval augmented agent",
        "episodic memory agent",
        "agent experience learning",
    ],
    "agent creation": [
        "agent creation automation",
        "automated agent building",
        "no-code agent",
        "agent development platform",
        "agent builder",
    ],
    "self-improving": [
        "self-improving agent",
        "agent self-reflection",
        "agent learning from experience",
        "experiential learning agent",
        "agent self-correction",
    ],
    "nlu": [
        "natural language understanding",
        "intent classification",
        "named entity recognition",
        "dialogue systems",
        "task-oriented dialogue",
    ],
    "rlhf": [
        "RLHF",
        "reinforcement learning human feedback",
        "direct preference optimization",
        "preference learning LLM",
        "reward model",
    ],
    "data generation": [
        "synthetic data generation",
        "SFT data",
        "instruction tuning data",
        "demonstration data LLM",
        "data augmentation LLM",
    ],
    "weak supervision": [
        "weak supervision",
        "programmatic labeling",
        "label function",
        "noisy labels",
        "semi-supervised learning",
    ],
    "rag": [
        "retrieval augmented generation",
        "RAG",
        "knowledge retrieval LLM",
        "grounded generation",
    ],
}


def expand_query(user_input):
    """
    Takes free-text input and returns a list of arxiv search queries.
    Matches against known expansions, and always includes the raw input itself.
    """
    input_lower = user_input.lower().strip()
    queries = set()

    # Always include the raw input as a query
    queries.add(user_input.strip())

    # Match against expansion map — partial matching
    for key, expansions in EXPANSION_MAP.items():
        if key in input_lower or input_lower in key:
            queries.update(expansions)

    # Also try individual words for broader matching
    words = input_lower.split()
    for key, expansions in EXPANSION_MAP.items():
        key_words = set(key.split())
        if len(key_words.intersection(words)) > 0 and len(words) > 1:
            # At least one word overlap and input has multiple words — partial match
            if len(key_words.intersection(words)) / len(key_words) >= 0.5:
                queries.update(expansions)

    return list(queries)
