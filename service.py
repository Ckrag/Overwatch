#!/usr/bin/python3

from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import re
import importlib
import overwatch_module

hostName = "localhost"
hostPort = 9001

modules = {}

# Very inspired by http://stackoverflow.com/a/26652985

# url http://localhost:9001
class LocalService(BaseHTTPRequestHandler):

    def do_GET(self):

        # special path for each plugin
        # canonical way of requesting data from plugin
        # EXPECTS BASEPATH/module/MODULE_NAME

        path_components = self.get_clean_path(self.path)

        if path_components[0] == "module" and path_components[1] in modules:

            module = modules[path_components[1]]

            if module.is_dirty:
                return

            # Here we convert the bytestring to regular string
            # Then we can re-encode it with whatever

            try:
                # Getting a bytestring
                response = str(module.get_response(self.path), 'utf-8')
            except ValueError as err:
                print(module.name + " response error: " + err)
                return

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(response, "utf-8"))

    @staticmethod
    def get_clean_path(path):
        path_components = re.split('\W+', path)
        clean_components = []

        for component in path_components:
            if component != "":
                clean_components.append(component.replace("/", ""))

        return clean_components


def stop_plugins(plugins):
    # http://stackoverflow.com/a/16867318
    for name, plugin in plugins.items():
        plugin.stop()


def start_plugins(plugins):
    for name, plugin in plugins.items():
        plugin.start()


def run(module_name_list):

    # Get modules
    global modules

    for module_name in module_name_list:
        modules[module_name] = overwatch_module.OverwatchModule(module_name)

    # Start plugins
    start_plugins(modules)

    # Start shared service
    local_service = HTTPServer((hostName, hostPort), LocalService)
    print(time.asctime(), "Server Starts - %s:%s" % (hostName, hostPort))

    try:
        local_service.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped, ..exiting")

    local_service.server_close()
    stop_plugins(modules)
    print(time.asctime(), "Server Stops - %s:%s" % (hostName, hostPort))