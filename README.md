A set of experiments to determine whether generative AI, based on vague [REQUIREMENTS.md](REQUIREMENTS.md), is capable of generating Django code for the [Learning API Styles](https://github.com/ldynia/learning-api-styles) book.

The source code for book was made public on GitHub on [July 17, 2025](https://github.com/ldynia/learning-api-styles/commit/35c31d369e6bef548eaf8dff7407969ef63efb21).
The initial implementation (design, code, and tests) took a human developer about 200 hours.

For safety, and to establish somewhat controllable conditions, experiments are run in a Virtual machine started with `vagrant up` using [Vagrantfile](Vagrantfile).

# Experiments

| Date | Outcome | PR | Tool / Version | Agent | Model | Knowledge cutoff | Duration | Cost | AGENTS.md | Human guidance |
|------|---------|----|----------------|-------|-------|------------------|----------|------|-----------|----------------|
| 2026-01-18 |Poor | [1](https://github.com/marcindulak/learning-api-styles-gen-ai/pull/1) | [ralph-wiggum-bdd](https://github.com/marcindulak/ralph-wiggum-bdd) / Experimental | 2.1.9 (Claude Code) | claude-haiku-4-5-20251001 | Feb 2025 "Reliable knowledge cutoff", and Jul 2025 "Training data cutoff" | About 11 hours clock time (about 7 hours agent time) | 40% (about $10 USD) of Pro weekly plan | No | Yes

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
