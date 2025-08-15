# vrchat-dparser

A Python tool for processing and aggregating VRChat world data from JSON files with advanced filtering, business analytics, and enhanced data extraction.

## Features

- Processes multiple JSON files containing VRChat world data
- Aggregates statistics for each world across all files
- Calculates average occupants and occurrence counts
- Advanced filtering (7+ occurrences minimum for final output)
- Business analytics with order estimation and marketing spend calculations
- Enhanced bio/social links extraction with proper formatting
- Heat and popularity value tracking
- Min/max occupant tracking across all data files
- Outputs results as CSV sorted by average occupants
- Handles large datasets efficiently using Python standard library only

## Usage

### World Data Aggregation

The main script `scripts/process_vrchat_analytics.py` processes JSON files in the `data/` directory and generates an aggregated CSV report with advanced analytics.

```bash
# Place your JSON files in the data/ directory
mkdir -p data
# Add your JSON files to data/

# Run the analytics processor script
python scripts/process_vrchat_analytics.py
```

**Input**: JSON files in `data/` directory containing world data arrays
**Output**: `worlds_aggregated.csv` with aggregated world statistics and business analytics

#### Expected JSON Format

The script handles multiple JSON formats and extracts the following fields:

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
    "bioLinks": ["https://twitter.com/author", "https://author.fanbox.cc/"],
    "bio": "可能性は無限大\n公式Twitter：＠Author",
    "heat": 75,
    "popularity": 85
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

The CSV output includes 15 columns in this order:

1. `world_name`: Name of the world
2. `world_id`: Unique world identifier  
3. `average_occupants`: Average number of occupants across all appearances
4. `total_occurrences`: Number of times the world appears in all files
5. `max_occupants`: Maximum recorded occupants across all data files
6. `min_occupants`: Minimum recorded occupants across all data files
7. `heat`: Heat value for the world
8. `popularity`: Popularity value for the world
9. `estimated_orders`: Estimated monthly orders (business analytics)
10. `max_marketing_spend`: Maximum recommended marketing spend
11. `image_url`: World preview image URL
12. `user_id`: World author's user ID
13. `user_name`: World author's display name
14. `bio_description`: Author's bio description (formatted)
15. `social_links`: Author's social media links (semicolon-separated)

**Filtering**: Only worlds with 7 or more total occurrences across all files are included in the final output.

**Missing Data**: Fields use "NA" when bio or bioLinks are missing/empty.

The output is sorted by average occupants in descending order.

## Business Analytics

### Factor Calculation System

The script implements a factor calculation system that converts heat and popularity values to factors ranging from 1.0 to 1.5:

- **Factor Range**: 1.0 (minimum) to 1.5 (maximum)
- **Higher Values**: Higher heat/popularity values result in higher factors (closer to 1.5)
- **Combined Factor**: The heat factor and popularity factor are averaged for a combined factor

### Business Formulas

#### Order Estimation Formula
```
orders = (avg_occupants × combined_factor × 30) / 10000
```

**Explanation**: The formula estimates monthly orders based on the principle that 10,000 monthly visitors typically generate one order. Since occupants come and go, the heat and popularity values help determine how much the average occurrence can be trusted as an indicator of traffic.

#### Maximum Marketing Spend Formula
```
max_marketing_spend = orders × 400 × 0.35
```

**Explanation**: The maximum marketing spend should not exceed 35% of revenue, assuming $400 revenue per order. This ensures profitable marketing campaigns while maintaining healthy margins.

### Financial Calculations

All financial calculations are rounded to 2 decimal places for practical business use.

## Requirements

- Python 3.6+
- No external dependencies (uses only Python standard library)
