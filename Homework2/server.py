from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sqlite3
from urllib.parse import urlparse
from urllib.parse import parse_qs
from urllib.parse import urlencode
import secrets


conn = sqlite3.connect('magazin.db')
class Serv(BaseHTTPRequestHandler):

    def do_GET(self):
        o = urlparse(self.path)
        if o.path == '/category':
            result = dict()
            query = parse_qs(o.query)
            if len(query) == 0:
                result.update({'Error': 'Our categories can only be identified by id or name'})
                result_json = json.dumps(result)
                self.send_response(400, "Bad parameters")
                self.send_header("Content-Type", 'text/plain')
                self.end_headers()
                self.wfile.write(bytes(result_json, 'utf-8'))
            else:
                print(query)
                if 'id' in query:
                    b = query['id']
                    print(b)
                    a = list(conn.execute('Select * FROM categories WHERE cat_id = ?', (int(b[0]),)))
                    print(a)
                    if len(a) == 0:
                        result.update({'Error': 'No category with this id'})
                        result_json = json.dumps(result)
                        self.send_response(404, "Not found")
                        self.send_header("Content-Type", 'text/plain')
                        self.end_headers()
                        self.wfile.write(bytes(result_json, 'utf-8'))
                    else:
                        result.update({'Category': a[0][0], 'Id': a[0][1]})
                        result_json = json.dumps(result)
                        self.send_response(200,"OK")
                        self.send_header("Content-Type", 'text/plain')
                        self.end_headers()
                        self.wfile.write(bytes(result_json,'utf-8'))
                elif 'category' in query:
                    b = query['category']
                    a = list(conn.execute('Select * FROM categories WHERE name =?', ((b[0]),)))
                    if len(a) == 0:
                        result.update({'Error': 'No category with this name'})
                        result_json = json.dumps(result)
                        self.send_response(404, "Item not found")
                        self.send_header("Content-Type", 'text/plain')
                        self.end_headers()
                        self.wfile.write(bytes(result_json, 'utf-8'))
                    else:
                        result.update({'Category': a[0][0], 'Id': a[0][1]})
                        result_json = json.dumps(result)
                        self.send_response(200, "OK")
                        self.send_header("Content-Type", 'text/plain')
                        self.end_headers()
                        self.wfile.write(bytes(result_json, 'utf-8'))
                else:
                    result.update({'Error': 'Our categories can only be identified by id or name'})
                    result_json = json.dumps(result)
                    self.send_response(400, "Bad parameters")
                    self.send_header("Content-Type", 'text/plain')
                    self.end_headers()
                    self.wfile.write(bytes(result_json, 'utf-8'))
        elif o.path == '/categories':
            a = list(conn.execute('Select * FROM categories'))
            result = dict()
            for i in range(0, len(a)):
                cat = {'Category': a[i][0], 'Id': a[i][1]}
                result.update({str(i+1): cat})
            result_json = json.dumps(result)
            self.send_response(200, "OK")
            self.send_header("Content-Type", 'text/plain')
            self.end_headers()
            self.wfile.write(bytes(result_json, 'utf-8'))
        elif o.path == '/products':
            query = parse_qs(o.query)
            if len(query) == 0:
                a = list(conn.execute('Select name, product_id FROM products'))
                result = dict()
                for i in range(0, len(a)):
                    res = {'Name': a[i][0], 'Product Id': a[i][1]}
                    result.update({str(i + 1): res})
                result_json = json.dumps(result)
                self.send_response(200, "OK")
                self.send_header("Content-Type", 'text/plain')
                self.end_headers()
                self.wfile.write(bytes(result_json, 'utf-8'))
            elif "category_id" in query:
                b = query['category_id']
                a = list(conn.execute('Select name, product_id FROM products WHERE cat_id =?', ((int(b[0])),)))
                result = dict()
                for i in range(0, len(a)):
                    res = {'Name': a[i][0], 'Product Id': a[i][1]}
                    result.update({str(i + 1): res})
                if len(result) == 0:
                    result.update({'Error': 'No category with this id'})
                    result_json = json.dumps(result)
                    self.send_response(404, "Not found")
                    self.send_header("Content-Type", 'text/plain')
                    self.end_headers()
                    self.wfile.write(bytes(result_json, 'utf-8'))
                else:
                    result_json = json.dumps(result)
                    self.send_response(200, "OK")
                    self.send_header("Content-Type", 'text/plain')
                    self.end_headers()
                    self.wfile.write(bytes(result_json, 'utf-8'))
            else:
                result = dict()
                result.update({'Error': 'Invalid query string parameters'})
                result_json = json.dumps(result)
                self.send_response(400, "Bad parameters")
                self.send_header("Content-Type", 'text/plain')
                self.end_headers()
                self.wfile.write(bytes(result_json, 'utf-8'))
        elif o.path == '/product':
            result = dict()
            query = parse_qs(o.query)
            if len(query) == 0:
                result.update({'Error': 'Our products can only be identified by id'})
                result_json = json.dumps(result)
                self.send_response(400, "No parameters")
                self.send_header("Content-Type", 'text/plain')
                self.end_headers()
                self.wfile.write(bytes(result_json, 'utf-8'))
            elif "product_id" in query:
                b = query['product_id']
                a = list(conn.execute('Select * FROM products WHERE product_id =?', (int(b[0]),)))
                if len(a) != 0:
                    result = dict()
                    for i in range(0, len(a)):
                        cat = list(conn.execute('Select name FROM categories WHERE cat_id =?', (int(a[i][1]),)))
                        res = {'Name': a[i][0], 'Category': cat, 'Product Id': a[i][2], 'Price': a[i][3], 'Description': a[i][4]}
                        result.update({str(i + 1): res})
                    result_json = json.dumps(result)
                    self.send_response(200, "OK")
                    self.send_header("Content-Type", 'text/plain')
                    self.end_headers()
                    self.wfile.write(bytes(result_json, 'utf-8'))
                else:
                    result.update({'Error': 'No product with this id'})
                    result_json = json.dumps(result)
                    self.send_response(404, "Not found")
                    self.send_header("Content-Type", 'text/plain')
                    self.end_headers()
                    self.wfile.write(bytes(result_json, 'utf-8'))
            else:
                result.update({'Error': 'Our products can only be identified by id'})
                result_json = json.dumps(result)
                self.send_response(400, "Bad parameters")
                self.send_header("Content-Type", 'text/plain')
                self.end_headers()
                self.wfile.write(bytes(result_json, 'utf-8'))
        else:
            result = dict()
            result.update({'Error': 'No such GET path is implemented'})
            result_json = json.dumps(result)
            self.send_response(501, "Bad path")
            self.send_header("Content-Type", 'text/plain')
            self.end_headers()
            self.wfile.write(bytes(result_json, 'utf-8'))


    def do_POST(self):
        done = 0
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            post_data_dict = json.loads(str(post_data, encoding='utf-8'))
        except:
            done = 1
            result = {"Error": "Invalid data format, only JSON is accepted"}
            result_json = json.dumps(result)
            self.send_response(415, "Invalid Format")
            self.send_header("Content-Type", 'text/plain')
            self.end_headers()
            self.wfile.write(bytes(result_json, 'utf-8'))

        if done == 0:


            if self.path == '/login':
                if 'user' in post_data_dict and 'pass' in post_data_dict:
                    a = list(conn.execute('Select user_id FROM users WHERE username =? AND password =?', (post_data_dict["user"],post_data_dict["pass"])))
                    if len(a) == 0:
                        result = {"ERROR": "Wrong username or password"}
                        result_json = json.dumps(result)
                        self.send_response(401, "Invalid credentials")
                        self.send_header("Content-Type", 'text/plain')
                        self.end_headers()
                        self.wfile.write(bytes(result_json, 'utf-8'))
                    else:
                        b = list(conn.execute('Select auth_token FROM logged_users WHERE user_id = ?', (int(a[0][0]),)))
                        if len(b) == 0:
                            auth_token = secrets.randbits(32)
                            conn.execute("INSERT INTO logged_users VALUES (?, ?)", (int(a[0][0]),auth_token))
                            conn.commit()
                            result = {"auth_token": auth_token}
                            result_json = json.dumps(result)
                            self.send_response(210, "Created")
                            self.send_header("Content-Type", 'text/plain')
                            self.end_headers()
                            self.wfile.write(bytes(result_json, 'utf-8'))
                        else:
                            result = {"auth_token": b[0][0]}
                            result_json = json.dumps(result)
                            self.send_response(200, "OK")
                            self.send_header("Content-Type", 'text/plain')
                            self.end_headers()
                            self.wfile.write(bytes(result_json, 'utf-8'))
                else:
                    result = {"ERROR": "Parameters not valid"}
                    result_json = json.dumps(result)
                    self.send_response(404, "Not Found")
                    self.send_header("Content-Type", 'text/plain')
                    self.end_headers()
                    self.wfile.write(bytes(result_json, 'utf-8'))



            elif self.path == '/add_category':
                if 'auth_token' in post_data_dict:
                    a = list(conn.execute('Select user_id FROM logged_users WHERE auth_token = ?', (int(post_data_dict['auth_token']),)))
                    if len(a) == 0:
                        result = {"ERROR": "Invalid authentification token"}
                        result_json = json.dumps(result)
                        self.send_response(401, "Invalid token")
                        self.send_header("Content-Type", 'text/plain')
                        self.end_headers()
                        self.wfile.write(bytes(result_json, 'utf-8'))
                    else:
                        if 'cat_name' in post_data_dict and 'cat_id' in post_data_dict:
                            if list(conn.execute('Select cat_id FROM categories WHERE name = ?', (post_data_dict['cat_name'],))) != []:
                                result = {"ERROR": "Category name already exists"}
                                result_json = json.dumps(result)
                                self.send_response(409, "Already Exists")
                                self.send_header("Content-Type", 'text/plain')
                                self.end_headers()
                                self.wfile.write(bytes(result_json, 'utf-8'))
                            elif list(conn.execute('Select name FROM categories WHERE cat_id = ?', ((int(post_data_dict['cat_id'])), ))) != []:
                                result = {"ERROR": "Category id already exists"}
                                result_json = json.dumps(result)
                                self.send_response(409, "Already Exists")
                                self.send_header("Content-Type", 'text/plain')
                                self.end_headers()
                                self.wfile.write(bytes(result_json, 'utf-8'))
                            else:
                                conn.execute("INSERT INTO categories VALUES (?, ?)",(post_data_dict['cat_name'], (int(post_data_dict['cat_id']))))
                                conn.commit()
                                result = {"Message": "Category created"}
                                result_json = json.dumps(result)
                                self.send_response(210, "Resource created")
                                self.send_header("Content-Type", 'text/plain')
                                self.end_headers()
                                self.wfile.write(bytes(result_json, 'utf-8'))
                        else:
                            result = {"ERROR": "Category name or id not provided"}
                            result_json = json.dumps(result)
                            self.send_response(400, "Invalid Parameters")
                            self.send_header("Content-Type", 'text/plain')
                            self.end_headers()
                            self.wfile.write(bytes(result_json, 'utf-8'))
                else:
                    result = {"ERROR": "Request requires an auth_token"}
                    result_json = json.dumps(result)
                    self.send_response(400, "Resource created")
                    self.send_header("Content-Type", 'text/plain')
                    self.end_headers()
                    self.wfile.write(bytes(result_json, 'utf-8'))
            else:
                result = dict()
                result.update({'Error': 'No such POST path is implemented'})
                result_json = json.dumps(result)
                self.send_response(501, "Bad path")
                self.send_header("Content-Type", 'text/plain')
                self.end_headers()
                self.wfile.write(bytes(result_json, 'utf-8'))

    def do_PUT(self):
        done1 = 0
        done2 = 0
        try:
            content_length = int(self.headers['Content-Length'])
            put_data = self.rfile.read(content_length)
            put_data_dict = json.loads(str(put_data, encoding='utf-8'))
        except:
            done1 = 1
            result = {"Error": "Invalid data format, only JSON is accepted"}
            result_json = json.dumps(result)
            self.send_response(415, "Invalid format")
            self.send_header("Content-Type", 'text/plain')
            self.end_headers()
            self.wfile.write(bytes(result_json, 'utf-8'))

        if "auth_token" not in put_data_dict:
            done2 = 1
            result = {"ERROR": "Auth_token not provided"}
            result_json = json.dumps(result)
            self.send_response(400, "Invalid Parameters")
            self.send_header("Content-Type", 'text/plain')
            self.end_headers()
            self.wfile.write(bytes(result_json, 'utf-8'))

        if done1 == 0 and done2 == 0:
            a = list(conn.execute('Select user_id FROM logged_users WHERE auth_token = ?',
                                  (int(put_data_dict['auth_token']),)))
            if self.path == '/modify_price':
                if len(a) == 0:
                    result = {"ERROR": "Invalid authentification token"}
                    result_json = json.dumps(result)
                    self.send_response(401, "Invalid token")
                    self.send_header("Content-Type", 'text/plain')
                    self.end_headers()
                    self.wfile.write(bytes(result_json, 'utf-8'))
                else:
                    b = list(conn.execute('Select auth_level FROM users WHERE user_id = ?', (int(a[0][0]),)))
                    if(int(b[0][0])) < 2:
                        result = {"ERROR": "Not authorized to perform this operation"}
                        result_json = json.dumps(result)
                        self.send_response(401, "Unauthorized")
                        self.send_header("Content-Type", 'text/plain')
                        self.end_headers()
                        self.wfile.write(bytes(result_json, 'utf-8'))
                    else:
                        if 'prod_id' not in put_data_dict or 'new_price' not in put_data_dict:
                            result = {"ERROR": "Parameters not valid"}
                            result_json = json.dumps(result)
                            self.send_response(404, "Not Found")
                            self.send_header("Content-Type", 'text/plain')
                            self.end_headers()
                            self.wfile.write(bytes(result_json, 'utf-8'))
                        else:
                            cursor = conn.cursor()
                            cursor.execute('''UPDATE products SET price = ? WHERE product_id = ?''',(int(put_data_dict['new_price']), int(put_data_dict['prod_id'])))
                            conn.commit()
                            result = {"Message": "Update sucesfull"}
                            result_json = json.dumps(result)
                            self.send_response(200, "OK")
                            self.send_header("Content-Type", 'text/plain')
                            self.end_headers()
                            self.wfile.write(bytes(result_json, 'utf-8'))
            elif self.path == '/modify_auth_level':
                if len(a) == 0:
                    result = {"ERROR": "Invalid authentification token"}
                    result_json = json.dumps(result)
                    self.send_response(401, "Invalid token")
                    self.send_header("Content-Type", 'text/plain')
                    self.end_headers()
                    self.wfile.write(bytes(result_json, 'utf-8'))
                else:
                    b = list(conn.execute('Select auth_level FROM users WHERE user_id = ?', (int(a[0][0]),)))
                    if (int(b[0][0])) < 3:
                        result = {"ERROR": "Not authorized to perform this operation"}
                        result_json = json.dumps(result)
                        self.send_response(401, "Unauthorized")
                        self.send_header("Content-Type", 'text/plain')
                        self.end_headers()
                        self.wfile.write(bytes(result_json, 'utf-8'))
                    else:
                        if 'user_id' not in put_data_dict or 'new_auth_level' not in put_data_dict:
                            result = {"ERROR": "Parameters not valid"}
                            result_json = json.dumps(result)
                            self.send_response(404, "Not Found")
                            self.send_header("Content-Type", 'text/plain')
                            self.end_headers()
                            self.wfile.write(bytes(result_json, 'utf-8'))
                        else:
                            c = list(conn.execute('Select auth_level FROM users WHERE user_id = ?', (int(put_data_dict['user_id']),)))
                            if len(c) == 0:
                                result = {"ERROR": "User not found"}
                                result_json = json.dumps(result)
                                self.send_response(404, "Not found")
                                self.send_header("Content-Type", 'text/plain')
                                self.end_headers()
                                self.wfile.write(bytes(result_json, 'utf-8'))
                            else:
                                cursor = conn.cursor()
                                cursor.execute('''UPDATE users SET auth_level = ? WHERE user_id = ?''',
                                               (int(put_data_dict['new_auth_level']), int(put_data_dict['user_id'])))
                                conn.commit()
                                result = {"Message": "Update sucesfull"}
                                result_json = json.dumps(result)
                                self.send_response(200, "OK")
                                self.send_header("Content-Type", 'text/plain')
                                self.end_headers()
                                self.wfile.write(bytes(result_json, 'utf-8'))
            else:
                result = dict()
                result.update({'Error': 'No such PUT path is implemented'})
                result_json = json.dumps(result)
                self.send_response(501, "Bad path")
                self.send_header("Content-Type", 'text/plain')
                self.end_headers()
                self.wfile.write(bytes(result_json, 'utf-8'))


    def do_DELETE(self):
        done1 = 0
        done2 = 0
        try:
            content_length = int(self.headers['Content-Length'])
            delete_data = self.rfile.read(content_length)
            delete_data_dict = json.loads(str(delete_data, encoding='utf-8'))
        except:
            done1 = 1
            result = {"Error": "Invalid data format, only JSON is accepted"}
            result_json = json.dumps(result)
            self.send_response(400, "Created")
            self.send_header("Content-Type", 'text/plain')
            self.end_headers()
            self.wfile.write(bytes(result_json, 'utf-8'))

        if "auth_token" not in delete_data_dict:
            done2 = 1
            result = {"ERROR": "Auth_token not provided"}
            result_json = json.dumps(result)
            self.send_response(400, "Invalid Parameters")
            self.send_header("Content-Type", 'text/plain')
            self.end_headers()
            self.wfile.write(bytes(result_json, 'utf-8'))

        if done1 == 0 and done2 == 0:
            a = list(conn.execute('Select user_id FROM logged_users WHERE auth_token = ?',
                                  (int(delete_data_dict['auth_token']),)))
            if self.path == '/delete_user':
                if len(a) == 0:
                    result = {"ERROR": "Invalid authentification token"}
                    result_json = json.dumps(result)
                    self.send_response(401, "Invalid token")
                    self.send_header("Content-Type", 'text/plain')
                    self.end_headers()
                    self.wfile.write(bytes(result_json, 'utf-8'))
                else:
                    b = list(conn.execute('Select auth_level FROM users WHERE user_id = ?', (int(a[0][0]),)))
                    if (int(b[0][0])) < 3:
                        result = {"ERROR": "Not authorized to perform this operation"}
                        result_json = json.dumps(result)
                        self.send_response(401, "Unauthorized")
                        self.send_header("Content-Type", 'text/plain')
                        self.end_headers()
                        self.wfile.write(bytes(result_json, 'utf-8'))
                    else:
                        if "user_id" not in delete_data_dict:
                            result = {"ERROR": "User id not provided"}
                            result_json = json.dumps(result)
                            self.send_response(400, "Invalid Parameters")
                            self.send_header("Content-Type", 'text/plain')
                            self.end_headers()
                            self.wfile.write(bytes(result_json, 'utf-8'))
                        else:
                            c = list(conn.execute('Select auth_level FROM users WHERE user_id = ?', (int(delete_data_dict['user_id']),)))
                            # print(len(c))
                            if len(c) > 0:
                                conn.execute("Delete from users where user_id = ?", (int(delete_data_dict['user_id']),))
                                conn.commit()
                                result = {"Message": "User deleted"}
                                result_json = json.dumps(result)
                                self.send_response(200, "OK")
                                self.send_header("Content-Type", 'text/plain')
                                self.end_headers()
                                self.wfile.write(bytes(result_json, 'utf-8'))
                            else:
                                print(len(c))
                                result = {"Message": "User does not exist"}
                                result_json = json.dumps(result)
                                self.send_response(404, "Not found")
                                self.send_header("Content-Type", 'text/plain')
                                self.end_headers()
                                self.wfile.write(bytes(result_json, 'utf-8'))
            elif self.path == '/delete_product':
                if len(a) == 0:
                    result = {"ERROR": "Invalid authentification token"}
                    result_json = json.dumps(result)
                    self.send_response(401, "Invalid token")
                    self.send_header("Content-Type", 'text/plain')
                    self.end_headers()
                    self.wfile.write(bytes(result_json, 'utf-8'))
                else:
                    b = list(conn.execute('Select auth_level FROM users WHERE user_id = ?', (int(a[0][0]),)))
                    if (int(b[0][0])) < 2:
                        result = {"ERROR": "Not authorized to perform this operation"}
                        result_json = json.dumps(result)
                        self.send_response(401, "Unauthorized")
                        self.send_header("Content-Type", 'text/plain')
                        self.end_headers()
                        self.wfile.write(bytes(result_json, 'utf-8'))
                    else:
                        if "product_id" not in delete_data_dict:
                            result = {"ERROR": "Product id not provided"}
                            result_json = json.dumps(result)
                            self.send_response(400, "Invalid Parameters")
                            self.send_header("Content-Type", 'text/plain')
                            self.end_headers()
                            self.wfile.write(bytes(result_json, 'utf-8'))
                        else:
                            c = list(conn.execute('Select name FROM products WHERE product_id = ?', (int(delete_data_dict['product_id']),)))
                            # print(len(c))
                            if len(c) > 0:
                                conn.execute("Delete from products where product_id = ?", (int(delete_data_dict['product_id']),))
                                conn.commit()
                                result = {"Message": "Product deleted"}
                                result_json = json.dumps(result)
                                self.send_response(200, "OK")
                                self.send_header("Content-Type", 'text/plain')
                                self.end_headers()
                                self.wfile.write(bytes(result_json, 'utf-8'))
                            else:
                                result = {"Error": "Product does not exist"}
                                result_json = json.dumps(result)
                                self.send_response(404, "Not found")
                                self.send_header("Content-Type", 'text/plain')
                                self.end_headers()
                                self.wfile.write(bytes(result_json, 'utf-8'))
            elif self.path == '/delete_category':
                if len(a) == 0:
                    result = {"ERROR": "Invalid authentification token"}
                    result_json = json.dumps(result)
                    self.send_response(401, "Invalid token")
                    self.send_header("Content-Type", 'text/plain')
                    self.end_headers()
                    self.wfile.write(bytes(result_json, 'utf-8'))
                else:
                    b = list(conn.execute('Select auth_level FROM users WHERE user_id = ?', (int(a[0][0]),)))
                    if (int(b[0][0])) < 2:
                        result = {"ERROR": "Not authorized to perform this operation"}
                        result_json = json.dumps(result)
                        self.send_response(401, "Unauthorized")
                        self.send_header("Content-Type", 'text/plain')
                        self.end_headers()
                        self.wfile.write(bytes(result_json, 'utf-8'))
                    else:
                        if "cat_id" not in delete_data_dict:
                            result = {"ERROR": "Category id not provided"}
                            result_json = json.dumps(result)
                            self.send_response(400, "Invalid Parameters")
                            self.send_header("Content-Type", 'text/plain')
                            self.end_headers()
                            self.wfile.write(bytes(result_json, 'utf-8'))
                        else:
                            c = list(conn.execute('Select name FROM categories WHERE cat_id = ?', (int(delete_data_dict['cat_id']),)))
                            # print(len(c))
                            if len(c) > 0:
                                conn.execute("Delete from categories where cat_id = ?", (int(delete_data_dict['cat_id']),))
                                conn.execute("Delete from products where cat_id = ?", (int(delete_data_dict['cat_id']),))
                                conn.commit()
                                result = {"Message": "Category and products deleted"}
                                result_json = json.dumps(result)
                                self.send_response(200, "OK")
                                self.send_header("Content-Type", 'text/plain')
                                self.end_headers()
                                self.wfile.write(bytes(result_json, 'utf-8'))
                            else:
                                result = {"Error": "Category does not exist"}
                                result_json = json.dumps(result)
                                self.send_response(404, "Not found")
                                self.send_header("Content-Type", 'text/plain')
                                self.end_headers()
                                self.wfile.write(bytes(result_json, 'utf-8'))
            else:
                result = dict()
                result.update({'Error': 'No such DELETE path is implemented'})
                result_json = json.dumps(result)
                self.send_response(501, "Bad path")
                self.send_header("Content-Type", 'text/plain')
                self.end_headers()
                self.wfile.write(bytes(result_json, 'utf-8'))









httpd = HTTPServer(('127.0.0.1', 8000), Serv)
httpd.serve_forever()
