# Traque Ai powered by RAG
![RAQ (1)](https://github.com/user-attachments/assets/afc2009b-2c90-4c17-8a93-dc5b7eb79e5e)



[Website](https://traque.cc) | [Twitter](https://twitter.com/TraqueAi)


## Features


- **Decentralized RAG for Blockchain Analysis**: Uses Retrieval-Augmented Generation (RAG) to process and analyze blockchain transactions with high accuracy.
- **Privacy-Preserving Storage**: Leverages IPFS for secure, decentralized data storage.
- **Low-Latency Communication**: Implements MQTT for real-time data sharing between nodes.
- **Immutable and Transparent Records**: Utilizes blockchain to ensure secure and verifiable transaction tracking.
- **Address Clustering & Fund Flow Analysis**: Identifies laundering patterns and traces transactions across addresses.
- **Graph-Based Visualization**: Displays transaction paths interactively for enhanced clarity.
- **AI-Driven Anomaly Detection**: Automatically flags suspicious transactions using machine learning.
- **Scalable & Collaborative Learning**: Nodes contribute knowledge to improve global blockchain analysis.

## Key Technologies

- **IPFS**: Decentralized storage for secure and censorship-resistant data management.
- **MQTT**: Lightweight protocol for fast, efficient communication between nodes.
- **Blockchain**: Immutable ledger for recording analysis results and rewarding contributions.
- **Qdrant**: Vector database for high-speed, scalable similarity search and retrieval.

## Setup and Installation

### Clone and Build

```sh
git clone https://github.com/TraqueAi/Traque-AI
cd Traque-AI
```

Build the package:

```sh
python setup.py sdist bdist_wheel
pip install .
```

### Running in Docker Container

Run all services:

```sh
docker compose up -d
```

Download the model and start the application:

```sh
bash run.sh
```

### Setting up Qdrant (Vector Database)

Download Qdrant Image:

```sh
docker pull qdrant/qdrant
```

Run Qdrant:

```sh
docker run -d -p 6333:6333 -p 6334:6334 \
    -v ./qdrant_data:/qdrant/storage \
    qdrant/qdrant
```

For Windows:

```sh
docker run -d --name qdrant_container -p 6333:6333 -p 6334:6334 \
    -v C:/path/to/qdrant_data:/qdrant/storage \
    qdrant/qdrant:latest
```

### Setting up Dependencies

**Ollama**: Install Ollama by following the instructions on Ollama's website.

**Language Model**: Pull a language model from the Ollama library:

```sh
ollama pull llama3:8b
```

**Text Embedding Model**:

```sh
ollama pull nomic-embed-text:latest
```

Install required Python libraries:

```sh
pip install -r requirements.txt
```

## Running the Application

### Configure Node Type

Edit `main.py` to specify the node type:

- **admin**: Institute Node (manages the global embedding)
- **data**: Data Node (contributes specialized knowledge)

Start the application:

```sh
python main.py --data-dir data --nodetype admin
```

Replace `data` with the desired data directory. Set `--nodetype` to either `admin` or `data`.

---

For more details, check the [Docs](https://github.com/TraqueAi/TraqueAI).

