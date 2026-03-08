In March 2026, Anthropic published a radar chart that should have alarmed every knowledge worker on the planet.[^1] It showed two overlaid shapes across twenty occupational categories: a large blue area representing the share of job tasks that AI could theoretically perform, and a much smaller red area representing the tasks AI is *actually* being used for. In computer and math occupations, the theoretical coverage reached 94%. The observed coverage was 33%. In legal occupations, the gap was even wider. In education, arts, architecture, and the sciences — the same pattern. Vast theoretical capability. Modest actual deployment.

Most commentary on this chart focuses on the gap and asks: when will the red catch up to the blue? When will AI's actual impact match its theoretical potential? This is the wrong question. It assumes that AI's impact on the economy is a function of how many individual tasks it automates — that the red area simply needs to expand until it fills the blue.

This is what I call the **first-order** view of AI. It is not wrong. But it is radically incomplete. The first-order view sees AI as a tool that does tasks faster. The second-order view sees AI as a force that restructures entire industries — changing which firms exist, how they are organised, what products are possible, and where the boundaries of a company begin and end.

The first-order effects are the ones the radar chart measures. The second-order effects are the ones that will actually reshape the economy. And they are, by definition, invisible to task-level analysis.

---

## First-Order: AI Does the Task

First-order AI effects are straightforward. A human performs a cognitive task — writing a report, reviewing a contract, estimating a construction project, diagnosing a skin lesion. An AI system performs the same task faster, cheaper, or at comparable quality. The human is either displaced or augmented.

This is what Eloundou et al. measured in their landmark 2023 paper "GPTs are GPTs," estimating that 80% of the U.S. workforce could have at least 10% of their tasks affected by large language models.[^2] It is what Massenkoff and McCrory measured with real usage data in 2026, finding that computer programmers already have 75% of their tasks covered by AI, customer service representatives 70%, and data entry workers 67%.[^1]

The economics of first-order effects are well understood. Daron Acemoglu, applying Hulten's theorem, estimated that task-level AI automation would produce only **0.93–1.56% of GDP growth over ten years** — significant but not transformative.[^3] The gains are real but bounded: you can only make each task so much faster before the bottleneck shifts elsewhere.

First-order effects are also what most companies are investing in right now. A law firm buys an AI tool that reviews contracts faster. An accounting firm deploys AI that flags anomalies in audits. A software company gives its engineers Copilot. These are productivity improvements within existing organisational structures. The firm is the same firm, doing the same things, slightly faster.

This is not where the revolution happens.

---

## Second-Order: AI Restructures the System

Second-order AI effects occur when AI capability changes not just how tasks are performed, but how entire industries are structured — which activities a firm performs internally, what products are possible, and how value chains are organised.

The academic literature has been circling this distinction for years. Agrawal, Gans, and Goldfarb argued in *Power and Prediction* (2022) that AI's disruptive potential comes not from improving individual decisions but from **redesigning entire systems of interdependent decisions**.[^4] Brynjolfsson, Rock, and Syverson described the "Productivity J-Curve" — a period where measured productivity actually *declines* as organisations invest heavily in complementary changes (business process redesign, new products, human capital) before the payoff arrives.[^5]

The historical analogy is electricity. The lightbulb was invented in 1879. Electric motors accounted for less than 5% of factory mechanical drive by 1900. It took until the **1920s** — over forty years — for electrification to show large productivity gains. The delay was not because the technology didn't work. It was because factories had been designed around a centralised steam engine with a single driveshaft and belt system. To exploit electricity, you had to redesign the entire factory — single-storey layouts, distributed power points, flexible production lines. The technology was first-order ready in 1880. The second-order transformation took until 1920.[^6]

AI is in the same position today. The technology is first-order ready — it can perform individual tasks at or above human level across dozens of occupations. The second-order transformation — redesigning firms, supply chains, products, and industries around AI capability — is just beginning.

Second-order effects take three forms:

**Vertical integration.** AI reduces the cost of internal coordination, allowing firms to bring activities in-house that were previously outsourced. When AI can manage complexity across design, manufacturing, logistics, and sales simultaneously, the transaction costs that once made outsourcing rational can flip — and a firm that controls the entire stack gains structural advantages that modular competitors cannot match.

**New product categories.** AI enables products that could not exist without it. These are not faster versions of existing products — they are fundamentally new value propositions that redefine what an industry makes.

**Competitive moats.** First-order AI is a tool anyone can buy. Second-order AI creates self-reinforcing loops — data flywheels, vertical integration advantages, AI-native product architectures — that compound over time and become structurally unreachable for competitors who treat AI as a bolt-on.

The clearest proof case for all three is Tesla.

---

## Tesla: The Proof Case

### First-Order AI at Tesla

Tesla uses AI in ways any large manufacturer might: computer vision for quality control on the production line, AI-assisted software development, predictive maintenance that has reduced unexpected machine failures by over 30%.[^7]

The most dramatic first-order effect was FSD v12, which replaced over **300,000 lines of explicit C++ code** with end-to-end neural networks.[^8] Three hundred thousand lines of hand-written rules — encoding human driving logic as if-then-else statements — collapsed into roughly 2,000 lines that simply activate and manage neural networks trained on driving data. This is AI doing a task (writing driving software) that humans used to do, at a scale and approach that was previously impossible.

These are impressive applications. They are also, in the framework of this essay, table stakes. Any well-capitalised company can deploy AI for quality control and code generation. What makes Tesla structurally different is the second-order effects.

### Second-Order: Vertical Integration Driven by AI

Tesla designs its own AI inference chips because no off-the-shelf solution delivers the right performance-per-watt for real-time autonomous driving on eight camera streams. The custom FSD chip (HW3, 2019) was followed by HW4 (2023), HW4.5 (2025), and the forthcoming AI5 — each generation designed specifically for Tesla's neural network architecture.[^9]

This is a second-order effect: the AI workload *defined* the hardware requirement, which *forced* vertical integration into chip design. Tesla didn't choose to design chips because it wanted to be a chip company. It had to design chips because no external supplier could optimise for its specific AI inference workload at the required cost and power envelope.

The same logic drove Tesla to build its own training infrastructure. The Cortex supercluster — 50,000 NVIDIA H100 GPUs plus 20,000 custom hardware units, requiring 130 megawatts of power — went live in Q4 2024, with a 500-megawatt expansion under construction.[^10] AI-related capital expenditure reached approximately $5 billion in 2024, representing 44% of all Tesla capex.[^11]

Tesla manufactures its own battery cells (4680 format) with AI-optimised production processes. It controls the entire software stack from vehicle operating system to cloud infrastructure, with no dealer network intermediary. It trains its own neural networks on proprietary fleet data. It is building humanoid robots (Optimus) that reuse the same neural architecture developed for autonomous driving.[^12]

Each of these decisions was *forced* by AI capability requirements. The AI workload demands specific hardware, specific data pipelines, specific software architectures, and specific manufacturing processes. A company that outsources any of these — buys chips from Mobileye, ADAS software from Bosch, sells through franchised dealers who block data access — cannot enter the self-reinforcing loop that Tesla has built.

### Second-Order: New Product Categories

A robotaxi is not a faster car. It is a product category that **cannot exist without AI**. An autonomous ride-hailing service — launched in Austin in June 2025, with driverless testing beginning in December 2025 — transforms a car from a depreciating asset that sits parked 95% of the time into a revenue-generating asset that works while the owner sleeps.[^13]

S&P Global projects robotaxi revenue could reach $75 billion by 2030, representing 45% of Tesla's automotive revenue.[^14] This is not an incremental improvement to an existing product. It is a new product made possible by second-order AI integration.

The energy division tells the same story. Autobidder, Tesla's AI-driven platform, autonomously trades electricity and optimises battery assets across grid markets. Energy revenue grew from $6 billion (2023) to $10 billion (2024) to $13 billion (2025) — and at ~22% gross margins, now exceeds the profitability of the automotive business on a margin basis.[^15]

### The Unreachable Moat

The second-order effects create a flywheel: more vehicles sold generates more fleet data (8.4 billion FSD miles and counting), which trains better neural networks, which enables new products (robotaxi, Optimus), which funds more AI infrastructure ($5+ billion/year), which produces better chips and manufacturing processes, which makes vehicles cheaper and better, which sells more vehicles.[^16]

Traditional automakers are structurally unable to enter this loop. Ford and VW's Argo AI shut down in 2022. GM's Cruise shut down in 2024 after burning over $10 billion.[^17] Detroit is 0-2 in autonomous driving — not because they lacked talent or capital, but because they treated AI as a first-order bolt-on to an existing business model rather than a second-order force that reshapes the entire company.

---

## Home Building: The Frontier Case

If Tesla demonstrates what second-order AI effects look like in a mature industry, residential construction shows what they could look like in an industry that hasn't even experienced first-order effects yet.

### The Productivity Crisis

Construction is the second-least digitised industry globally. IT spending accounts for less than 1% of revenue. R&D spending is similarly negligible.[^18]

The numbers are extraordinary: construction labour productivity has **declined more than 30%** since 1970, while aggregate U.S. labour productivity tripled over the same period. Since 1945, productivity in manufacturing has grown by as much as 1,500%. Construction has barely moved.[^19]

A 2024 NBER paper by D'Amico, Glaeser, Gyourko, Kerr, and Ponzetto identified the dominant cause: **land-use regulation**. A 1% increase in regulation intensity lowers annual construction productivity growth by 0.6–0.9 percentage points. Increased regulation since the 1960s has reduced annual productivity growth by approximately 0.7 percentage points — offsetting nearly all of the estimated 0.8 percentage point boost from technological change. Regulation also keeps firms small: if residential construction firms matched the size distribution of manufacturing, the sector would be approximately **60% more productive**.[^20]

This is an industry where the production function has been frozen for half a century. And 45% of construction firms have **zero AI implementation**.[^21]

### First-Order AI in Construction

The first-order effects are already emerging and are substantial:

AI-powered estimating tools like Togal.AI achieve 98% accuracy on takeoffs while being 80% faster, allowing estimators to bid on three to five times more projects without additional staff.[^22] AI scheduling systems like ALICE Technologies simulate millions of construction schedules in minutes, optimising for cost, time, and resource constraints.[^23] AI code compliance checking — tools like AutoReview.AI — can reduce plan review times from **weeks to 30 minutes**, directly attacking one of the biggest friction points in housing delivery.[^24]

On site, computer vision safety monitoring detects missing PPE, unsafe behaviours, and restricted zone breaches in real time, with adopters reporting incident reductions of 40–50%.[^25]

These are genuine productivity gains. But they are first-order: AI performing existing tasks within the existing fragmented, site-built, regulation-heavy construction system. They do not change the system itself.

### Second-Order: The AI-First Builder

The second-order question is: what would a "Tesla of home building" look like?

The answer is not a construction company that uses AI tools. It is a technology company that builds houses — one that uses AI to vertically or horizontally integrate the design-to-delivery pipeline, define new housing products that could not exist without AI, and create competitive moats that traditional builders cannot cross.

The modular and prefab construction wave of 2018–2023 attempted this without AI and mostly failed. Katerra raised over $2 billion and went bankrupt in 2021 — trying to vertically integrate by acquiring suppliers, hiring traditional construction talent, and scaling to a national market simultaneously.[^26] Veev raised $647 million and shut down in 2023. Entekra dissolved in 2023.

But the survivors are instructive. They share a common pattern that looks remarkably like Tesla's playbook:

**Software-defined product.** Cover, a Los Angeles-based builder, runs every home through proprietary software that handles design, engineering calculations, building code compliance, manufacturing specifications, and permitting — while the customer simply makes choices in a configurator. The software *is* the product; the house is the output.[^27]

**Horizontal integration, not vertical.** Aro Homes — incubated by Eric Schmidt's Innovation Endeavors, with first homes completed in September 2025 — explicitly learned from Katerra's failure. It owns the design-to-factory pipeline and the customer relationship but uses an ecosystem of specialised suppliers rather than acquiring its entire supply chain.[^28]

**Factory as platform.** Harbinger Homes (formerly Factory OS) produces over 600 homes per year from a single 275,000 sq ft facility — with factory labour productivity roughly **2x** site-built construction, timelines 50% faster, and costs 10–20% lower.[^29]

**Direct-to-consumer.** Bypass the developer-contractor-realtor chain entirely. Like Tesla eliminating the dealer network, the AI-first builder maintains a direct relationship with the homebuyer — and critically, retains the data from every home it builds to improve the next one.

### Second-Order: AI-First Housing Products

The most exciting second-order effect is new product categories that cannot exist without AI.

**Mass customisation.** Every home unique, but factory-efficient. Parametric design systems use AI to generate thousands of optimised layouts for a specific site, balancing cost, energy performance, structural requirements, and local building codes simultaneously. Recent research demonstrated a 15.8% reduction in lifecycle costs and a 21.2% decrease in energy consumption through AI-driven parametric design for industrialised construction.[^30]

**Homes as energy systems.** A factory-built home can integrate solar, battery storage, heat pumps, and intelligent energy management at the panel level — far more cost-effectively than retrofitting. The home becomes an energy management system with living space attached, not a living space with some smart devices bolted on. When every home is an energy node, the grid itself is transformed.

**Design-for-compliance.** Instead of designing a home and then checking it against building codes (a process that takes weeks to months), AI enables every design to be *born compliant*. The constraints of the local building code, zoning regulations, energy standards, and accessibility requirements are inputs to the generative design process, not post-hoc hurdles. This directly attacks the NBER finding that regulation has neutralised technological productivity gains — not by eliminating regulation, but by making it computationally trivial to satisfy.

### The Australian Test Case

Australia presents the most acute case for second-order AI in home building. The National Housing Accord commits to 1.2 million new homes by mid-2029 — 240,000 per year. Actual delivery in the first year was 174,000, a 27.5% shortfall. The country now needs 255,000 homes per year for the remaining four years to hit the target, and is forecast to fall approximately 262,000 homes short overall.[^31]

Sydney's median house price stands at $1.75 million — 13.8 times median household income, the second most unaffordable housing market in the world after Hong Kong.[^32] Construction costs have risen over 40% since the pandemic. The industry needs 90,000 additional workers by end of 2025, growing to a projected shortfall of **300,000 workers by 2027** — while apprenticeship commencements have fallen 41% since 2022.[^33]

The labour shortage is the critical constraint. You cannot build 255,000 homes per year when you are 300,000 workers short of the labour required. The only way to close that gap is to change the production function — to build more homes per worker. Factory-built modular construction delivers 2x the labour productivity of site-built, with 50% fewer people on site. The Australian government has pledged $54 million to boost prefabricated and modular housing, and CBA is now financing modular homes.[^34]

An AI-first modular builder operating at scale in Australia would address multiple constraints simultaneously: the labour shortage (factory automation requires fewer and different workers), cost (10–30% savings), speed (50% faster), and quality (consistent factory conditions with AI quality control). The question is whether second-order AI effects — the integration of design, manufacturing, compliance, energy systems, and customer relationships into a single AI-driven pipeline — can overcome the regulatory and fragmentation barriers that have kept construction productivity flat for fifty years.

---

## The Pattern

The Anthropic radar chart measures first-order effects — the share of tasks AI can perform. It finds a large gap between capability and adoption and, importantly, **no measurable unemployment effect yet**. The most provocative finding is a ~14% decline in hiring of 22–25 year olds into AI-exposed occupations — not displacement of existing workers, but slowed hiring at the entry level.[^1]

This is exactly what the first-order/second-order framework predicts. First-order effects are incremental. They make existing workers slightly faster and reduce the need for new hires at the margin. They do not restructure industries.

Second-order effects are where the transformation lives. Tesla didn't become the world's most valuable automaker by using AI to speed up existing manufacturing tasks. It became the most valuable automaker by using AI to vertically integrate chip design, training infrastructure, battery manufacturing, software, energy, and robotics into a self-reinforcing system that produces products — robotaxis, energy trading, humanoid robots — that could not exist without AI at the foundation.

The home building industry is where second-order effects are most needed and least developed. An industry with declining productivity, massive labour shortages, a housing crisis, and the lowest digitisation of any major sector is not going to be saved by AI tools that make estimators 80% faster. It will be transformed by AI-first companies that redesign the entire production system — factory manufacturing, parametric design, automated compliance, integrated energy systems, direct-to-consumer delivery — in ways that traditional builders cannot replicate, just as traditional automakers cannot replicate Tesla's AI flywheel.

The first-order view asks: which tasks will AI automate? The second-order view asks: which industries will be rebuilt from the ground up by companies that treat AI not as a tool but as a foundation?

The radar chart shows us where we are. The second-order effects will determine where we're going.

---

[^1]: Massenkoff and McCrory, ["Labor market impacts of AI: A new measure and early evidence"](https://www.anthropic.com/research/labor-market-impacts), Anthropic (March 2026). Uses real Claude usage data mapped to O*NET occupational tasks via the Anthropic Economic Index.
[^2]: Eloundou, Manning, Mishkin, and Rock, ["GPTs are GPTs: An Early Look at the Labor Market Impact Potential of Large Language Models"](https://arxiv.org/abs/2303.10130), *Science* (2024). Originally arXiv 2303.10130 (March 2023).
[^3]: Acemoglu, ["The Simple Macroeconomics of AI"](https://economics.mit.edu/sites/default/files/2024-04/The%20Simple%20Macroeconomics%20of%20AI.pdf), *Economic Policy* 40(121) (2024). Applies Hulten's theorem: GDP effects bounded by fraction of tasks impacted times average cost savings.
[^4]: Agrawal, Gans, and Goldfarb, [*Power and Prediction: The Disruptive Economics of Artificial Intelligence*](https://www.amazon.com/Power-Prediction-Disruptive-Artificial-Intelligence/dp/1647824192), Harvard Business Review Press (2022). Named one of Forbes' Ten Best Business Books of 2022.
[^5]: Brynjolfsson, Rock, and Syverson, ["The Productivity J-Curve: How Intangibles Complement General Purpose Technologies"](https://www.aeaweb.org/articles?id=10.1257/mac.20180386), *American Economic Journal: Macroeconomics* 13(1), 333–372 (2021).
[^6]: Paul David, ["The Dynamo and the Computer: An Historical Perspective on the Modern Productivity Paradox"](https://econpapers.repec.org/RePEc:aea:aecrev:v:80:y:1990:i:2:p:355-61), *American Economic Review* 80(2), 355–361 (1990). Electric motors were <5% of factory drive in 1900; productivity gains didn't appear until the 1920s.
[^7]: [Aicadium](https://aicadium.ai/tesla-increases-productivity-with-computer-vision-ai/), "Tesla Increases Productivity with Computer Vision AI" (2025). Predictive maintenance AI reduced unexpected failures by over 30%.
[^8]: [FredPope.com](https://www.fredpope.com/blog/machine-learning/tesla-fsd-12), "Tesla FSD 12: The Neural Network Revolution." 300,000+ lines of C++ replaced with end-to-end neural networks.
[^9]: [Wikipedia — Tesla Autopilot Hardware](https://en.wikipedia.org/wiki/Tesla_Autopilot_hardware). HW3 (2019, 14nm Samsung), HW4 (2023, 7nm), HW4.5 (2025), AI5 (expected 2027).
[^10]: [Tom's Hardware](https://www.tomshardware.com/desktops/servers/elon-musk-shows-off-cortex-ai-supercluster-first-look-at-teslas-50000-nvidia-h100s), "Elon Musk Shows Off Cortex AI Supercluster" (2024). 50,000 H100 GPUs, 130MW power, scaling to 500MW.
[^11]: [Yahoo Finance](https://finance.yahoo.com/news/tesla-unveils-20-billion-capex-161113987.html), "Tesla Unveils $20 Billion Capex Plan." ~$5B AI-related capex out of $11.34B total in 2024.
[^12]: [Humanoids Daily](https://www.humanoidsdaily.com/news/tesla-ai-chief-details-unified-world-simulator-for-fsd-and-optimus). Tesla VP of AI confirmed the same neural architecture used for FSD will transfer to Optimus.
[^13]: [CNBC](https://www.cnbc.com/2025/06/20/tesla-robotaxi-launch-austin.html), "Tesla Robotaxi Launches in Austin" (June 2025). Driverless testing began [December 2025](https://techcrunch.com/2025/12/15/tesla-starts-testing-robotaxis-in-austin-with-no-safety-driver/).
[^14]: [S&P Global](https://www.spglobal.com/market-intelligence/en/news-insights/research/teslas-robotaxis-could-drive-45-of-automotive-sales-by-2030), "Tesla's Robotaxis Could Drive 45% of Automotive Sales by 2030."
[^15]: [Energy Storage News](https://www.energy-storage.news/tesla-energy-storage-deployments-jumped-in-crucial-ai-transformation-year-company-expects-margin-compression-in-2026/). Energy revenue: $6B (2023) → $10B (2024) → $13B (2025), ~22% gross margins.
[^16]: [Teslarati](https://www.teslarati.com/tesla-fsd-supervised-fleet-passes-8-4-billion-cumulative-miles/), "Tesla FSD Fleet Passes 8.4 Billion Cumulative Miles" (2025).
[^17]: [NPR](https://www.npr.org/2024/12/11/g-s1-37700/gm-to-retreat-from-robotaxis-and-stop-funding-its-cruise-autonomous-vehicle-unit), "GM to Retreat from Robotaxis" (December 2024). Argo AI shut down October 2022; Cruise shut down after $10B+ investment.
[^18]: McKinsey, ["Reinventing Construction Through a Productivity Revolution"](https://www.mckinsey.com/capabilities/operations/our-insights/reinventing-construction-through-a-productivity-revolution). Construction ranks second-last on the McKinsey industry digitisation index; IT and R&D spending both below 1% of revenue.
[^19]: [Richmond Fed Economic Brief 25-31](https://www.richmondfed.org/publications/research/economic_brief/2025/eb_25-31) (August 2025), "Five Decades of Decline in Construction Productivity." Also McKinsey (2017): since 1945, manufacturing productivity up 1,500%, construction flat.
[^20]: D'Amico, Glaeser, Gyourko, Kerr, and Ponzetto, ["Why Has Construction Productivity Stagnated?"](https://www.nber.org/papers/w33188), NBER Working Paper 33188 (2024). Covered by [Goldman Sachs Research](https://www.goldmansachs.com/insights/articles/why-has-productivity-in-the-us-construction-industry-stagnated).
[^21]: [RICS global survey](https://dig.watch/updates/global-survey-reveals-slow-ai-adoption-across-the-construction-industry) (2025): 45% of construction firms report zero AI implementation. [ASCE survey](https://www.asce.org/publications-and-news/civil-engineering-source/article/2025/12/18/architecture-engineering-construction-sector-slow-to-adapt-ai-survey-shows) (December 2025) confirmed the AEC sector remains slow to adopt AI.
[^22]: [Togal.AI](https://www.togal.ai/): 98% accuracy, 80% faster takeoffs. [Beam AI](https://www.ibeam.ai/): saves estimators 15–20 hours/week; contractors bid 3–5x more projects.
[^23]: [ALICE Technologies](https://www.alicetechnologies.com/home): simulates millions of construction schedules in minutes using generative AI.
[^24]: University of Florida [research](https://warrington.ufl.edu/news/ai-review-construction-plans/) found AI plan review reduces permit approval from 30–60 days to 3–5 days. [AutoReview.AI](https://codecomply.ai/) reduces review time to 30 minutes.
[^25]: [ABC Carolinas](https://abccarolinas.org/ai-in-construction-site-safety/): over 43% of US construction firms use AI for site safety; adopters report 40–50% incident reduction.
[^26]: [Fast Company](https://www.fastcompany.com/90643381/this-prefab-builder-raised-more-than-2-billion-why-did-it-crash), "This Prefab Builder Raised More Than $2 Billion. Why Did It Crash?" (2021). Katerra failed by attempting full vertical integration through acquisition.
[^27]: [Freethink](https://www.freethink.com/the-material-world/prefab-cover), "Cover: Prefab Homes." Software handles design, engineering, code compliance, manufacturing specs, and permitting behind a customer configurator.
[^28]: [BuiltWorlds](https://builtworlds.com/news/learning-from-katerra-tesla-aro-homes-is-one-integrated-modular-startups/), "Learning from Katerra: Aro Homes." Incubated by Eric Schmidt's Innovation Endeavors; first home completed September 2025; 90-day build times; net-zero carbon.
[^29]: [Press Democrat](https://www.pressdemocrat.com/2025/12/13/harbinger-homes-factory-os-vallejo-modular-construction/), "Harbinger Homes / Factory OS." 275K sq ft facility in Vallejo, CA; 4,000+ homes since 2018; ~600 homes in 2025. [Industry data](https://www.mesocore.com/blog/prefab-construction-statistics): factory labour productivity 2x site-built; timelines 50% faster; costs 10–20% lower.
[^30]: [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0926580525001864): AI-driven parametric generative design in industrialised construction achieved 15.8% reduction in lifecycle costs and 21.2% decrease in energy consumption.
[^31]: [Architecture AU](https://architectureau.com/articles/australia-is-forecast-to-fall-262000-homes-short-of-its-housing-target-we-need-bold-action/): Australia forecast to fall 262,000 homes short of the 1.2 million target. [IPA](https://ipa.org.au/read/the-federal-governments-national-housing-accord-56000-homes-behind-and-counting): 174,030 homes in year one, 27.5% shortfall.
[^32]: [Pivot PB](https://pivotpb.com.au/is-sydney-the-most-unaffordable-city-in-the-world/): Sydney median house price $1.75 million, 13.8x median household income (second after Hong Kong at 14.4x).
[^33]: [CASU](https://casu.com.au/australias-300000-construction-worker-shortfall-what-it-means-for-businesses-in-2025-2027/): 300,000 worker shortfall by 2027. [HIA](https://hia.com.au/our-industry/newsroom/skills-training-and-workforce/2026/02/national-apprentice-week-shines-a-light-on-trade-skills-shortage): apprenticeship commencements fell 41% since March 2022.
[^34]: [CBA](https://www.commbank.com.au/articles/newsroom/2025/07/Supporting-prefabricated-housing.html): CBA financing modular homes. Australian government pledged $54 million for prefabricated housing.
