#!/usr/bin/env python3
"""
VRChat Analytics Processor Script

This script processes JSON files containing VRChat world data and aggregates
statistics about each world across all files. It includes advanced filtering,
business analytics, and enhanced data extraction.

Usage:
    python scripts/process_vrchat_analytics.py

Input: JSON files in 'data/' directory
Output: 'worlds_aggregated.csv' file
"""

import json
import csv
import os
import glob
from collections import defaultdict

# Try to import python-dotenv, fall back to defaults if not available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not found. Using default configuration.")


def load_config():
    """Load configuration from environment variables with fallback defaults."""
    config = {
        'DATA_LOCATION': os.getenv('DATA_LOCATION', 'data'),
        'MIN_OCCURRENCES': int(os.getenv('MIN_OCCURRENCES', '7')),
        'MIN_MARKETING_SPEND': float(os.getenv('MIN_MARKETING_SPEND', '15')),
        'HEAT_POPULARITY_FACTOR': float(os.getenv('HEAT_POPULARITY_FACTOR', '1.0'))
    }
    return config


def load_json_files(data_dir):
    """Generator that yields world data from all JSON files in the data directory."""
    json_pattern = os.path.join(data_dir, "*.json")
    json_files = glob.glob(json_pattern)
    
    if not json_files:
        print(f"Warning: No JSON files found in {data_dir}")
        return
    
    print(f"Found {len(json_files)} JSON files to process")
    
    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Handle different possible JSON structures
            if isinstance(data, list):
                # If the file contains a list of worlds directly
                for world in data:
                    yield world
            elif isinstance(data, dict):
                # If the file contains an object with a 'worlds' key
                if 'worlds' in data:
                    for world in data['worlds']:
                        yield world
                else:
                    # If the file contains a single world object
                    yield data
            else:
                print(f"Warning: Unexpected data structure in {file_path}")
                
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON file {file_path}: {e}")
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")


def safe_get(data, key, default=""):
    """Safely get a value from a dictionary, returning default if key doesn't exist."""
    return data.get(key, default) if isinstance(data, dict) else default


def format_bioLinks(bio_links):
    """Format social links into a string representation."""
    if not bio_links:
        return "NA"
    
    if isinstance(bio_links, list):
        if not bio_links:  # Empty list
            return "NA"
        # Join multiple links with semicolon
        return ";".join(str(link) for link in bio_links if link)
    else:
        link_str = str(bio_links).strip()
        return link_str if link_str else "NA"


def format_bio(bio):
    """Format bio description with proper handling of missing values."""
    if not bio:
        return "NA"
    bio_str = str(bio).strip()
    return bio_str if bio_str else "NA"


def calculate_business_metrics(avg_occupants, heat_popularity_factor):
    """
    Calculate business analytics metrics using simplified factor system.
    
    Args:
        avg_occupants: Average number of occupants
        heat_popularity_factor: Configurable multiplier factor
    
    Returns:
        tuple: (estimated_orders, max_marketing_spend)
    """
    # Simplified calculation: daily_visitors = avg_occupants × HEAT_POPULARITY_FACTOR
    daily_visitors = avg_occupants * heat_popularity_factor
    
    # Order estimation formula: (daily_visitors × 30) / 10000
    estimated_orders = (daily_visitors * 30) / 10000
    
    # Maximum marketing spend formula: orders × 400 × 0.35
    max_marketing_spend = estimated_orders * 400 * 0.35
    
    # Round to 2 decimal places
    estimated_orders = round(estimated_orders, 2)
    max_marketing_spend = round(max_marketing_spend, 2)
    
    return estimated_orders, max_marketing_spend


def aggregate_world_data(data_dir):
    """
    Aggregate world data from all JSON files.
    
    Returns:
        dict: Dictionary with world_id as key and aggregated data as value
    """
    world_data = defaultdict(lambda: {
        'occupants_sum': 0,
        'occurrences': 0,
        'max_occupants': 0,
        'min_occupants': float('inf'),
        'name': '',
        'image_url': '',
        'author_id': '',
        'author_name': '',
        'bioLinks': '',
        'bio': '',
        'heat': 0,
        'popularity': 0
    })
    
    world_count = 0
    
    for world in load_json_files(data_dir):
        world_id = safe_get(world, 'id')
        if not world_id:
            # Try alternative field names
            world_id = safe_get(world, 'worldId') or safe_get(world, 'world_id')
        
        if not world_id:
            print("Warning: Found world without ID, skipping")
            continue
        
        world_count += 1
        
        # Get occupants (try different possible field names)
        occupants = safe_get(world, 'occupants')
        if occupants is None or occupants == "":
            occupants = safe_get(world, 'currentUsers')
            if occupants is None or occupants == "":
                occupants = safe_get(world, 'users')
                if occupants is None or occupants == "":
                    occupants = 0
        
        try:
            occupants = int(occupants)
        except (ValueError, TypeError):
            occupants = 0
        
        # Aggregate data
        world_info = world_data[world_id]
        world_info['occupants_sum'] += occupants
        world_info['occurrences'] += 1
        
        # Track min/max occupants
        world_info['max_occupants'] = max(world_info['max_occupants'], occupants)
        if world_info['min_occupants'] == float('inf'):
            world_info['min_occupants'] = occupants
        else:
            world_info['min_occupants'] = min(world_info['min_occupants'], occupants)
        
        # Store world details (use first occurrence values)
        if not world_info['name']:
            world_info['name'] = safe_get(world, 'name')
        
        if not world_info['image_url']:
            world_info['image_url'] = safe_get(world, 'imageUrl') or safe_get(world, 'image_url')
        
        if not world_info['author_id']:
            world_info['author_id'] = safe_get(world, 'authorId') or safe_get(world, 'author_id')
        
        if not world_info['author_name']:
            world_info['author_name'] = safe_get(world, 'authorName') or safe_get(world, 'author_name')
        
        if not world_info['bioLinks'] or world_info['bioLinks'] == 'NA':
            bio_links = safe_get(world, 'bioLinks') or safe_get(world, 'bio_links')
            formatted_links = format_bioLinks(bio_links)
            if formatted_links != 'NA':
                world_info['bioLinks'] = formatted_links
        
        if not world_info['bio'] or world_info['bio'] == 'NA':
            bio = safe_get(world, 'bio') or safe_get(world, 'description')
            formatted_bio = format_bio(bio)
            if formatted_bio != 'NA':
                world_info['bio'] = formatted_bio
        
        # Extract heat and popularity (use first occurrence values)
        if world_info['heat'] == 0:
            heat = safe_get(world, 'heat')
            try:
                world_info['heat'] = float(heat) if heat else 0
            except (ValueError, TypeError):
                world_info['heat'] = 0
        
        if world_info['popularity'] == 0:
            popularity = safe_get(world, 'popularity')
            try:
                world_info['popularity'] = float(popularity) if popularity else 0
            except (ValueError, TypeError):
                world_info['popularity'] = 0
    
    print(f"Processed {world_count} world entries")
    print(f"Found {len(world_data)} unique worlds")
    
    return world_data


def calculate_averages_and_sort(world_data, config):
    """
    Calculate average occupants for each world and return sorted list.
    Filters worlds based on occurrences and marketing spend thresholds.
    
    Args:
        world_data: Dictionary of world data
        config: Configuration dictionary with MIN_OCCURRENCES, MIN_MARKETING_SPEND, etc.
    
    Returns:
        list: List of tuples (world_id, world_info) sorted by average occupants (descending)
    """
    world_list = []
    
    for world_id, info in world_data.items():
        if info['occurrences'] >= config['MIN_OCCURRENCES']:
            average_occupants = info['occupants_sum'] / info['occurrences']
            info['average_occupants'] = round(average_occupants, 2)
            
            # Handle case where min_occupants was never updated (no data)
            if info['min_occupants'] == float('inf'):
                info['min_occupants'] = 0
            
            # Calculate business metrics using simplified system
            estimated_orders, max_marketing_spend = calculate_business_metrics(
                average_occupants, config['HEAT_POPULARITY_FACTOR']
            )
            info['estimated_orders'] = estimated_orders
            info['max_marketing_spend'] = max_marketing_spend
            
            # Filter by marketing spend threshold
            if max_marketing_spend >= config['MIN_MARKETING_SPEND']:
                world_list.append((world_id, info))
    
    # Sort by average occupants (highest first)
    world_list.sort(key=lambda x: x[1]['average_occupants'], reverse=True)
    
    return world_list


def write_csv_output(world_list, output_file, config):
    """Write the aggregated world data to a CSV file."""
    headers = [
        'world_name',
        'world_id', 
        'average_occupants',
        'total_occurrences',
        'max_occupants',
        'min_occupants',
        'heat',
        'popularity',
        'estimated_orders',
        'max_marketing_spend',
        'image_url',
        'user_id',
        'user_name',
        'bio',
        'bioLinks'
    ]
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        
        for world_id, info in world_list:
            row = [
                info['name'] if info['name'] else world_id,
                world_id,
                info['average_occupants'],
                info['occurrences'],
                info['max_occupants'],
                info['min_occupants'],
                info['heat'],
                info['popularity'],
                info['estimated_orders'],
                info['max_marketing_spend'],
                info['image_url'] if info['image_url'] else "NA",
                info['author_id'] if info['author_id'] else "NA",
                info['author_name'] if info['author_name'] else "NA",
                info['bio'],
                info['bioLinks']
            ]
            writer.writerow(row)
    
    print(f"Results written to {output_file}")
    print(f"Total worlds processed: {len(world_list)}")
    print(f"Worlds filtered for {config['MIN_OCCURRENCES']}+ occurrences and ${config['MIN_MARKETING_SPEND']}+ marketing spend: {len(world_list)}")


def main():
    """Main function to run the world data aggregation."""
    # Load configuration from environment variables
    config = load_config()
    
    data_dir = config['DATA_LOCATION']
    output_file = "worlds_aggregated.csv"
    
    print("VRChat Analytics Processor Script")
    print("=====================================")
    print(f"Configuration:")
    print(f"  Data Location: {config['DATA_LOCATION']}")
    print(f"  Min Occurrences: {config['MIN_OCCURRENCES']}")
    print(f"  Min Marketing Spend: ${config['MIN_MARKETING_SPEND']}")
    print(f"  Heat/Popularity Factor: {config['HEAT_POPULARITY_FACTOR']}")
    print("=====================================")
    
    # Check if data directory exists
    if not os.path.exists(data_dir):
        print(f"Error: Data directory '{data_dir}' not found")
        print("Please create the data directory and add JSON files to process")
        return 1
    
    # Aggregate world data
    print(f"Processing JSON files in '{data_dir}' directory...")
    world_data = aggregate_world_data(data_dir)
    
    if not world_data:
        print("No world data found to process")
        return 1
    
    # Calculate averages and sort with configuration
    world_list = calculate_averages_and_sort(world_data, config)
    
    # Write output CSV
    write_csv_output(world_list, output_file, config)
    
    print("\nTop 5 worlds by average occupants:")
    for i, (world_id, info) in enumerate(world_list[:5], 1):
        world_name = info['name'] or world_id
        print(f"{i}. {world_name}: {info['average_occupants']} avg occupants ({info['occurrences']} occurrences)")
    
    return 0


if __name__ == "__main__":
    exit(main())
