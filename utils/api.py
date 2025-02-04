import threading, uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
from llama_index.core.base.response.schema import Response
from llama_index.core.query_engine.retriever_query_engine import RetrieverQueryEngine

import utils.logs as logs
from utils.latex_helper import replace_latex_inline

class MathQuery(BaseModel):
    question: str

class SourceReference(BaseModel):
    file_name: str
    page: Optional[int]
    text: str
    score: float

class MathResponse(BaseModel):
    response: str
    references: Dict[str, SourceReference]

global_query_engine: Optional[RetrieverQueryEngine] = None
api_thread: Optional[threading.Thread] = None

app = FastAPI()

def run_api():
    """Runs FastAPI in a separate thread."""
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000, 
        log_level="warning"
    )

def start_api():
    """
    Start the API in a new thread if not already running
    
    Args:
        N/A
    
    Returns:
        bool: True if the API was started, False if it was already running
    
    Note:
        This should automatically be called from the Streamlit app when the query engine is created.
    """
    global api_thread
    
    if api_thread and api_thread.is_alive():
        logs.log.info("API query engine already updated")
        return False
        
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    logs.log.info("API started on port 8000")
    return True

def set_query_engine(query_engine: RetrieverQueryEngine):
    """
    Set the global query engine instance.

    Args:
        query_engine (RetrieverQueryEngine): The query engine to use for the API
    
    Returns:
        N/A
    
    Note:
        This should automatically be called from the Streamlit app when the query engine is created.
    """
    global global_query_engine
    global_query_engine = query_engine

@app.post("/api/math-query", response_model=MathResponse)
async def process_math_query(query: MathQuery):
    """
    Process a mathematical query and return the answer with relevant sources.
    
    Args:
        query (MathQuery): The query object containing the question
        
    Returns:
        MathResponse: Object containing the generated answer and source references
        
    Raises:
        HTTPException: If the query engine is not initialized or other errors occur
    """
    try:
        if global_query_engine is None:
            raise HTTPException(
                status_code=500,
                detail="Query engine not initialized. Please ensure documents are loaded first."
            )

        # Process LaTeX in the question to match indexed content
        processed_question = replace_latex_inline(query.question)
        response: Response = global_query_engine.query(processed_question)

        references = {}
        if hasattr(response, 'source_nodes'):
            for i, node in enumerate(response.source_nodes):
                references[f"Reference {i+1}"] = SourceReference(
                    file_name=node.metadata.get('file_name', 'Unknown'),
                    page=int(node.metadata['page_label']) if 'page_label' in node.metadata else None,
                    text=node.text[:100] + "..." if len(node.text) > 100 else node.text,
                    score=round(node.score, 3) if hasattr(node, 'score') else 0.0
                )

        return MathResponse(
            response=str(response),
            references=references
        )

    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Error processing query: {str(e)}"
        )

@app.get("/api/health")
async def health_check():
    """
    Simple health check endpoint to verify API is running.

    Args:
        N/A
    
    Returns:
        dict: A dictionary containing the status and whether the query engine is initialized
    
    Note:
        This is used to check if the API is running while the query engine is initialized.
    """
    return {
        "status": "healthy",
        "query_engine_initialized": global_query_engine is not None
    }