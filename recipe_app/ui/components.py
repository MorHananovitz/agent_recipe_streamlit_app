import streamlit as st
from typing import Dict, List

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
    return st.text_input(
        "Did you like any of the options? If so, which dish did you prefer? "
        "If not, please let us know why and what changes you would suggest"
    )

def display_error(error: str):
    """Display error message."""
    st.error(f"An error occurred: {error}")

def display_success(message: str):
    """Display success message."""
    st.success(message) 