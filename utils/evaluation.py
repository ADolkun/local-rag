from llama_index.core.evaluation import (
    RetrieverEvaluator, 
    generate_question_context_pairs
    )



def generate_eval_dataset(nodes, llm):
    """Generate evaluation dataset from processed nodes"""
    try:
        eval_dataset = generate_question_context_pairs(
            nodes=nodes,
            llm=llm,
            num_questions_per_chunk=2
        )
        return eval_dataset
    except Exception as e:
        print(f"Error generating eval dataset: {str(e)}")
        raise

def evaluate_retrieval(query_engine, eval_dataset):
    """Evaluate retrieval performance using generated dataset"""
    try:
        evaluator = RetrieverEvaluator.from_metric_names(
            ["hit_rate", "mrr"], 
            retriever=query_engine.retriever
        )
        
        eval_results = []
        for query_id, query in eval_dataset.queries.items():
            expected_ids = eval_dataset.relevant_docs[query_id]
            
            result = evaluator.evaluate(
                query=query,
                expected_ids=expected_ids
            )
            eval_results.append(result)

        if len(eval_results) == 0:
            return {"hit_rate": 0, "mrr": 0}, []
            
        metrics = {
            "hit_rate": sum(r.metric_vals_dict["hit_rate"] for r in eval_results) / len(eval_results),
            "mrr": sum(r.metric_vals_dict["mrr"] for r in eval_results) / len(eval_results),
        }
        
        return metrics, eval_results
    except Exception as e:
        print(f"Error evaluating retrieval: {str(e)}")
        raise
