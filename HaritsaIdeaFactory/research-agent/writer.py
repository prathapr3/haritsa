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

    # Add seminal references section if available
    seminal_refs = paper.get("seminal_references", [])
    if seminal_refs:
        md += "\n## Seminal Referenced Papers\n\n"
        for ref in seminal_refs:
            ref_authors = ", ".join(ref["authors"][:3]) if ref["authors"] else "Unknown"
            year_str = f" ({ref['year']})" if ref.get("year") else ""
            cite_str = f" — {ref['citation_count']:,} citations" if ref.get("citation_count") else ""
            if ref.get("arxiv_url"):
                md += f"- **[{ref['title']}]({ref['arxiv_url']})**{year_str}{cite_str}\n"
                md += f"  - {ref_authors}\n"
            else:
                md += f"- **{ref['title']}**{year_str}{cite_str}\n"
                md += f"  - {ref_authors}\n"

    return md


def write_papers_to_vault(papers, run_label=None):
    """Write ranked papers as individual notes + append to digest if same day."""
    VAULT_PATH.mkdir(parents=True, exist_ok=True)

    if run_label is None:
        run_label = datetime.now().strftime("%Y-%m-%d")

    digest_path = VAULT_PATH / f"digest-{run_label}.md"
    run_time = datetime.now().strftime("%H:%M")

    # If digest already exists for today, append a new section
    if digest_path.exists():
        existing = digest_path.read_text()
        digest_lines = [
            existing.rstrip() + "\n\n",
            f"---\n\n",
            f"## Run at {run_time}\n\n",
            f"Papers found: {len(papers)}\n\n",
            "| # | Score | Title | Topics |\n",
            "|---|-------|-------|--------|\n",
        ]
    else:
        digest_lines = [
            f"# Research Digest — {run_label}\n\n",
            f"## Run at {run_time}\n\n",
            f"Papers found: {len(papers)}\n\n",
            "| # | Score | Title | Topics |\n",
            "|---|-------|-------|--------|\n",
        ]

    for i, paper in enumerate(papers, 1):
        safe_title = paper["title"].replace("/", "-").replace(":", " -")[:80]
        filename = f"{paper['id'].replace('/', '_')}.md"
        filepath = VAULT_PATH / filename

        if not filepath.exists():
            md_content = paper_to_markdown(paper)
            filepath.write_text(md_content)

        topics_str = ", ".join(paper["topics"])
        digest_lines.append(
            f"| {i} | {paper['score']:.1f} | [[{filename[:-3]}\\|{safe_title}]] | {topics_str} |\n"
        )

    # Add seminal references summary to digest
    digest_lines.append("\n---\n\n## Seminal Papers Referenced\n\n")
    digest_lines.append("Key older papers cited by this week's top papers:\n\n")
    seen_refs = set()
    for paper in papers:
        for ref in paper.get("seminal_references", []):
            ref_key = ref["title"]
            if ref_key in seen_refs:
                continue
            seen_refs.add(ref_key)
            year_str = f" ({ref['year']})" if ref.get("year") else ""
            cite_str = f" [{ref['citation_count']:,} cites]" if ref.get("citation_count") else ""
            if ref.get("arxiv_url"):
                digest_lines.append(f"- **[{ref['title']}]({ref['arxiv_url']})**{year_str}{cite_str}\n")
            else:
                digest_lines.append(f"- **{ref['title']}**{year_str}{cite_str}\n")

    if not seen_refs:
        digest_lines.append("_No reference data available from Semantic Scholar._\n")

    digest_path.write_text("".join(digest_lines))

    return digest_path
