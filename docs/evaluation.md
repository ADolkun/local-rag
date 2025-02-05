# Retrieval Evaluation

## Metrics Tracked

- **Hit Rate**: Percentage of queries where correct document was in top results
- **MRR (Mean Reciprocal Rank)**: Average of reciprocal ranks of first relevant document

## Interpretation Guidelines

| Metric       | Good Performance | Fair Performance | Poor Performance |
|--------------|-------------------|-------------------|-------------------|
| Hit Rate     | > 75%            | 50-75%            | < 50%            |
| MRR          | > 0.65           | 0.4-0.65          | < 0.4            |

**Recommendations for Improvement:**
- Increase chunk overlap for better context continuity
- Reduce chunk size for more precise embeddings
- Add domain-specific vocabulary to base LLM
- Review document preprocessing for quality issues

## Implementation Details

### Evaluation Workflow
1. Document Processing
   - Chunking with configurable size/overlap
   - Embedding generation
   - Node creation for vector search

2. Test Generation
   - Automatic question creation via LLM
   - Context pairing for validation
   - Dataset versioning

3. Metrics Calculation
   - Batch query execution
   - Position-aware scoring
   - Statistical aggregation

### Evaluation Process
1. Auto-generates test questions from document chunks
2. Runs queries against current retrieval configuration
3. Calculates metrics based on expected vs actual results
4. Stores results with timestamped history

## Limitations

- ⏱️ Computational Cost: Evaluation runtime scales with document volume
- 📚 Dataset Bias: Generated questions may not cover all use cases
- 🔄 Version Drift: Changing LLM requires re-evaluation
- 📊 Metric Variance: Results may fluctuate between hardware configurations
