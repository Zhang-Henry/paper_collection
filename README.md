# OpenReview Paper Scraper

A comprehensive tool for scraping academic papers from OpenReview with advanced filtering, venue discovery, and data organization capabilities.

Scrape papers from top conferences like ICML, ICLR, NeurIPS, etc using OpenReview API, by searching for specific keywords in title, abstract or keywords in the submissions and save them to a CSV file. Brings down the time taken to gather papers from several hours to a few minutes through automation.

## Quick Start

### Easy Mode - Use `run.py`
```bash
# Run with predefined settings for agent learning research
python run.py
```

### Advanced Mode - Use `run_with_options.py`
```bash
# Run with default settings (major conferences, recent years, agent-related keywords)
python run_with_options.py

# Scrape specific conferences and years
python run_with_options.py --conferences ICLR ICML --years 2024 2023

# Use custom keywords
python run_with_options.py --keywords "reinforcement learning" "neural networks"

# Force redownload (ignore existing data)
python run_with_options.py --force-redownload
```

## Installation

```bash
git clone https://github.com/pranftw/openreview_scraper.git # clone repo
python -m venv venv # create virtual environment
source venv/bin/activate # activate virtual environment
pip install -r requirements.txt # install requirements
cp config.py.example config.py # enter your OpenReview credentials in config.py (optional)
```

### Credentials

The scraper can read public data without authenticating, but providing valid
OpenReview credentials allows it to access information that requires a logged in
session. Credentials can be supplied through the `OPENREVIEW_EMAIL`,
`OPENREVIEW_PASSWORD`, and `OPENREVIEW_TOKEN` environment variables or by
editing `config.py`. If authentication fails the scraper will automatically
fall back to anonymous access instead of exiting.

## Command Line Options (`run_with_options.py`)

| Option | Description | Default |
|--------|-------------|---------|
| `--conferences` | List of conferences to scrape | ICLR, ICML, NeurIPS, AAAI, CVPR, ECCV, ICCV, ACL, EMNLP |
| `--years` | List of years to scrape | 2025, 2024, 2023 |
| `--keywords` | Keywords to filter papers | Agent, Data Synthesis, Synthetic, Trajectory |
| `--skip-existing` | Skip conferences/years with existing data | True |
| `--force-redownload` | Force redownload all data | False |
| `--output` | Output CSV filename | example.csv |
| `--log-level` | Logging verbosity | INFO |

## 📋 Usage Examples

### Example 1: Research on Large Language Models
```bash
python run_with_options.py \
  --conferences ICLR ICML NeurIPS \
  --years 2024 2023 \
  --keywords "large language model" "LLM" "transformer" \
  --output llm_papers.csv
```

### Example 2: Computer Vision Research
```bash
python run_with_options.py \
  --conferences CVPR ICCV ECCV \
  --years 2024 \
  --keywords "computer vision" "object detection" "segmentation" \
  --output cv_papers.csv
```

### Example 3: Natural Language Processing
```bash
python run_with_options.py \
  --conferences ACL EMNLP NAACL \
  --years 2024 2023 \
  --keywords "natural language processing" "NLP" "text generation" \
  --output nlp_papers.csv
```

## 🔍 Venue Discovery Tools

### Discover All Available Venues
```bash
# Get overview of all venues with conference details and URLs
python list_venues.py

# Get detailed JSON output
python list_venues.py --output-format json --output-file venues.json

# Filter specific conferences
python list_venues.py --filter-conferences ICLR ICML --include-workshops

# Get CSV format for analysis
python list_venues.py --output-format csv --output-file venues.csv
```

### Analyze Venue Patterns from Logs
```bash
# Analyze venues from scraper logs
python venues_explorer.py
```

## 📂 Output Structure

The scraper organizes data in the following structure:

```
data/
├── ICLR/
│   ├── 2024/
│   │   └── ICLR_2024.csv
│   └── 2023/
│       └── ICLR_2023.csv
├── ICML/
│   ├── 2024/
│   │   └── ICML_2024.csv
│   └── 2023/
│       └── ICML_2023.csv
└── ...

logs/
├── scraper_20241216_170712.log
└── ...

example.csv  # Combined results from all conferences
```

## 📊 CSV Output Format

Each CSV file contains the following columns:

| Column | Description |
|--------|-------------|
| `title` | Paper title |
| `authors` | Authors (semicolon separated) |
| `authorids` | Author IDs (semicolon separated) |
| `abstract` | Paper abstract |
| `keywords` | Keywords/tags |
| `forum` | OpenReview forum URL |
| `pdf` | Direct PDF download URL |

## ⚙️ Advanced Configuration

### Using the Python API (Legacy/Custom)

```python
from scraper import Scraper
from extract import Extractor
from filters import title_filter, keywords_filter, abstract_filter
from selector import Selector
from utils import save_papers, load_papers

years = ['2024']
conferences = ['ICLR']
keywords = ['generalization']

def modify_paper(paper):
    paper.forum = f"https://openreview.net/forum?id={paper.forum}"
    paper.content['pdf'] = f"https://openreview.net{paper.content['pdf']}"
    # Handle author information formatting
    if 'authors' in paper.content and isinstance(paper.content['authors'], dict):
        authors_list = paper.content['authors'].get('value', [])
        paper.content['authors'] = "; ".join(authors_list) if authors_list else ""
    return paper

# what fields to extract
extractor = Extractor(fields=['forum'], subfields={'content':['title', 'authors', 'authorids', 'keywords', 'abstract', 'pdf', 'match']})

# select all scraped papers
selector = None

scraper = Scraper(
    conferences=conferences,
    years=years,
    keywords=keywords,
    extractor=extractor,
    fpath='example.csv',
    fns=[modify_paper],
    selector=selector,
    skip_existing=True  # Skip existing data
)

# adding filters to filter on
scraper.add_filter(title_filter)
scraper.add_filter(keywords_filter)
scraper.add_filter(abstract_filter)

scraper()

# if you want to save scraped papers as OpenReview objects using pickle
save_papers(scraper.papers, fpath='papers.pkl')
saved_papers = load_papers(fpath='papers.pkl')
```
