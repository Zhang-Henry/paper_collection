#!/usr/bin/env python3
"""
简化版本的OpenReview Venues探索工具
基于现有日志文件分析venues
"""

import re
import json
from collections import defaultdict

def parse_log_for_venues(log_file_path):
    """从日志文件解析venues信息"""
    venues = []

    try:
        with open(log_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                # 查找venue匹配的日志行
                if 'venue for' in line and ('Conference venue' in line or 'Workshop venue' in line or 'Other venue' in line):
                    # 提取venue路径
                    venue_match = re.search(r'venue for \w+: (.+)$', line.strip())
                    if venue_match:
                        venues.append(venue_match.group(1))

    except FileNotFoundError:
        print(f"❌ 日志文件不存在: {log_file_path}")
        return []

    return venues

def categorize_venue(venue):
    """分析venue信息"""
    venue_lower = venue.lower()

    # 提取年份
    year_match = re.search(r'20\d{2}', venue)
    year = year_match.group() if year_match else 'unknown'

    # 提取会议名称
    conf_patterns = [
        r'(iclr|icml|neurips|nips|aaai|cvpr|iccv|eccv|acl|emnlp)',
        r'/([A-Z]{3,6})/',
        r'([A-Z]{3,6})\.(?:cc|org)',
        r'thecvf\.com/([A-Z]{3,6})/'
    ]

    conference = 'unknown'
    for pattern in conf_patterns:
        match = re.search(pattern, venue, re.IGNORECASE)
        if match:
            conference = match.group(1).upper()
            break

    # 判断类型
    if 'workshop' in venue_lower:
        venue_type = 'Workshop'
    elif 'conference' in venue_lower:
        venue_type = 'Conference'
    elif 'track' in venue_lower:
        venue_type = 'Track'
    else:
        venue_type = 'Other'

    return {
        'venue': venue,
        'conference': conference,
        'year': year,
        'type': venue_type
    }

def analyze_venues(venues_info):
    """分析venues统计信息"""
    stats = {
        'total': len(venues_info),
        'by_conference': defaultdict(int),
        'by_year': defaultdict(int),
        'by_type': defaultdict(int),
        'by_conf_year': defaultdict(lambda: defaultdict(int)),
        'by_conf_type': defaultdict(lambda: defaultdict(int))
    }

    for info in venues_info:
        conf = info['conference']
        year = info['year']
        vtype = info['type']

        stats['by_conference'][conf] += 1
        stats['by_year'][year] += 1
        stats['by_type'][vtype] += 1
        stats['by_conf_year'][conf][year] += 1
        stats['by_conf_type'][conf][vtype] += 1

    return stats

def print_analysis(stats, venues_info):
    """打印分析结果"""
    print("🔍 OpenReview Venues 分析报告")
    print("=" * 60)

    print(f"\n📊 总体统计:")
    print(f"  总venues数量: {stats['total']}")
    print(f"  涵盖会议数: {len(stats['by_conference'])}")
    print(f"  涵盖年份数: {len(stats['by_year'])}")
    print(f"  venue类型数: {len(stats['by_type'])}")

    print(f"\n🏛️ 各会议venues数量:")
    for conf, count in sorted(stats['by_conference'].items(), key=lambda x: x[1], reverse=True):
        if conf != 'unknown':
            print(f"  {conf}: {count} venues")

    print(f"\n📅 各年份venues数量:")
    for year in sorted(stats['by_year'].keys()):
        if year != 'unknown':
            count = stats['by_year'][year]
            print(f"  {year}: {count} venues")

    print(f"\n📝 各类型venues数量:")
    for vtype, count in sorted(stats['by_type'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {vtype}: {count} venues")

    print(f"\n🔍 详细分析:")
    for conf in sorted(stats['by_conf_type'].keys()):
        if conf != 'unknown':
            types = stats['by_conf_type'][conf]
            print(f"\n  {conf}:")
            for vtype, count in types.items():
                print(f"    {vtype}: {count}")

    print(f"\n📋 年份分布:")
    for conf in sorted(stats['by_conf_year'].keys()):
        if conf != 'unknown':
            years = stats['by_conf_year'][conf]
            print(f"\n  {conf}:")
            for year in sorted(years.keys()):
                if year != 'unknown':
                    count = years[year]
                    print(f"    {year}: {count} venues")

def main():
    # 使用最新的日志文件
    log_file = "logs/scraper_20251216_170320.log"

    print("🤖 OpenReview Venues 探索工具")
    print("=" * 50)
    print(f"📄 分析日志文件: {log_file}")

    # 从日志解析venues
    venues = parse_log_for_venues(log_file)

    if not venues:
        print("❌ 未找到venues信息")
        return

    print(f"✅ 找到 {len(venues)} 个venues")

    # 分析venues
    venues_info = [categorize_venue(v) for v in venues]
    stats = analyze_venues(venues_info)

    # 打印分析结果
    print_analysis(stats, venues_info)

    # 保存详细信息到JSON
    output_data = {
        'venues': venues_info,
        'statistics': {
            'by_conference': dict(stats['by_conference']),
            'by_year': dict(stats['by_year']),
            'by_type': dict(stats['by_type'])
        }
    }

    with open('venues_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"\n💾 详细分析结果已保存到: venues_analysis.json")

if __name__ == "__main__":
    main()