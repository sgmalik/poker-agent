# Poker Coach Agent - System Design Document

## Project Overview

A comprehensive poker coaching and study tool that provides hand analysis, range exploration, quiz-based learning, session tracking, and bankroll management. The system will feature an AI-powered coaching agent capable of providing personalized feedback and strategic guidance.

### Vision
Build a full-stack web application with a Python backend and TypeScript frontend that enables poker players to study and improve their game on any device (desktop, mobile, tablet). The application will start as a CLI tool for rapid development, then evolve into a professional web application.

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     User Interface Layer                 │
│  ┌──────────────┐              ┌──────────────────────┐ │
│  │  CLI (Phase 1)│              │  Next.js Web App    │ │
│  │  - Rich CLI   │              │  - TypeScript/React │ │
│  │  - Interactive│              │  - Mobile Responsive│ │
│  │  - Development│              │  - PWA Capable      │ │
│  └──────────────┘              └──────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                    API Gateway Layer                     │
│  ┌────────────────────────────────────────────────────┐ │
│  │              FastAPI Backend (Python)              │ │
│  │  - RESTful API endpoints                           │ │
│  │  - WebSocket support (real-time features)          │ │
│  │  - Authentication & authorization                  │ │
│  │  - Request validation (Pydantic)                   │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                    Application Layer                     │
│  ┌────────────────────────────────────────────────────┐ │
│  │           AI Coaching Agent (LLM-Powered)          │ │
│  │  - Natural language interaction                    │ │
│  │  - Context-aware coaching                          │ │
│  │  - Personalized recommendations                    │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │Hand Analysis │  │ Quiz Engine  │  │  Bankroll    │  │
│  │   Module     │  │              │  │  Management  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │    Range     │  │   Progress   │  │   Session    │  │
│  │  Management  │  │   Tracker    │  │   Analyzer   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                      Core Engine Layer                   │
│  ┌────────────────────────────────────────────────────┐ │
│  │              Poker Logic Engine                    │ │
│  │  - Hand evaluation (Texas Hold'em)                 │ │
│  │  - Equity calculations                             │ │
│  │  - Range computations                              │ │
│  │  - GTO principles                                  │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                      Data Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Hand History │  │    User      │  │   Preflop    │  │
│  │   Storage    │  │   Progress   │  │    Charts    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                          │
│  Phase 1: SQLite (local development)                    │
│  Phase 2: PostgreSQL (production)                       │
└─────────────────────────────────────────────────────────┘
```

### Component Architecture

#### 1. Core Poker Engine
- **Hand Evaluator**: Card ranking, winner determination
- **Equity Calculator**: Monte Carlo simulations, range vs range equity
- **Range Calculator**: Hand range manipulation, combo counting
- **GTO Solver Integration**: Basic GTO principles and heuristics

#### 2. AI Coaching Agent
- **LLM Integration**: Claude/OpenAI for natural language coaching
- **Context Management**: Maintains user history, playing style, weaknesses
- **Prompt Engineering**: Specialized prompts for different coaching scenarios
- **Knowledge Base**: Poker strategy principles, common mistakes, best practices

#### 3. Analysis Modules
- **Hand Reviewer**: Parse and analyze played hands
- **Decision Analyzer**: Evaluate individual decisions (bet sizing, line selection)
- **Spot Analyzer**: Identify common situations and optimal plays
- **Mistake Detector**: Flag suboptimal plays with explanations

#### 4. Study Tools
- **Quiz Engine**: Generate poker scenarios, validate answers, provide feedback
- **Scenario Generator**: Create realistic poker situations based on stakes/format
- **Progress Tracker**: Monitor improvement over time, identify weak areas
- **Spaced Repetition**: Review difficult concepts at optimal intervals

#### 5. Range Management
- **Range Builder**: Create and save custom ranges
- **Range Visualizer**: ASCII/text visualization (CLI), graphical grid (web)
- **Preflop Charts**: Store common preflop ranges by position/action
- **Range Analysis**: Compare user ranges to GTO/optimal ranges

#### 6. Bankroll Management
- **Session Tracker**: Log sessions (stakes, duration, profit/loss)
- **Variance Analyzer**: Calculate standard deviation, downswing analysis
- **Goal Setting**: Track progress toward bankroll goals
- **Risk of Ruin**: Calculate RoR based on win rate and bankroll

---

## Feature Deliverables

### Core Poker Engine

#### Hand Evaluation
- Parse hand strings (e.g., "AsKh", "Td9d")
- Evaluate 5-card and 7-card poker hands
- Determine hand strength and rankings
- Support for board textures and draw analysis

#### Equity Calculations
- Calculate equity for hand vs hand
- Calculate equity for hand vs range
- Calculate equity for range vs range
- Monte Carlo simulation engine
- Support for dead cards and run-it-multiple-times scenarios

#### Range Operations
- Parse range notation (e.g., "AK, QQ+, 98s+")
- Convert ranges to combinations
- Range vs range comparisons
- Range condensing and polarization analysis
- Preflop range charts by position

---

### Hand Analysis System

#### Hand History Parser
- Support multiple formats (PokerStars, GGPoker, manual entry)
- Extract key information (positions, actions, bet sizes, board)
- Normalize data into internal format
- Handle multi-way pots and complex action sequences

#### Strategic Analysis
- Evaluate each decision point (preflop, flop, turn, river)
- Compare actual play to GTO/exploitative optimal
- Analyze bet sizing (+EV sizing recommendations)
- Identify missed value or bluff opportunities
- Pot odds and implied odds calculations

#### Visualization & Reporting
- Display hand in readable format
- Highlight key decision points
- Show equity at each street
- Provide actionable recommendations
- Generate summary reports for multiple hands

---

### AI Coaching Agent

#### Conversational Interface
- Natural language hand review ("I had AK and villain 3-bet me...")
- Answer strategic questions ("What should I do with QQ vs a 4-bet?")
- Explain poker concepts (polarized ranges, blockers, etc.)
- Adaptive teaching based on user skill level

#### Coaching Capabilities
- Personalized feedback on hand histories
- Identify patterns in mistakes (e.g., "you overfold to 3-bets")
- Suggest study topics based on leaks
- Provide mental game advice
- Track user preferences and adjust coaching style

#### Knowledge Integration
- Access to poker strategy database
- GTO principles and fundamentals
- Common exploitative adjustments
- Stake-specific advice
- Game format considerations (cash, tournament, SNG)

---

### Quiz & Study System

#### Quiz Engine
- Multiple question types:
  - Multiple choice (action selection)
  - Bet sizing (numeric input)
  - Range construction
  - True/false concept questions
- Difficulty levels (beginner, intermediate, advanced)
- Topic-based quizzes (3-betting, c-betting, river play, etc.)
- Timed challenges

#### Scenario Generation
- Generate realistic poker situations
- Configurable by stake level and game format
- Include board textures, positions, stack depths
- Multi-street decision trees
- Edge case scenarios for advanced players

#### Progress Tracking
- Track quiz performance over time
- Identify weak topics/situations
- Spaced repetition scheduling
- Achievement system
- Study session statistics

---

### Range Management

#### Range Builder
- Create custom ranges for different positions/actions
- Save and load range sets
- Tag ranges by situation (BTN open, BB vs CO 3-bet, etc.)
- Import/export range formats

#### Range Visualization
- CLI: ASCII grid showing hand matrix
- Web: Interactive graphical grid with color coding
- Highlight specific combos, value/bluff portions
- Show equity heat maps
- Compare multiple ranges side-by-side

#### Preflop Strategy
- Store optimal opening ranges by position
- 3-bet/4-bet/5-bet ranges
- Cold calling ranges
- Squeeze play ranges
- Adjustments for different stack depths

---

### Session & Bankroll Tracking

#### Session Management
- Log sessions (date, duration, stakes, location/site)
- Track profit/loss
- Note game conditions and opponents
- Tag session types (cash, tournament, format)
- Quick session entry via CLI or web form

#### Statistical Analysis
- Win rate (bb/100, $/hour)
- Variance and standard deviation
- Upswing/downswing tracking
- Session duration analysis
- ROI for tournaments

#### Bankroll Management
- Current bankroll tracking
- Risk of ruin calculations
- Recommended stake levels
- Goal setting and progress
- Alerts for moving up/down stakes

#### Visualization
- Bankroll graph over time
- Session results distribution
- Winning/losing session ratio
- Best/worst sessions

---

### Progress & Learning Analytics

#### Skill Assessment
- Periodic skill evaluations via quizzes
- Track improvement in specific areas
- Compare to benchmarks (GTO, population tendencies)
- Identify stagnant areas needing focus

#### Study Habits
- Study session logging
- Time spent on different topics
- Review frequency and consistency
- Correlation between study and results

#### Recommendations Engine
- Suggest next study topics
- Prioritize leak fixing
- Recommend review of old hands
- Adaptive learning paths

---

## Technology Stack

### Phase 1: CLI Application (Development & MVP)

#### Core Dependencies
- **Python 3.11+**: Main language
- **poker** or **treys**: Hand evaluation library
- **numpy**: Numerical computations for equity calculations
- **rich**: Beautiful CLI interface with colors, tables, progress bars
- **typer**: Modern CLI framework with type hints
- **pydantic**: Data validation and settings management

#### AI & LLM Integration
- **anthropic**: Claude API client (primary)
- **openai**: OpenAI API client (fallback/alternative)
- **tiktoken**: Token counting for cost management

#### Data & Storage
- **SQLite**: Local database for hands, sessions, progress
- **sqlalchemy**: ORM for database operations
- **alembic**: Database migrations
- **pandas**: Data analysis and manipulation

#### Testing & Quality
- **pytest**: Testing framework
- **pytest-cov**: Code coverage
- **pytest-asyncio**: Async test support
- **black**: Code formatting
- **ruff**: Fast Python linter
- **pyrefly**: Static type checking

#### Utilities
- **python-dotenv**: Environment variable management
- **loguru**: Advanced logging
- **tqdm**: Progress bars for long operations

---

### Phase 2: Web Application

#### Backend (Python)
- **FastAPI**: Modern async web framework
- **uvicorn**: ASGI server
- **pydantic v2**: Request/response validation
- **python-jose[cryptography]**: JWT token handling
- **passlib[bcrypt]**: Password hashing
- **python-multipart**: File upload support
- **websockets**: Real-time communication
- **redis** (optional): Caching and session storage
- **celery** (optional): Background task processing

#### Frontend (TypeScript)
- **Next.js 14+**: React framework with App Router
- **React 18+**: UI library
- **TypeScript 5+**: Type-safe JavaScript
- **TailwindCSS**: Utility-first CSS framework
- **shadcn/ui**: High-quality React component library
- **Recharts**: Data visualization and charts
- **TanStack Query** (React Query): Server state management
- **Zustand**: Client state management
- **Zod**: Schema validation (TypeScript)
- **React Hook Form**: Form handling
- **Radix UI**: Headless UI primitives

#### Development Tools
- **Vite**: Fast build tool (bundled with Next.js)
- **ESLint**: JavaScript/TypeScript linting
- **Prettier**: Code formatting
- **Vitest**: Unit testing for frontend
- **Playwright**: E2E testing

#### Database & Storage
- **PostgreSQL**: Production database
- **Prisma** (optional): Type-safe ORM for TypeScript/Python interop
- **AWS S3** or **Cloudflare R2**: File storage (hand history uploads)

#### Deployment & Infrastructure
- **Docker**: Containerization
- **Docker Compose**: Local multi-container setup
- **Railway** or **Render**: Backend hosting (FastAPI)
- **Vercel**: Frontend hosting (Next.js)
- **GitHub Actions**: CI/CD pipeline
- **Sentry**: Error tracking and monitoring

#### Authentication & Security
- **NextAuth.js** (optional): Authentication for Next.js
- **JWT**: Token-based authentication
- **bcrypt**: Password hashing
- **CORS**: Cross-origin resource sharing
- **Rate limiting**: API protection

---

## Resources & References

### Poker Strategy Resources

#### Books & Theory
- "The Mathematics of Poker" by Bill Chen & Jerrod Ankenman
- "Applications of No-Limit Hold'em" by Matthew Janda
- "Modern Poker Theory" by Michael Acevedo
- "Play Optimal Poker" by Andrew Brokos
- GTO+ and PioSolver documentation

#### Online Resources
- Run It Once training videos
- Upswing Poker articles
- Two Plus Two forums (poker strategy)
- PokerSnowie and GTO Wizard for reference ranges
- Reddit: r/poker for community insights

### Technical Resources

#### Python & Poker Programming
- **treys** library documentation: Fast poker hand evaluation
- **poker** library documentation: Pure Python poker toolkit
- Monte Carlo simulation techniques
- Combinatorics in poker (combo counting)

#### LLM & AI Development
- Anthropic Claude API documentation
- OpenAI API documentation
- Prompt engineering guides
- Token optimization strategies

#### FastAPI & Backend
- FastAPI official documentation
- Pydantic v2 migration guide
- SQLAlchemy 2.0 ORM tutorial
- JWT authentication best practices
- WebSocket implementation patterns

#### Next.js & React
- Next.js 14+ App Router documentation
- React 18 documentation
- TypeScript handbook
- TailwindCSS documentation
- shadcn/ui component library
- React Query (TanStack Query) documentation

#### CLI Development
- Rich library documentation
- Typer tutorials
- Terminal UI best practices
- ANSI color codes and formatting

#### Database Design
- SQLAlchemy ORM patterns
- PostgreSQL performance tuning
- Database schema design for poker data
- Query optimization for hand history searches
- Time series data storage best practices

### Development Tools

#### Version Control & CI/CD
- Git best practices
- GitHub Actions workflows
- Pre-commit hooks for code quality
- Conventional commits

#### Documentation
- Sphinx for Python documentation
- MkDocs for project docs
- API documentation with FastAPI (auto-generated)
- Storybook for component documentation (frontend)

#### Monitoring (Production)
- Sentry for error tracking
- Analytics for user behavior
- Performance monitoring
- Logging best practices

---

## Development Phases

### Phase 1: CLI Application (Weeks 1-4)
**Goal**: Build functional poker coach CLI for personal use

**Deliverables**:
- Core poker engine (hand evaluation, equity calculations, ranges)
- Hand history parser and analyzer
- Basic AI coaching agent with Claude integration
- Range visualization (ASCII)
- Quiz engine with question bank
- Session and bankroll tracking
- SQLite database with schema
- Comprehensive test suite

**Tech Stack**: Python, Rich, Typer, SQLite, Claude API

---

### Phase 2: Backend API (Weeks 5-8)
**Goal**: Build FastAPI backend exposing all CLI functionality

**Deliverables**:
- FastAPI REST API with full endpoint coverage
- Authentication and authorization (JWT)
- Database migration to support multi-user
- WebSocket support for real-time coaching
- API documentation (auto-generated)
- Request validation and error handling
- Rate limiting and security
- Comprehensive API tests

**Tech Stack**: FastAPI, PostgreSQL, SQLAlchemy, Pydantic

---

### Phase 3: Frontend Application (Weeks 9-16)
**Goal**: Build Next.js web application for mobile/tablet/desktop

**Deliverables**:
- Next.js app with App Router
- Authentication flow (login, signup, session management)
- Hand review interface with visual hand replayer
- Range builder and visualizer (graphical grid)
- Quiz interface with interactive UI
- Bankroll tracking dashboard with charts
- AI chat interface for coaching
- Responsive design (mobile-first)
- PWA support (installable, offline capable)

**Tech Stack**: Next.js, React, TypeScript, TailwindCSS, shadcn/ui

---

### Phase 4: Polish & Launch (Weeks 17-20)
**Goal**: Production-ready application

**Deliverables**:
- Performance optimization
- E2E testing with Playwright
- Error tracking and monitoring (Sentry)
- Deployment pipeline (CI/CD)
- User documentation and tutorials
- Beta testing with real users
- Bug fixes and refinements
- Launch preparation

---

## Data Models

### Core Entities

#### Hand
- Hand ID (UUID)
- User ID (foreign key)
- Timestamp
- Game type (NLH, PLO, etc.)
- Stakes (blinds, ante)
- Players (JSON: positions, stack sizes, names)
- Hero position
- Actions (JSON: sequence of preflop/flop/turn/river actions)
- Board cards
- Results (showdown, winner, pot size)
- Analysis results (JSON: equity, recommendations, mistakes)
- User notes (text)
- Tags (array: e.g., "3-bet pot", "bluff catch", "bad beat")
- Created/Updated timestamps

#### Session
- Session ID (UUID)
- User ID (foreign key)
- Date & time (start, end)
- Duration (minutes)
- Stakes
- Location/Site
- Buy-in & cash-out amounts
- Profit/Loss
- Hands played count
- Notes (text)
- Game format (cash, tournament, SNG)
- Created/Updated timestamps

#### User
- User ID (UUID)
- Email (unique)
- Username (unique)
- Password hash
- Display name
- Skill level
- Preferences (JSON: coaching style, stakes played, etc.)
- Subscription tier (free, pro, etc.)
- Created/Updated timestamps

#### User Progress
- Progress ID (UUID)
- User ID (foreign key)
- Quiz scores (JSON: by topic, over time)
- Study time (JSON: by module)
- Identified leaks (array)
- Strong areas (array)
- Goals & milestones (JSON)
- Last study date
- Streak count
- Created/Updated timestamps

#### Range
- Range ID (UUID)
- User ID (foreign key, nullable for default ranges)
- Name (e.g., "BTN Open vs BB")
- Position
- Action context (open, 3-bet, call, etc.)
- Stack depth category
- Range string or combo list (JSON)
- Tags/Categories (array)
- Is default (boolean)
- Created/Updated timestamps

#### Quiz Question
- Question ID (UUID)
- Type (multiple choice, numeric, range, true/false)
- Difficulty (beginner, intermediate, advanced)
- Topic/Category
- Scenario (JSON: position, stacks, action, board)
- Question text
- Options (JSON: for multiple choice)
- Correct answer(s) (JSON)
- Explanation (text)
- Related concepts (array)
- Times answered (count)
- Success rate (percentage)
- Created/Updated timestamps

#### Quiz Attempt
- Attempt ID (UUID)
- User ID (foreign key)
- Question ID (foreign key)
- User answer (JSON)
- Is correct (boolean)
- Time taken (seconds)
- Timestamp

---

## API Design

### Authentication Endpoints
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login (returns JWT)
- `POST /api/auth/logout` - User logout
- `POST /api/auth/refresh` - Refresh JWT token
- `GET /api/auth/me` - Get current user info

### Hand Analysis Endpoints
- `POST /api/hands` - Submit hand for analysis
- `GET /api/hands` - List user's hands (paginated)
- `GET /api/hands/{hand_id}` - Get specific hand with analysis
- `PUT /api/hands/{hand_id}` - Update hand notes/tags
- `DELETE /api/hands/{hand_id}` - Delete hand
- `POST /api/hands/parse` - Parse hand history text
- `POST /api/hands/{hand_id}/analyze` - Re-run analysis

### Range Endpoints
- `GET /api/ranges` - List all ranges (default + user's)
- `GET /api/ranges/{range_id}` - Get specific range
- `POST /api/ranges` - Create custom range
- `PUT /api/ranges/{range_id}` - Update range
- `DELETE /api/ranges/{range_id}` - Delete range
- `POST /api/ranges/calculate` - Calculate range equity

### Quiz Endpoints
- `GET /api/quiz/questions` - Get quiz questions (filtered by topic/difficulty)
- `GET /api/quiz/questions/{question_id}` - Get specific question
- `POST /api/quiz/attempt` - Submit quiz answer
- `GET /api/quiz/stats` - Get user's quiz statistics
- `GET /api/quiz/next` - Get next recommended question

### Session/Bankroll Endpoints
- `GET /api/sessions` - List sessions (paginated)
- `GET /api/sessions/{session_id}` - Get specific session
- `POST /api/sessions` - Create new session
- `PUT /api/sessions/{session_id}` - Update session
- `DELETE /api/sessions/{session_id}` - Delete session
- `GET /api/bankroll/stats` - Get bankroll statistics
- `GET /api/bankroll/graph` - Get bankroll graph data

### AI Coaching Endpoints
- `POST /api/coach/chat` - Send message to AI coach
- `GET /api/coach/history` - Get chat history
- `POST /api/coach/analyze-hand` - AI analysis of specific hand
- `POST /api/coach/recommend` - Get study recommendations

### Progress Endpoints
- `GET /api/progress` - Get user progress overview
- `GET /api/progress/stats` - Detailed progress statistics
- `POST /api/progress/goal` - Set new goal
- `GET /api/progress/recommendations` - Get personalized recommendations

### WebSocket Endpoints
- `WS /ws/coach` - Real-time coaching chat
- `WS /ws/quiz` - Real-time quiz sessions

---

## Security & Privacy Considerations

### Data Privacy
- All user data encrypted at rest (database encryption)
- Hand histories are private by default
- Optional sharing with unique links
- No selling or sharing of user data
- GDPR compliance for EU users
- Data export functionality

### API Security
- JWT-based authentication
- API keys stored in environment variables (never committed)
- Rate limiting on all endpoints (per user/IP)
- Input validation with Pydantic
- SQL injection prevention (ORM parameterized queries)
- XSS prevention (React auto-escapes)
- CORS properly configured
- HTTPS only in production
- Secure password hashing (bcrypt)

### LLM Security
- API key rotation
- Cost monitoring and caps per user
- Token counting to prevent abuse
- Content filtering for inappropriate prompts
- Rate limiting on LLM endpoints

### Frontend Security
- HttpOnly cookies for JWT storage
- CSRF protection
- Secure session management
- No sensitive data in localStorage
- Content Security Policy headers

---

## Success Metrics

### User Engagement
- Daily/weekly active users
- Study sessions per week
- Hands analyzed
- Quizzes completed
- Average session duration
- Return rate (day 1, day 7, day 30)

### Learning Outcomes
- Quiz score improvements over time
- Identified leaks addressed
- Win rate improvements (self-reported)
- User-reported confidence gains
- Study consistency (streak tracking)

### System Performance
- Hand analysis speed (<1s per hand)
- Equity calculation accuracy (validated against solvers)
- LLM response time (<3s average)
- API response time (p95 <200ms)
- System uptime (99.9% target)
- Frontend load time (<2s)

### Business Metrics
- User signups
- Conversion to paid tier (if applicable)
- User retention rate
- Churn rate
- Net Promoter Score (NPS)
- Feature usage breakdown

---

## Future Enhancements

### Advanced Features
- Multi-table tournament (MTT) specific coaching
- ICM calculations and bubble analysis
- Opponent modeling and HUD stats
- Integration with tracking software (PT4, HM3)
- Community features (share ranges, discuss hands)
- Video hand review uploads with OCR
- Real-time coaching (browser extension for online poker)
- Multiplayer study sessions (study with friends)

### AI Improvements
- Fine-tuned models on poker strategy corpus
- Voice-based coaching (speech-to-text)
- Multimodal analysis (read hand screenshots with vision models)
- Personalized study curriculum generation
- Adaptive difficulty in quizzes
- Predictive leak detection

### Platform Expansion
- Mobile native apps (iOS/Android with React Native)
- Desktop applications (Electron)
- Browser extensions for popular poker sites
- Discord/Slack bots for quick queries
- Apple Watch / wearable integration for session tracking

### Advanced Analytics
- Machine learning for hand pattern recognition
- Predictive analytics for bankroll forecasting
- A/B testing different study methods
- Cohort analysis of improvement rates
- Benchmark against player pool

---

## Development Philosophy

### Principles
1. **Start Simple**: Build core functionality before adding complexity
2. **User-Centric**: Design for poker players, not just developers
3. **Iterative**: Release early, gather feedback, improve
4. **Modular**: Build independent components that can evolve separately
5. **Tested**: Maintain high test coverage for poker logic
6. **Documented**: Keep code and user docs up to date
7. **Performance**: Optimize for speed (poker players value quick feedback)
8. **Mobile-First**: Design for mobile/tablet from the start

### Code Quality
- Type hints throughout (Python + TypeScript)
- Comprehensive docstrings
- Unit tests for all poker calculations (100% coverage goal)
- Integration tests for API workflows
- E2E tests for critical user flows
- Clear naming conventions
- DRY principles
- Code reviews for all changes

### Performance Considerations
- Optimize hot paths (equity calculations, hand evaluation)
- Cache frequently used data (ranges, preflop charts, GTO solutions)
- Lazy loading for large datasets
- Database query optimization (indexes, query planning)
- Frontend code splitting
- Image optimization
- CDN for static assets
- Profile and benchmark critical operations

### User Experience
- Fast feedback loops (<1s for most operations)
- Clear error messages
- Progressive disclosure (don't overwhelm beginners)
- Consistent design language
- Accessible (WCAG 2.1 AA compliance)
- Offline capability (PWA)
- Keyboard shortcuts for power users

---

## Risks & Mitigations

### Technical Risks

**Risk**: Hand evaluation bugs leading to incorrect analysis
- **Mitigation**: Use battle-tested libraries (treys/poker), extensive unit tests, validation against known results

**Risk**: LLM costs spiraling out of control
- **Mitigation**: Token counting, response caching, rate limiting, cost caps per user, use smaller models where appropriate

**Risk**: Performance issues with complex equity calculations
- **Mitigation**: Optimize algorithms, use caching, implement progressive calculation (show estimates first), show progress indicators

**Risk**: Database performance degrades with large hand history datasets
- **Mitigation**: Proper indexing, query optimization, pagination, archiving old data, database partitioning

**Risk**: Frontend bundle size too large for mobile
- **Mitigation**: Code splitting, tree shaking, lazy loading, analyze bundle size regularly

### Product Risks

**Risk**: Coaching quality not meeting user expectations
- **Mitigation**: Iterate on prompts, gather user feedback, A/B test coaching approaches, provide fallback to manual resources

**Risk**: Feature creep delaying launch
- **Mitigation**: Strict MVP scope, prioritize ruthlessly, user story mapping, regular scope reviews

**Risk**: Insufficient differentiation from existing tools
- **Mitigation**: Focus on AI coaching as unique value prop, integrate multiple features (not just one tool), personalization

**Risk**: User adoption challenges (high learning curve)
- **Mitigation**: Interactive onboarding, progressive disclosure, tutorial content, example hands pre-loaded

### Business Risks

**Risk**: Low user retention
- **Mitigation**: Gamification (streaks, achievements), push notifications for study reminders, personalized email campaigns

**Risk**: Cannot monetize effectively
- **Mitigation**: Freemium model (free basic features, paid advanced), usage-based pricing for LLM features, affiliate partnerships

**Risk**: Competitor launches similar product
- **Mitigation**: Move fast, build community, focus on quality of coaching, continuous innovation

---

## Deployment Strategy

### Phase 1 (CLI)
- Distribute via PyPI (pip install poker-coach)
- GitHub releases with binaries
- Documentation on GitHub Pages

### Phase 2 (Web App)

#### Backend Deployment
- **Hosting**: Railway or Render (easy Python deployment)
- **Database**: Managed PostgreSQL (Railway/Render included)
- **Environment**: Production environment variables
- **Monitoring**: Sentry for error tracking
- **Logging**: Structured logging to cloud service
- **Backups**: Automated daily database backups

#### Frontend Deployment
- **Hosting**: Vercel (optimal for Next.js)
- **CDN**: Automatic via Vercel
- **Environment**: Separate env vars for API endpoints
- **Analytics**: Vercel Analytics or Plausible
- **Preview Deploys**: Automatic for pull requests

#### CI/CD Pipeline
- **Testing**: Run on every PR (pytest for backend, Vitest for frontend)
- **Linting**: Enforce code quality (ruff, ESLint, Prettier)
- **Type Checking**: pyrefly for Python, tsc for TypeScript
- **Build**: Automated builds on merge to main
- **Deploy**: Automatic deployment on successful build
- **Rollback**: One-click rollback capability

#### DNS & Domains
- Custom domain (e.g., pokercoach.ai)
- SSL certificates (automatic via Vercel/Railway)
- Subdomain for API (api.pokercoach.ai)

---

## Cost Estimates (Monthly)

### Development Phase
- **LLM API** (Claude/OpenAI): $50-200 (testing and development)
- **Infrastructure**: $0 (local development)
- **Tools**: $0 (free tiers)

### Production (100 active users)
- **Backend Hosting** (Railway/Render): $20-50
- **Database** (PostgreSQL): Included or $10-20
- **Frontend Hosting** (Vercel): $0 (free tier likely sufficient)
- **LLM API**: $200-500 (depends on usage, ~$2-5 per user)
- **Monitoring** (Sentry): $0-26 (free tier initially)
- **Total**: ~$250-600/month

### Scale Considerations
- LLM costs scale linearly with users (main cost driver)
- Infrastructure costs scale logarithmically (economies of scale)
- Consider caching, prompt optimization, and smaller models to reduce LLM costs

---

## Appendix

### Glossary
- **GTO**: Game Theory Optimal - unexploitable strategy
- **Equity**: Probability of winning the hand at any point
- **Range**: Set of possible hands a player could have in a situation
- **Combo**: Specific combination of two cards (e.g., AsKh is one AK combo)
- **bb/100**: Big blinds won per 100 hands (cash game win rate metric)
- **ICM**: Independent Chip Model - tournament chip valuation
- **HUD**: Heads-Up Display - stats overlay for online poker
- **Leak**: Strategic mistake or weakness in a player's game
- **Line**: Sequence of actions taken in a hand
- **Blocker**: Card that reduces opponent's possible holdings
- **Polarized**: Range consisting of very strong and very weak hands
- **Condensed**: Range with mostly medium-strength hands

### Abbreviations
- **CLI**: Command Line Interface
- **API**: Application Programming Interface
- **LLM**: Large Language Model
- **ORM**: Object-Relational Mapping
- **JWT**: JSON Web Token
- **CRUD**: Create, Read, Update, Delete
- **REST**: Representational State Transfer
- **UI/UX**: User Interface/User Experience
- **PWA**: Progressive Web App
- **SSR**: Server-Side Rendering
- **SPA**: Single Page Application

### Poker Position Abbreviations
- **UTG**: Under The Gun (first to act preflop)
- **MP**: Middle Position
- **CO**: Cutoff (one seat before button)
- **BTN**: Button (dealer position, acts last postflop)
- **SB**: Small Blind
- **BB**: Big Blind

---

## Document Version
- **Version**: 2.0
- **Last Updated**: 2025-12-25
- **Author**: Poker Coach Agent Development Team
- **Status**: Updated with Next.js/TypeScript frontend decision
- **Changes**:
  - Updated frontend stack from React to Next.js with detailed justification
  - Added comprehensive Next.js ecosystem (shadcn/ui, TanStack Query, etc.)
  - Expanded API design section
  - Added deployment strategy details
  - Included cost estimates
  - Enhanced development phases with realistic timeline

