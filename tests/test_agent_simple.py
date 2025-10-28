#!/usr/bin/env python3
"""Test script for the recipe agent workflow - Non-interactive mode."""

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

def main():
    """Main test function."""
    print_separator("*")
    print("🤖 RECIPE AGENT TEST - Terminal Mode")
    print_separator("*")
    
    # Check for API keys from environment
    openai_key = os.getenv("OPENAI_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")
    
    if not openai_key or not tavily_key:
        print("\n❌ ERROR: API keys not found in environment!")
        print("\nPlease set environment variables:")
        print("  export OPENAI_API_KEY='your-key-here'")
        print("  export TAVILY_API_KEY='your-key-here'")
        print("\nOr pass them as arguments:")
        print("  python test_agent_simple.py <openai_key> <tavily_key>")
        
        if len(sys.argv) >= 3:
            openai_key = sys.argv[1]
            tavily_key = sys.argv[2]
            os.environ["OPENAI_API_KEY"] = openai_key
            os.environ["TAVILY_API_KEY"] = tavily_key
            print("\n✅ API keys set from command line arguments!")
        else:
            sys.exit(1)
    else:
        print("\n✅ API keys found in environment!")
    
    # Initialize the graph
    print("\n⚙️  Initializing recipe agent graph...")
    graph = initialize_graph()
    
    # Test input
    user_input = "I have eggs, flour, tomatoes and cheese - what can I make?"
    print(f"\n👤 USER INPUT: {user_input}")
    print_separator()
    
    # Create initial state
    input_message = HumanMessage(content=user_input)
    
    print("\n🔄 Running agent workflow...")
    print_separator()
    
    try:
        # Run the graph
        print("\n📝 Step 1: Translating query...")
        output = graph.invoke(
            {"messages": [input_message]},
            {"configurable": {"thread_id": "test_1"}}
        )
        
        print(f"   ✓ Translated Query: '{output.get('query', 'N/A')}'")
        
        # Print recipes
        print_separator()
        print("\n🍳 RETRIEVED RECIPES")
        print_separator()
        
        for i, recipe in enumerate(output.get('recipes', []), 1):
            print(f"\n📖 Recipe {i}: {recipe.get('name', 'Unknown')}")
            print(f"   URL: {recipe.get('url', 'N/A')}")
            print(f"   Preview: {recipe.get('content', 'N/A')[:150]}...")
        
        # Print key features
        print_separator()
        print("\n✨ KEY FEATURES EXTRACTED")
        print_separator()
        
        for i, feature in enumerate(output.get('key_features', []), 1):
            print(f"\n🔹 Option {i}: {feature.dish_name}")
            print(f"   Ingredients: {', '.join(feature.key_ingredients)}")
            if feature.cooking_style:
                print(f"   Cooking Style: {feature.cooking_style}")
        
        # Summary
        print_separator("=")
        print("\n📊 WORKFLOW SUMMARY")
        print_separator("=")
        print(f"✓ Original Query: '{user_input}'")
        print(f"✓ Translated Query: '{output.get('query', 'N/A')}'")
        print(f"✓ Recipes Found: {len(output.get('recipes', []))}")
        print(f"✓ Key Features Extracted: {len(output.get('key_features', []))}")
        print(f"✓ Recipe Index: {output.get('recipes_index', -1)} (no selection yet)")
        
        print("\n✅ Agent workflow completed successfully!")
        print_separator("*")
        
        return output
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = main()
    sys.exit(0 if result else 1)

