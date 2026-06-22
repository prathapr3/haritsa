#!/usr/bin/env python3
"""
Research Agent — pulls top papers from arxiv in your domains.

Usage:
    python run.py                     # Last 7 days, all topics, top 10
    python run.py --days 14           # Last 14 days
    python run.py --topics agentic-ai llm-evaluation  # Specific topics
    python run.py --top 5             # Top 5 only
"""
import argparse
from fetcher import fetch_papers, rank_papers
from writer import write_papers_to_vault
from config import TOPICS, TOP_N


def main():
    parser = argparse.ArgumentParser(description="Fetch and rank recent arxiv papers")
    parser.add_argument("--days", type=int, default=7, help="How many days back to search")
    parser.add_argument("--topics", nargs="+", choices=list(TOPICS.keys()), help="Filter to specific topics")
    parser.add_argument("--top", type=int, default=TOP_N, help="Number of top papers to output")
    args = parser.parse_args()

    print(f"Fetching papers from last {args.days} days...")
    topics = args.topics if args.topics else None
    papers = fetch_papers(days_back=args.days, topic_filter=topics)
    print(f"  Found {len(papers)} papers across {len(topics or TOPICS)} topic areas")

    ranked = rank_papers(papers, top_n=args.top)
    print(f"  Ranked top {len(ranked)} papers\n")

    for i, p in enumerate(ranked, 1):
        print(f"  {i:2}. [{p['score']:.1f}] {p['title'][:80]}")
        print(f"      {', '.join(p['topics'])} | {p['published'].strftime('%Y-%m-%d')}")

    digest_path = write_papers_to_vault(ranked)
    print(f"\nDigest written to: {digest_path}")
    print(f"Individual notes in: {digest_path.parent}/")


if __name__ == "__main__":
    main()
