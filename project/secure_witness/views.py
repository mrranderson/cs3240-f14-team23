from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from forms import UserForm, BasicSearchForm, BulletinForm, FolderForm
from django.contrib.auth import login, authenticate, logout
from secure_witness.models import Bulletin, Document, Notification, Follow, Folder
from django.contrib.auth.models import User
from Crypto.PublicKey import RSA
#from Crypto.Cipher import PKCS1_v1_5
from Crypto.Cipher import PKCS1_OAEP, AES
from base64 import b64decode
from models import UserProfile

def encrypt_RSA(public_key_loc, message):
  '''
  param: public_key_loc Path to public key
  param: message String to be encrypted
  return base64 encoded encrypted string
  '''
  key = open(public_key_loc, "r").read()
  rsakey = RSA.importKey(key)
  rsakey = PKCS1_OAEP.new(rsakey)
  #rsakey = PKCS1_v1_5.new(rsakey)
  encrypted = rsakey.encrypt(message)
  return encrypted.encode('base64')

def decrypt_RSA(private_key_loc, package):
  '''
  param: public_key_loc Path to your private key
  param: package String to be decrypted
  return decrypted string
  '''
  key = open(private_key_loc, "r").read()
  rsakey = RSA.importKey(key)
  rsakey = PKCS1_OAEP.new(rsakey)
  #rsakey = PKCS1_v1_5.new(rsakey) #the original comment
  decrypted = rsakey.decrypt(b64decode(package))
  return decrypted

def generate_RSA(bits=2048):
  '''
  Generate an RSA keypair with an exponent of 65537 in PEM format
  param: bits The key length in bits
  Return private key and public key
  '''
  new_key = RSA.generate(bits) #, 65537)
  public_key = new_key.publickey().exportKey("PEM")
  private_key = new_key.exportKey("PEM")
  return private_key, public_key


#def IndexView(request):
#	return HttpResponse("Index")

@login_required
def IndexView(request):
    bulletin_list = Bulletin.objects.all()

    for b in bulletin_list:
        if b.author == request.user and request.user.profile.private_key != u'':
            b.title = decrypt_RSA(request.user.profile.private_key, str(b.title))

    current_user = request.user
    notifications = Notification.objects.filter(recipient=current_user, has_read=False)
    if len(notifications) != 0:
        inbox_str = 'Inbox( ' + str(len(notifications)) + ' )'
    else:
        inbox_str = 'Inbox'
        
    your_bulletins = Bulletin.objects.filter(author=request.user)
    folder_list = Folder.objects.all()

    for b in your_bulletins:
        if request.user.profile.private_key != u'':
            b.title = decrypt_RSA(request.user.profile.private_key, str(b.title))

    pub_bulletins = Bulletin.objects.filter(is_public=True)
    fol_bulletins = Follow.objects.filter(owner=request.user)
    
    return render(request, 'secure_witness/index.html', {'bulletin_list': bulletin_list, 'inbox_str': inbox_str, 'your_bulletins': your_bulletins, 'pub_bulletins': pub_bulletins, 'fol_bulletins': fol_bulletins, 'folder_list':folder_list}) 

@login_required
def basic_search(request):
    if request.method == "POST":
        #
        #  This is where you put the code to process the search
        #  Also need to figure out a better way to search by keyword
        #
        return HttpResponseRedirect('/')
    else:
        form = BasicSearchForm()
    return render(request, 'secure_witness/search.html', {'form': form}) 

@login_required
def logout_user(request):
    logout(request)
    return HttpResponseRedirect('/')

def lexusadduser(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            confirm = form.cleaned_data['confirm_password']

            public_key_loc = "" 
            if str(form.cleaned_data['public_key_loc']) != "":
                public_key_loc = form.cleaned_data['public_key_loc']

            private_key_loc = ""
            if str(form.cleaned_data['private_key_loc']) != "":
                private_key_loc = form.cleaned_data['private_key_loc']
            if password == confirm:
                new_user = User.objects.create_user(username=username, password=password)
                auth_user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
                UserProfile.objects.create(user=auth_user, public_key=public_key_loc, private_key=private_key_loc)
                login(request,auth_user)
                # redirect, or however you want to get to the main view
                return HttpResponseRedirect('/')
            
            
            else:
                form = UserForm()
    else:
        form = UserForm() 

    return render(request, 'secure_witness/adduser.html', {'form': form})

@login_required
def create_bulletin(request):
    if request.method == "POST":
        form = BulletinForm(request.POST, request.FILES)
        if form.is_valid():
            b = Bulletin()
            b.title = form.cleaned_data['title']
            b.location = form.cleaned_data['location']
            b.description = form.cleaned_data['description']
            b.author = request.user
            b.folder = form.cleaned_data['folder']
            #encryption handled here
            if not form.cleaned_data['is_public']:
                b.folder = form.cleaned_data['folder']
                b.is_encrypted = True
                pub_key = request.user.profile.public_key
                title = str(form.cleaned_data['title'])
                location = str(form.cleaned_data['location'])
                description = str(form.cleaned_data['description'])
                #author = str(request.user)
                b.title = encrypt_RSA(pub_key, title)
                b.location = encrypt_RSA(pub_key, location)
                b.description = encrypt_RSA(pub_key, description)
                #b.author = encrypt_RSA(pub_key, author)

            if(form.cleaned_data['is_public']):
                b.is_public = True
                b.is_searchable = True
            elif (form.cleaned_data['is_searchable']):
                b.is_public = False
                b.is_searchable = True
            else:
                b.is_public = False                                                                                                         
                b.is_searchable = False
	    #file upload
            if request.FILES.get('docfile', None):
                b.docfile = request.FILES['docfile']
            b.save()
        else:
            return HttpResponseRedirect('/logout')
        return HttpResponseRedirect('/')
    else:
        form = BulletinForm()

    return render(request, 'secure_witness/create_bulletin.html', {'form': form})

@login_required
def request_bulletin(request, bulletin_id):
    #Code needs work - cases
    n = Notification()
    bulletin = get_object_or_404(Bulletin, pk=bulletin_id)
    if(bulletin.is_public):
        i=0
    elif(bulletin.is_searchable):
        n.subject = str(request.user) + ' has requested access to your bulletin'
        n.sender = request.user
        n.is_request = True
        n.recipient = bulletin.author
        n.message = 'This is an automatic notification that user ' + str(request.user) + ' has requested access to your bulletin: ' + str(bulletin.title)
        n.bulletin = bulletin
        n.save()
    return HttpResponseRedirect('/')

@login_required
def detail_bulletin(request, bulletin_id):
    bulletin = get_object_or_404(Bulletin, pk=bulletin_id)
    #return render(request, 'secure_witness/detail_bulletin.html', {'bulletin': bulletin, 'user':request.user})
    #Decrypt if user is author or has permissions to view
    if not bulletin.is_public and request.user == bulletin.author and request.user.profile.private_key != u'':
        temp_b = bulletin
        private_key_loc = request.user.profile.private_key
        temp_b.title = decrypt_RSA(private_key_loc, str(bulletin.title))
        temp_b.description = decrypt_RSA(private_key_loc, str(bulletin.description))
        temp_b.location = decrypt_RSA(private_key_loc, str(bulletin.location))
        temp_b.docfile = bulletin.docfile
        return render(request, 'secure_witness/detail_bulletin.html', {'bulletin': temp_b})

    return render(request, 'secure_witness/detail_bulletin.html', {'bulletin': bulletin})
    
@login_required
def view_notification(request, notification_id):
    notification = get_object_or_404(Notification, pk=notification_id)
    notification.has_read = True
    notification.save()
    return render(request, 'secure_witness/notification.html', {'n': notification})


@login_required
def inbox(request):
    notifications = Notification.objects.filter(recipient=request.user)
    num_new = len(Notification.objects.filter(recipient=request.user, has_read=False))
    return render(request, 'secure_witness/inbox.html', {'notifications': notifications, 'num_new': num_new})
    
@login_required
def follow_bulletin(request, bulletin_id):
    
    bulletin = get_object_or_404(Bulletin, pk=bulletin_id)
    
    if request.user.username == bulletin.author.username:
        return HttpResponseRedirect('/')
    for fol in Follow.objects.filter(bulletin=bulletin):
        if fol.owner == request.user:
            return HttpResponseRedirect('/')
    if bulletin.is_public == False:
        return HttpResponseRedirect('/')
        
    #Create a follow object
    f = Follow()
    f.owner = request.user
    f.bulletin = bulletin
    f.save()
    
    #Create a notification object
    n = Notification()
    n.subject = str(request.user) + ' has started following your bulletin'
    n.sender = request.user
    n.recipient = bulletin.author
    n.message = 'This is an automatic notification that user ' + str(request.user) + ' has started following your bulletin: ' + str(bulletin.title)
    n.bulletin = bulletin
    n.save()
    return HttpResponseRedirect('/')
    
@login_required
def edit_bulletin(request, bulletin_id):
    bulletin = get_object_or_404(Bulletin, pk=bulletin_id)
    if request.method == "POST":
        form = BulletinForm(request.POST)
        if form.is_valid():
            bulletin.title = form.cleaned_data['title']
            bulletin.location = form.cleaned_data['location']
            bulletin.description = form.cleaned_data['description']
            bulletin.folder = form.cleaned_data['folder']
            if(form.cleaned_data['is_public']):
                bulletin.is_public = True
            else:
                bulletin.is_public = False
                for fol in Follow.objects.filter(bulletin=bulletin):
                    n = Notification()
                    n.subject = 'A bulletin you were following has been made private'
                    n.sender = request.user
                    n.recipient = fol.owner
                    n.message = 'this means you can no longer follow it, you may request permission'
                    n.bulletin = bulletin
                    n.save()
                    fol.delete()
                
            if(form.cleaned_data['is_searchable']):
                bulletin.is_searchable = True
            else:
                bulletin.is_searchable = False
            bulletin.save()
            
            #Send notification to users following the bulletin
            
            
            for fol in Follow.objects.filter(bulletin=bulletin):
                n = Notification()
                n.subject = 'something youre following has been changed'
                n.sender = request.user
                n.recipient = fol.owner
                n.message = 'auto generated'
                n.bulletin = bulletin
                n.save()
            
        else:
            return HttpResponseRedirect('/logout')
        return HttpResponseRedirect('/')
    else:
        form = BulletinForm(initial={'title': bulletin.title, 'description':bulletin.description, 'location':bulletin.location, 'is_public':bulletin.is_public, 'is_searchable':bulletin.is_searchable, 'folder':bulletin.folder})
    return render(request, 'secure_witness/edit_bulletin.html', {'bulletin': bulletin, 'form': form})

@login_required
def delete_bulletin(request, bulletin_id):
    bulletin = get_object_or_404(Bulletin, pk=bulletin_id)
    if bulletin.author == request.user:
        bulletin.delete()
    return HttpResponseRedirect('/')
    
@login_required
def delete_notification(request, notification_id):
    notification = get_object_or_404(Notification, pk=notification_id)
    if notification.recipient == request.user:
        notification.delete()
    return HttpResponseRedirect('/inbox')
    
@login_required
def accept_notification(request, notification_id):
    notification = get_object_or_404(Notification, pk=notification_id)
    if notification.is_request == False:
        return HttpResponseRedirect('/')
    if notification.recipient != request.user:
        return HttpResponseRedirect('/')
    return HttpResponseRedirect('/inbox')

@login_required
def reject_notification(request, notification_id):
    notification = get_object_or_404(Notification, pk=notification_id)
    if notification.is_request == False:
        return HttpResponseRedirect('/')
    if notification.recipient != request.user:
        return HttpResponseRedirect('/')
    else:
        n = Notification()
        n.subject = str(request.user) + ' has rejected your request to view their bulletin: ' + str(notification.bulletin.title)
        n.sender = request.user
        n.recipient = notification.sender
        n.message = 'auto generated'
        n.bulletin = notification.bulletin
        n.save()
        notification.delete()
        return HttpResponseRedirect('/inbox')

def create_folder(request):
    if request.method == "POST":
        form = FolderForm(request.POST)
        if form.is_valid():
            f = Folder()
            f.title = form.cleaned_data['title']
            f.parent_folder = form.cleaned_data['parent_folder']
            f.save()
        return HttpResponseRedirect('/')
    else:
        form = FolderForm()
    return render(request, 'secure_witness/create_folder.html', {'form': form})

def detail_folder(request, folder_id):
    f = get_object_or_404(Folder, pk=folder_id)
    bulletin_list = Bulletin.objects.filter(folder = f)
    subfolder_list = Folder.objects.filter(parent_folder = f)
    return render(request, 'secure_witness/detail_folder.html', {'folder': f, 'subfolder_list': subfolder_list, 'bulletin_list': bulletin_list})

def delete_folder(request, folder_id):
    f = get_object_or_404(Folder, pk=folder_id)
    f.delete()
    return HttpResponseRedirect('/')

def edit_folder(request, folder_id):
    f = get_object_or_404(Folder, pk=folder_id) 
    if request.method == "POST":
        form = FolderForm(request.POST)
        if form.is_valid():
            f.title = form.cleaned_data['title']
            f.parent_folder = form.cleaned_data['parent_folder']
            f.save()
        return HttpResponseRedirect('/')
    else:
        form = FolderForm(initial={'title':f.title})
    return render(request, 'secure_witness/edit_folder.html', {'folder': f, 'form': form})
# Create your views here.
