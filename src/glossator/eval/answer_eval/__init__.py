"""Answer evaluation: every question of a dataset, through every strategy.

Two kinds of number come out of a run, and they are kept apart on purpose (D-016).
The deterministic ones -- did a verified citation land on a gold URL, did the
quotes survive the verifier, was the refusal correct, what did it cost and how
long did it take -- carry no model dependency and are the primary report. The
judged ones -- correctness against the reference answer, groundedness of the
answer's claims in the cited text, whether each citation supports the sentence it
is attached to -- come from GLM through `glossator.eval.providers` (D-021) and are
reported beside them, never merged into them.

The judges never learn which strategy produced an answer or which pages the
dataset and citations name. They see the question, the reference answer, the
answer, and each verified citation's quote and cited passage. The run records
that input verbatim with the raw output so each judgement can be audited (D-023).
"""
