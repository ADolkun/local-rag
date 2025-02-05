# Setup Guide for Local RAG

## Prerequisites

Before setting up and running Local RAG, ensure you have the following installed:

- A local [Ollama](https://github.com/ollama/ollama/) instance.
- At least one model available within Ollama, such as `llama3:8b` or `llama2:7b`.
- Python 3.10 (Ensure your Python version is **less than 3.11**).

## MacOS Setup
### Checking Python Version
Run the following command to verify your Python version:
```sh
python3 --version
pip3 --version
```

## Installation Steps

### 1. Install Python 3.10
For macOS users, install Python using Homebrew:
```sh
brew install python@3.10
```

### 2. Install PyTorch and Dependencies (For M Series macOS)
If you are using an Apple M-series chip, install the required libraries:
```sh
pip install torch torchvision torchaudio fastapi uvicorn
```

### 3. Clone the Local RAG Repository
```sh
git clone https://github.com/jonfairbanks/local-rag.git
cd local-rag
```

### 4. Install Ollama and Run a Model
Download and install Ollama from [here](https://github.com/ollama/ollama/), then run an LLM of your choice:
```sh
ollama run llama3.1:8b
```

### 5. Install Project Dependencies
```sh
pip install pipenv && pipenv install
```
Run the following commands one by one to identify and resolve missing dependencies:
```sh
pipenv shell
streamlit run main.py
```
If there are missing dependencies, install them as suggested by the output:
```sh
pip install example_missing_library
```
After installing all required dependencies, run the application again:
```sh
streamlit run main.py
```

## Running Local RAG

### Local Setup
To start the application locally:
```sh
pipenv shell && streamlit run main.py
```

### Docker Setup
If you prefer using Docker, run the following command:
```sh
docker compose up -d
```

#### Note:
If you are running Ollama as a service, you may need to add an additional configuration to your `docker-compose.yml` file:
```yaml
extra_hosts:
  - 'host.docker.internal:host-gateway'
```

**WARNING:** This application is untested on Windows Subsystem for Linux (WSL). For best results, please use a Linux host if possible.

---
This guide ensures a smooth setup and helps troubleshoot missing dependencies effectively. Happy coding!

