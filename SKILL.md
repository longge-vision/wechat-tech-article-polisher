---
name: wechat-tech-article-polisher
description: Polish Chinese WeChat Official Account drafts for technical papers, especially industrial vision, defect detection, anomaly detection, AI papers, and arXiv-to-WeChat articles. Use when the user says a draft is not well written, too mechanical, too short, too translated, has English paragraphs, needs a better title, stronger lead, better structure, better figure captions, or a more engaging WeChat style before publishing.
---

# WeChat Tech Article Polisher

Use this skill after a paper draft has already been generated from parsed paper content.

## Goal

Turn a technical paper draft into a readable Chinese WeChat article:

- Chinese-first writing, no untranslated English paragraphs.
- More attractive Chinese title while preserving the original paper title in `论文信息`.
- Make the title and first screen attractive enough for WeChat readers to click: concrete method name + pain point/反常识 + dataset/metric/speed hook when available.
- Stronger opening and section transitions.
- Follow the observed white-list WeChat account style: pain point first, method highlight second, dataset/SOTA evidence third, production validation last.
- Explain methods in plain technical Chinese, not direct translation.
- Apply a final humanizer pass inspired by SkillHub `humanizer`: remove AI-writing tells such as vague significance inflation, formulaic “not only/but also” structure, generic positive conclusions, excessive bold-label bullets, and empty transition words.
- Keep claims grounded in the draft or parsed paper.
- Keep image links intact and rewrite captions in Chinese.
- Keep `wenyan` frontmatter valid for publishing.

## Engineering Public-Account Style Pass

When polishing industrial vision, anomaly detection, defect detection, or AI-for-inspection drafts, move the draft closer to strong Chinese engineering public-account writing:

- Title should combine a concrete technical claim with a reader benefit: `不用重建`, `不用缺陷样本`, `跨类别`, `统一超参`, `提速`, `上产线`, dataset/metric hook, or a clear method contrast. Keep only claims supported by the paper.
- Opening should start with production tension: false alarms, missed defects, sample scarcity, heatmap instability, deployment cost, parameter tuning, or product changeover. Do not start with "本文提出..." unless the user requests academic style.
- Convert generic paper sections into numbered, reader-facing sections when appropriate: `01 这篇论文到底解决什么问题`, `02 核心模块怎么工作`, `03 实验结果真正说明什么`, `04 上产线还要复核什么`.
- Every section should answer one practical question. Avoid headings that merely repeat paper section names.
- Turn experiment tables into conclusions: who wins, margin size, whether the win is robust, what metric matters, and what the hidden cost might be.
- Explain formulas only when necessary; translate them into "input -> operation -> output -> why it reduces a failure mode".
- End with a clear engineering verdict plus limitations, not a broad positive conclusion.

## Coze-Style Article Pass

Use this pass whenever polishing a paper-to-WeChat draft, especially when the user says another workflow produced a better article.

- First infer the target article length. If the user did not specify, keep it as a compact WeChat social article under about 3000 Chinese characters/words worth of reading burden.
- If a material file exists, such as `ADPretain微信公众号素材.md`, read it before polishing and preserve its verified paper facts, metrics, figure links, and citation notes.
- Treat the article as a new-media technical post, not a translated abstract: headline hook, first-screen pain point, method story, evidence, engineering takeaway, and citation.
- Use only paper figures already in the draft, extracted from the paper, or supplied in the material file. Do not add unrelated stock/search images.
- Keep figures inline near the paragraph that explains them. Rewrite captions so readers know what to inspect in the figure.
- Add or repair the final citation/reference note when missing.
- Use the review checklist internally: requirement adherence, content richness, logic, image validity, citation completeness, title attractiveness, and language naturalness. Do not print this checklist in the article body.
- Remove meta-writing such as `从白名单技术号常用的选题标准看`; the article should sound like an editor made those decisions, not like it is explaining the decisions.

## Run

```powershell
python C:\Users\User\.codex\skills\wechat-tech-article-polisher\scripts\polish_article.py `
  --input "F:\program\公众号\.paper2wechat\<arxiv_id>\outputs\<file>.wenyan.md" `
  --output "F:\program\公众号\.paper2wechat\<arxiv_id>\outputs\<file>.polished.wenyan.md" `
  --style industrial-vision `
  --length medium
```

If `--output` is omitted, the script writes beside the input as:

`<stem>.polished<suffix>`

## Style Rules

- Title: use a white-list style formula: `痛点/反常识/方法亮点 + 方法名 + 工业异常检测任务 + 数据集/指标/速度/落地结果`. Prefer concrete hooks such as `99.0 AUROC`, `120 FPS`, `2x speedup`, `MVTecAD/VisA`, `不用重建`, `不用缺陷样本`, `不训练也能分割`. Do not invent metrics; if no number exists, use a concrete technical contrast instead.
- Lead: open with the real industrial pain point and the paper's specific hook, not paper metadata. The first quote/paragraph should make the reader understand why this paper is worth opening within 3 seconds.
- Avoid bland titles like `工业异常检测又有新方法` unless followed by a concrete method, mechanism, and result hook.
- Title should make the reader want to click but must stay defensible: no fake SOTA, no invented speed, no overpromising deployment readiness.
- The first screen should answer: why this paper matters, what is different, and what concrete evidence exists.
- For industrial vision drafts, prefer numbered engineering sections and concrete subsection titles over academic outline headings.
- Summary: 4-6 bullets, each with a concrete point.
- Add `为什么这篇值得看` before paper metadata when missing.
- Method: explain the model pipeline in Chinese; avoid dumping source text.
- Experiments: explain datasets, metrics, comparison, and what the result means.
- Landing section: add a `产线复现 checklist` covering data, false positives/false negatives, heatmap quality, retraining cost, deployment cost, and failure cases.
- Ending: give a clear judgment, not a generic conclusion.
- References: ensure the article ends with a concise source/citation note for the original paper. If the user wants paper/code links hidden behind keyword auto-reply, keep the public article wording as a citation note and do not expose direct download links in the body.
- Humanizer pass: prefer concrete numbers, concrete failure cases, and direct judgment. Avoid empty phrases such as `具有重要意义`, `充分说明`, `未来值得关注`, `总的来说`, `综上所述`, and generic upbeat endings.

## Quality Gate

Before publishing, verify:

- No long English paragraphs remain. English is allowed for paper title, institution, dataset, method names, metric names, links, and code names.
- Image links resolve from the markdown output directory.
- The draft uses only paper/extracted/material-provided images unless the user explicitly authorized outside images.
- If the draft came from a material file with key figures, those figures are preserved unless a link is broken or a figure is clearly irrelevant.
- Frontmatter contains a Chinese `title`.
- The article does not include tool-credit disclaimers.
- The article is not just a rigid template.
- The first 300 Chinese characters should not read like AI boilerplate: no generic opening, no paper-metadata-first opening, no vague “重要意义/广阔前景” claim without evidence.
- Experiments are interpreted as decisions and trade-offs, not merely listed as benchmark names and numbers.
- A citation/reference note for the original paper/source is present near the end.
- Internal review passes: requirement adherence, content richness, logic, image validity, citation completeness, title attractiveness, and language naturalness.

## Integration

For `arxiv-defect-wechat-daily`, run this polisher after `make_article()` and before `wenyan publish`.
