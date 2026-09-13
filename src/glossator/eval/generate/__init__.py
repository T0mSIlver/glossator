"""Question generators for the development set.

Six kinds of question, one generator each, all drawing on the vendored corpus and
all recorded: every candidate the model produced, why it was kept or dropped, and
every call behind it (D-023). A generator is only allowed to be wrong loudly --
a candidate that cannot be checked is dropped and recorded, never silently
turned into a dataset row.
"""
