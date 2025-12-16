def get_venues(clients, confs, years, include_workshops=False):
  """
  Get venues from both API v1 and API v2 clients and merge the results.

  Args:
    clients: Tuple of (client_v1, client_v2)
    confs: List of conference names
    years: List of years
    include_workshops: Whether to include workshop venues

  Returns:
    List of venue IDs
  """
  import logging
  logger = logging.getLogger(__name__)

  client_v1, client_v2 = clients

  def filter_year(venue):
    if venue is None:
      return None
    for year in years:
      if year in venue:
        return venue
    return None

  # Get venues from API v1
  venues_v1 = []
  try:
    logger.info("Fetching venues from API v1...")
    venues_v1 = client_v1.get_group(id='venues').members
    logger.info(f"Found {len(venues_v1)} venues from API v1")
  except Exception as e:
    logger.error(f"Error getting venues from API v1: {e}")

  # Get venues from API v2
  venues_v2 = []
  try:
    logger.info("Fetching venues from API v2...")
    venues_v2 = client_v2.get_group(id='venues').members
    logger.info(f"Found {len(venues_v2)} venues from API v2")
  except Exception as e:
    logger.error(f"Error getting venues from API v2: {e}")

  # Merge venues from both APIs
  venues = list(set(venues_v1 + venues_v2))
  logger.info(f"Total unique venues: {len(venues)}")

  venues = list(map(filter_year, venues))
  venues = filter(lambda venue: venue is not None, venues)
  venues = list(venues)
  logger.info(f"Venues matching years {years}: {len(venues)}")

  # Collect all matching venues first, then prioritize
  all_matched_venues = {}

  for venue in venues:
    for conf in confs:
      if conf.lower() in venue.lower():
        if conf not in all_matched_venues:
          all_matched_venues[conf] = {
            'conference': [],
            'workshop': [],
            'other': []
          }

        # Categorize venues
        if 'conference' in venue.lower():
          all_matched_venues[conf]['conference'].append(venue)
          logger.info(f"🏛️  Conference venue for {conf}: {venue}")
        elif 'workshop' in venue.lower():
          all_matched_venues[conf]['workshop'].append(venue)
          logger.info(f"🔧 Workshop venue for {conf}: {venue}")
        else:
          all_matched_venues[conf]['other'].append(venue)
          logger.info(f"❓ Other venue for {conf}: {venue}")
        break

  # Apply priority selection
  reqd_venues = []
  for conf in confs:
    if conf in all_matched_venues:
      venues_for_conf = all_matched_venues[conf]

      # Priority 1: Conference venues
      if venues_for_conf['conference']:
        selected_venues = venues_for_conf['conference']
        logger.info(f"🎯 Selected {len(selected_venues)} Conference venues for {conf}")
        reqd_venues.extend(selected_venues)

      # Priority 2: Other venues (if no conference venues found)
      elif venues_for_conf['other']:
        selected_venues = venues_for_conf['other']
        logger.info(f"🎯 Selected {len(selected_venues)} Other venues for {conf} (no Conference venues found)")
        reqd_venues.extend(selected_venues)

      # Priority 3: Workshop venues (as last resort)
      elif venues_for_conf['workshop']:
        selected_venues = venues_for_conf['workshop'][:3]  # Limit to first 3 workshops
        logger.info(f"🎯 Selected {len(selected_venues)} Workshop venues for {conf} (no main venues found)")
        reqd_venues.extend(selected_venues)

      logger.info(f"📊 {conf} venue summary: {len(venues_for_conf['conference'])} Conference, {len(venues_for_conf['workshop'])} Workshop, {len(venues_for_conf['other'])} Other")

  reqd_venues = map(filter_year, reqd_venues)
  reqd_venues = list(filter(lambda venue: venue is not None, reqd_venues))

  logger.info(f"Final venues for conferences {confs}: {reqd_venues}")
  return reqd_venues


def group_venues(venues, bins):
  def get_bins_dict():
    bins_dict = {bin:[] for bin in bins}
    return bins_dict
  
  bins_dict = get_bins_dict()
  for venue in venues:
    for bin in bins:
      if bin.lower() in venue.lower():
        bins_dict[bin].append(venue)
        break
  
  return bins_dict