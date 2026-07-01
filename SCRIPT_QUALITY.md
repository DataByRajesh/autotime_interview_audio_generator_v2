# Script Quality Review

Use `script_quality_review.py` to check chatbot-produced scripts before turning them into audio.

It works locally. It does not call OpenAI or Claude. Instead, it scores the script and can produce a rewrite prompt that you paste into OpenAI, Claude, or another chatbot.

## Quick audit

```powershell
python script_quality_review.py --input sample_sql_podcast.txt
```

## Include a rewrite prompt

```powershell
python script_quality_review.py --input sample_sql_podcast.txt --include-prompt
```

## Save report and prompt separately

```powershell
python script_quality_review.py `
  --input output/uat_learn.txt `
  --output-report output/uat_quality_report.md `
  --rewrite-prompt output/uat_rewrite_prompt.txt
```

Paste the rewrite prompt into OpenAI or Claude. Ask it to return only the improved script text. Then save that improved script and run the normal audio generator.

## Targets

```powershell
python script_quality_review.py --input script.txt --target learning
python script_quality_review.py --input script.txt --target interview
python script_quality_review.py --input script.txt --target bilingual
```

## What It Checks

- Sentence length for listening comfort.
- Dense paragraphs that need splitting.
- Missing pause markers.
- Missing active recall questions.
- Missing workplace or FinTech examples.
- Generic AI-style filler phrases.
- Markdown/code/table/URL formatting that can sound bad in TTS.
- Repeated sentence openings.

## Quality Gate

Use `--min-score` if you want automation to fail below a threshold:

```powershell
python script_quality_review.py --input script.txt --min-score 70
```

Exit code `2` means the script needs editing before audio generation.
## EU Fintech Role Alignment

Use these targets when the script should prepare you for EU fintech roles, especially Business Systems Analyst, QA/UAT, production support, product delivery, data quality, controls, and reporting roles.

```powershell
python script_quality_review.py --input script.txt --target eu_fintech
python script_quality_review.py --input script.txt --target ireland_fintech
python script_quality_review.py --input script.txt --target netherlands_fintech
```

The checker looks for:

- Analyst actions: clarify requirements, map process flows, document business rules, validate UAT evidence, investigate incidents, escalate risks.
- EU fintech domains: payments lifecycle, SEPA, open banking APIs, PSD2/PSD3/PSR, AML/KYC, fraud, reconciliation, DORA, ICT third-party risk, operational resilience.
- Evidence mindset: audit trails, logs, expected results, sign-off evidence, control evidence, sample records, reconciliation reports.
- Ireland or Netherlands relevance when selected: Dublin/Ireland/Central Bank of Ireland context, or Dutch/Netherlands/DNB/Amsterdam context.
- Interview usefulness: a practical answer structure with situation, action, result, business impact, and stakeholder communication.

This is a heuristic learning-quality tool, not legal advice. Use it to make scripts more job-relevant before asking OpenAI or Claude to rewrite them.

Source themes used for the EU fintech checks:

- European Banking Authority DORA overview: https://www.eba.europa.eu/activities/direct-supervision-and-oversight/digital-operational-resilience-act
- European Commission financial data access and payments package: https://finance.ec.europa.eu/publications/financial-data-access-and-payments-package_en
