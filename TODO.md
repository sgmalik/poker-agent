# Poker Coach Agent - TODO List

> **Status**: Phase 1 - CLI Development
> **Last Updated**: 2025-12-25

## Phase 1: Core Engine & CLI

### 🔴 Critical Path (Build in Order)

- [ ] **#1: Hand Evaluator** `[CORE]`
  - [ ] Integrate treys library
  - [ ] Create HandEvaluator class
  - [ ] Parse card notation
  - [ ] Return hand rankings
  - [ ] Input validation
  - [ ] Tests (100% coverage on core logic)

- [ ] **#2: Equity Calculator (Hand vs Hand)** `[CORE]`
  - [ ] Create EquityCalculator class
  - [ ] Monte Carlo simulation
  - [ ] Handle all board states (0-5 cards)
  - [ ] Configurable iterations
  - [ ] Validate against PokerStove

- [ ] **#3: Basic CLI** `[CLI]`
  - [ ] Set up Typer framework
  - [ ] Integrate Rich for output
  - [ ] `evaluate` command
  - [ ] `equity` command
  - [ ] `info` command
  - [ ] Error handling

- [ ] **#4: Range Builder** `[CORE] [CRITICAL]`
  - [ ] Create RangeParser class
  - [ ] Parse notation (QQ+, AKs, A5s-A2s, etc.)
  - [ ] Generate combos
  - [ ] Card removal effects
  - [ ] Validate syntax
  - [ ] Tests vs GTO Wizard

- [ ] **#5: Equity Calculator (Hand vs Range)** `[CORE]`
  - [ ] Extend equity calculator for ranges
  - [ ] Weighted equity calculation
  - [ ] Performance optimization
  - [ ] Validate against solvers

### 🟡 Parallel Track (Can Build Alongside)

- [ ] **#6: Database Schema** `[DATABASE]`
  - [ ] Set up SQLAlchemy
  - [ ] Hand model
  - [ ] Session model
  - [ ] Indexes
  - [ ] Alembic migrations

- [ ] **#7: Session Tracker** `[FEATURE]`
  - [ ] SessionTracker service
  - [ ] `session start` command
  - [ ] `session end` command
  - [ ] `session history` command
  - [ ] `bankroll stats` command
  - [ ] Bankroll calculations

- [ ] **#8: Advanced Hand Analysis** `[FEATURE]`
  - [ ] Pot odds calculator
  - [ ] Implied odds calculator
  - [ ] SPR calculator
  - [ ] Position advice
  - [ ] Decision recommendations
  - [ ] `analyze` command (complete analysis)

- [ ] **#9: Range Visualization** `[FEATURE]`
  - [ ] RangeVisualizer class
  - [ ] 13x13 ASCII matrix
  - [ ] Color coding (Rich)
  - [ ] Combo counts
  - [ ] `range show` command

## Phase 2: AI & Advanced Features

### 🟢 AI Integration

- [ ] **#12: AI Coach** `[AI]`
  - [ ] PokerCoach class
  - [ ] Anthropic API integration
  - [ ] Prompt engineering
  - [ ] Context preparation (use local calculations)
  - [ ] Cost controls (token counting)
  - [ ] `coach` command
  - [ ] `--no-llm` flag for free tier

- [ ] **#11: Hand History Parser** `[FEATURE]`
  - [ ] HandHistoryParser class
  - [ ] PokerStars format
  - [ ] Manual entry format
  - [ ] Extract positions, actions, board
  - [ ] `parse` command

- [ ] **#13: Hand Review System** `[FEATURE]`
  - [ ] Integrate parser + analysis + AI
  - [ ] `review` command
  - [ ] Store reviews in database
  - [ ] Export reports
  - [ ] Track leaks over time

### 🔵 Study Tools

- [ ] **#10: Quiz System** `[FEATURE]`
  - [ ] Quiz database schema
  - [ ] Question types (range, action, equity)
  - [ ] `quiz start` command
  - [ ] Track performance
  - [ ] Spaced repetition
  - [ ] Explanations

## Milestones

### ✅ Milestone 1: Core Engine (MVP)
- [ ] Hand Evaluator (#1)
- [ ] Basic Equity Calculator (#2)
- [ ] Basic CLI (#3)
- **Goal**: Working poker calculator

### ⏳ Milestone 2: Ranges Unlock
- [ ] Range Builder (#4)
- [ ] Hand vs Range Equity (#5)
- [ ] Range Visualization (#9)
- **Goal**: Range-based analysis

### ⏳ Milestone 3: Practical Features
- [ ] Database Schema (#6)
- [ ] Session Tracker (#7)
- [ ] Advanced Analysis (#8)
- **Goal**: Usable study tool

### ⏳ Milestone 4: AI & Review
- [ ] Hand History Parser (#11)
- [ ] AI Coach (#12)
- [ ] Hand Review (#13)
- **Goal**: Complete coaching platform

### ⏳ Milestone 5: Study Tools
- [ ] Quiz System (#10)
- **Goal**: Interactive learning

## Current Sprint

**Focus**: Milestone 1 - Core Engine

**Active Tasks**:
1. Set up project dependencies
2. Implement Hand Evaluator
3. Build basic equity calculator

**Next Up**:
- Basic CLI commands
- Range builder foundation

## Dependencies to Install

### Phase 1
```txt
treys==0.1.8
typer==0.9.0
rich==13.7.0
pytest==7.4.3
pytest-cov==4.1.0
black==23.12.1
ruff==0.1.9
pyrefly==0.1.0
sqlalchemy==2.0.23
alembic==1.13.1
```

### Phase 2
```txt
anthropic==0.8.1
python-dotenv==1.0.0
```

## Notes

- Build ranges (#4) before advanced features - unlocks everything
- Session tracker (#7) can be built in parallel with poker logic
- Test all poker calculations against known results (PokerStove, GTO Wizard)
- Keep LLM optional to minimize costs
- Focus on local calculations first (free, fast, testable)

## GitHub Issues

All items have corresponding GitHub issues. See `.github/ISSUES_TEMPLATE.md` for full issue descriptions to copy into GitHub.

**To create issues**:
1. Go to repository on GitHub
2. Issues tab
3. Create new issue for each item from template
4. Add appropriate labels
5. Assign to milestones

## Progress Tracker

**Phase 1**: 0/9 features complete (0%)
**Phase 2**: 0/4 features complete (0%)
**Overall**: 0/13 features complete (0%)

---

**Last Updated**: 2025-12-25
**Current Focus**: Setting up core hand evaluator
