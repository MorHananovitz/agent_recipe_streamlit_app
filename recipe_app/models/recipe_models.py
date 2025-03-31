from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Optional, Union
from langgraph.graph import MessagesState

class SearchQuery(BaseModel):
    """Model for search queries."""
    search_query: str = Field(None, description="Search query for retrieval.")

class RecipeState(MessagesState):
    """State model for recipe processing."""
    query: str  # Search query
    recipes: List[Dict]  # List of found recipes
    key_features: List[str]  # Key features of recipes
    recipes_index: int = -1  # Selected recipe index, defaults to -1 (no selection)

class RecipeFeature(BaseModel):
    """Model for individual recipe features."""
    dish_name: str = Field(..., description="Name of the dish")
    key_ingredients: List[str] = Field(default_factory=list, description="List of key ingredients")
    cooking_style: Optional[str] = Field(None, description="Style of cooking (if applicable)")

class ResponseRecipeKeyFeatures(BaseModel):
    """Model for recipe key features response."""
    results: List[RecipeFeature]

class HumanSelection(BaseModel):
    """Model for human feedback on recipes."""
    like: Optional[int] = Field(None, description="Index of the liked recipe (0, 1, or 2). Null if none liked.")
    dislike: Optional[str] = Field(None, description="Explanation of why all recipes were disliked. Null if a recipe was liked.")

    @field_validator("like", mode="before")
    @classmethod
    def validate_and_convert_like(cls, value: Union[str, int, None]):
        if value is None:
            return None
        if isinstance(value, str) and value.isdigit():
            value = int(value)
        if value not in {0, 1, 2}:
            raise ValueError("like must be either 0, 1, 2, or None")
        return value

    class Config:
        json_schema_extra = {
            "example": [
                {"like": 1, "dislike": None},
                {"like": None, "dislike": "I prefer vegan options."},
                {"like": "2", "dislike": None}
            ]
        } 