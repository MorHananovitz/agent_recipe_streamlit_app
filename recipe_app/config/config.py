import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")

# Model Configuration
MODEL_NAME = "gpt-4"
TEMPERATURE = 0
MAX_SEARCH_RESULTS = 3

# UI Configuration
PAGE_TITLE = "Recipe Assistant"
PAGE_ICON = "🍳"

# System Messages
SEARCH_INSTRUCTIONS = """You will be given a message requesting recipe information.
Your task is to generate a concise search query for recipe retrieval.

Instructions:
1. Analyze the message to identify:
   - Main ingredients
   - Cooking styles
   - Dietary restrictions
   - Preferences
2. Return ONLY a search query string (3-10 words)
3. DO NOT include any explanations or additional text
4. Focus on recipe-specific keywords

Example input: "I want to make a vegetarian pasta dish with mushrooms for dinner"
Example output: vegetarian mushroom pasta recipe"""

RECIPE_FEATURES_INSTRUCTIONS = """You will receive the top 3 recipes from a web search. For each recipe, extract and structure the following information:
1. dish_name: The name of the dish
2. key_ingredients: A list of the main ingredients used in the recipe
3. cooking_style: (Optional) The style or method of cooking (e.g., baked, grilled, stir-fried)

Format the information according to the following structure for each recipe:
{
    "dish_name": "Name of the dish",
    "key_ingredients": ["ingredient1", "ingredient2", ...],
    "cooking_style": "Style of cooking"
}

Return exactly 3 recipes in this format.""" 