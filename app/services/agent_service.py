from typing import TypedDict

from langgraph.graph import StateGraph, END

from app.services.rag_service import retrieve_context
import asyncio

from app.services.llm_service import (
    get_fastest_response
)

from app.db.database import AsyncSessionLocal
from app.services.tool_service import (
    get_system_stats,
    search_documents_tool
)
from app.services.memory_service import (
    save_memory,
    get_memory
)

from app.services.language_service import (
    detect_language,
    translate_to_english,
    translate_response
)


# -----------------------------
# AGENT STATE
# -----------------------------

class AgentState(TypedDict):

    query: str

    rewritten_query: str

    use_rag: bool

    use_tool: bool

    use_search_tool: bool

    context: str

    tool_result: str

    retrieved_docs: str

    session_id: str

    user_id: int

    user_role: str

    user_department: str

    memory_context: str

    plan: str

    current_step: str

    execution_results: str

    response: str

    language: str


# -----------------------------
# DECISION NODE
# -----------------------------

def decide_rag(state: AgentState):

    query = state["query"].lower()

    keywords = [
        "policy",
        "document",
        "pdf",
        "report",
        "leave",
        "finance"
    ]

    analytics_keywords = [
        "stats",
        "analytics",
        "jobs",
        "documents",
        "system"
    ]

    search_keywords = [
        "find",
        "search",
        "documents",
        "policy",
        "report",
        "analyze",
        "summary",
        "summarize",
        "risk",
        "review",
        "finance"
    ]

    use_search_tool = any(
        k in query
        for k in search_keywords
    )

    use_rag = any(
        k in query
        for k in keywords
    )

    use_tool = any(
        k in query
        for k in analytics_keywords
    )

    return {
       **state,
       "use_rag": use_rag,
       "use_tool": use_tool,
       "use_search_tool": use_search_tool
    }

# -----------------------------
# QUERY REWRITER
# -----------------------------

async def rewrite_query(state: AgentState):

    query = state["query"]

    rewrite_prompt = f"""
    Rewrite the following user query into a short
    optimized semantic search query.

    Focus only on:
    - key topics
    - important entities
    - semantic meaning

    Remove conversational words.

    User Query:
    {query}

    Optimized Query:
    """

    response = await get_fastest_response(
        rewrite_prompt,
        user_id=0
    )

    

    rewritten_query = response.get(
       "response",
        state["query"]
    ).strip()

    print("REWRITTEN QUERY:", rewritten_query)

    return {
       "query": state["query"],

       "rewritten_query": rewritten_query,

       "use_rag": state["use_rag"],

       "use_tool": state["use_tool"],

       "use_search_tool": state["use_search_tool"],

       "context": state.get("context", ""),

       "tool_result": state.get("tool_result", ""),

       "retrieved_docs": state.get("retrieved_docs", ""),

       "session_id": state["session_id"],

       "user_id": state["user_id"],

       "user_role": state["user_role"],

       "user_department": state["user_department"],

       "memory_context": state.get("memory_context", ""),

       "plan":state.get("plan",""),

       "current_step":state.get("current_step",""),

       "execution_results":state.get("execution_results",""),

       "language": state["language"],

       "response": state.get("response", "")
    }


# -----------------------------
# MEMORY NODE
# -----------------------------

async def load_memory(state: AgentState):

    session_id = state["session_id"]

    memory = await get_memory(session_id)

    formatted = "\n".join([
        f"{m['role']}: {m['message']}"
        for m in memory[-10:]
    ])

    return {
        **state,
        "memory_context": formatted
    }

# -----------------------------
# PLANNER NODE
# -----------------------------

async def planner_node(state: AgentState):

    query = state["query"]

    planning_prompt = f"""
    You are an autonomous enterprise AI planner.

    Break the user's request into
    logical execution steps.

    User Request:
    {query}

    Return concise numbered steps only.
    """

    response = await get_fastest_response(
        planning_prompt,
        user_id=0
    )

    plan = response["response"]

    print("PLAN:", plan)

    return {
        **state,
        "plan": plan
    }


# -----------------------------
# LANGUAGE NODE
# -----------------------------

def language_node(state: AgentState):

    query = state["query"]

    language = detect_language(query)

    translated_query = query

    if language != "en":

        translated_query = translate_to_english(
            query
        )

    return {
        **state,
        "query": translated_query,
        "language": language
    }
# -----------------------------
# RETRIEVAL NODE
# -----------------------------

async def retrieve_docs(state: AgentState):

    async with AsyncSessionLocal() as db:

        result = await retrieve_context(
            db=db,
            query=state.get(
                "rewritten_query",
                state["query"]
            ),
            user_department=state["user_department"],
            user_role=state["user_role"]
        )

        # -----------------------------
        # NO RELEVANT DOCUMENT FOUND
        # -----------------------------

        if result.get("needs_general_knowledge"):

            return {
                **state,
                "response": result["message"],
                "context": "",
                "needs_general_knowledge": True
            }

        return {
            **state,
            "context": result["context"],
            "needs_general_knowledge": False
        }

# -----------------------------
# TOOL NODE
# -----------------------------

async def analytics_tool(state: AgentState):

    async with AsyncSessionLocal() as db:

        stats = await get_system_stats(db)

        return {
            **state,
            "tool_result": str(stats)
        }


async def document_search_tool(state: AgentState):

    async with AsyncSessionLocal() as db:

        results = await search_documents_tool(
            db=db,
            query=state.get(
                "rewritten_query",
                state["query"]
            ),
            user_department=state["user_department"],
            user_role=state["user_role"]
        )

        return {
            **state,
            "retrieved_docs": str(results)
        }
# -----------------------------
# GENERATION NODE
# -----------------------------

async def generate_response(state: AgentState):

    if state.get("needs_general_knowledge"):

        return {
            **state,
            "response": state["response"]
        }

    query = state["query"]

    context = state.get("context", "")

    memory_context = state.get(
       "memory_context",
       ""
    )

    plan = state.get(
    "plan",
    ""
    )

    

    retrieved_docs = state.get(
        "retrieved_docs",
        ""
    )

    tool_result = state.get(
        "tool_result",
        ""
    
    )

    if context or tool_result or retrieved_docs:

        prompt = f"""
        You are an enterprise AI assistant.
 
        Use the retrieved documents and context below
        to answer the user's question accurately.

        If relevant information exists,
        summarize it clearly.

        Execution Plan:
        {plan}

        Conversation Memory:
        {memory_context}

        Retrieved Documents:
        {retrieved_docs}

        Context:
        {context}

        Tool Result:
        {tool_result}

        Question:
        {query}

        Answer:
        """

    else:

        prompt = query

    response = await get_fastest_response(
        prompt,
        user_id=0
    )

    language = state.get(
       "language",
       "en"
    )

    final_response = response["response"]

    if language != "en":

        final_response = translate_response(
            final_response,
            language
        )
    #final_response = response["response"]    

    print("CONTEXT:", context)
    print("RETRIEVED DOCS:", retrieved_docs)

    print("LLM RESPONSE:", response)

    await save_memory(
       session_id=state["session_id"],
       role="user",
       message=query
    )

    await save_memory(
       session_id=state["session_id"],
       role="assistant",
       message=final_response
    )

    return {
        **state,
        "response": final_response
    }


# -----------------------------
# ROUTER
# -----------------------------

def rag_router(state: AgentState):

    if state["use_rag"]:

        return "retrieve"

    return "generate"

# -----------------------------
# TOOL ROUTER
# -----------------------------

def tool_router(state: AgentState):

    if state.get("use_search_tool"):

        return "doc_search"

    if state["use_tool"]:

        return "tool"

    if state["use_rag"]:

        return "retrieve"

    return "generate"
# -----------------------------
# BUILD GRAPH
# -----------------------------

graph = StateGraph(AgentState)

graph.add_node(
    "decide",
    decide_rag
)

graph.add_node(
    "rewrite",
    rewrite_query
)
graph.add_node(
    "memory",
    load_memory
)

graph.add_node(
    "planner",
    planner_node
)

graph.add_node(
    "language_node",
    language_node
)

graph.add_node(
    "retrieve",
    retrieve_docs
)
graph.add_node(
    "tool",
    analytics_tool
)

graph.add_node(
    "doc_search",
    document_search_tool
)

graph.add_node(
    "generate",
    generate_response
)

graph.set_entry_point("decide")

graph.add_edge(
    "decide",
    "memory"
)

graph.add_edge(
    "memory",
    "planner"
)

graph.add_edge(
    "planner",
    "language_node"
)

graph.add_edge(
    "language_node",
    "rewrite"
)

#graph.add_edge(
 #   "planner",
  #  "rewrite"
#)

graph.add_conditional_edges(
    "rewrite",
    tool_router,
    {
        "doc_search": "doc_search",
        "tool": "tool",
        "retrieve": "retrieve",
        "generate": "generate"
    }
)

graph.add_edge(
    "retrieve",
    "generate"
)

graph.add_edge(
    "tool",
    "generate"
)

graph.add_edge(
    "doc_search",
    "generate"
)

graph.add_edge(
    "generate",
    END
)

agent = graph.compile()


# -----------------------------
# PUBLIC FUNCTION
# -----------------------------

async def run_agent(
    query: str,
    session_id: str,
    user_id: int,
    user_role: str,
    user_department: str
):

    result = await agent.ainvoke({

      "query": query,

      "session_id": session_id,

      "user_id": user_id,

      "user_role": user_role,

      "user_department": user_department,

      "language": "en",

      "memory_context": "",

      "plan": "",

      "current_step": "",

      "execution_results": "",

      "rewritten_query": "",

      "use_rag": False,

      "use_tool": False,

      "use_search_tool": False,

      "context": "",

      "tool_result": "",

      "retrieved_docs": "",

      "response": ""
    })

    return result["response"]