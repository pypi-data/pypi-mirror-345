# TODO: Update TEST

# from node_hermes_core.nodes.depedency import HermesDependencies
# from node_hermes_qt.nodes.node_manager_node import NodeManagerWidget

# # config_path = r"packages\datacapture-core\test\yaml\basic_config.hermes"
# config_path = r"packages\hermes-qt\test\nested_config.hermes"

# # Load the required modules in order to be able to parse the full configuration
# HermesDependencies.import_from_yaml(config_path)

# # Reload the configuration
# import logging

# from node_hermes_core.nodes.root_nodes import HermesConfig

# logging.basicConfig(level=logging.DEBUG)


# output = "schema.json"
# with open(output, "w") as schema_file:
#     schema_file.write(HermesConfig.get_schema_json())


# config = HermesConfig.from_yaml(config_path)
# root_node = config.get_root_node()
# root_node.attempt_init()

# from qtpy import QtWidgets

# app = QtWidgets.QApplication([])
# widget = NodeManagerWidget()
# widget.set_root_node(root_node)
# widget.show()

# app.exec_()
