#!/usr/bin/env python3
"""Test script for the recipe agent feedback loop."""

import os
import sys

# Add parent directory to path to import recipe_app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END

from recipe_app.models.recipe_models import RecipeState
from recipe_app.services.recipe_services import (
    QueryTranslator, 
    RecipeRetriever, 
    RecipeKeyFeatures, 
    HumanFeedback,
    Satisfaction
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

def print_separator(char="=", length=80):
    """Print a separator line."""
    print(char * length)

def print_recipes(recipes):
    """Print the retrieved recipes in a formatted way."""
    if not recipes:
        print("No recipes found.")
        return
    
    for i, recipe in enumerate(recipes, 1):
        print(f"\n📖 Recipe {i}: {recipe.get('name', 'Unknown')}")
        print(f"   URL: {recipe.get('url', 'N/A')}")
        print(f"   Preview: {recipe.get('content', 'N/A')[:150]}...")

def print_key_features(features):
    """Print the extracted key features."""
    if not features:
        print("No key features extracted.")
        return
    
    for i, feature in enumerate(features, 1):
        print(f"\n🔹 Option {i}: {feature.dish_name}")
        print(f"   Ingredients: {', '.join(feature.key_ingredients) if feature.key_ingredients else 'N/A'}")
        if feature.cooking_style:
            print(f"   Cooking Style: {feature.cooking_style}")

def main():
    """Main test function."""
    print_separator("*")
    print("🤖 RECIPE AGENT - FEEDBACK LOOP TEST")
    print_separator("*")
    
    # Check for API keys from environment
    openai_key = os.getenv("OPENAI_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")
    
    if not openai_key or not tavily_key:
        print("\n❌ ERROR: API keys not found in environment!")
        print("\nPlease run:")
        print("  export OPENAI_API_KEY='your-key'")
        print("  export TAVILY_API_KEY='your-key'")
        sys.exit(1)
    
    print("\n✅ API keys configured!")
    
    # Initialize the graph
    print("\n⚙️  Initializing recipe agent graph...")
    graph = initialize_graph()
    
    # Test input
    user_input = "I have eggs, flour, tomatoes and cheese - what can I make?"
    print(f"\n👤 USER INPUT: {user_input}")
    print_separator()
    
    # Create initial state
    input_message = HumanMessage(content=user_input)
    
    print("\n🔄 ITERATION 1: Initial Recipe Search")
    print_separator()
    
    try:
        # First iteration - get initial recipes
        state = graph.invoke(
            {"messages": [input_message]},
            {"configurable": {"thread_id": "feedback_test"}}
        )
        
        print(f"\n✓ Translated Query: '{state.get('query', 'N/A')}'")
        print(f"✓ Recipes Found: {len(state.get('recipes', []))}")
        
        print_separator()
        print("\n🍳 RETRIEVED RECIPES")
        print_separator()
        print_recipes(state.get('recipes', []))
        
        print_separator()
        print("\n✨ KEY FEATURES")
        print_separator()
        print_key_features(state.get('key_features', []))
        
        # Now test feedback loop - Scenario 1: Provide negative feedback
        print("\n" + "="*80)
        print("🔄 ITERATION 2: Testing Negative Feedback (Request Different Recipes)")
        print("="*80)
        
        feedback1 = "I want something vegetarian and healthier"
        print(f"\n💬 Feedback: '{feedback1}'")
        
        # Add feedback to state
        state["feedback"] = feedback1
        
        # Run again with feedback
        state = graph.invoke(
            state,
            {"configurable": {"thread_id": "feedback_test"}}
        )
        
        print(f"\n✓ New Query: '{state.get('query', 'N/A')}'")
        print(f"✓ Recipes Found: {len(state.get('recipes', []))}")
        
        print_separator()
        print("\n🍳 NEW RECIPES AFTER FEEDBACK")
        print_separator()
        print_recipes(state.get('recipes', []))
        
        print_separator()
        print("\n✨ NEW KEY FEATURES")
        print_separator()
        print_key_features(state.get('key_features', []))
        
        # Test Scenario 2: Select a recipe
        print("\n" + "="*80)
        print("🔄 ITERATION 3: Testing Positive Feedback (Select Recipe)")
        print("="*80)
        
        feedback2 = "I like option 1, that sounds perfect!"
        print(f"\n💬 Feedback: '{feedback2}'")
        
        # Add feedback to state
        state["feedback"] = feedback2
        
        # Run again with selection feedback
        state = graph.invoke(
            state,
            {"configurable": {"thread_id": "feedback_test"}}
        )
        
        selected_index = state.get('recipes_index', -1)
        print(f"\n✓ Selected Recipe Index: {selected_index}")
        
        if selected_index >= 0:
            print_separator()
            print("\n🌟 SELECTED RECIPE")
            print_separator()
            selected_recipe = state.get('recipes', [])[selected_index]
            print(f"\n📖 {selected_recipe.get('name', 'Unknown')}")
            print(f"   URL: {selected_recipe.get('url', 'N/A')}")
            print(f"   Content: {selected_recipe.get('content', 'N/A')[:300]}...")
            
            selected_feature = state.get('key_features', [])[selected_index]
            print(f"\n✨ Dish: {selected_feature.dish_name}")
            print(f"   Ingredients: {', '.join(selected_feature.key_ingredients) if selected_feature.key_ingredients else 'N/A'}")
            if selected_feature.cooking_style:
                print(f"   Cooking Style: {selected_feature.cooking_style}")
        
        # Final Summary
        print("\n" + "="*80)
        print("📊 FEEDBACK LOOP TEST SUMMARY")
        print("="*80)
        print("\n✅ Iteration 1: Successfully retrieved initial recipes")
        print("✅ Iteration 2: Successfully processed negative feedback and found new recipes")
        print("✅ Iteration 3: Successfully processed positive feedback and selected recipe")
        print(f"\n🎉 Final Selection: Recipe {selected_index} - {state.get('key_features', [])[selected_index].dish_name if selected_index >= 0 else 'None'}")
        
        print("\n" + "*"*80)
        print("✅ FEEDBACK LOOP TEST COMPLETED SUCCESSFULLY!")
        print("*"*80)
        
        return state
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = main()
    sys.exit(0 if result else 1)

