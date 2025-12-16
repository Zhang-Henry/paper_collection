#!/usr/bin/env python3
"""
Advanced OpenReview Scraper with command line options
"""

import argparse
from scraper import Scraper
from extract import Extractor
from filters import title_filter, keywords_filter, abstract_filter
from selector import Selector
from utils import save_papers, load_papers

def parse_args():
    parser = argparse.ArgumentParser(description='OpenReview Paper Scraper with Advanced Options')

    parser.add_argument('--conferences', nargs='+',
                       default=['ICLR','ICML','NeurIPS','AAAI','CVPR','ECCV','ICCV','ACL','EMNLP'],
                       help='List of conferences to scrape (default: all major conferences)')

    parser.add_argument('--years', nargs='+',
                       default=['2025','2024', '2023'],
                       help='List of years to scrape (default: 2025 2024 2023)')

    parser.add_argument('--keywords', nargs='+',
                       default=['Agent','Data Synthesis','Synthetic','Trajectory'],
                       help='Keywords to filter papers (default: Agent, Data Synthesis, Synthetic, Trajectory)')

    parser.add_argument('--skip-existing', action='store_true', default=True,
                       help='Skip conferences/years that already have data (default: True)')

    parser.add_argument('--force-redownload', action='store_true',
                       help='Force redownload all data, ignore existing files')

    parser.add_argument('--output', default='example.csv',
                       help='Output CSV filename (default: example.csv)')

    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       default='INFO', help='Logging level (default: INFO)')

    return parser.parse_args()

def modify_paper(paper):
    paper.forum = f"https://openreview.net/forum?id={paper.forum}"
    paper.content['pdf'] = f"https://openreview.net{paper.content['pdf']}"

    # 处理作者信息格式
    if 'authors' in paper.content and isinstance(paper.content['authors'], dict):
        authors_list = paper.content['authors'].get('value', [])
        paper.content['authors'] = "; ".join(authors_list) if authors_list else ""
    elif 'authors' not in paper.content:
        paper.content['authors'] = ""

    if 'authorids' in paper.content and isinstance(paper.content['authorids'], dict):
        authorids_list = paper.content['authorids'].get('value', [])
        paper.content['authorids'] = "; ".join(authorids_list) if authorids_list else ""
    elif 'authorids' not in paper.content:
        paper.content['authorids'] = ""

    # 处理可能缺失的其他字段
    if 'keywords' not in paper.content:
        paper.content['keywords'] = None

    return paper

def main():
    args = parse_args()

    print("🤖 OpenReview Paper Scraper")
    print("="*50)
    print(f"📋 Conferences: {args.conferences}")
    print(f"📅 Years: {args.years}")
    print(f"🔍 Keywords: {args.keywords}")
    print(f"⏭️  Skip existing: {args.skip_existing and not args.force_redownload}")
    print(f"📄 Output file: {args.output}")
    print("="*50)

    # what fields to extract
    extractor = Extractor(fields=['forum'], subfields={'content':['title', 'authors', 'authorids', 'keywords', 'abstract', 'pdf', 'match']})

    # select all scraped papers
    selector = None

    # Determine skip behavior
    skip_existing = args.skip_existing and not args.force_redownload

    scraper = Scraper(
        conferences=args.conferences,
        years=args.years,
        keywords=args.keywords,
        extractor=extractor,
        fpath=args.output,
        fns=[modify_paper],
        selector=selector,
        skip_existing=skip_existing
    )

    # adding filters to filter on
    scraper.add_filter(title_filter)
    scraper.add_filter(keywords_filter)
    scraper.add_filter(abstract_filter)

    scraper()

    print("\n=== Scraping completed ===")
    print("Data saved to data/ directory organized by conference and year")
    print("Detailed logs saved in logs/ directory")

if __name__ == "__main__":
    main()