#!/usr/bin/python3

import os
import sys
import subprocess


class OverwatchModule(object):

    max_response_time = 5
    is_dirty = False
    process = None

    def __init__(self, name):
        self.name = name

    def start(self):
        path = sys.path[0] + '/plugins/' + self.name + '/'
        self.process = subprocess.Popen(
            [sys.executable, "plugins/" + self.name + "/overwatch_plugin_starter.py"],
            shell=False,
            env={'PYTHONPATH':path}
        )
        print("Started " + self.name + " with ID " + str(self.process.pid))

    def stop(self):
        # Get the process id & try to terminate it gracefuly
        pid = self.process.pid
        self.process.terminate()

        # Check if the process has really terminated & force kill if not.
        try:
            os.kill(pid, 0)
            self.process.kill()
            print("Forced killed" + self.name + " with pid " + str(pid))
        except OSError:
            print("Terminated" + self.name + " with pid " + pid + " gracefully")

    def get_gui_path(self):
        try:
            byte_path = subprocess.check_output(
                [sys.executable, "plugins/" + self.name + "/overwatch_gui_provider.py"], shell=False,
                timeout=self.max_response_time, env={'PATH': '/plugins/' + self.name + '/'}
            )
            return str(byte_path, "utf-8")

        except subprocess.TimeoutExpired:
            self.is_dirty = True
            raise ValueError('the response to longer than permitted, ' + str(self.max_response_time))

    def get_response(self, path):
        try:
            return subprocess.check_output(
                [sys.executable, "plugins/" + self.name + "/overwatch_data_provider.py", path], shell=False,
                timeout=self.max_response_time, env={'PATH':'/plugins/' + self.name + '/'}
            )
        except subprocess.TimeoutExpired:
            self.is_dirty = True
            raise ValueError('the response to longer than permitted, ' + str(self.max_response_time))
