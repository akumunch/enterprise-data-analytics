import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage 

from tools.basic_tools import get_sales_data, calculate

load_dotenv()

model_name = os.getenv("MODEL")

llm = ChatGoogleGenerativeAI(
    model=model_name,
    temperature=0
)

tools = [
    get_sales_data,
    calculate,
]

tool_map = {
    "get_sales_data": get_sales_data,
    "calculate": calculate,
}

llm_with_tools = llm.bind_tools(tools)

def execute_tool_calls(response: AIMessage) -> list[ToolMessage]:
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
    def __init__(
        self,
        model,
        max_iterations: int = 10,
    ):
        self.model = model 
        self.messages = [] #chat history 
        self.max_iterations = max_iterations

    def ask(self, user_input: str) -> str:
        self.messages.append(HumanMessage(content=user_input))

        for _ in range(self.max_iterations):
            response = self.model.invoke(self.messages)

            if not isinstance(response, AIMessage):
                raise TypeError("The model must return an AIMessage.")

            self.messages.append(response)

            if not response.tool_calls:
                return response.content

            tool_messages = execute_tool_calls(response)

            self.messages.extend(tool_messages)

        raise RuntimeError(
            "The conversation has exceeded 10 tries to execute."
        )


def main():
    conversation = Conversation(llm_with_tools)

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