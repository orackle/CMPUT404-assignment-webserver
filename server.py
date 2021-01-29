#  coding: utf-8
import socketserver
import os.path
import time
import os
# Copyright 2021 Abram Hindle, Eddie Antonio Santos, Debangana Ghosh
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):

    def handle(self):
        """
        Handles the request sent to server and sends out an HTTP response
        HTTP Response is sent to client using a bytearray
        """
        self.data = self.request.recv(1024).strip()
        request_string = self.data.decode('utf-8')
        check_status = request_string.split(" ")

        # create response handler
        http_response = self.check_405(check_status)
        if not http_response:
            http_response = self.check_404(check_status)
        self.request.sendall(bytearray(http_response,'utf-8')) # serving the response to the server

    def check_405(self, request):
        """
        Checks if server is receiving anything other than a GET method
        :param request: the array of request sent to server
        :returns 405 Method not Allowed http response if true
        """
        if(request[0]!="GET"):
            page = self.return_error_html("405 Method Not Allowed")
            return self.return_HTTP("405 Method Not Allowed", page)
        return False

    def check_404(self, request):
        """
        check validity of request url
        - if file doesn't exist in ./www
            :returns: 404 HTTP Error response
        - if url is of directory and file path is incomplete
            :returns: 301 Moved Permanently, new Location
        - if url is trailing with "/"
            - serves the index.html if it exists in the folder
            - returns with 200 OK HTTP Response

        Citations:
        parent = os.path.abspath("www")
        from https://docs.python.org/3/library/os.path.html
        """
        parent = os.path.abspath("www")
        path_given = request[1]
        newpath = parent + path_given    # appends requested path onto base path

        if parent not in os.path.abspath(newpath):      # checks that path doesn't go behind www/ directory
            page = self.return_error_html("404 Page Not Found")
            return self.return_HTTP("404 Page Not Found", page)

        if os.path.exists(newpath):             # only proceeds if it's an existing path
            if os.path.isdir(newpath):
                if path_given[-1] != "/":
                    page = self.return_error_html(f"301 Moved Permanently\r\nLocation: localhost:8000/{path_given}/")
                    return self.return_HTTP(f"301 Moved Permanently\r\nLocation: {path_given}/", page)
            if path_given[-1] == "/":
                if "html" not in path_given:
                    newpath += "index.html"
            # file path is valid
            # to check its a file that can be served over web
            # only css or html files
            if "css" in newpath or "html" in newpath:
                fetch_page = open(newpath, "r")
                read_page = fetch_page.read()
                fetch_page.close()

                mimetype = "text/html"
                if "css" in newpath:
                    mimetype = "text/css"
                return """HTTP/1.1 {}\r\nAllow: GET\r\nContent-Type: {}\r\nConnection: close\r\n\r\n{}""".format("200 OK",mimetype,read_page)

        page = self.return_error_html("404 Page Not Found")
        return self.return_HTTP("404 Page Not Found", page)


    def return_HTTP(self, status_code, page):
        """
        :param status_code: 200 OK | 404 Page Not Found
            | 301 Moved Permanently | 405 Method Not Allowed
        :param page: html page
        :returns: a simple http response as string
        """
        http = """HTTP/1.1 {}\r\nAllow: GET\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n{}""".format(status_code,page)
        return http

    def return_error_html(self, status_code):
        page = """
        <!DOCTYPE html>
        <html>
        <head>
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
        </head>
        <body>
            <h1>{}</h1>
        </body>
        </html>
        """.format(status_code)
        return page

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
