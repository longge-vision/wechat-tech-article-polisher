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
- Stronger opening and section transitions.
- Follow the observed white-list WeChat account style: pain point first, method highlight second, dataset/SOTA evidence third, production validation last.
- Explain methods in plain technical Chinese, not direct translation.
- Keep claims grounded in the draft or parsed paper.
- Keep image links intact and rewrite captions in Chinese.
- Keep `wenyan` frontmatter valid for publishing.

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

- Title: use a white-list style formula: `痛点/会议/方法亮点 + 工业异常检测任务 + 数据集/SOTA/落地结果`.
- Lead: open with the real industrial pain point, not paper metadata.
- Summary: 4-6 bullets, each with a concrete point.
- Add `为什么这篇值得看` before paper metadata when missing.
- Method: explain the model pipeline in Chinese; avoid dumping source text.
- Experiments: explain datasets, metrics, comparison, and what the result means.
- Landing section: add a `产线复现 checklist` covering data, false positives/false negatives, heatmap quality, retraining cost, deployment cost, and failure cases.
- Ending: give a clear judgment, not a generic conclusion.

## Quality Gate

Before publishing, verify:

- No long English paragraphs remain. English is allowed for paper title, institution, dataset, method names, metric names, links, and code names.
- Image links resolve from the markdown output directory.
- Frontmatter contains a Chinese `title`.
- The article does not include tool-credit disclaimers.
- The article is not just a rigid template.

## Integration

For `arxiv-defect-wechat-daily`, run this polisher after `make_article()` and before `wenyan publish`.
