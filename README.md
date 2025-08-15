# vrchat-dparser

A Python tool for processing and aggregating VRChat world data from JSON files.

## Features

- Processes multiple JSON files containing VRChat world data
- Aggregates statistics for each world across all files
- Calculates average occupants and occurrence counts
- Outputs results as CSV sorted by average occupants
- Handles large datasets efficiently using Python standard library only

## Usage

### World Data Aggregation

The main script `scripts/aggregate_worlds.py` processes JSON files in the `data/` directory and generates an aggregated CSV report.

```bash
# Place your JSON files in the data/ directory
mkdir -p data
# Add your JSON files to data/

# Run the aggregation script
python scripts/aggregate_worlds.py
```

**Input**: JSON files in `data/` directory containing world data arrays
**Output**: `worlds_aggregated.csv` with aggregated world statistics

#### Expected JSON Format

The script handles multiple JSON formats:

1. Array of world objects:
```json
[
  {
    "id": "wrld_001",
    "name": "World Name",
    "occupants": 25,
    "imageUrl": "https://example.com/image.jpg",
    "authorId": "usr_author1",
    "authorName": "Author Name",
    "bioLinks": ["https://link1.com", "https://link2.com"],
    "bio": "World description"
  }
]
```

2. Object with worlds array:
```json
{
  "worlds": [
    { ... world objects ... }
  ]
}
```

#### Output CSV Columns

- `world_name`: Name of the world
- `world_id`: Unique world identifier
- `average_occupants`: Average number of occupants across all appearances
- `occurrences`: Number of times the world appears in all files
- `image_url`: World preview image URL
- `author_id`: World author's user ID
- `author_name`: World author's display name
- `social_links`: Author's social media links (semicolon-separated)
- `bio_description`: Author's bio description

The output is sorted by average occupants in descending order.

## Requirements

- Python 3.6+
- No external dependencies (uses only Python standard library)
