# vrchat-dparser

A Python tool for processing and aggregating VRChat world data from JSON files with advanced filtering, business analytics, and enhanced data extraction.

## Features

- Processes multiple JSON files containing VRChat world data
- Aggregates statistics for each world across all files
- Calculates average occupants and occurrence counts
- Environment-based configuration system with .env support
- Configurable filtering thresholds (occurrences and marketing spend)
- Simplified business analytics with configurable factor calculation
- Enhanced bio/social links extraction with proper formatting
- Heat and popularity value tracking
- Min/max occupant tracking across all data files
- Outputs results as CSV sorted by average occupants
- Handles large datasets efficiently using Python standard library

## Installation

1. Install the required dependency:
```bash
pip install python-dotenv
```

2. Set up your environment configuration:
```bash
cp .env.example .env
# Edit .env with your preferred settings
```

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

**Filtering**: Only worlds meeting both criteria are included in output:
- Minimum occurrences (configurable, default: 7+)  
- Minimum marketing spend (configurable, default: $15+)

**Missing Data**: Fields use "NA" when bio or bioLinks are missing/empty.

The output is sorted by average occupants in descending order.

## Business Analytics

### Simplified Factor Calculation System

The script uses a configurable multiplier system for business calculations:

- **Daily Visitors Formula**: `daily_visitors = avg_occupants × HEAT_POPULARITY_FACTOR`
- **Factor Range**: Configurable (default 1.0)
- **Simple Configuration**: Single environment variable controls the multiplier

### Business Formulas

#### Order Estimation Formula
```
orders = (daily_visitors × 30) / 10000
```

**Explanation**: The formula estimates monthly orders based on the principle that 10,000 monthly visitors typically generate one order. The configurable factor allows adjustment based on actual data analysis.

#### Maximum Marketing Spend Formula
```
max_marketing_spend = orders × 400 × 0.35
```

**Explanation**: The maximum marketing spend should not exceed 35% of revenue, assuming $400 revenue per order. This ensures profitable marketing campaigns while maintaining healthy margins.

### Filtering

The system applies two filters:
1. **Minimum Occurrences**: Only worlds appearing in at least `MIN_OCCURRENCES` files (default: 7)
2. **Minimum Marketing Spend**: Only worlds with marketing spend ≥ `MIN_MARKETING_SPEND` (default: $15)

### Financial Calculations

All financial calculations are rounded to 2 decimal places for practical business use.

## Requirements

- Python 3.6+
- python-dotenv (for environment configuration)

## Environment Configuration

The script supports environment-based configuration through a `.env` file. Copy `.env.example` to `.env` and customize the values:

```bash
cp .env.example .env
```

### Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `DATA_LOCATION` | `data` | Directory containing JSON files to process |
| `MIN_OCCURRENCES` | `7` | Minimum occurrences required for a world to be included in output |
| `MIN_MARKETING_SPEND` | `15` | Minimum marketing spend threshold (worlds below this are excluded) |
| `HEAT_POPULARITY_FACTOR` | `1.0` | Multiplier for daily visitors calculation |

### Factor Calculation System

The script uses a simplified factor calculation system:

- **Daily Visitors**: `daily_visitors = avg_occupants × HEAT_POPULARITY_FACTOR`  
- **Order Estimation**: `orders = (daily_visitors × 30) ÷ 10,000`
- **Marketing Spend**: `max_marketing_spend = orders × 400 × 0.35`

**Default Factor**: 1.0 means daily_visitors equals avg_occupants. This can be adjusted based on actual heat/popularity analysis when real multipliers are determined from data analysis.

**Future Enhancement**: Heat and popularity values (range 1-10) can be mapped to specific multipliers once sufficient data analysis determines the correlation between these values and actual traffic patterns.
