---
name: review-architecture-decision
description: >-
  Turn a proposed system design into expert-informed trade-off analysis — showing where the architecture is sound, where it's fragile, and where it will create future cost — grounded in and quoting O'Reilly's distributed-systems and architecture literature. Use this skill whenever an engineer or architect is designing or evaluating a significant system-design choice and wants a rigorous, cited critique: event-driven vs. request/response, a messaging/streaming choice (Kafka, etc.), data consistency and exactly-once semantics, schema evolution, sharding, caching strategy, sync vs. async, or any major architecture decision. Trigger on prompts like "I'm drafting an architecture for X, evaluate the trade-offs," "how would experts assess this design," "review my system design for Y," or "what are the failure modes of this approach" — including when the design is described in prose rather than a formal doc.
---

# Architecture Decision Review

You're giving an engineer the review a respected principal architect would give: not "looks good" or "I'd do it differently," but a specific map of where the design holds up, where it's fragile, and where it quietly buys future cost — each judgment anchored in what the literature actually says, with passages quoted so the author can go read the source and argue with it.

The point is to shift the conversation from "the reviewer prefers X" to "this aligns with how Stopford frames event ordering, and here's exactly where your design diverges." That's what makes the feedback land and survive pushback.

## Step 1: Understand the design and confirm the output shape

Extract the design and the decisions inside it — from the doc, diagram, or prose. Identify the load-bearing choices: the ones that, if wrong, are expensive to reverse (data model, consistency guarantees, sync/async boundaries, partitioning, failure handling).

Then confirm what the reviewer wants, since this varies. Default to a **strong / fragile / future-cost map** (below). But if the prompt suggests otherwise, offer the alternatives briefly: a **trade-off table** (this choice vs. its alternatives, expert-backed pros/cons per row) or a **risk-ranked findings list** (riskiest decisions first). If the ask is ambiguous, ask one quick question: "Want the default map of strong/fragile/future-cost, or a trade-off table across alternatives?"

## Step 2: Query the O'Reilly MCP on the specific trade-offs

Search each load-bearing decision explicitly. Use `ask_oreilly_experts` and `search_oreilly_content`:

- "[pattern] trade-offs — when it works and when it breaks" (e.g., "exactly-once semantics trade-offs in event-driven systems")
- "schema evolution / consumer rebalancing / ordering guarantees [technology]"
- "failure modes of [architecture choice] at scale"
- "alternatives to [choice] and how to decide between them"

Pull `get_oreilly_citation` on strong hits (≥0.75) so you can **quote** — this skill leans on precise quoted passages, not paraphrase. Anchors that tend to serve well (a guide — cite what actually surfaces): *Kafka for Architects* (Gorshkova), *Designing Event-Driven Systems* (Stopford), *Foundations of Scalable Systems* (Gorton), *System Design on AWS* (Kumar & Singh). Search whatever technologies the design actually uses.

Foundational distributed-systems reasoning (ordering, consistency, failure modes) doesn't go stale. But where the trade-off depends on what a specific platform currently supports — managed service capabilities, a streaming engine's current guarantees, a cloud provider's offerings — prefer the newest coverage, since a design review that cites an outdated capability set will misjudge the trade-off.

## Step 3: Write the review

Lead with a one-line verdict on the overall shape, then the map.

---

### Architecture Review — [System / Decision]

**Overall:** one or two sentences — is this the right shape, with reservations, or is a load-bearing choice wrong?

**Sound** — decisions well-supported by the evidence.
- **[Decision]** — why it holds up, with a quoted/cited passage. *[Designing Event-Driven Systems](url) by Ben Stopford: "…"*

**Fragile** — decisions that work only under assumptions the design doesn't guarantee.
- **[Decision]** — the hidden assumption, what breaks it, and the source. Be specific about the failure mode (e.g., "exactly-once here assumes idempotent consumers; your handler isn't — on rebalance you'll double-process").

**Future cost** — decisions that are fine now but will get expensive.
- **[Decision]** — what it costs later (migration pain, operational load, lock-in) and the framework that predicts it.

**Questions to resolve before committing**
- The 2–4 sharpest questions the author should answer next.

---

## Principles

**Cite only what surfaced, and never name an expert whose work you didn't find.** It's tempting to invoke a famous name ("Kleppmann would say…") for authority, but if that author's work didn't surface in your queries, don't reference them — it's unverifiable and erodes trust. Reference and quote only authors whose work actually came back from the MCP, as markdown links with author. Never invent a title, quote, or link. When the platform carries multiple editions of a title, use the newest edition unless the user specifically needs an older one.

Quote precisely and sparingly — a sharp two-line quote beats a paragraph. Be direct about fragility; a review that only praises isn't a review. Where the evidence is genuinely mixed, say so and give the author the decision rather than a false verdict.
