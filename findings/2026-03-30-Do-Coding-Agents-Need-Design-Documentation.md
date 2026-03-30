# Do Coding Agents Need Design Documentation?

Coding agent orchestrators generate design documentation, implementation plans, and even specifications.
Whether these documents should be kept, and which ones, is debated (see for example [spec-kit](https://github.com/github/spec-kit/discussions/1437), [agentbench](https://github.com/eth-sri/agentbench), [symphony](https://github.com/openai/symphony/discussions/49), [OpenSpec](https://github.com/Fission-AI/OpenSpec/issues/878), [superpowers](https://github.com/obra/superpowers/issues/729)).

We tested the effect of providing design documentation to a coding agent orchestrator on our project.
The result is nuanced.

## What is design documentation?

Software design documentation describes the choices used to implement the requirements.
Development methodologies vary in how they treat design documentation.

Agile emphasizes working software over comprehensive documentation, often leaving design decisions unrecorded.
Waterfall specifies requirements upfront, makes design choices based on those requirements, formulates the specification, and then implements it.

Let's explain the relation among these concepts using an example.
A requirement describes what the system does, for example 'System must authenticate users', and a design choice explains how to meet the requirement, e.g. 'Use JWT for user authentication'.
A specification (or spec) then provides a detailed technical description of the system, including design decisions such as “JWT tokens expire after 24 hours, refresh tokens after 7 days”.

Neither the agile nor the waterfall approach focuses on documenting rejected design alternatives.
Architecture Decision Records (ADRs) address this gap, but remain a separate practice.

The often overlooked "fake rational design" (FRD) described by Parnas in the 1980s is different in the way it treats design documentation.
Because upfront design is hard to achieve, and actual design is ad-hoc and iterative, this approach requires documenting design decisions and rejected alternatives retrospectively, and presenting them as if the process had been rationally planned from the start.

> We will never find a process that allows us to design software in a perfectly rational way. The good news is that we can fake it. We can present our system to others as if we had been rational designers and it pays to pretend do so during development and maintenance.
>
> We make a policy of recording all of the design alternatives that we considered and rejected. For each, we explain why it was considered and why it was finally rejected. Months, weeks, or even hours later, when we wonder why we did what we did, we can find out.
> 
> - Parnas and Clements, [A rational design process: How and why to fake it](https://doi.org/10.1109/TSE.1986.6312940), 1986

Developers often ignored spec-driven development until it became relevant with Large Language Model (LLM) coding agents.
FRD documentation was probably neglected even more than specs.
Could such design documentation be valuable for coding agents?

## Is design documentation useful for coding agents?

To explore this question, we chose our own project, [Learning API Styles](https://learningapistyles.com).
We created it to demonstrate various web API styles, including REST, GraphQL, Web Feeds, gRPC, Webhooks, WebSocket, and Messaging.
The initial implementation (design, code, and tests) took a human developer about 200 hours, with GitHub Copilot chat in 2023.

As authors of the book, we were often asked whether coding agents could autonomously generate comparable code today.
Coding agents produce code fast and cheaply, so we ran code generation under different conditions and compared the results.
We decided to evaluate two things: speed (development time, a proxy for model usage cost) and code similarity (how much the generated code resembled the reference implementation).

We ran three experiments with increasing levels of design documentation guidance.
The agent given design documentation (see the documentation [here](https://github.com/marcindulak/learning-api-styles-gen-ai-experiments/blob/2026-03-08/REQUIREMENTS.md)) was not meaningfully faster and partly ignored it. For example, it used `WORKDIR=app` instead of the documented `WORKDIR=/app`, and skipped the documented `api.openweathermap.org` API choice.
On the other hand, the agent took several similar decisions across all three experiments, such as the choice of Django REST Framework or Atom feeds implementation.
This appears to reflect the model's preferences rather than the provided documentation.

The full results are available at [learning-api-styles-gen-ai-experiments](https://github.com/marcindulak/learning-api-styles-gen-ai-experiments) across three experiments: [2026-03-01](https://github.com/marcindulak/learning-api-styles-gen-ai-experiments?tab=readme-ov-file#2026-03-01) (agent alone), [2026-03-02](https://github.com/marcindulak/learning-api-styles-gen-ai-experiments?tab=readme-ov-file#2026-03-02) (agent with orchestrator), and [2026-03-08](https://github.com/marcindulak/learning-api-styles-gen-ai-experiments?tab=readme-ov-file#2026-03-08) (agent with orchestrator and access to design documentation produced by 2026-03-02).

## Is design documentation useful overall?

One may argue that our result is only a single case, and that with a different model, prompt or orchestrator, an agent might follow design documentation better.
In our case, the agent did not.
Greater compliance with the documentation could be achieved with extra verification steps, but then the documentation would be used as post-implementation enforcement rather than to help the agent upfront.

The problem is that current command-line coding agents behave nondeterministically and [tend not to follow instructions](https://github.com/anthropics/claude-code/issues/13689), so they may skip or invert some of the documented design choices.
Even with verification, they may produce working software with gaps and inconsistencies, because it's infeasible to document all software behavior.
Hickey called a similar pattern "guardrail programming":

> I think we're in this world I like to call guardrail programming. Right. It's really sad. We're like, I can make change cause I have tests. Right? Who does that?  Who drives their car around banging against the guardrails, saying whoa, I'm glad I've got these guardrails because I'd never make it to the show on time.
>
> - Rich Hickey, [Simple Made Easy](https://www.youtube.com/watch?v=SxdOUGdseq4#t=16m08s), 2011

On the other hand, when the design documentation itself is inaccurate, agents that follow it may repeat mistakes. 
Both agents and developers may also question such documentation and depart from it, but when agents do so, their choices are often unfounded, whereas developers can rely on experience and intuition.
When coding agents deviate from the design documentation, humans can use it as a reference to make decisions and correct the agents.
