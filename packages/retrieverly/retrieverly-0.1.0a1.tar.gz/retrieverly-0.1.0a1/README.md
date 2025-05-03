# Retrieverly 

**Retrieverly: A lightweight, async-first Python package for building Multi-Modal Retrieval-Augmented Generation (RAG) applications.**

Retrieverly simplifies the process of indexing visual content (images, pages from PDFs) and retrieving the most relevant items based on text queries. It integrates with Cohere's multimodal embeddings and Qdrant vector stores out-of-the-box.

**Key Features:**

*   **Async First:** Built with `asyncio` for efficient I/O operations.
*   **Multi-Modal Indexing:** Supports indexing individual image files (`.png`, `.jpg`, `.jpeg`, `.bmp`) and extracting/indexing images from PDF pages.
*   **Text-to-Image Retrieval:** Retrieve relevant images or PDF pages based on natural language queries.
*   **Cohere Integration:** Uses Cohere's powerful `embed-v4.0` model for generating multimodal embeddings.
*   **Qdrant Integration:** Provides a ready-to-use vector store implementation using Qdrant (supports in-memory, local, and cloud instances).
*   **Extensible:** Base classes (`VectorStore`, `EmbeddingProvider`) allow for integration with other vector databases or embedding models.
*   **Simple API:** Easy-to-use interface for indexing and retrieval.

## Table of Contents

- [Retrieverly](#retrieverly)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
    - [Dependencies](#dependencies)
      - [Poppler (External System Dependency)](#poppler-external-system-dependency)
      - [Python Dependencies](#python-dependencies)
  - [Quickstart](#quickstart)
    - [Output Directory](#output-directory)
  - [Contributing](#contributing)
  - [License](#license)

## Installation

You can install `retrieverly` using pip:

```bash
pip install retrieverly
```

**Requirements:**

*   Python 3.11+

### Dependencies

#### Poppler (External System Dependency)

Retrieverly uses the `pdf2image` library to extract images from PDF files. `pdf2image` relies on the **Poppler** PDF rendering library utilities being installed on your system and available in your PATH.

**Installation Instructions:**

*   **Debian/Ubuntu:**
    ```bash
    sudo apt-get update && sudo apt-get install poppler-utils
    ```
*   **macOS (using Homebrew):**
    ```bash
    brew install poppler
    ```
*   **Windows:**
    *   Download the latest Poppler binaries (e.g., from [here](https://github.com/oschwartz10612/poppler-windows/releases/)).
    *   Extract the archive.
    *   Add the `bin/` directory from the extracted archive to your system's PATH environment variable.


You can check if Poppler is likely installed and accessible using:
```python
from retrieverly.utils import check_poppler_installed

if check_poppler_installed():
    print("Poppler utilities seem to be installed and accessible.")
else:
    print("Warning: Poppler utilities (needed for PDF indexing) not found in PATH.")
```

#### Python Dependencies

Retrieverly's core Python dependencies (like `cohere`, `qdrant-client`, `pdf2image`, `Pillow`, `numpy`) are listed in `pyproject.toml` and will be installed automatically by pip.


## Quickstart

This example demonstrates indexing a PDF and retrieving relevant pages based on a text query using an in-memory Qdrant database.

```python
#!/usr/bin/env python3
"""
Simple usage example for Retrieverly.
"""

import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from qdrant_client import AsyncQdrantClient

from retrieverly import MultiModalRAG, QdrantVectorStore


async def main():
    # Load environment variables
    load_dotenv()

    # Configuration
    pdf_path = "PATH_TO_YOUR_FILE.pdf"

    cohere_api_key = os.getenv("COHERE_API_KEY")

    try:
        # Initialize vector store
        qdrant_client = AsyncQdrantClient(":memory:")
        vector_store = QdrantVectorStore(qdrant_client, collection_name="my_collection")

        # Initialize RAG client
        rag = MultiModalRAG(vector_store, cohere_api_key, verbose=True)

        # Index PDF
        summary = await rag.index(pdf_path)
        print(f"Indexing summary: {summary}")

        # Retrieve results
        while True:
            # Get query from user
            query = input("\nEnter your query (or 'exit' to quit): ")
            
            if query.lower() == "exit":
                break

            # Retrieve results
            results = await rag.retrieve(query, top_k=3)

            # Display results
            for i, result in enumerate(results, 1):
                print(f"\nResult {i}:")
                print(f"  Source: {result.source_file}")
                print(f"  Page: {result.page_number}")
                print(f"  Score: {result.score:.4f}")
                
                # Show a preview of the image data
                if result.image_data_base64:
                    print(f"  Image Data: {result.image_data_base64[:50]}...")
                elif result.image_path:
                    print(f"  Image Path: {result.image_path}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```


### Output Directory

The `output_dir` parameter in `MultiModalRAG` specifies where supporting files are stored, primarily the images extracted from PDFs when using `storage_mode="reference"`.

*   **Default:** If `output_dir` is not provided, it defaults to `./.retrieverly/data` (a directory named `.retrieverly` containing `data`) **relative to the current working directory** where your Python script is executed.
*   **Specified Path:** If you provide a path (e.g., `output_dir="my_data"` or `output_dir="/abs/path/data"`), Retrieverly will resolve it:
    *   Relative paths are interpreted relative to the current working directory.
    *   Absolute paths are used directly.
*   **Creation:** Retrieverly ensures this directory exists, creating it if necessary.


## Contributing

Contributions are welcome! Please follow these guidelines:

1.  **Reporting Issues:** Use the GitHub issue tracker to report bugs, suggest features, or ask questions. Provide clear steps to reproduce bugs.
2.  **Pull Requests:**
    *   Fork the repository.
    *   Create a new branch for your feature or bug fix.
    *   Install development dependencies: `pip install -e .[dev]`
    *   Make your changes.
    *   Ensure code is formatted (`black .`), sorted (`isort .`), and passes type checks (`mypy src`). Add tests if applicable.
    *   Commit your changes with clear messages.
    *   Push your branch and open a pull request against the main branch.
3.  **Code Style:** Follow Black for formatting, isort for imports, and use type hints (checked with MyPy).

## License

This project is licensed under the **MIT License**. See the `LICENSE` file for details.

---