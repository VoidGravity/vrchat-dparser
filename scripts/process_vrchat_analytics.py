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


def format_social_links(bio_links):
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


def format_bio_description(bio):
    """Format bio description with proper handling of missing values."""
    if not bio:
        return "NA"
    bio_str = str(bio).strip()
    return bio_str if bio_str else "NA"


def calculate_factor(value, min_val=0, max_val=100):
    """
    Calculate factor from heat or popularity value.
    Converts value to a factor ranging from 1.0 to 1.5.
    Higher values = higher factors (closer to 1.5).
    """
    if value <= min_val:
        return 1.0
    if value >= max_val:
        return 1.5
    # Linear interpolation between 1.0 and 1.5
    return 1.0 + (0.5 * (value - min_val) / (max_val - min_val))


def calculate_business_metrics(avg_occupants, heat, popularity):
    """
    Calculate business analytics metrics.
    
    Returns:
        tuple: (estimated_orders, max_marketing_spend)
    """
    # Calculate factors (assuming max values for normalization)
    heat_factor = calculate_factor(heat, 0, 100)
    popularity_factor = calculate_factor(popularity, 0, 100)
    
    # Average the heat factor and popularity factor for combined factor
    combined_factor = (heat_factor + popularity_factor) / 2
    
    # Order estimation formula: (avg_occupants × combined_factor × 30) / 10000
    estimated_orders = (avg_occupants * combined_factor * 30) / 10000
    
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
        'social_links': '',
        'bio_description': '',
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
        
        if not world_info['social_links']:
            bio_links = safe_get(world, 'bioLinks') or safe_get(world, 'bio_links')
            world_info['social_links'] = format_social_links(bio_links)
        
        if not world_info['bio_description']:
            bio = safe_get(world, 'bio') or safe_get(world, 'description') or safe_get(world, 'bio_description')
            world_info['bio_description'] = format_bio_description(bio)
        
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


def calculate_averages_and_sort(world_data):
    """
    Calculate average occupants for each world and return sorted list.
    Only includes worlds with 7 or more total occurrences.
    
    Returns:
        list: List of tuples (world_id, world_info) sorted by average occupants (descending)
    """
    world_list = []
    
    for world_id, info in world_data.items():
        if info['occurrences'] >= 7:  # Filter for 7+ occurrences
            average_occupants = info['occupants_sum'] / info['occurrences']
            info['average_occupants'] = round(average_occupants, 2)
            
            # Handle case where min_occupants was never updated (no data)
            if info['min_occupants'] == float('inf'):
                info['min_occupants'] = 0
            
            # Calculate business metrics
            estimated_orders, max_marketing_spend = calculate_business_metrics(
                average_occupants, info['heat'], info['popularity']
            )
            info['estimated_orders'] = estimated_orders
            info['max_marketing_spend'] = max_marketing_spend
            
            world_list.append((world_id, info))
    
    # Sort by average occupants (highest first)
    world_list.sort(key=lambda x: x[1]['average_occupants'], reverse=True)
    
    return world_list


def write_csv_output(world_list, output_file):
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
        'bio_description',
        'social_links'
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
                info['bio_description'],
                info['social_links']
            ]
            writer.writerow(row)
    
    print(f"Results written to {output_file}")
    print(f"Total worlds processed: {len(world_list)}")
    print(f"Worlds filtered for 7+ occurrences: {len(world_list)}")


def main():
    """Main function to run the world data aggregation."""
    data_dir = "data"
    output_file = "worlds_aggregated.csv"
    
    print("VRChat Analytics Processor Script")
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
    
    # Calculate averages and sort
    world_list = calculate_averages_and_sort(world_data)
    
    # Write output CSV
    write_csv_output(world_list, output_file)
    
    print("\nTop 5 worlds by average occupants:")
    for i, (world_id, info) in enumerate(world_list[:5], 1):
        world_name = info['name'] or world_id
        print(f"{i}. {world_name}: {info['average_occupants']} avg occupants ({info['occurrences']} occurrences)")
    
    return 0


if __name__ == "__main__":
    exit(main())