from django.db import models
from django.contrib.auth.models import User

class Bulletin(models.Model):
	title = models.CharField(max_length=200)
	date_created = models.DateTimeField(auto_now_add=True)
	date_modified = models.DateTimeField(auto_now=True)
	#Author's user account
	author = models.ForeignKey(User)
	location = models.CharField(max_length=200)
	description = models.CharField(max_length=200)

	def __unicode__(self):
		return self.title

class Document(models.Model):
	title = models.CharField(max_length=200)
	#Link to bulletin it's posted with
	owner = models.ForeignKey(Bulletin)
	#field to hold file
