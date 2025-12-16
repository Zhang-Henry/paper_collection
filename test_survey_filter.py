#!/usr/bin/env python3
"""
Test script for survey_filter.py
Tests the filtering on a small subset of papers
"""

import pandas as pd
import json
import os
import sys

# Try to import survey_filter, skip OpenAI-dependent tests if not available
try:
    from survey_filter import SurveyFilter
    SURVEY_FILTER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import survey_filter: {e}")
    print("Some tests will be skipped. To run full tests, install requirements:")
    print("pip install -r requirements.txt")
    SURVEY_FILTER_AVAILABLE = False

def create_test_data():
    """Create test CSV with sample papers"""
    test_papers = [
        {
            'forum': 'https://openreview.net/forum?id=test1',
            'title': '{"value": "AgentBench: Evaluating LLMs as Agents"}',
            'abstract': '{"value": "The potential of Large Language Model (LLM) as agents has been widely acknowledged recently. Thus, there is an urgent need to quantitatively evaluate LLMs as agents on challenging tasks in interactive environments. We present AgentBench, a multi-dimensional benchmark that consists of 8 distinct environments to assess LLM-as-Agent\'s reasoning and decision-making abilities."}',
            'keywords': '{"value": ["Large language models", "Autonomous agents", "Reasoning", "Evaluation", "Benchmark"]}',
            'venue': 'ICLR.cc',
            'year': '2024',
            'pdf': 'https://openreview.net/pdf/test1.pdf'
        },
        {
            'forum': 'https://openreview.net/forum?id=test2',
            'title': '{"value": "Synthetic Data Generation for Multi-Agent Reinforcement Learning"}',
            'abstract': '{"value": "This paper proposes a novel approach for generating synthetic training data for multi-agent reinforcement learning systems. We use simulation-based methods to create diverse agent trajectories and demonstrate improved learning performance on complex coordination tasks."}',
            'keywords': '{"value": ["Multi-agent", "Synthetic data", "Reinforcement learning", "Simulation"]}',
            'venue': 'ICML.cc',
            'year': '2024',
            'pdf': 'https://openreview.net/pdf/test2.pdf'
        },
        {
            'forum': 'https://openreview.net/forum?id=test3',
            'title': '{"value": "Attention Mechanisms in Computer Vision"}',
            'abstract': '{"value": "We study attention mechanisms in computer vision models and propose a new architecture for image classification. Our approach achieves state-of-the-art results on ImageNet and other benchmarks without using any agent-based methods."}',
            'keywords': '{"value": ["Computer vision", "Attention", "Deep learning", "Image classification"]}',
            'venue': 'CVPR.cc',
            'year': '2024',
            'pdf': 'https://openreview.net/pdf/test3.pdf'
        }
    ]

    # Create test directory structure
    os.makedirs('test_data/TEST/2024', exist_ok=True)

    # Save test CSV
    df = pd.DataFrame(test_papers)
    df.to_csv('test_data/TEST/2024/papers.csv', index=False)

    print("Test data created at test_data/TEST/2024/papers.csv")
    return test_papers

def test_field_cleaning():
    """Test the _clean_field method"""
    if not SURVEY_FILTER_AVAILABLE:
        print("\nSkipping field cleaning test - SurveyFilter not available")
        return

    filter_system = SurveyFilter(api_key="dummy_key")

    test_cases = [
        ('{"value": "Test Title"}', "Test Title"),
        ("{'value': 'Another Title'}", "Another Title"),
        ("Plain string", "Plain string"),
        ('{"value": ["keyword1", "keyword2"]}', "['keyword1', 'keyword2']")
    ]

    print("\nTesting field cleaning:")
    for input_val, expected in test_cases:
        result = filter_system._clean_field(input_val)
        print(f"Input: {input_val}")
        print(f"Expected: {expected}")
        print(f"Got: {result}")
        print(f"✓ Passed" if str(result) == str(expected) else f"✗ Failed")
        print()

def test_data_loading():
    """Test data loading functionality"""
    if not SURVEY_FILTER_AVAILABLE:
        print("\nSkipping data loading test - SurveyFilter not available")
        return

    filter_system = SurveyFilter(api_key="dummy_key")

    print("Testing data loading...")
    papers = filter_system.load_all_papers("test_data")

    print(f"Loaded {len(papers)} test papers")
    for i, paper in enumerate(papers):
        print(f"\nPaper {i+1}:")
        print(f"  Title: {paper['title'][:50]}...")
        print(f"  Conference: {paper['conference']}")
        print(f"  Year: {paper['year']}")
        print(f"  Has abstract: {bool(paper['abstract'])}")

def test_prompt_generation():
    """Test prompt generation"""
    if not SURVEY_FILTER_AVAILABLE:
        print("\nSkipping prompt generation test - SurveyFilter not available")
        return

    filter_system = SurveyFilter(api_key="dummy_key")

    print("\nTesting prompt generation:")
    prompt = filter_system.create_evaluation_prompt(
        title="Synthetic Data Generation for Multi-Agent Reinforcement Learning",
        abstract="This paper proposes a novel approach for generating synthetic training data for multi-agent reinforcement learning systems.",
        keywords="Multi-agent, Synthetic data, Reinforcement learning"
    )

    print("Generated prompt:")
    print("-" * 50)
    print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
    print("-" * 50)

def main():
    """Run all tests"""
    print("=" * 60)
    print("SURVEY FILTER TEST SUITE")
    print("=" * 60)

    # Create test data
    create_test_data()

    # Run tests
    test_field_cleaning()
    test_data_loading()
    test_prompt_generation()

    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    print("\nTo run with real API:")
    print("python survey_filter.py --api-key YOUR_API_KEY --data-dir test_data --batch-size 1")

if __name__ == "__main__":
    main()