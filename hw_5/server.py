import http.server

port = 8080

addrport = ('', port)

serv = http.server.HTTPServer(
    addrport,
    http.server.CGIHTTPRequestHandler
)
serv.serve_forever()
