<div align="center">

# pirag: pilot-onpremise-rag

<!-- <img alt="RAG Logo" src="docs/rag-logo.jpg" width="450" style="object-fit: contain; max-width: 100%; aspect-ratio: 16 / 9;"> -->

🌱 LLM+RAG CLI project operating in On-Premise environment

[![Python](https://img.shields.io/badge/3.9+-3776AB?style=flat&logo=Python&logoColor=white&label=Python)](https://typer.tiangolo.com/)
[![CLI](https://img.shields.io/badge/CLI-orange?style=flat&logo=iterm2&logoColor=white)](https://typer.tiangolo.com/)
[![LLM](https://img.shields.io/badge/LLM-green?style=flat&logo=OpenAI&logoColor=white)](https://openai.com)
[![LangChain](https://img.shields.io/badge/LangChain-blue?style=flat&logo=Langchain&logoColor=white)](https://langchain.com)
[![Milvus](https://img.shields.io/badge/Milvus-red?style=flat&logo=Milvus&logoColor=white)](https://milvus.io/)
[![MinIO](https://img.shields.io/badge/MinIO-red?style=flat&logo=MinIO&logoColor=white)](https://min.io/)

[![PyPI - Version](https://img.shields.io/pypi/v/pirag?logo=pypi&logoColor=white)](https://pypi.org/project/pirag/)
[![Build Status](https://github.com/jyje/pilot-onpremise-rag/actions/workflows/build-and-publish.yml/badge.svg)](https://github.com/jyje/pilot-onpremise-rag/actions/workflows/build-and-publish.yml)
<!-- [![Docker](https://img.shields.io/badge/Docker-blue?style=flat&logo=Docker&logoColor=white)](https://docker.com) -->

</div>

## 🚀 Introduction

**pilot-onpremise-rag** is a CLI tool that implements a knowledge-based RAG (Retrieval-Augmented Generation) system with LLM. It provides powerful document retrieval and generation capabilities while ensuring data privacy.

## 🔧 Setup

### Install pirag from PyPI
```bash
pip install pirag
```

### Install pirag from source
```bash
git clone https://github.com/jyje/pilot-onpremise-rag
cd pilot-onpremise-rag

pip install --upgrade -e .
```

### (Optional) Setup External Dependencies
```bash
git clone https://github.com/jyje/pilot-onpremise-rag
cd pilot-onpremise-rag

docker compose -f docker/compose.yaml up
```

## 📚 Usage

### Basic Commands

```
# View help
pirag --help

# Train documents
pirag train --source ./documents

# Ask a question
pirag ask "Give me a joke for Cat-holic."
```

## 🏗️ Project Structure

```
pilot-onpremise-rag/
├── app/                        # Main application directory
│   ├── main.py                 # CLI main entry point
│   ├── setup.py                # Package setup configuration
│   ├── pyproject.toml          # PEP 517/518 build configuration
│   ├── requirements.txt        # Dependencies
│   ├── logs/                   # Application logs
│   └── rag/                    # RAG implementation
│       ├── config.py           # Configuration settings
│       ├── agent.py            # Agent implementation
│       ├── ask/                # Query handling module
│       ├── train/              # Document training module
│       ├── test/               # Testing module
│       └── doctor/             # Diagnostic tools
├── VERSION                     # Project version
├── docker/                     # Docker configuration
├── assets/                     # Static assets (Files are not included)
└── LICENSE                     # License information
```

## 🔄 How It Works

1. **Document Training**: Process local documents and store in vector database
2. **Search Engine**: Find document chunks related to user queries
3. **Context Generation**: Create LLM prompts from retrieved documents
4. **Response Generation**: Provide accurate responses via local LLM

## 💡 Key Features

- **Privacy Guaranteed**: All data and processing occurs locally
- **Multiple Document Support**: Support for PDF, Markdown, TXT, DOCX, and other formats
- **Custom LLM**: Compatible with various local LLM models
- **Vector Database**: Vector DB integration for efficient document retrieval

## 🧪 Performance Optimization

| Configuration | Memory Usage | Response Speed | Suitable Use Cases |
|--------------|-------------|---------------|-------------------|
| Light Model | 4-6GB | Fast | Simple queries, low-spec hardware |
| Medium Model | 8-12GB | Medium | General use, most queries |
| Large Model | 16GB+ | Slow | Complex document analysis, expert answers |

## 🔗 References

- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)
- [LLM Optimization Techniques](https://huggingface.co/docs/optimum/index)
- [RAG Paper](https://arxiv.org/abs/2005.11401)

## Contributing

Any contributions are welcome!

### Current Maintainers
- [Studio R4iny](https://github.com/studior4iny)
    - [jyje](https://github.com/jyje), [semir4in](https://github.com/semir4in) (Same person)
