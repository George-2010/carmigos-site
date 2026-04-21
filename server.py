import http.server
import socketserver
import json
import urllib.parse
from pymongo import MongoClient

PORT = 3000

# ==============================================================================
# 🚀 MONGODB ATLAS CONNECTION STRING
# ==============================================================================
# Replace this entire string with your actual Free MongoDB Atlas connection string.
# Example: "mongodb+srv://testuser:MySecretPassword@cluster0.abcd.mongodb.net/?retryWrites=true&w=majority"
MONGO_URI = "PASTE_YOUR_MONGODB_CONNECTION_STRING_HERE"
# ==============================================================================

# Database Setup & Connecting
use_mongo = False
try:
    if "mongodb+srv" in MONGO_URI and "<password>" not in MONGO_URI:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping') # Test connection
        db = client['carmigos']
        products_collection = db['products']
        use_mongo = True
        print("\n✅ Successfully connected to MongoDB Atlas Cloud!")
    else:
        print("\n⚠️ MongoDB URI not configured yet. Running in Local Memory fallback mode.")
except Exception as e:
    print(f"\n❌ MongoDB Connection Error. Check your URI string. Error: {e}")
    print("⚠️ Running in Local Memory fallback mode.")

# Fallback Local Memory (Used if MongoDB isn't active yet)
local_products = [
    { "id": 1, "title": "Apex Carbon Fiber Spoiler", "category": "Exterior", "price": 499.00, "image": "assets/product_brakes.png" },
    { "id": 2, "title": "Neon Nova Interior LED Kit", "category": "Illumination", "price": 89.99, "image": "assets/product_lights.png" },
    { "id": 3, "title": "Forged Alloy Wheels 19\"", "category": "Exterior", "price": 1249.00, "image": "assets/product_wheels.png" },
    { "id": 4, "title": "Recaro Racing Seats", "category": "Interior", "price": 850.00, "image": "assets/product_seats.png" }
]
cart = []

class CustomAPIHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        
        # REST Endpoint: GET Products
        if parsed_path.path == '/api/products':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            if use_mongo:
                # Fetch dynamically from MongoDB Atlas
                mongo_items = list(products_collection.find({}, {"_id": 0}))
                self.wfile.write(json.dumps(mongo_items).encode('utf-8'))
            else:
                self.wfile.write(json.dumps(local_products).encode('utf-8'))
            return
            
        # Serve Static Frontend Files otherwise
        return super().do_GET()

    def do_POST(self):
        parsed_path = urllib.parse.urlparse(self.path)
        
        # REST Endpoint: POST item to Cart
        if parsed_path.path == '/api/cart':
            content_length = int(self.headers['Content-Length'])
            item = json.loads(self.rfile.read(content_length).decode('utf-8'))
            cart.append(item)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"message": "Added securely", "cart_size": len(cart)}).encode('utf-8'))
            return

        # REST Endpoint: POST new product (Admin Dashboard)
        if parsed_path.path == '/api/products':
            try:
                content_length = int(self.headers['Content-Length'])
                new_product = json.loads(self.rfile.read(content_length).decode('utf-8'))
                
                if use_mongo:
                    # Save permanently to MongoDB Cloud
                    highest_id = products_collection.find_one(sort=[("id", -1)])
                    new_product['id'] = (highest_id['id'] + 1) if highest_id else 1
                    products_collection.insert_one(new_product)
                    del new_product['_id'] # Remove object ID for JSON response
                else:
                    new_id = max([p['id'] for p in local_products]) + 1 if local_products else 1
                    new_product['id'] = new_id
                    local_products.append(new_product)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"message": "Product added!", "product": new_product}).encode('utf-8'))
            except Exception as e:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
            return

        self.send_response(404)
        self.end_headers()

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), CustomAPIHandler) as httpd:
        print(f"=========================================")
        print(f"Server Route: http://localhost:{PORT}")
        print(f"Database: {'⚡ MONGODB ATLAS CLOUD' if use_mongo else '🔋 IN-MEMORY LOCAL MODE'}")
        print(f"=========================================")
        httpd.serve_forever()
