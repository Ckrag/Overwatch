#!/usr/bin/python3

from http.server import BaseHTTPRequestHandler, SimpleHTTPRequestHandler, HTTPServer
import time
import os
import sys
import overwatch_module
import requests

__hostName__ = "localhost"
__hostPort__ = 9001

__path_html__ = "html"
__path_plugins__ = "plugins"

__plugins__ = {}
__overwatch_gui_html__ = ""

# Very inspired by http://stackoverflow.com/a/26652985

# url http://localhost:9001
class LocalService(SimpleHTTPRequestHandler):

    def do_GET(self):

        # special path for each plugin
        # canonical way of requesting data from plugin
        # EXPECTS BASEPATH/module/MODULE_NAME
        path_components = self.get_clean_path(self.path)

        if len(path_components) >= 3 and path_components[0] == "module" and path_components[1] in __plugins__ and path_components[2] == "gui":
            # return plugin gui

            module = __plugins__[path_components[1]]

            if module.is_dirty:
                return

            module_gui_paths = LocalService.get_clean_path(module.get_gui_path().rstrip())

            # change base
            path_components[0] = __path_plugins__

            # delete the gui keyword
            del path_components[2]

            # insert the path specified by the plugin
            path_components[2:2] = module_gui_paths

            uri = ""

            for path in path_components:
                uri += "/" + path

            if "." not in path_components[len(path_components) - 1]:
                uri += "/"

            self.path = uri
            super().do_GET()

        elif len(path_components) >= 2 and path_components[0] == "module" and path_components[1] in __plugins__:

            module = __plugins__[path_components[1]]

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
            self.send_header("Content-type", "application/json") # SHOULD NOT RELY ON THIS HEADER
            self.end_headers()
            self.wfile.write(bytes(response, "utf-8"))


        # Everything not related to plugins (/modules/..) will go here
        elif len(path_components) >= 1:
            # If the GUI specifically is requested, do the contentswapping and generating to populate with plugins
            if path_components[0].lower() == "overwatch":
                # The front page
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.send_header("Content-length", str(len(__overwatch_gui_html__)))
                self.end_headers()
                self.wfile.write(bytes(__overwatch_gui_html__, "utf-8"))
            else:
                # All other resources just get piped to the html folder
                self.path = __path_html__ + self.path
                super().do_GET()


    @staticmethod
    def get_clean_path(path):
        path_components = path.split(os.sep)
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


def build_gui(plugins):

    error = None

    with open(sys.path[0] + "/html/index.html", 'r') as html_template:
        base_html = html_template.read()
    with open(sys.path[0] + "/html/iframe_snippet.html", 'r') as html_plugin_snippet:
        snippet_html = html_plugin_snippet.read()

    if base_html is None and snippet_html is None:
        raise ValueError('Error building GUI. Unable to read in HTML')

    iframe_html_dom = ""
    for name, plugin in plugins.items():

        # Skip the example
        if name == "example_plugin":
            continue

        if plugin.is_web():

            path = plugin.get_gui_path()


            # check if open web url. First sign will always be a /, since it's supposed to handle relative paths
            if path[:4] != "http":
                error = "Web url has to be fully qualified: http://www...."

            path = plugin.get_gui_path()
        else:
            path = "//" + __hostName__ + ":" + str(__hostPort__) + "/module/" + plugin.name + "/gui/"

        iframe_html_dom += snippet_html.replace("{{SRC}}", path)

        # Added error text
        iframe_html_dom.replace("{{ERRROR}}", error if error is not None else "")

    return base_html.replace("{{DATA}}", iframe_html_dom)


def run(module_name_list):

    # Get modules
    global __plugins__

    for module_name in module_name_list:
        __plugins__[module_name] = overwatch_module.OverwatchModule(module_name)

    # build main gui
    global __overwatch_gui_html__
    __overwatch_gui_html__ = build_gui(__plugins__)

    # Start plugins
    start_plugins(__plugins__)

    # Start shared service
    local_service = HTTPServer((__hostName__, __hostPort__), LocalService)
    print(time.asctime(), "Server Starts - %s:%s" % (__hostName__, __hostPort__))

    try:
        local_service.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped, ..exiting")

    local_service.server_close()
    stop_plugins(__plugins__)
    print(time.asctime(), "Server Stops - %s:%s" % (__hostName__, __hostPort__))
