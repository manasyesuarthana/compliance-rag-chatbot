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
-   **Backend (AI/RAG):** Python, FastAPI, Langchain, Gemini 1.5 Pro
-   **Vector Database:** ChromaDB
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
    Open a new terminal and use the following command to upload a PDF (e.g., `gdpr.pdf`) and teach the chatbot.
    ```bash
    curl -X POST -F "file=@gdpr.pdf" http://localhost:8000/ingest
    ```

4.  **Access the Chatbot:**
    Open your web browser and navigate to `http://localhost:8080`. You can now start asking questions.
