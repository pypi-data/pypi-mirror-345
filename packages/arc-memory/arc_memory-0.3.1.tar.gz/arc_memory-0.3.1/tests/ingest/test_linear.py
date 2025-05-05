#!/usr/bin/env python

import logging
from pathlib import Path

from arc_memory.ingest.linear import LinearIngestor

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create a LinearIngestor
ingestor = LinearIngestor()

# Set the Linear API key
linear_token = "lin_api_tIx4onkiXzTCrRnzaQyC72XCOTeW0HlUtFt9KQaj"

# Run the ingest method
try:
    nodes, edges, metadata = ingestor.ingest(
        repo_path=Path("."),
        token=linear_token,
    )
    print(f"Successfully ingested {len(nodes)} nodes and {len(edges)} edges")
    print(f"Metadata: {metadata}")
except Exception as e:
    print(f"Error: {e}")
