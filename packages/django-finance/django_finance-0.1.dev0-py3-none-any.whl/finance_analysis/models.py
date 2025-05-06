from django.db import models


class Filter(models.Model):
    field = models.CharField('Name', max_length=255)
    operator = models.CharField('Name', max_length=255)
    pattern = models.CharField('Name', max_length=255)


class Group(models.Model):
    name = models.CharField(max_length=255, unique=True)
    parent = models.ForeignKey('Group', related_name='children', null=True, on_delete=models.CASCADE)
    level = models.SmallIntegerField()
    filters = models.ManyToManyField(Filter, related_name='groups')

    def save(self, *args, **kwargs):
        self.level = 0
        obj = self
        while obj.parent:
            obj = obj.parent
            self.level += 1
        return super().save(*args, **kwargs)


class Tag(models.Model):
    name = models.CharField(max_length=255)
    filters = models.ManyToManyField(Filter, related_name='tags')

