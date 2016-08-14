#!/usr/bin/python3

from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import re
import importlib

hostName = "localhost"
hostPort = 9001

modules = []

# Very inspired by http://stackoverflow.com/a/26652985

# url http://localhost:9001
class LocalService(BaseHTTPRequestHandler):

    def do_GET(self):

        # special path for each plugin
        # canonical way of requesting data from plugin
        # EXPECTS BASEPATH/module/MODULE_NAME

        path_components = self.get_clean_path(self.path)

        if path_components[0] == "module" and path_components[1] in modules:

            module = importlib.import_module("plugins." + path_components[1] + ".plugger")

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(module.serve_response(self.path), "utf-8"))

    @staticmethod
    def get_clean_path(path):
        path_components = re.split('\W+', path)
        clean_components = []

        for component in path_components:
            if component != "":
                clean_components.append(component.replace("/", ""))

        return clean_components


def run(module_list):

    global modules
    modules = module_list

    local_service = HTTPServer((hostName, hostPort), LocalService)
    print(time.asctime(), "Server Starts - %s:%s" % (hostName, hostPort))

    try:
        local_service.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped, ..exiting")

    local_service.server_close()
    print(time.asctime(), "Server Stops - %s:%s" % (hostName, hostPort))