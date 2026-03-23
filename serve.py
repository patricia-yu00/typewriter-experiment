import http.server
import socketserver
import os

PORT = 4242
DIR = "/Users/patriciay/Desktop/Personal projects/typewriter-project-2"

os.chdir(DIR)

Handler = http.server.SimpleHTTPRequestHandler
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    httpd.serve_forever()
