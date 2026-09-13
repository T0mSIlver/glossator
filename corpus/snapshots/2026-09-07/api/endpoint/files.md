---
url: https://docs.mistral.ai/api/endpoint/files
title: Files API
breadcrumbs: [API, Files]
kind: api
locale: en
source_path: openapi.yaml
source_commit: 2e094f7bbe1395de4a738a3483def3573143d973
openapi_md5: 316010c8ca4ddeb962becf11df72be9e
openapi_url: https://docs.mistral.ai/openapi.yaml
---

# Files API

Reference for the Files endpoints of the Mistral API, generated from the OpenAPI specification.

## List Files {#operation-files_api_routes_list_files}

`GET /v1/files`

Returns a list of files that belong to the user's organization.

- Operation id: `files_api_routes_list_files`
- Tag: files

### Parameters

- `page` (integer, optional, in query)
- `page_size` (integer, optional, in query)
- `include_total` (boolean, optional, in query)
- `sample_type` (array of SampleType or null, optional, in query)
- `source` (array of Source or null, optional, in query)
- `search` (string or null, optional, in query)
- `purpose` (enum: 'fine-tune', 'batch', 'ocr', optional, in query)
- `mimetypes` (array of string or null, optional, in query)

### Responses

- `200` — OK (application/json, schema ListFilesResponse)

## Upload File {#operation-files_api_routes_upload_file}

`POST /v1/files`

Upload a file that can be used across various endpoints.

The size of individual files can be a maximum of 512 MB. The Fine-tuning API only supports .jsonl files.

Please contact us if you need to increase these storage limits.

- Operation id: `files_api_routes_upload_file`
- Tag: files

### Request body

`multipart/form-data` (required)

- `expiry` (integer or null, optional)
- `visibility` (object, optional)
- `purpose` (enum: 'fine-tune', 'batch', 'ocr', optional)
- `file` (File, required) — The File object (not file name) to be uploaded. To upload a file and specify a custom file name you should format your request as such:

  ```bash
  file=@path/to/your/file.jsonl;filename=custom_name.jsonl
  ```
  Otherwise, you can just keep the original file name:
  ```bash
  file=@path/to/your/file.jsonl
  ```

### Responses

- `200` — OK (application/json, schema CreateFileResponse)

## Retrieve File {#operation-files_api_routes_retrieve_file}

`GET /v1/files/{file_id}`

Returns information about a specific file.

- Operation id: `files_api_routes_retrieve_file`
- Tag: files

### Parameters

- `file_id` (string (uuid), required, in path)

### Responses

- `200` — OK (application/json, schema GetFileResponse)

## Delete File {#operation-files_api_routes_delete_file}

`DELETE /v1/files/{file_id}`

Delete a file.

- Operation id: `files_api_routes_delete_file`
- Tag: files

### Parameters

- `file_id` (string (uuid), required, in path)

### Responses

- `200` — OK (application/json, schema DeleteFileResponse)

## Download File {#operation-files_api_routes_download_file}

`GET /v1/files/{file_id}/content`

Download a file

- Operation id: `files_api_routes_download_file`
- Tag: files

### Parameters

- `file_id` (string (uuid), required, in path)

### Responses

- `200` — OK (application/octet-stream)

## Get Signed Url {#operation-files_api_routes_get_signed_url}

`GET /v1/files/{file_id}/url`

- Operation id: `files_api_routes_get_signed_url`
- Tag: files

### Parameters

- `file_id` (string (uuid), required, in path)
- `expiry` (integer, optional, in query) — Number of hours before the URL becomes invalid. Defaults to 24h. Must be between 1h and 168h.

### Responses

- `200` — OK (application/json, schema GetSignedUrlResponse)
