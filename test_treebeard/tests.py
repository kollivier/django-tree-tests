import time

from django.conf import settings
from django.db import connection, reset_queries
from django.test import TestCase

from test_treebeard.models import Object, TreeNode


def get(pk):
    """
    For speed, Treebeard uses raw queries for write operations that don't update the ORM objects.
    If you need to write then read in the same procedure, you need to re-query it.

    :param pk: The primary key of the TreeNode to retrieve
    :return: TreeNode object (throws an exception if object with pk is not found or unique)
    """
    return TreeNode.objects.get(pk=pk)

class PerfTestCase(TestCase):

    def setUp(self):
        settings.DEBUG = True
        reset_queries()
        self.root_node = TreeNode.add_root(name="The Root of All Nodes")
        self.root_node = get(self.root_node.pk)
        reset_queries()
        self.root_node.save()

    def _report_queries(self, operation):
        print("{} ran {} queries:".format(operation, len(connection.queries)))
        for query in connection.queries:
            print(query['sql'])

    def _create_objects(self, num_objects):
        start = time.time()
        for i in range(num_objects):
            Object.objects.create(name="Test object {}".format(i))
        elapsed = time.time() - start

        return elapsed

    def _create_nodes(self, num_nodes):
        parent = self.root_node
        count = TreeNode.objects.count()
        start = time.time()
        settings.DEBUG = True
        for i in range(num_nodes):
            assert parent
            reset_queries()
            new_node = parent.add_child(name="Child Node {}".format(i))
            # self._report_queries("Adding MP child")
            if num_nodes > 20 and i > 0 and i % (num_nodes / 10) == 0:
                parent = get(new_node.pk)

        assert TreeNode.objects.count() == count + num_nodes
        elapsed = time.time() - start
        return elapsed

    def test_create_objects(self):
        num_tests = [10, 100, 1000]
        for num_objects in num_tests:
            elapsed = self._create_objects(num_objects)
            print("Creating {} objects took {} seconds".format(num_objects, elapsed))

    def test_create_nodes(self):
        num_tests = [10, 100, 1000]
        for num in num_tests:
            elapsed = self._create_nodes(num)
            print("Creating {} nodes took {} seconds".format(num, elapsed))

        start = time.time()
        descendants = self.root_node.get_descendants()
        elapsed = time.time() - start
        print("Getting {} descendants takes {} seconds".format(descendants.count(), elapsed))

    def test_move_nodes(self):
        self._create_nodes(10000)

        node = self.root_node
        for i in range(5):
            node = node.get_last_child()

        start = time.time()

        node.move(node.get_parent().get_first_child(), 'left')
        elapsed = time.time() - start

        print("Moving last MP root child five levels deep to front took {} seconds".format(elapsed))

        start = time.time()
        last_child = self.root_node.get_last_child()
        last_child.move(self.root_node.get_first_child(), 'first-child')
        elapsed = time.time() - start

        print("Moving last MP root child to front took {} seconds".format(elapsed))