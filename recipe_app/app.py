import streamlit as st
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage

from recipe_app.config.config import PAGE_TITLE, PAGE_ICON
from recipe_app.models.recipe_models import RecipeState
from recipe_app.services.recipe_services import (
    QueryTranslator, 
    RecipeRetriever, 
    RecipeKeyFeatures, 
    HumanFeedback,
    Satisfaction
)
from recipe_app.ui.components import (
    display_recipe_card,
    display_recipe_features,
    get_user_feedback,
    display_error,
    display_success
)

def initialize_graph():
    """Initialize the recipe processing graph."""
    builder = StateGraph(RecipeState)

    # Add nodes
    builder.add_node("translate_query", QueryTranslator.translate)
    builder.add_node("retrieve_recipes", RecipeRetriever.retrieve)
    builder.add_node("extract_key_features", RecipeKeyFeatures.extract)
    builder.add_node("human_feedback", HumanFeedback.refine)

    # Add edges
    builder.add_edge(START, "translate_query")
    builder.add_edge("translate_query", "retrieve_recipes")
    builder.add_edge("retrieve_recipes", "extract_key_features")
    builder.add_edge("extract_key_features", "human_feedback")

    # Add conditional edges for feedback loop
    builder.add_conditional_edges(
        "human_feedback",
        Satisfaction.recipe_satisfaction,
        {
            "translate_query": "translate_query",
            END: END
        }
    )

    return builder.compile()

def reset_chat():
    """Reset the chat state."""
    if "graph" in st.session_state:
        del st.session_state.graph
    if "memory" in st.session_state:
        del st.session_state.memory
    if "current_recipe" in st.session_state:
        del st.session_state.current_recipe

def save_to_favorites(recipe: dict):
    """Save a recipe to favorites."""
    if "favorites" not in st.session_state:
        st.session_state.favorites = []
    
    # Check if recipe is already in favorites
    if recipe not in st.session_state.favorites:
        st.session_state.favorites.append(recipe)
        display_success("Recipe saved to favorites!")
    else:
        st.warning("This recipe is already in your favorites!")

def display_favorites():
    """Display the favorites section."""
    if "favorites" in st.session_state and st.session_state.favorites:
        st.sidebar.header("📚 Favorite Recipes")
        for i, recipe in enumerate(st.session_state.favorites):
            with st.sidebar.expander(f"⭐ {recipe['name']}", expanded=False):
                display_recipe_card(recipe)
                if st.button("Remove from Favorites", key=f"remove_{i}"):
                    st.session_state.favorites.remove(recipe)
                    st.rerun()
    else:
        st.sidebar.info("No favorite recipes yet!")

def main():
    """Main Streamlit application."""
    st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout="wide")
    st.title(f"{PAGE_ICON} {PAGE_TITLE}")

    # API Keys input section
    with st.sidebar:
        st.header("🔑 API Configuration")
        openai_api_key = st.text_input("OpenAI API Key", type="password", key="openai_api_key")
        tavily_api_key = st.text_input("Tavily API Key", type="password", key="tavily_api_key")
        
        if not openai_api_key or not tavily_api_key:
            st.warning("Please enter your API keys to use the application.")
            st.stop()
        
        # Set the API keys in environment
        import os
        os.environ["OPENAI_API_KEY"] = openai_api_key
        os.environ["TAVILY_API_KEY"] = tavily_api_key

    # Display favorites in sidebar
    display_favorites()

    # Create two columns for the main layout
    left_col, right_col = st.columns([2, 1])

    with left_col:
        # New Chat button and search input row
        col1, col2 = st.columns([6, 1])
        with col2:
            if st.button("🔄 New Chat"):
                reset_chat()
                st.rerun()

        # Initialize session state
        if "graph" not in st.session_state:
            st.session_state.graph = initialize_graph()
            st.session_state.memory = MemorySaver()

        # User input
        with col1:
            user_input = st.text_input("What recipe would you like to find?")

        if user_input:
            try:
                input_message = HumanMessage(content=user_input)
                
                with st.spinner("Searching for recipes..."):
                    output = st.session_state.graph.invoke(
                        {"messages": [input_message]},
                        {"configurable": {"thread_id": "1"}}
                    )

                # Display results
                if output and 'recipes' in output:
                    st.subheader("Found Recipes")
                    
                    # Display recipe features
                    if 'key_features' in output:
                        display_recipe_features(output['key_features'])

                    # Display recipes
                    for i, recipe in enumerate(output['recipes']):
                        with st.expander(f"Recipe {i+1}: {recipe['name']}"):
                            display_recipe_card(recipe)
                            # Add save to favorites button
                            if st.button("⭐ Save to Favorites", key=f"save_{i}"):
                                save_to_favorites(recipe)

                    # Get user feedback
                    feedback = get_user_feedback()
                    if feedback:
                        with st.spinner("Processing your feedback..."):
                            # Create new state with feedback
                            feedback_state = output.copy()
                            feedback_state["feedback"] = feedback
                            
                            # Process feedback
                            output = st.session_state.graph.invoke(
                                feedback_state,
                                {"configurable": {"thread_id": "1"}}
                            )
                            
                            if output.get('recipes_index', -1) != -1:
                                selected_recipe = output['recipes'][output['recipes_index']]
                                st.session_state.current_recipe = selected_recipe
                                st.session_state.has_final_recipe = True

            except Exception as e:
                display_error(str(e))

    # Right column for final selected recipe
    with right_col:
        if "has_final_recipe" in st.session_state and st.session_state.has_final_recipe:
            st.markdown("### 🌟 Your Selected Recipe")
            st.markdown("---")
            display_recipe_card(st.session_state.current_recipe)
            # Add save to favorites button for selected recipe
            if st.button("⭐ Save to Favorites", key="save_selected"):
                save_to_favorites(st.session_state.current_recipe)
        else:
            st.info("Select a recipe from the search results to see it here!")

if __name__ == "__main__":
    main() 