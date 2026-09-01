# Topic 28 — LangChain Message Flow: Concrete Example

This is a practical companion to the LangChain message-flow mental model.

## Mental model

```text
HumanMessage
      ↓
   Chat Model
      ↓
   AIMessage
   + tool call
      ↓
   Tool execution
      ↓
  ToolMessage
      ↓
   Chat Model
      ↓
  final AIMessage
```

## Example scenario

Suppose the user asks:

> "What is the current balance of account 1234?"

The model has access to a `get_account_balance` tool.

---

## 1. HumanMessage — user sends the request

```python
from langchain_core.messages import HumanMessage

messages = [
    HumanMessage(content="What is the current balance of account 1234?")
]
```

The `HumanMessage` represents the user's input.

```text
HumanMessage
content = "What is the current balance of account 1234?"
```

At this point, no tool has executed.

---

## 2. Chat Model — model receives the messages

The chat model receives the message sequence:

```python
response = model.invoke(messages)
```

The model decides that it does not have the account balance itself and should call the available tool.

---

## 3. AIMessage + tool call — model requests an action

The model returns an `AIMessage` containing a tool call.

Conceptually:

```text
AIMessage
content = ""
tool_calls = [
    {
        "name": "get_account_balance",
        "args": {"account_id": "1234"},
        "id": "call_001"
    }
]
```

Important point:

> The AI message is **not the tool result**. It is the model saying, "Please execute this tool with these arguments."

---

## 4. Tool execution — application executes the tool

The application/agent runtime sees the tool call and invokes the actual function.

```python
def get_account_balance(account_id: str) -> float:
    return 12500.50
```

Execution:

```python
result = get_account_balance("1234")
```

Result:

```text
12500.50
```

The tool itself is deterministic application code or an external service; the model is requesting the action.

---

## 5. ToolMessage — send the tool result back to the model

The tool result is represented as a `ToolMessage`.

```python
from langchain_core.messages import ToolMessage

messages.append(
    ToolMessage(
        content="12500.50",
        tool_call_id="call_001",
    )
)
```

Now the conversation history is conceptually:

```text
HumanMessage
  "What is the current balance of account 1234?"

AIMessage
  tool_call → get_account_balance(account_id="1234")

ToolMessage
  "12500.50"
```

The `tool_call_id` associates the result with the specific tool call.

---

## 6. Chat Model again — model sees the tool result

The updated message history is sent back to the chat model.

```python
final = model.invoke(messages)
```

Now the model has:

```text
User question
      +
Its previous tool call
      +
Tool result
```

It can use that evidence to produce the final response.

---

## 7. Final AIMessage — model answers the user

The model may now return:

```text
AIMessage
content = "The current balance of account 1234 is $12,500.50."
```

This is the final user-facing answer.

---

# Complete flow with concrete data

```text
1. HumanMessage
   "What is the current balance of account 1234?"

          ↓

2. Chat Model
   Decides a tool is needed

          ↓

3. AIMessage
   tool_call:
   get_account_balance({"account_id": "1234"})

          ↓

4. Tool execution
   get_account_balance("1234")
   → 12500.50

          ↓

5. ToolMessage
   "12500.50"

          ↓

6. Chat Model
   Interprets the tool result

          ↓

7. Final AIMessage
   "The current balance ... is $12,500.50."
```

---

## Why this matters for agents

This flow is the basic building block for tool-calling agents.

The model can decide:

```text
Do I answer directly?

or

Do I call a tool?
```

For more complex tasks, the loop can repeat:

```text
HumanMessage
    ↓
 Chat Model
    ↓
 AIMessage + Tool A
    ↓
 ToolMessage
    ↓
 Chat Model
    ↓
 AIMessage + Tool B
    ↓
 ToolMessage
    ↓
 Chat Model
    ↓
 Final AIMessage
```

---

## RAG connection

The same pattern can be used when retrieval is exposed as a tool.

Example:

```text
HumanMessage
"What is our refund policy?"
        ↓
Chat Model
        ↓
AIMessage + search_documents(query=...)
        ↓
Retrieval tool
        ↓
ToolMessage
contains retrieved chunks
        ↓
Chat Model
        ↓
Final AIMessage
with grounded answer
```

In our AI Platform architecture, retrieval can remain a dedicated service/component while LangChain handles the message/tool orchestration around it.

---

## Interview questions

### What is an `AIMessage`?

> A message representing the model's response. It can contain normal generated content or, in a tool-calling interaction, one or more tool call requests.

### What is a `ToolMessage`?

> A message carrying the result of a tool execution back to the model, associated with the corresponding tool call.

### Does the LLM execute the tool?

> No. The model requests the tool call; the application or agent runtime executes the tool and sends the result back as a tool message.

### Why do we call the model again after the `ToolMessage`?

> The model needs the tool result as context so it can interpret it and either call another tool or produce the final answer.

### Can there be multiple tool calls?

> Yes. An agent can execute multiple tools in sequence or, depending on the model/runtime, handle multiple tool calls before producing the final response.
