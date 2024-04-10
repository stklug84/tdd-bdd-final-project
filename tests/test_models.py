# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    def test_read_product(self):
        """Read Product from Product Class"""
        # Create product
        product = ProductFactory()
        # Set product ID to None
        product.id = None
        # Check if create product works
        product.create()
        self.assertIsNotNone(product.id)
        # Check if product can be found again
        retrieved_product = Product.find(product.id)
        self.assertEqual(retrieved_product.id, product.id)
        self.assertEqual(retrieved_product.name, product.name)
        self.assertEqual(retrieved_product.description, product.description)
        self.assertEqual(retrieved_product.price, product.price)

    def test_update_product(self):
        """Update Product"""
        # Create product
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        # Update product description
        product.description = "test description"
        # Save product id for desrciption check assertion
        product_id = product.id
        # Test Update method
        product.update()
        self.assertEqual(product.id, product_id)
        self.assertEqual(product.description, "test description")
        # Get all products form the database
        products = Product.all()
        # Check that there is only one product
        self.assertEqual(len(products), 1)
        # Check if product id has not been modified
        self.assertEqual(products[0].id, product_id)
        # Check updated description
        self.assertEqual(products[0].description, "test description")

    def test_delete_product(self):
        """Delete Product"""
        # Create product
        product = ProductFactory()
        product.create()
        # Check if there is one product in the database
        self.assertEqual(len(Product.all()), 1)
        # Delete the product
        product.delete()
        # Check there are no products in the database left
        self.assertEqual(len(Product.all()), 0)

    def test_list_all_products(self):
        """List all Products in the database"""
        # Check there are no products in the database
        product_list = Product.all()
        self.assertEqual(product_list, [])
        # Create five products
        products = ProductFactory.create_batch(5)
        for product in products:
            product.create()
        product_list = Product.all()
        self.assertEqual(len(product_list), 5)

    def test_find_by_name(self):
        """Find a product by name"""
        # Create five products
        products = ProductFactory.create_batch(5)
        for product in products:
            product.create()
        # Retrieve the name of the first product
        name = products[0].name
        # Count the number of occurances in product list
        count = len([product for product in products if product.name == name])
        # Get products matching the name
        products_with_name = Product.find_by_name(name)
        # Check if all products have been found
        self.assertEqual(products_with_name.count(), count)
        # Check if product name matches
        for product in products_with_name:
            self.assertEqual(product.name, name)

    def test_find_by_availability(self):
        """Find Products by Availability"""
        # Create ten products
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        # Check if first product is available
        is_available = products[0].available
        # Count how many products are available
        count = 0
        for product in products:
            if product.available == is_available:
                count += 1
        # Find all products with availability
        products_with_availability = Product.find_by_availability(is_available)
        # Check if counts match
        self.assertEqual(products_with_availability.count(), count)
        # Check if each product matches availability
        for product in products_with_availability:
            self.assertEqual(product.available, is_available)

    def test_find_by_category(self):
        """Find Products by Category"""
        # Create ten products
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        # Retrieve category of the first product
        category = products[0].category
        # Count the number of products with that category
        count = 0
        for product in products:
            if product.category == category:
                count += 1
        # Retrieve products with that category
        products_with_category = Product.find_by_category(category)
        # Check if count matches
        self.assertEqual(products_with_category.count(), count)
        # Check if each products matches the category
        for product in products_with_category:
            self.assertEqual(product.category, category)
