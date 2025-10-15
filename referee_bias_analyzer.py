#!/usr/bin/env python3
"""
Referee Bias Analyzer
Generates "Interesting Observations" for all games and referees
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict
import json

@dataclass
class BiasObservation:
    referee_name: str
    referee_id: int
    observation_type: str
    description: str
    severity: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    statistical_evidence: Dict
    matches_involved: List[int]

@dataclass
class RefereeProfile:
    referee_id: int
    referee_name: str
    total_matches: int
    total_penalties: int
    avg_penalties_per_match: float
    home_penalty_bias: float
    timing_patterns: Dict
    penalty_type_preferences: Dict
    score_situation_bias: Dict
    observations: List[BiasObservation]

class RefereeBiasAnalyzer:
    def __init__(self, matches_csv: str, penalties_csv: str):
        self.matches_df = pd.read_csv(matches_csv)
        self.penalties_df = pd.read_csv(penalties_csv)
        self.referee_profiles = {}
        self.league_averages = {}
        
        print(f"📊 Loaded {len(self.matches_df)} matches and {len(self.penalties_df)} penalties")
        self.calculate_league_averages()
    
    def calculate_league_averages(self):
        """Calculate league-wide averages for comparison"""
        self.league_averages = {
            'avg_penalties_per_match': self.penalties_df.groupby('match_id').size().mean(),
            'home_penalty_percentage': (self.penalties_df['is_home_team'].sum() / len(self.penalties_df)) * 100,
            'avg_penalties_per_period': self.penalties_df.groupby('period').size().mean(),
            'most_common_penalty_types': self.penalties_df['penalty_type'].value_counts().head(5).to_dict()
        }
        
        print(f"🏒 League averages calculated:")
        print(f"  Average penalties per match: {self.league_averages['avg_penalties_per_match']:.1f}")
        print(f"  Home team penalty rate: {self.league_averages['home_penalty_percentage']:.1f}%")
    
    def analyze_referee(self, referee_id: int, referee_name: str) -> RefereeProfile:
        """Comprehensive analysis of a single referee"""
        
        # Get all matches and penalties for this referee
        ref_matches = self.matches_df[
            (self.matches_df['referee1_id'] == referee_id) | 
            (self.matches_df['referee2_id'] == referee_id)
        ]
        
        ref_penalties = self.penalties_df[
            (self.penalties_df['referee1_id'] == referee_id) | 
            (self.penalties_df['referee2_id'] == referee_id)
        ]
        
        if len(ref_matches) == 0:
            return None
        
        # Basic stats
        total_matches = len(ref_matches)
        total_penalties = len(ref_penalties)
        avg_penalties = total_penalties / total_matches if total_matches > 0 else 0
        
        # Home/away bias
        home_penalties = len(ref_penalties[ref_penalties['is_home_team'] == True])
        away_penalties = len(ref_penalties[ref_penalties['is_home_team'] == False])
        home_bias = (home_penalties - away_penalties) / total_penalties * 100 if total_penalties > 0 else 0
        
        # Timing patterns
        timing_patterns = self.analyze_timing_patterns(ref_penalties)
        
        # Penalty type preferences
        penalty_types = ref_penalties['penalty_type'].value_counts().to_dict()
        
        # Score situation bias
        score_bias = self.analyze_score_situation_bias(ref_penalties)
        
        # Generate observations
        observations = self.generate_observations(referee_id, referee_name, ref_matches, ref_penalties)
        
        profile = RefereeProfile(
            referee_id=referee_id,
            referee_name=referee_name,
            total_matches=total_matches,
            total_penalties=total_penalties,
            avg_penalties_per_match=avg_penalties,
            home_penalty_bias=home_bias,
            timing_patterns=timing_patterns,
            penalty_type_preferences=penalty_types,
            score_situation_bias=score_bias,
            observations=observations
        )
        
        return profile
    
    def analyze_timing_patterns(self, ref_penalties: pd.DataFrame) -> Dict:
        """Analyze when referee calls penalties during games"""
        if len(ref_penalties) == 0:
            return {}
        
        # Period distribution
        period_dist = ref_penalties['period'].value_counts().to_dict()
        
        # Time within periods (early vs late)
        ref_penalties['time_in_period'] = ref_penalties['minute'] + ref_penalties['second'] / 60
        
        # Classify as early (0-7 min), middle (7-13 min), late (13-20 min)
        def classify_time(time_val):
            if time_val < 7:
                return 'early'
            elif time_val < 13:
                return 'middle'
            else:
                return 'late'
        
        ref_penalties['time_category'] = ref_penalties['time_in_period'].apply(classify_time)
        time_dist = ref_penalties['time_category'].value_counts().to_dict()
        
        return {
            'period_distribution': period_dist,
            'time_distribution': time_dist,
            'avg_penalty_time': ref_penalties['time_in_period'].mean()
        }
    
    def analyze_score_situation_bias(self, ref_penalties: pd.DataFrame) -> Dict:
        """Analyze penalty calling based on score situations"""
        if len(ref_penalties) == 0:
            return {}
        
        # Classify score situations
        def classify_score_situation(score_diff):
            if abs(score_diff) <= 1:
                return 'close_game'
            elif abs(score_diff) <= 3:
                return 'moderate_lead'
            else:
                return 'blowout'
        
        ref_penalties['score_situation'] = ref_penalties['score_diff_at_time'].apply(classify_score_situation)
        
        # Analyze penalties by score situation
        situation_dist = ref_penalties['score_situation'].value_counts().to_dict()
        
        # Analyze penalties when team is leading vs trailing
        ref_penalties['team_situation'] = ref_penalties.apply(
            lambda row: 'leading' if (row['is_home_team'] and row['score_diff_at_time'] > 0) or 
                                   (not row['is_home_team'] and row['score_diff_at_time'] < 0)
                        else 'trailing' if (row['is_home_team'] and row['score_diff_at_time'] < 0) or 
                                         (not row['is_home_team'] and row['score_diff_at_time'] > 0)
                        else 'tied', axis=1
        )
        
        team_situation_dist = ref_penalties['team_situation'].value_counts().to_dict()
        
        return {
            'score_situation_distribution': situation_dist,
            'team_situation_distribution': team_situation_dist
        }
    
    def generate_observations(self, referee_id: int, referee_name: str, 
                            ref_matches: pd.DataFrame, ref_penalties: pd.DataFrame) -> List[BiasObservation]:
        """Generate interesting observations about referee behavior"""
        observations = []
        
        if len(ref_penalties) == 0:
            return observations
        
        # 1. Home/Away Bias Analysis
        home_penalties = len(ref_penalties[ref_penalties['is_home_team'] == True])
        away_penalties = len(ref_penalties[ref_penalties['is_home_team'] == False])
        total_penalties = len(ref_penalties)
        
        if total_penalties > 5:  # Only analyze if sufficient data
            home_percentage = (home_penalties / total_penalties) * 100
            league_home_avg = self.league_averages['home_penalty_percentage']
            
            bias_diff = home_percentage - league_home_avg
            
            if abs(bias_diff) > 15:  # Significant deviation
                severity = "HIGH" if abs(bias_diff) > 25 else "MEDIUM"
                bias_type = "home team" if bias_diff > 0 else "away team"
                
                observations.append(BiasObservation(
                    referee_name=referee_name,
                    referee_id=referee_id,
                    observation_type="HOME_AWAY_BIAS",
                    description=f"Shows significant bias AGAINST {bias_type} - calls {abs(bias_diff):.1f}% more penalties than league average",
                    severity=severity,
                    statistical_evidence={
                        'referee_home_penalty_rate': home_percentage,
                        'league_average': league_home_avg,
                        'deviation': bias_diff,
                        'sample_size': total_penalties
                    },
                    matches_involved=ref_matches['match_id'].tolist()
                ))
        
        # 2. Penalty Rate Analysis
        avg_penalties = total_penalties / len(ref_matches)
        league_avg = self.league_averages['avg_penalties_per_match']
        
        if abs(avg_penalties - league_avg) > 2:  # Significant deviation
            severity = "HIGH" if abs(avg_penalties - league_avg) > 4 else "MEDIUM"
            tendency = "strict" if avg_penalties > league_avg else "lenient"
            
            observations.append(BiasObservation(
                referee_name=referee_name,
                referee_id=referee_id,
                observation_type="PENALTY_RATE",
                description=f"Unusually {tendency} referee - calls {avg_penalties:.1f} penalties per match vs league average of {league_avg:.1f}",
                severity=severity,
                statistical_evidence={
                    'referee_avg': avg_penalties,
                    'league_average': league_avg,
                    'deviation': avg_penalties - league_avg,
                    'matches': len(ref_matches)
                },
                matches_involved=ref_matches['match_id'].tolist()
            ))
        
        # 3. Score Situation Bias
        if 'score_situation' in ref_penalties.columns:
            blowout_penalties = len(ref_penalties[ref_penalties['score_situation'] == 'blowout'])
            close_penalties = len(ref_penalties[ref_penalties['score_situation'] == 'close_game'])
            
            if total_penalties > 10:
                blowout_rate = blowout_penalties / total_penalties
                close_rate = close_penalties / total_penalties
                
                if blowout_rate > 0.6:  # More than 60% of penalties in blowouts
                    observations.append(BiasObservation(
                        referee_name=referee_name,
                        referee_id=referee_id,
                        observation_type="SCORE_SITUATION_BIAS",
                        description=f"Tends to call more penalties in blowout games ({blowout_rate*100:.1f}% of penalties) - possible 'game management' style",
                        severity="MEDIUM",
                        statistical_evidence={
                            'blowout_penalty_rate': blowout_rate,
                            'close_game_penalty_rate': close_rate,
                            'total_penalties': total_penalties
                        },
                        matches_involved=ref_matches['match_id'].tolist()
                    ))
        
        # 4. Timing Pattern Analysis
        if len(ref_penalties) > 8:
            period_3_penalties = len(ref_penalties[ref_penalties['period'] == 3])
            period_3_rate = period_3_penalties / total_penalties
            
            if period_3_rate > 0.5:  # More than 50% in final period
                observations.append(BiasObservation(
                    referee_name=referee_name,
                    referee_id=referee_id,
                    observation_type="TIMING_PATTERN",
                    description=f"Calls disproportionate number of penalties in final period ({period_3_rate*100:.1f}%) - possible 'late game management'",
                    severity="MEDIUM",
                    statistical_evidence={
                        'period_3_rate': period_3_rate,
                        'period_3_count': period_3_penalties,
                        'total_penalties': total_penalties
                    },
                    matches_involved=ref_matches['match_id'].tolist()
                ))
        
        # 5. Penalty Type Specialization
        penalty_types = ref_penalties['penalty_type'].value_counts()
        if len(penalty_types) > 0:
            most_common = penalty_types.iloc[0]
            most_common_type = penalty_types.index[0]
            
            if most_common / total_penalties > 0.4:  # More than 40% of one type
                observations.append(BiasObservation(
                    referee_name=referee_name,
                    referee_id=referee_id,
                    observation_type="PENALTY_TYPE_BIAS",
                    description=f"Shows strong preference for calling '{most_common_type}' ({most_common}/{total_penalties} penalties, {most_common/total_penalties*100:.1f}%)",
                    severity="LOW",
                    statistical_evidence={
                        'preferred_penalty': most_common_type,
                        'count': most_common,
                        'percentage': most_common/total_penalties*100,
                        'total_penalties': total_penalties
                    },
                    matches_involved=ref_matches['match_id'].tolist()
                ))
        
        return observations
    
    def analyze_all_referees(self) -> Dict[int, RefereeProfile]:
        """Analyze all referees in the dataset"""
        print(f"\n🔍 Analyzing all referees...")
        
        # Get unique referees
        ref1_data = self.matches_df[['referee1_id', 'referee1_name']].rename(columns={'referee1_id': 'id', 'referee1_name': 'name'})
        ref2_data = self.matches_df[['referee2_id', 'referee2_name']].rename(columns={'referee2_id': 'id', 'referee2_name': 'name'})
        
        all_refs = pd.concat([ref1_data, ref2_data]).drop_duplicates()
        all_refs = all_refs[all_refs['id'] != 0]  # Remove empty referee entries
        
        profiles = {}
        
        for _, ref_row in all_refs.iterrows():
            ref_id = ref_row['id']
            ref_name = ref_row['name']
            
            print(f"  Analyzing {ref_name} (ID: {ref_id})...")
            
            profile = self.analyze_referee(ref_id, ref_name)
            if profile:
                profiles[ref_id] = profile
        
        print(f"✅ Analyzed {len(profiles)} referees")
        return profiles
    
    def generate_comprehensive_report(self, profiles: Dict[int, RefereeProfile]) -> str:
        """Generate a comprehensive report with all interesting observations"""
        report = []
        report.append("=" * 80)
        report.append("🏒 SSL REFEREE BIAS ANALYSIS REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Summary statistics
        total_refs = len(profiles)
        total_observations = sum(len(p.observations) for p in profiles.values())
        high_severity = sum(1 for p in profiles.values() for obs in p.observations if obs.severity == "HIGH")
        
        report.append(f"📊 SUMMARY:")
        report.append(f"  Referees analyzed: {total_refs}")
        report.append(f"  Total observations: {total_observations}")
        report.append(f"  High severity issues: {high_severity}")
        report.append("")
        
        # League averages
        report.append(f"🏒 LEAGUE AVERAGES:")
        report.append(f"  Average penalties per match: {self.league_averages['avg_penalties_per_match']:.1f}")
        report.append(f"  Home team penalty rate: {self.league_averages['home_penalty_percentage']:.1f}%")
        report.append("")
        
        # Individual referee reports
        for ref_id, profile in sorted(profiles.items(), key=lambda x: len(x[1].observations), reverse=True):
            if len(profile.observations) > 0:
                report.append(f"👨‍⚖️ {profile.referee_name.upper()} (ID: {profile.referee_id})")
                report.append("-" * 60)
                report.append(f"  Matches officiated: {profile.total_matches}")
                report.append(f"  Total penalties called: {profile.total_penalties}")
                report.append(f"  Average per match: {profile.avg_penalties_per_match:.1f}")
                report.append(f"  Home penalty bias: {profile.home_penalty_bias:+.1f}%")
                report.append("")
                
                report.append("  🔍 INTERESTING OBSERVATIONS:")
                for obs in profile.observations:
                    severity_emoji = {"LOW": "🟡", "MEDIUM": "🟠", "HIGH": "🔴", "CRITICAL": "⚠️"}
                    report.append(f"    {severity_emoji.get(obs.severity, '🔵')} {obs.severity}: {obs.description}")
                
                report.append("")
        
        return "\n".join(report)
    
    def save_detailed_analysis(self, profiles: Dict[int, RefereeProfile], filename: str = "referee_analysis.json"):
        """Save detailed analysis to JSON for further processing"""
        analysis_data = {}
        
        for ref_id, profile in profiles.items():
            analysis_data[ref_id] = {
                'referee_name': profile.referee_name,
                'basic_stats': {
                    'total_matches': profile.total_matches,
                    'total_penalties': profile.total_penalties,
                    'avg_penalties_per_match': profile.avg_penalties_per_match,
                    'home_penalty_bias': profile.home_penalty_bias
                },
                'timing_patterns': profile.timing_patterns,
                'penalty_type_preferences': profile.penalty_type_preferences,
                'score_situation_bias': profile.score_situation_bias,
                'observations': [
                    {
                        'type': obs.observation_type,
                        'description': obs.description,
                        'severity': obs.severity,
                        'evidence': obs.statistical_evidence,
                        'matches': obs.matches_involved
                    }
                    for obs in profile.observations
                ]
            }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"💾 Detailed analysis saved to {filename}")

def main():
    """Main analysis process"""
    print("=== REFEREE BIAS ANALYZER ===")
    print("Generating 'Interesting Observations' for all referees\n")
    
    try:
        # Initialize analyzer
        analyzer = RefereeBiasAnalyzer('ssl_matches.csv', 'ssl_penalties.csv')
        
        # Analyze all referees
        profiles = analyzer.analyze_all_referees()
        
        # Generate comprehensive report
        report = analyzer.generate_comprehensive_report(profiles)
        
        # Save report
        with open('referee_bias_report.txt', 'w', encoding='utf-8') as f:
            f.write(report)
        
        # Save detailed analysis
        analyzer.save_detailed_analysis(profiles)
        
        # Print report to console
        print(report)
        
        print(f"\n📁 Files generated:")
        print(f"  - referee_bias_report.txt (human-readable report)")
        print(f"  - referee_analysis.json (detailed data)")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()