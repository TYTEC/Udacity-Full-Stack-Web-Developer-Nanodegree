# Build web server 

# Import modules
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

# Handler Class
class WebServerHandler(BaseHTTPRequestHandler):
    # Handle all GET requests
    def do_GET(self):
        # Look for URL that ends with 'hello'
        if self.path.endswith("/hello"):
            # Send a response code 200 indicating a successful git request
            self.send_response(200)
            # Reply in form of html to client
            self.send_header('Content-type', 'text/html')
            # Send blank line
            self.end_headers()
            message = ""
            # Add message
            message += "<html><body>Hello!</body></html>"
            # Send message to the client
            self.wfile.write(message)
            print message
            return
        else:
            self.send_error(404, 'File Not Found: %s' % self.path)

# Main method 
def main():
    # Add try/except block
    try:
        # Define port
        port = 8080
        # Set host address to empty and specify port
        # Create webserver 
        server = HTTPServer(('', port), WebServerHandler)
        # Add print statement to see if the server is running
        print "Web Server running on port %s" % port
        # Keep listening until CTRL+C or exiting application
        server.serve_forever()
    # Add except
    except KeyboardInterrupt:
        print " ^C entered, stopping web server...."
        # Shut down server
        server.socket.close()

# Run main method when python executes the script
if __name__ == '__main__':
    main()