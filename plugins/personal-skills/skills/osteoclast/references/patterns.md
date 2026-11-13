# Patterns

Each row: what it looks like, the check that shows whether it carries load, and the usual tier once the check comes
back empty. The check decides, not the resemblance. If the check finds a user, the code stays.

## Abstraction with one user

| Pattern | Check | Tier | Cut |
| --- | --- | --- | --- |
| Interface, ABC or protocol with one implementer | grep subclasses and implementers; look for plugin hooks or entry points | A | delete the interface, use the class |
| Factory, registry or DI container wiring a fixed set | grep registrations: are any added at runtime or from config? | A | construct directly |
| Wrapper that only delegates | diff the wrapper's methods against the wrapped object's | A | call the wrapped object |
| Helper called once | grep call sites | A | inline it, if the result is shorter |
| Class with one method and no state worth keeping | grep instantiations; is the instance ever passed around or subclassed? | A | make it a function |
| Strategy or policy object where one variant is ever chosen | grep where the variant is selected | A | keep the one branch |
| Value wrapper around a primitive (`Money`, `UserId`) used only internally | grep whether it crosses a public boundary | A inside, B if public | use the primitive |
| Event bus or hook points with no listeners | grep subscriptions | A | delete emit calls and the bus |

## Defensiveness

| Pattern | Check | Tier | Cut |
| --- | --- | --- | --- |
| Guard on a state the caller already rules out | trace every caller to the guarantee (type, earlier check, constructor) | A if every caller is in the repo and proven; else B | delete the guard |
| `try/except` around code that cannot raise | read what the body calls | A | unwrap |
| Catch, log and continue | does anything depend on continuing? this often hides real failures | B | let it raise |
| Fallback to a default or older path | can the primary path fail on reachable input? | B | delete the fallback |
| Retry, timeout or backoff around pure in-memory code | confirm there is no I/O underneath | A | delete |
| Retry, timeout or backoff around I/O | this is usually load | Keep | none |
| Validation repeated at an inner layer | find the outer check; confirm every path passes through it | A | keep the outermost |
| Validation where untrusted data enters | this is load | Keep | none |

## Speculative generality

| Pattern | Check | Tier | Cut |
| --- | --- | --- | --- |
| Option, parameter or flag no caller sets | grep call sites, config files, env reads, docs | A if internal; B if on a CLI, env or public API | delete it and the branches it selects |
| Config layer (file, env, defaults merge) for values that never vary | grep for anything setting them, including deploy files | B | constants |
| Plugin discovery nobody uses | grep entry points and docs | A if never called; else B | delete |
| Generic type or multi-backend support with one concrete use | grep instantiations | A | make it concrete |
| Version or compatibility shim | find the consumer that needs it | B | delete |

## Unrequested scope

| Pattern | Check | Tier | Cut |
| --- | --- | --- | --- |
| Feature the request does not mention | reread the request; grep for users | B | delete with its tests and docs |
| Caching or memoization with no stated performance need | is there a measurement or a requirement? can it go stale? does building the key reject anything (unhashable input)? | A if pure, keyed on full input and rejecting nothing; else B | delete |
| Metrics, tracing or audit logging nobody asked for | grep for a consumer | B | delete |
| Extra output formats, CLI subcommands, endpoints | reread the request | B | delete |

## Dead weight

| Pattern | Check | Tier | Cut |
| --- | --- | --- | --- |
| Unused function, class, module, constant | grep the name, including strings and dynamic imports | A; B if exported from a library | delete |
| Unreachable branch | show the condition cannot hold | A | delete |
| Dependency nothing imports | grep imports | A | remove from the manifest |
| Old and new implementation side by side | which one is called? | A | delete the unused one |
| Comment that restates the line below it | read it | A | delete; keep comments that give a reason |
| Docs for removed or imagined behavior | compare with the code | A | delete |

## Tests

Cut test bloat last, after every source cut, so the gate stays whole while source changes. Always tier B.

| Pattern | Check | Cut |
| --- | --- | --- |
| Test that asserts only that a mock was called | would it fail if the behavior broke? | delete, after confirming the behavior is covered elsewhere |
| Tests for an internal seam that is being removed | is the behavior exercised through a public entry point? | move the cases to the entry point, then delete |
| The same case repeated with trivial variation | diff the tests | keep one |
