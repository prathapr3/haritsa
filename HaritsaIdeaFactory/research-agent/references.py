"""
Reference chain following via Semantic Scholar API.
Fetches references for top papers and identifies seminal cited works.
"""
import time
import requests

SEMANTIC_SCHOLAR_BASE = "https://api.semanticscholar.org/graph/v1/paper"
FIELDS = "references.title,references.authors,references.year,references.externalIds,references.citationCount"


HEADERS = {
    "User-Agent": "ResearchAgent/1.0 (academic paper fetcher; mailto:research@example.com)"
}


def fetch_references(arxiv_id, max_retries=3):
    """Fetch references for a paper from Semantic Scholar.

    Args:
        arxiv_id: The arxiv paper ID (e.g., '2401.12345' or '2401.12345v1')

    Returns:
        List of reference dicts, or empty list on failure.
    """
    # Strip version suffix (e.g., v1, v2) for Semantic Scholar lookup
    clean_id = arxiv_id.split("v")[0] if "v" in arxiv_id else arxiv_id

    url = f"{SEMANTIC_SCHOLAR_BASE}/arXiv:{clean_id}?fields={FIELDS}"

    for attempt in range(max_retries + 1):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("references", [])
            elif resp.status_code == 429:
                # Rate limited — exponential back off
                wait = 5 * (2 ** attempt)
                print(f"    [Semantic Scholar] Rate limited, waiting {wait}s...")
                time.sleep(wait)
                continue
            elif resp.status_code == 404:
                # Paper not found in Semantic Scholar
                return []
            else:
                return []
        except (requests.RequestException, ValueError):
            if attempt < max_retries:
                time.sleep(2)
                continue
            return []

    return []


def get_seminal_references(arxiv_id, top_k=3):
    """Get the top-K most cited references for a paper.

    Returns:
        List of dicts with keys: title, authors, year, citation_count, arxiv_url
    """
    refs = fetch_references(arxiv_id)
    if not refs:
        return []

    # Filter out references with missing data
    valid_refs = []
    for ref in refs:
        cited_paper = ref.get("citedPaper", ref)
        if not cited_paper:
            continue
        title = cited_paper.get("title")
        citation_count = cited_paper.get("citationCount")
        if title and citation_count is not None:
            authors = cited_paper.get("authors", [])
            author_names = [a.get("name", "") for a in authors[:5]] if authors else []
            year = cited_paper.get("year")
            external_ids = cited_paper.get("externalIds", {}) or {}
            arxiv_ext_id = external_ids.get("ArXiv")
            arxiv_url = f"https://arxiv.org/abs/{arxiv_ext_id}" if arxiv_ext_id else None

            valid_refs.append({
                "title": title,
                "authors": author_names,
                "year": year,
                "citation_count": citation_count,
                "arxiv_url": arxiv_url,
            })

    # Sort by citation count, return top K
    valid_refs.sort(key=lambda r: r["citation_count"], reverse=True)
    return valid_refs[:top_k]


def enrich_papers_with_references(papers, top_k_refs=3):
    """Add seminal references to each paper in the list.

    Adds a 'seminal_references' key to each paper dict.
    Respects rate limits with a sleep between requests.
    """
    print("  Fetching reference chains from Semantic Scholar...")
    for i, paper in enumerate(papers):
        arxiv_id = paper["id"]
        refs = get_seminal_references(arxiv_id, top_k=top_k_refs)
        paper["seminal_references"] = refs
        if refs:
            print(f"    {paper['title'][:60]}... -> {len(refs)} seminal refs")
        else:
            print(f"    {paper['title'][:60]}... -> no refs found")

        # Sleep between requests to respect rate limits (free tier: ~100 req/5 min)
        if i < len(papers) - 1:
            time.sleep(3.0)

    return papers
