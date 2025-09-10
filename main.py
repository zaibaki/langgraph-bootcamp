"""
LangGraph Bootcamp - Session 1: Basic Chatbot
==============================================

This is our starting point - a simple chatbot that can have conversations.
Think of this as building the "brain" of your agent before adding special skills.

Learning Goals:
- Understand StateGraph basics
- Create a working conversational agent
- Test the chat loop

Real-world analogy: We're building the basic conversation ability of a customer 
service representative before teaching them about products or policies.
"""

import os
from typing import Annotated, TypedDict
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from dotenv import load_dotenv
load_dotenv()  # Load environment variables from a .env file if present 

# ============================================================================
# STEP 1: ENVIRONMENT SETUP
# ============================================================================

# Set your OpenAI API key here (in production, use environment variables)
# Get your key from: https://platform.openai.com/api-keys

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Initialize the language model
# Think of this as hiring a "brain" for your agent
llm = ChatOpenAI(
    model="gpt-3.5-turbo",  # Cheaper and faster for learning
    temperature=0.7         # Makes responses more creative (0=robotic, 1=very creative)
)

# ============================================================================
# STEP 2: DEFINE THE AGENT'S "MEMORY" (STATE)
# ============================================================================

class AgentState(TypedDict):
    """
    This defines what our agent remembers during conversations.
    
    Think of this as the agent's notepad where it writes down:
    - All messages in the conversation
    - (Later we'll add more fields like user preferences, task status, etc.)
    
    The 'add_messages' function is special - it means "append new messages 
    to the list" instead of replacing the entire conversation.
    """
    messages: Annotated[list, add_messages]

# ============================================================================
# STEP 3: DEFINE WHAT THE AGENT CAN DO (NODES)
# ============================================================================

def chatbot_node(state: AgentState) -> dict:
    """
    The main "thinking" node of our agent.
    
    Real-world analogy: This is like the customer service rep listening to 
    the customer and formulating a response.
    
    Args:
        state: The current conversation state (all messages so far)
        
    Returns:
        dict: Contains the new message to add to the conversation
    """
    # Get all messages from the conversation history
    messages = state["messages"]
    
    # Ask the LLM to generate a response based on the conversation
    response = llm.invoke(messages)
    
    # Return the response in the format expected by our state
    # This will be added to the conversation history automatically
    return {"messages": [response]}

# ============================================================================
# STEP 4: BUILD THE AGENT'S "DECISION TREE" (GRAPH)
# ============================================================================

def create_basic_chatbot():
    """
    Creates our basic chatbot agent.
    
    Think of this as creating the workflow:
    START -> Listen to user -> Generate response -> END
    """
    # Create a new graph with our state definition
    graph_builder = StateGraph(AgentState)
    
    # Add the chatbot node (our main conversation skill)
    graph_builder.add_node("chatbot", chatbot_node)
    
    # Define the flow: START -> chatbot -> END
    graph_builder.add_edge(START, "chatbot")  # Always start with chatbot
    graph_builder.add_edge("chatbot", END)    # Always end after chatbot responds
    
    # Compile the graph into a runnable agent
    return graph_builder.compile()

# ============================================================================
# STEP 5: HELPER FUNCTIONS FOR TESTING
# ============================================================================

def chat_with_agent(agent, user_input: str):
    """
    Helper function to have a single conversation turn with the agent.
    
    Args:
        agent: The compiled LangGraph agent
        user_input: What the user wants to say
        
    Returns:
        str: The agent's response
    """
    # Format the user input as a message
    initial_state = {
        "messages": [{"role": "user", "content": user_input}]
    }
    
    # Run the agent and get the final state
    final_state = agent.invoke(initial_state)
    
    # Extract the last message (the agent's response)
    last_message = final_state["messages"][-1]
    return last_message.content

def run_chat_loop(agent):
    """
    Interactive chat loop for testing your agent.
    
    Type 'quit' to exit.
    """
    print("🤖 Basic Chatbot started! Type 'quit' to exit.")
    print("=" * 50)
    
    while True:
        # Get user input
        user_input = input("\n👤 You: ").strip()
        
        # Check for exit conditions
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
            
        if not user_input:
            print("Please enter a message.")
            continue
        
        try:
            # Get agent response
            response = chat_with_agent(agent, user_input)
            print(f"\n🤖 Agent: {response}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            print("💡 Make sure your API key is set correctly!")

# ============================================================================
# STEP 6: TESTING AND DEMO
# ============================================================================

def test_basic_functionality():
    """
    Test the basic chatbot with a few example conversations.
    """
    print("🧪 Testing Basic Chatbot Functionality")
    print("=" * 40)
    
    # Create the agent
    agent = create_basic_chatbot()
    
    # Test conversations
    test_cases = [
        "Hello! What can you help me with?",
        "What's the weather like today?",
        "Can you tell me a joke?",
        "Explain quantum physics in simple terms."
    ]
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_input}")
        try:
            response = chat_with_agent(agent, test_input)
            print(f"✅ Response: {response[:100]}{'...' if len(response) > 100 else ''}")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Check if API key is set
    if os.environ.get("OPENAI_API_KEY") == "your-api-key-here":
        print("⚠️  Please set your OpenAI API key in the code!")
        print("Get one from: https://platform.openai.com/api-keys")
        exit(1)
    
    # Run tests first
    test_basic_functionality()
    
    # Then start interactive chat
    print("\n" + "=" * 50)
    agent = create_basic_chatbot()
    run_chat_loop(agent)

# ============================================================================
# TROUBLESHOOTING GUIDE
# ============================================================================
"""
Common Issues and Solutions:

1. "AuthenticationError: Invalid API key"
   - Make sure you set your OpenAI API key correctly
   - Check that your API key is active and has credits

2. "ImportError: No module named 'langgraph'"
   - Run: pip install langgraph langchain-openai

3. Agent gives weird responses:
   - This is normal! LLMs can be unpredictable
   - Try adjusting the temperature (0-1) in ChatOpenAI

4. Slow responses:
   - Normal for API calls
   - Consider using gpt-3.5-turbo instead of gpt-4 for faster responses

Next Steps:
- Try different conversation topics
- Experiment with different temperature values
- Notice how each conversation is independent (no memory yet)
- Ready for Session 2: Adding tools!
"""