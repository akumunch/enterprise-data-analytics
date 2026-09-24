import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage

from tools.sql_tools import query_database
from tools.analysis_tools import generate_chart
from prompts import SYSTEM_PROMPT
load_dotenv()

from tools.rag_tools import ingest_pdf, search_documents_tool


model_name = os.getenv("MODEL")

llm = ChatGoogleGenerativeAI(
    model=model_name,
    temperature=0
)

def execute_tool_calls(response: AIMessage, tool_map: dict) -> list[ToolMessage]:
    tool_messages = []

    print(response.tool_calls)

    for tool_call in response.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        tool_call_id = tool_call["id"]

        tool = tool_map.get(tool_name)

        if tool is None:
            result = f"Tool '{tool_name}' is not available."
        else:
            try:
                result = tool.invoke(tool_args)
            except Exception as error:
                result = f"Tool '{tool_name}' failed: {error}"

        tool_messages.append(
            ToolMessage(
                content=str(result),
                tool_call_id=tool_call_id,
            )
        )

    return tool_messages

class Conversation: 
    def __init__(self, model, client_id: str, tool_map: dict, max_iterations: int = 10,):
        self.model = model 
        self.client_id = client_id
        self.tool_map = tool_map
        self.max_iterations = max_iterations

        #chat history
        self.messages = [SystemMessage(content=SYSTEM_PROMPT)]  

    def ask(self, user_input: str) -> str:
        self.messages.append(HumanMessage(content=user_input))

        for _ in range(self.max_iterations):
            response = self.model.invoke(self.messages) #google api receives full convo history

            if not isinstance(response, AIMessage):
                raise TypeError("The model must return an AIMessage.")

            self.messages.append(response)

            if not response.tool_calls:
                return response.content

            tool_messages = execute_tool_calls(response, self.tool_map)

            self.messages.extend(tool_messages)

        raise RuntimeError(
            "The conversation has exceeded 10 tries to execute."
        )


def main():
    client_id = "test_client_1"

    search_documents = search_documents_tool(client_id)
    tools = [query_database, generate_chart, search_documents,]
    tool_map = {"query_database": query_database, "generate_chart": generate_chart, "search_documents": search_documents, }

    llm_with_tools = llm.bind_tools(tools)

    chunks_added = ingest_pdf("company_policy.pdf", client_id=client_id)
    print(f"Ingested {chunks_added} chunks for {client_id}")

    conversation = Conversation(llm_with_tools, tool_map=tool_map, client_id=client_id)

    print("Type 'exit' or 'quit' to stop.")

    while True:
        user_input = input("\nYou: ").strip()

        print(conversation.messages)

        if user_input.lower() in {"exit", "quit"}:
            print("Bye bye.")
            break

        if not user_input:
            continue

        try:
            answer = conversation.ask(user_input)
            print(f"\nAI: {answer[0][answer[0]['type']].replace('*','')}")
        except Exception as error:
            print(f"\nError: {error}")

if __name__ == "__main__":
    main()