#!/usr/bin/env python3
"""
SSL Production Scraper
Scalable scraper for all SSL matches with referee bias analysis focus
"""

import requests
import json
import time
import csv
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import os

@dataclass
class RefereeInfo:
    id: int
    name: str

@dataclass
class TeamInfo:
    id: int
    name: str
    short_name: str

@dataclass
class PenaltyInfo:
    player_name: str
    team_name: str
    is_home_team: bool
    penalty_type: str
    penalty_code: str
    period: int
    minute: int
    second: int
    home_goals_at_time: int
    away_goals_at_time: int

@dataclass
class MatchInfo:
    match_id: int
    date: str
    home_team: TeamInfo
    away_team: TeamInfo
    venue: str
    referee1: RefereeInfo
    referee2: RefereeInfo
    home_goals: int
    away_goals: int
    penalties: List[PenaltyInfo]
    total_events: int
    spectators: int

class SSLProductionScraper:
    def __init__(self):
        self.session = requests.Session()
        self.setup_session()
        self.scraped_matches = []
        self.failed_matches = []
    
    def setup_session(self):
        """Setup requests session with working headers and cookies from solution file"""
        # Load fresh API configuration
        try:
            with open('ssl_api_solution.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.session.headers.update(config['required_headers'])
            self.session.cookies.update(config['required_cookies'])
            
            print(f"✅ Loaded fresh API configuration (refreshed: {config.get('refreshed_at', 'unknown')})")
            
        except Exception as e:
            print(f"❌ Could not load API configuration: {e}")
            print(f"Run refresh_api_token.py first!")
            raise
    
    def get_all_ssl_match_ids(self) -> List[str]:
        """Get all SSL match IDs from our previous discovery"""
        # In production, this would come from the Selenium scraper
        # For now, we'll use a sample of known match IDs
        print("🔍 Getting all SSL match IDs...")
        
        # This is a placeholder - in production we'd use the Selenium scraper
        # to get all 182 match IDs from the season page
        sample_matches = [
            "1571765", "1571824", "1571825", "1571855", "1571859", 
            "1571876", "1571901", "1571822"  # Add more as needed
        ]
        
        print(f"📋 Found {len(sample_matches)} matches to scrape")
        return sample_matches
    
    def scrape_match(self, match_id: str) -> Optional[MatchInfo]:
        """Scrape a single match and return structured data"""
        url = f"https://api.innebandy.se/v2/api/matches/{match_id}"
        
        try:
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                print(f"❌ Match {match_id}: HTTP {response.status_code}")
                return None
            
            data = response.json()
            
            # Check if match has been played (has referee data)
            if not data.get('Referee1') or not data.get('Referee2'):
                print(f"⏳ Match {match_id}: Not played yet or no referee data")
                return None
            
            # Extract match info
            match_info = MatchInfo(
                match_id=int(match_id),
                date=data.get('MatchDateTime', ''),
                home_team=TeamInfo(
                    id=data.get('HomeTeamID', 0),
                    name=data.get('HomeTeam', ''),
                    short_name=data.get('HomeTeamShortName', '')
                ),
                away_team=TeamInfo(
                    id=data.get('AwayTeamID', 0),
                    name=data.get('AwayTeam', ''),
                    short_name=data.get('AwayTeamShortName', '')
                ),
                venue=data.get('Venue', ''),
                referee1=RefereeInfo(
                    id=data.get('Referee1ID', 0),
                    name=data.get('Referee1', '')
                ),
                referee2=RefereeInfo(
                    id=data.get('Referee2ID', 0),
                    name=data.get('Referee2', '')
                ),
                home_goals=data.get('GoalsHomeTeam', 0),
                away_goals=data.get('GoalsAwayTeam', 0),
                penalties=[],
                total_events=len(data.get('Events', [])),
                spectators=data.get('Spectators', 0)
            )
            
            # Extract penalties
            events = data.get('Events', [])
            for event in events:
                if event.get('MatchEventType') == 'Utvisning':
                    penalty = PenaltyInfo(
                        player_name=event.get('PlayerName', ''),
                        team_name=event.get('MatchTeamName', ''),
                        is_home_team=event.get('IsHomeTeam', False),
                        penalty_type=event.get('PenaltyName', ''),
                        penalty_code=event.get('PenaltyCode', ''),
                        period=event.get('Period', 0),
                        minute=event.get('Minute', 0),
                        second=event.get('Second', 0),
                        home_goals_at_time=event.get('GoalsHomeTeam', 0),
                        away_goals_at_time=event.get('GoalsAwayTeam', 0)
                    )
                    match_info.penalties.append(penalty)
            
            print(f"✅ Match {match_id}: {match_info.home_team.name} vs {match_info.away_team.name} "
                  f"({len(match_info.penalties)} penalties)")
            
            return match_info
            
        except Exception as e:
            print(f"❌ Match {match_id}: Error - {e}")
            return None
    
    def scrape_all_matches(self, match_ids: List[str], delay: float = 1.0) -> List[MatchInfo]:
        """Scrape all matches with rate limiting"""
        print(f"🚀 Starting to scrape {len(match_ids)} matches...")
        
        successful_matches = []
        
        for i, match_id in enumerate(match_ids):
            print(f"[{i+1}/{len(match_ids)}] Scraping match {match_id}...")
            
            match_info = self.scrape_match(match_id)
            
            if match_info:
                successful_matches.append(match_info)
                self.scraped_matches.append(match_info)
            else:
                self.failed_matches.append(match_id)
            
            # Rate limiting
            if delay > 0:
                time.sleep(delay)
        
        print(f"\n📊 Scraping completed:")
        print(f"  ✅ Successful: {len(successful_matches)}")
        print(f"  ❌ Failed: {len(self.failed_matches)}")
        
        return successful_matches
    
    def save_to_csv(self, matches: List[MatchInfo], filename: str = "ssl_matches.csv"):
        """Save match data to CSV for analysis"""
        print(f"💾 Saving {len(matches)} matches to {filename}...")
        
        # Prepare CSV data
        csv_data = []
        
        for match in matches:
            # Basic match row
            base_row = {
                'match_id': match.match_id,
                'date': match.date,
                'home_team_id': match.home_team.id,
                'home_team': match.home_team.name,
                'away_team_id': match.away_team.id,
                'away_team': match.away_team.name,
                'venue': match.venue,
                'referee1_id': match.referee1.id,
                'referee1_name': match.referee1.name,
                'referee2_id': match.referee2.id,
                'referee2_name': match.referee2.name,
                'home_goals': match.home_goals,
                'away_goals': match.away_goals,
                'total_penalties': len(match.penalties),
                'home_penalties': len([p for p in match.penalties if p.is_home_team]),
                'away_penalties': len([p for p in match.penalties if not p.is_home_team]),
                'spectators': match.spectators
            }
            
            csv_data.append(base_row)
        
        # Write CSV
        if csv_data:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=csv_data[0].keys())
                writer.writeheader()
                writer.writerows(csv_data)
            
            print(f"✅ Saved to {filename}")
    
    def save_penalties_csv(self, matches: List[MatchInfo], filename: str = "ssl_penalties.csv"):
        """Save detailed penalty data to CSV"""
        print(f"💾 Saving penalty data to {filename}...")
        
        penalty_data = []
        
        for match in matches:
            for penalty in match.penalties:
                penalty_row = {
                    'match_id': match.match_id,
                    'date': match.date,
                    'home_team': match.home_team.name,
                    'away_team': match.away_team.name,
                    'referee1_id': match.referee1.id,
                    'referee1_name': match.referee1.name,
                    'referee2_id': match.referee2.id,
                    'referee2_name': match.referee2.name,
                    'player_name': penalty.player_name,
                    'team_name': penalty.team_name,
                    'is_home_team': penalty.is_home_team,
                    'penalty_type': penalty.penalty_type,
                    'penalty_code': penalty.penalty_code,
                    'period': penalty.period,
                    'minute': penalty.minute,
                    'second': penalty.second,
                    'time_string': f"{penalty.minute:02d}:{penalty.second:02d}",
                    'home_goals_at_time': penalty.home_goals_at_time,
                    'away_goals_at_time': penalty.away_goals_at_time,
                    'score_diff_at_time': penalty.home_goals_at_time - penalty.away_goals_at_time
                }
                penalty_data.append(penalty_row)
        
        if penalty_data:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=penalty_data[0].keys())
                writer.writeheader()
                writer.writerows(penalty_data)
            
            print(f"✅ Saved {len(penalty_data)} penalties to {filename}")
    
    def generate_referee_summary(self, matches: List[MatchInfo]):
        """Generate referee statistics summary"""
        print(f"\n📈 REFEREE SUMMARY")
        print(f"=" * 50)
        
        referee_stats = {}
        
        for match in matches:
            # Count for both referees
            for ref in [match.referee1, match.referee2]:
                if ref.id not in referee_stats:
                    referee_stats[ref.id] = {
                        'name': ref.name,
                        'matches': 0,
                        'total_penalties': 0,
                        'home_penalties': 0,
                        'away_penalties': 0,
                        'penalty_types': {}
                    }
                
                stats = referee_stats[ref.id]
                stats['matches'] += 1
                stats['total_penalties'] += len(match.penalties)
                stats['home_penalties'] += len([p for p in match.penalties if p.is_home_team])
                stats['away_penalties'] += len([p for p in match.penalties if not p.is_home_team])
                
                # Count penalty types
                for penalty in match.penalties:
                    penalty_type = penalty.penalty_type
                    if penalty_type not in stats['penalty_types']:
                        stats['penalty_types'][penalty_type] = 0
                    stats['penalty_types'][penalty_type] += 1
        
        # Display top referees by matches
        sorted_refs = sorted(referee_stats.items(), key=lambda x: x[1]['matches'], reverse=True)
        
        print(f"Top referees by matches officiated:")
        for ref_id, stats in sorted_refs[:10]:
            home_bias = stats['home_penalties'] - stats['away_penalties']
            avg_penalties = stats['total_penalties'] / stats['matches'] if stats['matches'] > 0 else 0
            
            print(f"  {stats['name']:<20} | {stats['matches']:2d} matches | "
                  f"{avg_penalties:.1f} pen/match | Home bias: {home_bias:+d}")
        
        return referee_stats

def main():
    """Main scraping process"""
    print("=== SSL PRODUCTION SCRAPER ===")
    print("Scraping SSL matches for referee bias analysis\n")
    
    scraper = SSLProductionScraper()
    
    try:
        # Step 1: Get all match IDs
        match_ids = scraper.get_all_ssl_match_ids()
        
        # Step 2: Scrape all matches
        matches = scraper.scrape_all_matches(match_ids, delay=0.5)  # 0.5s delay between requests
        
        if matches:
            # Step 3: Save data
            scraper.save_to_csv(matches)
            scraper.save_penalties_csv(matches)
            
            # Step 4: Generate summary
            referee_stats = scraper.generate_referee_summary(matches)
            
            print(f"\n🎉 Scraping completed successfully!")
            print(f"📁 Data saved to:")
            print(f"  - ssl_matches.csv (match data)")
            print(f"  - ssl_penalties.csv (penalty details)")
            
            print(f"\n🔍 Ready for referee bias analysis!")
            
        else:
            print(f"❌ No matches were successfully scraped")
    
    except KeyboardInterrupt:
        print(f"\n⚠️ Scraping interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()