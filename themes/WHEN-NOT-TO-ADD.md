# WHEN NOT TO ADD to `themes/`

> **Intentionally near-empty principle**: this directory is for **display-layer presentation only**. Each theme defines display names, emoji, and tone for the 9 supported themes (3 languages × 3 cultural settings each). Adding a new theme is one of the most expensive operations in lifeos — it must be paid in every future agent / spec / command that adds a role name.

## What does NOT belong here

1. **Engine logic** — e.g. "what archiver does in phase 2". → Goes to: `pro/agents/archiver.md`.
2. **Spec content** — e.g. "definition of session frontmatter". → Goes to: `references/session-index-spec.md`.
3. **Translations of agent behavior** — themes only translate **display names**, NOT behaviors. Behavior remains identical across themes.
4. **A new cultural setting "just because"** — see "Before adding a new theme" below.
5. **Theme variants for sub-domains** — e.g. "zh-classical-finance" with money-focused display names. Themes are session-wide, not per-domain.
6. **Per-user customization** — users edit `meta/config.md` to switch themes; they don't add new ones.

## What DOES belong here

A complete theme file containing all of:
- `Role Mapping` table — every engine role from SKILL.md mapped to display name + emoji + report label
- `Domain Mapping` table — the 6 domains mapped to their theme equivalents
- `Trigger Words` — theme-specific trigger words (e.g. "上朝" for zh-classical)
- `Tone` — narrative voice the theme uses

If any of these is missing, the theme is incomplete and will fall back to engine IDs (ugly).

## Before adding a new theme — high bar

A new theme means:
- Every existing agent's display name needs a translation
- Every future agent (e.g. memory-keeper in v1.8.7) MUST add a row in this theme
- Trigger words need to be carefully chosen (must not collide with existing themes)
- Tone / cultural framing must be internally consistent across all 22+ agents
- Three-language alignment if it's a translation of an existing theme

**Real question to ask before adding**: is there a user (or community) actually asking for this theme, or is it engineering for engineering's sake? If the latter, do not add.

## Currently shipped themes (9)

| Language | Themes |
|----------|--------|
| English | `en-roman.md` (Roman Republic) / `en-usgov.md` (US Government) / `en-csuite.md` (Corporate C-Suite) |
| 中文 | `zh-classical.md` (三省六部) / `zh-gov.md` (中国政府) / `zh-corp.md` (公司部门) |
| 日本語 | `ja-meiji.md` (明治政府) / `ja-kasumigaseki.md` (霞が関) / `ja-corp.md` (企業) |

Adding a 10th theme requires user-facing justification + RFC entry + commitment to maintain.

## Reference

- `meta/rfc/v1.8.7-openhuman-borrowed-patterns.md` §2.4 F12 + §9 Q3 (memory-keeper added across all 9 themes simultaneously — illustrative of the cost)
- Pattern source: `tinyhumansai/openhuman` `.claude/rules/README.md`
- Companion: SKILL.md `## Theme System`
