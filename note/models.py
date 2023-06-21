from django.db import models


class Note(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()

    def __str__(self):
        return f"id = {self.id} - {self.title} content: {self.content}"
