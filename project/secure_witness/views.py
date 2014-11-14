from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from forms import UserForm, BasicSearchForm, BulletinForm
from django.contrib.auth import login, authenticate, logout
from secure_witness.models import Bulletin, Document, Notification, Follow
from django.contrib.auth.models import User

#def IndexView(request):
#	return HttpResponse("Index")

@login_required
def IndexView(request):
    bulletin_list = Bulletin.objects.all()
    current_user = request.user
    notifications = Notification.objects.filter(recipient=current_user, has_read=False)
    if len(notifications) != 0:
        inbox_str = 'Inbox( ' + str(len(notifications)) + ' )'
    else:
        inbox_str = 'Inbox'
        
    your_bulletins = Bulletin.objects.filter(author=request.user)
    pub_bulletins = Bulletin.objects.filter(is_public=True)
    fol_bulletins = Follow.objects.filter(owner=request.user)
    
    return render(request, 'secure_witness/index.html', {'bulletin_list': bulletin_list, 'inbox_str': inbox_str, 'your_bulletins': your_bulletins, 'pub_bulletins': pub_bulletins, 'fol_bulletins': fol_bulletins}) 

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
            if password == confirm:
                new_user = User.objects.create_user(username=username, password=password)
                user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
                login(request,user)
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
        form = BulletinForm(request.POST)
        if form.is_valid():
            b = Bulletin()
            b.title = form.cleaned_data['title']
            b.location = form.cleaned_data['location']
            b.description = form.cleaned_data['description']
            b.author = request.user
            if(form.cleaned_data['is_public']):
                b.is_public = True
                b.is_searchable = True
            elif (form.cleaned_data['is_searchable']):
                b.is_public = False
                b.is_searchable = True
            else:
                b.is_public = False                                                                                                         
                b.is_searchable = False
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
        n.recipient = bulletin.author
        n.message = 'This is an automatic notification that user ' + str(request.user) + ' has requested access to your bulletin: ' + str(bulletin.title)
        n.bulletin = bulletin
        n.save()
    return HttpResponseRedirect('/')

@login_required
def detail_bulletin(request, bulletin_id):
    bulletin = get_object_or_404(Bulletin, pk=bulletin_id)

    #return render(request, 'secure_witness/detail_bulletin.html', {'bulletin': bulletin, 'user':request.user})

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
        form = BulletinForm(initial={'title': bulletin.title, 'description':bulletin.description, 'location':bulletin.location, 'is_public':bulletin.is_public, 'is_searchable':bulletin.is_searchable})
    return render(request, 'secure_witness/edit_bulletin.html', {'bulletin': bulletin, 'form': form})

@login_required
def delete_bulletin(request, bulletin_id):
    bulletin = get_object_or_404(Bulletin, pk=bulletin_id)
    bulletin.delete()
    return HttpResponseRedirect('/')

# Create your views here.
