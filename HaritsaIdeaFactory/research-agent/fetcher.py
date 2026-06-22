import time
import arxiv
from datetime import datetime, timedelta
from config import TOPICS, MAX_RESULTS_PER_QUERY, ELITE_AUTHORS, ELITE_INSTITUTIONS, USER_WORK_KEYWORDS


def fetch_papers(days_back=7, topic_filter=None):
    """Fetch recent papers from arxiv across configured topics."""
    cutoff = datetime.now().astimezone() - timedelta(days=days_back)
    all_papers = {}

    topics = TOPICS if topic_filter is None else {k: v for k, v in TOPICS.items() if k in topic_filter}

    client = arxiv.Client(page_size=MAX_RESULTS_PER_QUERY, delay_seconds=4, num_retries=5)

    for topic, queries in topics.items():
        for query_str in queries:
            search = arxiv.Search(
                query=f'all:"{query_str}"',
                max_results=MAX_RESULTS_PER_QUERY,
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending,
            )
            try:
                results = list(client.results(search))
            except Exception:
                time.sleep(10)
                continue
            for result in results:
                if result.published.replace(tzinfo=None) < cutoff.replace(tzinfo=None):
                    continue
                paper_id = result.entry_id.split("/")[-1]
                if paper_id not in all_papers:
                    all_papers[paper_id] = {
                        "id": paper_id,
                        "title": result.title,
                        "authors": [a.name for a in result.authors],
                        "abstract": result.summary,
                        "published": result.published,
                        "url": result.entry_id,
                        "pdf_url": result.pdf_url,
                        "categories": result.categories,
                        "topics": [topic],
                    }
                else:
                    if topic not in all_papers[paper_id]["topics"]:
                        all_papers[paper_id]["topics"].append(topic)

    return list(all_papers.values())


def score_paper(paper):
    """Score a paper based on heuristics: elite authors, institutions, topic breadth."""
    score = 0.0

    for author in paper["authors"]:
        if any(elite.lower() in author.lower() for elite in ELITE_AUTHORS):
            score += 3.0
            break

    affiliations = " ".join(paper["authors"]) + " " + paper["abstract"]
    for inst in ELITE_INSTITUTIONS:
        if inst.lower() in affiliations.lower():
            score += 1.5
            break

    score += len(paper["topics"]) * 2.0

    abstract_lower = paper["abstract"].lower()
    production_signals = ["production", "deployed", "real-world", "at scale", "industry"]
    for signal in production_signals:
        if signal in abstract_lower:
            score += 1.0

    if len(paper["authors"]) <= 6:
        score += 0.5

    # Relevance boost: papers matching user's own research interests
    relevance_hits = 0
    for keyword in USER_WORK_KEYWORDS:
        if keyword.lower() in abstract_lower:
            relevance_hits += 1
    if relevance_hits >= 3:
        score += 3.0
    elif relevance_hits >= 2:
        score += 2.0
    elif relevance_hits >= 1:
        score += 1.0

    return score


def rank_papers(papers, top_n=10):
    """Score and rank papers, return top N."""
    for paper in papers:
        paper["score"] = score_paper(paper)
    papers.sort(key=lambda p: (-p["score"], -p["published"].timestamp()))
    return papers[:top_n]
