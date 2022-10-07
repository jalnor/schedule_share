from django.db import models
from django.urls import reverse


# TODO Rename class to match application and add variables for ex. address...
class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    @property
    def get_html_url(self):
        url = reverse('calendar:event_edit', args=(self.id,))
        return f'<a href="{url}"> {self.title} </a>'
