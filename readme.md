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
git clone https://github.com/saeidrznr/smart-library
cd smart-library
```

[### 2. ](https://github.com/saeidrznr/smart-library)Configure Environment Variables

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

This initializes the database with the project's sample data. Run this step after the migrations have been applied and PostgreSQL is ready.

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

## API Usage

Send a `POST` request to `/chat` with a JSON body.

### Example Request

```json
{
  "question": "نام اعضایی که حداقل یک امانت معوق دارند چیست؟"
}
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

The `data` array is abbreviated for readability. Use actual output from the running application when documenting test results.

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

Check `scenario_results.json` for the scenario results if the integration script writes its results to that file.

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

- No authentication: The API does not implement user authentication or access control.
- Responses depend on Google Gemini API availability and quota.
- RAG quality depends on document retrieval and the quality of the source documents.
- NL2SQL accuracy depends on the generated SQL and the available database data.
- Documents must be indexed before using the RAG functionality.
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
