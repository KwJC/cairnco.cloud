答案引擎优化（Answer Engine Optimisation，简称 AEO）要做的事，是让别人向 AI 助手提问时，答案里会提到你的公司。ChatGPT、Perplexity、Claude 和 Google 的 AI Overviews 都会给出一段简短回答，并引用几个来源。AEO 就是争取成为其中之一。它建立在 SEO 之上，但目标是被写进那段答案里，而这种曝光往往完全不带点击。

我们是新加坡的一家两人技术公司，自己的网站从 2026 年 9 月才从零开始。下面每一条，要么出自 AI 公司自己的文档，要么是我们亲自测过的，都标了日期，你可以自己核对。

## AEO 和 SEO、GEO 是一回事吗？

是近亲。SEO 让一个页面在一串链接里排得更靠前。AEO 让一段文字被直接抬进答案里。GEO，也就是生成引擎优化，是同一个思路，针对的是每次都重新写一段答案的助手。也有人把这一整套统称为 AI SEO。新加坡大多数做 AEO 的公司会把三样一起卖，所以在比较 AEO 服务时，要问清楚他们具体会做什么。

一个本地的小麻烦：在 Google 搜 "AEO Singapore"，推荐词里会出现海关认证和 American Eagle Outfitters，因为 AEO 在新加坡也是一个海关术语。所以在任何你想被搜到的页面上，至少把全称完整写一次，另外也要考虑到有人会用美式拼写 answer engine optimization 来搜。

## 新加坡的搜索已经在出 AI 答案了吗？

我们试过的大部分都会。2026 年 9 月 22 日，我们在 Google 新加坡关掉个性化，跑了十个搜索，记录有没有出现 AI Overview。八个有。

- **出现了 AI 答案：** how much does a website cost in singapore · business process automation singapore sme · how to automate invoicing small business singapore · it support for small business singapore · answer engine optimisation singapore · best crm for small business singapore · hire a web developer singapore · why is my business not showing up on google singapore
- **没有出现 AI 答案：** web design company singapore · seo agency singapore

没出现的那两个，都是纯粹在挑供应商。"seo agency singapore" 估计每月有 1,900 次搜索，Google 仍然只给了一串普通链接。而每一个描述问题、或者问价格的搜索，都给了 AI 答案。

这件事重要，是因为大多数采购都是从一个问题开始的。如果 AI 回答了这第一个问题却没提到你，你在客户看到任何名单之前就已经输了，而你的分析工具不会显示这件事。十个搜索、一天的数据只是个草图，所以请自己试一遍。

## 怎么让自己的公司出现在 ChatGPT 的回答里？

没有人能卖给你一个在 ChatGPT 推荐里的保证位置。你真正能控制的是四件事，而它们对 Perplexity、Claude 和 Google 同样管用。

1. **让该进来的爬虫进来。** 下面细说。
2. **把答案放在最前面。** AI 工具是整段抬走的，所以把答案写进头两三句，不要埋在第九段的公司沿革后面。
3. **到处都是同一家公司。** 网站上、结构化数据里、各类名录上、社交资料里，名称、地址和描述都要一致。细节互相矛盾时，助手就更没有理由相信其中任何一份。
4. **写点值得被重复的东西。** 如果你的页面说的和别人页面一样，就没有理由选你。你自己测出来的数字、日期，还有诚实的注意事项，才是容易被引用的部分。

## 网站应该放哪些 AI 爬虫进来？

每家 AI 公司都跑着不止一个机器人，而其中只有一部分和被引用有关。以下出自各公司自己的文档，核对日期为 2026 年 10 月 2 日：

- **OpenAI：** `OAI-SearchBot` 把网站收进 ChatGPT 的搜索。`GPTBot` 收集训练数据。
- **Anthropic：** `Claude-SearchBot` 和 `Claude-User` 为 Claude 的回答抓取页面。`ClaudeBot` 收集训练数据。
- **Perplexity：** `PerplexityBot` 为它的答案建立索引。`Perplexity-User` 为某一个人的某一次提问抓取页面，而且按 Perplexity 自己的说法，它一般不理 robots.txt。
- **Google：** AI Overviews 用的是普通搜索索引。`Google-Extended` 只管 Gemini 的训练，Google 说它不影响搜索，所以屏蔽它并不会让你从 AI Overviews 里消失。

所以你可以屏蔽 GPTBot 但仍然放行 OAI-SearchBot，也就是不想被拿去训练、但想被引用。Google 还补充说，它的 AI 功能不需要任何特别设置，只要页面被索引、并且有资格出摘要就行。你仍然会看到有人把 FAQ 结构化数据当成 AEO 的捷径来卖，但它过去能换来的那些下拉条目已经没有了：Google 在 2026 年 5 月 7 日停止显示 FAQ 富媒体结果。

9 月我们读了一批在 AEO 相关词上有排名的新加坡公司的 robots.txt，大多数至少漏掉了一个当前的答案引擎机器人。我们自己也漏了，直到 9 月 28 日才修好。这个检查很容易：在任何域名后面加上 /robots.txt，把那份名单读一遍。不过，一份正确的文件只是基本功。上面那四点才是真正要做的事。

## 怎么判断 AEO 有没有起作用？

主要靠自己查。Search Console 把 Google AI Overview 的出现次数混进了普通数据里，而其他助手根本不向它汇报。我们每个月会做三件事：

- 用买家原本的问法，去问 ChatGPT 和 Perplexity，记录谁被提到
- 看来自 chatgpt.com 和 perplexity.ai 的访问
- 在服务器日志里查 `OAI-SearchBot`、`Claude-SearchBot` 和 `PerplexityBot`

我们自己的起点：截至 2026 年 10 月 2 日的三个月里，19 次搜索曝光，1 次点击。9 月 22 日和 27 日我们问 Perplexity 同一个问题，它提到的公司完全没有重叠，而两次名单上都没有我们。查一次说明不了什么。

## 应该从哪里开始？

去问 ChatGPT 或者 Perplexity 一个问题：你最好的客户在听说你之前会问的那个问题。不要带上自己的公司名，只描述问题。被提到的那些就是你真正的竞争对手，而且往往不是你以为的那几家。

没有人能保证你会被提到。你能做的就是上面那些事，然后持续检查它有没有带来变化。

## 来源

- [OpenAI crawlers](https://developers.openai.com/api/docs/bots)
- [Anthropic crawlers](https://support.claude.com/en/articles/8896518)
- [Perplexity crawlers](https://docs.perplexity.ai/guides/bots)
- [Google's common crawlers, including Google-Extended](https://developers.google.com/search/docs/crawling-indexing/google-common-crawlers)
- [Google: AI features and your website](https://developers.google.com/search/docs/appearance/ai-features)
- [Google Search Central updates, 8 May and 15 June 2026](https://developers.google.com/search/updates)
- 搜索量估算：DataForSEO Labs，新加坡，英文，2026 年 9 月。搜索测试、robots.txt 检查和 Search Console 数据：均为我们自己的，日期见上文。
