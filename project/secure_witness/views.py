from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from forms import UserForm, BasicSearchForm, BulletinForm, FolderForm, UserEditForm, UserDeleteForm, PrivateFolderForm, CopyForm, BasicAddDoc
from django.contrib.auth import login, authenticate, logout
from secure_witness.models import Bulletin, Document, Notification, Follow, Folder
from django.contrib.auth.models import User
from Crypto.PublicKey import RSA
#from Crypto.Cipher import PKCS1_v1_5
from Crypto.Cipher import PKCS1_OAEP, AES
from base64 import b64decode
from models import UserProfile
import string, random, os, struct

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

def rand_key(size=32, chars=string.ascii_lowercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

def encrypt_file(key, in_filename, out_filename=None, chunksize=64*1024):
    """ Encrypts a file using AES (CBC mode) with the
        given key.

        key:
            The encryption key - a string that must be
            either 16, 24 or 32 bytes long. Longer keys
            are more secure.

        in_filename:
            Name of the input file

        out_filename:
            If None, '<in_filename>.enc' will be used.

        chunksize:
            Sets the size of the chunk which the function
            uses to read and encrypt the file. Larger chunk
            sizes can be faster for some files and machines.
            chunksize must be divisible by 16.
    """
    if not out_filename:
        out_filename = in_filename + '.enc'

    iv = ''.join(chr(random.randint(0, 0xFF)) for i in range(16))
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    filesize = os.path.getsize(in_filename)

    with open(in_filename, 'rb') as infile:
        with open(out_filename, 'wb') as outfile:
            outfile.write(struct.pack('<Q', filesize))
            outfile.write(iv)

            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                elif len(chunk) % 16 != 0:
                    chunk += ' ' * (16 - len(chunk) % 16)

                outfile.write(encryptor.encrypt(chunk))

def decrypt_file(key, in_filename, out_filename=None, chunksize=24*1024):
    """ Decrypts a file using AES (CBC mode) with the
        given key. Parameters are similar to encrypt_file,
        with one difference: out_filename, if not supplied
        will be in_filename without its last extension
        (i.e. if in_filename is 'aaa.zip.enc' then
        out_filename will be 'aaa.zip')
    """
    if not out_filename:
        out_filename = os.path.splitext(in_filename)[0]

    with open(in_filename, 'rb') as infile:
        origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
        iv = infile.read(16)
        decryptor = AES.new(key, AES.MODE_CBC, iv)

        with open(out_filename, 'wb') as outfile:
            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                outfile.write(decryptor.decrypt(chunk))

            outfile.truncate(origsize)

#def IndexView(request):
#	return HttpResponse("Index")

@login_required
def IndexView(request):
    bulletin_list = Bulletin.objects.all()

    for b in bulletin_list:
        if b.author == request.user and request.user.profile.private_key != u'' and b.is_encrypted and not b.is_searchable:
            b.title = decrypt_RSA(request.user.profile.private_key, str(b.title))

    current_user = request.user
    notifications = Notification.objects.filter(recipient=current_user, has_read=False)
    if len(notifications) != 0:
        inbox_str = 'Inbox( ' + str(len(notifications)) + ' )'
    else:
        inbox_str = 'Inbox'
        
    your_bulletins = Bulletin.objects.filter(author=request.user)

    folder_list = Folder.objects.filter(is_global=True).filter(parent_folder__isnull=True)
    my_folders = Folder.objects.filter(is_global=False).filter(owner=request.user).filter(parent_folder__isnull=True)

    for b in your_bulletins:
        if request.user.profile.private_key != u'' and b.is_encrypted and not b.is_searchable:
            b.title = decrypt_RSA(request.user.profile.private_key, str(b.title))

    pub_bulletins = Bulletin.objects.filter(is_public=True)
    fol_bulletins = Follow.objects.filter(owner=request.user)
    
    return render(request, 'secure_witness/index.html', {'bulletin_list': bulletin_list, 'inbox_str': inbox_str, 'your_bulletins': your_bulletins, 'pub_bulletins': pub_bulletins, 'fol_bulletins': fol_bulletins, 'folder_list':folder_list, 'user':request.user, 'my_folders':my_folders}) 

@login_required
def basic_search(request):
    if request.method == "POST":
        form = BasicSearchForm(request.POST)
        if form.is_valid():
            terms = form.cleaned_data['keywords']
            term_list = terms.split(' ')
            bul_list = []
            for word in term_list:
                bul_list.extend(Bulletin.objects.filter(title__contains=word))
            bulletins = set(bul_list)
            return render(request, 'secure_witness/search_results.html', {'bulletins': bulletins})
        else:
            return HttpResponseRedirect('/logout')
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
            create_keys = form.cleaned_data['create_keys']

            public_key_loc = "" 
            if str(form.cleaned_data['public_key_loc']) != "":
                public_key_loc = form.cleaned_data['public_key_loc']

            private_key_loc = ""
            if str(form.cleaned_data['private_key_loc']) != "":
                private_key_loc = form.cleaned_data['private_key_loc']
            if password == confirm:
                if create_keys:
                   new_keys = generate_RSA()
                   new_public_key = open(str(public_key_loc), 'w+')
                   new_public_key.write(new_keys[1])
                   new_private_key = open(str(private_key_loc), 'w+')
                   new_private_key.write(new_keys[0])

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
                b.currently_encrypted = True
                b.folder = form.cleaned_data['folder']
                b.is_encrypted = True
                pub_key = request.user.profile.public_key
                title = str(form.cleaned_data['title'])
                location = str(form.cleaned_data['location'])
                description = str(form.cleaned_data['description'])
                #author = str(request.user)
                b.location = encrypt_RSA(pub_key, location)
                b.description = encrypt_RSA(pub_key, description)
                aes_key = rand_key()
                b.doc_key = encrypt_RSA(pub_key, aes_key)
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

            if not b.is_searchable:
                b.title = encrypt_RSA(pub_key, title)
	    #file upload
            if request.FILES.get('docfile', None):
                b.docfile = request.FILES['docfile']
            b.save()
            if b.is_encrypted and b.docfile:
                directory = os.path.dirname(__file__)
                directory = os.path.join(directory, "../project/")
                filename = os.path.join(directory, b.docfile.url[1:])
                aes_key = decrypt_RSA(request.user.profile.private_key, str(b.doc_key))
                encrypt_file(aes_key, filename, filename + '.enc') 
                os.remove(filename)
        else:
            return HttpResponseRedirect('/create_bulletin')
        return HttpResponseRedirect('/')
    else:
        form = BulletinForm()

    return render(request, 'secure_witness/create_bulletin.html', {'form': form})

@login_required
def request_bulletin(request, bulletin_id):
    #Code needs work - cases
    n = Notification()
    bulletin = get_object_or_404(Bulletin, pk=bulletin_id)
    if(bulletin.is_public) or bulletin.author == request.user:
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
def add_document(request, bulletin_id):
    bulletin = get_object_or_404(Bulletin, pk=bulletin_id)
    if(bulletin.author == request.user):
        if request.method == "POST":
            form = BasicAddDoc(request.POST, request.FILES)
            if form.is_valid():
                b = Document()
                b.owner = bulletin
                aes_key = rand_key()
                pub_key = request.user.profile.public_key
                b.doc_key = encrypt_RSA(pub_key, aes_key)
                
                if request.FILES.get('docfile', None):
                    b.docfile = request.FILES['docfile']
                b.save()
                if bulletin.is_encrypted and b.docfile:
                    directory = os.path.dirname(__file__)
                    directory = os.path.join(directory, "../project/")
                    filename = os.path.join(directory, b.docfile.url[1:])
                    aes_key = decrypt_RSA(request.user.profile.private_key, str(b.doc_key))
                    encrypt_file(aes_key, filename, filename + '.enc') 
                    os.remove(filename)
                return HttpResponseRedirect('/search')
        else:
            form = BasicAddDoc()
            return render(request, 'secure_witness/add_doc.html', {'form':form})
    return HttpResponseRedirect('/')
    
@login_required
def detail_bulletin(request, bulletin_id):
    bulletin = get_object_or_404(Bulletin, pk=bulletin_id)
    userprof = UserProfile.objects.filter(user=bulletin.author)[0]
    #return render(request, 'secure_witness/detail_bulletin.html', {'bulletin': bulletin, 'user':request.user})
    #Decrypt if user is author or has permissions to view
    more = Document.objects.filter(owner=bulletin)
    if bulletin.is_encrypted and request.user == bulletin.author and request.user.profile.private_key != u'':
        temp_b = bulletin
        private_key_loc = request.user.profile.private_key
        if not bulletin.is_searchable:
            temp_b.title = decrypt_RSA(private_key_loc, str(bulletin.title))
        temp_b.description = decrypt_RSA(private_key_loc, str(bulletin.description))
        temp_b.location = decrypt_RSA(private_key_loc, str(bulletin.location))
        aes_key = decrypt_RSA(private_key_loc, str(bulletin.doc_key))
        temp_b.docfile = bulletin.docfile

        return render(request, 'secure_witness/detail_bulletin.html', {'bulletin': temp_b, 'userprof':userprof, 'files':more})

    return render(request, 'secure_witness/detail_bulletin.html', {'bulletin': bulletin, 'userprof':userprof, 'files':more})

@login_required
def detail_user(request, bulletin_id):
    bulletin = get_object_or_404(Bulletin, pk=bulletin_id)
    user = bulletin.author
    userprof = UserProfile.objects.filter(user=user)[0]
    if userprof.is_public:
        public_bulletins = Bulletin.objects.filter(author=user, is_public=True)
        searchable_bulletins = Bulletin.objects.filter(author=user, is_public=False, is_searchable=True)
        return render(request, 'secure_witness/detail_user.html', {'user':user, 'userprof':userprof, 'public_bulletins':public_bulletins, 'searchable_bulletins':searchable_bulletins})
    else:
        return HttpResponseRedirect('/')
    
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
def decrypt_document(request, bulletin_id):
	bulletin = get_object_or_404(Bulletin, pk=bulletin_id)
	more = Document.objects.filter(owner=bulletin)
	if bulletin.author == request.user:
		private_key_loc = request.user.profile.private_key
		aes_key = decrypt_RSA(private_key_loc, bulletin.doc_key)
		directory = os.path.dirname(__file__)
		directory = os.path.join(directory, "../project/")
		filename = os.path.join(directory, bulletin.docfile.url[1:])
		if bulletin.is_encrypted and bulletin.docfile and os.path.isfile(filename+".enc"):
			decrypt_file(aes_key, filename+".enc", filename+".dec")
			bulletin.currently_encrypted = False
			bulletin.save()
		for doc in more:
			filename = os.path.join(directory, doc.docfile.url[1:])
			aes_key = decrypt_RSA(private_key_loc, doc.doc_key)
			if bulletin.is_encrypted and bulletin.docfile and os.path.isfile(filename+".enc"):
				decrypt_file(aes_key, filename+".enc", filename+".dec")
	return HttpResponseRedirect('/'+bulletin_id)

@login_required
def encrypt_document(request, bulletin_id):
  bulletin = get_object_or_404(Bulletin, pk=bulletin_id)
  more = Document.objects.filter(owner=bulletin)
  if bulletin.author == request.user:
    #private_key_loc = request.user.profile.private_key
    #aes_key = decrypt_RSA(private_key_loc, str(bulletin.doc_key))
    directory = os.path.dirname(__file__)
    directory = os.path.join(directory, "../project/")
    filename = os.path.join(directory, bulletin.docfile.url[1:])
    if bulletin.is_encrypted and bulletin.docfile and os.path.isfile(filename+".dec"):
      os.remove(filename+".dec")
      bulletin.currently_encrypted = True
      bulletin.save()
      #encrypt_file(aes_key, filename, filename)
    for doc in more:
      if bulletin.is_encrypted and bulletin.docfile and os.path.isfile(filename+".dec"):
			  os.remove(filename+".dec")
  return HttpResponseRedirect('/'+bulletin_id)

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
        return HttpResponseRedirect('/logout')
    if notification.recipient != request.user:
        return HttpResponseRedirect('/logout')
    b = notification.bulletin
    author = request.user
    a_key = request.user.profile.private_key
    r_key = notification.sender.profile.public_key
    new_b = Bulletin()
    #new_b.title = encrypt_RSA(r_key, "Requested: "+decrypt_RSA(a_key, b.title))
    new_b.title = encrypt_RSA(r_key, "Requested: "+str(b.title))
    new_b.date_created = b.date_created
    new_b.date_modified = b.date_modified
    new_b.author = notification.sender
#    new_b.reader = notification.sender
    new_b.location = encrypt_RSA(r_key, decrypt_RSA(a_key, b.location))
    new_b.description = encrypt_RSA(r_key, decrypt_RSA(a_key, b.description))
    new_b.is_encrypted = True
    new_b.is_public = False 
    new_b.is_searchable = False
    new_b.folder = b.folder
    new_b.docfile = b.docfile
    new_b.doc_key = encrypt_RSA(r_key, decrypt_RSA(a_key, b.doc_key))
    new_b.currently_encrypted = b.currently_encrypted
    new_b.save()
    notification.delete()
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
        
@login_required
def manage_user(request):
    updated_password = None
    updated_ssh = None
    updated_public = None
    form = UserEditForm()
    if request.method == "POST":
        form = UserEditForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['current_password'] != '' and form.cleaned_data['new_password'] != '' and form.cleaned_data['confirm_new_password'] != '':
                if authenticate(username=request.user.username, password = form.cleaned_data['current_password']):
                    if form.cleaned_data['new_password'] == form.cleaned_data['confirm_new_password']:
                        us = UserProfile.objects.filter(user=request.user)[0]
                        u = us.user
                        u.set_password(form.cleaned_data['new_password'])
                        u.save()
                        us.save()
                        updated_password = 'Your password has been updated'
                    else:
                        updated_password = 'Your new passwords did not match'
                else:
                    updated_password = 'You entered your current password incorrectly'
            else:
                if form.cleaned_data['current_password'] != '' or form.cleaned_data['new_password'] != '' or form.cleaned_data['confirm_new_password'] != '':
                    updated_password = 'You need to enter all of the fields to updated your password'
            if form.cleaned_data['private_key_loc'] != '' and form.cleaned_data['public_key_loc'] != '':
                us = UserProfile.objects.filter(user=request.user)[0]
                us.public_key = form.cleaned_data['public_key_loc']
                us.private_key = form.cleaned_data['private_key_loc']
                us.save()
                updated_ssh = 'Your ssh keys have been updated'
            else:
                if form.cleaned_data['private_key_loc'] != '' or form.cleaned_data['public_key_loc'] != '':
                    updated_ssh = 'You need to enter all of the fields to update your SSH keys'
            if form.cleaned_data['make_public'] and form.cleaned_data['make_private']:
                updated_public = 'You cannot make your account both public and private'
            elif form.cleaned_data['make_public']:
                us = UserProfile.objects.filter(user=request.user)[0]
                us.is_public = True
                us.save()
                updated_public = 'You succesfully made your account public'
            elif form.cleaned_data['make_private']:
                us = UserProfile.objects.filter(user=request.user)[0]
                us.is_public = False
                us.save()
                updated_public = 'You succesfully made your account private'
        else:
            return HttpResponseRedirect('/manage')
        return render(request, 'secure_witness/account_manage.html', {'form': form, 'user': UserProfile.objects.filter(user=request.user)[0], 'updated_password':updated_password, 'updated_ssh':updated_ssh, 'updated_public':updated_public})
    else:
        return render(request, 'secure_witness/account_manage.html', {'form': form, 'user': UserProfile.objects.filter(user=request.user)[0], 'updated_password':updated_password, 'updated_ssh':updated_ssh, 'updated_public':updated_public})

@login_required
def delete_user(request):
    message = None
    if request.method == "POST":
        form = UserDeleteForm(request.POST)
        if form.is_valid():
            if not form.cleaned_data['keep_data']:
                message = 'You must confirm'
                return render(request, 'secure_witness/delete_user.html', {'form': form, 'user': request.user, 'message':message})
            else:
                us = UserProfile.objects.filter(user=request.user)[0]
                u = us.user
                u.delete()
                us.delete()
                
                #ADD CODE TO DELETE ASSOCIATED BULLETINS
                
                return HttpResponseRedirect('/')
        else:
            return HttpResponseRedirect('/')
    else:
        form = UserDeleteForm()
    return render(request, 'secure_witness/delete_user.html', {'form': form, 'user': request.user, 'message':message})
    
@login_required
def create_folder(request):
    if request.method == "POST":
        form = FolderForm(request.POST)
        if form.is_valid():
            f = Folder()
            f.title = form.cleaned_data['title']
            f.parent_folder = form.cleaned_data['parent_folder']
            f.is_global = True
            f.owner = request.user
            f.save()
        return HttpResponseRedirect('/')
    else:
        form = FolderForm()
    return render(request, 'secure_witness/create_folder.html', {'form': form})

def create_private_folder(request):
    if request.method == "POST":
        form = PrivateFolderForm(request.POST)
        if form.is_valid():
            f = Folder()
            f.title = form.cleaned_data['title']
            f.parent_folder = form.cleaned_data['parent_folder']
            f.is_global = False
            f.owner = request.user
            f.save()
        return HttpResponseRedirect('/')
    else:
        form = PrivateFolderForm()
    return render(request, 'secure_witness/create_private_folder.html', {'form': form})

@login_required
def detail_folder(request, folder_id):
    f = get_object_or_404(Folder, pk=folder_id)
    bulletin_list = Bulletin.objects.filter(folder = f)
    private_bulletins = Bulletin.objects.filter(private_folder = f)
    subfolder_list = Folder.objects.filter(parent_folder = f)
    user = request.user
    return render(request, 'secure_witness/detail_folder.html', {'folder': f, 'subfolder_list': subfolder_list, 'bulletin_list': bulletin_list, 'user':user, 'private_bulletins': private_bulletins})

@login_required
def delete_folder(request, folder_id):
    f = get_object_or_404(Folder, pk=folder_id)
    f.delete()
    return HttpResponseRedirect('/')

@login_required
def edit_folder(request, folder_id):
    f = get_object_or_404(Folder, pk=folder_id) 
    if request.method == "POST":
        form = PrivateFolderForm(request.POST)
        if form.is_valid():
            f.title = form.cleaned_data['title']
            f.parent_folder = form.cleaned_data['parent_folder']
            f.save()
        return HttpResponseRedirect('/')
    else:
        form = PrivateFolderForm(initial={'title':f.title})
    return render(request, 'secure_witness/edit_folder.html', {'folder': f, 'form': form})
# Create your views here.

def all_global_folders(request):
    return render(request, 'secure_witness/all_global_folders.html', {'folder_list':Folder.objects.filter(is_global=True).filter(parent_folder__isnull=True)})
    
def all_private_folders(request):
    return render(request, 'secure_witness/all_private_folders.html', {'folder_list':Folder.objects.filter(is_global=False).filter(owner=request.user).filter(parent_folder__isnull=True)})

def all_my_bulletins(request):
    return render(request, 'secure_witness/all_my_bulletins.html', {'bulletin_list':Bulletin.objects.filter(author=request.user)})

def all_followed_bulletins(request):
    return render(request, 'secure_witness/all_followed_bulletins.html', {'fol_list':Follow.objects.filter(owner=request.user)})

def all_public_bulletins(request):
    return render(request, 'secure_witness/all_public_bulletins.html', {'pub_bulletins':Bulletin.objects.filter(is_public=True)})

def copy_bulletin(request, bulletin_id):
    bulletin = get_object_or_404(Bulletin, pk=bulletin_id)
    if request.method == "POST":
        form = CopyForm(request.POST)
        if form.is_valid():
            bulletin.private_folder = form.cleaned_data['folder']
            bulletin.save()
        return HttpResponseRedirect('/')
    else:
        form = CopyForm()
    return render(request, 'secure_witness/copy_bulletin.html', {'form': form, 'bulletin': bulletin})
