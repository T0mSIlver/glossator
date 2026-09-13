---
url: https://docs.mistral.ai/studio/workflows/building-workflows/activities
title: Activities
breadcrumbs: [Studio, Workflows, Building Workflows]
kind: doc
locale: en
source_path: src/content/en/docs/studio/workflows/building-workflows/activities/page.mdx
source_commit: 2ca5afeebb3ee0e675575d1ac60f3c138d2c4a3d
---

# Activities

This page covers the practical patterns for building activities. For the underlying model (atomicity, retries, replay semantics), see [Core Concepts > Activities](https://docs.mistral.ai/studio/workflows/getting-started/core_concepts/activities).

An activity is a unit of work that performs computations, API calls, file I/O, LLM calls, or anything else with side effects. Key characteristics:

- **Safe to re-execute**: a retry after a partial failure leaves the system in a consistent state. Side effects converge to the same observable outcome (the precise notion of *idempotency*; outputs need not be byte-identical).
- **Isolated execution**: each activity runs in its own process, with automatic retries on failure.
- **JSON-serializable I/O**: inputs and outputs accept any JSON-serializable types, such as `str`, `int`, `dict`, or `list`.
- **Per-call limit**: 2MB of input or output per call. For larger payloads, see [Payload offloading](https://docs.mistral.ai/studio/workflows/building-workflows/payload_offloading).

## Topics {#topics}

- [Basics](https://docs.mistral.ai/studio/workflows/building-workflows/activities/basics): defining activities, configuring timeouts and retries, heartbeats, granularity, nesting. **Start here.**
- [Local activities](https://docs.mistral.ai/studio/workflows/building-workflows/activities/local_activities): run sub-second activities directly in the workflow worker to skip scheduling overhead.
- [Sticky worker sessions](https://docs.mistral.ai/studio/workflows/building-workflows/activities/sticky_worker_sessions): pin a sequence of activities to the same worker to share an in-memory resource (for example, a loaded ML model or a database connection).

## Choosing an activity flavor {#choosing-an-activity-flavor}

| Mode             | Routing overhead | Worker isolation | Resource sharing | Best for                                        |
| ---------------- | ---------------- | ---------------- | ---------------- | ----------------------------------------------- |
| Regular activity | Standard         | Yes              | No               | API calls, complex logic, anything with retries |
| Sticky session   | Standard         | Yes              | Yes (in-memory)  | Reusing a loaded model or database connection   |
| Local activity   | None             | No               | N/A              | Sub-second pure computations and lookups        |
