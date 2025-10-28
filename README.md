# Streamlit Recipe Agent

This application is an interactive Recipe Agent built using Streamlit, LangChain, and LangGraph. It allows users to find recipes based on their queries, provides feedback mechanisms, and lets users save their favorite recipes.

## Features

*   **Conversational Recipe Search:** Enter your recipe query in natural language.
*   **Multi-turn Interaction:** The agent asks for clarification or feedback if the initial results aren't satisfactory.
*   **Key Feature Extraction:** Automatically extracts key details from retrieved recipes.
*   **Save Favorites:** Save recipes you like to a persistent list viewable in the sidebar.
*   **New Chat:** Easily clear the current conversation and start a fresh one.
*   **Powered by LangGraph:** Uses a state graph to manage the flow of conversation and recipe retrieval logic.

## Core Technologies

*   [Streamlit](https://streamlit.io/): For the interactive web UI.
*   [LangChain](https://python.langchain.com/): For orchestrating language model interactions, state management, and tool usage.
*   [LangGraph](https://python.langchain.com/docs/langgraph): For defining the agent's stateful, cyclical logic.
*   [OpenAI API](https://platform.openai.com/): For language understanding and generation.
*   [Tavily Search API](https://tavily.com/): For retrieving recipes from the web.

## Quick Start

### Prerequisites
- Python 3.10 or higher
- Make (comes pre-installed on macOS and most Linux distributions)

### Setup and Run

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/MorHananovitz/agent_recipe_streamlit_app.git
    cd agent_recipe_streamlit_app
    ```

2.  **Setup the environment and install dependencies:**
    ```bash
    make setup
    ```
    This will create a virtual environment and install all required dependencies.

3.  **Run the application:**
    ```bash
    make run
    ```
    This will start the Streamlit app and automatically open it in Chrome at `http://localhost:8501`.

## Makefile Commands

The project uses a Makefile for easy setup and management. Here are all available commands:

| Command | Description |
|---------|-------------|
| `make help` | Show all available commands |
| `make setup` | Complete setup: create environment and install dependencies |
| `make install` | Install all dependencies (requires venv to exist) |
| `make run` | Run the app and open Chrome browser |
| `make dev` | Run the app without opening browser |
| `make test-env` | Test if environment is properly set up |
| `make clean` | Remove virtual environment and cache files |
| `make reinstall` | Clean and reinstall everything |
| `make update` | Update all dependencies |
| `make info` | Show project information |

## API Keys Setup

The application requires two API keys to function:

1. **OpenAI API Key**: Get it from [OpenAI Platform](https://platform.openai.com/)
2. **Tavily API Key**: Get it from [Tavily](https://tavily.com/)

When you run the app, you'll be prompted to enter these keys in the sidebar. The keys are stored in your session and need to be re-entered each time you restart the app.

### Optional: Environment Variables

You can also create a `.env` file in the root directory to store your API keys:

```env
OPENAI_API_KEY="your_openai_api_key_here"
TAVILY_API_KEY="your_tavily_api_key_here"
```

## Usage

1. Enter your API keys in the sidebar
2. Type a recipe query in the search box (e.g., "vegetarian pasta with mushrooms")
3. Browse the retrieved recipes
4. Save your favorites using the ⭐ button
5. Provide feedback to refine results
6. Start a new chat with the 🔄 button

## Development

To run the app in development mode (without auto-opening the browser):
```bash
make dev
```

To update dependencies after modifying `requirements.txt`:
```bash
make update
```

To clean up and start fresh:
```bash
make clean
make setup
```

## Troubleshooting

### Virtual environment issues
```bash
make clean
make setup
```

### Dependencies not installing
Make sure you have Python 3.10+ installed:
```bash
python3 --version
```

### Port already in use
The app runs on port 8501 by default. If this port is busy, you can modify the `PORT` variable in the Makefile.

## Project Structure

```
agent_recipe_streamlit_app/
├── Makefile              # Build and run commands
├── README.md            # This file
├── Dockerfile           # Docker configuration (optional)
├── docker-compose.yml   # Docker Compose config (optional)
└── recipe_app/
    ├── __init__.py
    ├── app.py           # Main Streamlit application
    ├── requirements.txt # Python dependencies
    ├── config/
    │   └── config.py    # Configuration settings
    ├── models/
    │   └── recipe_models.py  # Data models
    ├── services/
    │   └── recipe_services.py  # Business logic
    └── ui/
        └── components.py  # UI components
```

## Contributing

Contributions are welcome! Please feel free to open an issue or submit a pull request.

## License

This project is licensed under the Apache 2.0 License - see the LICENSE file for details.
