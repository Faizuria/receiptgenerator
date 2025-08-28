import http.server
import socketserver
import urllib.parse
import json
import subprocess
import sys
import os
from access_check import check_user_access

PORT = 3000

class AccessCheckHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Handle access check API requests
        if self.path.startswith('/check_access'):
            self.handle_access_check()
        else:
            # Serve static files
            super().do_GET()
    
    def handle_access_check(self):
        try:
            # Parse query parameters
            parsed_url = urllib.parse.urlparse(self.path)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            
            user_id = query_params.get('user_id', [None])[0]
            
            if not user_id:
                self.send_error_response('No user ID provided')
                return
            
            # Check user access
            access_result = check_user_access(user_id)
            
            # Send JSON response
            self.send_json_response(access_result)
            
        except Exception as e:
            self.send_error_response(f'Error checking access: {str(e)}')
    
    def send_json_response(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        response = json.dumps(data)
        self.wfile.write(response.encode('utf-8'))
    
    def send_error_response(self, message):
        self.send_response(400)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        error_data = {'error': message}
        response = json.dumps(error_data)
        self.wfile.write(response.encode('utf-8'))
    
    def do_OPTIONS(self):
        # Handle CORS preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def main():
    # Change to the directory containing the HTML files
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    with socketserver.TCPServer(("", PORT), AccessCheckHandler) as httpd:
        print(f"Server running at http://localhost:{PORT}")
        print(f"Dashboard: http://localhost:{PORT}/dashboard.html")
        print(f"Main page: http://localhost:{PORT}/Resellora.html")
        print("Press Ctrl+C to stop the server")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")

if __name__ == "__main__":
    main()
