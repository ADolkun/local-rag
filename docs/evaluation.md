# Retrieval Evaluation

## Metrics Tracked

- **Hit Rate**: Percentage of queries where correct document was in top results
- **MRR (Mean Reciprocal Rank)**: Average of reciprocal ranks of first relevant document

## Implementation Details

Evaluation process:
1. Auto-generates test questions from document chunks
2. Runs queries against current retrieval configuration
3. Calculates metrics based on expected vs actual results
4. Stores results with timestamped history
