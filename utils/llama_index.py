import os

import streamlit as st

from warnings import filterwarnings
import utils.logs as logs
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.node_parser import SentenceSplitter

# This is not used but required by llama-index and must be set FIRST
os.environ["OPENAI_API_KEY"] = "sk-abc123"

from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    Settings,
)



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
        nodes = node_parser.get_nodes_from_documents(documents, show_progress=True)
        # by default, the node ids are set to random uuids. To ensure same id's per run, we manually set them.
        for idx, node in enumerate(nodes):
            node.id_ = f"node_{idx}"
        logs.log.info(f"Loaded {len(nodes):,} nodes from files")
        return nodes
    
    except Exception as err:
        logs.log.error(f"Error creating data index: {err}")
        raise Exception(f"Error creating data index: {err}")
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

        logs.log.info("Query Engine created successfully")

        return query_engine
    except Exception as e:
        logs.log.error(f"Error when creating Query Engine: {e}")
        raise Exception(f"Error when creating Query Engine: {e}")
