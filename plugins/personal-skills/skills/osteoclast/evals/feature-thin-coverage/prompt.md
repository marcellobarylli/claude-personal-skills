---
tags: [skill-creator]
max_turns: 80
timeout_seconds: 1800
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---
shopcart/pricing/ is absurdly layered for what is basically three discounts and tax (the rules are in the README). Strip it down to something a person can read in one sitting. Heads-up: the tests are thin. Do the safe cuts now; anything that changes what callers or ops could rely on, list for me instead of doing it. Leave the rest of the repo alone.
