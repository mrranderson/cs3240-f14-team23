from django.db import models
from django.contrib.auth.models import User
#from django.contrib.postgres.fields import ArrayField
 
class UserProfile(models.Model):
	user = models.ForeignKey(User, unique=True)
	public_key = models.CharField(max_length=500, default="")
	private_key = models.CharField(max_length=500, default="")

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])

class Folder(models.Model):
    title = models.CharField(max_length=200)
    def __unicode__(self):
        return self.title
    parent_folder = models.ForeignKey('self', null=True, on_delete=models.SET_NULL)
    is_global = models.BooleanField(default=True)
    owner = models.ForeignKey(User, null=True)

class Bulletin(models.Model):
	title = models.CharField(max_length=200)
	date_created = models.DateTimeField(auto_now_add=True)
	date_modified = models.DateTimeField(auto_now=True)
	#Author's user account
	author = models.ForeignKey(User, related_name="author")
#	reader = models.ForeignKey(User, related_name="reader", default=None)
	location = models.CharField(max_length=200)
	description = models.CharField(max_length=200)
    	#display permissions
	is_encrypted = models.BooleanField(default=False)
	is_public = models.BooleanField(default=False)
	is_searchable = models.BooleanField(default=False)
	folder = models.ForeignKey(Folder, null=True)
	#file upload
	docfile = models.FileField(upload_to='documents', blank=True, null=True)
	doc_key = models.CharField(max_length=200, default="")
	#readers = ArrayField(models.ForeignKey(Permission))

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
