"""Where does a real question's similarity stop and a junk question's begin?

D-030 wants two numbers on the retriever: an absolute cosine floor and a relative
margin below the query's own best hit. Both are only defensible if the corridor
between real questions and junk ones was measured rather than guessed, so this
runs both populations through the live index, records the similarity at four
depths per query, and proposes the numbers only when the two distributions
actually separate. When they overlap it says so and proposes nothing: a floor
picked from overlapping distributions refuses real questions.

Junk questions are written here rather than generated, from domains the corpus
has no reason to contain -- cooking, veterinary medicine, astronomy, sport. They
are ordinary, well-formed questions, because a malformed one would be refused for
the wrong reason.

Usage:
    python -m glossator.eval.calibrate_floors --dataset eval/dev.jsonl --name dev
"""
