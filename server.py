#! /usr/bin/python3.6
import http.server, os, socketserver, ssl, json, shutil, sqlite3
from datetime import datetime

PORT = 80
DIR = '/home/joe/sql_server_querier/'
HTML_LOC = './index.html'

os.chdir(DIR)

#cat setup | sqlite3 thedatabase.db

def execute_sql(comm):
    db = sqlite3.connect('thedatabase.db')
    c = db.cursor()
    try:
        c.execute(comm)
        db.commit()
    except sqlite3.Error as e:
        return json.dumps(e.args[0])
    try:
        headers = [m[0] for m in c.description]
    except:
        return '"no table returned"'
    return json.dumps([headers, *c.fetchall()])

class Handler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length'])).decode('utf-8')
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        print(data)
        msg = execute_sql(data)
        self.wfile.write(msg.encode('utf-8'))
    def do_GET(self):
        #just serves some server status things for me
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        shutil.copyfileobj(open(HTML_LOC,'rb'), self.wfile)
    def log_message(self, *_):
        pass

print('serving on port', PORT)
socketserver.TCPServer.allow_reuse_address = 1
with socketserver.TCPServer(('',PORT), Handler) as httpd:
    #httpd.socket = ssl.wrap_socket(httpd.socket,
    #                               certfile='/etc/letsencrypt/live/joe.iddon.com/fullchain.pem',
    #                               keyfile ='/etc/letsencrypt/live/joe.iddon.com/privkey.pem',
    #                               server_side=True)
    httpd.serve_forever()
