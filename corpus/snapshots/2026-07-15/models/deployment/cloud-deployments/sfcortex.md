---
url: https://docs.mistral.ai/models/deployment/cloud-deployments/sfcortex
title: Snowflake Cortex
breadcrumbs: [Models, Deployment, Cloud]
kind: doc
locale: en
source_path: src/content/en/docs/models/deployment/cloud-deployments/sfcortex/page.mdx
source_commit: 7925ed1f1b7f02a453d3747e88aa58d1537c304c
---

# Snowflake Cortex

Mistral AI's open and commercial models can be leveraged from the Snowflake Cortex platform as fully managed endpoints. Mistral models on Snowflake Cortex are serverless services, so you don't have to manage any infrastructure.

As of today, the following models are available:
- Mistral Large
- Mistral 7B

For more details, visit the [models](https://docs.mistral.ai/models/overview) page.

## Getting Started {#getting-started}

The following sections outline the steps to query the latest version of Mistral Large on the Snowflake Cortex platform.

### Getting Access to the Model {#getting-access-to-the-model}

The following items are required:
- The associated Snowflake account must be in a compatible region (see the [region list](https://docs.snowflake.com/en/user-guide/snowflake-cortex/llm-functions#availability) in the Snowflake documentation).
- The principal calling the model must have the `CORTEX_USER` database role.

### Querying the Model (Chat Completion) {#querying-the-model}

The model can be called either directly in SQL or in Python using Snowpark ML. It is exposed via the [`COMPLETE` _LLM function_](https://docs.snowflake.com/en/sql-reference/functions/complete-snowflake-cortex).

**SQL**

```sql
SELECT SNOWFLAKE.CORTEX.COMPLETE('mistral-large2', 'Who is the best French painter? Answer in one short sentence.');
```

**Python**

Execute this code either from a hosted Snowflake notebook or from your local machine.

For local execution, you need to:
- Create a virtual environment with the following package:
    - `snowflake-ml-python` (tested with version `1.6.1`)
- Ensure that you have a [configuration file](https://docs.snowflake.com/en/user-guide/snowsql-config) with the proper credentials on your system. The example below assumes that you have a named connection called `mistral` that is configured appropriately.

```python
from snowflake.snowpark import Session
from snowflake.ml.utils import connection_params
from snowflake.cortex import Complete

# Start session (local execution only)
params = connection_params.SnowflakeLoginOptions(connection_name="mistral")
session = Session.builder.configs(params).create()

# Query the model
prompt = "Who is the best French painter? Answer in one short sentence."
completion = Complete(model="mistral-large2", prompt=prompt)
print(completion)
```

## Going Further {#going-further}

For more information and examples, you can check the Snowflake documentation for:
- [LLM functions](https://docs.snowflake.com/en/user-guide/snowflake-cortex/llm-functions)
- The API of the `COMPLETE` function in [SQL](https://docs.snowflake.com/en/sql-reference/functions/complete-snowflake-cortex) and [Python](https://docs.snowflake.com/en/developer-guide/snowpark-ml/reference/latest/api/model/snowflake.cortex.Complete).
