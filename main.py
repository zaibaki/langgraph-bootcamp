"""
LangGraph Bootcamp - Session 2: Adding Tools to Your Agent
=========================================================

Building on Session 1, we're adding "superpowers" to our chatbot.
Now it can search the web for current information!

Learning Goals:
- Understand tool integration
- Implement conditional routing (when to use tools vs. just chat)
- Handle tool responses

Real-world analogy: We're upgrading our customer service rep from someone who 
can only answer from memory to someone who can also look things up in real-time.
"""

import os
from typing import Annotated, TypedDict
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# STEP 1: ENVIRONMENT SETUP
# ============================================================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Get from: https://platform.openai.com/account/api-keys
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")  # Get from: https://tavily.com

# Initialize the language model
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.7
)

# ============================================================================
# STEP 2: DEFINE TOOLS (THE AGENT'S SUPERPOWERS)
# ============================================================================

def setup_tools():
    """
    Define what tools our agent can use.
    
    Think of this as giving your agent access to:
    - Web search (like having Google)
    - Calculator (we'll add this as homework)
    - Any other external capability
    """
    # Web search tool - lets the agent look up current information
    search_tool = TavilySearch(
        max_results=3  # Don't overwhelm with too many results
    )
    
    return [search_tool]

# ============================================================================
# STEP 3: STATE DEFINITION (SAME AS SESSION 1)
# ============================================================================

class AgentState(TypedDict):
    """
    Our agent's memory - same as Session 1.
    The messages list will now include:
    - User messages
    - Assistant messages  
    - Tool call messages
    - Tool response messages
    """
    messages: Annotated[list, add_messages]

# ============================================================================
# STEP 4: ENHANCED CHATBOT NODE (NOW WITH TOOLS!)
# ============================================================================

def chatbot_node(state: AgentState) -> dict:
    """
    Enhanced chatbot that can decide whether to use tools or just respond.
    
    The LLM will now:
    1. Look at the conversation
    2. Decide if it needs to use a tool
    3. Either make a tool call OR respond directly
    
    Real-world analogy: Customer service rep deciding whether to look something 
    up in the system or answer from their knowledge.
    """
    messages = state["messages"]
    
    # The LLM bound with tools can now make tool calls
    response = llm_with_tools.invoke(messages)
    
    return {"messages": [response]}

def should_continue(state: AgentState) -> str:
    """
    Decision function: Does the agent want to use a tool or is it done?
    
    This is called after the chatbot_node to decide what happens next.
    
    Returns:
        "tools" if the agent wants to use a tool
        "end" if the agent is ready to respond to the user
    """
    messages = state["messages"]
    last_message = messages[-1]
    
    # If the last message contains tool calls, route to tools
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    
    # Otherwise, we're done for this turn
    return "end"

# ============================================================================
# STEP 5: BUILD THE ENHANCED AGENT
# ============================================================================

def create_agent_with_tools():
    """
    Creates an agent that can chat AND use tools.
    
    The workflow now looks like:
    START -> chatbot -> decision -> [tools -> chatbot] OR [end]
    
    The agent can loop between chatbot and tools multiple times if needed!
    """
    # Set up tools
    tools = setup_tools()
    
    # Create LLM that knows about tools
    global llm_with_tools
    llm_with_tools = llm.bind_tools(tools)
    
    # Build the graph
    graph_builder = StateGraph(AgentState)
    
    # Add our nodes
    graph_builder.add_node("chatbot", chatbot_node)
    graph_builder.add_node("tools", ToolNode(tools))  # Pre-built tool executor
    
    # Define the flow
    graph_builder.add_edge(START, "chatbot")
    
    # Conditional routing after chatbot
    graph_builder.add_conditional_edges(
        "chatbot",           # From this node
        should_continue,     # Use this function to decide
        {
            "tools": "tools", # If returns "tools", go to tools node
            "end": END        # If returns "end", finish
        }
    )
    
    # After using tools, always go back to chatbot to process results
    graph_builder.add_edge("tools", "chatbot")
    
    return graph_builder.compile()

# ============================================================================
# STEP 6: ENHANCED TESTING FUNCTIONS
# ============================================================================

def chat_with_agent(agent, user_input: str) -> str:
    """
    Have a conversation turn with the tool-enabled agent.
    
    Now the agent might:
    1. Search for information
    2. Process the search results  
    3. Give you a comprehensive answer
    """
    initial_state = {
        "messages": [{"role": "user", "content": user_input}]
    }
    
    # Run the agent - it might loop through multiple nodes
    final_state = agent.invoke(initial_state)
    
    # Get the final response
    last_message = final_state["messages"][-1]
    return last_message.content

def run_enhanced_chat_loop(agent):
    """
    Interactive chat loop that shows when tools are being used.
    """
    print("🔧 Enhanced Chatbot with Tools started!")
    print("Try asking about current events, recent news, or specific information.")
    print("Type 'quit' to exit.")
    print("=" * 60)
    
    while True:
        user_input = input("\n👤 You: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
            
        if not user_input:
            continue
        
        try:
            print("🤖 Agent: Thinking...")
            response = chat_with_agent(agent, user_input)
            print(f"🤖 Agent: {response}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            if "tavily" in str(e).lower():
                print("💡 Make sure your Tavily API key is set correctly!")
            else:
                print("💡 Check your OpenAI API key and internet connection.")

# ============================================================================
# STEP 7: COMPREHENSIVE TESTING
# ============================================================================

def test_tool_functionality():
    """
    Test both regular chat and tool usage.
    """
    print("🧪 Testing Enhanced Agent with Tools")
    print("=" * 40)
    
    agent = create_agent_with_tools()
    
    # Test cases that should trigger different behaviors
    test_cases = [
        # Should use tools (current/recent information)
        ("Current events", "What's happening in the news today?"),
        ("Recent information", "What's the latest development in AI?"),
        ("Specific lookup", "What's the current weather in New York?"),
        
        # Should NOT use tools (general knowledge)
        ("General question", "What is the capital of France?"),
        ("Math question", "What's 15 + 27?"),
        ("Creative task", "Write a short poem about cats."),
    ]
    
    for category, test_input in test_cases:
        print(f"\n📝 {category}: {test_input}")
        try:
            response = chat_with_agent(agent, test_input)
            print(f"✅ Response: {response[:150]}{'...' if len(response) > 150 else ''}")
        except Exception as e:
            print(f"❌ Error: {e}")

def demonstrate_tool_flow():
    """
    Show the step-by-step process of how tools work.
    """
    print("\n🔍 Tool Flow Demonstration")
    print("=" * 30)
    
    agent = create_agent_with_tools()
    
    # Let's trace through what happens with a tool-requiring question
    question = "What are the latest developments in AI in 2024?"
    print(f"Question: {question}")
    
    initial_state = {"messages": [{"role": "user", "content": question}]}
    
    print("\n📊 Step-by-step execution:")
    print("1. User asks question")
    print("2. Chatbot analyzes and decides to search")
    print("3. Search tool finds current information")
    print("4. Chatbot processes search results")
    print("5. Chatbot provides comprehensive answer")
    
    try:
        final_state = agent.invoke(initial_state)
        response = final_state["messages"][-1].content
        print(f"\n✅ Final answer: {response[:200]}...")
    except Exception as e:
        print(f"❌ Error in demonstration: {e}")

# ============================================================================
# STEP 8: HOMEWORK HELPER - CALCULATOR TOOL EXAMPLE
# ============================================================================

def create_calculator_tool():
    """
    Example of how to create a simple calculator tool for homework.
    
    This shows you how to add more tools to your agent!
    """
    from langchain_core.tools import tool
    
    @tool
    def calculator(expression: str) -> str:
        """
        Calculate mathematical expressions safely.
        Use this for any math problems or calculations.
        
        Args:
            expression: A mathematical expression like "15 + 27" or "10 * 5"
        """
        try:
            # Safe evaluation of mathematical expressions
            import ast
            import operator
            
            # Supported operations
            ops = {
                ast.Add: operator.add,
                ast.Sub: operator.sub,
                ast.Mult: operator.mul,
                ast.Div: operator.truediv,
                ast.Pow: operator.pow,
                ast.USub: operator.neg,
            }
            
            def eval_expr(node):
                if isinstance(node, ast.Num):
                    return node.n
                elif isinstance(node, ast.BinOp):
                    return ops[type(node.op)](eval_expr(node.left), eval_expr(node.right))
                elif isinstance(node, ast.UnaryOp):
                    return ops[type(node.op)](eval_expr(node.operand))
                else:
                    raise TypeError(f"Unsupported operation: {node}")
            
            result = eval_expr(ast.parse(expression, mode='eval').body)
            return f"The result of {expression} is {result}"
            
        except Exception as e:
            return f"Sorry, I couldn't calculate '{expression}'. Please check the format. Error: {e}"
    
    return calculator

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
    test_tool_functionality()
    demonstrate_tool_flow()
    
    # Start interactive chat
    print("\n" + "=" * 60)
    agent = create_agent_with_tools()
    run_enhanced_chat_loop(agent)

# ============================================================================
# HOMEWORK ASSIGNMENT
# ============================================================================
"""
🏠 HOMEWORK: Add Calculator Tool

Your task:
1. Uncomment and integrate the calculator tool created above
2. Test that your agent can:
   - Answer "What's 15 + 27?" using the calculator
   - Search for "latest AI news" using web search
   - Chat normally for general questions

Steps:
1. Add the calculator tool to the setup_tools() function
2. Test with mathematical questions
3. Verify it works alongside web search

Bonus challenges:
- Add a tool that gets random jokes from an API
- Create a tool that converts currencies
- Add a tool that gets weather information

Common issues:
- Make sure both API keys are set
- Tools should have clear descriptions for the LLM
- Test each tool individually before combining

Next session: We'll add memory so the agent remembers conversations!
"""