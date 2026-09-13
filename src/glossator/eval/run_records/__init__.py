"""The durable record of one run: config, every call, every candidate, metrics.

D-023: a number that cannot be traced back to raw model output cannot be
defended. The run directory holds that trace, and the README is rendered from
it -- no sentence in the README is written by hand or preserved across a
regeneration.
"""
