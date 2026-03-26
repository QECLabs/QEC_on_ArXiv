---
name: arxiv-paper-triage
description: Review generated arXiv exports from QEC_on_ArXiv and shortlist papers relevant to quantum error correction or adjacent fault-tolerant quantum computing topics. Use when analyzing `data/weekly/qec_*.csv`, `data/weekly/qec_*.jsonl`, or weekly Markdown digests, scanning titles and abstracts for QEC relevance, proposing keyword filters, or designing automated triage on top of the tracker output.
---

# arXiv Paper Triage

## Overview

Use this skill to turn tracker exports into a short QEC-focused reading list or into actionable filtering heuristics for the API-based workflow.

## Workflow

1. Start from the newest generated `data/weekly/qec_*.csv`, `data/weekly/qec_*.jsonl`, or weekly Markdown digest.
2. Load `references/triage-guidelines.md` for positive and negative title heuristics.
3. Classify papers into direct QEC, adjacent fault-tolerance, or likely off-topic.
4. Explain ambiguous calls briefly so the user can review the shortlist quickly.
5. If asked to automate triage, prefer adding tags or scores before deleting rows entirely.

## Triage Rules

- Prioritize titles that explicitly mention error correction, fault tolerance, decoding, syndrome processing, stabilizer codes, surface codes, LDPC codes, bosonic codes, or thresholds.
- Keep adjacent titles when they likely affect QEC workflows, such as magic-state distillation, erasure mitigation, transversal gates, topological codes, or quantum memory.
- Deprioritize titles that are clearly unrelated applications, hardware demonstrations without control/correction relevance, or generic information-theory work with no quantum coding angle.
- When the signal is weak, keep the paper with a note rather than dropping it silently.

## Automation Guidance

- If implementing filtering in code, prefer adding a relevance label or score column instead of removing non-QEC rows.
- If the user wants strict filtering, make the keyword list explicit and document the false-positive and false-negative tradeoff.
- Update `README.md` if automated triage changes the output format.
