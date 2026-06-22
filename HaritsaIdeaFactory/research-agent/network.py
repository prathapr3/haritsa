"""
Author network tracking — accumulates author sightings across runs.
"""
import json
from pathlib import Path
from config import VAULT_PATH

NETWORK_PATH = VAULT_PATH / "author_network.json"


def load_network():
    """Load the author network from disk."""
    if NETWORK_PATH.exists():
        try:
            return json.loads(NETWORK_PATH.read_text())
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_network(network):
    """Save the author network to disk."""
    NETWORK_PATH.parent.mkdir(parents=True, exist_ok=True)
    NETWORK_PATH.write_text(json.dumps(network, indent=2))


def update_network(papers):
    """Update the author network with authors from new papers.

    Each author entry tracks:
        - count: number of times seen
        - papers: list of paper IDs they've authored (most recent first)
        - last_seen: date of most recent paper
    """
    network = load_network()

    for paper in papers:
        date_str = paper["published"].strftime("%Y-%m-%d")
        paper_id = paper["id"]

        for author in paper["authors"]:
            if author not in network:
                network[author] = {
                    "count": 0,
                    "papers": [],
                    "last_seen": None,
                }
            entry = network[author]
            entry["count"] += 1
            if paper_id not in entry["papers"]:
                entry["papers"].insert(0, paper_id)
                # Keep only last 20 paper IDs
                entry["papers"] = entry["papers"][:20]
            entry["last_seen"] = date_str

    save_network(network)
    return network


def print_top_authors(top_n=20):
    """Print the top N most frequently seen authors."""
    network = load_network()
    if not network:
        print("No author network data yet. Run the fetcher first.")
        return

    sorted_authors = sorted(network.items(), key=lambda x: x[1]["count"], reverse=True)

    print(f"\nTop {top_n} Most Frequent Authors in Your Domains\n")
    print(f"{'#':>3}  {'Author':<35} {'Count':>5}  {'Last Seen':<12} Papers")
    print(f"{'---':>3}  {'-'*35} {'-----':>5}  {'-'*12} {'------'}")

    for i, (author, data) in enumerate(sorted_authors[:top_n], 1):
        last_seen = data.get("last_seen", "?")
        paper_count = len(data.get("papers", []))
        print(f"{i:3}  {author:<35} {data['count']:>5}  {last_seen:<12} {paper_count} unique")
