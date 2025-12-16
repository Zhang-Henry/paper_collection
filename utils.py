import openreview
import csv
from config import EMAIL, PASSWORD, TOKEN
import dill
import os


def _auth_kwargs():
    if TOKEN:
        return {'token': TOKEN}
    if EMAIL and PASSWORD:
        return {'username': EMAIL, 'password': PASSWORD}
    return {}


def _build_client(constructor, baseurl, auth_kwargs):
    kwargs = {'baseurl': baseurl}
    if auth_kwargs:
        kwargs.update(auth_kwargs)
    try:
        return constructor(**kwargs)
    except openreview.OpenReviewException as exc:
        if auth_kwargs:
            print(
                f"Authentication with OpenReview failed ({exc}). "
                "Falling back to anonymous access."
            )
            return constructor(baseurl=baseurl)
        raise


def get_client():
    """
    Returns a tuple of (client_v1, client_v2) for both OpenReview API versions.
    """
    auth_kwargs = _auth_kwargs()
    client_v1 = _build_client(
        openreview.Client,
        baseurl='https://api.openreview.net',
        auth_kwargs=auth_kwargs
    )
    
    client_v2 = _build_client(
        openreview.api.OpenReviewClient,
        baseurl='https://api2.openreview.net',
        auth_kwargs=auth_kwargs
    )
    
    return client_v1, client_v2


def papers_to_list(papers):
  all_papers = []
  for grouped_venues in papers.values():
    for venue_papers in grouped_venues.values():
      for paper in venue_papers:
        all_papers.append(paper)
  return all_papers


def create_output_directory(conference, year, base_dir='data'):
  """Create directory structure for conference and year"""
  output_dir = os.path.join(base_dir, conference, str(year))
  os.makedirs(output_dir, exist_ok=True)
  return output_dir

def to_csv(papers_list, fpath):
  def write_csv():
    # Ensure directory exists only if there's a directory path
    dir_path = os.path.dirname(fpath)
    if dir_path:
      os.makedirs(dir_path, exist_ok=True)
    with open(fpath, 'a+') as fp:
      fp.seek(0, 0) # seek to beginning of file and then read
      previous_contents = fp.read()
      writer = csv.DictWriter(fp, fieldnames=field_names)
      if previous_contents.strip()=='':
        writer.writeheader()
      writer.writerows(papers_list)
  if len(papers_list)>0:
    field_names = list(papers_list[0].keys()) # choose one of the papers, get all the keys as they'll be same for rest of them
    write_csv()


def save_papers(papers, conferences, years, base_dir='data', filename='papers.pkl'):
  """Save papers organized by conference and year"""
  for conference in conferences:
    for year in years:
      output_dir = create_output_directory(conference, year, base_dir)
      fpath = os.path.join(output_dir, filename)

      # Filter papers for this specific conference and year
      filtered_papers = {}
      for group, grouped_venues in papers.items():
        filtered_papers[group] = {}
        for venue, venue_papers in grouped_venues.items():
          venue_split = venue.split('/')
          venue_name, venue_year = venue_split[0], venue_split[1]
          if (venue_name.upper().startswith(conference.upper()) or
              conference.upper() + '.' in venue_name.upper()) and venue_year == str(year):
            filtered_papers[group][venue] = venue_papers

      # Only save if there are papers for this conference/year
      if any(venue_papers for grouped_venues in filtered_papers.values() for venue_papers in grouped_venues.values()):
        # Ensure directory exists
        os.makedirs(os.path.dirname(fpath), exist_ok=True)
        with open(fpath, 'wb') as fp:
          dill.dump(filtered_papers, fp)
        print(f'Papers saved at: {fpath}')


def load_papers(conference, year, base_dir='data', filename='papers.pkl'):
  """Load papers for specific conference and year"""
  output_dir = create_output_directory(conference, year, base_dir)
  fpath = os.path.join(output_dir, filename)

  if os.path.exists(fpath):
    with open(fpath, 'rb') as fp:
      papers = dill.load(fp)
    print(f'Papers loaded from: {fpath}')
    return papers
  else:
    print(f'No papers found at: {fpath}')
    return None
