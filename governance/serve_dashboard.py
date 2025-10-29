"""
Simple HTTP server to serve the governance dashboard
"""

import http.server
import socketserver
import os
import sys

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def end_headers(self):
        # Add CORS headers to allow local file access
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

if __name__ == '__main__':
    # Check if dashboard_data.json exists
    data_file = os.path.join(DIRECTORY, 'dashboard_data.json')
    if not os.path.exists(data_file):
        print("⚠️  Warning: dashboard_data.json not found!")
        print("📊 Please run: python governance/fetch_dashboard_data.py")
        print()
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(0)
    
    print("=" * 60)
    print("🚀 MLOps Governance Dashboard Server")
    print("=" * 60)
    print(f"📂 Serving from: {DIRECTORY}")
    print(f"🌐 Dashboard URL: http://localhost:{PORT}/dashboard.html")
    print(f"📊 Data file: {'✅ Found' if os.path.exists(data_file) else '❌ Missing'}")
    print("=" * 60)
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    print()
    
    try:
        with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("🛑 Server stopped.")
        print("=" * 60)
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"\n❌ Error: Port {PORT} is already in use!")
            print(f"💡 Try a different port or stop the other server.")
        else:
            print(f"\n❌ Error: {e}")
