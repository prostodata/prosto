import json
import copy

from prosto.utils import *

from prosto.Prosto import *
from prosto.Table import *
from prosto.Column import *
from prosto.TableOperation import *
from prosto.ColumnOperation import *
from prosto.Data import *


class Topology:
    """Topology is a graph of operations built taking into account their dependencies."""

    column_path_separator = "::"

    def __init__(self, prosto):

        self.prosto = prosto  # If context can be modified then make a copy: copy.deepcopy(prosto)

        self.layers = []  # Graph of operations
        self.elem_layers = []  # Graph of elements

    def translate(self) -> None:
        """Build a graph of operations by analyzing table and column dependencies."""

        # Collect all operations into one list
        all_operations = [x for x in self.prosto.operations]

        #
        # Augment topology
        # Find undefined dependencies and try to define them as explicit operations (e.g., column paths)
        #

        for op in all_operations:

            if isinstance(op, TableOperation):
                pass  # Currently we do check table operations
            elif isinstance(op, ColumnOperation):

                deps = op.get_dependencies_names()

                for table_name, column_names in deps.items():

                    table = self.prosto.get_table(table_name)
                    if not table:
                        raise ValueError("Table not found. Operation '{}' generates table '{}' which is not found in the schema.".format(op.id, table_name))

                    # Check if all columns/attributes really exist and if not then try to insert an operation for their generation
                    for column_name in column_names:
                        # Check if such a column exists
                        column = self.prosto.get_column(table_name, column_name)
                        # TODO: Check if an operation for this column generation exists and if yes then add the corresponding column and warn (or error - operation without output column object)
                        #ops = self.prosto.get_column_operations(table_name, column_name)
                        if column:
                            continue
                        # Check if it is an attribute
                        is_attribute = self.prosto.has_attribute(table_name, column_name)
                        if is_attribute:
                            continue
                        # TODO: Parse the name and check if it is a column path
                        column_path = column_name.split(Topology.column_path_separator)
                        if len(column_path) > 1:
                            # Insert an (merge) operation for this column path. It will also add a column object(s)
                            self.prosto.merge(column_name, table_name, column_path)

            else:
                raise ValueError("Operation '{}' with unknown class found while building topology.".format(op.id))

        #
        # Build graph of operations by analyzing dependencies
        #

        all_operations = [x for x in self.prosto.operations]

        # Empty collection of already processed elements (they can be simultaneously removed from all)
        done = []

        # Topology to be built is a list of layers in the order of execution of their operations.
        # First layer does not have dependencies. Second layer depends on the operations in the first layer and so on.
        layers = []
        while True:
            layer = []  # List of operations which depend on only operations in some previous layers

            # We will build this new layer from the available (not added to previous layers) operations
            for op in all_operations:

                if op in done:
                    continue

                #
                # Find dependencies of this operation
                #
                if isinstance(op, TableOperation):
                    deps = op.get_dependencies()
                elif isinstance(op, ColumnOperation):
                    deps = op.get_dependency_objects()
                else:
                    raise ValueError("Operation '{}' with unknown class found while building topology.".format(op.id))

                #
                # Find operations which generate these elements
                #
                dep_ops = []
                for dep in deps:
                    if isinstance(dep, Table):
                        ops = self.prosto.get_table_operations(dep.id)
                    elif isinstance(dep, Column):
                        ops = self.prosto.get_column_operations(dep.table.id, dep.id)
                    else:
                        raise ValueError("Element '{}' with unknown class found while building topology (only Table and Column are possible).".format(dep.id))
                        #ops = []
                    dep_ops.extend(ops)

                #
                # If all dependencies have been processed (belong to previous layers) then add this element to the current layer
                #
                if set(dep_ops) <= set(done):
                    layer.append(op)

            if len(layer) == 0:
                break

            layers.append(layer)
            done.extend(layer)

        # Layers of operations
        self.layers = layers

        # Layers of tables/columns
        elem_layers = []
        for layer in layers:
            elem_layer = []
            for op in layer:
                # Find element (column or table) this operation produces
                outputs = op.get_outputs()
                if isinstance(op, TableOperation):  # Find table
                    tables = self.prosto.get_tables(outputs)
                    elem_layer.extend(tables)

                    # Allocate/initialize data and other resources
                    for tab in tables:
                        tab.data = Data(tab)

                elif isinstance(op, ColumnOperation):  # Find column
                    table_name = op.definition.get("table")
                    columns = self.prosto.get_columns(table_name, outputs)
                    elem_layer.extend(columns)
            elem_layers.append(elem_layer)

        self.elem_layers = elem_layers


if __name__ == '__main__':
    pass
