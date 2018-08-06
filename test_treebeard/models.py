from django.db import models
from treebeard.mp_tree import MP_Node


class Object(models.Model):
    name = models.CharField(max_length=50)


class TreeNode(MP_Node):
    name = models.CharField(max_length=30)

    def __unicode__(self):
        return 'Category: %s' % self.name

