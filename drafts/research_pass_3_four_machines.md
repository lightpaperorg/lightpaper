# Research Pass 3: AI as Four New Types of Machines and the Rewritten Production Function

## 1. The Four Types of AI Machines — A Taxonomy

### 1a. Word Machines (Language Models / LLMs)

**What they do:** Read, write, translate, summarize, and generate text at scale. They are general-purpose engines for the production of language — the fundamental medium of knowledge work.

**Industrial Revolution Analogy: The Printing Press and the Textile Loom**

The printing press (1440) was the first machine to mechanize the production of written words. Before Gutenberg, a scribe could copy perhaps 40 pages per workday. A single movable-type printing press could produce 3,600 pages per workday — a 90x improvement. By 1500, printing presses across Western Europe had produced more than 20 million volumes; by the end of the 16th century, output rose tenfold to 150-200 million copies (Dittmar, "Information Technology and Economic Change: The Impact of the Printing Press," CEPR).

The economic impact was staggering: cities that adopted the printing press between 1450 and 1600 saw economic growth 60 percentage points higher than those that did not. The press brought scholars, merchants, craftsmen, and mechanics together in commercial environments, eroding the pre-existing "town and gown" divide and catalysing the rise of individual traders over merchant guilds.

The textile loom mechanised the production of cloth. The Jacquard loom (1801) — the first programmable machine — used punched cards to control the lifting of individual warp threads. Traditional silk weavers produced approximately one inch of complex fabric per day; a skilled Jacquard operator could produce two feet in the same time — a 24x improvement.

LLMs are to written content what the printing press was to books and the power loom was to cloth: they mechanise the production of ALL written output — emails, reports, code, legal documents, marketing copy, translations, summaries, analyses.

**Current Capabilities (2025-2026):**
- GPT-4o, Claude Opus 4, Gemini 2.0 — frontier models capable of drafting legal documents, writing production code, translating between 100+ languages, summarising research papers, and generating marketing copy indistinguishable from human-written text.
- 25% of Google's new code is now AI-assisted (CEO Sundar Pichai, 2025). Nearly half of all code written in 2025 is AI-generated.
- 4% of all GitHub public commits are authored by Claude Code as of early 2026; at current trajectory, this will reach 20%+ of all daily commits by end of 2026 (Anthropic, "2026 Agentic Coding Trends Report").

**Production Function Impact — The Evidence:**

*Coding:*
- GitHub Copilot controlled experiment (95 professional developers): treatment group completed tasks 55.8% faster (1h11m vs 2h41m), statistically significant at P=0.0017. Success rates improved from 70% to 78%. 90% of developers felt more productive (Peng et al., 2023, arXiv:2302.06590).
- Microsoft reports it takes approximately 11 weeks for developers to fully realise productivity gains from AI coding tools.
- 82% of developers report using AI tools weekly as of Q1 2025, with 59% running three or more tools in parallel.

*Content and Marketing:*
- AI-produced content is 4.7x cheaper than human-written content ($131 vs $611 per blog post). Businesses report 42% reduction in content production costs and 77% increase in content output volume within six months of implementation.
- 90% of content marketers plan to use AI in 2025 (up from 64.7% in 2023).
- The AI content creation market is projected to reach $3.53 billion in 2025 (CAGR 21.9%) and $7.74 billion by 2029.

*Legal:*
- Lawyers using AI save 1-10 hours per week on average; 65% save 1-5 hours weekly, equalling 260 hours (32.5 working days) per year.
- AI tools deliver 94% accuracy in contract review. AI adoption in legal tripled from 11% (2023) to 30% (2024).
- AI summarisation of legal documents shows the strongest time savings currently; drafting productivity is improving but has not yet matched the summarisation gains.

*Customer Service:*
- Klarna's AI assistant handled 2.3 million customer conversations in its first month — equivalent to 700 full-time agents. Resolution time dropped from 11 minutes to under 2 minutes. Repeat inquiries fell 25%. Projected $40M profit improvement in 2024, at a deployment cost of just $2-3M.
- Industry-wide: AI chatbot handles a query for $0.50-0.70 vs $8-15 for a live agent — a 90-95% cost reduction per interaction.
- AI customer service market projected to grow from $12.06B (2024) to $47.82B (2030), CAGR 25.8%.

**Who is affected:** Writers, lawyers, analysts, programmers, marketers, translators, customer service agents, journalists, administrative assistants — anyone whose primary output is words. McKinsey estimates that ~75% of the $2.6-4.4 trillion in annual value from generative AI comes from four functions: customer operations, marketing & sales, software engineering, and R&D — all word-intensive.

---

### 1b. Thought Machines (Reasoning / Chain-of-Thought / Planning AI)

**What they do:** Reason through complex problems, plan multi-step solutions, make decisions under uncertainty, analyse trade-offs, synthesise evidence, and evaluate hypotheses.

**Industrial Revolution Analogy: The Calculating Engine to the Analytical Engine**

Charles Babbage's Difference Engine (1822) was designed to automate the tedious, error-prone work of calculating mathematical tables. In 1821, while checking manually calculated tables with astronomer John Herschel, Babbage exclaimed: "I wish to God these calculations had been executed by steam." The Difference Engine No. 1 called for 25,000 parts and would have weighed four tons.

Babbage's Analytical Engine (1837) was far more ambitious — the first design for a general-purpose computer, incorporating an arithmetic logic unit, conditional branching, loops, and integrated memory. It used punched cards borrowed from the Jacquard loom. Ada Lovelace wrote the first algorithm intended for it, recognising that it could manipulate symbols of any kind, not just numbers.

The leap from the Difference Engine to the Analytical Engine mirrors the leap from calculators to reasoning AI. The Difference Engine could compute; the Analytical Engine could *think* — conditionally, iteratively, and in ways its operators had not explicitly programmed for each specific case.

Modern reasoning models (OpenAI o1, o3, o4-mini; Claude with extended thinking; Gemini 2.0 with chain-of-thought) represent a new generation of "analytical engines" — machines that don't merely generate text but reason through problems step by step.

**Current Capabilities (2025-2026):**
- OpenAI o3 scored 96.7% on the American Invitational Mathematics Exam (AIME 2024) and 91.6% accuracy on the AIME 2024, vs o1's 74.3%. On the AIME 2025: 88.9%.
- o3 scored 75.7% on the ARC-AGI visual reasoning benchmark (low-compute), approaching human-level performance of 85% — a dramatic improvement over o1.
- o3 makes 20% fewer major errors than o1 on difficult real-world tasks, "especially excelling in areas like programming, business/consulting, and creative ideation" (OpenAI).
- o3 is both smarter AND cheaper than o1 for most use cases — the cost-performance frontier strictly improves over the previous generation.

**Production Function Impact — The Evidence:**

*The Harvard/BCG Study ("Navigating the Jagged Technological Frontier"):*
This landmark 2023 study used 758 BCG consultants (~7% of individual contributor-level employees). Key findings:
- Consultants using AI completed 12.2% more tasks on average and were 25.1% faster.
- Quality of output was 40%+ higher compared to control group.
- Below-average performers improved by 43%; above-average by 17% — a massive skill-levelling effect.
- BUT: for tasks OUTSIDE AI's capabilities, consultants using AI were 19 percentage points LESS likely to produce correct solutions. This defines the "jagged technological frontier."

A follow-up BCG study (September 2024) found that consultants achieved "up to 49 percentage point improvement on complex tasks outside their skillset" when using generative AI — suggesting AI enables workers to operate beyond their existing expertise.

*Medical Reasoning:*
- GPT-4T achieved 94% diagnostic accuracy in 2025 studies, up from 66.97% in 2024 and 57.49% in 2023 — a steep improvement curve.
- The US FDA has approved 882 medical devices using AI/ML assistance as of May 2024.
- AI-powered clinical decision support systems enhance diagnostic accuracy and personalised patient care through deep learning pattern extraction from images, ECGs, and other medical data.

*The Centaur Model — Human + AI Outperforms Either Alone:*
Garry Kasparov invented "Advanced Chess" after losing to Deep Blue in 1997. In a 2005 tournament open to computers, grandmasters, and human-AI teams, the surprise result was that human-AI "centaur" teams beat pure AI. As Kasparov argued: "The combination of human + AI seemed to be more effective than AI alone." Human intuition and strategic thinking paired with machine calculation produced superior outcomes.

This pattern has replicated across domains. Brynjolfsson, Li, and Raymond's "Generative AI at Work" (NBER Working Paper #31161, QJE 2023) studied 5,179 customer support agents and found: AI increased productivity by 14% on average, with 34% improvement for novice/low-skilled workers. The AI "disseminates the best practices of more able workers and helps newer workers move down the experience curve."

**Who is affected:** Analysts, strategists, researchers, managers, doctors, engineers, financial advisors, architects — anyone whose value comes from thinking, reasoning, planning, and making judgements. The centaur model suggests the near-term effect is augmentation rather than replacement: the human provides judgement and context; the thought machine provides analytical power and breadth.

---

### 1c. Doing Machines (AI Agents / Autonomous Systems)

**What they do:** Take actions, execute multi-step tasks, operate tools, manage workflows, coordinate processes, and complete complex sequences of knowledge work autonomously or semi-autonomously.

**Industrial Revolution Analogy: The Jacquard Loom and Ford's Assembly Line**

The Jacquard loom (1804) was the first programmable automation system. By changing punched cards, weavers could create different patterns — "programming" the machine to execute different sequences of operations. It automated not just a single task but a *workflow*.

Ford's assembly line (1913) took this further: it broke a complex manufacturing task (building a car) into a sequence of simpler, automated or semi-automated steps, each executed at a specific station. The Model T's production time dropped from 12 hours to 93 minutes. This was not just mechanisation of individual tasks but orchestration of an entire process.

AI agents combine both concepts: they are programmable (accepting natural language instructions), they break complex tasks into sequences of steps, and they execute those steps using tools (APIs, code execution, file systems, databases). They are the assembly lines of knowledge work.

**Current Capabilities (2025-2026):**
- Claude Code leads SWE-bench at 72%+, with 83.8% of pull requests merged by maintainers (567 PRs studied). Claude Code currently authors 4% of all GitHub public commits.
- Anthropic's 2026 Agentic Coding Trends Report: organisations report 30-79% faster development cycles. Rakuten reduced time-to-market by 79% (24 days to 5 days). TELUS shipped 30% faster while accumulating 500,000 hours in total time savings across 57,000+ team members.
- Developers now use AI in 60% of work. Zapier reports 97% AI adoption across their entire organisation as of January 2026.
- Rakuten tested Claude Code on implementing activation vector extraction in vLLM — a 12.5-million-line codebase — and the AI completed the task in 7 hours of autonomous work with 99.9% numerical accuracy.

*The "$300/month General-Purpose Agent" Concept:*
The economics are striking. A coding agent running on Claude Opus 4 costs roughly $15/75 per million input/output tokens. For a full workday of heavy agent usage, costs might range $50-200. This is approximately $1,000-4,000/month of compute — compared to a junior software engineer costing $8,000-15,000/month fully loaded in the US. The ratio continues to improve: inference costs are declining 10x annually.

*Workflow Automation Beyond Coding:*
- Block (formerly Square) cut headcount nearly in half (10,000 to under 6,000), directly attributed to AI automation.
- C.H. Robinson eliminated ~1,400 jobs after deploying AI-driven pricing, scheduling, and shipment tracking.
- IBM laid off ~8,000 employees, primarily in HR, replaced by the AskHR chatbot.

**Who is affected:** Project managers, coordinators, administrative workers, junior knowledge workers executing well-defined tasks, customer service teams, logistics coordinators, HR administrators — anyone whose role centres on executing sequences of steps rather than making high-level judgements.

---

### 1d. Perceiving Machines (Computer Vision / Robotics / Multimodal AI)

**What they do:** See, hear, sense, navigate, manipulate physical objects, inspect surfaces, recognise patterns in visual/audio data, and respond to physical environments.

**Industrial Revolution Analogy: From the Steam Engine to the Electric Motor**

The steam engine (1769, Watt) brought mechanical power to fixed locations — factories had to be built around a single, large steam engine connected to machines via belts and shafts. Power was centralised and inflexible.

The electric motor (late 1800s) distributed power to ANY location and ANY scale. Unlike steam engines, electric motors don't lose efficiency as they get smaller. This enabled a fundamental reorganisation of production: in 1899, electricity provided less than 5% of manufacturing horsepower; by 1919, 50%; by 1929, 75%. Factory layouts were redesigned around workflow rather than proximity to a central engine. Ford's assembly line was only possible because electric motors could power individual conveyor belts arranged in any configuration.

As economist Paul David documented, this transition took decades because factory owners initially just replaced their single steam engine with a single electric motor — failing to grasp that the revolution was in *distributed* power. Only when factories were redesigned from scratch around the new technology did the full productivity gains materialise.

Perceiving machines bring intelligence to ANY physical context — warehouses, roads, factories, farms, homes, hospitals. Just as the electric motor distributed mechanical power, perceiving AI distributes cognitive perception.

**Current Capabilities (2025-2026):**

*Autonomous Vehicles:*
- Waymo: 127 million rider-only miles through September 2025. At 56.7 million miles, statistically significant reductions: 79% fewer any-injury crashes, 81% fewer airbag deployments vs human benchmarks. Operating in Phoenix, San Francisco, Los Angeles, and Austin.
- Tesla FSD (Supervised): 8+ billion miles driven. Tesla reports one accident per 6.69 million miles with Autopilot/FSD engaged in Q2 2025, claiming 7x fewer major collisions vs manual driving. (Note: methodology critiques exist around baseline comparisons.)
- FSD annual miles: 6M (2021) → 80M (2022) → 670M (2023) → 2.25B (2024) → 4.25B (2025) — exponential growth in deployment.

*Warehouse Robotics:*
- Amazon: 1+ million robots across 300+ fulfillment centres, approaching 1:1 ratio with its ~1.5M human employees. Packages handled per worker surged from 175 (2016) to 3,870 (2025) — a 22x improvement.
- Robots automate 30-40% of intra-warehouse transport tasks and reduce manual walking distances by up to 70%.
- Amazon aims to automate ~75% of operations by 2033 and expects to avoid ~160,000 new roles by 2027.

*Manufacturing Quality Inspection:*
- AI vision systems achieve 97-99.5% defect detection accuracy vs 60-80% for human inspectors. Surface defects as small as 0.1mm detected with 99.8% accuracy.
- AI systems detected 37% more critical defects than expert human inspectors in controlled 2024 study.
- Automotive manufacturing: 83% reduction in defect escape rates (Deloitte, 2024). Siemens: 30% increase in inspection accuracy. Foxconn: 80% improvement in defect detection.
- AI visual inspection market: from $15.5B (2023) to projected $89.7B (2033), CAGR 19.6%.

*Surgical Robotics:*
- Intuitive Surgical (da Vinci): 1,721 systems placed in 2025. Procedures grew 18% in 2025. Revenue: $2.87B in Q4 2025 alone. ~60% global market share. Surgical robotics market: $2.9B (2024) projected to $9.2B (2034).

*Drones:*
- Global drone market: ~$69B (2026) projected to $147.8B (2036). Agricultural drones: $2.63B (2025) to $10.76B (2030), CAGR 32.6%.
- 30%+ of large farms worldwide using drones for field operations in 2025.
- Inspection & maintenance projected to exceed 25% of all commercial drone revenue by 2030.

*Construction — The Final Frontier:*
- Construction productivity CAGR: 0.4% (2000-2022) vs manufacturing 3.0% — the one major industry that has resisted capital deepening.
- Construction robotics market: $1.4B (2024) to $3.66B (2030), CAGR 18%. 3D printing construction: $53.9M (2024) to $4.18B (2030), CAGR 111%.
- Potential: productivity improvements of up to 40%, cost reductions of 30%, accident reductions of 70%.
- Funding for general-purpose robots (including humanoids) grew 5x from 2022-2024, now exceeding $1B annually.

**Who is affected:** Drivers (3.5M in the US alone), warehouse workers, factory inspectors, security guards, quality control technicians, agricultural workers, construction labourers — anyone whose value comes from perceiving and responding to physical environments.

---

## 2. The Combined Effect — How All Four Machine Types Transform Production Functions

### At the Individual Level: The N-of-1 Knowledge Worker

**Historical Analogy:** A farmer in 1800 with manual tools could feed 1-2 families. A farmer in 1900 with horse-drawn equipment could feed 5-6 families. A farmer in 2000 with a combine harvester could feed 130+ families. The capital-to-labour ratio increased by two orders of magnitude, and output per worker increased by a similar factor.

**The AI equivalent:** A solo founder in 2026, equipped with:
- **Word machines** (Claude, GPT-4o) for writing code, marketing copy, documentation, legal drafts
- **Thought machines** (o3, extended thinking) for strategic analysis, market research, technical architecture
- **Doing machines** (Claude Code, Copilot Workspace) for executing complex development tasks, managing deployments, handling customer inquiries
- **Perceiving machines** (vision APIs, monitoring dashboards) for product analytics, visual design, quality testing

...can produce output that previously required a team of 5-15 people.

**Real-world evidence:**
- Base44 (Maor Shlomo): Solo founder built an AI "vibe coding" platform, reached 300,000 users and $3.5M ARR in 6 months, sold to Wix for $80M cash.
- Midjourney (David Holz): Fewer than 15 people, $200M annual revenue, multi-billion-dollar valuation.
- Pieter Levels: Solo operator of Nomad List and Remote OK — seven figures revenue, zero employees.
- Danny Postma: Built HeadshotPro to $1M ARR in less than a year, solo.
- Solo-founded startups now represent 36.3% of all new ventures (2026), up from 22% in 2015. 52.3% of successful startup exits were achieved by solo founders.

**The new individual production function:**

Y_individual = f(human_judgment, AI_word, AI_thought, AI_doing, AI_perceiving)

The human provides: taste, ambition, domain expertise, ethical judgement, customer empathy, creative vision. The four machines provide: unlimited word production, deep analytical reasoning, autonomous task execution, and environmental perception.

### At the Firm Level: Smaller Teams, Larger Ambitions

**Historical Parallel: Did factories get smaller with the electric motor?**

Yes AND no. The electrification of manufacturing (1890s-1920s) had a dual effect:
1. Individual factories became more efficient, requiring fewer workers per unit of output.
2. The overall scale of industry grew dramatically, as the cost of manufacturing fell and new products became economically viable.

The same pattern is emerging with AI:

**Evidence of smaller teams per unit of output:**
- Microsoft: AI tools like Copilot write up to 30% of new code. "Companies need fewer people per project" (Nadella).
- Amazon: 14,000 corporate jobs eliminated as AI enabled "flatter management layers and faster decision-making."
- Klarna: Revenue per employee up 73% year-on-year, driven by AI chatbot replacing 700 agents.
- Block: Headcount halved (10,000 to <6,000), explicitly attributed to AI.

**Evidence of larger ambitions enabled:**
- Total corporate AI investment: $252.3B in 2024, up 44.5% in private investment (Stanford AI Index 2025).
- Software developer demand remains strong despite automation — 25% of Google's code is AI-assisted, yet they describe the gain as "engineering velocity, not replacement."
- The Jevons Paradox in action: as AI makes cognitive work cheaper, demand for it explodes. Companies don't just do the same work with fewer people — they do vastly MORE work.

**The McKinsey breakdown by function:**
~75% of the $2.6-4.4 trillion in annual generative AI value comes from:
- **Customer operations** (word machines + doing machines)
- **Marketing and sales** (word machines): 5-15% productivity gain on total marketing spending
- **Software engineering** (word machines + thought machines + doing machines): 20-45% productivity gain
- **R&D** (thought machines + word machines): accelerated discovery and analysis

### At the National Level: A New Factor of Production

**The Classical Production Function:**
Y = A * f(K, L)
Where Y = output, A = total factor productivity, K = capital, L = labour.

**AI as a distinct capital type:**
AI is not merely an improvement in TFP (A). It is a new form of capital — one that substitutes for certain types of labour in ways that traditional capital never could. Traditional capital (machines, buildings) substitutes for physical labour. AI capital substitutes for cognitive labour.

**GDP Impact Projections (range of estimates):**

| Source | Estimate | Timeframe |
|--------|----------|-----------|
| Goldman Sachs (2023) | +7% global GDP, 1.5pp productivity growth | 10 years |
| Goldman Sachs (2025 actual) | "basically zero" actual impact so far | 2025 |
| McKinsey (2023) | $2.6-4.4T annual value added | Full adoption |
| Acemoglu (2024) | +1.1-1.6% GDP over 10 years (0.05%/yr) | 10 years |
| Aghion & Bunel (2024) | +0.8-1.3pp productivity/yr (historical approach); +0.07-1.24pp (task-based, median 0.68pp) | 10 years |
| ARK Invest (2025) | +$200T economic output, 6-8% real GDP growth | By 2030 |
| IMF | +5.4% output (US, high-productivity scenario) | Medium-term |
| Charles Jones (Stanford, 2026) | Prosperity in both explosive and gradual AI scenarios | Long-run |

The range is enormous — from Acemoglu's cautious 0.05%/year to ARK's explosive 6-8% growth. This is itself informative: we are in a period of radical uncertainty about magnitude, even as the direction is clear.

**Key insight from Goldman Sachs (2025-2026):**
Goldman Sachs' chief economist acknowledged that AI contributed "basically zero" to U.S. GDP growth in 2025, with only 0.1 percentage points of direct impact. But this mirrors the electric motor story: Paul David showed that electrification took 20-30 years to show up in productivity statistics, because factories had to be *redesigned* around the new technology. Goldman still projects that "the largest productivity benefits from AI are still a few years off."

**Which Countries Will Benefit Most?**

The pattern from industrialisation: countries that adopted new technologies earliest and most aggressively benefited disproportionately (Britain, then Germany, then the US).

For AI:
- **United States:** Leads in AI investment ($109.1B in 2024), foundational model development (61% of global output), and controls 73% of global AI compute. Projected output gain: 5.4% (high-productivity scenario, IMF).
- **China:** AI projected to contribute 26.1% to GDP ($4.8T) by 2030, driven by 37% annual growth in implementation, highest AI adoption in healthcare (76%) and manufacturing (57%), and largest global AI patent portfolio.
- **Low-income countries:** Output gains of just 2.7% — the AI revolution risks widening the global development gap, just as industrialisation created a "Great Divergence" between the West and the rest.

The global AI market is projected to hit $1.81T by 2030, potentially adding up to $15.7T to world GDP, with the US, China, and India capturing the largest shares.

---

## 3. The Pattern of Machine Adoption — Lessons from History for AI

### The Consistent Five-Stage Pattern

Every major machine revolution in history has followed the same sequence:

**Stage 1: Initial Displacement**
Workers doing the old task lose their jobs. The transition is painful and often politically explosive.
- Textile: Handloom weavers' wages fell from 240 pence/week (1806) to under 100 pence/week (1820) — a 58% decline. At peak, ~250,000 hand weavers in Britain; the Luddite movement (1811-1816) saw workers smashing machines.
- Telephone: Switchboard operators (peak: 350,000+ in the US in the 1940s) were eliminated by automatic switching.
- Automobiles: The entire horse-drawn carriage industry — farriers, stable hands, coach builders — was destroyed.

**Stage 2: Cost Collapse**
The cost of the output drops dramatically, often by 90% or more.
- Printing press: 90x productivity improvement per worker-day; books went from luxury goods to mass commodities.
- Textiles: Cloth prices fell so far that cotton went from a luxury to a basic commodity affordable to all classes.
- Telephone: Long-distance call costs fell by 99%+ over the 20th century.
- Computing: Cost per MIPS dropped from millions of dollars (1970s) to fractions of a cent (2020s).

**Stage 3: Demand Explosion**
Because costs fall, demand explodes — far beyond what anyone predicted.
- More cloth was produced and consumed after power looms than was even conceivable before them.
- More text is published per day on the internet than was published in the entire history of the printing press.
- The total number of trips taken by humans per year increased massively after automobiles, despite (and because of) the destruction of the horse carriage industry.

**Stage 4: New Job Creation**
Entirely new categories of work emerge that could not have been predicted.
- Typewriter → clerical worker (women: 5% of office workers in 1880, 75% by 1900).
- Telephone → switchboard operator → telecommunications engineer → network administrator → systems architect.
- Automobile → mechanic, filling station attendant, driving instructor, traffic engineer, highway designer, suburban developer, shopping mall designer, logistics coordinator.
- Computer → programmer, web developer, data scientist, UX designer, cybersecurity analyst, social media manager, cloud architect.

**Stage 5: Net Positive**
More total employment, higher wages, vastly more output — but with significant disruption during the transition.

### Applying the Pattern to Each AI Machine Type

#### Word Production: Content, Code, Legal Documents

**Displacement:** Writers, junior lawyers, entry-level programmers, translators, customer service agents.
- Evidence: Stanford study found employment among software developers aged 22-25 fell nearly 20% between 2022 and 2025.
- 41% of companies plan to reduce workforces by 2030 due to AI (WEF/CNN, 2025).

**Cost Collapse:**
- Content creation: 4.7x cheaper with AI ($131 vs $611 per blog post).
- Customer service: $0.50-0.70 per AI interaction vs $8-15 per human agent (90-95% cost reduction).
- Code: Inference costs declining 10x/year. GPT-4-equivalent performance: $20/million tokens (2022) → $0.40/million tokens (2025) — a 50x decline.
- Legal: Contract review at 94% accuracy, lawyer time savings of 32.5 working days/year.

**Demand Explosion:**
- Companies don't just produce the same content cheaper — they produce vastly MORE. Businesses report 77% increase in content output volume within 6 months of AI adoption.
- Software: despite (or because of) AI coding tools, the AI code tools market is projected to grow from $4.91B (2024) to $30.1B (2032).
- The Jevons Paradox is already visible: "AI is simultaneously, and perhaps primarily, an expansion technology — it makes cognitive services so cheap that demand for them can grow faster than the displacement effect."

**New Jobs:** Prompt engineers, AI content strategists, AI safety engineers, model fine-tuning specialists, human-AI quality editors, AI-assisted legal analysts.

#### Thought Production: Analysis, Strategy, Research

**Displacement:** Junior analysts, entry-level consultants, research assistants, basic diagnostic roles.
- BCG study: below-average consultants improved 43% with AI — meaning the gap between junior and senior narrows, reducing demand for large teams of juniors.

**Cost Collapse:**
- Consulting-quality analysis available via API for pennies per query.
- Medical diagnostic AI: from specialist consultation ($200-500) to API call ($0.01-0.10).
- Financial analysis: previously $10,000+ for a custom research report; AI can generate comparable analysis in minutes.

**Demand Explosion:**
- Every small business can now afford "consultant-quality" strategic analysis.
- Every rural clinic can access specialist-level diagnostic support.
- Every student can have a personalised tutor. The BCG study showed AI enabled consultants to tackle tasks "beyond their existing expertise" — expanding what's possible, not just making the existing cheaper.

**New Jobs:** AI strategy consultants, human-AI collaboration designers, AI-augmented decision architects, centaur team leads.

#### Task Execution: Project Management, Coordination

**Displacement:** Administrative coordinators, project managers for routine workflows, scheduling assistants, basic operations staff.
- IBM: 8,000 HR jobs replaced by AskHR chatbot. C.H. Robinson: 1,400 jobs eliminated via AI logistics tools.

**Cost Collapse:**
- Workflow automation: tasks that required teams of coordinators can be orchestrated by a single person directing AI agents.
- Development cycles: 30-79% faster (Anthropic report). Rakuten: 24 days → 5 days.

**Demand Explosion:**
- More projects become viable when coordination costs plummet. A solo founder can now manage what previously required a 10-person team.
- 52.3% of successful startup exits are by solo founders (up from much lower historical baselines).

**New Jobs:** Agent orchestrators, AI workflow designers, human-in-the-loop supervisors, multi-agent system architects.

#### Perception Tasks: Driving, Inspection, Navigation

**Displacement:** Drivers, warehouse workers doing manual sorting, factory quality inspectors, security guards doing visual monitoring.
- Amazon: plans to avoid ~160,000 new roles by 2027 through automation. 75% of operations automated by 2033.

**Cost Collapse:**
- Waymo ride costs declining as fleet scales; target is below human-driven ride-hailing.
- Quality inspection: AI detects 37% more critical defects at fraction of human inspector cost.
- Warehouse: packages per worker from 175 (2016) to 3,870 (2025) — a 22x throughput improvement.

**Demand Explosion:**
- Cheaper autonomous transport → more deliveries, more ride-hailing trips, more goods movement.
- Cheaper inspection → inspection applied to products/processes that were never inspected before.
- Agricultural drones: enabling precision farming practices that were economically infeasible with manual inspection.

**New Jobs:** Robot fleet managers, autonomous vehicle remote operators, computer vision training specialists, human-robot interaction designers, drone operations managers.

---

## 4. Why This Time Could Be Different — And Why It Probably Isn't

### The "This Time Is Different" Argument

**Core claim:** Previous machines replaced muscles; AI replaces minds. There is nowhere left for humans to go.

The argument has intellectual force. Every previous machine revolution left cognitive work untouched:
- Steam engine: replaced physical power but not thinking.
- Electric motor: distributed physical power but not judgement.
- Computer: automated calculation but not reasoning.
- AI: automates reasoning itself. If machines can think, write, plan, perceive, and act — what is left for humans?

**Supporting evidence:**
- AI now affects high-skill work, not just routine tasks. Acemoglu's research notes that AI "is a better substitute for high-skill workers than traditional physical capital and a better substitute for high-skill workers than for low-skill workers."
- Elasticity of substitution for intelligence tasks: 2.2 (Brookings working paper) — meaning AI can substitute for human intelligence tasks relatively easily, compared to capital-labour substitution in manufacturing (elasticity ~0.6).
- WEF identifies three waves: (1) traditional automation of routine manual work, (2) generative AI reshaping cognitive/creative work, (3) agentic AI executing multi-step tasks without human input. All three are now operating simultaneously.
- Employment among young software developers (22-25) fell nearly 20% from 2022 to 2025 — the first clear signal of AI displacement in a high-skill profession.

### The "Same Pattern" Argument

**Core claim:** Every previous revolution seemed like it would destroy all jobs. It never did. The same forces that created new work before will do so again.

**Six reasons it probably isn't different:**

**1. Comparative Advantage (Ricardo, 1817)**
Even if AI is better than humans at every task in absolute terms, humans will still have comparative advantage in tasks where AI's relative advantage is smallest. The question is never "can AI do this?" but "is AI's advantage here bigger than its advantage elsewhere?" As long as there are tasks where humans are *relatively* (not absolutely) more productive, there will be demand for human labour.

**2. The Jevons Paradox / Demand Explosion**
When cognitive work becomes cheaper, we don't do less of it — we do vastly more. As NPR reported (February 2025), "AI becoming accessible to startups, schools and small businesses would expand the market and, in turn, increase — not lessen — energy demand and AI use." The same applies to the outputs of cognitive work: we will demand more analysis, more personalised content, more strategic thinking, more creative work — not less.

**3. Human Preferences for Human Interaction**
People want to interact with other people in many contexts. Even Klarna, after replacing 700 agents with AI, reversed course to ensure "customers always have the option to speak with a human." Healthcare, education, therapy, leadership, sales, negotiation — all involve trust relationships where human presence matters.

**4. New Desires Emerge**
In 1900, no one wanted a social media presence. In 1950, no one wanted a website. In 2000, no one wanted a mobile app. In 2020, no one wanted an AI agent. Human desires are not fixed — they expand as technology creates new possibilities. The WEF projects 170 million NEW jobs created vs 92 million displaced by 2030.

**5. David Autor's "Rebuilding the Middle"**
Autor (2024, "Applying AI to Rebuild Middle Class Jobs") argues AI could actually REVERSE four decades of wage polarisation. His key insight: AI as a collaboration tool is a "force multiplier for expertise" — it enables ordinary workers to do work previously requiring expensive specialists. This could expand the middle class, not destroy it.

**6. Erik Brynjolfsson's "Turing Trap" Warning**
Brynjolfsson (2022) warns against the "Turing Trap" — optimising AI to replicate and replace human labour rather than augment it. When AI automates, "the marginal value of workers' contributions is reduced." When AI augments, "more of the gains go to human workers." The trap is a choice, not an inevitability. Policy and corporate strategy can steer toward augmentation.

### The Honest Assessment

The academic literature is genuinely divided:
- **Pessimists** (Acemoglu): AI's GDP impact will be modest (1.1-1.6% over 10 years) and the risk of "wrong direction" automation is real.
- **Moderates** (Aghion & Bunel): Productivity growth of 0.07-1.24pp/year depending on assumptions. Substantial but not revolutionary.
- **Optimists** (Brynjolfsson, ARK Invest): Transformative productivity gains if the centaur/augmentation model prevails.

The key variable is the **elasticity of substitution between AI and human labour for different task types**. Current estimates:
- Intelligence tasks: elasticity of 2.2 (high substitutability)
- Physical tasks: much lower (robot bodies scale slowly)
- Creative/empathetic tasks: effectively zero (humans irreplaceable)

The most likely outcome is heterogeneous: massive displacement in some task categories, massive augmentation in others, and massive creation of entirely new task categories. The net effect on employment is genuinely uncertain; the net effect on output is almost certainly positive and large.

---

## 5. The Production Function, Rewritten

### The Classical Framework

The standard production function taught in every economics course:

**Y = A * K^α * L^(1-α)**

Where Y is output, A is total factor productivity (technology, institutions, culture), K is physical capital, L is labour, and α is capital's share of income (~0.33 historically).

This framework treats technology as a single residual (A) — everything that isn't capital or labour. It was adequate when machines were dumb tools that amplified human physical effort. It is inadequate for an era where machines can think.

### The Rewritten Production Function

**Y = f(K_physical, K_word, K_thought, K_doing, K_perceiving, L_human, A)**

Where:
- **K_physical** = traditional capital (machines, buildings, infrastructure, raw materials)
- **K_word** = word machine capacity (LLM tokens, content generation, translation, coding)
- **K_thought** = thought machine capacity (reasoning compute, analysis, planning, diagnosis)
- **K_doing** = doing machine capacity (agent hours, workflow automation, task execution)
- **K_perceiving** = perceiving machine capacity (computer vision, robotics, sensors, navigation)
- **L_human** = irreducible human labour (creativity, judgement, empathy, physical presence, taste, trust)
- **A** = total factor productivity (institutional quality, culture, coordination, legal framework)

### What Determines the "Price" of Each AI Capital Type?

**Compute costs — the fundamental input:**
- AI training costs improving at 50x the pace of Moore's Law (ARK Invest, 2025).
- Inference costs declining 10x/year for equivalent performance. GPT-4 equivalent: $20/million tokens (2022) → $0.40/million tokens (2025). Median decline across benchmarks: 50x/year (Epoch AI).
- OpenAI's text-davinci-003 (late 2022): $20/million tokens. GPT-4o mini (mid-2024): $0.15/million input tokens — a 99% cost reduction in under two years.
- Energy efficiency of leading AI GPUs: improving 40%/year (Epoch AI).
- Inference costs dropped 280-fold in 18 months for comparable performance.

**Current API Pricing (as of early 2026):**

| Model | Input ($/M tokens) | Output ($/M tokens) | Category |
|-------|-------------------|---------------------|----------|
| Claude Opus 4.5 | $5.00 | $25.00 | Frontier reasoning |
| GPT-4o mini | $0.15 | $0.60 | Efficient general |
| DeepSeek R1 | $0.55 | $2.19 | Open-source reasoning |

The cost trajectory is clear: AI "intelligence" is becoming a commodity, priced per unit and declining rapidly. Just as electricity went from expensive luxury (1890s) to near-free utility (2000s), AI inference is on a similar trajectory but moving faster.

**Key drivers of cost decline:**
1. Better GPU cost/performance (Moore's Law continuation)
2. Model quantisation: 16-bit → 4-bit (4x performance gain)
3. Software optimisations: reduced compute and memory bandwidth requirements
4. Algorithmic efficiency: post-training enhancements offer gains equivalent to 5-20x more compute at <1% of the cost
5. Competition: Chinese models (DeepSeek) entered at 90% lower price points, forcing global price competition

### Elasticity of Substitution — How Easily Can AI Replace Humans?

Recent economic research proposes nested CES (constant elasticity of substitution) production functions distinguishing three types of capital: traditional physical capital, industrial robots, and AI.

**Empirical estimates:**
- Intelligence tasks: elasticity of substitution = 2.2 (high — AI substitutes easily)
- Capital-labour substitution in manufacturing: ~0.6 (moderate)
- Physical tasks requiring embodiment: much lower (robot bodies scale slowly)

The key insight: **substitution is task-dependent, not occupation-dependent.** A single occupation may contain tasks where AI substitutes easily (elasticity > 1) and tasks where it doesn't (elasticity < 1). Whether AI actually displaces an AI-exposed occupation depends on "the relative strength of direct substitution effects, indirect effects that operate through reallocation of effort in potentially complementary tasks, and aggregate effects that operate through changes in firm productivity."

### Academic Frameworks Related to the Rewritten Production Function

**1. Acemoglu's Task-Based Model (2024)**
Divides production into tasks that can be allocated to either capital or labour with different comparative advantages. AI's effect depends on what fraction of tasks are impacted and average task-level cost savings. His estimate: 20% of US job tasks exposed to AI; GDP impact of 1.1-1.6% over 10 years.

**2. Aghion & Bunel's Dual Approach (2024)**
Uses both historical technological revolution parallels and task-based frameworks. Estimates: 0.8-1.3pp/year (historical approach) or 0.07-1.24pp/year (task-based, median 0.68pp).

**3. Charles Jones's "AI and Our Economic Future" (2026)**
Models the economy using a task-based production function with elasticity of substitution of 0.5 — a "weak link" framework where production is like a chain only as strong as its weakest link. Even in this conservative framework, both explosive and gradual AI scenarios lead to long-run prosperity.

**4. Brookings Working Paper: "(Artificial) Intelligence Saturation"**
Proposes a novel framework dividing the economy into physical and intelligence sectors, arguing they scale fundamentally differently. Physical production has diminishing returns; intelligence production may not.

**5. WTO Staff Working Paper (2025)**
Examines AI's effect on international trade and production functions across countries, finding that AI capital complements high-skill labour but substitutes for routine cognitive labour.

### The Distributional Question

All frameworks agree on one key prediction: **returns shift toward capital and away from labour.** The skill premium declines (AI narrows the gap between expert and novice), but the capital-labour share shifts further toward capital owners.

This echoes every previous machine revolution:
- Textile mill owners captured most of the gains from power looms; weavers' wages fell.
- Factory owners captured most of the gains from electrification; factory workers eventually benefited through higher wages but with a multi-decade lag.
- Tech company founders/shareholders capture most of the gains from AI; knowledge workers may eventually benefit but the transition path matters enormously.

The magnitude of distributional effects depends on AI's long-run growth rate and production factor complementarity — the key parameters that are currently most uncertain.

---

## Key Statistics Summary Table

| Metric | Value | Source |
|--------|-------|--------|
| Generative AI annual value potential | $2.6-4.4 trillion | McKinsey (2023) |
| Goldman Sachs 10-year GDP impact | +7% global | Goldman Sachs (2023) |
| Actual AI GDP impact (2025) | ~0.1 percentage points | Goldman Sachs (2026) |
| Acemoglu 10-year GDP impact | +1.1-1.6% total | Acemoglu (2024) |
| GitHub Copilot task completion speedup | 55.8% faster | Peng et al. (2023) |
| BCG consultant quality improvement | 40%+ higher quality | Dell'Acqua et al. (2023) |
| BCG low-skill worker improvement | +43% | Dell'Acqua et al. (2023) |
| Customer support productivity gain | +14% average, +34% for novices | Brynjolfsson et al. (2023) |
| AI content cost reduction | 4.7x cheaper | EngageCoders (2025) |
| AI customer service cost reduction | 90-95% per interaction | Industry data (2025) |
| LLM inference cost decline rate | ~10x/year (median 50x/year) | Epoch AI / a16z |
| AI training cost improvement | 50x pace of Moore's Law | ARK Invest (2025) |
| Amazon robots deployed | 1+ million (1:1 with workers) | Amazon (2025) |
| Amazon packages/worker | 175 (2016) → 3,870 (2025) | Amazon data |
| Waymo injury crash reduction | 79% fewer than human benchmark | Waymo (2025) |
| Tesla FSD miles driven | 8+ billion cumulative | Tesla (2025) |
| AI visual inspection accuracy | 97-99.5% vs 60-80% human | Industry studies (2024) |
| Da Vinci surgical procedures growth | +18% year-on-year | Intuitive Surgical (2025) |
| Total corporate AI investment | $252.3 billion (2024) | Stanford AI Index |
| WEF net new jobs from AI | +78 million (170M created, 92M displaced) | WEF Future of Jobs (2025) |
| Solo-founded startup share | 36.3% of new ventures (2026) | Scalable.news |
| Developer AI tool usage | 82% weekly (Q1 2025) | Industry surveys |
| Claude Code GitHub commit share | 4% (early 2026), trending to 20%+ | Anthropic (2026) |
| AI code tools market | $4.91B (2024) → $30.1B (2032) | Grand View Research |
| Construction productivity CAGR | 0.4% (2000-2022) vs 3.0% manufacturing | McKinsey |
| Countries: US share of global AI compute | 73% | Stanford/Epoch AI (2025) |

---

## Sources

### Academic Papers
- Acemoglu, D. (2024). "The Simple Macroeconomics of AI." *Economic Policy*, 40(121), 13-58.
- Aghion, P. & Bunel, S. (2024). "AI and Growth: Where Do We Stand?" Federal Reserve Bank of San Francisco.
- Autor, D. (2024). "Applying AI to Rebuild Middle Class Jobs." SSRN.
- Brynjolfsson, E. (2022). "The Turing Trap: The Promise & Peril of Human-Like Artificial Intelligence." *Daedalus*.
- Brynjolfsson, E., Li, D., & Raymond, L. (2023). "Generative AI at Work." NBER Working Paper #31161, *Quarterly Journal of Economics*.
- Dell'Acqua, F. et al. (2023). "Navigating the Jagged Technological Frontier." Harvard Business School Working Paper.
- Dittmar, J. "Information Technology and Economic Change: The Impact of the Printing Press." CEPR.
- Jones, C.I. (2026). "A.I. and Our Economic Future." Stanford GSB/NBER.
- Peng, S. et al. (2023). "The Impact of AI on Developer Productivity: Evidence from GitHub Copilot." arXiv:2302.06590.

### Industry Reports
- Anthropic. (2026). "2026 Agentic Coding Trends Report."
- ARK Invest. (2025). "Big Ideas 2025."
- Goldman Sachs. (2023). "Generative AI Could Raise Global GDP by 7%."
- Goldman Sachs. (2026). "AI boosted US economy by 'basically zero' in 2025."
- McKinsey & Company. (2023). "The Economic Potential of Generative AI: The Next Productivity Frontier."
- McKinsey & Company. (2025). "The State of AI in 2025: Agents, Innovation, and Transformation."
- Stanford HAI. (2025). "AI Index Report 2025."
- World Economic Forum. (2025). "Future of Jobs Report 2025."
- Epoch AI. (2025). "LLM Inference Price Trends."

### Company Data
- Amazon: 1M+ robots, packages/worker data, automation targets.
- Intuitive Surgical: da Vinci procedure growth, system placements, revenue.
- Klarna: AI assistant performance metrics, revenue per employee.
- Tesla: FSD safety statistics, miles driven.
- Waymo: Crash rate comparison data at 56.7M and 127M miles.
