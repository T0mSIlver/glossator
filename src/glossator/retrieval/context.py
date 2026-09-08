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
from mistralai.search.toolkit.plugins.vespa.context import extract_query_params
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


def with_restrict(context: RetrievalContext, schema_name: str) -> RetrievalContext:
    """The caller's context, with the schema restriction merged into its query params.

    Merged rather than substituted: a caller's context carries its own state --
    other bound YQL params, client options, tracing -- and replacing it to add one
    parameter would drop all of that silently. A caller that already pinned
    ``model.restrict`` keeps its own value.
    """
    params = extract_query_params(context)
    if RESTRICT_PARAM in params:
        return context
    # model_copy sets the field without revalidating, so a plain RetrievalContext
    # (which declares no query_params) gains one and satisfies the protocol, while
    # a context that already declares the field keeps its own type and fields.
    return context.model_copy(update={"query_params": {**params, RESTRICT_PARAM: schema_name}})
