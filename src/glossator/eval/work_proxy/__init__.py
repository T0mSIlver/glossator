"""The Vibe Work stand-in: the Conversations API's Connector tool loop.

Work has no API, but a Work session is a Connector-attached agent, and the
Conversations API runs the same server-side tool loop with the same model and
``reasoning_effort``. This package sends a question set through that loop --
one agent per run, one unstored conversation per question -- and writes a run
directory the consumer ``judge`` and ``score`` subcommands read unchanged.
"""
