from django.db import models

# Create your models here.
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


class Object(models.Model):
    name = models.CharField(max_length=50)


class TreeNode(MPTTModel):
    name = models.CharField(max_length=50)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
