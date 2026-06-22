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
        "enterprise agent orchestration",
        "agent authentication",
        "agent cloud deployment",
    ],
    "agent-evaluation": [
        "agent evaluation",
        "evaluating AI agents",
        "agent benchmark",
        "agent reliability",
        "multi-agent evaluation",
        "agent testing",
        "agent failure analysis",
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

# Keywords related to the user's own work — papers matching these get a relevance boost
USER_WORK_KEYWORDS = [
    "multi-agent purchase",
    "multi-agent purchasing",
    "agent evaluation",
    "self-improving agent",
    "retrieval augmented planning",
    "web agent",
    "agent memory",
    "weak supervision",
    "evaluation at scale",
    "defect detection",
    "SFT",
    "supervised fine-tuning",
    "demonstration data",
    "preference optimization",
    "adaptive test",
    "perturbation testing",
    "robustness testing",
    "NER",
    "named entity recognition",
    "agent creation",
    "agent automation",
    "self-improving",
    "memory retrieval",
    "data generation",
    "LLM evaluation",
    "automated evaluation",
    "agent reliability",
    "agent failure",
    "enterprise agent",
    "agent auth",
    "cloud agent",
    "agent creation",
    "agent benchmark",
]
