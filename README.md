<a id="readme-top"></a>

<!-- PROJECT SHIELDS -->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![LinkedIn][linkedin-shield]][linkedin-url]



<!-- PROJECT LOGO -->
<br />
<div align="center">
  <h1>Poker Coach Agent</h1>

  <p align="center">
    An AI-powered poker coaching and study platform with TUI interface
    <br />
    <a href="https://github.com/sgmalik/poker-agent"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/sgmalik/poker-agent/issues/new?labels=bug">Report Bug</a>
    &middot;
    <a href="https://github.com/sgmalik/poker-agent/issues/new?labels=enhancement">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#features">Features</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

Poker Coach Agent is a comprehensive poker study tool featuring AI-powered hand analysis, range exploration, quiz-based learning, and bankroll management. Built as a **TUI (Text User Interface)** application where each mode is both a standalone tool and an AI agent tool.

**Key Capabilities:**
- **Hand Analysis**: Evaluate hand strength, equity, pot odds, SPR, and EV with detailed recommendations
- **Range Tools**: Visualize GTO preflop ranges with interactive 13x13 matrix display
- **Quiz System**: 216 scenario-based questions across 7 topics to test and improve your skills
- **Session Tracking**: Monitor results, variance, and bankroll with graphs and analytics
- **Hand History**: Store, tag, and analyze your played hands for pattern recognition
- **AI Coaching**: Chat with an AI coach that has access to all tools and your personal data

<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

* [![Python][Python]][Python-url]
* [![Anthropic][Anthropic]][Anthropic-url]
* [![LangChain][LangChain]][LangChain-url]
* [![SQLite][SQLite]][SQLite-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

### Prerequisites

- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- Git
- Anthropic API key (for AI Coach mode)

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/sgmalik/poker-agent.git
   cd poker-agent
   ```

2. Install dependencies with uv
   ```sh
   uv sync
   ```

3. Set up environment variables
   ```sh
   cp .env.example .env
   ```

4. Add your Anthropic API key to `.env`
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

Run the TUI application:
```sh
uv run python -m src.tui.app
```

### Application Modes

| Mode | Description |
|------|-------------|
| **1. Hand Evaluator** | Analyze hand strength, equity, pot odds, EV, and get recommendations |
| **2. Range Tools** | Explore GTO preflop ranges with visual 13x13 matrix |
| **3. Quiz System** | Test your knowledge with 216 scenario-based questions |
| **4. Session Tracker** | Log sessions and track bankroll with graphs |
| **5. Hand History** | Store, tag, and analyze your hands |
| **6. AI Agent Coach** | Chat with an AI coach that uses all tools |
| **7. Admin Dashboard** | View and manage raw database tables |

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- FEATURES -->
## Features

### Phase 1: TUI Application (Complete)
- [x] Core poker engine (hand evaluation, equity, outs, pot odds)
- [x] Mode 1: Hand Evaluator & Spot Analyzer
- [x] Mode 2: Range Tools (GTO charts, 13x13 matrix visualization)
- [x] Mode 3: Quiz System (216 questions, 7 topics, database persistence)
- [x] Mode 4: Session Tracker (bankroll graphs, stats dashboard)
- [x] Mode 5: Hand History Manager (tagging, search, pattern analysis)
- [x] Mode 6: AI Agent Coach (LangChain integration, 17 tools)
- [x] Mode 7: Admin Dashboard (view/manage database tables)
- [x] Centralized configuration (`src/config.py`)
- [x] 415+ tests passing

### Quiz Bank Stats
- **216 total questions** focused on situational scenarios
- **Topics**: postflop (85), preflop (35), ranges (24), hand_strength (22), game_theory (18), pot_odds (17), position (15)
- **Difficulty**: beginner (17), intermediate (44), advanced (99), elite (56)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

- [x] Core TUI application with all 7 modes
- [x] AI coaching integration with LangChain
- [x] Quiz question expansion (216 situational scenarios)
- [x] Agent tools for quiz creation and leak identification
- [ ] Range-based equity calculator
- [ ] Mixed frequency hands with hover tooltips
- [ ] Spaced repetition for quiz system
- [ ] Hand history import (PokerStars, GGPoker formats)

See the [open issues](https://github.com/sgmalik/poker-agent/issues) for a full list of proposed features and known issues.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Run quality checks (`uv run black . && uv run ruff check . && uv run pytest`)
4. Commit your Changes (`git commit -m 'feat: add AmazingFeature'`)
5. Push to the Branch (`git push origin feature/AmazingFeature`)
6. Open a Pull Request

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on code style, testing requirements, and development workflow.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Surya Malik - [@sgmalik](https://github.com/sgmalik) - malik.g.surya@gmail.com

Project Link: [https://github.com/sgmalik/poker-agent](https://github.com/sgmalik/poker-agent)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* [Textual](https://textual.textualize.io/) - TUI framework
* [treys](https://github.com/ihendley/treys) - Poker hand evaluation
* [LangChain](https://python.langchain.com/) - Agent framework
* [Anthropic Claude](https://www.anthropic.com/) - AI coaching
* GTO Wizard, Run It Once, Two Plus Two - Poker strategy resources

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- PROJECT INFO -->
## Project Info

**Current Phase**: Phase 1 Complete - All 7 Modes + Quiz Expansion
**Last Updated**: January 30, 2026
**Version**: 0.2.0-alpha



<!-- MARKDOWN LINKS & IMAGES -->
[contributors-shield]: https://img.shields.io/github/contributors/sgmalik/poker-agent.svg?style=for-the-badge
[contributors-url]: https://github.com/sgmalik/poker-agent/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/sgmalik/poker-agent.svg?style=for-the-badge
[forks-url]: https://github.com/sgmalik/poker-agent/network/members
[stars-shield]: https://img.shields.io/github/stars/sgmalik/poker-agent.svg?style=for-the-badge
[stars-url]: https://github.com/sgmalik/poker-agent/stargazers
[issues-shield]: https://img.shields.io/github/issues/sgmalik/poker-agent.svg?style=for-the-badge
[issues-url]: https://github.com/sgmalik/poker-agent/issues
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/suryamalik
[Python]: https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white
[Python-url]: https://python.org
[Anthropic]: https://img.shields.io/badge/Anthropic-191919?style=for-the-badge&logo=anthropic&logoColor=white
[Anthropic-url]: https://anthropic.com
[LangChain]: https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white
[LangChain-url]: https://langchain.com
[SQLite]: https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white
[SQLite-url]: https://sqlite.org
