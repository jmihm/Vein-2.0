from datetime import date, timedelta

from data_loading.data_loaders import DataLoader
from data_loading.data_loaders import loader_utils
from data_loading.invariant_file_types import invariant_utils

from data_loading.invariant_file_types import file_invariants
from miso_tables import models


class NodeLoader(DataLoader.DataLoader):

    def get_model_class(self):
        return models.Node

    def get_priority(self):
        return 2

    def get_accessible_dates(self):
        two_years_ago = date.today().year - 2
        start_date = date(two_years_ago, 1, 1)
        end_date = date.today() - timedelta(days=3)
        return loader_utils.get_date_range_set_inclusive(start_date, end_date)

    def insert_data_for_date(self, date):
        data = invariant_utils.getFile(file_invariants.da_invariant, date)
        lines = data.strip().split("\n")
        headers = lines[4]
        assert headers.startswith("Node,Type,")
        lines = lines[5:]
        nodes = []
        for line in lines:
            [node_name, node_type] = line.split(",")[0:2]
            try:
                node = models.Node.objects.get(name=node_name)
                if not (node.name == node_name and node.type == node_type):
                    raise Exception('Node information has changed for node: %s.' % node_name)
            except models.Node.DoesNotExist:
                node = models.Node(name=node_name, type=node_type, deprecated=False)
                nodes.append(node)
        models.Node.objects.bulk_create(nodes)


