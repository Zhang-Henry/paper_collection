#!/usr/bin/env python3
"""
Runner script for survey_filter.py that loads API key from .env file
"""

import os
import sys
from dotenv import load_dotenv
import argparse

def main():
    load_dotenv()

    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OPENAI_API_KEY not found in .env file")
        print("Please create a .env file with your OpenAI API key:")
        print("OPENAI_API_KEY=your_api_key_here")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Filter papers for survey using GPT-4o-mini")
    parser.add_argument("--data-dir", default="data", help="Data directory path")
    parser.add_argument("--output", default="data/survey_relevant_papers.csv", help="Output CSV file")
    parser.add_argument("--batch-size", type=int, default=10, help="Batch size for processing")
    parser.add_argument("--model", default="gpt-4o-mini", help="OpenAI model to use")

    args = parser.parse_args()

    # Import and run survey filter
    from survey_filter import SurveyFilter

    filter_system = SurveyFilter(
        api_key=api_key,
        model=args.model,
        batch_size=args.batch_size
    )

    filter_system.run_filtering(args.data_dir, args.output)

if __name__ == "__main__":
    main()