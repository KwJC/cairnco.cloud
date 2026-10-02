Answer engine optimisation (AEO) is the work of getting your business named when someone asks an AI assistant instead of searching. ChatGPT, Perplexity, Claude and Google's AI Overviews all reply with a short answer that cites a few sources. AEO is about being one of them. It builds on SEO, but the goal is a mention inside the answer, which often comes with no click at all.

We're a two-person tech firm in Singapore whose own site started from zero in September 2026. Everything below comes from the AI companies' own documentation or from something we measured, dated so you can check it.

## Is AEO the same as SEO or GEO?

Close cousins. SEO ranks a page in a list of links. AEO gets a passage lifted into a direct answer. GEO, generative engine optimisation, is the same idea aimed at assistants that write a fresh answer each time. Some call the whole lot AI SEO. Most Singapore AEO agencies sell all three together, so when you compare AEO services, ask what they'll actually do.

One local quirk: Google's suggestions for "AEO Singapore" include customs certification and American Eagle Outfitters, because AEO is also a customs term here. Spell the full name out at least once on any page you want found for it, and expect people to search the American spelling, answer engine optimization, too.

## Are Singapore searches already getting AI answers?

Most of the ones we tried. On 22 September 2026 we ran ten searches on Google Singapore with personalisation off and noted whether an AI Overview appeared. Eight did.

- **AI answer shown:** how much does a website cost in singapore · business process automation singapore sme · how to automate invoicing small business singapore · it support for small business singapore · answer engine optimisation singapore · best crm for small business singapore · hire a web developer singapore · why is my business not showing up on google singapore
- **No AI answer:** web design company singapore · seo agency singapore

The two without one are pure supplier shopping. "seo agency singapore" gets an estimated 1,900 searches a month, and Google still answered it with a plain list of links. Every search that described a problem or asked about cost got an AI answer.

That matters because most buying starts with a problem. If the AI answers that first question without mentioning you, you've lost the customer before they saw any list, and your analytics won't show it. Ten searches on one day is only a sketch, so try it yourself.

## How do you get your business to show up on ChatGPT?

Nobody can sell you a guaranteed spot in ChatGPT's recommendations. What you control comes down to four things, and they work the same way for Perplexity, Claude and Google.

1. **Let the right crawlers in.** More on this below.
2. **Answer the question early.** AI tools lift passages, so put the answer in your first two or three sentences, not in paragraph nine under the company history.
3. **Be the same business everywhere.** Same name, address and description on your site, in your structured data, on directories and on social profiles. When the details disagree, an assistant has less reason to trust any of them.
4. **Publish something worth repeating.** If your page says what every other page says, there's no reason to pick it. Figures you measured, dates and honest caveats are what tend to get quoted.

## Which AI crawlers should your website let in?

Each AI company runs more than one bot, and only some of them matter for being quoted. From each company's documentation, checked on 2 October 2026:

- **OpenAI:** `OAI-SearchBot` puts sites into ChatGPT search. `GPTBot` collects training data.
- **Anthropic:** `Claude-SearchBot` and `Claude-User` fetch pages for Claude's answers. `ClaudeBot` collects training data.
- **Perplexity:** `PerplexityBot` indexes sites for its answers. `Perplexity-User` fetches a page for one person's question and, by Perplexity's own account, generally ignores robots.txt.
- **Google:** AI Overviews come from the normal search index. `Google-Extended` covers Gemini training only, and Google says it doesn't affect Search, so blocking it won't keep you out of AI Overviews.

So you can block GPTBot and still allow OAI-SearchBot if you'd rather not be trained on but do want to be cited. Google adds that its AI features need nothing special, just a page that's indexed and eligible for a snippet. You'll still see FAQ markup sold as an AEO quick win, but the dropdowns it used to earn are gone: Google stopped showing FAQ rich results on 7 May 2026.

In September we read the robots.txt files of Singapore agencies ranking for AEO terms, and most were missing at least one current answer engine bot. Ours was too, until we fixed it on 28 September. It's an easy check: add /robots.txt to the end of any domain and read the list. Still, a correct file is housekeeping. The four points above are the real work.

## How do you know if AEO is working?

Mostly by checking yourself. Search Console mixes Google's AI Overview appearances into its normal numbers, and the other assistants don't report to it at all. Once a month, we:

- ask ChatGPT and Perplexity the questions our buyers ask, in the same wording, and note who gets named
- look at visits referred from chatgpt.com and perplexity.ai
- check our server logs for `OAI-SearchBot`, `Claude-SearchBot` and `PerplexityBot`

Our own starting point: 19 search impressions and one click in the three months to 2 October 2026. When we asked Perplexity the same question on 22 and 27 September, the businesses it named didn't overlap at all, and we weren't on either list. One check tells you very little.

## Where should you start?

Ask ChatGPT or Perplexity the question your best customer would ask before they'd heard of you. Leave your name out and describe the problem. Whoever gets named is your real competition, and it's often not who you expected.

Nobody can promise you'll be named. What you can do is the work above, and keep checking whether it moved.

## Sources

- [OpenAI crawlers](https://developers.openai.com/api/docs/bots)
- [Anthropic crawlers](https://support.claude.com/en/articles/8896518)
- [Perplexity crawlers](https://docs.perplexity.ai/guides/bots)
- [Google's common crawlers, including Google-Extended](https://developers.google.com/search/docs/crawling-indexing/google-common-crawlers)
- [Google: AI features and your website](https://developers.google.com/search/docs/appearance/ai-features)
- [Google Search Central updates, 8 May and 15 June 2026](https://developers.google.com/search/updates)
- Search estimate: DataForSEO Labs, Singapore, English, September 2026. Search tests, robots.txt checks and Search Console figures: our own, dated above.
