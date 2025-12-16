#!/bin/bash
# Example script for running the survey filter

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Survey Paper Filtering Example${NC}"
echo -e "${BLUE}========================================${NC}"

# Check if API key is provided
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${RED}Error: OPENAI_API_KEY environment variable not set${NC}"
    echo -e "Please set your OpenAI API key:"
    echo -e "export OPENAI_API_KEY='your-api-key-here'"
    echo -e "Then run this script again."
    exit 1
fi

# Check if dependencies are installed
echo -e "${BLUE}Checking dependencies...${NC}"
python -c "import openai, pandas, tqdm" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${RED}Missing dependencies. Installing...${NC}"
    pip install -r requirements.txt
fi

# Run test to create sample data
echo -e "${BLUE}Creating test data...${NC}"
python test_survey_filter.py

# Run filtering on test data (small scale)
echo -e "${BLUE}Running survey filter on test data...${NC}"
python survey_filter.py \
    --api-key $OPENAI_API_KEY \
    --data-dir test_data \
    --output test_data/survey_results.csv \
    --batch-size 1

# Check results
if [ -f "test_data/survey_results.csv" ]; then
    echo -e "${GREEN}Test completed successfully!${NC}"
    echo -e "Results saved to: test_data/survey_results.csv"
    echo -e "Number of relevant papers found:"
    tail -n +2 test_data/survey_results.csv | wc -l
    echo ""
    echo -e "${BLUE}Sample results:${NC}"
    head -3 test_data/survey_results.csv
else
    echo -e "${RED}Test failed - no output file generated${NC}"
fi

echo ""
echo -e "${BLUE}To run on full dataset:${NC}"
echo -e "python survey_filter.py --api-key \$OPENAI_API_KEY"
echo ""
echo -e "${BLUE}Estimated cost for full dataset (~5000 papers): \$3-5 USD${NC}"
echo -e "${BLUE}========================================${NC}"