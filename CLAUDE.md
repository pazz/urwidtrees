# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Overview

`urwidtrees` is a small library (about 1500 lines, package `urwidtrees/`) providing tree widgets for the [urwid](http://urwid.org/) toolkit. Version lives in `urwidtrees/version.py` and is read by `setup.py`.

## Commands

```sh
python3 -m unittest                                  # full test suite, as run in CI
python3 -m pytest tests/test_tree.py::TestSimpleTree::test_positions
make -C docs html                                    # API docs (needs sphinx); sources in docs/source/
```

Tests are unittest-style under `tests/`; `tests/utilities.py` has a small sample tree, a selectable `Node` widget and helpers that render decorated lines to strings. CI (`.github/workflows/test.yml`) runs the suite on Python 3.10 and 3.14 with the latest urwid, and on 3.10 with urwid 2.1.2. The scripts in `docs/examples/` are interactive demos, not checks.

`tests/test_invariants.py` checks navigation invariants on randomly generated trees (seeded, so reproducible) against a flat depth-first model of the same tree. Known bugs are marked `@unittest.expectedFailure` there; a fix removes the marker, which then serves as its regression test.

## Architecture

The design is MVC with local operations on node *positions* (opaque, hashable handles). A tree never exposes a global structure, only navigation from a position.

- `tree.py`: `Tree` is the abstract base. Subclasses implement `__getitem__(pos)` (returns the widget) plus `parent_position`, `first_child_position`, `last_child_position`, `next_sibling_position`, `prev_sibling_position`. Everything else (`depth`, `next_position`, `prev_position`, `positions`, `last_decendant`, ...) is derived from those in the base class. `SimpleTree` is the concrete implementation backed by nested lists of `(widget, [children])`, with tuple-index positions.
- `decoration.py`: `DecoratedTree` wraps another `Tree`, delegating navigation and overriding `__getitem__` via `get_decorated`/`decorate`. Behaviour is layered by wrapping: `CollapseMixin` (hides children by overriding first/last child positions; collapse state is a callable or set via `set_position_collapsed`), `CollapseIconMixin` (adds icons), `CollapsibleTree`, `IndentedTree`, `ArrowTree` and combinations. Collapsing is treated as decoration, not part of the data tree.
- `nested.py`: `NestedTree` embeds trees as nodes of other trees, so positions become nested tuples and navigation has to recurse into sub-trees (`outmost_only` and `interpret_covered` flags affect this).
- `widgets.py`: `TreeListWalker` adapts a `Tree` to an `urwid.ListWalker` (with a cache cleared by `clear_cache`); `TreeBox` is the `WidgetWrap` around `urwid.ListBox` that handles key bindings (collapse, expand, focus parent/child/sibling).

When adding a tree feature, implement it as a `DecoratedTree` subclass or mixin and compose it, rather than editing `Tree` or `SimpleTree`. Check that `NestedTree` still behaves, since it re-implements navigation instead of inheriting it.

## Change policy

- `main` is the only branch; the tag 1.0.5 marks the last release before AI-assisted work. One concern per branch off `main`, one PR each into `main`. Ask before pushing.
- Small is beautiful: the smallest clean diff that solves the problem. Prefer deletion, stdlib and existing helpers; no speculative parameters, layers or abstractions.
- Bug fixes come with a regression test that fails without the fix.
- Keep the public API (everything exported from `urwidtrees/__init__.py`, constructor keyword arguments, `TreeBox` key bindings) backwards compatible unless the change says otherwise.

## Reviews

This section applies to AI-assisted contributions; human contributors are welcome without it.

Reviewers are the agents in `.claude/agents/`. Each runs in a fresh context and gets only the branch or commit and the issue or PR numbers, never the author's summary, so that the author's assumptions do not frame the review. Run the agents of a tier in parallel. CI already runs the test suite on the Python and urwid versions above; the reviewers cover what CI cannot (tests failing without the fix, deep and wide trees, behaviour, design).

- **Trivial** (documentation, comments): `review-correctness`.
- **Normal** (everything else, including CI workflows): `review-correctness` and `review-design`.
When unsure, take the higher tier.

Every finding is either fixed or left with a reason. The PR description ends with a "Review findings and resolution" section: for each reviewer, its findings and what was done with each (fixed, or left and why).
