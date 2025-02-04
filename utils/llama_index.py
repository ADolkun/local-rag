import os, re
import streamlit as st

from llama_index.core import (
    Document,
    VectorStoreIndex,
    SimpleDirectoryReader,
    Settings,
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.node_parser import SentenceSplitter

import utils.logs as logs

# This is not used but required by llama-index and must be set FIRST
os.environ["OPENAI_API_KEY"] = "sk-abc123"

import re

latex_pattern = re.compile(
    r"""
    (?P<dollar>\${1,2})(?P<dcontent>.+?)\1  # Matches $...$ or $$...$$
    |
    \\begin\{(?P<env>equation|align|gather|multline)\*?\}
        (?P<env_content>.+?)
    \\end\{(?P=env)\*?\}
    |
    \\?\[(?P<brack>.+?)\\?\]   # Matches \[...\]
    |
    \\?\((?P<inline>.+?)\\?\)  # Matches \(...\)
    |
    \\begin\{(?P<xtd_env>lemma|theorem|proof)\}
        (?P<xtd_content>.+?)
    \\end\{(?P=xtd_env)\}
    |
    \\DeclareMathOperator\*?\{(?P<decl_op>[A-Za-z]+)\}\{(?P<decl_expr>.+?)\}
    |
    \\ensuremath\{(?P<ensure>.+?)\}
    """,
    re.DOTALL | re.VERBOSE
)

def normalize_expression(expr: str) -> str:
    """
    Math-specific normalization without adding extra spaces around operators.
    """
    expr = re.sub(
        r'\\operatorname\*?\{([^{}]+)\}',
        lambda m: '\\' + m.group(1).replace(' ', ''),
        expr
    )
    # Remove any spaces immediately following one or more backslashes.
    expr = re.sub(r'(\\+)\s+', r'\1', expr)
    # Remove \text{...} or \mbox{...} blocks entirely.
    expr = re.sub(r'\\(text|mbox)\s*\{.*?\}', '', expr)
    # Remove or normalize spaces around certain operators
    operators = r'([=+\-*/^<>:;])'
    expr = re.sub(rf'\s*{operators}\s*', r'\1', expr)
    #  Collapse all other internal whitespace to a single space and strip leading/trailing space.
    expr = ' '.join(expr.split()).strip()

    return expr

def insert_latex_inline(text: str):
    """Extract LaTeX expressions from text"""
    new_text = []
    last_end = 0

    for match in latex_pattern.finditer(text):
        start, end = match.span()
        new_text.append(text[last_end:start])

        expr_text = None
        for group in ['dcontent', 'env_content', 'inline', 'brack',
                      'xtd_content', 'ensure', 'decl_expr']:
            if match.group(group):
                expr_text = match.group(group)
                break

        if expr_text:
            expr_text = normalize_expression(expr_text)
            inline_math = f"<<MATH: {expr_text} >>"
            new_text.append(inline_math)
        last_end = end

    new_text.append(text[last_end:])
    return ''.join(new_text)

###################################
#
# Setup Embedding Model
#
###################################


@st.cache_resource(show_spinner=False)
def setup_embedding_model(
    model: str,
):
    """
    Sets up an embedding model using the Hugging Face library.

    Args:
        model (str): The name of the embedding model to use.

    Returns:
        An instance of the HuggingFaceEmbedding class, configured with the specified model and device.

    Raises:
        ValueError: If the specified model is not a valid embedding model.

    Notes:
        The `device` parameter can be set to 'cpu' or 'cuda' to specify the device to use for the embedding computations. If 'cuda' is used and CUDA is available, the embedding model will be run on the GPU. Otherwise, it will be run on the CPU.
    """
    try:
        from torch import cuda
        device = "cpu" if not cuda.is_available() else "cuda"
    except:
        device = "cpu"
    finally:
        logs.log.info(f"Using {device} to generate embeddings")

    try:
        Settings.embed_model = HuggingFaceEmbedding(
            model_name=model,
            device=device,
        )

        logs.log.info(f"Embedding model created successfully")
        
        return
    except Exception as err:
        print(f"Failed to setup the embedding model: {err}")


###################################
#
# Load files
#
###################################


def load_files(data_dir: str):
    """
    Loads files from a directory and splits them into nodes.

    Args:
        data_dir (str): The path to the directory containing the files to be loaded.

    Returns:
        A list of nodes, where each node is a string representing information about the corresponding file.
    Raises:
        Exception: If there is an error creating the data index.

    Notes:
        The `data_dir` parameter should be a path to a directory containing files that represent the files to be loaded. The function will iterate over all files in the directory, and load their contents into a list of strings.
    """
    try:
        node_parser = SentenceSplitter(
            chunk_size=st.session_state["chunk_size"],
            chunk_overlap=st.session_state["chunk_overlap"],
            paragraph_separator="\n\n",
            secondary_chunking_regex="[^,.;。？！]+[,.;。？！]?",
        )
        
        files = SimpleDirectoryReader(input_dir=data_dir, recursive=True)
        documents = files.load_data(show_progress=True)
        processed_docs = []
        for doc in documents: 
            updated_text = insert_latex_inline(doc.text) 
            processed_docs.append(
                Document(
                    text=updated_text,
                    metadata=doc.metadata
                )
            )

        nodes = node_parser.get_nodes_from_documents(processed_docs, show_progress=True)
        # by default, the node ids are set to random uuids. To ensure same id's per run, we manually set them.
        for idx, node in enumerate(nodes):
            node.id_ = f"node_{idx}"
        logs.log.info(f"Loaded {len(nodes):,} nodes from files")
        return nodes
    
    except Exception as err:
        logs.log.error(f"File loading error: {err}")
        raise
    finally:
        for file in os.scandir(data_dir):
            if file.is_file() and not file.name.startswith(
                ".gitkeep"
            ):  # TODO: Confirm syntax here
                os.remove(file.path)
        logs.log.info(f"File loading complete; removing local file(s)")


###################################
#
# Create Node Index
#
###################################


@st.cache_resource(show_spinner=False)
def create_index(_nodes):
    """
    Creates an index from the provided nodes.

    Args:
        _nodes (list[str]): A list of strings representing the nodes to be indexed.

    Returns:
        An instance of `VectorStoreIndex`, containing the indexed data.

    Raises:
        Exception: If there is an error creating the index.

    Notes:
        The `_nodes` parameter should be a list of strings representing the content of the nodes to be indexed.
    """

    try:
        index = VectorStoreIndex(
            nodes=_nodes, show_progress=True
        )

        logs.log.info("Index created from loaded nodes successfully")

        return index
    except Exception as err:
        logs.log.error(f"Index creation failed: {err}")
        raise Exception(f"Index creation failed: {err}")


###################################
#
# Create Query Engine
#
###################################

# @st.cache_resource(show_spinner=False)
def create_query_engine(_nodes):
    """
    Creates a query engine from the provided nodes.

    Args:
        _nodes (list[str]): A list of strings representing the nodes to be indexed.

    Returns:
        An instance of `QueryEngine`, containing the indexed data and allowing for querying of the data using a variety of parameters.

    Raises:
        Exception: If there is an error creating the query engine.

    Notes:
        The `_nodes` parameter should be a list of strings representing the content of the nodes to be indexed.

        This function uses the `create_index` function to create an index from the provided nodes, and then creates a query engine from the resulting index. The `query_engine` parameter is used to specify the parameters of the query engine, including the number of top-ranked items to return (`similarity_top_k`) and the response mode (`response_mode`).
    """
    try:
        index = create_index(_nodes)
        
        query_engine = index.as_query_engine(
            similarity_top_k=st.session_state["top_k"],
            response_mode=st.session_state["chat_mode"],
            streaming=True,
        )

        st.session_state["query_engine"] = query_engine
        logs.log.info("Latex-aware query engine created successfully")
        return query_engine
    
    except Exception as e:
        logs.log.error(f"Error creating query engine: {e}")
        raise

