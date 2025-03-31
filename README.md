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

## Setup

1.  **Clone the repository (if you haven't already):**
    ```bash
    git clone https://github.com/MorHananovitz/agent_recipe_streamlit_app.git
    cd agent_recipe_streamlit_app
    ```

2.  **Install Dependencies:** This project uses Poetry.
    ```bash
    # Install poetry if you don't have it (https://python-poetry.org/docs/#installation)
    poetry install
    ```
    Alternatively, if not using Poetry, create a virtual environment and install from a `requirements.txt` if available (you might need to generate one from `pyproject.toml`).

3.  **Set up Environment Variables:** Create a `.env` file in the root directory (`streamlit_agent_app`) and add your API keys:
    ```env
    OPENAI_API_KEY="your_openai_api_key_here"
    TAVILY_API_KEY="your_tavily_api_key_here"
    # LANGCHAIN_API_KEY="your_langsmith_api_key_here" # Optional, for LangSmith tracing
    ```

## Running the Application

1.  **Activate your virtual environment (if using one):**
    ```bash
    # If using Poetry
    poetry shell

    # If using venv
    # source venv/bin/activate
    ```

2.  **Run the Streamlit app:** Make sure you are in the `streamlit_agent_app` directory.
    ```bash
    streamlit run recipe_app/app.py
    ```

3.  Open your web browser and navigate to the local URL provided (usually `http://localhost:8501`).

## Contributing

Contributions are welcome! Please feel free to open an issue or submit a pull request.
