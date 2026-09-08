import os

# The starter migration's default contains an underscore, which toolkit 0.0.13
# rejects before backend-dependent tests can reach their offline skip.
os.environ.setdefault("COLLECTION_NAME", "exampledocs")
