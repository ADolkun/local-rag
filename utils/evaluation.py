from datetime import datetime

import streamlit as st

import utils.logs as logs

from llama_index.core.evaluation import (
    RetrieverEvaluator, 
    generate_question_context_pairs
    )


def generate_eval_dataset(nodes, llm):
    """Generate evaluation dataset from processed nodes

    Args:
        nodes[list[str]]: The nodes to evaluate
        llm[BaseLanguageModel]: The LLM to use for evaluation

    Returns:
        eval_dataset[list]: The evaluation dataset

    Raises:
        Exception: If there is an error generating the evaluation dataset

    Notes:
        Only runs if nodes and llm are available in session state
    """
    try:
        eval_dataset = generate_question_context_pairs(
            nodes=nodes,
            llm=llm,
            num_questions_per_chunk=2
        )
        logs.log.info("Evaluation dataset generated successfully")
        return eval_dataset
    except Exception as e:
        logs.log.error(f"Error generating eval dataset: {str(e)}")
        raise

def evaluate_retrieval(query_engine, eval_dataset):
    """Evaluate retrieval performance using generated dataset

    Args:
        query_engine: The query engine to evaluate
        eval_dataset: The evaluation dataset

    Returns:
        metrics[dict]: The metrics of the evaluation
        eval_results[list]: The results of the evaluation

    Raises:
        Exception: If there is an error evaluating the dataset

    Notes:
        Only runs if query_engine and eval_dataset are available
    """
    try:
        start_time = datetime.now()
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
            logs.log.warning("Empty evaluation results")
            return {"hit_rate": 0, "mrr": 0}, []
        
        eval_time = datetime.now() - start_time
        hours, remainder = divmod(eval_time.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        milliseconds = eval_time.microseconds // 1000

        metrics = {
            "hit_rate": sum(r.metric_vals_dict["hit_rate"] for r in eval_results) / len(eval_results),
            "mrr": sum(r.metric_vals_dict["mrr"] for r in eval_results) / len(eval_results),
            "eval_time": f"{hours}h {minutes}m {seconds}s {milliseconds}ms",
            "num_queries": len(eval_results)
        }
        
        logs.log.info("Evaluation completed successfully")
        return metrics, eval_results
    except Exception as e:
        logs.log.error(f"Error evaluating retrieval: {str(e)}")
        raise

# Add standalone evaluation runner
def run_retrieval_evaluation():
    """Main entry point for manual evaluation runs

    Args:
        None

    Returns:
        None

    Raises:
        Exception: If there is an error generating the evaluation dataset or evaluating the retrieval

    Notes:
        Only runs if nodes and query_engine are available in session state
    """
    try:
        if not st.session_state["nodes"]:
            raise ValueError("No documents available for evaluation")
            
        if not st.session_state["query_engine"]:
            raise ValueError("Query engine not initialized")

        eval_dataset = generate_eval_dataset(
            st.session_state["nodes"],
            st.session_state["llm"]
        )
        
        metrics, results = evaluate_retrieval(
            st.session_state["query_engine"],
            eval_dataset
        )
        
        st.session_state["eval_metrics"] = metrics
        st.session_state["eval_results"] = results
        st.session_state.setdefault("eval_history", []).append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "metrics": metrics
        })
        logs.log.info("Evaluation results stored in session state")

    except Exception as e:
        logs.log.error(f"Evaluation failed: {str(e)}")
        raise