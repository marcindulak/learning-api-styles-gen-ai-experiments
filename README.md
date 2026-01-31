A set of experiments to determine whether generative AI, based on vague [REQUIREMENTS.md](REQUIREMENTS.md), is capable of generating Django code for the [Learning API Styles](https://github.com/ldynia/learning-api-styles) book.

The source code for book was made public on GitHub on [July 17, 2025](https://github.com/ldynia/learning-api-styles/commit/35c31d369e6bef548eaf8dff7407969ef63efb21).
The initial implementation (design, code, and tests) took a human developer about 200 hours.

For safety, and to establish somewhat controllable conditions, experiments are run in a Virtual machine started with `vagrant up` using [Vagrantfile](Vagrantfile).

# Experiments

| Date | Outcome | PR | Tool / Version | Agent | Model | Knowledge cutoff | Duration | Cost | AGENTS.md | Human guidance |
|------|---------|----|----------------|-------|-------|------------------|----------|------|-----------|----------------|
| 2026-01-18 |Poor | [1](https://github.com/marcindulak/learning-api-styles-gen-ai/pull/1) | [ralph-wiggum-bdd](https://github.com/marcindulak/ralph-wiggum-bdd) / Experimental | 2.1.9 (Claude Code) | claude-haiku-4-5-20251001 | Feb 2025 "Reliable knowledge cutoff", and Jul 2025 "Training data cutoff" | About 11 hours clock time (about 7 hours agent time) | $10 USD (about 40% of Pro weekly plan) | No | Yes
| 2026-01-31 |Poor | [8](https://github.com/marcindulak/learning-api-styles-gen-ai/pull/8) | [ralph-wiggum-bdd](https://github.com/marcindulak/ralph-wiggum-bdd) / [542a1ca9640cf1e59eb31eaaa51be95a85fb84bf](https://github.com/marcindulak/ralph-wiggum-bdd/commit/542a1ca9640cf1e59eb31eaaa51be95a85fb84bf) | 2.1.17 (Claude Code) | claude-opus-4-5-20251101 | May 2025 "Reliable knowledge cutoff", and Aug 2025 "Training data cutoff" | About 12 hours clock time (about 5 hours agent time) | $10 USD (about 40% of Pro weekly plan) | No | Yes

## 2026-01-18

Summary: poor outcome, despite occasional human help in interactive mode.

The agent focused on writing code instead of setting up the infrastructure (Docker, database, test runner).
Claimed success after silently skipping tests.

The agent claimed successful implementation of all features without running any tests.
It turned out that `.claude/settings.json` was blocking Docker commands, and the agent decided to silently skip tests.
The agent randomly kept discovering logical inconsistencies in [REQUIREMENTS.md](REQUIREMENTS.md).
After human in interactive mode correcting the Docker access, and instructing the agent to use Docker, the agent started using Docker, but claimed success again, despite failing to handle database cleanup during tests.
The agent kept git committing the `.cache` directory, containing Python packages, until instructed by human in interactive mode to stop.
The agent decided to use end-of-life libraries, like [Django 5.0.1](https://docs.djangoproject.com/en/6.0/releases/5.0.1/) (2024), [Daphne 4.0.0](https://pypi.org/project/daphne/4.0.0/) (2022), or an unmaintained [graphene](https://github.com/graphql-python/graphene/issues/1312) library.
The agent used different Docker commands than those present in [REQUIREMENTS.md](REQUIREMENTS.md), and created the project README.md with the commands it didn't use.
The agent left temporary files git committed (e.g., test_graphql_simple.py).
The agent was wasting time on spinning up unnecessary containers and waiting for them with sleep, because [podman compose does not support --wait](https://github.com/containers/podman-compose/issues/710).

See the screen recording of the session.
It's split into two due to Claude Code large memory use ([anthropics/claude-code/issues/11315](https://github.com/anthropics/claude-code/issues/11315)).
The videos don't represent the clock time, the long period when there are no changes on the terminal are trimmed away.

[![Watch Video 2026-01-18 Part1](images/2026-01-18-01.png)](https://www.youtube.com/watch?v=9Dog71hr3yk)

[![Watch Video 2026-01-18 Part2](images/2026-01-18-02.png)](https://www.youtube.com/watch?v=JsmNmM1K4sA)

## 2026-01-31

Summary: poor outcome, despite occasional human help in interactive mode.

The agent incorrectly claimed all features are implemented, and only admitted gaps when questioned by the human.
The non-functional requirements were not covered by tests, and TLS, OpenAPI Spec, AsyncAPI Spec requirements were skipped.

The agent correctly discovered that Docker commands were blocked, and correctly refused to mark the features as complete without running tests.
On the other hand, the agent decided to use end-of-life libraries, like [Django 5.0.1](https://docs.djangoproject.com/en/6.0/releases/5.0.1/) (2024), [graphene-django](https://github.com/graphql-python/graphene-django/releases/tag/v3.2.0) (2023), or an unmaintained [graphene](https://github.com/graphql-python/graphene/issues/1312) library.
When asked why it decided to use old or unmaintained libraries answered "I didn't make any library choices ... The implementation and library selections were made in a previous session/iteration that I have no context about.".
Moreover, despite being instructed to read CLAUDE.md, it silently ignore this instruction while encountering a file read error.

The agent got stuck several times, was not making progress for 5 up to 30 minutes, and not consuming any tokens as seen on https://claude.ai/settings/usage.
The human interventions by pressing `Ctrl+C` in the case of non-interactive run, and `Esc` during interactive run were needed to unblock the agent.

See the screen recording of the session.
The video doesn't represent the clock time, the long period when there are no changes on the terminal are trimmed away.

[![Watch Video 2026-01-31 Part1](images/2026-01-31-01.png)](https://www.youtube.com/watch?v=ZkgFuE6g8d0)
