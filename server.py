
import SimpleHTTPServer
import SocketServer

port = 1234
Handler = SimpleHTTPServer.SimpleHTTPRequestHandler

http = SocketServer.TCPServer(("", port), Handler)

print "SERVING WEBAPP ON PORT", port

http.serve_forever()
