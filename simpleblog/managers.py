from django.db import models


class PostManager(models.Manager):
    """Manager for Post model with additional public() and drafts() methods
    """

    class PostQuerySet(models.QuerySet):
        def public(self):
            return self.filter(is_public=True)
        def drafts(self):
            return self.filter(is_public=False)

    def get_queryset(self):
        return self.PostQuerySet(self.model, using=self._db)

    def public(self):
        """return published posts queryset (is_public = True)."""
        return self.get_queryset().public()

    def drafts(self):
        """return drafts queryset (is_public = False)."""
        return self.get_queryset().drafts()
