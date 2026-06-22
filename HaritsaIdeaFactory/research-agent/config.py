from pathlib import Path

VAULT_PATH = Path.home() / "obsidian-vaults" / "career-depth" / "research"

TOPICS = {
    "agentic-ai": [
        "multi-agent system",
        "autonomous agent",
        "agentic AI",
        "web agent",
        "tool use LLM",
        "agent planning",
        "agent memory",
    ],
    "llm-evaluation": [
        "LLM evaluation",
        "LLM-as-judge",
        "automated evaluation",
        "benchmark LLM",
        "red teaming LLM",
        "evaluation metric language model",
    ],
    "nlu": [
        "natural language understanding",
        "intent classification",
        "named entity recognition",
        "dialogue systems",
        "task-oriented dialogue",
    ],
    "llm": [
        "large language model",
        "instruction tuning",
        "RLHF",
        "direct preference optimization",
        "retrieval augmented generation",
        "chain of thought",
    ],
}

ELITE_AUTHORS = [
    "Yann LeCun",
    "Yoshua Bengio",
    "Jason Wei",
    "Denny Zhou",
    "Shunyu Yao",
    "Graham Neubig",
    "Noah Smith",
    "Percy Liang",
    "Diyi Yang",
    "Tatsunori Hashimoto",
    "Sewon Min",
    "Ofir Press",
    "Danqi Chen",
    "Karthik Narasimhan",
]

ELITE_INSTITUTIONS = [
    "Stanford",
    "MIT",
    "CMU",
    "Berkeley",
    "Princeton",
    "Google DeepMind",
    "OpenAI",
    "Anthropic",
    "Meta AI",
    "Microsoft Research",
    "Allen Institute",
]

MAX_RESULTS_PER_QUERY = 20
TOP_N = 10
