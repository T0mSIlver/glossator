"""The search loop's caps as evaluation axes: one knob at a time (D-035c).

The loop stops after ``round_cap`` rounds, answers at most ``searches_per_round``
searches per round, and shows the model ``tool_result_chars``-character previews
of what its tools found; none of the three was ever varied. This grid varies
each in turn against the shipped point (round_cap 4, searches_per_round 4,
tool_result_chars 600), so every row isolates one knob rather than mixing three.
It runs on a local server: ``GLOSSATOR_CHAT_SERVER_URL`` points the answer layer
at it while embeddings stay on the Mistral API, and the numbers are relative
comparisons between configurations on that server -- never absolute quality
figures, which keep coming from the API.

Each configuration is a normal ``answer_eval`` run directory named
``<name>-<axis>-<value>`` (resumable like any answer run), and the grid writes a
summary directory ``<stamp>-<name>`` with the comparison table and one pair of
figures per axis.
"""
