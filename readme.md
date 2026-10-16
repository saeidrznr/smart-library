# Smart Library AI Assistant

An AI-powered library assistant built with **FastAPI, LangGraph, PostgreSQL, ChromaDB, and Google Gemini**. The system uses specialized agents to answer questions about library data and documents, perform calculations, and handle general queries.

## Features

- **NL2SQL Agent:** Answers questions about library members, books, and loans using PostgreSQL.
- **Document RAG Agent:** Retrieves relevant information from library documents using ChromaDB.
- **Calculator Agent:** Performs arithmetic and multi-step calculations.
- **Coordinator Agent:** Routes user questions to the appropriate agent using LangGraph.
- **General Agent:** Handles greetings and general queries.
- **FastAPI:** Exposes an HTTP API for interacting with the assistant.

## Architecture

LangGraph coordinates specialized agents. PostgreSQL stores structured library data, while ChromaDB stores document embeddings for semantic retrieval. Google Gemini provides language-model capabilities through its API.

<p align="center">
  <img src="reports/architecture.png" alt="System Architecture" width="700">
</p>

## Requirements

- Git
- Docker Desktop with Docker Compose
- A Google Gemini API key

## Setup and Run

Run the following commands in **PowerShell**.

### 1. Clone the Repository

```powershell
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd smart-library
```

Replace `<YOUR_GITHUB_REPOSITORY_URL>` with the actual GitHub repository URL.

### 2. Configure Environment Variables

Create a `.env` file in the project root, using `.env.example` as a template.

Configure the required values:

```env
POSTGRES_DB=library_db
POSTGRES_USER=library_user
POSTGRES_PASSWORD=your_password
DATABASE_URL=postgresql+asyncpg://library_user:your_password@db:5432/library_db
GEMINI_API_KEY=your_gemini_api_key
```

Replace `your_password` and `your_gemini_api_key` with your own values. Ensure that the database credentials in `DATABASE_URL` match `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB`.

**Important:** When the application runs inside Docker Compose, use `db` as the PostgreSQL hostname. Never commit `.env` or API keys to GitHub.

### 3. Build and Start the Containers

Build the application image and start FastAPI and PostgreSQL:

```powershell
docker compose up --build -d
```

Check the container status:

```powershell
docker compose ps
```

Both the `app` and `db` services should be running. PostgreSQL must pass its health check before the application can start.

If the application fails to start, inspect its logs:

```powershell
docker compose logs --tail=100 app
```

To follow the application logs continuously, press `Ctrl+C` to stop following them:

```powershell
docker compose logs -f app
```

For PostgreSQL logs:

```powershell
docker compose logs --tail=100 db
```

### 4. Initialize the Database

Run the database seeding script inside the application container:

```powershell
docker compose exec app python -m scripts.seed_database
```

This initializes the database with the project's sample data. Run this step after PostgreSQL is ready.

### 5. Index the Documents

Run the document indexing script inside the application container:

```powershell
docker compose exec app python index_documents.py
```

The script processes the configured source documents, splits them into chunks, generates embeddings, and stores them in ChromaDB.

Run this step before using document-based question answering. Re-run it whenever the indexed documents need to be updated.

### 6. Run and Verify the Application

If the containers are already running, the API should be accessible. Otherwise, start the existing services with:

```powershell
docker compose up -d
```

Check the status:

```powershell
docker compose ps
```

Open the interactive API documentation:

- **Swagger UI:** http://127.0.0.1:8000/docs
- **Chat API:** `POST http://127.0.0.1:8000/chat`

To test the API through Swagger UI:

1. Open http://127.0.0.1:8000/docs.
2. Expand `POST /chat`.
3. Click **Try it out**.
4. Enter the following request body.
5. Click **Execute**.

```json
{
  "question": "نام اعضایی که حداقل یک امانت معوق دارند چیست؟"
}
```

The API response should contain the assistant's answer and relevant execution details.

A valid Gemini API key and available API quota are required for model-based requests.

## API Usage

Send a `POST` request to `/chat` with a JSON body.

### Example Request

```json
{
  "question": "نام اعضایی که حداقل یک امانت معوق دارند چیست؟"
}
```

### Example Using PowerShell

```powershell
$body = @{
    question = "نام اعضایی که حداقل یک امانت معوق دارند چیست؟"
} | ConvertTo-Json

Invoke-RestMethod `
    -Uri "http://127.0.0.1:8000/chat" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
```

## Example Scenarios and Outputs

The following examples illustrate the application's main workflows. Actual answers depend on the database contents, indexed documents, and model responses.

### 1. Structured Data Query (NL2SQL)

**Request:**

```json
{
  "question": "برای هر وضعیت امانت، تعداد امانت‌ها و نام اعضایی که آن امانت‌ها را دریافت کرده‌اند نمایش بده."
}
```

**Example response:**

```json
{
  "answer": "بر اساس اطلاعات موجود در سیستم، جزئیات امانت‌ها به تفکیک وضعیت نمایش داده می‌شود.",
  "sources": [],
  "sql": "SELECT l.loan_status AS loan_status, COUNT(l.id) AS loan_count, m.full_name AS member_name FROM loans l INNER JOIN members m ON l.member_id = m.id GROUP BY l.loan_status, m.full_name",
  "data": [
    {
      "loan_status": "borrowed",
      "loan_count": 2,
      "member_name": "امیر جعفری"
    }
  ],
  "agents_used": ["sql_agent"],
  "execution_log": ["sql_agent executed"]
}
```

The `data` array is abbreviated for readability.

### 2. Document Question Answering (RAG)

**Request:**

```json
{
  "question": "برای تمدید امانت کتاب چه شرایطی باید رعایت شود؟"
}
```

**Example response:**

```json
{
  "answer": "تمدید امانت به شرایطی مانند نبود رزرو فعال، نداشتن بدهی معوق و رعایت محدودیت تعداد دفعات تمدید بستگی دارد.",
  "sources": [
    {
      "source": "پرسش و پاسخ.pdf",
      "section": "بخش سوم ـ تمدید امانت منابع",
      "chunk_type": "faq"
    },
    {
      "source": "قوانین امانت.pdf",
      "section": "ماده ۲ ـ شرایط امانت منابع",
      "chunk_type": "article_clause"
    }
  ],
  "sql": null,
  "data": null,
  "agents_used": ["document_agent"],
  "execution_log": ["document_agent executed"]
}
```

### 3. Agent and Tool Workflow

This example demonstrates a workflow that retrieves data using SQL and then uses the calculator agent to calculate a percentage.

**Request:**

```json
{
  "question": "چند درصد از کل امانت‌ها برگشت داده شده‌اند؟ نتیجه را تا دو رقم اعشار بیان کن."
}
```

**Example response:**

```json
{
  "answer": "۲۰.۰۰ درصد از کل امانت‌ها برگشت داده شده‌اند.",
  "sources": [],
  "sql": "SELECT COUNT(CASE WHEN loan_status = 'returned' THEN 1 END) AS returned_loans_count, COUNT(*) AS total_loans_count FROM loans",
  "data": [
    {
      "returned_loans_count": 5,
      "total_loans_count": 25
    }
  ],
  "agents_used": [
    "sql_agent",
    "calculator_agent"
  ],
  "execution_log": [
    "sql_agent executed",
    "calculator tool called: (5 / 25) * 100",
    "calculator_agent executed"
  ]
}
```

These examples illustrate the expected response structure. Verify exact response values against the current implementation and database contents.

## Tests

The repository includes component tests and integration scenarios. Run the following commands from the project root in PowerShell while the application container is running.

### Component Tests

```powershell
docker compose exec app pytest -v test_coodinator.py
docker compose exec app pytest -v test_graph.py
docker compose exec app pytest -v test_llm_connect.py
docker compose exec app pytest -v test_sql_agent.py
docker compose exec app pytest -v test_sql_executer.py
```

These tests cover the coordinator, graph workflow, LLM connectivity, SQL agent, and SQL execution components.

### Integration Scenarios

Run the integration scenarios:

```powershell
docker compose exec app pytest -v test_integerated.py
```

The integration script is expected to write its results to `scenario_results.json` if its implementation performs that file-writing step.

Before running tests, ensure that:

- Both containers are running.
- The database has been initialized.
- The document index has been created for RAG scenarios.
- `.env` contains a valid Gemini API key.
- The required Python test dependencies are installed in the image.

## Container Management

### Stop the Containers

```powershell
docker compose stop
```

### Start the Stopped Containers Again

```powershell
docker compose start
```

### Restart the Application

```powershell
docker compose restart app
```

### Stop and Remove the Containers

```powershell
docker compose down
```

This removes the containers and network but preserves the PostgreSQL named volume.

To also delete the PostgreSQL volume and its stored data:

```powershell
docker compose down -v
```

**Warning:** The `-v` option permanently deletes the PostgreSQL volume and its stored data.

## Limitations

- Gemini responses depend on external API availability, rate limits, and quota.
- Document-answering quality depends on the source documents, chunking, embeddings, and retrieval configuration.
- NL2SQL accuracy depends on the database schema, generated SQL, and available data.
- The document index must be created before document-based queries and refreshed when source documents change.
- Test outcomes can depend on external API access and the current database state.

## Technology Stack

| Component | Technology |
|---|---|
| API | FastAPI |
| Agent orchestration | LangGraph |
| Language model | Google Gemini |
| Structured database | PostgreSQL |
| Vector database | ChromaDB |
| Language | Python |
| Containerization | Docker Compose |

## Security Notes

- Keep `.env` and API keys out of version control.
- Use `.env.example` to document required configuration without including secrets.
- Use secure database credentials for deployments beyond local development.
- If an API key has been exposed, revoke it and replace it with a new key.
