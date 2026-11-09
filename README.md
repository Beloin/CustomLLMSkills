# my-skills

Personal skill repository. One directory per skill under `skills/`. Installs
into Claude Code and OpenCode.

## What this skill solves

Turning a capability into an agent skill needs a `SKILL.md` with valid
frontmatter, a place for helper code, and a way to install the result into
each agent host. This repository provides that structure and the tooling to
manage it, so a new skill takes one command to create and one to install.

## Why this is a skill (model delta)

Without it, an agent asked to "make a slide deck" writes a binary `.pptx` by
hand or guesses at file locations. This skill hands over the toolkit and the
workflow, so the deck is a script, the layout is consistent, and the result
is checked before delivery.

## Use when

- Adding a new skill to this repository.
- Installing the repository's skills into Claude Code or OpenCode.
- Listing the skills in the repository.
- Checking that the repository conforms to the Agent Skills specification.

## Expected outputs

- `skills/<name>/SKILL.md` — a skill definition with `name` and `description`
  frontmatter.
- `skills/<name>/scripts/` — helper code, executed but never loaded.
- `skills/<name>/references/` — supporting documents, loaded on demand.
- A symlink or copy of each skill in the target host's skills directory.

## Context requirements

Python 3.10 or newer. No third-party packages for the repository tooling.
`python-pptx` is needed only by the `slide-creator` skill itself.

## Example prompts

- "Create a new skill called `pdf-extract` for pulling tables out of PDFs."
- "Install every skill in this repo into Claude Code and OpenCode."
- "List the skills in this repository with their descriptions."
- "Check that this repo passes the skill specification validation."

## Layout

```
my-skills/
├── plugin.json                  # portable manifest, source of truth
├── .claude-plugin/
│   ├── plugin.json              # Claude Code projection of plugin.json
│   ├── marketplace.json         # marketplace manifest
│   └── icon.png
├── skills/
│   └── <skill-name>/
│       ├── SKILL.md             # frontmatter + instructions
│       ├── README.md
│       ├── scripts/             # executable helpers
│       ├── references/          # documents loaded on demand
│       └── examples/            # worked examples
├── scripts/
│   ├── skill_repo.py            # list, install, uninstall
│   ├── new_skill.py             # scaffold a new skill
│   ├── validate_repo.py         # specification validation
│   └── _frontmatter.py          # frontmatter parser
├── references/
│   └── writing-skills.md        # how to write a good SKILL.md
└── README.md
```

A skill is valid when `skills/<name>/SKILL.md` exists with frontmatter
containing `name` and `description`. Everything else is optional.

## Installation

Install the skills into the hosts you use:

```bash
python3 scripts/skill_repo.py list
python3 scripts/skill_repo.py install
python3 scripts/skill_repo.py install slide-creator
python3 scripts/skill_repo.py uninstall
```

| Flag | Effect |
|---|---|
| `--target claude\|opencode\|both` | which host to install into (default: both) |
| `--mode link\|copy` | symlink the skill (default) or copy it |
| `--dry-run` | show what would happen, change nothing |

Install locations:

| Host | Path |
|---|---|
| Claude Code | `~/.claude/skills/<name>` |
| OpenCode | `~/.config/opencode/skills/<name>` |

Override with `CLAUDE_CONFIG_DIR` and `OPENCODE_CONFIG_DIR`. OpenCode also
reads `~/.claude/skills` as a compatibility root, so a Claude Code install
alone is already visible to OpenCode. Installing for both keeps each host's
own directory authoritative.

The default is a symlink, so edits in this repository take effect
immediately with no reinstall.

As a Claude Code plugin:

```
/plugin marketplace add Beloin/CustomLLMSkills
/plugin install my-skills@my-skills
```

Plugin skills are invoked as `/my-skills:<skill-name>`. The plugin reads from
the repository, so edits take effect on the next session start or
`/reload-plugins`.

## Related skills

- [slide-creator](skills/slide-creator/) — build styled PowerPoint decks with
  `python-pptx`.
- [Agent Skills specification](https://agentskills.io/specification) — the
  format this repository follows.
- [Claude Code skills](https://code.claude.com/docs/en/skills) — how the host
  discovers and invokes skills.

## Contributing

Create a skill, then validate the repository:

```bash
python3 scripts/new_skill.py my-skill-name --description "What it does"
python3 scripts/validate_repo.py
```

The validator checks frontmatter, name and description rules, body length,
flat discovery, manifest parity between `plugin.json` and
`.claude-plugin/plugin.json`, and repository hygiene. It exits non-zero on
errors.

## License

MIT. See [LICENSE](LICENSE).
