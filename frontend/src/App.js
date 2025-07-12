import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [ingredients, setIngredients] = useState({});
  const [generatedMenu, setGeneratedMenu] = useState(null);
  const [loading, setLoading] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [newItemName, setNewItemName] = useState("");

  const categories = [
    { key: "entree", label: "Entrée", icon: "🥗", color: "bg-green-100 border-green-300" },
    { key: "base_sauce", label: "Base Sauce", icon: "🥫", color: "bg-orange-100 border-orange-300" },
    { key: "proteine", label: "Protéine", icon: "🍖", color: "bg-red-100 border-red-300" },
    { key: "feculent", label: "Féculent", icon: "🌾", color: "bg-yellow-100 border-yellow-300" },
    { key: "legumes", label: "Légumes", icon: "🥬", color: "bg-green-100 border-green-300" },
    { key: "technique_cuisson", label: "Technique Cuisson", icon: "🔥", color: "bg-purple-100 border-purple-300" },
    { key: "dessert", label: "Dessert", icon: "🍰", color: "bg-pink-100 border-pink-300" }
  ];

  // Initialize data on first load
  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    try {
      // Initialize sample data
      await axios.post(`${API}/initialize-data`);
      
      // Load ingredients
      await loadIngredients();
    } catch (error) {
      console.error("Error initializing app:", error);
    }
  };

  const loadIngredients = async () => {
    try {
      const response = await axios.get(`${API}/ingredients`);
      const ingredientsByCategory = {};
      
      categories.forEach(category => {
        ingredientsByCategory[category.key] = response.data.filter(
          ingredient => ingredient.category === category.key
        );
      });
      
      setIngredients(ingredientsByCategory);
    } catch (error) {
      console.error("Error loading ingredients:", error);
    }
  };

  const handleDoubleClick = (ingredientName) => {
    const searchQuery = `recette healthy ${ingredientName}`;
    const googleSearchUrl = `https://www.google.com/search?q=${encodeURIComponent(searchQuery)}`;
    window.open(googleSearchUrl, '_blank');
  };

  const generateRandomMenu = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/generate-menu`);
      setGeneratedMenu(response.data);
    } catch (error) {
      console.error("Error generating menu:", error);
      alert("Erreur lors de la génération du menu");
    } finally {
      setLoading(false);
    }
  };

  const startEditing = (ingredient, category) => {
    setEditingItem({ ...ingredient, category });
    setNewItemName(ingredient.name);
  };

  const saveEdit = async () => {
    if (!newItemName.trim()) return;

    try {
      await axios.put(`${API}/ingredients/${editingItem.id}`, {
        name: newItemName.trim()
      });
      setEditingItem(null);
      setNewItemName("");
      await loadIngredients();
    } catch (error) {
      console.error("Error updating ingredient:", error);
      alert("Erreur lors de la modification");
    }
  };

  const cancelEdit = () => {
    setEditingItem(null);
    setNewItemName("");
  };

  const addNewIngredient = async (category) => {
    const name = prompt(`Ajouter un nouvel élément à ${categories.find(c => c.key === category)?.label}:`);
    if (!name || !name.trim()) return;

    try {
      await axios.post(`${API}/ingredients`, {
        name: name.trim(),
        category: category
      });
      await loadIngredients();
    } catch (error) {
      console.error("Error adding ingredient:", error);
      alert("Erreur lors de l'ajout");
    }
  };

  const deleteIngredient = async (ingredientId) => {
    if (!window.confirm("Êtes-vous sûr de vouloir supprimer cet élément ?")) return;

    try {
      await axios.delete(`${API}/ingredients/${ingredientId}`);
      await loadIngredients();
    } catch (error) {
      console.error("Error deleting ingredient:", error);
      alert("Erreur lors de la suppression");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-gray-900 mb-2">🍽️ MealPro</h1>
            <p className="text-xl text-gray-600 mb-4">Plan. Cook. Enjoy</p>
            <p className="text-gray-500 max-w-2xl mx-auto">
              Smart meal planning that adapts to your lifestyle. Create healthy, delicious meals with zero hassle.
            </p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        
        {/* Generate Menu Button */}
        <div className="text-center mb-8">
          <button
            onClick={generateRandomMenu}
            disabled={loading}
            className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 px-8 rounded-lg shadow-lg transform transition hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? "Génération..." : "🎲 Générer Menu Aléatoire"}
          </button>
          <p className="text-sm text-gray-500 mt-2">
            Double-cliquez sur un ingrédient pour rechercher une recette healthy
          </p>
        </div>

        {/* Generated Menu Display */}
        {generatedMenu && (
          <div className="bg-white rounded-xl shadow-lg p-6 mb-8 border border-gray-200">
            <h3 className="text-2xl font-bold text-center text-gray-800 mb-6">🍽️ Menu Généré</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {categories.map(category => (
                <div key={category.key} className="text-center">
                  <div className="text-lg font-semibold text-gray-700 mb-1">
                    {category.icon} {category.label}
                  </div>
                  <div className="bg-gray-50 rounded-lg p-3 text-gray-800 font-medium">
                    {generatedMenu[category.key]}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Meal Planning Dashboard */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-800">Meal Planning Dashboard</h2>
            <p className="text-sm text-gray-500">Double-cliquez sur un élément pour des recettes</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-7 gap-4">
            {categories.map(category => (
              <div key={category.key} className={`rounded-lg border-2 ${category.color} p-4`}>
                {/* Category Header */}
                <div className="text-center mb-4">
                  <div className="text-2xl mb-1">{category.icon}</div>
                  <h3 className="font-bold text-gray-800 text-sm">{category.label}</h3>
                </div>

                {/* Ingredients List */}
                <div className="space-y-2 min-h-[300px]">
                  {ingredients[category.key]?.map(ingredient => (
                    <div key={ingredient.id} className="relative group">
                      {editingItem?.id === ingredient.id ? (
                        <div className="space-y-2">
                          <input
                            type="text"
                            value={newItemName}
                            onChange={(e) => setNewItemName(e.target.value)}
                            className="w-full px-2 py-1 text-xs border rounded"
                            autoFocus
                          />
                          <div className="flex space-x-1">
                            <button
                              onClick={saveEdit}
                              className="px-2 py-1 bg-green-500 text-white text-xs rounded hover:bg-green-600"
                            >
                              ✓
                            </button>
                            <button
                              onClick={cancelEdit}
                              className="px-2 py-1 bg-gray-500 text-white text-xs rounded hover:bg-gray-600"
                            >
                              ✕
                            </button>
                          </div>
                        </div>
                      ) : (
                        <div 
                          className="bg-white rounded-lg p-3 text-xs text-center cursor-pointer hover:bg-gray-50 transition-colors shadow-sm border"
                          onDoubleClick={() => handleDoubleClick(ingredient.name)}
                        >
                          <span>{ingredient.name}</span>
                          <div className="opacity-0 group-hover:opacity-100 transition-opacity mt-2 flex justify-center space-x-1">
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                startEditing(ingredient, category.key);
                              }}
                              className="px-2 py-1 bg-blue-500 text-white text-xs rounded hover:bg-blue-600"
                              title="Modifier"
                            >
                              ✏️
                            </button>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                deleteIngredient(ingredient.id);
                              }}
                              className="px-2 py-1 bg-red-500 text-white text-xs rounded hover:bg-red-600"
                              title="Supprimer"
                            >
                              🗑️
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                  
                  {/* Add New Item Button */}
                  <button
                    onClick={() => addNewIngredient(category.key)}
                    className="w-full bg-gray-100 hover:bg-gray-200 border-2 border-dashed border-gray-300 rounded-lg p-3 text-xs text-gray-500 transition-colors"
                  >
                    + Ajouter
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;