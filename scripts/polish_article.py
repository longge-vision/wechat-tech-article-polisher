#!/usr/bin/env python
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


DATASETS = ["MVTec", "VisA", "BTAD", "DAGM", "MPDD", "Real-IAD", "MVTec-3D", "MVTec-loco"]
METHOD_NAMES = [
    "CCAD",
    "CLIP",
    "WinCLIP",
    "AnomalyCLIP",
    "PatchCore",
    "PaDiM",
    "FastFlow",
    "DRAEM",
    "MoE",
    "Diffusion",
    "Transformer",
]


def clean(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def split_frontmatter(text: str) -> tuple[str, str]:
    if not text.startswith("---\n"):
        return "", text
    end = text.find("\n---\n", 4)
    if end == -1:
        return "", text
    return text[: end + 5], text[end + 5 :].lstrip()


def update_frontmatter(frontmatter: str, title: str) -> str:
    if not frontmatter:
        return f"---\ntitle: {title}\nauthor: LabVIEW\n---\n\n"
    if re.search(r"^title:\s*.*$", frontmatter, flags=re.M):
        frontmatter = re.sub(r"^title:\s*.*$", f"title: {title}", frontmatter, flags=re.M)
    else:
        frontmatter = frontmatter.replace("---\n", f"---\ntitle: {title}\n", 1)
    return frontmatter.rstrip() + "\n\n"


def extract_field(body: str, field: str) -> str:
    match = re.search(rf"^-\s*{re.escape(field)}[:：]\s*(.+)$", body, flags=re.M)
    return clean(match.group(1)) if match else ""


def extract_section(body: str, heading: str) -> str:
    pattern = rf"^##\s*{re.escape(heading)}\s*\n(?P<content>.*?)(?=^##\s+|\Z)"
    match = re.search(pattern, body, flags=re.M | re.S)
    return match.group("content").strip() if match else ""


def remove_section(body: str, heading: str) -> str:
    pattern = rf"^##\s*{re.escape(heading)}\s*\n.*?(?=^##\s+|\Z)"
    return re.sub(pattern, "", body, flags=re.M | re.S).strip()


def english_ratio(text: str) -> float:
    letters = sum(c.isascii() and c.isalpha() for c in text)
    zh = sum("\u4e00" <= c <= "\u9fff" for c in text)
    return letters / max(letters + zh, 1)


def strip_english_paragraphs(body: str) -> str:
    kept: list[str] = []
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped:
            kept.append(line)
            continue
        if stripped.startswith(("#", "-", ">", "!", "|")):
            kept.append(line)
            continue
        letters = sum(c.isascii() and c.isalpha() for c in stripped)
        zh = sum("\u4e00" <= c <= "\u9fff" for c in stripped)
        if letters > 120 and letters > zh * 2:
            continue
        kept.append(line)
    return "\n".join(kept)


def detected_terms(text: str, terms: list[str]) -> list[str]:
    lower = text.lower()
    found: list[str] = []
    for term in terms:
        if term.lower() in lower and term not in found:
            found.append(term)
    return found


def infer_method_label(original_title: str, body: str) -> str:
    text = f"{original_title} {body}"
    methods = detected_terms(text, METHOD_NAMES)
    if methods:
        return methods[0]
    if "compressed global feature" in text.lower() or "全局特征" in text:
        return "全局特征压缩"
    if "zero-shot" in text.lower() or "零样本" in text:
        return "零样本方案"
    if "few-shot" in text.lower() or "少样本" in text:
        return "少样本方案"
    return "新方法"


def attractive_title(original_title: str, body: str) -> str:
    text = f"{original_title} {body}".lower()
    method = infer_method_label(original_title, body)
    datasets = detected_terms(f"{original_title} {body}", DATASETS)
    dataset_part = "、".join(datasets[:2]) if datasets else "工业数据集"

    if "ccad" in text or "compressed global feature" in text:
        return "不用缺陷样本也能稳定位？CCAD 用全局特征压缩刷新工业异常检测"
    if "clip" in text and ("zero-shot" in text or "零样本" in body):
        return f"不用训练缺陷样本，{method} 在 {dataset_part} 上做零样本异常检测"
    if "few-shot" in text or "少样本" in body:
        return f"缺陷样本太少怎么办？{method} 把少样本工业异常检测做得更稳"
    if "localization" in text or "定位" in body or "segmentation" in text:
        return f"不只判断异常，还要定位缺陷：{method} 的工业异常分割思路"
    if "sota" in text:
        return f"{method} 刷新工业异常检测结果，真正值得看的是这几个技术细节"
    return f"工业异常检测又有新方法：{method} 如何提升缺陷定位和产线泛化"


def normalize_heading(body: str, title: str) -> str:
    if re.search(r"^#\s+.+$", body, flags=re.M):
        return re.sub(r"^#\s+.+$", f"# {title}", body, count=1, flags=re.M)
    return f"# {title}\n\n{body.lstrip()}"


def replace_opening_quote(body: str, original_title: str) -> str:
    method = infer_method_label(original_title, body)
    lead = (
        f"> 工业异常检测最难的不是把公开数据集分数做高，而是缺陷样本少、产品换型快、"
        f"细小划痕和纹理波动容易混在一起。今天这篇论文的看点，是用 {method} 把“判断异常”和“定位缺陷”放进同一条技术路线里。"
    )
    if re.search(r"^>\s*.+$", body, flags=re.M):
        return re.sub(r"^>\s*.+$", lead, body, count=1, flags=re.M)
    return re.sub(r"(^# .+\n)", rf"\1\n{lead}\n", body, count=1, flags=re.M)


def remove_template_tone(body: str) -> str:
    replacements = {
        "这是一篇面向工业视觉团队的技术解读。重点不是简单复述摘要，而是拆开论文的问题设定、方法设计、实验验证和落地边界，帮助判断它是否值得继续复现或引入产线验证。":
            "工业异常检测最难的不是把公开数据集分数做高，而是缺陷样本少、产品换型快、细小划痕和纹理波动容易混在一起。",
        "从工程视角看，它值得关注的地方有三点：":
            "从白名单技术号常用的选题标准看，这篇论文值得单独写，是因为它同时踩中了三个点：",
        "看实验时，不建议只看 AUROC 或 F1 的最终数值，还要看下面这些细节：":
            "读这类实验，不建议只盯 AUROC 或 F1 的最终数值。真正决定能不能进产线验证的，通常是下面几件事：",
    }
    for old, new in replacements.items():
        body = body.replace(old, new)
    return body


def polish_captions(body: str) -> str:
    counter = 0

    def repl(match: re.Match[str]) -> str:
        nonlocal counter
        counter += 1
        image = match.group(1)
        caption = match.group(2).strip()
        if english_ratio(caption) > 0.45:
            caption = f"图 {counter}：论文中的关键可视化结果，建议重点看异常区域响应、正常区域误报和不同方法的定位边界。"
        return f"{image}\n\n> {caption}"

    return re.sub(r"(!\[[^\]]*\]\([^)]+\))\n\n>\s*(.+)", repl, body)


def value_section(original_title: str, body: str) -> str:
    method = infer_method_label(original_title, body)
    datasets = detected_terms(f"{original_title} {body}", DATASETS)
    dataset_text = "、".join(datasets[:4]) if datasets else "MVTec、VisA 等工业异常检测数据集"
    return f"""## 为什么这篇值得看

这类文章能不能成为目标选题，关键看它有没有具体技术增量。{method} 的价值不在于换一个名字包装异常检测，而在于它尝试回答三个产线团队真正关心的问题：

- **缺陷样本少时怎么建模**：工业现场很难提前收集完整缺陷类型，方法必须尽量依赖正常样本或少量样本。
- **异常区域能不能稳定定位**：只给 image-level 判断不够，AOI 复核、返修和工艺追溯更需要 pixel-level 热力图。
- **换产品后是否还能泛化**：公开数据集上的平均分只是第一步，{dataset_text} 上的表现需要结合跨类别、跨纹理和跨光照结果一起看。
"""


def checklist_section(original_title: str, body: str) -> str:
    method = infer_method_label(original_title, body)
    return f"""## 产线复现 checklist

如果要把 {method} 放进自己的工业视觉项目里验证，建议不要只复现实验表格，而是按下面这组问题逐项检查：

- **数据准备**：先用本产品的正常样本建立验证集，再单独收集划痕、污点、缺料、压伤、脏污等典型异常做压力测试。
- **误报/漏报拆开看**：漏报影响质量风险，误报影响人工复核成本，两者不能只用一个综合指标代替。
- **热力图是否可解释**：异常响应应该落在缺陷区域，而不是边缘、反光、纹理周期或背景噪声上。
- **换型成本**：确认每个产品是否都要重新训练，还是只需要更新正常样本库或少量适配参数。
- **部署成本**：记录输入分辨率、单张推理耗时、显存占用和批量处理能力，确认能否满足在线检测节拍。
- **失败案例**：专门保留误检、漏检和边界模糊样本，这比只看 SOTA 表格更能判断方法是否值得继续投入。
"""


def verdict_section(original_title: str, body: str) -> str:
    method = infer_method_label(original_title, body)
    return f"""## 一句话判断

这篇论文更适合作为工业异常检测方案池里的候选技术，而不是直接拿来替换产线模型。它值得复现的原因，是 {method} 给了一个更具体的异常定位思路；真正要落地，还需要在自己的产品、光照、相机和节拍条件下重新验证误报、漏报和热力图稳定性。
"""


def insert_after_section(body: str, heading: str, addition: str) -> str:
    pattern = rf"(^##\s*{re.escape(heading)}\s*\n.*?)(?=^##\s+|\Z)"
    match = re.search(pattern, body, flags=re.M | re.S)
    if not match:
        return body.rstrip() + "\n\n" + addition.strip() + "\n"
    end = match.end(1)
    return body[:end].rstrip() + "\n\n" + addition.strip() + "\n\n" + body[end:].lstrip()


def move_paper_info_after_value(body: str) -> str:
    info = extract_section(body, "论文信息")
    if not info:
        return body
    body = remove_section(body, "论文信息")
    section = "## 论文信息\n\n" + info.strip() + "\n"
    if "## 为什么这篇值得看" in body:
        return insert_after_section(body, "为什么这篇值得看", section)
    if "## 导读" in body:
        return insert_after_section(body, "导读", section)
    return body.rstrip() + "\n\n" + section


def ensure_value_and_checklist(body: str, original_title: str) -> str:
    if "## 为什么这篇值得看" not in body:
        body = insert_after_section(body, "导读", value_section(original_title, body))
    if "## 产线复现 checklist" not in body:
        if "## 对工业视觉团队的落地建议" in body:
            body = insert_after_section(body, "对工业视觉团队的落地建议", checklist_section(original_title, body))
        elif "## 实验与结果怎么看" in body:
            body = insert_after_section(body, "实验与结果怎么看", checklist_section(original_title, body))
        else:
            body = body.rstrip() + "\n\n" + checklist_section(original_title, body)
    if "## 一句话判断" not in body:
        if "## 扩展阅读" in body:
            body = body.replace("## 扩展阅读", verdict_section(original_title, body).strip() + "\n\n## 扩展阅读", 1)
        else:
            body = body.rstrip() + "\n\n" + verdict_section(original_title, body)
    return body


def add_editorial_bridges(body: str) -> str:
    bridges = {
        "## 方法拆解": "先说结论：读这类方法，重点不是记住模块名字，而是看它怎样把正常外观建模、异常响应和像素级定位串起来。",
        "## 实验与结果怎么看": "工业异常检测论文的实验最好分两层看：一层是公开数据集排名，另一层是它对真实产线扰动的承受能力。",
        "## 局限与复核点": "方向值得跟，但公开数据集结论不能直接等同于产线效果，尤其要复核失败样本和部署成本。",
    }
    for heading, text in bridges.items():
        pattern = rf"({re.escape(heading)}\s*\n\n)(?!{re.escape(text)})"
        body = re.sub(pattern, rf"\1{text}\n\n", body, count=1)
    return body


def polish(text: str, style: str, length: str) -> str:
    frontmatter, body = split_frontmatter(text)
    original_title = extract_field(body, "标题")
    title = attractive_title(original_title, body)
    body = normalize_heading(body, title)
    body = replace_opening_quote(body, original_title)
    body = strip_english_paragraphs(body)
    body = polish_captions(body)
    body = remove_template_tone(body)
    body = ensure_value_and_checklist(body, original_title)
    body = move_paper_info_after_value(body)
    body = add_editorial_bridges(body)
    body = re.sub(r"\n{3,}", "\n\n", body).strip() + "\n"
    return update_frontmatter(frontmatter, title) + body


def default_output(input_path: Path) -> Path:
    if input_path.suffix:
        return input_path.with_name(f"{input_path.stem}.polished{input_path.suffix}")
    return input_path.with_name(f"{input_path.name}.polished.md")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output")
    parser.add_argument("--style", default="industrial-vision")
    parser.add_argument("--length", choices=["short", "medium", "long"], default="medium")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output) if args.output else default_output(input_path)
    text = input_path.read_text(encoding="utf-8")
    polished = polish(text, args.style, args.length)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(polished, encoding="utf-8")
    print(str(output_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
