# Enterprise Data Analyst Agent

## Overview

An AI-powered enterprise data analyst that allows users to ask questions about company data using natural language.

The agent can reason about a user's question, select the appropriate tools, retrieve information, analyze the results, and provide a final answer.

## Current Iteration (Implemented)

The current iteration is a command-line, tool-calling agent. It uses a Google Generative AI chat model configured through the `MODEL` environment variable and exposes four tools:

* `get_sales_data` returns the current sample sales data.
* `calculate` evaluates a mathematical expression.
* `query_database` executes read-only SELECT queries against the Northwind database with safety validation.
* `generate_chart` creates line or bar charts from SQL query results and saves them as PNG files.

The conversation stores its message history and allows up to 10 model/tool iterations for each question. RAG and enterprise data platforms are part of the target architecture, but are not implemented in this iteration.

### Current Iteration Architecture

```text
Command Line Interface
      |  user input and final output
      v
Conversation
      |  message history and iteration limit (10)
      v
Google Generative AI Model
      |  tool calls or final response
      v
Tool Dispatcher / Tool Map
      |
      +------------------------------------------+
      |                  |                       |
      v                  v                       v
get_sales_data      calculate          query_database
src/tools/basic_tools.py              src/tools/sql_tools.py
                                              |
                                              +---> Database (Northwind)
                                              
                                              |
                                              v
                                       generate_chart
                                   src/tools/analysis_tools.py
                                              |
                                              +---> PNG Charts (charts/)
```

### Current Iteration Flow

1. The CLI accepts a user question and adds it to the conversation as a `HumanMessage`.
2. The tool-capable model receives the conversation history.
3. If the model returns no tool calls, its response is returned as the final answer.
4. If the model requests tools, the dispatcher looks up and invokes each requested tool.
5. Each tool result is added to the conversation as a `ToolMessage`.
6. The model is invoked again with the updated history, repeating until it returns a final answer.
7. The conversation stops with an error if the 10-iteration limit is exceeded; tool and conversation errors are surfaced by the CLI.

### Implemented Tools (Iteration 2)

#### 1. `query_database` (src/tools/sql_tools.py)
Executes read-only SELECT queries against the Northwind database with comprehensive safety validation:
* Enforces SELECT-only queries
* Blocks destructive operations (DROP, DELETE, UPDATE, INSERT, ALTER, TRUNCATE, etc.)
* Returns query results as formatted text
* Handles database errors gracefully

Available tables: categories, customers, employees, orders, order_details, products, suppliers, and more.

#### 2. `generate_chart` (src/tools/analysis_tools.py)
Creates data visualizations from SQL query results:
* Supports line charts and bar charts
* Accepts SQL query, chart type, X/Y column names, and title
* Uses pandas for data handling and matplotlib for rendering
* Automatically generates unique PNG filenames
* Saves charts to the `charts/` directory
* Validates columns and data before rendering

#### 3. `get_sales_data` (src/tools/basic_tools.py)
Returns sample sales data for basic queries and demonstrations.

#### 4. `calculate` (src/tools/basic_tools.py)
Evaluates mathematical expressions for computational analysis.

## Target System Flow

The following flow describes the desired architecture beyond the current iteration:

```text
User
  |
  v
Natural Language Question
  |
  v
AI Agent
  |
  +-------------------+
  | Understand Query  |
  +-------------------+
           |
           v
   Select Appropriate Tool
           |
     +-----+-----+----------------+
     |           |                |
     v           v                v
 SQL Tool    RAG/Search      Data Analysis
     |           |                |
     v           v                v
 Database    Documents        Python/Pandas
     |           |                |
     +-----------+----------------+
                 |
                 v
          Analyze Results
                 |
                 v
       Is More Information
            Required?
          /           \
        Yes            No
         |              |
         v              v
   Select Another    Final Answer
       Tool
         |
         +-------> Agent
```

## Target Functional Requirements

### 1. Natural Language Queries

Users should be able to ask questions such as:

* What was our revenue last month?
* Which product sold the most?
* Why did revenue drop in March?
* Show me sales for Product A over the last 6 months.
* What is our refund policy?

### 2. Data Access

The agent should be able to access:

* Structured business data through SQL
* Unstructured company documents
* Data analysis tools
* Eventually, large-scale data through Apache Spark / Databricks

### 3. Tool Selection

The agent should determine which tool is appropriate for a given question.

Initial tools:

* SQL database tool
* Document search tool
* Python/data-analysis tool
* Calculator

### 4. Multi-Step Agentic Workflow

The agent should be able to:

1. Understand the user's question
2. Determine what information is required
3. Select an appropriate tool
4. Execute the tool
5. Analyze the result
6. Determine whether additional information is required
7. Repeat the process when necessary
8. Generate the final answer

### 5. Data Analysis

The agent should be able to:

* Filter data
* Aggregate data
* Calculate metrics
* Compare time periods
* Identify trends
* Generate basic visualizations

### 6. Retrieval-Augmented Generation

For questions involving company documents, the agent should retrieve relevant information before generating an answer.

### 7. Explainability

The agent should provide the source or reasoning behind important answers.

Example:

> Revenue was $1.2M based on sales data for January 2026.

### 8. Error Handling

The system should handle:

* Invalid queries
* Tool failures
* Missing data
* Invalid tool arguments
* Database errors

The agent should not generate an answer based on failed or unavailable data without making this clear.

## Target Non-Functional Requirements

### 1. Performance

* Minimize unnecessary LLM calls
* Minimize unnecessary tool calls
* Maintain reasonable response times

### 2. Reliability

* The system should gracefully handle tool failures
* Invalid queries should not crash the application
* Results should be validated where appropriate

### 3. Security

* Credentials must never be exposed
* Database access must be controlled
* Destructive SQL operations must be prevented
* Users should only access authorized data

### 4. Accuracy

* Prefer database/retrieval-backed answers over unsupported generation
* Important answers should provide their source
* The agent should clearly state when information is unavailable

### 5. Scalability

The architecture should allow the data layer to evolve:

```text
SQLite / PostgreSQL
        |
        v
Larger SQL Database
        |
        v
Data Lake
        |
        v
Apache Spark
        |
        v
Databricks / Lakehouse
```

The agent layer should not need to be completely rewritten when the underlying data infrastructure changes.

### 6. Observability

The system should eventually capture the agent's execution flow:

```text
User Question
      |
      v
LLM Call
      |
      v
Tool Selected
      |
      v
Tool Execution
      |
      v
Tool Result
      |
      v
LLM Analysis
      |
      v
Final Answer
```

This will allow us to debug agent behavior and measure performance.

### 7. Maintainability

The application should be modular and separate concerns such as:

```text
agent/
├── tools/
├── database/
├── rag/
├── analysis/
├── models/
└── evaluation/
```

## Iteration 3+: Multi-Tenant Platform with Data Upload & Caching

### Overview

The next major iteration will transform this into a **multi-tenant SaaS platform** where company founders and staff can upload their own data and ask questions about it through a web interface. A key optimization is **query result caching** to reduce redundant tool invocations and improve response times in subsequent conversations.

### Multi-Tenant Data Upload System

#### User Interface Requirements

1. **Data Upload Interface**
   - Web UI for companies to upload their data
   - Support multiple data types:
     * Structured data (CSV, Excel, Parquet)
     * Documents (PDF, DOCX, TXT) for RAG-based retrieval
     * Database connection strings for direct SQL access
     * Unstructured company files (reports, policies, guides)
   - Tenant isolation: Each company's data is siloed and only accessible by their team
   - Authentication & authorization layer for role-based access

2. **Data Processing Pipeline**
   - Ingest uploaded data into tenant-specific schemas
   - Index documents for RAG (Retrieval-Augmented Generation)
   - Create database views/tables scoped to tenant
   - Validate data format and quality
   - Generate data metadata (column names, data types, row counts)

#### Backend Architecture

```text
Web UI (Upload Interface)
      |
      v
Authentication/Authorization
      |
      v
Tenant Router
      |
      +------> Tenant A Data Store
      |        ├── Structured Tables
      |        ├── Document Index
      |        └── Cached Query Results
      |
      +------> Tenant B Data Store
      |        ├── Structured Tables
      |        ├── Document Index
      |        └── Cached Query Results
      |
      v
Agent (with Tenant Context)
      |
      +------> Query Cache Lookup
      |        (Avoid redundant tool calls)
      |
      +------> Tool Dispatcher
               ├── query_database (tenant-scoped)
               ├── generate_chart
               ├── document_search (RAG)
               └── python_analysis
```

### Query Caching Strategy

#### Problem Statement
Currently, if a user asks the same question twice or asks a follow-up question that requires similar data, the agent re-executes the same database queries or document searches. This wastes:
- LLM tokens (longer conversation history)
- API calls to external services
- Computational resources
- User wait time

#### Solution: Query Result Caching (Safe Approach)

**Key Principle**: Cache on the **resolved query/command**, not the English question. The LLM decides what query to generate; if it generates the same query twice, the cache hits. If it generates a different query, cache correctly misses.

```text
LAYER 1: Query Result Cache (SAFE)
├── Cache by the ACTUAL RESOLVED QUERY, not question
├── Key: HASH(sql_query + tenant_id)
│    Example: HASH("SELECT * FROM orders WHERE date > 2026-01-01")
├── Value: {result_data, timestamp, row_count, schema}
├── Invalidation: TTL-based, manual refresh, or event-based on data updates
└── Hit only when: Model generates IDENTICAL sql/tool command
    
LAYER 2: Conversation Context Cache  
├── Store tool outputs + reasoning within a session
├── Key: HASH(tool_name + tool_args + tenant_id)
├── Value: {raw_output, execution_timestamp, model_analysis}
├── Scope: Only reused within same conversation thread
└── Use for: Follow-up questions that reference the same data already fetched
```

**Why Layer 3 (Semantic Similarity) is NOT included**:
- **The Problem**: Two semantically similar questions may need completely different queries:
  - "Revenue last month" → `SELECT SUM(revenue) FROM orders WHERE month = CURRENT_MONTH - 1`
  - "Revenue last quarter" → `SELECT SUM(revenue) FROM orders WHERE quarter = CURRENT_QUARTER - 1`
  - Caching by embedding similarity would silently return wrong data
- **No Safety Net**: Unlike actual tool calls, there's no execution to catch the error
- **Solution**: Let the LLM decide what query to generate. If it's identical, cache hits. If different, cache correctly misses.
- **Alternative**: If you want "related previous answers", show them as context to the model (don't auto-reuse)

```text
SAFE Cache Decision Logic:

User Question
     |
     v
Model decides: "What query/tool should I use?"
     |
     v
Model generates SQL: "SELECT ..."
     |
     v
Check cache key = HASH(sql)
     |
     +---> Cache HIT (same SQL)
     |     ├── Verify not stale (check TTL)
     |     ├── Reuse result
     |     └── Skip tool call ✓ SAFE
     |
     +---> Cache MISS (different SQL)
           ├── Execute tool
           ├── Get new result ✓ CORRECT
           ├── Store in cache with key=HASH(sql)
           └── Return to model
```

#### Functional Requirements

1. **Cache Invalidation**
   - **TTL-based**: Configurable expiration (e.g., 1 hour for real-time data, 24 hours for slower-changing data)
   - **Manual**: User/admin can manually refresh or invalidate cache for a specific query
   - **Event-based**: Invalidate affected cache entries when underlying data is updated (data refresh triggers)
   - **Stale data notification**: If cache is older than data's freshness window, mark as stale and re-execute

2. **Cache Metadata**
   - Each cached result stores:
     * **Cache key**: `HASH(sql_query + tenant_id)` - uniquely identifies this query for this tenant
     * **Result**: Raw data or tool output
     * **Schema**: Column names, data types (for validation)
     * **Row count**: How many results returned
     * **Execution time**: When the query ran (for freshness)
     * **TTL**: When it expires
     * **Hit count**: How many times reused (for analytics)
     * **Tool used**: Which tool generated this (query_database, generate_chart, etc.)

3. **Cache Hit vs. Miss Decision**
   - **HIT**: Model generates the same SQL query → Verify cache is not stale → Reuse result → Skip tool call
   - **MISS**: Model generates different SQL query → Execute tool → Store in cache → Return result
   - **VERIFICATION**: Always check TTL before returning cached result; if stale, treat as miss

#### Data Structure Example

```python
# Cache Entry (Safe, Query-Based)
{
    "id": "cache_abc123",
    "tenant_id": "company_xyz",
    "cache_key": "sha256_hash_of_query",  # HASH(sql_query + tenant_id)
    "sql_query": "SELECT * FROM orders WHERE date > '2026-01-01'",  # The actual query
    "tool": "query_database",
    "ttl_seconds": 3600,  # 1 hour
    "created_at": "2026-09-02T10:30:00Z",
    "expires_at": "2026-09-02T11:30:00Z",
    "is_stale": False,
    "result": {
        "schema": ["order_id", "customer_id", "total", "date"],
        "data": [
            [1001, 45, 250.00, "2026-01-02"],
            [1002, 78, 180.50, "2026-01-03"],
            ...
        ],
        "row_count": 156
    },
    "metadata": {
        "execution_time_ms": 245,
        "hit_count": 3,  # Reused 3 times
        "data_freshness": "real-time"
    }
}
```

#### Agent Integration

```python
class CachedConversation(Conversation):
    def __init__(self, model, cache_manager, tenant_id, max_iterations=10):
        super().__init__(model, max_iterations)
        self.cache_manager = cache_manager
        self.tenant_id = tenant_id
    
    def ask(self, user_input: str) -> str:
        self.messages.append(HumanMessage(content=user_input))
        
        for iteration in range(self.max_iterations):
            response = self.model.invoke(self.messages)
            self.messages.append(response)
            
            if not response.tool_calls:
                return response.content  # Final answer
            
            # Process tool calls with cache awareness
            tool_messages = []
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                tool_call_id = tool_call["id"]
                
                # Generate cache key based on actual tool + args
                cache_key = self.cache_manager.generate_key(
                    tool_name, tool_args, self.tenant_id
                )
                
                # Check cache BEFORE executing tool
                cached_result = self.cache_manager.get(cache_key)
                
                if cached_result and not cached_result.is_stale():
                    # Cache hit - reuse result
                    result = cached_result.result
                    print(f"[CACHE HIT] {tool_name}")
                else:
                    # Cache miss - execute tool
                    tool = tool_map.get(tool_name)
                    if tool is None:
                        result = f"Tool '{tool_name}' is not available."
                    else:
                        try:
                            result = tool.invoke(tool_args)
                            # Store in cache for future use
                            self.cache_manager.set(
                                cache_key, 
                                result, 
                                ttl_seconds=3600,
                                metadata={
                                    "tool": tool_name,
                                    "tenant_id": self.tenant_id
                                }
                            )
                            print(f"[CACHE MISS] {tool_name} - stored result")
                        except Exception as error:
                            result = f"Tool '{tool_name}' failed: {error}"
                
                tool_messages.append(
                    ToolMessage(
                        content=str(result),
                        tool_call_id=tool_call_id,
                    )
                )
            
            self.messages.extend(tool_messages)
        
        raise RuntimeError("The conversation has exceeded max iterations.")
```

**Key Safety Features**:
1. Cache key = `HASH(tool_name + tool_args + tenant_id)` → Only hits when exact same query/tool call
2. Stale check prevents returning outdated data
3. If cache misses, tool always executes (no silent wrong data)
4. Model decides what query to generate (no embedding-based guessing)

#### Performance Metrics to Track

- Cache hit rate (%)
- Average response time (cached vs. uncached)
- Tokens saved per cached hit
- Cache invalidation frequency
- Storage used per tenant

### Implementation Phases

**Phase 1: Single-Tenant with Cache**
- Implement query result caching layer
- Add cache management (store, lookup, invalidate)
- Measure improvements

**Phase 2: Multi-Tenant Architecture**
- Add authentication/authorization
- Implement tenant isolation
- Deploy multi-tenant data layer

**Phase 3: Advanced Caching**
- Semantic caching using embeddings
- Intelligent cache invalidation
- Cross-conversation context reuse

**Phase 4: Web UI & Data Upload**
- File upload interface
- Data preview & validation
- Scheduled data refresh
- Data governance dashboard

## Future Scope

The project will progressively evolve from a simple tool-calling agent into an enterprise-scale AI/data system:

```text
LLM
 |
 v
Tool Calling
 |
 v
SQL
 |
 v
RAG
 |
 v
Data Analysis
 |
 v
Agentic Workflows
 |
 v
Memory & Evaluation
 |
 v
Multi-Tenant Platform
 |
 v
Query Caching & Optimization
 |
 v
Multi-Agent Systems
 |
 v
Apache Spark
 |
 v
Databricks / Lakehouse
```
