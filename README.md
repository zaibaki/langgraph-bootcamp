# LangGraph AI Agents Bootcamp

A comprehensive 3-week hands-on bootcamp for building production-ready AI agents using LangGraph. Designed for developers with basic Python knowledge who want to create intelligent, stateful agents that can use tools, maintain memory, and handle complex workflows.

## Overview

This bootcamp takes you from building basic chatbots to deploying production-ready AI agents with FastAPI backends. By the end, you'll have built multiple working agents and understand how to create reliable, scalable AI systems.

### What You'll Build

- **Week 1**: Conversational agents with web search and memory
- **Week 2**: Reliable agents with human oversight and error handling  
- **Week 3**: Production-deployed agents with FastAPI and monitoring

### Key Features

- **Multi-model support**: Choose between OpenAI (GPT) or Google Gemini models
- **Progressive learning**: Each session builds on the previous one
- **Real-world focus**: Projects that solve actual problems
- **Production-ready**: Learn deployment, monitoring, and best practices

## Quick Start

### Prerequisites

- Python 3.9+ (3.10+ recommended)
- Basic Python knowledge (functions, classes, imports)
- Text editor or IDE (VS Code recommended)
- Internet connection for API calls

### 1. Clone and Setup

```bash
git clone <repository-url>
cd langgraph-bootcamp
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Get API Keys

**Choose your language model:**

**Option A: Google Gemini (FREE tier)**
1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Sign in with Google account
3. Create API key
4. Copy key (starts with "AIza...")

**Option B: OpenAI (requires payment)**
1. Visit [OpenAI Platform](https://platform.openai.com)
2. Create account and add payment method
3. Generate API key
4. Copy key (starts with "sk-...")

**Required for web search:**
1. Visit [Tavily](https://tavily.com)
2. Sign up for free account
3. Get API key from dashboard

### 3. Configure Environment

Create `.env` file in project root:

```bash
# Language model (choose one or both)
GOOGLE_API_KEY=your_google_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Web search (required)
TAVILY_API_KEY=your_tavily_api_key_here
```

### 4. Test Setup

```bash
python test_setup.py
```

If all tests pass, you're ready to start!

## Curriculum Structure

### Week 1: Foundation
**Build your first intelligent agent**

- **Session 1**: Basic chatbot with StateGraph fundamentals
- **Session 2**: Adding tools (web search, calculator)
- **Session 3**: Memory and conversation persistence

**Outcome**: Conversational agent that remembers context and can search the web

### Week 2: Intermediate Features  
**Make agents reliable and interactive**

- **Session 4**: Human-in-the-loop workflows and approvals
- **Session 5**: Custom state management for complex workflows
- **Session 6**: Error handling and robust agent design

**Outcome**: Reliable agent with human oversight and error recovery

### Week 3: Production Deployment
**Deploy real-world agents**

- **Session 7**: Time travel debugging and state inspection
- **Session 8**: FastAPI backend integration and REST APIs
- **Session 9**: Production monitoring and deployment strategies

**Outcome**: Production-deployed agent accessible via web API

## Project Structure

```
langgraph-bootcamp/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── test_setup.py            # Setup verification
├── .env                     # API keys (create this)
├── .gitignore              # Git ignore rules
├── week1/                  # Foundation sessions
│   ├── session1_basic.py
│   ├── session2_tools.py
│   └── session3_memory.py
├── week2/                  # Intermediate sessions
│   ├── session4_hitl.py
│   ├── session5_state.py
│   └── session6_errors.py
├── week3/                  # Production sessions
│   ├── session7_debug.py
│   ├── session8_fastapi.py
│   └── session9_production.py
└── projects/               # Your implementations
    ├── homework/
    └── final_project/
```

## Language Model Comparison

| Feature | Google Gemini | OpenAI |
|---------|---------------|---------|
| **Cost** | FREE tier | Requires payment |
| **Setup** | No credit card needed | Credit card required |
| **Rate Limits** | Generous free limits | Depends on plan |
| **Multimodal** | Images, audio, video | Images only |
| **Documentation** | Good | Extensive |
| **Community** | Growing | Large |

**Recommendation**: Start with Gemini for free learning, switch to OpenAI for production if preferred.

## Session Format

Each session follows this structure:

1. **Concept Introduction** (15-20 min): Core concepts with real-world analogies
2. **Live Coding** (60-75 min): Build working examples step-by-step  
3. **Testing & Debugging** (10-15 min): Common issues and solutions
4. **Homework Assignment**: Reinforcement project

## Running the Code

### Individual Sessions
```bash
# Run specific session
python week1/session1_basic.py

# Run with model preference
python week1/session1_basic.py --model gemini
python week1/session1_basic.py --model openai
```

### Interactive Development
```bash
# Start Jupyter for experimentation
jupyter notebook

# Or use Jupyter Lab
jupyter lab
```

## Troubleshooting

### Common Issues

**"No module named 'langgraph'"**
```bash
pip install --upgrade langgraph
```

**API Key Errors**
- Double-check keys are copied correctly (no extra spaces)
- Verify OpenAI account has billing set up
- Check Gemini key at [AI Studio](https://aistudio.google.com/)

**Tool Calling Issues**
- Ensure you're using compatible models (gpt-3.5-turbo+, gemini-1.5+)
- Check that tools are properly bound to the model

**Memory/Checkpointing Problems**
- Verify thread_id consistency across calls
- For production, use PostgresSaver instead of MemorySaver

### Getting Help

1. Check the troubleshooting section in each session file
2. Review session recordings (if available)
3. Ask in community Discord/Slack
4. Open GitHub issue with error details

## Best Practices

### Development
- Use virtual environments
- Keep API keys in environment variables
- Test with small examples before scaling
- Use descriptive thread_ids for debugging

### Production
- Implement proper error handling
- Monitor agent performance and costs
- Use database checkpointers for persistence
- Set up proper logging and observability

## Advanced Topics

After completing the bootcamp, explore:

- **Multi-agent systems**: Coordinating multiple specialized agents
- **Advanced routing**: Complex conditional logic and dynamic workflows
- **Custom tools**: Building domain-specific capabilities
- **Performance optimization**: Caching, parallel execution, streaming
- **Enterprise integration**: Authentication, monitoring, compliance

## Contributing

Found a bug or want to improve the curriculum?

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Resources

### Documentation
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [OpenAI API Docs](https://platform.openai.com/docs)
- [Google AI API Docs](https://ai.google.dev/docs)

### Community
- [LangChain Discord](https://discord.gg/langchain)
- [GitHub Discussions](https://github.com/langchain-ai/langgraph/discussions)

### Learning Path
- Complete this bootcamp
- Build a personal project
- Join the LangChain community
- Explore advanced LangGraph patterns

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built on [LangGraph](https://github.com/langchain-ai/langgraph) by LangChain
- Inspired by real-world AI agent development challenges
- Designed for practical, hands-on learning

---

**Ready to build AI agents?** Start with `python test_setup.py` and then dive into Week 1, Session 1!