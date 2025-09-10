"""
LangGraph Bootcamp - Session 3: Adding Memory to Your Agent
==========================================================

Building on Sessions 1-2, we're adding memory so your agent remembers conversations.
Now it can have multi-turn conversations and remember context!

Learning Goals:
- Understand checkpointing and persistence
- Implement conversation memory
- Manage multiple conversation threads
- Debug and inspect agent state

Real-world analogy: Upgrading from a customer service rep who forgets everything 
between calls to one who remembers your history and preferences.
"""

import os
from typing import Annotated, TypedDict
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# STEP 1: ENVIRONMENT SETUP
# ============================================================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Get from: https://platform.openai.com/account/api-keys
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")  # Get from: https://tavily.com

# Initialize the language model
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

# ============================================================================
# STEP 2: ENHANCED TOOLS (INCLUDING CALCULATOR FROM HOMEWORK)
# ============================================================================

def setup_tools():
    """
    Set up tools including web search and calculator.
    """
    # Web search tool
    search_tool = TavilySearch(
        max_results=3
    )
    
    # Calculator tool (homework from Session 2)
    @tool
    def calculator(expression: str) -> str:
        """
        Calculate mathematical expressions safely.
        
        Args:
            expression: Mathematical expression like "15 + 27" or "10 * 5"
        """
        try:
            # Safe evaluation for basic math
            allowed_chars = set('0123456789+-*/.() ')
            if not all(c in allowed_chars for c in expression):
                return "Error: Only basic math operations allowed (+, -, *, /, parentheses)"
            
            result = eval(expression)
            return f"The result of {expression} is {result}"
        except Exception as e:
            return f"Error calculating '{expression}': {str(e)}"
    
    return [search_tool, calculator]

# ============================================================================
# STEP 3: STATE DEFINITION (ENHANCED FOR MEMORY DEMO)
# ============================================================================

class AgentState(TypedDict):
    """
    Agent state that will be persisted across conversations.
    
    Everything in this state gets saved automatically when using checkpointing.
    This means the agent can pick up exactly where it left off!
    """
    messages: Annotated[list, add_messages]
    # Future: We could add user_preferences, task_status, etc.

# ============================================================================
# STEP 4: AGENT NODES (SAME AS SESSION 2)
# ============================================================================

def chatbot_node(state: AgentState) -> dict:
    """
    Main conversation node - now with memory context!
    
    The LLM can see the full conversation history from the checkpointed state.
    """
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def should_continue(state: AgentState) -> str:
    """Route to tools or end based on whether tools are needed."""
    messages = state["messages"]
    last_message = messages[-1]
    
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    return "end"

# ============================================================================
# STEP 5: MEMORY-ENABLED AGENT CREATION
# ============================================================================

def create_memory_agent():
    """
    Create an agent with persistent memory using checkpointing.
    
    Key enhancement: Adding a checkpointer that saves state after each step.
    """
    # Set up tools
    tools = setup_tools()
    global llm_with_tools
    llm_with_tools = llm.bind_tools(tools)
    
    # Build the graph (same structure as Session 2)
    graph_builder = StateGraph(AgentState)
    
    graph_builder.add_node("chatbot", chatbot_node)
    graph_builder.add_node("tools", ToolNode(tools))
    
    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_conditional_edges(
        "chatbot",
        should_continue,
        {"tools": "tools", "end": END}
    )
    graph_builder.add_edge("tools", "chatbot")
    
    # 🆕 THE MAGIC: Add memory with checkpointing!
    memory = MemorySaver()  # In-memory storage for this session
    
    # Compile with checkpointer - this enables memory!
    return graph_builder.compile(checkpointer=memory)

# ============================================================================
# STEP 6: MEMORY-AWARE CONVERSATION FUNCTIONS
# ============================================================================

def chat_with_memory(agent, user_input: str, thread_id: str = "default") -> str:
    """
    Have a conversation with memory persistence.
    
    Args:
        agent: The memory-enabled agent
        user_input: What the user wants to say
        thread_id: Conversation thread identifier (each thread has separate memory)
        
    Returns:
        The agent's response
    """
    # Configuration that tells the agent which conversation thread to use
    config = {"configurable": {"thread_id": thread_id}}
    
    # Input state - just the new user message
    input_state = {"messages": [{"role": "user", "content": user_input}]}
    
    # The agent will automatically load previous conversation from this thread
    # and append the new message to the conversation history
    final_state = agent.invoke(input_state, config=config)
    
    # Return the agent's response
    return final_state["messages"][-1].content

def run_memory_chat_loop(agent):
    """
    Interactive chat with memory demonstration.
    """
    print("🧠 Memory-Enabled Chatbot Started!")
    print("Your agent now remembers everything across the conversation.")
    print("Try asking follow-up questions or referring to earlier topics.")
    print("Type 'quit' to exit, 'new' to start a new conversation thread.")
    print("=" * 70)
    
    thread_id = "main_conversation"
    conversation_count = 1
    
    while True:
        user_input = input(f"\n👤 You (Thread {conversation_count}): ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
        
        if user_input.lower() == 'new':
            conversation_count += 1
            thread_id = f"conversation_{conversation_count}"
            print(f"🔄 Started new conversation thread: {thread_id}")
            continue
            
        if not user_input:
            continue
        
        try:
            response = chat_with_memory(agent, user_input, thread_id)
            print(f"🧠 Agent: {response}")
            
        except Exception as e:
            print(f"❌ Error: {e}")

# ============================================================================
# STEP 7: MEMORY INSPECTION AND DEBUGGING
# ============================================================================

def inspect_conversation_state(agent, thread_id: str = "default"):
    """
    Inspect what the agent remembers about a conversation.
    
    This is useful for debugging and understanding what's stored in memory.
    """
    config = {"configurable": {"thread_id": thread_id}}
    
    try:
        # Get the current state snapshot
        state_snapshot = agent.get_state(config)
        
        print(f"📊 Memory Inspection for Thread: {thread_id}")
        print("=" * 50)
        
        if state_snapshot and state_snapshot.values:
            messages = state_snapshot.values.get("messages", [])
            print(f"💬 Total messages in memory: {len(messages)}")
            
            # Show conversation summary
            for i, msg in enumerate(messages):
                role = getattr(msg, 'type', 'unknown')
                content = getattr(msg, 'content', str(msg))
                
                # Truncate long messages for display
                display_content = content[:100] + "..." if len(content) > 100 else content
                print(f"  {i+1}. {role}: {display_content}")
                
        else:
            print("📝 No conversation history found for this thread.")
            
    except Exception as e:
        print(f"❌ Error inspecting state: {e}")

def demonstrate_memory_features():
    """
    Demonstrate key memory features with automated examples.
    """
    print("🎯 Memory Features Demonstration")
    print("=" * 40)
    
    agent = create_memory_agent()
    
    # Demonstrate conversation continuity
    print("\n1️⃣ Testing Conversation Continuity:")
    print("   First, I'll tell the agent my name...")
    response1 = chat_with_memory(agent, "Hi! My name is Alex and I'm learning Python.", "demo")
    print(f"   Agent: {response1[:100]}...")
    
    print("\n   Then I'll ask if it remembers...")
    response2 = chat_with_memory(agent, "Do you remember my name?", "demo")
    print(f"   Agent: {response2[:100]}...")
    
    # Demonstrate separate thread isolation
    print("\n2️⃣ Testing Thread Isolation:")
    print("   Asking the same question in a different thread...")
    response3 = chat_with_memory(agent, "Do you remember my name?", "different_thread")
    print(f"   Agent: {response3[:100]}...")
    
    # Show memory inspection
    print("\n3️⃣ Memory Contents:")
    inspect_conversation_state(agent, "demo")

def test_memory_with_tools():
    """
    Test that memory works correctly with tool usage.
    """
    print("🔧 Testing Memory + Tools Integration")
    print("=" * 40)
    
    agent = create_memory_agent()
    thread = "tool_memory_test"
    
    # Ask for a calculation
    print("\n📝 Step 1: Ask for calculation")
    calc_response = chat_with_memory(agent, "What's 25 * 47?", thread)
    print(f"Response: {calc_response[:150]}...")
    
    # Ask for search
    print("\n📝 Step 2: Ask for search")
    search_response = chat_with_memory(agent, "What's the latest news about Python?", thread)
    print(f"Response: {search_response[:150]}...")
    
    # Reference previous results
    print("\n📝 Step 3: Reference previous conversation")
    ref_response = chat_with_memory(agent, "What was that calculation result again?", thread)
    print(f"Response: {ref_response[:150]}...")
    
    # Show full conversation
    print("\n📊 Full conversation memory:")
    inspect_conversation_state(agent, thread)

# ============================================================================
# STEP 8: ADVANCED MEMORY PATTERNS
# ============================================================================

def create_user_preference_tracker():
    """
    Example of how to extend state for user preferences tracking.
    This is a preview of more advanced state management.
    """
    class AdvancedAgentState(TypedDict):
        messages: Annotated[list, add_messages]
        user_preferences: dict  # Could store user likes, dislikes, etc.
        conversation_summary: str  # Could store conversation summaries
    
    # This would require more complex state management
    # We'll cover this in later sessions
    print("💡 Advanced state management coming in Week 2!")

# ============================================================================
# STEP 9: TROUBLESHOOTING AND BEST PRACTICES
# ============================================================================

def memory_troubleshooting_guide():
    """
    Common memory-related issues and solutions.
    """
    troubleshooting_tips = """
    🔧 Memory Troubleshooting Guide:
    
    Problem: "Agent doesn't remember previous conversation"
    ✅ Solution: Make sure you're using the same thread_id
    ✅ Check: Are you passing the config parameter correctly?
    
    Problem: "Memory seems to reset randomly"
    ✅ Solution: In production, use PostgresSaver instead of MemorySaver
    ✅ Check: MemorySaver only works within the same Python session
    
    Problem: "Conversations are mixing between users"
    ✅ Solution: Use unique thread_ids per user (e.g., f"user_{user_id}")
    ✅ Best practice: thread_id = f"{user_id}_{conversation_type}"
    
    Problem: "Memory usage growing too large"
    ✅ Solution: Implement conversation summarization
    ✅ Consider: Pruning old messages or using message windows
    
    Performance Tips:
    - Use descriptive thread_ids for easier debugging
    - Consider conversation length limits for large chat histories
    - In production, regularly backup checkpoint data
    """
    print(troubleshooting_tips)

# ============================================================================
# STEP 10: MAIN EXECUTION AND HOMEWORK
# ============================================================================

if __name__ == "__main__":
    # API keys are loaded from .env file automatically
    print("🔑 Loading API keys from .env file...")
    
    if not OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY not found in .env file!")
        print("💡 Add your OpenAI API key to the .env file")
        exit(1)
    
    if not TAVILY_API_KEY:
        print("❌ TAVILY_API_KEY not found in .env file!")
        print("💡 Add your Tavily API key to the .env file")
        exit(1)
    
    print("✅ API keys loaded successfully")
    
    # Run demonstrations
    demonstrate_memory_features()
    print("\n" + "=" * 60)
    test_memory_with_tools()
    print("\n" + "=" * 60)
    memory_troubleshooting_guide()
    
    # Start interactive session
    print("\n" + "=" * 60)
    agent = create_memory_agent()
    run_memory_chat_loop(agent)

# ============================================================================
# HOMEWORK ASSIGNMENT - PERSONAL ASSISTANT
# ============================================================================
"""
🏠 HOMEWORK: Build a Personal Assistant with Memory

Your task: Create a personal assistant that remembers user preferences.

Requirements:
1. Remember user's name and preferences
2. Track ongoing projects or goals
3. Provide personalized responses based on memory
4. Use tools when needed (search, calculate)

Example conversation flow:
User: "Hi, I'm Sarah. I'm working on learning machine learning."
Agent: "Nice to meet you, Sarah! Machine learning is exciting..."

User: "What's 2^10?"
Agent: "2^10 equals 1024. Is this for your machine learning studies?"

User: "How's my ML progress going?"
Agent: "Based on our conversation, you mentioned you're learning ML..."

Implementation hints:
1. Extend the AgentState to include user_profile
2. Create a node that updates user preferences
3. Use the memory to provide contextual responses

Bonus challenges:
- Add a "remind me" feature
- Track user's learning goals and progress
- Suggest relevant resources based on interests

Test your assistant with:
- Multi-turn conversations about preferences
- Switching topics and returning to previous ones
- Using tools within the context of remembered information

Next week: We'll add human-in-the-loop controls for approval workflows!
"""