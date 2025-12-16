#!/usr/bin/env python3

import logging
from scraper import Scraper
from extract import Extractor
from filters import title_filter, keywords_filter, abstract_filter

# 只测试ACL
years = ['2025', '2024', '2023']
conferences = ['ACL']  # 只测试ACL
keywords = ['Agent','Data Synthesis','Synthetic','Trajectory']

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

# what fields to extract
extractor = Extractor(fields=['forum'], subfields={'content':['title', 'authors', 'authorids', 'keywords', 'abstract', 'pdf', 'match']})

scraper = Scraper(conferences=conferences, years=years, keywords=keywords, extractor=extractor, fpath='acl_test.csv', fns=[modify_paper], selector=None)

# adding filters to filter on
scraper.add_filter(title_filter)
scraper.add_filter(keywords_filter)
scraper.add_filter(abstract_filter)

print("=== 专门测试ACL ===")
scraper()

print("\n=== ACL测试完成 ===")
print("检查是否在data/目录下生成了ACL文件夹")