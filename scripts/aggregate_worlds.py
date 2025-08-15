#!/usr/bin/env python3
"""
VRChat World Data Aggregation Script

This script processes JSON files containing VRChat world data and aggregates
statistics about each world across all files. It outputs a CSV file with
world information sorted by average occupants.

Usage:
    python scripts/aggregate_worlds.py

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
        return ""
    
    if isinstance(bio_links, list):
        # Join multiple links with semicolon
        return "; ".join(str(link) for link in bio_links)
    else:
        return str(bio_links)


def aggregate_world_data(data_dir):
    """
    Aggregate world data from all JSON files.
    
    Returns:
        dict: Dictionary with world_id as key and aggregated data as value
    """
    world_data = defaultdict(lambda: {
        'occupants_sum': 0,
        'occurrences': 0,
        'name': '',
        'image_url': '',
        'author_id': '',
        'author_name': '',
        'social_links': '',
        'bio_description': ''
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
            world_info['bio_description'] = safe_get(world, 'bio') or safe_get(world, 'description') or safe_get(world, 'bio_description')
    
    print(f"Processed {world_count} world entries")
    print(f"Found {len(world_data)} unique worlds")
    
    return world_data


def calculate_averages_and_sort(world_data):
    """
    Calculate average occupants for each world and return sorted list.
    
    Returns:
        list: List of tuples (world_id, world_info) sorted by average occupants (descending)
    """
    world_list = []
    
    for world_id, info in world_data.items():
        if info['occurrences'] > 0:
            average_occupants = info['occupants_sum'] / info['occurrences']
            info['average_occupants'] = round(average_occupants, 2)
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
        'occurrences',
        'image_url',
        'author_id',
        'author_name',
        'social_links',
        'bio_description'
    ]
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        
        for world_id, info in world_list:
            row = [
                info['name'],
                world_id,
                info['average_occupants'],
                info['occurrences'],
                info['image_url'],
                info['author_id'],
                info['author_name'],
                info['social_links'],
                info['bio_description']
            ]
            writer.writerow(row)
    
    print(f"Results written to {output_file}")
    print(f"Total worlds processed: {len(world_list)}")


def main():
    """Main function to run the world data aggregation."""
    data_dir = "data"
    output_file = "worlds_aggregated.csv"
    
    print("VRChat World Data Aggregation Script")
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