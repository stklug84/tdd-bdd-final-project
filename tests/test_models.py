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

    #
    # ADD YOUR TEST CASES HERE
    #
    def test_read_product(self):
        """It should Read a product from the database and ensure it returns correctly."""
        product = ProductFactory()
        product.id = None
        product.create()
        fetched = Product.find(product.id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.name, product.name)
        self.assertEqual(fetched.description, product.description)
        self.assertEqual(Decimal(fetched.price), product.price)
        self.assertEqual(fetched.available, product.available)
        self.assertEqual(fetched.category, product.category)

    def test_update_product(self):
        """It should update a product in the database successfully and pass the test"""
        product = ProductFactory()
        product.id = None
        product.create()
        # Update product properties
        product.name = "Updated Product Name"
        product.description = "Updated description"
        product.price = product.price + Decimal("10.00")
        product.available = not product.available
        product.category = Category.FOOD if product.category != Category.FOOD else Category.CLOTHS
        product.update()
        # Retrieve updated product
        updated = Product.find(product.id)
        self.assertIsNotNone(updated)
        self.assertEqual(updated.name, "Updated Product Name")
        self.assertEqual(updated.description, "Updated description")
        self.assertEqual(updated.price, product.price)
        self.assertEqual(updated.available, product.available)
        self.assertEqual(updated.category, product.category)

    def test_delete_product(self):
        """It should delete a product from the database successfully and pass the test"""
        product = ProductFactory()
        product.id = None
        product.create()
        # Ensure the product was added
        fetched = Product.find(product.id)
        self.assertIsNotNone(fetched)
        # Delete the product
        product.delete()
        # Attempt to retrieve the deleted product
        deleted = Product.find(product.id)
        self.assertIsNone(deleted)

    def test_list_all_products(self):
        """It should list all products from the database."""
        # Create multiple products
        product1 = ProductFactory()
        product1.id = None
        product1.create()
        product2 = ProductFactory()
        product2.id = None
        product2.create()
        # Retrieve and assert the total count is 2
        products = Product.all()
        self.assertEqual(len(products), 2)

    def test_find_by_name(self):
        """It should search for a product by name and return the correct result."""
        # Create two products with distinct names
        product1 = ProductFactory()
        product1.id = None
        product1.name = "UniqueProductName"
        product1.create()
        product2 = ProductFactory()
        product2.id = None
        product2.name = "DifferentProduct"
        product2.create()

        # Search for product1 by name, converting the query to a list
        results = Product.find_by_name("UniqueProductName").all()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "UniqueProductName")

    def test_find_by_category(self):
        """It should search for products by category and return the correct result."""
        # Create products with distinct categories
        product1 = ProductFactory()
        product1.id = None
        product1.category = Category.FOOD
        product1.create()
        product2 = ProductFactory()
        product2.id = None
        product2.category = Category.CLOTHS
        product2.create()

        results = Product.find_by_category(Category.FOOD).all()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].category, Category.FOOD)

    def test_find_by_availability(self):
        """It should search for a product by availability and return the correct result."""
        # Create two products with distinct availability
        product1 = ProductFactory()
        product1.id = None
        product1.available = True
        product1.create()
        product2 = ProductFactory()
        product2.id = None
        product2.available = False
        product2.create()

        results = Product.find_by_availability(True).all()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].available, True)
