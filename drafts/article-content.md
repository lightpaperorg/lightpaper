> Publishing used to require permission. Now it requires a sentence.

## The Old Way

For most of history, getting published meant convincing someone else that your ideas were worth sharing. An editor. A committee. A platform algorithm. The process was slow, gatekept, and designed for a world where distribution was scarce.

Even on the modern web, publishing has friction. Medium puts your work behind a paywall you did not choose. LinkedIn buries it in a feed within hours. WordPress demands you manage hosting, themes, and plugins before you have written a single word. Academic journals take months of peer review for ideas that matter right now.

The result: most ideas never get published. They die in chat windows, Google Docs, and email threads — seen by a handful of people, then forgotten.

## The Prompt That Changes Everything

Imagine this: you have an idea. Maybe it is a technical insight you gained at work. Maybe it is a framework for thinking about a problem. Maybe it is a tutorial that would have saved you three days last month.

You open Claude, Cursor, or any AI assistant connected to [lightpaper.org](https://lightpaper.org) and say:

*Write an article about why microservices are overrated for teams under ten engineers, and publish it.*

That is it. Within seconds:

1. The agent writes a well-structured article with headings, examples, and references
2. It calls `POST /v1/publish` with the content
3. You get a permanent URL like `https://lightpaper.org/why-microservices-are-overrated`
4. The page is live — beautiful typography, OG previews for social sharing, structured data for search engines
5. A quality score tells you exactly how the article rates and what to improve

You went from idea to published author in one prompt. No editor approved it. No algorithm decided whether people would see it. No platform owns it. The URL works forever.

## What Makes This Different

There are plenty of places to put text on the internet. What makes lightpaper different is that it was designed from the ground up for this exact workflow — the moment when a human has an idea and an AI agent turns it into something permanent.

### Permanent URLs

Every article gets a URL that never changes, never expires, and never gets paywalled. A [2024 Pew Research study](https://www.pewresearch.org/data-labs/2024/05/17/when-online-content-disappears/) found that 38% of web pages from 2013 no longer exist[^1]. lightpaper is built to be the opposite of that. Your URL works in ten years the same way it works today.

### Quality Scoring

Every document receives a transparent quality score from 0 to 100, based on four dimensions:

| Dimension | What It Measures | Points |
|-----------|-----------------|--------|
| Structure | Headings, paragraphs, variety | 0-25 |
| Substance | Word count, code blocks, lists, tables | 0-25 |
| Tone | Professional language, no clickbait | 0-25 |
| Attribution | Links, references, footnotes | 0-25 |

This is not a black box. You can see exactly why your article scored what it did, and the agent can revise it to score higher. Most first drafts land around 65-75. With a revision pass focused on adding references and structural variety, 80+ is straightforward.

### Three Formats for Three Kinds of Writing

Not everything should look like a blog post. lightpaper offers three presentation formats from the same markdown:

- **Post** — Clean, modern sans-serif. Perfect for tutorials, how-to guides, and technical writeups. Think [Substack](https://substack.com) or [dev.to](https://dev.to).
- **Paper** — Serif font, numbered headings, abstract box. For research, analysis, and methodology. Think [arXiv](https://arxiv.org).
- **Essay** — Elegant serif, drop cap, pull-quotes. For arguments, narratives, and cultural commentary. Think [The New Yorker](https://www.newyorker.com).

Same content, dramatically different reading experience. The format is just a field in the API call.

### Author Gravity

Anyone can publish, but verified authors rank higher. lightpaper has a [gravity system](https://lightpaper.org/author-gravity-a-trust-system-for-the-agentic-web) that rewards verifiable identity signals:

- Connect LinkedIn → Level 1 (1.1x search boost)
- Add a second identity verification → Level 2 (1.25x boost)
- Verify a credential like a degree → Level 3 (1.4x boost)

This takes about two minutes through the API. No follower counts, no popularity contests — just proof that a real person stands behind the work.

## Who Is This For?

**Developers** who write architecture decision records, technical retrospectives, and framework comparisons that deserve better than a Confluence page.

**Founders** who have insights about their market, their approach, or their failures that would help others — but never get around to writing them up.

**Researchers** who want to share findings faster than academic journals allow, without sacrificing credibility signals.

**Anyone with an idea** who has ever thought they should write about something and then did not, because the friction of setting up a blog or navigating a platform was just enough to kill the momentum.

## The Freedom to Just Ship

lightpaper is built on a simple belief: the world has more good ideas than published articles. The gap is not talent or knowledge — it is friction. Every step between having something to say and having a URL is a chance for the idea to die.

With AI agents and a single API endpoint, that gap shrinks to nearly zero. You think it, you say it, it is published. Permanently. Beautifully. Discoverably.

The old web made everyone a reader. The agentic web makes everyone an author.

## Get Started

You can start publishing in under a minute:

1. **Connect the MCP server** — add your config to [Claude Desktop](https://claude.ai) or [Cursor](https://cursor.com)
2. **Create an account** — the agent walks you through email verification
3. **Publish** — just tell the agent what to write about

Or use the [API directly](https://lightpaper.org/publishing-your-first-document-via-the-api).

Open source: [github.com/lightpaperorg/lightpaper](https://github.com/lightpaperorg/lightpaper)

## References

[^1]: Pew Research Center. "When Online Content Disappears." May 2024. https://www.pewresearch.org/data-labs/2024/05/17/when-online-content-disappears/

[^2]: Bjork, B-C., and Solomon, D. "The publishing delay in scholarly peer-reviewed journals." *Journal of Informetrics*, 7(4), 914-923. 2013. https://doi.org/10.1016/j.joi.2013.09.001

[^3]: Model Context Protocol. "MCP Specification." Linux Foundation. 2025. https://modelcontextprotocol.io

[^4]: llms.txt Standard. "A proposal for a /llms.txt file." 2024. https://llmstxt.org