# 🏒 SSL Referee Bias Analysis System

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](CONTRIBUTING.md)

A comprehensive system for analyzing referee behavioral patterns in Swedish Floorball (SSL) to identify potential biases in officiating and promote transparency in the sport.

## 🏒 Overview

This system scrapes match data from SSL games and analyzes referee decision-making patterns to detect:
- Home/away penalty bias
- Penalty calling rate variations
- Score situation bias (game management)
- Timing patterns in penalty calls
- Penalty type preferences

## 📁 Project Structure

```
domarkollen/
├── .kiro/specs/referee-bias-analysis/    # Project specifications
│   ├── requirements.md                   # System requirements
│   ├── design.md                        # Technical design
│   └── tasks.md                         # Implementation tasks
├── ssl_production_scraper.py            # Main data scraper
├── referee_bias_analyzer.py             # Analysis engine
├── ssl_api_solution.json               # API access configuration
├── ssl_matches.csv                      # Match data (generated)
├── ssl_penalties.csv                    # Penalty data (generated)
└── venv/                               # Python virtual environment
```

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies (already installed)
pip install requests pandas numpy selenium beautifulsoup4
```

### 2. Scrape SSL Data
```bash
# Run the production scraper
python ssl_production_scraper.py
```

### 3. Analyze Referee Bias
```bash
# Generate bias analysis report
python referee_bias_analyzer.py
```

## 📊 Output Files

### Data Files
- `ssl_matches.csv` - Match-level data with referee assignments
- `ssl_penalties.csv` - Detailed penalty data with timing and context

### Analysis Files
- `referee_bias_report.txt` - Human-readable analysis report
- `referee_analysis.json` - Detailed statistical data

## 🔍 Analysis Features

### Bias Detection Types
1. **Home/Away Bias** - Statistical deviation from league average penalty distribution
2. **Penalty Rate Analysis** - Identifies unusually strict or lenient referees
3. **Score Situation Bias** - Detects "game management" patterns
4. **Timing Patterns** - Analyzes when penalties are called during games
5. **Penalty Type Preferences** - Identifies referee specializations

### Statistical Validation
- Only flags statistically significant deviations
- Includes confidence levels and sample sizes
- Severity classification (LOW/MEDIUM/HIGH/CRITICAL)

## 🏒 Example Output

```
👨‍⚖️ PATRIC TERELIUS (ID: 3262)
------------------------------------------------------------
  Matches officiated: 15
  Total penalties called: 98
  Average per match: 6.5
  Home penalty bias: +23.4%

  🔍 INTERESTING OBSERVATIONS:
    🟠 MEDIUM: Shows significant bias AGAINST home team - calls 15.2% more penalties than league average
    🟡 LOW: Tends to call more penalties in final period (45.2%) - possible 'late game management'
```

## 🛠️ Technical Details

### API Access
- Uses reverse-engineered API calls to `api.innebandy.se`
- Includes proper authentication headers and cookies
- Rate-limited to respect server resources

### Data Structure
- Comprehensive match and penalty data extraction
- Game situation context (score, time, period)
- Referee assignment tracking
- Statistical analysis ready format

## 📈 Future Enhancements

- Scale to all 182 SSL matches per season
- Historical trend analysis across multiple seasons
- Team-specific referee matchup analysis
- Predictive modeling for penalty patterns
- Web dashboard for interactive analysis

## 🔧 Development

This project follows spec-driven development methodology:
1. **Requirements** - Detailed user stories and acceptance criteria
2. **Design** - Technical architecture and data models  
3. **Tasks** - Implementation plan with clear deliverables

See `.kiro/specs/referee-bias-analysis/` for complete specifications.

## ⚖️ Ethical Use

This system is designed for:
- Statistical analysis and research
- Improving officiating consistency
- Educational purposes
- Supporting referee development

**Not intended for:**
- Personal attacks on referees
- Gambling or betting purposes
- Undermining the integrity of the sport

All analysis is based on publicly available match data and statistical methods.

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to help improve this project.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌟 Acknowledgments

- Swedish Floorball Federation for providing public match data
- SSL referees who make the sport possible
- The floorball community for supporting transparency in officiating

## 📊 Website

Visit our website for interactive analysis and latest findings: [Coming Soon]

## 🐛 Issues & Support

Found a bug or have a suggestion? Please [open an issue](../../issues) on GitHub.