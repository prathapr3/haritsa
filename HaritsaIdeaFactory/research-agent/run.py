#!/usr/bin/env python3
"""
Research Agent — pulls top papers from arxiv in your domains.

Usage:
    python run.py                                # All predefined topics, top 10
    python run.py "enterprise agents"            # Free-text topic (semantic expansion)
    python run.py "agent evaluation"             # Another example
    python run.py "self-improving web agents"    # Combines multiple expansions
    python run.py --days 14                      # Last 14 days
    python run.py --top 5                        # Top 5 only
    python run.py --list                         # Show available topic suggestions
    python run.py --network                      # Show top 20 most-seen authors
"""
import argparse
import time
import arxiv
from datetime import datetime, timedelta

from config import TOPICS, MAX_RESULTS_PER_QUERY, TOP_N
from fetcher import score_paper
from query_expander import expand_query, EXPANSION_MAP
from writer import write_papers_to_vault
from references import enrich_papers_with_references
from network import update_network, print_top_authors


def fetch_free_text(query_text, days_back=7):
    """Fetch papers using semantically expanded queries from free text."""
    cutoff = datetime.now().astimezone() - timedelta(days=days_back)
    all_papers = {}
    queries = expand_query(query_text)

    print(f"  Expanded '{query_text}' into {len(queries)} search queries")

    client = arxiv.Client(page_size=MAX_RESULTS_PER_QUERY, delay_seconds=4, num_retries=5)

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
                    "topics": [query_text],
                }

    return list(all_papers.values())


def main():
    parser = argparse.ArgumentParser(
        description="Fetch and rank recent arxiv papers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py "enterprise agents"
  python run.py "agent evaluation" --days 14
  python run.py "self-improving web agents" --top 20
  python run.py --list
  python run.py                          # All predefined topics
""",
    )
    parser.add_argument("query", nargs="?", default=None, help="Free-text topic to search (e.g., 'enterprise agents')")
    parser.add_argument("--days", type=int, default=7, help="How many days back to search")
    parser.add_argument("--top", type=int, default=TOP_N, help="Number of top papers to output")
    parser.add_argument("--network", action="store_true", help="Show top 20 most frequently seen authors")
    parser.add_argument("--list", action="store_true", help="List available topic suggestions")
    args = parser.parse_args()

    if args.network:
        print_top_authors(top_n=20)
        return

    if args.list:
        print("Available topic suggestions (use any as free text):\n")
        for key in sorted(EXPANSION_MAP.keys()):
            print(f"  • {key}")
        print(f"\n  ...or type anything — the tool will expand it semantically.")
        print(f"\nPredefined broad topics (used when no query given):")
        for key in sorted(TOPICS.keys()):
            print(f"  • {key}")
        return

    print(f"Fetching papers from last {args.days} days...")

    if args.query:
        papers = fetch_free_text(args.query, days_back=args.days)
    else:
        from fetcher import fetch_papers
        papers = fetch_papers(days_back=args.days)

    print(f"  Found {len(papers)} papers")

    # Score and rank
    for paper in papers:
        paper["score"] = score_paper(paper)
    papers.sort(key=lambda p: (-p["score"], -p["published"].timestamp()))
    ranked = papers[: args.top]

    print(f"  Ranked top {len(ranked)} papers\n")

    for i, p in enumerate(ranked, 1):
        print(f"  {i:2}. [{p['score']:.1f}] {p['title'][:80]}")
        print(f"      {', '.join(p['topics'])} | {p['published'].strftime('%Y-%m-%d')}")

    # Enrich with reference chains from Semantic Scholar
    print()
    ranked = enrich_papers_with_references(ranked, top_k_refs=3)

    # Update author network
    update_network(ranked)

    digest_path = write_papers_to_vault(ranked)
    print(f"\nDigest written to: {digest_path}")
    print(f"Individual notes in: {digest_path.parent}/")


if __name__ == "__main__":
    main()
