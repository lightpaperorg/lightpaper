# Research Pass 2: Production Functions at Different Scales

## 1. The Individual Worker's Production Function

### What Is "Labour" at the Individual Level?

For a knowledge worker, labour is not simply "hours at a desk." It decomposes into three scarce resources:

- **Time**: The hard constraint. A knowledge worker has roughly 2,000 productive hours per year (250 days x 8 hours). But not all hours are equal — "deep work" hours (Cal Newport's term) where complex cognitive output is produced may number only 3-4 per day.
- **Attention**: The binding constraint in the information age. Herbert Simon recognised this in 1971: "a wealth of information creates a poverty of attention." Attention is the bottleneck through which all cognitive output must pass.
- **Cognitive effort**: The metabolic cost. The brain consumes ~20% of the body's energy despite being ~2% of body mass. Decision fatigue, context-switching costs, and mental depletion are real constraints on output.

### What Is "Capital" at the Individual Level?

- **Physical tools**: Pen, typewriter, computer, smartphone, AI assistant. Each represents a different vintage of capital that transforms the individual production function.
- **Human capital (education)**: Accumulated knowledge and skills. A trained surgeon's hands produce a categorically different output than an untrained person's, using the same physical tools.
- **Organisational capital**: Processes, habits, workflows. David Allen's "Getting Things Done" is essentially a method for optimising the individual's organisational capital.
- **Network capital**: Connections, reputation, access. In knowledge work, who you can reach often matters more than what you can produce alone.

### Historical Progression: How Capital Rewrote the Individual Production Function

#### A Scribe in 1400

The production function of a medieval scribe was almost pure labour with minimal capital:

- **Output**: Approximately 2-3 pages (leaves) per day. Carla Bozzolo and Ezio Ornato, studying colophons in dated manuscript catalogues, calculated an average daily output of 2.85 leaves. A dozen pages per day represented an optimistic upper bound.
- **Capital**: A quill, ink, parchment or vellum, a desk. Total capital cost was trivial relative to the labour cost.
- **Time to produce a book**: A single manuscript Bible might take a scribe 15-20 months of continuous labour. Some sources cite two full years.
- **Labour intensity**: Writing speed varied with the season — cold fingers in winter could slow or halt production entirely. The quill needed frequent re-cutting. The scribe's entire body was the production apparatus.
- **Output per lifetime**: A prolific scribe might produce a few dozen complete works in a career.

The production function was approximately: **Q = f(L)** with capital barely registering. Output scaled linearly with labour hours, with an effective ceiling around 3 pages/day regardless of skill.

**The Gutenberg Disruption (1450s)**:
A single printing press could produce 3,600 pages per workday, compared to ~3 by hand-copying — a **1,200x productivity increase**. Before 1450, there were perhaps tens of thousands of books in all of Europe. By 1500, printing presses had produced more than 20 million volumes. The price of books fell by roughly two-thirds between 1450 and 1500. The production function for written documents shifted from Q = f(L) to Q = f(K, L) virtually overnight, with capital becoming the dominant input.

#### A Clerk in 1900 with a Typewriter

The typewriter, commercialised from 1874, fundamentally changed the office production function:

- **Handwriting speed**: The world record in 1853 was 30 words per minute (WPM). A typical clerk managed considerably less.
- **Typewriter speed**: A competent typist could sustain 60-80 WPM, with professionals reaching much higher. Shorthand transcription at 130 WPM could finally be turned into legible text at comparable speed.
- **Productivity claim**: Philip G. Hubert, writing in the 1880s, claimed typewriters could "save 40 minutes out of an hour" compared with the pen. He wrote: "With the aid of this little machine an operator can accomplish more correspondence in a day than half a dozen clerks can with the pen, and do better work."
- **Scale of adoption**: Remington sold 1,400 typewriters in 1882 and 14,000 in 1887 — a 10x increase in five years.
- **New labour market**: The typewriter opened clerical work to women on a massive scale, creating an entirely new occupational category. "Typewriter" initially referred to both the machine and the person operating it.
- **Systemic change**: The typewriter eliminated the need for clerks to laboriously copy letters and invoices into heavy ledger books, ending centuries of hand-copying as the backbone of business documentation.

The production function shifted to: **Q = A * f(K, L)** where the typewriter (K) multiplied effective labour output by 3-6x for document production. But this was still fundamentally labour-constrained — the typist's speed was the bottleneck.

#### A Knowledge Worker in 2000 with a Computer

The personal computer transformed the production function more deeply than the typewriter because it affected not just the speed of output but the *nature* of what could be produced:

- **Word processing**: Eliminated retyping for revisions. A document that previously required complete retyping for each draft could be edited incrementally. This changed the economics of revision — quality improved because the marginal cost of improvement dropped to near zero.
- **Spreadsheets**: VisiCalc (1979), Lotus 1-2-3 (1983), Excel (1985). Tasks that previously required teams of accountants and actuaries — financial modelling, scenario analysis, budgeting — could be performed by a single person. Accounting, data processing, and record-keeping tasks once managed by large teams could now be completed by one person.
- **Email**: Eliminated the latency of physical mail, enabling coordination across distances that previously required co-location or expensive telecommunications.
- **Productivity data**: US worker productivity had been growing at 1.0-1.5% annually since the early 1970s. From 1995-2000, it surged to 2.9% per year — many economists credited computer-related information technology.
- **New job categories**: Computer salespeople, software developers, IT support technicians became essential to nearly every business. Secretaries transformed into administrative assistants skilled in operating advanced software.
- **Job displacement**: Clerical occupations saw declining employment share from the 1980s onward as computers automated filing, calculation, and routine correspondence.

The production function became: **Q = A(IT) * f(K_physical, K_human, L)** where information technology (IT) served as a general-purpose technology multiplier on all inputs.

**The Solow Paradox**: In 1987, Robert Solow observed: "You can see the computer age everywhere, except in productivity statistics." Despite massive IT investment through the 1970s and 1980s, measured productivity growth remained sluggish. This was resolved in the late 1990s when:
1. **Complementary organisational investments** matured — firms had to redesign business processes, train workers, and develop new management practices (Erik Brynjolfsson's key finding).
2. **Implementation lags** of 2-5 years for IT investments to show productivity returns.
3. **Measurement problems** — quality improvements in IT goods were understated, causing inflation overestimates and productivity underestimates.
4. Productivity growth averaged over 2.8% per year from 1995-2005, with the largest gains in retail, wholesale, and finance — sectors that had reorganised around IT.

#### A Developer in 2024-2025 with AI Coding Assistants

The AI coding assistant represents a qualitative shift in the individual production function — capital that doesn't merely *amplify* labour but partially *substitutes* for it:

- **GitHub Copilot study (2023)**: 95 freelance programmers on Upwork were hired to build a web server. The group with access to GitHub Copilot completed the task **55.8% faster** than the control group.
- **Google internal study (2024)**: A randomised controlled trial on ~100 Google software engineers found developers using AI completed tasks **21% faster** on average (96 minutes vs 114 minutes).
- **Multi-company study (2024)**: A study spanning Microsoft, Accenture, and a Fortune 100 enterprise with nearly 5,000 developers found an average **26% increase in productivity** with Copilot access.
- **Code generation share**: AI is now writing **46% of the average developer's code**, reaching as high as **61% in Java projects** (GitHub data, 2025).
- **Adoption scale**: GitHub Copilot surpassed 20 million users by July 2025, up from 15 million in April 2025 — 400% year-over-year growth between early 2024 and early 2025.
- **Quality concerns**: GitClear's 2025 research suggests a **4x growth in code clones** (copy-paste patterns), indicating that raw output gains may come with quality trade-offs.

The production function is shifting toward: **Q = f(K_AI, K_human, L_direction)** where L_direction is the labour of directing and evaluating AI output rather than producing it directly. The worker becomes more architect than bricklayer.

### The N-of-1 Company

Sam Altman's prediction: "In my little group chat with my tech CEO friends, there's this betting pool for the first year that there is a one-person billion-dollar company." He has stated this "would have been unimaginable without AI and now will happen."

**The economics**: When AI capital can substitute for multiple employees, the minimum viable team for a company shrinks toward one. The individual production function begins to look like a firm's production function:

**Existing lean-team precedents**:
- **Instagram**: 13 employees when acquired by Facebook for $1 billion (2012)
- **WhatsApp**: 55 employees when acquired by Facebook for $19 billion (2014)
- **Mojang (Minecraft)**: ~40 employees when acquired by Microsoft for $2.5 billion (2014)
- **Midjourney**: Started with ~11 employees in 2022, achieved $200 million annual revenue with zero marketing spend by 2023. By 2025, expanded to 107-163 employees with $500 million annual revenue — revenue per employee exceeding **$5 million**.

**AI-enabled solo examples (2024-2025)**:
- The share of new US startups founded by solos with no venture funding surged from 22% in 2015 to **38% in 2024**.
- Solo-founded startups grew from 23.7% in 2019 to **36.3% by mid-2025**.
- A complete solopreneur AI stack now costs **$3,000-$12,000 annually** — a 95-98% reduction in operating costs compared to traditional staffing.
- **Andrej Karpathy coined "vibe coding"** in February 2025 — describing software development where you describe what you want in natural language and let AI generate the code.

The N-of-1 company represents the logical endpoint of capital deepening at the individual level: when one person's capital stack (AI tools, cloud infrastructure, automated workflows) can produce output that previously required 10-50 people, the production function has been fundamentally rewritten.

---

## 2. The Firm's Production Function

### How Firms Combine K and L

At the firm level, the production function Y = A * f(K, L) becomes concrete and measurable. The key metric is **capital intensity** — the ratio of capital to labour. Firms in the same industry can have radically different K/L ratios, producing the same output type with very different input mixes.

### Case Study: Tesla vs Traditional Auto Manufacturing

**The core comparison — vehicles per employee**:
- **Tesla (2019)**: ~9 vehicles per full-time employee
- **Toyota (2019)**: ~24 vehicles per full-time employee
- **Tesla (2024)**: 1,789,226 vehicles delivered / 125,665 employees = **~14.2 vehicles per employee**
- **Toyota**: ~370,000 employees, producing ~10 million vehicles = **~27 vehicles per employee**

Tesla is *less* labour-efficient than Toyota on a vehicles-per-employee basis, despite being more automated. This is partly because Tesla is a younger manufacturer still optimising processes, and partly because Tesla vertically integrates more functions (battery production, software development, charging infrastructure) that Toyota outsources.

**Revenue per employee**:
- **Tesla (2024)**: $97 billion revenue / ~140,000 employees = **~$690,000 per employee**
- **General Motors (2023)**: Over **$1 million per employee** (163,000 employees)
- **Ford (2023)**: **~$937,000 per employee** (173,000 employees)

**Industry-wide robot density** (2024):
- The automotive industry employs **38% of all industrial robots** globally
- **China**: 470 robots per 10,000 manufacturing employees (3rd highest globally)
- **United States**: 295 robots per 10,000 manufacturing employees (10th globally)
- US automotive robot installations increased **10.7%** in 2024, reaching 13,700 new units

**Key insight**: Tesla's story is not (yet) one of capital successfully substituting for labour at higher efficiency than incumbents. Toyota's lean manufacturing system — developed over decades — remains more labour-efficient. The interesting question is whether Tesla's heavy investment in automation (including the Optimus humanoid robot programme) will eventually flip this ratio. As of January 2025, Musk admitted zero Optimus robots are doing "useful work" at Tesla.

### Case Study: Amazon Warehouse Automation

**The Kiva acquisition**: In March 2012, Amazon acquired Kiva Systems for **$775 million** in cash — at the time, Amazon's second-largest acquisition ever.

**Before Kiva robots**:
- "Click to ship" cycle: **60-75 minutes**
- Workers walked miles per shift to retrieve items
- A warehouse performing 200,000 picks/day required two 75-person, 8-hour shifts (150 workers)

**After Kiva robots (2014 onwards)**:
- "Click to ship" cycle: **15 minutes** (a 75-80% reduction)
- Operating costs reduced by **~20% per warehouse** (~$22 million per facility)
- Same 200,000-pick warehouse: **25 workers per shift** (a 67% reduction)
- Workers could process **300-400 items per hour** instead of ~100 (3-4x improvement)
- Kiva robots present a new item every 6 seconds — base rate of **600 picks per hour**
- Each Kiva-equipped warehouse holds **50% more inventory per square foot**
- Potential savings if deployed across all 110 warehouses: **~$2.5 billion** (Deutsche Bank estimate)

**But did Amazon cut jobs?** No. Amazon now has **over 1 million robots** across its operations (as of 2024) and **1,556,000 employees** (2024) — having added over a million jobs worldwide since the Kiva acquisition. Approximately 65% of Amazon's workforce (~1 million people) work in operations and fulfilment roles.

**Scale**: Amazon customers place an estimated 12.3 million orders per day globally, equalling ~27.1 million products (2.21 items per order average). The company operates hundreds of fulfilment centres, with an average of ~670 employees per major facility, plus micro-fulfilment centres with 80-120 workers processing ~10,000 packages per day. Over 390,000 delivery drivers work across 4,400 Amazon Delivery Service Partners.

**The Amazon paradox mirrors the ATM-teller paradox**: Robots dramatically reduced the cost of operating each warehouse, which allowed Amazon to open vastly more warehouses, expand into same-day delivery, and process exponentially more orders — ultimately requiring *more* total workers, not fewer.

### Case Study: Netflix vs Blockbuster

This is perhaps the cleanest example of capital (technology infrastructure) completely replacing labour (store employees):

**Blockbuster at peak (2004)**:
- **9,094 stores** worldwide
- **84,300 employees**
- **$6 billion revenue**
- Revenue per employee: **~$71,000**
- Business model: massive physical capital (stores) + massive labour (store staff, distribution workers)

**Netflix (2024)**:
- **0 stores**
- **14,000 employees** (1,000 more than previous year, +7.7%)
- **$39 billion revenue**
- Revenue per employee: **$3.0 million** (up from $2.63M in 2023)
- Profit per employee: **$622,260** annually
- Business model: massive digital capital (streaming infrastructure, algorithms, content) + lean technical workforce

**The comparison**: Netflix generates **6.5x more revenue** than peak Blockbuster, with **1/6th the employees**. Revenue per employee is **42x higher**. Netflix's largest discipline is engineering (~3,480 employees, 25% of headcount), followed by marketing and product (~2,600, 19%). The entire workforce fits in a few office buildings; Blockbuster needed 9,094 retail locations.

**What happened**: Netflix replaced Blockbuster's labour-intensive distribution model (store clerks, shelf stockers, physical logistics workers) with capital-intensive digital infrastructure (servers, CDN networks, recommendation algorithms, content delivery systems). The physical capital was different too — Blockbuster's stores were depreciating retail real estate; Netflix's capital is server farms and software that improve with scale.

### Case Study: Google/Alphabet — Revenue Per Employee

**Alphabet (2024-2025)**:
- Revenue per employee: **$2.20 million** (FY2025), up from $1.92M in 2024
- Five-year average (2021-2025): **$1.77 million**, median $1.68M
- This is **~5x the Communication Services sector average** of $0.41M per employee

**Comparison with traditional companies**: The sector average is $0.41 million with a standard deviation of $0.38 million. Alphabet's figure of $2.20M is multiple standard deviations above, demonstrating the extreme leverage that software-and-algorithm capital provides over human labour.

**Why Google is so efficient**: Most of Google's revenue comes from automated advertising auctions — algorithms matching advertisers to users in real-time across billions of searches. The marginal cost of serving one more search query or one more ad is near zero. This is a production function where capital (algorithms, data centres, accumulated training data) has almost completely substituted for the labour that traditional advertising required (sales teams, media buyers, campaign managers).

### Case Study: Agriculture — One Farmer Feeding the World

The most dramatic long-run transformation in any industry's production function:

**People fed per farmer**:
- **1800s**: 3-5 people
- **1900**: ~4 people (with 41% of workforce in farming)
- **1940**: 19 people
- **1970s**: ~50 people
- **2024**: **155-168 people**

**Output growth**: US agricultural output nearly **tripled between 1948 and 2017** while agricultural employment fell from 40% of the workforce to under 2%. Output grew at an average rate of **1.53% per year** between 1948 and 2017, with total input use approximately flat — meaning virtually all growth came from total factor productivity (technology, better seeds, fertilisers, mechanisation, GPS-guided precision agriculture).

**Farmland**: Between 1992 and 2012, US farmland decreased by 31 million acres (roughly the area of New York state), yet output continued to rise.

**Capital substitution**: Tractors replaced horses and manual labour. Combine harvesters replaced teams of reapers. GPS-guided planters and sprayers optimise seed placement and chemical application to the square metre. Drones monitor crop health. Automated irrigation systems respond to soil moisture sensors. The capital investment per farm has increased enormously while the labour input has collapsed by over 95%.

---

## 3. The National/Government Production Function

### GDP as Output: Y = A * f(K, L)

At the national level, the production function becomes the Solow growth model's core equation. Y is real GDP, K is the national capital stock (factories, infrastructure, equipment, software), L is the labour force (adjusted for human capital), and A is total factor productivity (TFP) — the "technology" residual that captures everything that makes K and L more productive.

### The United States: Four Economic Eras

The US labour force composition tells the story of four production function regimes:

**Agricultural era (~1800)**:
- ~66% of workers in agriculture
- Capital: hand tools, animal power, simple ploughs
- The production function was land-intensive — output scaled primarily with acreage and labour

**Industrial era (1880-1950)**:
- In 1880, agricultural workers outnumbered industrial workers 3:1
- By 1920, the numbers were approximately equal
- Manufacturing employment expanded 4x from 2.5 million to 10 million workers (1880-1920)
- By 1900: ~40% agriculture, growing manufacturing share
- Capital deepening: factories, steam power, railroads, electrification

**Services era (1950-2000)**:
- Agriculture fell from ~40% (1900) to 10% (1950) to 2% (2000)
- Service sector rose from 31% (1900) to **78% (1999)**
- Manufacturing peaked and began declining as a share of employment
- Capital: office buildings, telecommunications, early computing

**Knowledge/Digital era (2000-present)**:
- **2023 breakdown**: Agriculture 1.57%, Industry 19.34%, Services **79.09%**
- Capital: software, data centres, algorithms, AI systems
- The fastest-growing "capital" is intangible — software, data, trained AI models

### China: The Greatest Capital Deepening in History

China's transformation from 1980 to 2020 represents the most dramatic capital deepening any nation has ever undertaken:

**GDP growth**:
- Average annual GDP growth 1979-2010: **9.91%**
- Historical high: **15.2%** (1984)
- Average since 1990: nearly **9% per year**, sometimes exceeding 14%
- GDP in current US$: rose from ~$191 billion (1980) to **$14.7 trillion (2020)** — a ~77x increase

**Capital formation**:
- Gross capital formation has been maintained at close to **45% of GDP** — roughly double the US rate and unprecedented in economic history
- Gross fixed capital formation (GFCF) stood at **42% of GDP** in 2020 and 2021
- This rate started to decline after 2010, but remains far above global averages

**Manufacturing dominance**:
- In 2024, value-added industrial output accounted for nearly **37% of China's GDP** — more than double the United States' 17.3%
- China's nominal GDP surpassed Italy (2000), France (2005), UK (2006), Germany (2007), Japan (2010), and the Eurozone (2018)
- By PPP, China surpassed the US in 2014

**The significance**: China's capital deepening strategy — investing ~45% of GDP in physical capital — is the purest modern example of moving along the production function by increasing K/L. Carnegie Endowment research has argued that China now needs institutional reform rather than additional capital deepening, suggesting diminishing returns to the pure capital-accumulation strategy.

### Japan: The Post-War Miracle (1945-1990)

Japan's recovery and growth is the textbook case of capital accumulation + technological catch-up:

**Growth rates**:
- Average annual GDP growth 1956-1973: **9.3%**
- Average throughout the 1960s: **~10% per year**
- The Income Doubling Plan (1960) targeted 7.2% annual growth; actual growth averaged **over 10%**, doubling the economy in less than 7 years
- GDP grew from **$91 billion (1965)** to **$1.065 trillion (1980)**

**Savings and investment** (the engine of capital deepening):
- Average domestic savings 1960-1971: **36.1% of national income** (vs 15.8% in the US over the same period)
- Gross private savings rose from 16.5% of GNP (1952-54) to **31.9%** (1970-71)
- Investment in capital equipment: averaged >11% of GNP prewar, rose to ~20% in the 1950s, and **exceeded 30%** in the late 1960s and 1970s
- Personal savings/disposable income averaged **18.3%** during 1959-1970 (vs 12% Germany, 7% US)

**Technological catch-up**: After the war, Japan had lost more than a quarter of its industrial capacity. This was, paradoxically, an advantage — Japan could adopt the latest technologies without waiting for older assets to depreciate. Japan imported advanced technologies, adapted them, and combined them with its exceptionally well-educated workforce.

### South Korea: Poorest to Powerhouse in One Generation

The most compressed national transformation in economic history:

**GDP per capita**:
- **1960**: $79 (one of the poorest countries in the world)
- **1962**: $103.88
- **1989**: $5,438.24
- **2006**: Crossed $20,000
- **2020**: **$31,721** — a **400x increase** from 1960 in nominal terms

**Growth rates**: Real GDP expanded by an average of more than **8% per year**, from $2.7 billion (1962) to $230 billion (1989), breaking the trillion-dollar mark in the early 2000s.

**Investment in human capital and R&D**:
- Government education spending: averaged **3.63% of GDP** from 1970-2021
- R&D spending: reached **5.21% of GDP** in 2022 — second highest in the world after Israel
- The chaebols (Samsung, Hyundai, LG, SK) were the vehicle for technology development, with generous government support since the early 1960s

**Samsung as microcosm**: Founded in 1938 as a food-trading company. Entered electronics in 1969 (black-and-white TVs). Achieved the world's first 64MB DRAM (1992), 256MB DRAM (1994), 1GB DRAM (1996), and first 8GB NAND flash (2004). Samsung Group's revenue has reached **~23% of South Korea's GDP**. This trajectory — from dried fish exporter to world-leading semiconductor manufacturer — is the firm-level equivalent of South Korea's national transformation.

### Government Spending as Capital in the Production Function

**Infrastructure spending** acts as capital that multiplies private-sector labour productivity:
- The fiscal multiplier for public investment is typically around **1.5** — meaning each dollar of public investment generates $1.50 of economic activity. For infrastructure specifically, the estimated multiplier is **1.6**.
- These multipliers are significantly higher during economic downturns than during booms.
- Changes in road infrastructure are associated with larger productivity changes in vehicle-intensive industries.
- Broadband internet access increases the probability of employment by **3.1-13.2%** in Sub-Saharan African countries.
- A 10% increase in market access results in **2.9-6.5% increase in employment**, with the largest impact in commerce and services.

**Education spending** as human capital formation:
- For every $1 invested in education, economies can see **$10-$15 generated** in economic growth over time.
- One standard deviation improvement in test scores (equivalent to ~3-4 years of additional schooling) is associated with a **2-percentage-point higher** average annual GDP growth rate over 40 years.
- While 24% of cross-country GDP variation is explained by school attainment differences, this rises to **~40% when cognitive skills** are considered.
- A study across 38 OECD countries (1995-2021) found that workforce segments with higher education positively impact GDP growth.

**R&D spending** as technology creation:
- A 1% of GDP increase in total R&D expenditure over five years raises the average TFP growth rate by **5.0 to 7.7 percentage points**.
- The lag between R&D spending and GDP growth averages **11 years**.
- Government-funded nondefence R&D leads to significant productivity increases, but with an **~8-year delay** — after which productivity rises steadily and remains elevated for at least 15 years.
- Defence R&D does not drive economic growth in the same way as nondefence R&D.
- R&D knowledge has positive **spillovers** across firms, industries, and regions because it is non-rival — one firm's R&D benefits others.
- Corporate R&D rate of return is approximately the same size as returns on conventional capital investments, but with much larger social returns due to spillovers.

---

## 4. What Actually Happened When Machines Changed Production Functions

### The Luddites (1811-1816): What Were They Actually Protesting?

**The common misconception**: The Luddites were ignorant workers afraid of progress.

**The reality**: The Luddites were skilled textile workers — framework-knitters, croppers, handloom weavers — protesting specific economic abuses:
- **Wage-cutting** by manufacturers
- Use of **unapprenticed youths** to undercut skilled workers' wages
- Deployment of **"wide frames"** that produced cheap, inferior-quality goods
- Circumvention of **standard labour practices** of the time

They were not opposed to machines per se — many were skilled machine operators. They attacked manufacturers who were using new machinery specifically to de-skill and underpay work. The movement began in Arnold, Nottinghamshire, on 11 March 1811 and spread rapidly.

**The context**: The Napoleonic Wars had created harsh economic conditions — poor harvests, trade disruption, inflation. The Luddites were protesting the *distributional consequences* of technological change, not technology itself.

**What happened to textile workers in the medium term?**

The story is captured by the concept of **"Engels' Pause"** (coined by economic historian Robert C. Allen):

- **1780-1840**: Output per worker rose by **46%**, but real wages rose by only **12%**. Workers were producing far more wealth while their compensation remained largely flat.
- **The profit rate doubled** during this period. The share of profits in national income expanded at the expense of labour and land.
- **Handloom weavers** experienced catastrophic decline: they numbered 37,000 in 1780, surged to 240,000 by 1820 as demand for textiles grew, then collapsed to 43,000 by 1850. Their wages peaked in 1805 but fell to barely a quarter of that level by 1830.
- Despite real wages nearly halving, **hundreds of thousands of people remained in the handloom weaving profession** — a vivid illustration of labour market friction and the absence of alternative employment.

**The long-term resolution**: Between **1840 and 1900**, the pattern reversed — output per worker increased by **90%** and real wages grew by **123%**. The production function eventually delivered wage gains that exceeded productivity gains. But the transition took **60-80 years** from the initial disruption.

**Carl Benedikt Frey's explanation**: The early inventions of the Industrial Revolution were predominantly **labour-replacing** — machines that did what artisans did, but cheaper. The gains accrued to capital owners (industrialists who reinvested in factories and machines) rather than workers. Children tended machines with minimal bargaining power. The distributional consequences were severe and lasted decades.

### US Agriculture 1900-2000: Where Did 38% of the Workforce Go?

**The decline**:
- 1900: **41%** of the workforce in agriculture
- 1945: 16%
- 1950: 10%
- 1970: 4%
- 2000: 2%
- 2023: **1.57%**

**Food output**: Agricultural output nearly **tripled** between 1948 and 2017. The USDA notes that "even as the amount of land and labor inputs used in farming declined, total farm output more than doubled between 1948 and 2013."

**Where did the workers go?**

**Phase 1: Agriculture to Manufacturing (1880-1960)**
- In 1880, agricultural workers outnumbered industrial workers **3 to 1**
- By 1920, they were approximately **equal**
- Manufacturing employment expanded 4-fold from **2.5 million to 10 million** (1880-1920)
- The largest shift was the expansion of manufacturing employment from 14% to almost 25% of the workforce

**Phase 2: Manufacturing to Services (1960-present)**
- Service sector employment rose from **31% (1900)** to **78% (1999)**
- White-collar administrative and clerical positions expanded massively
- New categories: retail, healthcare, education, finance, professional services, IT

**The pattern**: Over two centuries, American labour markets accomplished a massive redistribution — first out of agriculture into manufacturing, then from manufacturing into services. At each stage, the displaced sector's productivity gains (from capital substitution) freed up labour for new sectors that didn't previously exist at scale.

**Total employment**: Critically, total employment **never fell** during these transitions. The US labour force grew continuously even as individual sectors shed workers. New sectors absorbed the displaced workers — often at higher wages, though with painful transition periods.

### Bank Tellers and ATMs: The Counter-Intuitive Case

James Bessen's research documented one of the most instructive cases in the history of automation:

**The expectation**: ATMs would eliminate bank teller jobs.

**What actually happened**:
- From the 1970s through 2010, approximately **400,000 ATMs** were installed across the United States
- During the same period, bank teller employment grew from around **500,000 to nearly 600,000**

**Why?**
1. **ATMs reduced the operating cost of a bank branch**: The number of tellers needed per branch fell from **20 to 13** between 1988 and 2004.
2. **Cheaper branches meant more branches**: With lower per-branch costs, banks opened more locations to compete for market share. Bank branches in urban areas increased **43%**.
3. **The teller's role changed**: As ATMs automated routine transactions (cash withdrawal, deposits, balance enquiries), the remaining work that tellers performed became more valuable. Banks pushed tellers into **"relationship banking"** — serving small business customers, selling financial products, and providing personalised advice.
4. **The net effect**: More branches x fewer tellers per branch = more tellers overall. Plus, the tellers' jobs shifted from routine transaction processing to higher-value advisory work.

**The generalised lesson**: When automation reduces the cost of a *unit of production* (a bank branch), demand for that unit can expand enough to increase total employment — even as employment per unit falls. This is a specific manifestation of the **scale effect** overpowering the **substitution effect**.

### The Computer Revolution and Solow's Paradox (1980-2020)

**The paradox (1987)**: Robert Solow's quip that "you can see the computer age everywhere, except in productivity statistics" captured a genuine puzzle. Despite massive corporate IT spending through the 1970s and 1980s, measured productivity growth remained stubbornly low (1.0-1.5% annually).

**What changed (1995-2005)**: Productivity growth surged to **2.8% per year** — a 1.5-percentage-point increase over the previous decades. This "productivity boom" was concentrated in the decade from 1995 to 2005.

**Why the delay? Brynjolfsson's crucial insight**: Erik Brynjolfsson and colleagues identified the key mechanism — IT investments only produced productivity gains when combined with **complementary organisational changes**:
- Redesigned business processes
- Flattened management hierarchies
- Retrained workforces
- New performance measurement systems
- Enterprise resource planning (ERP) systems
- Supply chain reorganisation

**The J-curve**: When firms invest in IT, measured productivity initially *falls* as resources are diverted to reorganisation, training, and process redesign. Only after these complementary investments mature (typically 2-5 years) do productivity gains appear. Firms that invested in IT *without* reorganising saw no gains.

**Where the gains materialised**: A large share of productivity gains outside the IT equipment industry itself appeared in **retail, wholesale, and finance** — sectors that had most thoroughly reorganised around IT. The gap between "leaders and laggers" started widening in 1995.

**Implications for AI**: A 2026 Fortune article notes that thousands of executives are not yet seeing an AI productivity boom — echoing the IT-era paradox. The historical precedent suggests that AI's productivity impact may similarly require years of complementary organisational investment before appearing in aggregate statistics.

---

## 5. The Construction Industry: A Case Study in FAILED Capital Substitution

### The Scale of the Problem

**Five decades of decline**: Real output per worker in construction in 2020 was more than **30% lower** than in 1970, following one of the most persistent productivity declines in any major industry. Since 1965, labour productivity in US construction has been falling at an average pace of **0.6% per year**, while productivity in the wider economy has been growing at about **1.6% per year**.

**The divergence from manufacturing**:
- In value added per hour worked between 1947 and 2010: Construction improved by a factor of **1.1x**; agriculture improved by **16.1x**; manufacturing improved by **8.6x**.
- Manufacturing productivity ended up about **3.6 times higher** than construction productivity by 2010.
- Auto industry: productivity rose from **4.8 cars per employee per year** (1939) to **~25** (2020).
- Construction: effectively flat or declining over the same period.

### Why Has Construction Failed to Achieve Capital Deepening?

**1. Industry fragmentation**:
- **83-94% of construction firms** employ fewer than 20 people
- In residential construction and specialty trades, **more than half** have fewer than 5 employees
- Construction productivity could be **60% higher** if firm sizes matched those in manufacturing
- Firms with 500+ employees produce **more than 4x as many units per employee** as the smallest firms
- Australian data: firms with 200+ employees generate **86% more revenue per worker** than firms with 5-19 employees
- If Australian construction firm sizes matched manufacturing, the industry would produce **12% ($54 billion) more revenue per year** without additional labour

**2. Collapse in innovation**:
- Patenting activity in construction **stagnated after 1970**, while manufacturing patents continued to grow
- Corporate R&D expenditure as a fraction of revenues is **at least 10x higher in manufacturing** than in construction
- Smaller firms have reduced incentives to invest in R&D because benefits cannot be spread across enough projects

**3. Regulation and market structure**:
- The industry is extensively regulated, highly dependent on public-sector demand, and extremely cyclical
- There is a negative association between productivity growth and measures of housing supply regulation (measured by the Wharton Residential Land Use Regulatory Indexes)
- Building codes, permitting processes, and zoning restrictions create barriers to standardisation and prefabrication

**4. Site-specific nature of work**:
- Unlike manufacturing, each construction project is essentially a prototype built at a unique location
- Weather, soil conditions, local regulations, and site access all vary
- This makes factory-style standardisation fundamentally harder

### The Opportunity Cost

**McKinsey's estimate**: If construction-sector productivity were to catch up with that of the total economy, this would boost the sector's value added by an estimated **$1.6 trillion**, adding about **2% to global GDP**. This would meet about half of the world's annual infrastructure needs.

**Housing affordability implications**: Every third urban household globally cannot afford decent housing at market rates, with the total affordability gap amounting to **$650 billion per year**. Productivity improvements could allow construction of more, higher-quality structures at lower cost, directly addressing this crisis.

**McKinsey's path to improvement**: Acting in seven areas simultaneously could boost productivity by **50-60%**:
1. Reshaping regulation
2. Rewiring the contractual framework
3. Rethinking design and engineering processes
4. Improving procurement and supply-chain management
5. Improving onsite execution
6. Infusing digital technology and advanced automation
7. Reskilling the workforce

### Why Disruption Attempts Haven't Scaled

**Modular/prefabricated construction**:
- Barriers include regulatory misalignment, financing hurdles, transport logistics, and conservative industry culture
- Prefab requires upfront capital investment in factory capacity that small, fragmented firms cannot justify
- Transport constraints limit the size of prefabricated modules, constraining design flexibility

**3D printing in construction**:
- Current technology addresses at most **45% of total building cost** (structural walls/foundations only — not finishing, windows, doors, plumbing, electrical, HVAC)
- 60% of construction firms cite **workforce skills** as a critical limitation to implementing 3D printing
- Limited availability of scalable, cost-effective, printable materials
- Underutilisation of expensive equipment can **eliminate the cost advantage** entirely
- Building codes and standards have not been updated for 3D-printed structures

**Robotics**:
- Site variability makes it harder to deploy robots than in controlled factory environments
- Each construction site presents unique challenges (terrain, weather, access) that factory robots are not designed to handle
- The fragmented nature of the industry means no single firm has the scale to justify large robotics R&D investments

### The Fundamental Insight

Construction represents a **counter-example** to the narrative that technology inevitably transforms production functions. The conditions for successful capital deepening — large firms with R&D capacity, standardised products, controlled production environments, supportive regulation, and sustained investment in innovation — are largely absent in construction. The result is that an industry employing tens of millions of people worldwide operates with productivity levels barely above those of the 1970s, while manufacturing, agriculture, and services have undergone multiple productivity revolutions.

The construction case demonstrates that the production function is not rewritten by technology alone — it requires an institutional and market structure that allows capital to effectively substitute for and complement labour. Where those structures are absent, the production function remains stuck.

---

## Summary: Key Statistics Reference Table

| Metric | Historical | Current | Change Factor |
|--------|-----------|---------|---------------|
| Scribe output | 3 pages/day (1400) | 3,600 pages/day printing press (1450s) | 1,200x |
| Handwriting speed | 30 WPM (1853 record) | 60-80 WPM typewriter (1900) | 2-3x |
| US farm workers as % of workforce | 41% (1900) | 1.57% (2023) | -96% |
| People fed per US farmer | 3-5 (1800s) | 155-168 (2024) | ~40x |
| Bank tellers (US) | 500,000 (1970s) | 600,000 (2010) | +20% (despite 400K ATMs) |
| Blockbuster employees | 84,300 (2004) | Netflix: 14,000 (2024) | 6x fewer for 6.5x revenue |
| Netflix revenue per employee | N/A | $3.0M (2024) | 42x Blockbuster's ~$71K |
| Alphabet revenue per employee | N/A | $2.20M (2025) | 5x sector average |
| Amazon "click to ship" | 60-75 min (pre-Kiva) | 15 min (post-Kiva) | 75-80% reduction |
| Amazon operating cost per warehouse | Baseline | -20% (~$22M saving) | With Kiva robots |
| GitHub Copilot coding speed | Baseline | +55.8% (controlled study) | 2023 experiment |
| AI code generation share | 0% (pre-2021) | 46% average, 61% Java (2025) | New category |
| China GFCF/GDP | ~30% (1980) | 42% (2020) | Sustained >40% for decades |
| China GDP | ~$191B (1980) | $14.7T (2020) | ~77x |
| Japan GDP growth | 9.3% avg (1956-73) | <1% (1990s-2020s) | Miracle then stagnation |
| Japan savings rate | 36.1% of national income (1960-71) | ~28% (recent) | US was only 15.8% |
| South Korea GDP/capita | $79 (1960) | $31,721 (2020) | ~400x |
| South Korea R&D/GDP | Minimal (1960s) | 5.21% (2022) | 2nd highest globally |
| Construction productivity | Baseline (1970) | -30% (2020) | 50-year decline |
| Construction vs manufacturing value-added growth | 1.1x (1947-2010) | vs 8.6x manufacturing | 8x divergence |
| Engels' Pause: output vs wages | Output per worker +46% (1780-1840) | Wages +12% same period | Gap: 34 percentage points |
| Post-Pause recovery | Output +90% (1840-1900) | Wages +123% same period | Workers eventually gained more |
| Solo-founded startups | 22% (2015) | 38% (2024) | +73% |
| US productivity growth | 1.0-1.5%/yr (1970s-1994) | 2.8%/yr (1995-2005) | IT boom doubled it |
