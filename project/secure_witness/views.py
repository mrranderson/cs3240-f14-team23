from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone

from secure_witness.models import Bulletin, Document

#def IndexView(request):
#	return HttpResponse("Index")

class IndexView(generic.ListView):
    template_name = 'secure_witness/index.html'
    context_object_name = 'bulletin_list'

    def get_queryset(self):
        return Bulletin.objects.filter(date_created__lte=timezone.now()).order_by('-date_created')[:5]

# Create your views here.
