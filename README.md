# claude-personal-skills

A personal Claude Code plugin marketplace holding skills that aren't tied to any one
project: `codex-critique`, `round-log`, `phone-learning-artifact`, `autonomous-sandbox` and `osteoclast`.

## Install on a new machine

```
/plugin marketplace add <owner>/claude-personal-skills
/plugin install personal-skills@claude-personal-skills
```

(Replace `<owner>` with wherever this repo ends up hosted — GitHub owner/repo, or a
full git URL if it's not on GitHub.)

## Dependency

`codex-critique` shells out to the separate **codex plugin**
(`openai/codex-plugin-cc`). Install that too on any machine that needs
codex-critique:

```
/plugin marketplace add openai/codex-plugin-cc
/plugin install codex@openai-codex
```

## Updating

Edit a skill under `plugins/personal-skills/skills/`, commit, push. On each
machine: `/plugin marketplace update claude-personal-skills` (or reinstall) to
pick up the change — no manual file copying.
