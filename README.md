# my-skills

Personal skill repository. One directory per skill under `skills/`. Installs
into Claude Code and OpenCode.

## Layout

```
my-skills/
├── .claude-plugin/
│   ├── plugin.json          # plugin manifest (Claude Code)
│   └── marketplace.json     # marketplace manifest, for /plugin marketplace add
├── skills/
│   └── <skill-name>/
│       ├── SKILL.md         # the skill: frontmatter + instructions
│       ├── scripts/         # optional helper code
│       ├── references/      # optional supporting docs
│       └── examples/        # optional worked examples
├── scripts/
│   ├── install.sh           # install / list / uninstall
│   └── new-skill.sh         # scaffold a new skill
└── README.md
```

A skill is valid when `skills/<name>/SKILL.md` exists with YAML frontmatter
containing `name` and `description`. Everything else in the directory is
optional.

## Install

```bash
./scripts/install.sh              # every skill, into Claude Code and OpenCode
./scripts/install.sh --list       # show what is in the repo
./scripts/install.sh slide-creator
./scripts/install.sh --target claude
./scripts/install.sh --target opencode
./scripts/install.sh --mode copy  # copy instead of symlink
./scripts/install.sh --uninstall
./scripts/install.sh --dry-run
```

Default install is a symlink per skill, so edits in this repo take effect
immediately with no reinstall.

Install locations:

| Host | Path |
|---|---|
| Claude Code | `~/.claude/skills/<name>` |
| OpenCode | `~/.config/opencode/skills/<name>` |

Override with `CLAUDE_CONFIG_DIR` and `OPENCODE_CONFIG_DIR`. OpenCode also
reads `~/.claude/skills` as a compatibility root, so installing for Claude
Code alone already makes the skills visible to OpenCode. Installing for both
keeps each host's own directory authoritative.

## New skill

```bash
./scripts/new-skill.sh my-skill-name --description "What it does"
```

Creates `skills/my-skill-name/` with a `SKILL.md` template, then edit and
install it.

## As a Claude Code plugin

The repo is also a valid plugin. Push it to GitHub, then:

```
/plugin marketplace add <owner>/<repo>
/plugin install my-skills@my-skills
```

Plugin skills are invoked as `/my-skills:<skill-name>`.

## Skills in this repo

Run `./scripts/install.sh --list` for the live list.
