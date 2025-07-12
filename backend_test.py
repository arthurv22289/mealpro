import requests
import sys
import json
from datetime import datetime

class MealProAPITester:
    def __init__(self, base_url="https://c6e25d30-1005-4923-add6-0459f2453805.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.created_ingredient_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}" if endpoint else self.base_url
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, list):
                        print(f"   Response: List with {len(response_data)} items")
                    else:
                        print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                except:
                    print(f"   Response: {response.text[:100]}...")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}...")

            return success, response.json() if response.text and response.status_code < 400 else {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test root API endpoint"""
        success, response = self.run_test(
            "Root API Endpoint",
            "GET",
            "",
            200
        )
        return success

    def test_initialize_data(self):
        """Test data initialization"""
        success, response = self.run_test(
            "Initialize Sample Data",
            "POST",
            "initialize-data",
            200
        )
        return success

    def test_get_all_ingredients(self):
        """Test getting all ingredients"""
        success, response = self.run_test(
            "Get All Ingredients",
            "GET",
            "ingredients",
            200
        )
        if success and isinstance(response, list):
            print(f"   Found {len(response)} ingredients")
            categories = set(ingredient.get('category') for ingredient in response)
            print(f"   Categories: {categories}")
        return success, response

    def test_get_ingredients_by_category(self):
        """Test getting ingredients by category"""
        categories = ["entree", "base_sauce", "proteine", "feculent", "legumes", "technique_cuisson", "dessert"]
        all_passed = True
        
        for category in categories:
            success, response = self.run_test(
                f"Get Ingredients - {category}",
                "GET",
                f"ingredients/{category}",
                200
            )
            if success and isinstance(response, list):
                print(f"   Found {len(response)} ingredients in {category}")
            all_passed = all_passed and success
            
        return all_passed

    def test_create_ingredient(self):
        """Test creating a new ingredient"""
        test_ingredient = {
            "name": f"Test Ingredient {datetime.now().strftime('%H%M%S')}",
            "category": "entree"
        }
        
        success, response = self.run_test(
            "Create New Ingredient",
            "POST",
            "ingredients",
            200,
            data=test_ingredient
        )
        
        if success and 'id' in response:
            self.created_ingredient_id = response['id']
            print(f"   Created ingredient with ID: {self.created_ingredient_id}")
        
        return success

    def test_update_ingredient(self):
        """Test updating an ingredient"""
        if not self.created_ingredient_id:
            print("❌ Skipping update test - no ingredient ID available")
            return False
            
        update_data = {
            "name": f"Updated Test Ingredient {datetime.now().strftime('%H%M%S')}"
        }
        
        success, response = self.run_test(
            "Update Ingredient",
            "PUT",
            f"ingredients/{self.created_ingredient_id}",
            200,
            data=update_data
        )
        return success

    def test_delete_ingredient(self):
        """Test deleting an ingredient"""
        if not self.created_ingredient_id:
            print("❌ Skipping delete test - no ingredient ID available")
            return False
            
        success, response = self.run_test(
            "Delete Ingredient",
            "DELETE",
            f"ingredients/{self.created_ingredient_id}",
            200
        )
        return success

    def test_generate_menu(self):
        """Test generating a random menu"""
        success, response = self.run_test(
            "Generate Random Menu",
            "POST",
            "generate-menu",
            200
        )
        
        if success:
            expected_fields = ["entree", "base_sauce", "proteine", "feculent", "legumes", "technique_cuisson", "dessert"]
            missing_fields = [field for field in expected_fields if field not in response]
            if missing_fields:
                print(f"   ⚠️  Missing fields in menu: {missing_fields}")
            else:
                print(f"   ✅ Menu contains all required categories")
        
        return success

    def test_get_generated_menus(self):
        """Test getting generated menus"""
        success, response = self.run_test(
            "Get Generated Menus",
            "GET",
            "generated-menus",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} generated menus")
        
        return success

def main():
    print("🍽️ MealPro API Testing Suite")
    print("=" * 50)
    
    tester = MealProAPITester()
    
    # Test sequence
    tests = [
        ("Root Endpoint", tester.test_root_endpoint),
        ("Initialize Data", tester.test_initialize_data),
        ("Get All Ingredients", lambda: tester.test_get_all_ingredients()[0]),
        ("Get Ingredients by Category", tester.test_get_ingredients_by_category),
        ("Create Ingredient", tester.test_create_ingredient),
        ("Update Ingredient", tester.test_update_ingredient),
        ("Delete Ingredient", tester.test_delete_ingredient),
        ("Generate Menu", tester.test_generate_menu),
        ("Get Generated Menus", tester.test_get_generated_menus),
    ]
    
    print(f"\n🚀 Running {len(tests)} test suites...")
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            test_func()
        except Exception as e:
            print(f"❌ Test suite failed with error: {str(e)}")
    
    # Print final results
    print(f"\n{'='*50}")
    print(f"📊 FINAL RESULTS")
    print(f"{'='*50}")
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())