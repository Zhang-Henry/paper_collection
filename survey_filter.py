#!/usr/bin/env python3
"""
Survey Paper Filtering Script using GPT-4o-mini
Filters papers relevant to "Agent Learning with Data Synthesis: A Comprehensive Survey"
"""

import os
import pandas as pd
import glob
import time
import json
import logging
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import openai
from tqdm import tqdm
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('survey_filtering.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SurveyFilter:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini", batch_size: int = 10):
        """
        Initialize the survey filtering system

        Args:
            api_key: OpenAI API key
            model: OpenAI model to use (default: gpt-4o-mini)
            batch_size: Number of papers to process in each batch
        """
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.batch_size = batch_size
        self.survey_topic = "Agent Learning with Data Synthesis"
        self.survey_description = """
        A comprehensive survey on agent learning methods that utilize data synthesis techniques.
        This includes:
        - Reinforcement learning agents that use synthetic data for training
        - Multi-agent systems with synthetic trajectory generation
        - Agent learning with simulated environments
        - Data augmentation techniques for agent training
        - Synthetic data generation for improving agent performance
        - Learning from synthetic demonstrations or expert trajectories
        """

        # Statistics tracking
        self.total_papers = 0
        self.processed_papers = 0
        self.relevant_papers = 0
        self.api_calls = 0
        self.total_cost = 0.0

    def load_all_papers(self, data_dir: str = "data") -> List[Dict]:
        """
        Load all papers from CSV files in the data directory

        Args:
            data_dir: Path to the data directory containing conference papers

        Returns:
            List of paper dictionaries with metadata
        """
        logger.info("Loading papers from all CSV files...")
        all_papers = []

        # Find all papers.csv files
        csv_files = glob.glob(f"{data_dir}/*/*/papers.csv")
        logger.info(f"Found {len(csv_files)} CSV files to process")

        for csv_file in csv_files:
            try:
                # Extract conference and year from path
                path_parts = csv_file.split(os.sep)
                conference = path_parts[-3]
                year = path_parts[-2]

                # Read CSV file
                df = pd.read_csv(csv_file)

                # Process each paper
                for _, row in df.iterrows():
                    paper = {
                        'forum': row.get('forum', ''),
                        'title': self._clean_field(row.get('title', '')),
                        'abstract': self._clean_field(row.get('abstract', '')),
                        'keywords': self._clean_field(row.get('keywords', '')),
                        'authors': self._clean_field(row.get('authors', '')),
                        'pdf': row.get('pdf', ''),
                        'conference': conference,
                        'year': year,
                        'venue': row.get('venue', ''),
                        'original_file': csv_file
                    }

                    # Only add papers with both title and abstract
                    if paper['title'] and paper['abstract']:
                        all_papers.append(paper)

                logger.info(f"Loaded {len(df)} papers from {conference} {year}")

            except Exception as e:
                logger.error(f"Error loading {csv_file}: {e}")
                continue

        self.total_papers = len(all_papers)
        logger.info(f"Total papers loaded: {self.total_papers}")
        return all_papers

    def _clean_field(self, field) -> str:
        """Clean and extract value from field that might be a dict or string"""
        if pd.isna(field):
            return ""

        if isinstance(field, str):
            # Try to parse as JSON if it looks like a dict
            if field.startswith("{'value':") or field.startswith('{"value":'):
                try:
                    # Convert single quotes to double quotes and parse
                    field_clean = field.replace("'", '"')
                    parsed = json.loads(field_clean)
                    if isinstance(parsed, dict) and 'value' in parsed:
                        return str(parsed['value'])
                except:
                    pass
            return field

        return str(field)

    def create_evaluation_prompt(self, title: str, abstract: str, keywords: str = "") -> str:
        """
        Create a prompt for GPT-4o-mini to evaluate paper relevance

        Args:
            title: Paper title
            abstract: Paper abstract
            keywords: Paper keywords (optional)

        Returns:
            Formatted prompt string
        """
        prompt = f"""
You are an expert researcher evaluating papers for inclusion in a survey titled: "{self.survey_topic}: A Comprehensive Survey"

Survey Scope:
{self.survey_description}

Please evaluate the following paper for relevance to this survey:

Title: {title}

Abstract: {abstract}

Keywords: {keywords}

Evaluation Criteria:
1. Does this paper involve agents (RL agents, multi-agent systems, autonomous agents)?
2. Does it involve data synthesis, synthetic data generation, or simulated data?
3. Is there a connection between agent learning and synthetic/generated data?
4. Would this paper provide valuable insights for the survey topic?

Please respond with ONLY a JSON object in this exact format:
{{
    "relevant": true/false,
    "confidence": 0.0-1.0,
    "relevance_score": 1-10,
    "reasoning": "Brief explanation of why this paper is/isn't relevant",
    "key_aspects": ["list", "of", "relevant", "aspects"]
}}

Be strict but thorough in your evaluation. Papers should clearly involve both agent learning AND data synthesis/synthetic data.
"""
        return prompt

    def evaluate_papers_batch(self, papers: List[Dict]) -> List[Dict]:
        """
        Evaluate a batch of papers using GPT-4o-mini

        Args:
            papers: List of paper dictionaries

        Returns:
            List of papers with evaluation results
        """
        results = []

        for paper in papers:
            try:
                prompt = self.create_evaluation_prompt(
                    paper['title'],
                    paper['abstract'],
                    paper.get('keywords', '')
                )

                # Make API call
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are an expert research assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=500
                )

                self.api_calls += 1

                # Parse response
                try:
                    evaluation = json.loads(response.choices[0].message.content.strip())

                    # Add evaluation results to paper
                    paper.update({
                        'gpt_relevant': evaluation.get('relevant', False),
                        'gpt_confidence': evaluation.get('confidence', 0.0),
                        'gpt_relevance_score': evaluation.get('relevance_score', 0),
                        'gpt_reasoning': evaluation.get('reasoning', ''),
                        'gpt_key_aspects': ', '.join(evaluation.get('key_aspects', []))
                    })

                    if evaluation.get('relevant', False):
                        self.relevant_papers += 1

                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse GPT response for paper: {paper['title'][:50]}...")
                    paper.update({
                        'gpt_relevant': False,
                        'gpt_confidence': 0.0,
                        'gpt_relevance_score': 0,
                        'gpt_reasoning': 'Failed to parse response',
                        'gpt_key_aspects': ''
                    })

                results.append(paper)
                self.processed_papers += 1

                # Rate limiting
                time.sleep(0.1)

            except Exception as e:
                logger.error(f"Error processing paper {paper['title'][:50]}...: {e}")
                paper.update({
                    'gpt_relevant': False,
                    'gpt_confidence': 0.0,
                    'gpt_relevance_score': 0,
                    'gpt_reasoning': f'API Error: {str(e)}',
                    'gpt_key_aspects': ''
                })
                results.append(paper)

        return results

    def save_results(self, papers: List[Dict], output_file: str = "data/survey_relevant_papers.csv"):
        """
        Save filtered papers to CSV file

        Args:
            papers: List of evaluated papers
            output_file: Output CSV file path
        """
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        # Convert to DataFrame
        df = pd.DataFrame(papers)

        # Save all papers
        all_output = output_file.replace('.csv', '_all_evaluated.csv')
        df.to_csv(all_output, index=False)
        logger.info(f"All evaluated papers saved to: {all_output}")

        # Save only relevant papers
        relevant_df = df[df['gpt_relevant'] == True].copy()
        relevant_df = relevant_df.sort_values('gpt_relevance_score', ascending=False)
        relevant_df.to_csv(output_file, index=False)
        logger.info(f"Relevant papers saved to: {output_file}")

        return len(relevant_df)

    def run_filtering(self, data_dir: str = "data", output_file: str = "data/survey_relevant_papers.csv"):
        """
        Run the complete filtering process

        Args:
            data_dir: Input data directory
            output_file: Output CSV file
        """
        logger.info("Starting survey filtering process...")
        logger.info(f"Survey topic: {self.survey_topic}")

        # Load papers
        papers = self.load_all_papers(data_dir)

        if not papers:
            logger.error("No papers found to process!")
            return

        logger.info(f"Processing {len(papers)} papers in batches of {self.batch_size}")

        # Process in batches
        all_results = []

        for i in tqdm(range(0, len(papers), self.batch_size), desc="Processing batches"):
            batch = papers[i:i + self.batch_size]
            batch_results = self.evaluate_papers_batch(batch)
            all_results.extend(batch_results)

            # Progress logging
            if i % (self.batch_size * 5) == 0:
                logger.info(f"Processed {self.processed_papers}/{self.total_papers} papers, "
                          f"found {self.relevant_papers} relevant so far")

        # Save results
        relevant_count = self.save_results(all_results, output_file)

        # Final statistics
        logger.info("\n" + "="*50)
        logger.info("FILTERING COMPLETE")
        logger.info(f"Total papers processed: {self.processed_papers}")
        logger.info(f"Relevant papers found: {relevant_count}")
        logger.info(f"Relevance rate: {(relevant_count/self.processed_papers)*100:.2f}%")
        logger.info(f"API calls made: {self.api_calls}")
        logger.info(f"Output saved to: {output_file}")
        logger.info("="*50)

def main():
    parser = argparse.ArgumentParser(description="Filter papers for survey using GPT-4o-mini")
    parser.add_argument("--api-key", required=True, help="OpenAI API key")
    parser.add_argument("--data-dir", default="data", help="Data directory path")
    parser.add_argument("--output", default="data/survey_relevant_papers.csv", help="Output CSV file")
    parser.add_argument("--batch-size", type=int, default=10, help="Batch size for processing")
    parser.add_argument("--model", default="gpt-4o-mini", help="OpenAI model to use")

    args = parser.parse_args()

    # Initialize filter
    filter_system = SurveyFilter(
        api_key=args.api_key,
        model=args.model,
        batch_size=args.batch_size
    )

    # Run filtering
    filter_system.run_filtering(args.data_dir, args.output)

if __name__ == "__main__":
    main()