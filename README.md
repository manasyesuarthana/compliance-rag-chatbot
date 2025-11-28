# Compliance Chatbot

An intelligent chatbot that simplifies regulatory compliance. Upload your PDFs, ask the chatbot questions, and get instant, accurate answers with direct references to the source documents. It makes finding critical information quick, reliable, and conversational.

## Key Features

-   **Conversational AI:** Ask questions in plain language and get intelligent, contextual answers from the chatbot.
-   **Custom Knowledge Base:** Upload your own regulatory documents (PDFs) to teach the chatbot.
-   **Evidence-Based Answers:** Every answer includes a citation, pointing to the exact source in your documents for full transparency.
-   **Secure & Scalable:** Built with a modern microservices architecture that is both secure and ready to scale.

## Tech Stack

-   **Frontend:** React, Vite, Tailwind CSS
-   **Middleware:** Node.js, Express
-   **Backend (AI/RAG):** Python, FastAPI, Langchain, Gemini 2.5 Flash
-   **Vector Database:** ChromaDB with provided documents for initial model knowledge
-   **Containerization:** Docker, Docker Compose

## Getting Started

### Prerequisites

-   Docker and Docker Compose installed.
-   A `GOOGLE_API_KEY` with access to the Gemini API.

### Running the Application

1.  **Set your API Key:**
    ```bash
    export GOOGLE_API_KEY=[your_gemini_api_key]
    ```

2.  **Build and run the services:**
    ```bash
    docker-compose up --build
    ```

3.  **Ingest a document:**
    For security purposes, the `rag_service` is not directly exposed to the host machine for external access on `localhost:8000`. To ingest documents, you need to execute the `curl` command from within the `rag-engine` Docker container.

    First, ensure your PDF document (e.g., `gdpr.pdf`) is located in the `rag_service/data` directory so it's accessible within the container at `/app/data/`.

    Then, open a new terminal and run the following commands:
    ```bash
    # Find the container ID or name of the running rag-engine service
    docker ps

    # Execute the ingest command from within the rag-engine container
    docker exec -it <rag-engine-container-id-or-name> curl -X POST -F "file=@/app/data/gdpr.pdf" http://localhost:8000/ingest
    ```
    Replace `<rag-engine-container-id-or-name>` with the actual ID or name of your `compliance-rag-engine` container.

    *Note: Ensure the filename in the curl command matches the PDF file placed in the `rag_service/data` directory.*

4.  **Access the Chatbot:**
    Open your web browser and navigate to `http://localhost:8080`. You can now start asking questions.
