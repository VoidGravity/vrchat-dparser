# VRChat Data Parser

VRChat Data Parser is a Python tool for processing and aggregating VRChat world data from JSON files with advanced filtering, business analytics, and enhanced data extraction.

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively

- Bootstrap and run the repository:
  - `pip install python-dotenv`
  - `cp .env.example .env`
  - `mkdir -p data`
  - Add JSON files to the `data/` directory (see JSON Format Requirements section)
  - `python scripts/process_vrchat_analytics.py`
- **Execution Time**: Script runs in under 1 second for typical datasets. NEVER CANCEL - allow up to 30 seconds for large datasets.
- **Output**: Creates `worlds_aggregated.csv` with 15 columns of aggregated analytics data

## Validation

- ALWAYS test any code changes by running the complete workflow:
  1. Ensure `data/` directory contains valid JSON files
  2. Run `python scripts/process_vrchat_analytics.py`
  3. Verify `worlds_aggregated.csv` is created with expected data
  4. Check console output shows proper world counts and filtering results
- **Manual Testing Scenario**: Create test JSON files with 7+ occurrences to meet default filtering thresholds, run script, verify CSV output contains business analytics columns
- Python syntax validation: `python -m py_compile scripts/process_vrchat_analytics.py`
- **No build system, no tests, no linting tools** - this is a simple standalone Python script

## Configuration System

Environment variables via `.env` file (copy from `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `DATA_LOCATION` | `../data` | Directory containing JSON files to process |
| `MIN_OCCURRENCES` | `7` | Minimum occurrences required for a world to be included in output |
| `MIN_MARKETING_SPEND` | `15` | Minimum marketing spend threshold (worlds below this are excluded) |
| `HEAT_POPULARITY_FACTOR` | `1.0` | Multiplier for daily visitors calculation |

**Configuration Testing**: Change values in `.env` and verify script behavior changes accordingly.

## JSON Format Requirements

The script handles two JSON formats in the `data/` directory:

1. **Array format**:
```json
[
  {
    "id": "wrld_001",
    "name": "World Name",
    "occupants": 25,
    "imageUrl": "https://example.com/image.jpg",
    "authorId": "usr_author1",
    "authorName": "Author Name",
    "bioLinks": ["https://twitter.com/author"],
    "bio": "Author bio description",
    "heat": 75,
    "popularity": 85
  }
]
```

2. **Object with worlds array**:
```json
{
  "worlds": [
    { ... world objects ... }
  ]
}
```

**Required for testing**: Create at least 7 JSON files with same world IDs to meet `MIN_OCCURRENCES` default threshold. For initial testing, lower `MIN_MARKETING_SPEND=5` in `.env` to see results with test data.

## Business Analytics Formula

The script calculates business metrics using configurable formulas:
- **Daily Visitors**: `avg_occupants × HEAT_POPULARITY_FACTOR`
- **Order Estimation**: `(daily_visitors × 30) ÷ 10,000`
- **Marketing Spend**: `orders × 400 × 0.35`

## Error Handling

- **Missing data directory**: Script exits with error code 1 and helpful message
- **No JSON files**: Shows warning and exits gracefully
- **Invalid JSON**: Logs parsing errors but continues processing other files
- **Missing world IDs**: Skips entries with warning
- **Invalid occupant values**: Defaults to 0 and continues

## Repository Structure

```
vrchat-dparser/
├── .env                          # Environment configuration
├── .env.example                  # Environment template
├── .gitignore                    # Git ignore rules
├── README.md                     # Documentation
├── scripts/
│   └── process_vrchat_analytics.py  # Main analytics script
└── data/                         # JSON input files directory (user-created)
```

## Common Commands

### Repository Root
```bash
ls -la
# Output:
.env
.env.example
.gitignore
README.md
scripts/
```

### Check Script Syntax
```bash
python -m py_compile scripts/process_vrchat_analytics.py
# Output: (no output if successful)
```

### Run with Custom Configuration
```bash
DATA_LOCATION=custom_data python scripts/process_vrchat_analytics.py
```

### View CSV Output Structure
```bash
head -1 worlds_aggregated.csv
# Output: world_name,world_id,average_occupants,total_occurrences,max_occupants,min_occupants,heat,popularity,estimated_orders,max_marketing_spend,image_url,user_id,user_name,bio,bioLinks
```

## Dependencies

- **Python 3.6+** (tested with Python 3.12)
- **python-dotenv** (for environment configuration)

Install command: `pip install python-dotenv`

## Key Script Functions

- `load_config()`: Loads environment variables with defaults
- `aggregate_world_data()`: Processes all JSON files and aggregates statistics
- `calculate_business_metrics()`: Applies business formulas for analytics
- `write_csv_output()`: Generates final CSV report with 15 columns

## Troubleshooting

- **No output data**: Check `MIN_OCCURRENCES` and `MIN_MARKETING_SPEND` thresholds in `.env` - lower `MIN_MARKETING_SPEND` to 5 for testing
- **Script not finding data**: Verify `DATA_LOCATION` path in `.env` file
- **JSON parsing errors**: Ensure JSON files follow required format structure
- **Missing dependencies**: Run `pip install python-dotenv`
