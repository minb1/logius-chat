# Git Documentation Chat

A RAG (Retrieval-Augmented Generation) application that allows users to interact with Git documentation through a chat interface.

## Features

- Chat interface for querying Git documentation
- RAG architecture using Gemini API for embeddings and text generation
- Pinecone vector database for efficient similarity search
- No authentication required

## Architecture

The application follows a layered architecture:

1. **Frontend**: Simple chat interface built with HTML, CSS, and JavaScript
2. **API Layer**: Django REST Framework endpoints for handling chat requests
3. **Context Layer**: Orchestrates the RAG workflow
4. **Prompt Layer**: Generates prompts with retrieved context
5. **Model Layer**: Handles embeddings and text generation using Gemini API

## Setup

### Prerequisites

- Python 3.8+
- Gemini API key
- Pinecone API key and environment

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
   # Edit .env with your API keys
   ```

4. Create the data directory for document chunks:
   ```
   mkdir -p logius_chat/data/chunks
   ```

5. Run migrations:
   ```
   python logius_chat/manage.py migrate
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

## License

[MIT License](LICENSE)