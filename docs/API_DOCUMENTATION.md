# API Documentation

## GET /
Returns project name, status, and disclaimer.

## GET /health
Returns API health.

## POST /predict
Request:

```json
{"ppg": [0.01, 0.04, 0.08], "fs": 64.0, "top_k": 3}
```

Response includes prediction, confidence, uncertainty, signal quality, risk flag, top features, similar indexed windows, explanation, and disclaimer.

The `similar_windows` field is populated from the local vector index at `models/ppg_feature_vector_index.joblib` when it exists. If the index has not been generated yet, the API returns an empty list and marks retrieval as disabled.

## GET /model-info
Returns model name, version, dataset mode, metrics path, vector database metadata, and limitations.

## GET /sample-response
Returns a demo prediction response.
