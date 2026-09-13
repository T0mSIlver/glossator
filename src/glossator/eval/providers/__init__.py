"""One chat client for the OpenAI-compatible endpoints the offline tools call.

Everything the evaluation tooling asks a model goes through here, so that every
request is cached by content, recorded verbatim in the run directory (D-023), and
counted. The run directory is the durable ledger; the disk cache only stops a
rerun from paying twice.
"""
