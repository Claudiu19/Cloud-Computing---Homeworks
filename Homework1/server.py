from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
import json
import time
import os
import logging

clients = 0

f = open("metrics.txt", "r")
a = json.loads(f.read())
f.close()



def random(dict):
    request = {"jsonrpc":"2.0",
            "method":"generateIntegers",
            "params":{"apiKey":"f8acc21c-2f5c-415e-a017-46a9b15b48ae",
                      "n":1,
                      "min":1,
                      "max":807,
                      "replacement" : True,
                      "base":10},
            "id":9489}
    dict["random-request"] = ["https://api.random.org/json-rpc/1/invoke", request]
    response = requests.post("https://api.random.org/json-rpc/1/invoke", json = request)
    response.raise_for_status()
    json = response.json()
    dict["random-response"] = json
    number = json['result']['random']['data'][0]
    return number


def pokemon(n, dict, a):
    dict["pokemon-request"] = 'https://pokeapi.co/api/v2/pokemon/'
    start = time.time()
    response1 = requests.get('https://pokeapi.co/api/v2/pokemon/' + str(n))
    dict['pokemon-time'] = time.time()-start
    a['pokemon-average'] = (float((a['pokemon-average'])) + dict['pokemon-time']) / float(a["clients"])
    json_response1 = response1.json()
    dict['pokemon-response'] = json_response1

    dict['card-request'] = 'https://api.pokemontcg.io/v1/cards?name=' + json_response1['forms'][0]['name']
    start = time.time()
    response2 = requests.get('https://api.pokemontcg.io/v1/cards?name=' + json_response1['forms'][0]['name'])
    dict['card-time'] = time.time() - start
    a['card-average'] = (float((a['card-average'])) + dict['card-time']) / float(a["clients"])
    json_response2 = response2.json()
    dict['card-response'] = json_response2

    return json_response1['forms'][0]['name'], json_response2['cards'][0]['imageUrl']


class Serv(BaseHTTPRequestHandler):

    def do_GET(self):
        start = time.time()
        if self.path == '/':
            self.path = '/index.html'
            file_to_open = open(self.path[1:]).read()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(bytes(file_to_open, 'utf-8'))
        elif self.path == '/script.js':
            self.path = '/script.js'
            file_to_open = open(self.path[1:]).read()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(bytes(file_to_open, 'utf-8'))
        elif self.path == '/a':
            dict = {"Response time": "", "Request": self.path, "Response": "", "random-request": [], "random-response": {},
                    "pokemon-request": "", "pokemon-response": {}, "card-request" : "", "card-response": {}, "random-time": 0,
                    "pokemon-time": 0, "card-time": 0}
            a["clients"] = str(int(a["clients"]) + 1)
            start1 = time.time()
            n = random(dict)
            dict['random-time'] = time.time() - start1
            a['random-average'] = (float((a['random-average'])) + dict['random-time'])/float(a["clients"])
            result = pokemon(n, dict, a)
            result_json = json.dumps({"name": result[0][0].upper() + result[0][1:], "card": result[1], "number": str(n)})
            dict['Response'] = result_json
            self.send_response(200)
            self.send_header("Content-Type", 'text/plain')
            self.end_headers()
            self.wfile.write(bytes(result_json, 'utf-8'))
            dict['Response time'] = str(time.time() - start)
            a['total-average'] = (float((a['total-average'])) + float(dict['Response time'])) / float(a["clients"])
            done = 0
            while done == 0:
                try:
                    os.rename("logs.txt", "logs.txt")
                    f = open('logs.txt', 'a+')
                    f.write(json.dumps(dict) + "\n\n")
                    f.close()
                    done = 1
                except OSError as e:
                    pass
            done = 0
            while done == 0:
                try:
                    os.rename("metrics.txt", "metrics.txt")
                    f = open('metrics.txt', 'w+')
                    f.write(json.dumps(a))
                    f.close()
                    done = 1
                except OSError as e:
                    pass
        elif self.path == '/metrics':
            self.path = '/metrics.txt'
            file_to_open = open(self.path[1:]).read()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(bytes(file_to_open, 'utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(bytes("File not found", 'utf-8'))


httpd = HTTPServer(('localhost', 8000), Serv)
httpd.serve_forever()