import service
import os

# make list of plugins
list_of_plugins = list(filter(lambda v: os.path.isdir, os.listdir(os.getcwd() + "/plugins")))
# parse to service
service.run(list_of_plugins)



