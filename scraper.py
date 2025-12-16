from utils import get_client, to_csv, papers_to_list, create_output_directory, setup_logging, check_existing_data
from venue import get_venues, group_venues
from paper import get_papers
from filters import satisfies_any_filters
import logging


class Scraper:
  def __init__(self, conferences, years, keywords, extractor, fpath, selector=None, fns=[], groups=['conference'], only_accepted=True, skip_existing=True):
    # fns is a list of functions that can be specified by the user each taking in a single paper object as a parameter and returning the modified paper
    self.confs = conferences
    self.years = years
    self.keywords = keywords
    self.extractor = extractor
    self.fpath = fpath
    self.fns = fns
    self.groups = groups
    self.only_accepted = only_accepted
    self.selector = selector
    self.filters = []
    self.skip_existing = skip_existing

    # Setup logging
    self.logger = setup_logging()
    self.logger.info("="*60)
    self.logger.info("Starting OpenReview Scraper")
    self.logger.info(f"Conferences: {conferences}")
    self.logger.info(f"Years: {years}")
    self.logger.info(f"Keywords: {keywords}")
    self.logger.info(f"Output file: {fpath}")
    self.logger.info("="*60)

    # Get both API v1 and API v2 clients
    self.clients = get_client()
    self.papers = None # this'll contain all the papers returned from apply_on_papers
  
  def __call__(self):
    self.scrape()
  
  def scrape(self):
    # Process each conference separately
    all_papers = {}

    for i, conference in enumerate(self.confs, 1):
      self.logger.info(f"\n{'='*50}")
      self.logger.info(f"Processing {conference} ({i}/{len(self.confs)})")
      self.logger.info(f"{'='*50}")

      # Check if we should skip existing data
      years_to_process = self.years.copy()  # Default: process all years

      if self.skip_existing:
        years_to_process = []
        for year in self.years:
          if not check_existing_data(conference, year):
            years_to_process.append(year)

        if not years_to_process:
          self.logger.info(f"⏭️  All data already exists for {conference}, skipping...")
          continue

        self.logger.info(f"📋 Will process years {years_to_process} for {conference} (skip_existing=True)")
      else:
        self.logger.info(f"📋 Will process all years {years_to_process} for {conference} (skip_existing=False)")

      # Get venues for this specific conference (use original years for venue discovery)
      self.logger.info(f"Getting venues for {conference}...")
      venues = get_venues(self.clients, [conference], self.years)

      if not venues:
        self.logger.warning(f"❌ No venues found for {conference}")
        continue

      self.logger.info(f"✅ Found venues for {conference}: {venues}")

      # Get papers for this conference
      self.logger.info(f"Getting papers from {len(venues)} venues...")
      try:
        conf_papers = get_papers(self.clients, group_venues(venues, self.groups), self.only_accepted)
      except Exception as e:
        self.logger.error(f"❌ Error getting papers for {conference}: {e}")
        continue

      # Count total papers before filtering
      total_papers = sum(len(venue_papers) for grouped_venues in conf_papers.values()
                        for venue_papers in grouped_venues.values())

      if total_papers == 0:
        self.logger.warning(f"❌ No papers found for {conference}")
        continue

      self.logger.info(f"Found {total_papers} total papers for {conference}")

      # Apply filters
      self.logger.info(f"Applying filters (keywords: {self.keywords})...")
      try:
        conf_papers = self.apply_on_papers(conf_papers)
      except Exception as e:
        self.logger.error(f"❌ Error applying filters for {conference}: {e}")
        continue

      if self.selector is not None:
        conf_papers_list = self.selector(conf_papers)
      else:
        conf_papers_list = papers_to_list(conf_papers)

      if not conf_papers_list:
        self.logger.warning(f"❌ No papers passed filters for {conference}")
        continue

      self.logger.info(f"✅ {len(conf_papers_list)} papers passed filters for {conference}")

      # Save papers for this conference by year (only for years that need processing)
      for year in years_to_process:
        # Filter papers for this specific year
        year_papers = [paper for paper in conf_papers_list if paper.get('year') == str(year)]

        if year_papers:
          self.logger.info(f"📄 Saving {len(year_papers)} papers for {conference} {year}...")
          output_dir = create_output_directory(conference, year)
          csv_path = f"{output_dir}/papers.csv"

          try:
            to_csv(year_papers, csv_path)
            self.logger.info(f"✅ CSV saved successfully: {csv_path}")

            # Also save pkl data structure
            if conference not in all_papers:
              all_papers[conference] = {}
            all_papers[conference][year] = {
              'conference': {f"{conference}.cc/{year}/Conference": []}
            }

            # Convert papers back to original format for pkl saving
            for paper_dict in year_papers:
              # Create a mock paper object for pkl saving
              class MockPaper:
                def __init__(self, data):
                  for key, value in data.items():
                    setattr(self, key, value)

              mock_paper = MockPaper(paper_dict)
              all_papers[conference][year]['conference'][f"{conference}.cc/{year}/Conference"].append(mock_paper)

          except Exception as e:
            self.logger.error(f"❌ Error saving papers for {conference} {year}: {e}")
        else:
          self.logger.info(f"📄 No papers found for {conference} {year}")

    # Store all papers for potential later use
    self.papers = all_papers
    self.logger.info("\n" + "="*60)
    self.logger.info("Scraping completed successfully!")
    self.logger.info("="*60)
  
  def apply_on_papers(self, papers):
    modified_papers = {}
    for group, grouped_venues in papers.items():
      modified_papers[group] = {}
      for venue, venue_papers in grouped_venues.items():
        modified_papers[group][venue] = []
        venue_split = venue.split('/')
        venue_name, venue_year, venue_type = venue_split[0], venue_split[1], venue_split[2]
        for paper in venue_papers:
          # FILTERS
          satisfying_keyword, satisfying_filter_type, satisfies = satisfies_any_filters(paper, self.keywords, self.filters)
          if satisfies:
            # creating a new field(key) in content attr which is a dict
            paper.content['match'] = {satisfying_filter_type: satisfying_keyword}
            paper.content['group'] = group
            # Execute some custom functions
            for fn in self.fns:
              paper = fn(paper)
            # FIELD EXTRACTION here paper object will be converted into a dict
            extracted_paper = self.extractor(paper)
            # add some extra fields
            extracted_paper['venue'] = venue_name
            extracted_paper['year'] = venue_year
            extracted_paper['type'] = venue_type
            modified_papers[group][venue].append(extracted_paper)
    return modified_papers

  def add_filter(self, filter_, *args, **kwargs):
    self.filters.append((filter_, args, kwargs))