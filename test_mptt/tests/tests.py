import time

from django.conf import settings
from django.db import connection, reset_queries
from django.test import TestCase

from test_mptt.models import Object, TreeNode


class PerfTestCase(TestCase):

    def setUp(self):
        settings.DEBUG = True
        reset_queries()
        self.root_node = TreeNode.objects.create(name="The Root of All Nodes")
        # self._report_queries("Creating root node")
        reset_queries()
        self.root_node.save()
        # self._report_queries("Saving root node")

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

    def _create_nodes(self, num_nodes, levels=10):
        parent = self.root_node
        count = TreeNode.objects.count()
        start = time.time()
        with TreeNode.objects.delay_mptt_updates():
            for i in range(num_nodes):
                assert parent
                new_node = TreeNode.objects.create(name="Child Node {}".format(i), parent=parent)
                new_node.save()
                if num_nodes > 20 and i > 0 and i % (num_nodes / levels) == 0:
                    parent = new_node

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
        assert TreeNode.objects.count() == 1
        self._create_nodes(10000, levels=10)

        # print("Moving last MPTT root child five levels deep to front took {} seconds".format(elapsed))

        start = time.time()
        last_child = self.root_node.get_children().last()
        first_child = self.root_node.get_children().first()
        assert last_child.name != first_child.name
        last_child.move_to(first_child, 'first-child')
        elapsed = time.time() - start

        print("Moving last MPTT root child to front took {} seconds".format(elapsed))
