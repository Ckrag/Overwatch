import service
import os

# make list of plugins
list_of_plugins = next(os.walk(os.getcwd() + "/plugins"))[1]
# parse to service
service.run(list_of_plugins)