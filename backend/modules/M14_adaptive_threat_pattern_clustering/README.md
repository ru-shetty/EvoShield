# Module 14 — Adaptive Threat Pattern Clustering

## Purpose

Assigns each normalized feature vector to a streaming-friendly
cluster and maintains cluster statistics.

## Input

Normalized FeatureVector[N]

## Output

- Cluster ID
- Cluster centroid
- Cluster size
- Mean distance
- Distance variance
- Stability score
- Error rate
- PSI score
- Distance z-score
- ADWIN drift flag
- Overall drift decision

## Algorithm

MiniBatchKMeans is used for incremental clustering.

For every incoming batch:

1. Preprocess feature vectors.
2. Incrementally update MiniBatchKMeans.
3. Predict cluster IDs.
4. Calculate distance to assigned centroid.
5. Calculate batch statistics.
6. During warmup, establish EWMA baseline.
7. Calculate PSI.
8. Calculate distance z-score.
9. Update adaptive window.
10. Detect ADWIN change.
11. Determine drift.
12. Update baseline when stable.
13. Retrain using recent feature vectors when drift occurs.

## API

### Process

POST:

`/api/m14/process/`

Example:

```json
{
    "feature_vectors": [
        {
            "entity_id": "url_001",
            "features": [
                0.12,
                0.23,
                0.31,
                0.44,
                0.51,
                0.12,
                0.18,
                0.32,
                0.42,
                0.52
            ]
        }
    ]
}