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

### Claude Code, as a plugin

```
/plugin marketplace add Beloin/CustomLLMSkills
/plugin install my-skills@my-skills
```

Plugin skills are invoked as `/my-skills:<skill-name>`. The plugin reads from
the repository, so edits take effect on the next session start or
`/reload-plugins`.

### Both hosts, from a clone

```bash
git clone git@github.com:Beloin/CustomLLMSkills.git
cd CustomLLMSkills
python3 scripts/skill_repo.py install
```

Installs every skill into `~/.claude/skills/<name>` and
`~/.config/opencode/skills/<name>` as a symlink, so edits in the clone take
effect immediately with no reinstall.

| Flag | Effect |
|---|---|
| `--target claude\|opencode\|both` | which host to install into (default: both) |
| `--mode link\|copy` | symlink the skill (default) or copy it |
| `--dry-run` | show what would happen, change nothing |

Override the destination with `CLAUDE_CONFIG_DIR` and `OPENCODE_CONFIG_DIR`.
OpenCode also reads `~/.claude/skills` as a compatibility root, so a Claude
Code install alone is already visible to OpenCode. Installing for both keeps
each host's own directory authoritative.

### OpenCode, without installing

Point OpenCode at a clone through its own config, in
`~/.config/opencode/opencode.json`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "skills": {
    "paths": ["/path/to/CustomLLMSkills/skills"]
  }
}
```

`skills.paths` takes directories that are scanned for `SKILL.md`. Restart
OpenCode after editing the config. The `urls` key expects an HTTP catalog
that serves `index.json`, not a git repository.

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
