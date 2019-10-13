from hashlib import sha256

from django.db import models


class Manifestation(models.Model):
	id = models.CharField(max_length=200, primary_key=True)
	name = models.CharField(max_length=200, blank=True)

	def __str__(self):
		return self.name[:100]

	@classmethod
	def get_id(cls, data):
		return sha256(data.encode('utf8')).hexdigest()[:16]


class Condition(models.Model):
	id = models.CharField(max_length=100, primary_key=True)
	url = models.URLField(blank=False)
	name = models.CharField(max_length=100, blank=True)
	updated_at = models.DateTimeField(auto_now=True)
	manifestations = models.ManyToManyField(Manifestation)


class Disharmony(models.Model):
	id = models.CharField(max_length=200, primary_key=True)
	name = models.CharField(max_length=200, blank=True)
	updated_at = models.DateTimeField(auto_now=True)
	manifestations = models.ManyToManyField(Manifestation)


