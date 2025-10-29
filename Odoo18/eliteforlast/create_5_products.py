import xmlrpc.client
import sys

# Configuration - Update these values if needed
URL = 'http://localhost:8018'
DB = 'fresh_db'
USERNAME = 'admin'
PASSWORD = 'admin'


def create_demo_products():
    """Create 5 demo products using Odoo XML-RPC API"""

    print("=== Odoo Demo Products Creator ===")
    print(f"URL: {URL}")
    print(f"Database: {DB}")
    print(f"Username: {USERNAME}")
    print("-" * 50)

    try:
        # Step 1: Connect to Odoo common endpoint
        print("🔗 Connecting to Odoo...")
        common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')

        # Step 2: Authenticate
        print("🔐 Authenticating...")
        uid = common.authenticate(DB, USERNAME, PASSWORD, {})

        if not uid:
            print("❌ Authentication failed!")
            print("Please check:")
            print("- Odoo server is running")
            print("- Database name is correct")
            print("- Username and password are correct")
            return False

        print(f"✅ Authentication successful! User ID: {uid}")

        # Step 3: Connect to object endpoint
        models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')

        # Step 4: Define demo products
        products = [
            {
                'name': 'MacBook Pro 16"',
                'list_price': 2499.00,
                'type': 'product',
                'description': 'High-performance laptop with M2 Pro chip',
                'description_sale': 'Perfect for developers and creative professionals'
            },
            {
                'name': 'iPhone 15 Pro',
                'list_price': 999.00,
                'type': 'product',
                'description': 'Latest iPhone with titanium design and A17 Pro chip',
                'description_sale': 'Advanced camera system and Action Button'
            },
            {
                'name': 'iPad Air',
                'list_price': 599.00,
                'type': 'product',
                'description': 'Powerful tablet with M1 chip and 10.9-inch display',
                'description_sale': 'Perfect for creativity and productivity'
            },
            {
                'name': 'AirPods Pro',
                'list_price': 249.00,
                'type': 'product',
                'description': 'Active noise cancellation wireless earbuds',
                'description_sale': 'Spatial audio and adaptive transparency'
            },
            {
                'name': 'Apple Watch Series 9',
                'list_price': 399.00,
                'type': 'product',
                'description': 'Advanced health and fitness tracking smartwatch',
                'description_sale': 'Double tap gesture and S9 SiP technology'
            }
        ]

        # Step 5: Create products
        print(f"\n📦 Creating {len(products)} demo products...")
        created_products = []
        failed_products = []

        for i, product_data in enumerate(products, 1):
            try:
                print(f"  [{i}/{len(products)}] Creating: {product_data['name']}")

                product_id = models.execute_kw(
                    DB, uid, PASSWORD,
                    'product.template', 'create',
                    [product_data]
                )

                created_products.append({
                    'id': product_id,
                    'name': product_data['name'],
                    'price': product_data['list_price']
                })

                print(f"      ✅ Success! Product ID: {product_id}")

            except Exception as e:
                print(f"      ❌ Failed: {e}")
                failed_products.append({
                    'name': product_data['name'],
                    'error': str(e)
                })

        # Step 6: Display results
        print("\n" + "=" * 50)
        print("📊 CREATION SUMMARY")
        print("=" * 50)

        if created_products:
            print(f"✅ Successfully created {len(created_products)} products:")
            for product in created_products:
                print(f"   • {product['name']} - ${product['price']:.2f} (ID: {product['id']})")

        if failed_products:
            print(f"\n❌ Failed to create {len(failed_products)} products:")
            for product in failed_products:
                print(f"   • {product['name']}: {product['error']}")

        print(f"\n🎉 Process completed! {len(created_products)}/{len(products)} products created successfully.")

        if created_products:
            print("\n📍 Next steps:")
            print("1. Go to Odoo web interface")
            print("2. Navigate to: Inventory > Products > Products")
            print("3. You should see your new demo products listed")

        return len(created_products) > 0

    except xmlrpc.client.ProtocolError as e:
        print(f"❌ Connection error: {e}")
        print("Make sure Odoo server is running and accessible")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_connection():
    """Test connection to Odoo server"""
    try:
        print("🧪 Testing connection...")
        common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
        version = common.version()
        print(f"✅ Connected to Odoo {version.get('server_version', 'Unknown')}")
        return True
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False


if __name__ == '__main__':
    # Test connection first
    if test_connection():
        # Create products
        success = create_demo_products()

        if success:
            print("\n🚀 All done! Your demo products are ready to use.")
        else:
            print("\n⚠️  Some issues occurred. Please check the errors above.")
            sys.exit(1)
    else:
        print("\n⚠️  Cannot connect to Odoo. Please check your configuration.")
        sys.exit(1)
