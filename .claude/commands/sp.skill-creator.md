---
description: |
  Creates production-grade, reusable skills that extend Claude's capabilities.
  This skill should be used when users want to create a new skill, improve an
  existing skill, or build domain-specific intelligence. Gathers context from
  codebase, conversation, and authentic sources before creating adaptable skills.
handoffs:
  label: Create New Skill
  prompt: |
    Create a skill for the following domain/use case. Follow the skill-creator-pro
    framework: determine skill type, research the domain thoroughly, ask clarifying
    questions about the user's specific requirements, then create a complete skill
    with SKILL.md and reference files.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Overview

This command invokes the **skill-creator-pro** skill to create production-grade, reusable skills.

## Steps

1. **Load the skill** from `.claude/commands/skills/skill-creator-pro/SKILL.md`

2. **Determine Skill Type** - Ask the user what type of skill they want:
   - **Builder**: Create artifacts (widgets, code, documents)
   - **Guide**: Provide instructions (how-to, tutorials)
   - **Automation**: Execute workflows (file processing, deployments)
   - **Analyzer**: Extract insights (code review, data analysis)
   - **Validator**: Enforce quality (compliance checks, scoring)

3. **Identify Domain** - What domain or technology does the skill cover?

4. **Domain Discovery** (Automatic) - Research thoroughly:
   - Core concepts from official docs
   - Standards and compliance requirements
   - Best practices (search "[domain] best practices 2025")
   - Anti-patterns (search "[domain] common mistakes")
   - Security considerations
   - Ecosystem tools

5. **Ask Clarifying Questions** (about user's specific context, NOT domain knowledge):
   - What's YOUR specific use case?
   - What's YOUR tech stack/environment?
   - Any existing resources to include?
   - Any specific constraints or requirements?

6. **Create the Skill** following the type-specific patterns:
   - Initialize skill directory structure
   - Write SKILL.md with proper frontmatter
   - Create reference files with embedded domain expertise
   - Generate scripts/assets if needed
   - Validate with package_skill.py

## Output

A complete skill in `.claude/commands/skills/<skill-name>/` with:
- SKILL.md (main skill file with workflows and procedures)
- references/ (domain expertise, best practices, patterns)
- scripts/ (executable code if needed)
- assets/ (templates, boilerplate if needed)
