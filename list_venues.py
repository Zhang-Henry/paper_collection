#!/usr/bin/env python3
"""
OpenReview Venues Discovery Script
获取和分析OpenReview平台上所有可用的venues
"""

import argparse
import json
import csv
from collections import defaultdict
import re
from datetime import datetime
from utils import get_client, setup_logging
import logging

def parse_args():
    parser = argparse.ArgumentParser(description='Discover and analyze OpenReview venues')

    parser.add_argument('--output-format', choices=['console', 'json', 'csv'],
                       default='console', help='Output format (default: console)')

    parser.add_argument('--output-file',
                       help='Output filename (optional)')

    parser.add_argument('--filter-conferences', nargs='+',
                       help='Filter by specific conferences (e.g., ICLR ICML NeurIPS)')

    parser.add_argument('--filter-years', nargs='+',
                       help='Filter by specific years (e.g., 2023 2024 2025)')

    parser.add_argument('--include-workshops', action='store_true',
                       help='Include workshop venues')

    parser.add_argument('--group-by', choices=['conference', 'year', 'type'],
                       default='conference', help='Group results by (default: conference)')

    parser.add_argument('--verbose', action='store_true',
                       help='Verbose output with detailed analysis')

    return parser.parse_args()

def categorize_venue(venue):
    """Categorize venue by type and extract metadata"""
    venue_lower = venue.lower()

    # Extract year
    year_match = re.search(r'20\d{2}', venue)
    year = year_match.group() if year_match else 'unknown'

    # Extract conference name
    conf_patterns = [
        r'(iclr|icml|neurips|nips|aaai|cvpr|iccv|eccv|acl|emnlp|naacl|eacl|coling)',
        r'/([A-Z]{3,6})/',
        r'([A-Z]{3,6})\.(?:cc|org)',
        r'([a-z]+)\.org/([A-Z]{3,6})'
    ]

    conference = 'unknown'
    for pattern in conf_patterns:
        match = re.search(pattern, venue, re.IGNORECASE)
        if match:
            conference = match.group(1).upper()
            break

    # Determine type
    if 'workshop' in venue_lower:
        venue_type = 'Workshop'
    elif 'conference' in venue_lower:
        venue_type = 'Conference'
    elif 'track' in venue_lower:
        venue_type = 'Track'
    elif 'tutorial' in venue_lower:
        venue_type = 'Tutorial'
    elif 'demo' in venue_lower:
        venue_type = 'Demo'
    elif 'poster' in venue_lower:
        venue_type = 'Poster'
    else:
        venue_type = 'Other'

    return {
        'venue': venue,
        'conference': conference,
        'year': year,
        'type': venue_type
    }

def fetch_all_venues():
    """Fetch all venues from OpenReview"""
    logger = logging.getLogger(__name__)

    try:
        logger.info("Connecting to OpenReview API...")
        clients = get_client()
        client_v1, client_v2 = clients

        # Get venues from both APIs
        venues_v1 = []
        venues_v2 = []

        try:
            logger.info("Fetching venues from API v1...")
            venues_v1 = client_v1.get_group(id='venues').members
            logger.info(f"Found {len(venues_v1)} venues from API v1")
        except Exception as e:
            logger.warning(f"Error fetching from API v1: {e}")

        try:
            logger.info("Fetching venues from API v2...")
            venues_v2 = client_v2.get_group(id='venues').members
            logger.info(f"Found {len(venues_v2)} venues from API v2")
        except Exception as e:
            logger.warning(f"Error fetching from API v2: {e}")

        # Merge and deduplicate
        all_venues = list(set(venues_v1 + venues_v2))
        logger.info(f"Total unique venues: {len(all_venues)}")

        return all_venues

    except Exception as e:
        logger.error(f"Failed to fetch venues: {e}")
        return []

def filter_venues(venues, conferences=None, years=None, include_workshops=True):
    """Filter venues based on criteria"""
    filtered = []

    for venue_info in venues:
        # Filter by conference
        if conferences and venue_info['conference'].upper() not in [c.upper() for c in conferences]:
            continue

        # Filter by year
        if years and venue_info['year'] not in years:
            continue

        # Filter workshops
        if not include_workshops and venue_info['type'] == 'Workshop':
            continue

        filtered.append(venue_info)

    return filtered

def analyze_venues(venues):
    """Analyze venue statistics"""
    stats = {
        'total': len(venues),
        'by_conference': defaultdict(int),
        'by_year': defaultdict(int),
        'by_type': defaultdict(int),
        'by_conf_year': defaultdict(lambda: defaultdict(int))
    }

    for venue_info in venues:
        conf = venue_info['conference']
        year = venue_info['year']
        vtype = venue_info['type']

        stats['by_conference'][conf] += 1
        stats['by_year'][year] += 1
        stats['by_type'][vtype] += 1
        stats['by_conf_year'][conf][year] += 1

    return stats

def output_results(venues, stats, args):
    """Output results in specified format"""

    if args.output_format == 'console':
        output_console(venues, stats, args)
    elif args.output_format == 'json':
        output_json(venues, stats, args)
    elif args.output_format == 'csv':
        output_csv(venues, args)

def output_console(venues, stats, args):
    """Output to console"""
    print("🔍 OpenReview Venues Discovery Report")
    print("="*60)

    print(f"\n📊 Summary Statistics:")
    print(f"  Total venues: {stats['total']}")
    print(f"  Unique conferences: {len(stats['by_conference'])}")
    print(f"  Years covered: {len(stats['by_year'])}")
    print(f"  Venue types: {len(stats['by_type'])}")

    print(f"\n🏛️  Top Conferences:")
    for conf, count in sorted(stats['by_conference'].items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {conf}: {count} venues")

    print(f"\n📅 By Year:")
    for year, count in sorted(stats['by_year'].items()):
        if year != 'unknown':
            print(f"  {year}: {count} venues")

    print(f"\n📝 By Type:")
    for vtype, count in sorted(stats['by_type'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {vtype}: {count} venues")

    if args.verbose:
        print(f"\n📋 Detailed Conference-Year Breakdown:")
        for conf in sorted(stats['by_conf_year'].keys()):
            if conf != 'unknown':
                print(f"\n  {conf}:")
                years = stats['by_conf_year'][conf]
                for year in sorted(years.keys()):
                    if year != 'unknown':
                        print(f"    {year}: {years[year]} venues")

        print(f"\n📄 Sample Venues:")
        grouped = defaultdict(list)
        for venue_info in venues[:20]:  # Show first 20
            key = f"{venue_info['conference']} {venue_info['year']} ({venue_info['type']})"
            grouped[key].append(venue_info['venue'])

        for key, venue_list in list(grouped.items())[:10]:
            print(f"\n  {key}:")
            for venue in venue_list[:3]:  # Show max 3 per group
                print(f"    - {venue}")
            if len(venue_list) > 3:
                print(f"    ... and {len(venue_list)-3} more")

def output_json(venues, stats, args):
    """Output to JSON file"""
    data = {
        'summary': {
            'total_venues': stats['total'],
            'generated_at': str(datetime.now()),
            'filters': {
                'conferences': args.filter_conferences,
                'years': args.filter_years,
                'include_workshops': args.include_workshops
            }
        },
        'statistics': {
            'by_conference': dict(stats['by_conference']),
            'by_year': dict(stats['by_year']),
            'by_type': dict(stats['by_type'])
        },
        'venues': venues
    }

    filename = args.output_file or 'openreview_venues.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Results saved to {filename}")

def output_csv(venues, args):
    """Output to CSV file"""
    filename = args.output_file or 'openreview_venues.csv'

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['venue', 'conference', 'year', 'type'])
        writer.writeheader()
        writer.writerows(venues)

    print(f"✅ Results saved to {filename}")

def main():
    args = parse_args()

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(log_level)
    logger = logging.getLogger(__name__)

    print("🤖 OpenReview Venues Discovery Tool")
    print("="*50)

    # Fetch all venues
    logger.info("Starting venue discovery...")
    raw_venues = fetch_all_venues()

    if not raw_venues:
        print("❌ No venues found or failed to connect to OpenReview")
        return

    # Categorize venues
    logger.info("Analyzing venue metadata...")
    venues = []
    for venue in raw_venues:
        venue_info = categorize_venue(venue)
        venues.append(venue_info)

    # Apply filters
    if args.filter_conferences or args.filter_years or not args.include_workshops:
        logger.info("Applying filters...")
        venues = filter_venues(venues, args.filter_conferences, args.filter_years, args.include_workshops)

    # Analyze statistics
    stats = analyze_venues(venues)

    # Output results
    output_results(venues, stats, args)

if __name__ == "__main__":
    main()