# pyforgejo

A Python client library for accessing the [Forgejo](https://forgejo.org/) API.

**:warning: pyforgejo `2.0` introduces significant changes.** If you're using `1.0`, you can view docs on the [`1.0` branch](https://codeberg.org/harabat/pyforgejo/src/branch/1.0).

## Usage

1. Create an `.env` file in your project directory with the `BASE_URL` and your `API_KEY`:

``` yaml
BASE_URL=https://codeberg.org/api/v1
API_KEY=your_api_key
```

2. Create a client and call an endpoint:

```python
from pyforgejo import PyforgejoApi

client = PyforgejoApi()

# get a specific repo
repo = client.repository.repo_get(owner='harabat', repo='pyforgejo')

repo
# Repository(allow_fast_forward_only_merge=False, allow_merge_commits=True, allow_rebase=True, ...)

repo.dict()
# {'allow_fast_forward_only_merge': False,
#  'allow_merge_commits': True,
#  'allow_rebase': True,
#  ...
# }

# list issues for the repo
issues = client.issue.list_issues(owner=repo.owner.login, repo=repo.name)

[issue.title for issue in issues]
# ['Normalize option model names',
#  'Calling methods from client',
#  '`parsed` is None for most methods',
#  '`openapi-python-client` does not support `text/plain` requests']
```

The client follows this pattern for calling endpoints:

``` python
client.<resource>.<operation_id>(args)
```
where:

- `<resource>`: the API resource (e.g., `repository`, `issue`, `user`)
- `<operation_id>`: the specific operation, derived from the OpenAPI spec's `operationId` (converted to snake_case)

You can find the `resource` and `operation_id` either in the [Swagger spec](https://codeberg.org/swagger.v1.json) or in the [API reference](https://codeberg.org/api/swagger). 

## Installation

``` shell
pip install pyforgejo
```

## Forgejo API Resources

- [API Usage | Forgejo](https://forgejo.org/docs/latest/user/api-usage/): user guide for the Forgejo API
- [Forgejo API | Codeberg](https://forgejo.org/api/swagger): API reference for Forgejo
- [Forgejo API Swagger spec | Codeberg](https://forgejo.org/swagger.v1.json): Forgejo API Swagger spec
- [About Swagger Specification | Documentation | Swagger](https://swagger.io/docs/specification/about/): docs for Swagger spec
- [The OpenAPI Specification Explained | OpenAPI Documentation](https://learn.openapis.org/specification/): docs for OpenAPI spec

## Development

### Using `fern`

`pyforgejo` 2.0 is generated with [fern](https://github.com/fern-api/fern), based on a slightly edited Forgejo OpenAPI spec.

The user experience and code architecture of the `fern`-generated client follow best practice. As the library is tested by users, we will identify any issues inherent to `fern` that prove limiting to `pyforgejo`: if we find such issues and cannot patch them upstream, the current codebase provides a good foundation for further development and any divergence from `fern` would not affect the vast majority of usecases.

### Generating the client with `fern`

1. Install fern, initialise a new workspace, and specify `pyforgejo` as the name of your organisation (= client).

``` shell
npm install -g fern-api

fern init --openapi https://code.forgejo.org/swagger.v1.json
# Please enter your organization: pyforgejo
```

2. Edit the `fern/openapi/openapi.json` file to keep only `AuthorizationHeaderToken` in `securityDefinitions` and `security`.

``` json
"securityDefinitions": {
  "AuthorizationHeaderToken": {
    "description": "API tokens must be prepended with \"token\" followed by a space.",
    "type": "apiKey",
    "name": "Authorization",
    "in": "header"
  }
},
"security": [
  {
    "AuthorizationHeaderToken": []
  }
]
```

3. Convert [Forgejo's Swagger (v2) API spec](https://code.forgejo.org/swagger.v1.json) to [OpenAPI v3](https://spec.openapis.org/oas/v3.0.1.html) via <https://converter.swagger.io/>.

4. Modify endpoints with multiple return types in `fern/openapi/openapi.json`.

``` diff
    "/repos/{owner}/{repo}/contents/{filepath}": {
      "get": {
        // ...
        "responses": {
          "200": {
-            "$ref": "#/components/responses/ContentsResponse"
+            "description": "A single file's contents or a directory listing",
+            "content": {
+              "application/json": {
+                "schema": {
+                  "oneOf": [
+                    {
+                      "$ref": "#/components/schemas/ContentsResponse"
+                    },
+                    {
+                      "type": "array",
+                      "items": {
+                        "$ref": "#/components/schemas/ContentsResponse"
+                      }
+                    }
+                  ]
+                }
+              },
+              "text/html": {
+                "schema": {
+                  "oneOf": [
+                    {
+                      "$ref": "#/components/schemas/ContentsResponse"
+                    },
+                    {
+                      "type": "array",
+                      "items": {
+                        "$ref": "#/components/schemas/ContentsResponse"
+                      }
+                    }
+                  ]
+                }
+              }
+            }
          },
          "404": {
            "$ref": "#/components/responses/notFound"
          }
        }
      },
// ...
    },
```

5. Add the Python SDK generator to `fern`.

``` shell
fern add fernapi/fern-python-sdk
```

6. Remove the other generators and modify the name of the output dir to `pyforgejo`.

``` diff
# yaml-language-server: $schema=https://schema.buildwithfern.dev/generators-yml.json
api:
  specs:
    - openapi: openapi/openapi.json
default-group: local
groups:
  local:
    generators:
-      - name: fernapi/fern-typescript-sdk
-        # ...
      - name: fernapi/fern-python-sdk
        version: x.x.x
        output:
          location: local-file-system
-          path: ../sdks/python
+          path: ../sdks/pyforgejo
```

7. Generate the client (output will be in `sdks/pyforgejo`).

``` shell
fern generate
# you'll have to login to GitHub
```

8. Create a `.env` file in `sdks/pyforgejo` with your `BASE_URL` and `API_KEY`.

``` yml
BASE_URL=https://codeberg.org/api/v1
API_KEY="token your_api_key"
```

9. Modify the `PyforgejoApi` and `AsyncPyforgejoApi` classes in `sdks/pyforgejo/pyforgejo/client.py` to use environment variables.

``` diff
# ...
from .user.client import AsyncUserClient
+import os
+from dotenv import load_dotenv
+
+load_dotenv()
+
+BASE_URL = os.getenv('BASE_URL')
+API_KEY = os.getenv('API_KEY')

class PyforgejoApi:
# ...
    base_url : typing.Optional[str]
-        The base url to use for requests from the client.
+        The base url to use for requests from the client. Defaults to BASE_URL from .env file.
# ...
-    api_key : str
+    api_key : typing.Optional[str]
+        The API key to use for authentication. Defaults to API_KEY from .env file.
# ...
    def __init__(
# ...
-        api_key: str,
+        api_key: typing.Optional[str] = None,
# ...
     ):
+        base_url = base_url or BASE_URL
+        api_key = api_key or API_KEY
+
+        if not base_url:
+            raise ValueError("base_url must be provided either as an .env variable or as an argument")
+        if not api_key:
+            raise ValueError("api_key must be provided either as an .env variable or as an argument")
# same for AsyncPyforgejoApi
```

10. Update handling of `api_key` in `core/client_wrapper.py`.

``` diff
    def get_headers(self) -> typing.Dict[str, str]:
        headers: typing.Dict[str, str] = {
            "X-Fern-Language": "Python",
        }
-        headers["Authorization"] = self.api_key
+        headers["Authorization"] = f"token {self.api_key.replace('token ', '')}"
        return headers
```

11. Create a virtual environment and install the lib.

``` shell
cd /path/to/sdks
uv init
uv venv
uv pip install -e .
uv pip install pipreqs
uv run pipreqs ./pyforgejo --savepath requirements.txt
uv add -r requirements.txt
uv sync
```

12. Use the client as shown in the [Usage](#usage) section.

``` python
# uv pip install ipython
# uv run ipython

from pyforgejo import PyforgejoApi

client = PyforgejoApi()

user = client.user.get_current()
```

13. Run tests (tests need to be cloned from <https://codeberg.org/harabat/pyforgejo/src/branch/main/tests)>.

``` python
uv pip install pytest
uv run pytest -v tests/test_client.py
```
