#!/usr/bin/env python3
"""
Smart SSL Scraper - Only scrapes played matches
"""

from ssl_full_season_scraper import SSLFullSeasonScraper
from ssl_production_scraper import SSLProductionScraper
import time

def smart_scrape_ssl():
    """Smart scraping - find played matches first, then scrape them"""
    print("🧠 SMART SSL SCRAPER")
    print("Finding played matches first, then scraping efficiently\n")
    
    scraper = SSLFullSeasonScraper()
    
    # Step 1: Get all match IDs
    print("STEP 1: Getting all SSL match IDs...")
    match_ids = scraper.get_all_ssl_match_ids()
    
    if not match_ids:
        print("❌ Could not get match IDs")
        return
    
    print(f"✅ Found {len(match_ids)} total matches")
    
    # Step 2: Quick scan to find played matches
    print(f"\nSTEP 2: Quick scan to identify played matches...")
    
    played_matches = []
    future_matches = []
    
    # Test every 10th match first to get a sense of the season
    sample_matches = match_ids[::10]  # Every 10th match
    print(f"📊 Sampling {len(sample_matches)} matches to estimate played vs future...")
    
    for i, match_id in enumerate(sample_matches):
        print(f"[{i+1}/{len(sample_matches)}] Checking {match_id}...", end=" ")
        
        if scraper.is_future_match(match_id):
            future_matches.append(match_id)
            print("⏳ Future")
        else:
            played_matches.append(match_id)
            print("✅ Played")
        
        time.sleep(0.2)  # Quick check
    
    # Estimate played matches
    played_ratio = len(played_matches) / len(sample_matches) if sample_matches else 0
    estimated_played = int(len(match_ids) * played_ratio)
    
    print(f"\n📈 Sample results:")
    print(f"  Played: {len(played_matches)}/{len(sample_matches)} ({played_ratio*100:.1f}%)")
    print(f"  Estimated total played matches: ~{estimated_played}")
    
    if estimated_played == 0:
        print("❌ No played matches found in sample. Season may not have started yet.")
        return
    
    # Step 3: Find the boundary between played and future matches
    print(f"\nSTEP 3: Finding boundary between played and future matches...")
    
    # Binary search approach to find the last played match
    start_idx = 0
    end_idx = len(match_ids) - 1
    last_played_idx = -1
    
    while start_idx <= end_idx:
        mid_idx = (start_idx + end_idx) // 2
        match_id = match_ids[mid_idx]
        
        print(f"Checking boundary at index {mid_idx} (match {match_id})...", end=" ")
        
        if scraper.is_future_match(match_id):
            print("⏳ Future")
            end_idx = mid_idx - 1
        else:
            print("✅ Played")
            last_played_idx = mid_idx
            start_idx = mid_idx + 1
        
        time.sleep(0.2)
    
    if last_played_idx >= 0:
        played_match_ids = match_ids[:last_played_idx + 1]
        print(f"✅ Found {len(played_match_ids)} played matches (up to index {last_played_idx})")
    else:
        print("❌ Could not determine played matches boundary")
        return
    
    # Step 4: Scrape only the played matches
    print(f"\nSTEP 4: Scraping {len(played_match_ids)} played matches...")
    
    scraper.all_match_ids = played_match_ids  # Override with only played matches
    matches = scraper.scrape_all_ssl_matches(delay=0.8)  # Slightly faster since we know they're played
    
    if matches:
        # Step 5: Save and analyze
        print(f"\nSTEP 5: Saving data and running analysis...")
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        matches_file, penalties_file, summary_file = scraper.save_comprehensive_data(matches, timestamp)
        
        # Run analysis
        report_file, data_file = scraper.run_full_analysis(matches_file, penalties_file)
        
        print(f"\n" + "=" * 80)
        print("🎉 SMART SSL SCRAPING COMPLETED!")
        print("=" * 80)
        print(f"📊 Results:")
        print(f"  Total matches in season: {len(match_ids)}")
        print(f"  Played matches scraped: {len(matches)}")
        print(f"  Success rate: {len(matches)/len(played_match_ids)*100:.1f}%")
        print(f"  Total penalties analyzed: {sum(len(m.penalties) for m in matches)}")
        print(f"  Unique referees: {len(set([m.referee1.id for m in matches] + [m.referee2.id for m in matches]))}")
        
        print(f"\n📁 Generated files:")
        print(f"  📊 {matches_file}")
        print(f"  ⚠️ {penalties_file}")
        print(f"  📈 {summary_file}")
        print(f"  📋 {report_file}")
        print(f"  📈 {data_file}")
        
        return matches_file, report_file
    
    else:
        print("❌ No matches were successfully scraped")
        return None, None

if __name__ == "__main__":
    try:
        matches_file, report_file = smart_scrape_ssl()
        
        if report_file:
            print(f"\n🔍 Quick preview of referee analysis:")
            with open(report_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # Show first 30 lines of the report
                for line in lines[:30]:
                    print(line.rstrip())
                if len(lines) > 30:
                    print(f"... (showing first 30 lines of {len(lines)} total)")
        
    except KeyboardInterrupt:
        print(f"\n⚠️ Scraping interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()