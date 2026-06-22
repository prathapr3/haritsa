from pathlib import Path
from datetime import datetime
from config import VAULT_PATH


def paper_to_markdown(paper):
    """Convert a paper dict to an Obsidian markdown note."""
    authors_str = ", ".join(paper["authors"][:8])
    if len(paper["authors"]) > 8:
        authors_str += f" (+{len(paper['authors']) - 8} more)"

    topics_tags = " ".join(f"#{t}" for t in paper["topics"])
    date_str = paper["published"].strftime("%Y-%m-%d")

    abstract = paper["abstract"].replace("\n", " ").strip()
    if len(abstract) > 1000:
        abstract = abstract[:1000] + "..."

    md = f"""---
title: "{paper['title']}"
authors: "{authors_str}"
published: {date_str}
score: {paper['score']:.1f}
tags: [paper, {', '.join(paper['topics'])}]
arxiv: {paper['url']}
pdf: {paper['pdf_url']}
---

# {paper['title']}

**Authors:** {authors_str}
**Published:** {date_str}
**Topics:** {topics_tags}
**Score:** {paper['score']:.1f}

[arXiv]({paper['url']}) | [PDF]({paper['pdf_url']})

## Abstract

{abstract}

## Why This Is Relevant

- Categories: {', '.join(paper['categories'])}
- Matched topics: {', '.join(paper['topics'])}
"""
    return md


def write_papers_to_vault(papers, run_label=None):
    """Write ranked papers as individual notes + a digest note."""
    VAULT_PATH.mkdir(parents=True, exist_ok=True)

    if run_label is None:
        run_label = datetime.now().strftime("%Y-%m-%d")

    digest_lines = [
        f"# Research Digest — {run_label}\n",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n",
        f"Papers found: {len(papers)}\n\n",
        "| # | Score | Title | Topics |\n",
        "|---|-------|-------|--------|\n",
    ]

    for i, paper in enumerate(papers, 1):
        safe_title = paper["title"].replace("/", "-").replace(":", " -")[:80]
        filename = f"{paper['id'].replace('/', '_')}.md"
        filepath = VAULT_PATH / filename

        md_content = paper_to_markdown(paper)
        filepath.write_text(md_content)

        topics_str = ", ".join(paper["topics"])
        digest_lines.append(
            f"| {i} | {paper['score']:.1f} | [[{filename[:-3]}\\|{safe_title}]] | {topics_str} |\n"
        )

    digest_path = VAULT_PATH / f"digest-{run_label}.md"
    digest_path.write_text("".join(digest_lines))

    return digest_path
