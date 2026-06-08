# API Documentation

## GET /
Returns project name, status, and disclaimer.

## GET /health
Returns API health.

## POST /predict
Request:

```json
{"ppg": [0.01, 0.04, 0.08], "fs": 64.0}
```

Response includes prediction, confidence, uncertainty, signal quality, risk flag, top features, explanation, and disclaimer.

## GET /model-info
Returns model name, version, dataset mode, metrics path, and limitations.

## GET /sample-response
Returns a demo prediction response.

