# Enterprise Data Analyst Agent

## Overview

An AI-powered enterprise data analyst that allows users to ask questions about company data using natural language.

The agent can reason about a user's question, select the appropriate tools, retrieve information, analyze the results, and provide a final answer.

## Current Iteration (Implemented)

The current iteration is a command-line, tool-calling agent. It uses a Google Generative AI chat model configured through the `MODEL` environment variable and exposes two tools:

* `get_sales_data` returns the current sample sales data.
* `calculate` evaluates a mathematical expression.

The conversation stores its message history and allows up to 10 model/tool iterations for each question. SQL, RAG, Python/Pandas analysis, and enterprise data platforms are part of the target architecture, but are not implemented in this iteration.

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
      +-------------------------+
      |                         |
      v                         v
get_sales_data           calculate
src/tools/basic_tools.py
```

### Current Iteration Flow

1. The CLI accepts a user question and adds it to the conversation as a `HumanMessage`.
2. The tool-capable model receives the conversation history.
3. If the model returns no tool calls, its response is returned as the final answer.
4. If the model requests tools, the dispatcher looks up and invokes each requested tool.
5. Each tool result is added to the conversation as a `ToolMessage`.
6. The model is invoked again with the updated history, repeating until it returns a final answer.
7. The conversation stops with an error if the 10-iteration limit is exceeded; tool and conversation errors are surfaced by the CLI.

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
Multi-Agent Systems
 |
 v
Apache Spark
 |
 v
Databricks / Lakehouse
```
