"""Attach Vespa's schema restriction to each retrieval request.

The application contains embedding tensors of different sizes, so
``model.restrict`` must select a schema before Vespa resolves ranking input types.
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
