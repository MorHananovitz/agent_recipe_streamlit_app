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
    apply_custom_css,
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

    # Compile with memory checkpointer
    memory = MemorySaver()
    return builder.compile(checkpointer=memory)

def reset_chat():
    """Reset the chat state."""
    if "graph" in st.session_state:
        del st.session_state.graph
    if "current_output" in st.session_state:
        del st.session_state.current_output
    if "current_recipe" in st.session_state:
        del st.session_state.current_recipe
    if "current_feature" in st.session_state:
        del st.session_state.current_feature
    if "has_final_recipe" in st.session_state:
        del st.session_state.has_final_recipe
    if "new_search" in st.session_state:
        del st.session_state.new_search
    if "user_input" in st.session_state:
        del st.session_state.user_input
    if "feedback_input" in st.session_state:
        del st.session_state.feedback_input
    # Increment chat counter to reset text input
    if "chat_counter" not in st.session_state:
        st.session_state.chat_counter = 0
    st.session_state.chat_counter += 1

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
    
    # Apply custom CSS styling
    apply_custom_css()
    
    # Create header with aligned New Chat button
    header_col1, header_col2 = st.columns([4, 1])
    with header_col1:
        st.title(f"{PAGE_ICON} {PAGE_TITLE}")
    with header_col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Add spacing to align with title
        if st.button("🔄 New Chat", key="header_new_chat"):
            reset_chat()
            st.rerun()

    # API Keys input section
    with st.sidebar:
        st.header("🔑 API Configuration")
        openai_api_key = st.text_input("OpenAI API Key", type="password", key="openai_api_key")
        tavily_api_key = st.text_input("Tavily API Key", type="password", key="tavily_api_key")
        
        if not openai_api_key or not tavily_api_key:
            st.markdown('<p style="color: black;">Please enter your API keys to use the application.</p>', unsafe_allow_html=True)
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
        # Initialize session state
        if "graph" not in st.session_state:
            st.session_state.graph = initialize_graph()
        
        # Initialize chat counter if not exists
        if "chat_counter" not in st.session_state:
            st.session_state.chat_counter = 0

        # User input with key that changes on reset and enter icon
        user_input = st.text_input(
            "What recipe would you like to find? ⏎",
            key=f"user_input_{st.session_state.chat_counter}",
            placeholder="e.g., 'I have eggs, flour, tomatoes and cheese'"
        )

        if user_input:
            try:
                # Store current output in session state
                if 'current_output' not in st.session_state or st.session_state.get('new_search'):
                    input_message = HumanMessage(content=user_input)
                    
                    with st.spinner("Searching for recipes..."):
                        output = st.session_state.graph.invoke(
                            {"messages": [input_message]},
                            {"configurable": {"thread_id": "1"}}
                        )
                        st.session_state.current_output = output
                        st.session_state.new_search = False

                output = st.session_state.current_output

                # Check if a recipe has been selected
                if "has_final_recipe" in st.session_state and st.session_state.has_final_recipe:
                    # Display selected recipe in main column
                    st.markdown("### 🌟 Your Selected Recipe")
                    st.markdown("---")
                    
                    # Display the key features first
                    if "current_feature" in st.session_state:
                        feature = st.session_state.current_feature
                        st.markdown(f"## {feature.dish_name}")
                        st.markdown("#### 🥘 Key Ingredients")
                        for ingredient in feature.key_ingredients:
                            st.markdown(f"- {ingredient}")
                        if feature.cooking_style:
                            st.markdown(f"#### 👨‍🍳 Cooking Style: {feature.cooking_style}")
                        st.markdown("---")
                    
                    # Display full recipe details
                    display_recipe_card(st.session_state.current_recipe)
                    
                    # Add save to favorites button for selected recipe
                    if st.button("⭐ Save to Favorites", key="save_selected_main"):
                        save_to_favorites(st.session_state.current_recipe)
                
                # Display results - ONLY key ingredients initially (if no recipe selected)
                elif output and 'key_features' in output and len(output['key_features']) > 0:
                    st.subheader("🍳 Recipe Suggestions")
                    
                    # Display ONLY the key ingredients for each recipe
                    display_recipe_features(output['key_features'])
                    
                    st.markdown("---")
                    
                    # Get user feedback
                    feedback = get_user_feedback()
                    
                    # Add a submit button for feedback
                    submit_feedback = st.button("Submit Feedback", type="primary")
                    
                    if submit_feedback and feedback:
                        with st.spinner("Processing your feedback..."):
                            from recipe_app.services.recipe_services import HumanFeedback
                            from langchain_openai import ChatOpenAI
                            from langchain.schema import SystemMessage
                            from recipe_app.models.recipe_models import HumanSelection
                            from recipe_app.config.config import MODEL_NAME, TEMPERATURE
                            
                            # Process feedback directly
                            llm = ChatOpenAI(model=MODEL_NAME, temperature=TEMPERATURE)
                            system_message = SystemMessage(content=f"""
                            Process the user feedback on the suggested recipes:
                            Current recipes: {output.get('key_features', [])}
                            User feedback: {feedback}

                            Instructions:
                            1. If the user expresses satisfaction with any recipe, return its index (0, 1, or 2).
                            2. If the user wants modifications or different recipes, explain why in the dislike field.
                            3. Be strict about recipe selection - only set 'like' if there's clear positive feedback.
                            """)

                            structured_llm = llm.with_structured_output(HumanSelection)
                            classification = structured_llm.invoke([system_message])
                            
                            # Check if user selected a recipe
                            if classification.like is not None:
                                selected_index = classification.like
                                selected_recipe = output['recipes'][selected_index]
                                selected_feature = output['key_features'][selected_index]
                                st.session_state.current_recipe = selected_recipe
                                st.session_state.current_feature = selected_feature
                                st.session_state.has_final_recipe = True
                                # Clear the current output
                                st.session_state.current_output = None
                                st.success(f"Great! You selected: {selected_feature.dish_name}")
                                st.rerun()
                            else:
                                # User wants different recipes - create new query from dislike reason
                                st.info(f"Searching for: {classification.dislike}")
                                # Create a new input message with the refined request
                                input_message = HumanMessage(content=classification.dislike)
                                
                                with st.spinner("Searching for better recipes..."):
                                    output = st.session_state.graph.invoke(
                                        {"messages": [input_message]},
                                        {"configurable": {"thread_id": "1"}}
                                    )
                                    st.session_state.current_output = output
                                    st.session_state.new_search = False
                                    st.rerun()

            except Exception as e:
                display_error(str(e))

    # Right column for tips and info
    with right_col:
        st.markdown("### 💡 How to Use")
        st.markdown("""
        1. **Enter your ingredients** or recipe request
        2. **Review suggestions** - I'll show 3 recipe options with key ingredients
        3. **Provide feedback**:
           - Say "I like option 1" to select a recipe
           - Or request changes like "I want something vegetarian"
        4. **View full recipe** - Selected recipe appears with complete details
        5. **Save favorites** - Click ⭐ to save recipes for later
        """)
        
        st.markdown("---")
        st.markdown("### 🎯 Example Queries")
        st.markdown("""
        - "I have eggs, flour, tomatoes and cheese"
        - "Quick pasta dinner for 4 people"
        - "Vegetarian lunch ideas"
        - "Healthy breakfast with oats"
        """)

if __name__ == "__main__":
    main() 