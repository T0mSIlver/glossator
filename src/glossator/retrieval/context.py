"""Query parameters every request to this application must carry.

One Vespa application holds all three index variants, and two of them embed at
different sizes. Vespa resolves the type of a ranking input across every rank
profile in the application, so a query that supplies ``query(embedding)`` without
saying which schema it is for is rejected:

    Conflicting input type declarations for 'query(embedding)':
    declared as tensor<float>(x[128]) in rank profile 'weighted-rank2' in schema
    'docs_section_lowdim', and as tensor<float>(x[1024]) in schema
    'docs_section_fulldim'

Naming the schema in the YQL ``from`` clause is not enough -- the input types are
resolved before source selection. ``model.restrict`` is, and the toolkit has one
seam that reaches the request body: query params riding on the retrieval context.
"""

from typing import Any

from mistralai.search.toolkit.context import RetrievalContext
from pydantic import Field

# Vespa's source restriction. Not a bound YQL @param, but the toolkit passes every
# entry of ``query_params`` through to the request body verbatim, which is the only
# way to set a request parameter it does not model itself.
RESTRICT_PARAM = "model.restrict"


class DocsRetrievalContext(RetrievalContext):
    """A retrieval context carrying Vespa request parameters.

    Satisfies the toolkit's ``VespaFilterParamsContext`` protocol, so the params
    are applied uniformly by ``search`` and by the positional navigate/read/grep
    operations.
    """

    query_params: dict[str, Any] = Field(default_factory=dict)


def restrict_to(schema_name: str) -> DocsRetrievalContext:
    """A context that scopes every request to one schema."""
    return DocsRetrievalContext(query_params={RESTRICT_PARAM: schema_name})
