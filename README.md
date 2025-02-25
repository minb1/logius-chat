# Git Documentation Chat

A RAG (Retrieval-Augmented Generation) application that allows users to interact with Git documentation through a chat interface.

## Features

- Chat interface for querying Git documentation
- RAG architecture using Gemini API for embeddings and text generation
- PostgreSQL database for storing documents and chunks
- Pinecone vector database for efficient similarity search (with PostgreSQL fallback)
- Redis for chat history management
- No authentication required

## Architecture

The application follows a layered architecture:

1. **Frontend**: Simple chat interface built with HTML, CSS, and JavaScript
2. **API Layer**: Django REST Framework endpoints for handling chat requests
3. **Context Layer**: Orchestrates the RAG workflow
4. **Prompt Layer**: Generates prompts with retrieved context
5. **Model Layer**: Handles embeddings and text generation using Gemini API
6. **Database Layer**: PostgreSQL for document storage and Redis for chat history

## Setup

### Prerequisites

- Python 3.8+
- PostgreSQL (optional, falls back to SQLite)
- Gemini API key
- Pinecone API key and environment (optional)
- Redis instance (for chat history)

### Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd logius-chat
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file based on `.env.example` and add your API keys:
   ```
   cp .env.example .env
   # Edit .env with your API keys and database settings
   ```

4. Set up the database:
   ```
   python logius_chat/manage.py migrate
   ```

5. Import chunks from the data directory (if available):
   ```
   python logius_chat/manage.py import_chunks
   ```

6. Start the development server:
   ```
   python logius_chat/manage.py runserver
   ```

7. Access the application at http://localhost:8000

## Usage

1. Open the application in your web browser
2. Type your Git-related question in the chat box
3. The application will:
   - Convert your query to embeddings
   - Find relevant Git documentation chunks
   - Generate a response based on the retrieved context
   - Display the response in the chat interface

## Data Preparation

Before using the application, you need to:

1. Prepare Git documentation by splitting it into chunks
2. Generate embeddings for each chunk
3. Store the embeddings in Pinecone

The chunks should be stored in the `logius_chat/data/chunks` directory, with each file containing a portion of the Git documentation.

## Data Management

### Document Import

You can import documents in several ways:

1. **Using the management command**:
   ```
   python logius_chat/manage.py import_document /path/to/document.md
   ```

2. **Using the API**:
   ```
   curl -X POST -F "file=@/path/to/document.md" http://localhost:8000/api/documents/
   ```

3. **Using the admin interface**:
   - Go to http://localhost:8000/admin/
   - Log in with your superuser credentials
   - Navigate to the Documents section
   - Click "Add Document" and fill in the form

### Chunking Documents

After importing a document, you can chunk it:

1. **Using the management command**:
   ```
   python logius_chat/manage.py chunk_document <document_id>
   ```

2. **Using the API**:
   ```
   curl -X POST -H "Content-Type: application/json" -d '{"chunk_size": 1000, "overlap": 200}' http://localhost:8000/api/documents/<document_id>/chunk/
   ```

### Generating Embeddings

Generate embeddings for chunks:

```
python logius_chat/manage.py generate_embeddings
```

## License

[MIT License](LICENSE)