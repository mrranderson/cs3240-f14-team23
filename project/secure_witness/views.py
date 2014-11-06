from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from forms import UserForm
from django.contrib.auth import login
from secure_witness.models import Bulletin, Document

#def IndexView(request):
#	return HttpResponse("Index")

class IndexView(generic.ListView):
    template_name = 'secure_witness/index.html'
    context_object_name = 'bulletin_list'

    def get_queryset(self):
        return Bulletin.objects.filter(date_created__lte=timezone.now()).order_by('-date_created')[:5]

def lexusadduser(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            new_user = User.objects.create_user(**form.cleaned_data)
            login(new_user)
            # redirect, or however you want to get to the main view
            return HttpResponseRedirect('main.html')
    else:
        form = UserForm() 

    return render(request, 'secure_witness/adduser.html', {'form': form}) 
# Create your views here.
