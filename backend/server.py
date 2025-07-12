from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class Ingredient(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    category: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class IngredientCreate(BaseModel):
    name: str
    category: str

class IngredientUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None

class GeneratedMenu(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    entree: str
    base_sauce: str
    proteine: str
    feculent: str
    legumes: str
    technique_cuisson: str
    dessert: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Ingredient routes
@api_router.get("/")
async def root():
    return {"message": "MealPro API is running"}

@api_router.get("/ingredients", response_model=List[Ingredient])
async def get_ingredients():
    """Get all ingredients"""
    ingredients = await db.ingredients.find().to_list(1000)
    return [Ingredient(**ingredient) for ingredient in ingredients]

@api_router.get("/ingredients/{category}", response_model=List[Ingredient])
async def get_ingredients_by_category(category: str):
    """Get ingredients by category"""
    ingredients = await db.ingredients.find({"category": category}).to_list(1000)
    return [Ingredient(**ingredient) for ingredient in ingredients]

@api_router.post("/ingredients", response_model=Ingredient)
async def create_ingredient(ingredient: IngredientCreate):
    """Create a new ingredient"""
    ingredient_dict = ingredient.dict()
    ingredient_obj = Ingredient(**ingredient_dict)
    await db.ingredients.insert_one(ingredient_obj.dict())
    return ingredient_obj

@api_router.put("/ingredients/{ingredient_id}", response_model=Ingredient)
async def update_ingredient(ingredient_id: str, ingredient_update: IngredientUpdate):
    """Update an ingredient"""
    update_data = {k: v for k, v in ingredient_update.dict().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No update data provided")
    
    result = await db.ingredients.update_one(
        {"id": ingredient_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    
    updated_ingredient = await db.ingredients.find_one({"id": ingredient_id})
    return Ingredient(**updated_ingredient)

@api_router.delete("/ingredients/{ingredient_id}")
async def delete_ingredient(ingredient_id: str):
    """Delete an ingredient"""
    result = await db.ingredients.delete_one({"id": ingredient_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    
    return {"message": "Ingredient deleted successfully"}

@api_router.post("/generate-menu", response_model=GeneratedMenu)
async def generate_random_menu():
    """Generate a random menu by selecting one ingredient from each category"""
    categories = ["entree", "base_sauce", "proteine", "feculent", "legumes", "technique_cuisson", "dessert"]
    menu_items = {}
    
    for category in categories:
        ingredients = await db.ingredients.find({"category": category}).to_list(1000)
        if ingredients:
            import random
            selected = random.choice(ingredients)
            menu_items[category] = selected["name"]
        else:
            menu_items[category] = f"Aucun {category} disponible"
    
    menu = GeneratedMenu(**menu_items)
    await db.generated_menus.insert_one(menu.dict())
    return menu

@api_router.get("/generated-menus", response_model=List[GeneratedMenu])
async def get_generated_menus():
    """Get all generated menus"""
    menus = await db.generated_menus.find().sort("created_at", -1).to_list(50)
    return [GeneratedMenu(**menu) for menu in menus]

@api_router.post("/initialize-data")
async def initialize_sample_data():
    """Initialize the database with sample ingredients"""
    
    # Check if data already exists
    existing_count = await db.ingredients.count_documents({})
    if existing_count > 0:
        return {"message": "Data already initialized"}
    
    sample_ingredients = [
        # Entrées
        {"name": "Soupe froide", "category": "entree"},
        {"name": "Gaspacho", "category": "entree"},
        {"name": "Velouté", "category": "entree"},
        {"name": "Salade verte", "category": "entree"},
        {"name": "Crudités", "category": "entree"},
        
        # Base Sauce
        {"name": "Base fromage blanc", "category": "base_sauce"},
        {"name": "Base yaourt grec", "category": "base_sauce"},
        {"name": "Base miso", "category": "base_sauce"},
        {"name": "Base tahini", "category": "base_sauce"},
        {"name": "Base olive", "category": "base_sauce"},
        
        # Protéines
        {"name": "Grillé", "category": "proteine"},
        {"name": "Air fryer", "category": "proteine"},
        {"name": "Mariné", "category": "proteine"},
        {"name": "Mi-cuit", "category": "proteine"},
        {"name": "Fumé", "category": "proteine"},
        
        # Féculents
        {"name": "Riz complet", "category": "feculent"},
        {"name": "Riz noir", "category": "feculent"},
        {"name": "Bulgour", "category": "feculent"},
        {"name": "Épautre", "category": "feculent"},
        {"name": "Papetline", "category": "feculent"},
        
        # Légumes
        {"name": "Vapeur", "category": "legumes"},
        {"name": "Air fryer", "category": "legumes"},
        {"name": "Sautés", "category": "legumes"},
        {"name": "Rôtis four", "category": "legumes"},
        {"name": "Salade wok", "category": "legumes"},
        
        # Technique Cuisson
        {"name": "Air Fryer 180°C", "category": "technique_cuisson"},
        {"name": "Plancha haute température", "category": "technique_cuisson"},
        {"name": "Grill/Barbecue", "category": "technique_cuisson"},
        {"name": "Four 200°C chaleur tournante", "category": "technique_cuisson"},
        {"name": "Wok sauté rapide", "category": "technique_cuisson"},
        
        # Desserts
        {"name": "Nice cream", "category": "dessert"},
        {"name": "Chia pudding", "category": "dessert"},
        {"name": "Mousse", "category": "dessert"},
        {"name": "Skyr", "category": "dessert"},
        {"name": "Fromage blanc", "category": "dessert"}
    ]
    
    ingredients_objects = [Ingredient(**ingredient) for ingredient in sample_ingredients]
    ingredients_dicts = [ingredient.dict() for ingredient in ingredients_objects]
    
    await db.ingredients.insert_many(ingredients_dicts)
    
    return {"message": f"Initialized {len(sample_ingredients)} sample ingredients"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()