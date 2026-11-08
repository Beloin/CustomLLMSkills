# Writing a good SKILL.md

## The three surfaces

A skill is read in three stages, at three different moments. A fact on the
wrong surface is why a capability that exists still does not get used.

| Surface | When it enters context | What a gap costs |
|---|---|---|
| `name` + `description` | always, at startup, for every installed skill | The skill is never activated, so nothing else is ever read. |
| `SKILL.md` body | when the skill is activated | The skill runs and does not know the thing exists. |
| `references/`, `scripts/` | when the agent decides to reach for one | Nothing, until something needs it. |

The description is the only lever on whether a skill is opened. It carries
the entire burden of triggering.

## Budgets

| Element | Limit | Target |
|---|---|---|
| `name` | 64 chars, `[a-z0-9-]`, must match the directory name | 15-40 |
| `description` | 1024 chars | under 500 |
| `compatibility` | 500 chars | one sentence, usually omit |
| `SKILL.md` body | under 500 lines | 100-250 |
| reference file | none | add a Contents list past 100 lines |

Lines, not words. Frontmatter is not body: counting them together makes the
description compete with the instructions for one allowance.

## The description is a router, not documentation

Write what and when, and stop:

```yaml
description: >
  Use when the user asks for a PowerPoint deck, a .pptx file, slides for a
  talk, a conference presentation, or a thesis defense deck.
```

Not this:

```yaml
description: >
  Builds a styled 16:9 dark deck by first detecting the request, then
  selecting a layout per slide, then writing Python, then rendering to PNG…
```

A description that narrates a workflow invites the agent to follow that
summary instead of activating the skill and reading the real instructions.

Two rules that follow:

- A fact the agent lacks belongs in the description: the artefacts it must
  produce, the place they belong. Not the steps.
- A description hands over a noun, not a procedure. Naming four files gets
  the missing one written. Naming a way of working does not, because
  following it means already being inside the skill.

## What belongs in SKILL.md

A control plane, not a handbook.

In it:

1. Invariants that must never be forgotten.
2. Decisions: if X, read or run Y.
3. Workflow order, where order matters.
4. Guardrails.
5. The resource map: every reference and every executable, each with a trigger.
6. Verification: how the agent knows it is done.

Not in it: API documentation, syntax references, long examples, mappings,
lookup tables, historical explanations, CLI references, schemas. Those go to
`references/`.

Anything deterministic belongs in `scripts/`. Scripts are executed, never
loaded, so their body costs no context. A script named in `SKILL.md` costs
one line and buys the only chance the agent has of knowing it exists.

## Flat discovery: one level, always

Keep file references one level deep from `SKILL.md`. A file reachable only
through a second hop sits behind a door with no sign on it.

Name every reference and every executable in `SKILL.md`:

```markdown
## Resources

- Layout catalog: `references/layouts.md`
- Deck builder: `scripts/deck_kit.py`
```

A reference may also point at a script. That redundancy is welcome for
orientation. It must not be the only path by which the agent learns the
script exists.

## A sentence that prevents a mistake belongs in the body

A reference is for what an agent will look up once it knows it needs it: a
mapping, a schema, the fiftieth edge case. A rule that prevents a common
mistake belongs in the body, even when the surrounding treatment stays in
the reference. The body is read whenever the skill is activated; the
reference is read when the agent decides to.

## Long references need a Contents section

Agents preview long files rather than reading them whole. A contents list at
the top makes the rest of the file visible anyway. Past about 100 lines, add
one.

## Testing whether a skill triggers

- About 20 queries: 8-10 that should trigger, 8-10 that should not.
- Negatives must be near-misses: same keywords, different need.
- Skill selection is nondeterministic. Run each query about 3 times and use
  the trigger rate, with 0.5 as a reasonable threshold.
- Split train (about 60 percent) and validation (about 40 percent) and keep
  the split fixed, or the description gets overfitted to its own test set.
- Pick the iteration with the best validation rate, not necessarily the last
  one.

## Sources

- Agent Skills specification: <https://agentskills.io/specification>
- Optimizing skill descriptions: <https://agentskills.io/skill-creation/optimizing-descriptions>
- Evaluating skill output quality: <https://agentskills.io/skill-creation/evaluating-skills>
- Claude Code skills: <https://code.claude.com/docs/en/skills>
