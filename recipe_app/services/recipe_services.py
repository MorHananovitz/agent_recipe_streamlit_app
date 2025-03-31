import logging
from typing import Dict, Any, List
from langchain.schema import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search.tool import TavilySearchResults
from recipe_app.models.recipe_models import (
    RecipeState, 
    ResponseRecipeKeyFeatures, 
    HumanSelection,
    RecipeFeature
)
from recipe_app.config.config import (
    MODEL_NAME, 
    TEMPERATURE, 
    MAX_SEARCH_RESULTS,
    SEARCH_INSTRUCTIONS,
    RECIPE_FEATURES_INSTRUCTIONS,
    TAVILY_API_KEY
)
import streamlit as st

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QueryTranslator:
    """Transforms human messages into structured web queries using LLM."""

    @staticmethod
    def translate(state: RecipeState) -> RecipeState:
        try:
            logger.info("Starting query translation")
            llm = ChatOpenAI(model=MODEL_NAME, temperature=TEMPERATURE)
            messages = state.get("messages", [])
            
            # Update system message to request just the search query
            system_message = SystemMessage(content=SEARCH_INSTRUCTIONS + "\nProvide ONLY the search query without any additional text or explanation.")
            response = llm.invoke([system_message] + messages)
            
            # Extract just the query text, removing any quotes
            query = response.content.strip().strip('"').strip("'")
            state["query"] = query
            
            logger.info(f"Query translated: {query}")
            return state
        except Exception as e:
            logger.error(f"Error in query translation: {str(e)}")
            raise

class RecipeRetriever:
    """Retrieves recipes using Tavily search."""

    @staticmethod
    def _cached_search(query: str) -> list:
        """Cached search function that takes a string instead of state."""
        logger.info(f"Performing cached search for query: {query}")
        tavily_search = TavilySearchResults(max_results=MAX_SEARCH_RESULTS)
        search_docs = tavily_search.run(query)
        return [
            {
                "name": doc.get("title", "Unknown Dish"),
                "url": doc["url"],
                "content": doc["content"]
            }
            for doc in search_docs
        ]

    @staticmethod
    def retrieve(state: RecipeState) -> RecipeState:
        try:
            logger.info("Starting recipe retrieval")
            query = state.get("query", "")
            
            if not query:
                logger.error("No query provided")
                state['recipes'] = []
                return state
            
            # Use the cached search function with just the query string
            formatted_search_recipes = st.cache_data(ttl=3600)(_cached_search)(query)
            
            state['recipes'] = formatted_search_recipes
            logger.info(f"Retrieved {len(formatted_search_recipes)} recipes")
            return state
        except Exception as e:
            logger.error(f"Error in recipe retrieval: {str(e)}")
            state['recipes'] = []
            return state

class RecipeKeyFeatures:
    """Extracts key features from the retrieved recipes."""

    @staticmethod
    def _cached_extract(recipes_str: str) -> List[RecipeFeature]:
        """Cached extraction function that takes a string instead of state."""
        logger.info("Performing cached feature extraction")
        llm = ChatOpenAI(model=MODEL_NAME, temperature=TEMPERATURE)
        structured_llm = llm.with_structured_output(ResponseRecipeKeyFeatures)
        key_features = structured_llm.invoke([
            SystemMessage(content=RECIPE_FEATURES_INSTRUCTIONS),
            HumanMessage(content=recipes_str)
        ])
        return key_features.results

    @staticmethod
    def extract(state: RecipeState) -> RecipeState:
        try:
            logger.info("Starting feature extraction")
            # Convert recipes to a string for caching
            formatted_docs = "\n\n".join([
                f"Recipe: {doc['name']}\nContent: {doc['content']}"
                for doc in state['recipes']
            ])
            
            # Use the cached extraction function with just the string
            features = st.cache_data(ttl=3600)(_cached_extract)(formatted_docs)
            
            state['key_features'] = features
            logger.info("Feature extraction completed")
            return state
        except Exception as e:
            logger.error(f"Error in feature extraction: {str(e)}")
            state['key_features'] = []
            return state

class HumanFeedback:
    """Processes user feedback on recipes."""

    @staticmethod
    def refine(state: RecipeState) -> Dict[str, Any]:
        try:
            logger.info("Processing user feedback")
            llm = ChatOpenAI(model=MODEL_NAME, temperature=TEMPERATURE)
            
            # Get user feedback from state
            user_feedback = state.get("feedback")
            if not user_feedback:
                # Keep existing recipes_index if it exists
                if 'recipes_index' not in state:
                    state['recipes_index'] = -1
                return state

            system_message = SystemMessage(content=f"""
            Process the user feedback on the suggested recipes:
            Current recipes: {state.get('key_features', [])}
            User feedback: {user_feedback}

            Instructions:
            1. If the user expresses satisfaction with any recipe, return its index (0, 1, or 2).
            2. If the user wants modifications or different recipes, explain why in the dislike field.
            3. Be strict about recipe selection - only set 'like' if there's clear positive feedback.
            """)

            structured_llm = llm.with_structured_output(HumanSelection)
            classification = structured_llm.invoke([system_message])

            if classification.like is not None:
                state['recipes_index'] = classification.like
                logger.info(f"User selected recipe {classification.like}")
            else:
                state['recipes_index'] = -1
                state["messages"] = [HumanMessage(content=classification.dislike)]
                logger.info(f"User requested modifications: {classification.dislike}")
            
            # Clear feedback after processing to prevent loops
            state["feedback"] = None
            return state
        except Exception as e:
            logger.error(f"Error in feedback processing: {str(e)}")
            if 'recipes_index' not in state:
                state['recipes_index'] = -1
            return state

class Satisfaction:
    """Determines if the user is satisfied with the recipe selection."""

    @staticmethod
    def recipe_satisfaction(state: RecipeState) -> str:
        try:
            # Get recipes_index with default value of -1
            recipes_index = state.get('recipes_index', -1)
            
            # Check if we have feedback to process
            has_feedback = state.get('feedback') is not None
            
            # Only restart if we have feedback and no recipe was selected
            if recipes_index == -1 and has_feedback:
                logger.info("User not satisfied, restarting query")
                return "translate_query"
            elif recipes_index >= 0:
                logger.info(f"User satisfied with recipe {recipes_index}")
                return END
            else:
                # If no feedback yet, end current iteration
                logger.info("No feedback yet or current iteration complete")
                return END
                
        except Exception as e:
            logger.error(f"Error in satisfaction check: {str(e)}")
            # On error, end current iteration
            return END 