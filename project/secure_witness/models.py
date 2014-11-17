from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
	user = models.ForeignKey(User, unique=True)
	public_key = models.CharField(max_length=500, default="")
	private_key = models.CharField(max_length=500, default="")

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])

class Bulletin(models.Model):
	title = models.CharField(max_length=200)
	date_created = models.DateTimeField(auto_now_add=True)
	date_modified = models.DateTimeField(auto_now=True)
	#Author's user account
	author = models.ForeignKey(User)
	location = models.CharField(max_length=200)
	description = models.CharField(max_length=200)
    	#display permissions
	is_encrypted = models.BooleanField(default=False)
	is_public = models.BooleanField(default=False)
	is_searchable = models.BooleanField(default=False)
	#file upload
        docfile = models.FileField(upload_to='documents', blank=True, null=True)

        def filename(self):
        	return os.path.basename(self.docfile.name)

	def __unicode__(self):
		return self.title

class Document(models.Model):
	title = models.CharField(max_length=200)
	#Link to bulletin it's posted with
	owner = models.ForeignKey(Bulletin)
	#field to hold file
	
	class Meta:
		permissions = (
			("decrypt_document", "Can decrypt and use file"),
		)

class Notification(models.Model):
    subject = models.CharField(max_length=200)
    sender = models.ForeignKey(User, related_name='+')
    recipient = models.ForeignKey(User)
    has_read = models.BooleanField(default=False)
    message = models.TextField()
    is_request = models.BooleanField(default=False)
    is_update = models.BooleanField(default=False)
    bulletin = models.ForeignKey(Bulletin)
    
class Follow(models.Model):
    owner = models.ForeignKey(User)
    bulletin = models.ForeignKey(Bulletin)
