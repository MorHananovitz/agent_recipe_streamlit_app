import streamlit as st
from typing import Dict, List

def apply_custom_css():
    """Apply custom CSS styling with the specified color palette."""
    st.markdown("""
        <style>
        /* Color palette:
           #BAA5FF - Light Purple
           #DBFE87 - Light Green/Yellow
           #E6A2D0 - Light Pink
           #60C7B8 - Teal
           #5339EA - Deep Purple
        */
        
        /* Main container styling */
        .main {
            background-color: #FFFFFF;
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            background-color: #BAA5FF;
            border-radius: 8px;
            border: 2px solid #5339EA;
        }
        
        /* Button styling */
        .stButton>button {
            background-color: #5339EA;
            color: white;
            border-radius: 8px;
            border: none;
            padding: 0.5rem 1rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .stButton>button:hover {
            background-color: #60C7B8;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        
        /* Text input styling */
        .stTextInput>div>div>input {
            border: 2px solid #BAA5FF;
            border-radius: 8px;
        }
        
        .stTextInput>div>div>input:focus {
            border-color: #5339EA;
            box-shadow: 0 0 0 2px rgba(83, 57, 234, 0.1);
        }
        
        /* Success message styling */
        .stSuccess {
            background-color: #DBFE87;
            border-left: 4px solid #60C7B8;
        }
        
        /* Info message styling */
        .stInfo {
            background-color: #E6A2D0;
            border-left: 4px solid #5339EA;
        }
        
        /* Header styling */
        h1, h2, h3 {
            color: #5339EA;
        }
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: #BAA5FF;
        }
        
        /* Expander content background */
        .streamlit-expanderContent {
            background-color: #F8F7FF;
            border: 1px solid #BAA5FF;
        }
        
        /* Link styling */
        a {
            color: #5339EA;
            text-decoration: none;
        }
        
        a:hover {
            color: #60C7B8;
            text-decoration: underline;
        }
        
        /* Markdown styling for recipe cards */
        .recipe-card {
            background: linear-gradient(135deg, #E6A2D0 0%, #BAA5FF 100%);
            padding: 1rem;
            border-radius: 12px;
            margin: 1rem 0;
        }
        
        /* Accent elements */
        .stMarkdown {
            color: #262730;
        }
        
        /* Warning styling */
        .stWarning {
            background-color: #DBFE87;
            border-left: 4px solid #5339EA;
        }
        </style>
    """, unsafe_allow_html=True)

def display_recipe_card(recipe: Dict):
    """Display a recipe card with title, ingredients, and instructions."""
    st.markdown(f"## {recipe['name']}")
    st.markdown(f"[View Original Recipe]({recipe['url']})")
    st.markdown("### Recipe Details")
    st.markdown(recipe['content'])

def display_recipe_features(features: List[Dict]):
    """Display extracted recipe features."""
    st.markdown("### 📋 Recipe Overview")
    for i, feature in enumerate(features, 1):
        with st.expander(f"Recipe {i}: {feature.dish_name}", expanded=True):
            st.markdown("#### 🥘 Key Ingredients")
            for ingredient in feature.key_ingredients:
                st.markdown(f"- {ingredient}")
            if feature.cooking_style:
                st.markdown(f"#### 👨‍🍳 Cooking Style: {feature.cooking_style}")

def get_user_feedback() -> str:
    """Get user feedback through a text input."""
    import streamlit as st
    
    # Get chat counter for resetting input
    chat_counter = st.session_state.get("chat_counter", 0)
    
    st.markdown("### 💬 Do you like any of these suggestions or should I make any changes?")
    return st.text_area(
        "Your feedback",
        placeholder="e.g., 'I like option 2' or 'I want something vegetarian and healthier'",
        height=100,
        key=f"feedback_input_{chat_counter}",
        label_visibility="collapsed"
    )

def display_error(error: str):
    """Display error message."""
    st.error(f"An error occurred: {error}")

def display_success(message: str):
    """Display success message."""
    st.success(message) 