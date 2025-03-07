# server.py
from http.server import BaseHTTPRequestHandler, HTTPServer
import socket


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

# Define a custom request handler class
class MyRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Set the response status code
        self.send_response(200)

        # Set the headers to tell the browser the response is HTML
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        # Write the custom HTML content in the response
        html_content = """
        <html>
            <head>
                <title>Custom Response</title>
            </head>
            <body>
                <h1>Welcome to My Custom Server!</h1>
                <p>This is a custom HTML response from the server.</p>
            </body>
        </html>
        """
        self.wfile.write(html_content.encode('utf-8'))

# Set up and start the HTTP server
def runserver(server_class=HTTPServer, handler_class=MyRequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting server on port {port}...")
    httpd.serve_forever()