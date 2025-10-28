#!/usr/bin/env python3
"""Test script for the recipe agent workflow."""

import os
import sys

# Add parent directory to path to import recipe_app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

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

def print_recipes(state):
    """Print the retrieved recipes in a formatted way."""
    print_separator()
    print("🍳 RETRIEVED RECIPES")
    print_separator()
    
    if not state.get('recipes'):
        print("No recipes found.")
        return
    
    for i, recipe in enumerate(state['recipes'], 1):
        print(f"\n📖 Recipe {i}: {recipe.get('name', 'Unknown')}")
        print(f"   URL: {recipe.get('url', 'N/A')}")
        print(f"   Content: {recipe.get('content', 'N/A')[:200]}...")

def print_key_features(state):
    """Print the extracted key features."""
    print_separator()
    print("✨ KEY FEATURES")
    print_separator()
    
    if not state.get('key_features'):
        print("No key features extracted.")
        return
    
    for i, feature in enumerate(state['key_features'], 1):
        print(f"\n🔹 Option {i}: {feature.dish_name}")
        print(f"   Ingredients: {', '.join(feature.key_ingredients)}")
        if feature.cooking_style:
            print(f"   Cooking Style: {feature.cooking_style}")

def main():
    """Main test function."""
    print_separator("*")
    print("🤖 RECIPE AGENT TEST - Terminal Mode")
    print_separator("*")
    
    # Check for API keys
    openai_key = os.getenv("OPENAI_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")
    
    if not openai_key:
        openai_key = input("\n🔑 Enter your OpenAI API Key: ").strip()
        os.environ["OPENAI_API_KEY"] = openai_key
    
    if not tavily_key:
        tavily_key = input("🔑 Enter your Tavily API Key: ").strip()
        os.environ["TAVILY_API_KEY"] = tavily_key
    
    print("\n✅ API keys configured!")
    
    # Initialize the graph
    print("\n⚙️  Initializing recipe agent graph...")
    graph = initialize_graph()
    memory = MemorySaver()
    
    # Test input
    user_input = "I have eggs, flour, tomatoes and cheese - what can I make?"
    print(f"\n👤 USER INPUT: {user_input}")
    print_separator()
    
    # Create initial state
    input_message = HumanMessage(content=user_input)
    
    print("\n🔄 Running agent workflow...")
    print_separator()
    
    try:
        # Step 1: Translate Query
        print("\n📝 Step 1: Translating query...")
        output = graph.invoke(
            {"messages": [input_message]},
            {"configurable": {"thread_id": "test_1"}}
        )
        
        print(f"   Translated Query: '{output.get('query', 'N/A')}'")
        
        # Print recipes
        print_recipes(output)
        
        # Print key features
        print_key_features(output)
        
        # Summary
        print_separator("=")
        print("📊 WORKFLOW SUMMARY")
        print_separator("=")
        print(f"✓ Query: {output.get('query', 'N/A')}")
        print(f"✓ Recipes Found: {len(output.get('recipes', []))}")
        print(f"✓ Key Features Extracted: {len(output.get('key_features', []))}")
        print(f"✓ Recipe Index: {output.get('recipes_index', -1)}")
        
        print("\n✅ Agent workflow completed successfully!")
        print_separator("*")
        
        # Optional: Test feedback loop
        test_feedback = input("\n❓ Would you like to test the feedback loop? (yes/no): ").strip().lower()
        
        if test_feedback in ['yes', 'y']:
            feedback = input("\n💬 Enter your feedback (e.g., 'I want something vegetarian'): ").strip()
            
            print(f"\n🔄 Processing feedback: '{feedback}'")
            print_separator()
            
            # Add feedback to state
            output["feedback"] = feedback
            
            # Run again with feedback
            output = graph.invoke(
                output,
                {"configurable": {"thread_id": "test_1"}}
            )
            
            print_recipes(output)
            print_key_features(output)
            
            print("\n✅ Feedback processed!")
        
        return output
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()

