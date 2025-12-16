# Survey Paper Filtering with GPT-4o-mini

This tool uses GPT-4o-mini to automatically filter papers for the survey "Agent Learning with Data Synthesis: A Comprehensive Survey".

## Features

- **Intelligent Filtering**: Uses GPT-4o-mini to evaluate paper relevance based on title, abstract, and keywords
- **Batch Processing**: Efficiently processes thousands of papers with rate limiting
- **Comprehensive Output**: Generates detailed evaluation results with confidence scores and reasoning
- **Error Handling**: Robust error handling with retry mechanisms
- **Progress Tracking**: Real-time progress monitoring with logging
- **Flexible Configuration**: Customizable batch sizes and evaluation parameters

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Get your OpenAI API key from https://platform.openai.com/api-keys

## Usage

### Basic Usage

```bash
python survey_filter.py --api-key YOUR_OPENAI_API_KEY
```

### Advanced Options

```bash
python survey_filter.py \
  --api-key YOUR_OPENAI_API_KEY \
  --data-dir data \
  --output data/survey_relevant_papers.csv \
  --batch-size 10 \
  --model gpt-4o-mini
```

### Parameters

- `--api-key`: Your OpenAI API key (required)
- `--data-dir`: Directory containing conference paper CSV files (default: data)
- `--output`: Output CSV file path (default: data/survey_relevant_papers.csv)
- `--batch-size`: Number of papers to process per batch (default: 10)
- `--model`: OpenAI model to use (default: gpt-4o-mini)

## Input Data Format

The script expects CSV files organized as:
```
data/
├── CONFERENCE/
│   ├── YEAR/
│   │   └── papers.csv
```

Each `papers.csv` should contain columns:
- `forum`: OpenReview forum URL
- `title`: Paper title (may be JSON format with 'value' key)
- `abstract`: Paper abstract
- `keywords`: Paper keywords
- `venue`: Conference venue
- `year`: Publication year
- `authors`: Authors (optional)
- `pdf`: PDF URL (optional)

## Output Format

The script generates two output files:

### 1. `survey_relevant_papers.csv` (Filtered Results)
Contains only papers marked as relevant, sorted by relevance score.

### 2. `survey_relevant_papers_all_evaluated.csv` (All Evaluations)
Contains all papers with GPT evaluation results.

**Additional columns added:**
- `gpt_relevant`: Boolean indicating relevance (true/false)
- `gpt_confidence`: Confidence score (0.0-1.0)
- `gpt_relevance_score`: Relevance rating (1-10)
- `gpt_reasoning`: GPT's explanation of the evaluation
- `gpt_key_aspects`: Relevant aspects identified by GPT
- `conference`: Extracted conference name
- `year`: Extracted year

## Survey Scope

The filtering focuses on papers relevant to **"Agent Learning with Data Synthesis"**, specifically:

- Reinforcement learning agents using synthetic data for training
- Multi-agent systems with synthetic trajectory generation
- Agent learning with simulated environments
- Data augmentation techniques for agent training
- Synthetic data generation for improving agent performance
- Learning from synthetic demonstrations or expert trajectories

## Testing

Run the test suite to verify functionality:

```bash
python test_survey_filter.py
```

For full testing with API calls:

```bash
# Install requirements first
pip install -r requirements.txt

# Run on test data
python survey_filter.py --api-key YOUR_API_KEY --data-dir test_data --batch-size 1
```

## Cost Estimation

**GPT-4o-mini pricing** (as of 2024):
- Input tokens: $0.150 / 1M tokens
- Output tokens: $0.600 / 1M tokens

**Estimated cost for ~5000 papers:**
- Average input per paper: ~800 tokens (title + abstract + prompt)
- Average output per paper: ~100 tokens (evaluation result)
- **Total estimated cost: ~$3-5 USD**

## Logging

Detailed logs are saved to `survey_filtering.log` including:
- Processing progress
- API call statistics
- Error handling details
- Final summary statistics

## Example Output

```
===========================================
FILTERING COMPLETE
Total papers processed: 4568
Relevant papers found: 127
Relevance rate: 2.78%
API calls made: 4568
Output saved to: data/survey_relevant_papers.csv
===========================================
```

## Error Handling

The script includes comprehensive error handling for:
- API rate limiting and timeouts
- Malformed JSON responses from GPT
- Missing or corrupted CSV files
- Network connectivity issues
- Invalid API keys

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError**: Install requirements with `pip install -r requirements.txt`

2. **API Key Error**: Ensure your OpenAI API key is valid and has sufficient credits

3. **Rate Limiting**: The script includes automatic rate limiting, but you can reduce `--batch-size` if needed

4. **Memory Issues**: For very large datasets, consider processing in smaller batches

5. **JSON Parsing Errors**: Check that input CSV files are properly formatted

### Performance Tips

- Use larger batch sizes (10-20) for faster processing
- Monitor API usage to avoid hitting rate limits
- Use SSD storage for faster CSV processing
- Consider running during off-peak hours for better API performance

## File Structure

```
├── survey_filter.py          # Main filtering script
├── test_survey_filter.py     # Test suite
├── requirements.txt          # Python dependencies
├── SURVEY_FILTER_README.md   # This documentation
├── survey_filtering.log      # Processing logs
└── data/                     # Input/output data
    ├── CONFERENCE/YEAR/papers.csv  # Input papers
    ├── survey_relevant_papers.csv      # Relevant papers
    └── survey_relevant_papers_all_evaluated.csv  # All evaluations
```

---

**Note**: This tool is designed specifically for the "Agent Learning with Data Synthesis" survey. The evaluation criteria and prompts are tailored to this research area.