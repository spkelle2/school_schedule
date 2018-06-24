from django.db import models

class Document(models.Model):
	# saves to MEDIA_ROOT/...
    docfile = models.FileField(upload_to='')