from django.shortcuts import render
from django.template import loader
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.conf import settings
import os

from .models import Document
from .forms import DocumentForm
from .scheduler import create_schedule

def list(request):
    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():

	        # grab the file
            newdoc = Document(docfile=request.FILES['docfile'])
            
            # save just to media folder (save adds to db and media. delete
            # removes from db)
            newdoc.save()
            newdoc.delete()

            # build the schedule
            file_path = os.path.join(settings.MEDIA_ROOT, request.FILES['docfile'].name)
            response = create_schedule(file_path)
            
            if response == 'Failed':
            	# error handling here
            	return

            # Redirect to the document list after POST
            return response
    else:
        # Document.objects.all().delete()
        form = DocumentForm() # A empty, unbound form

    # Load documents for the list page
    documents = Document.objects.all()

    # Render list page with the documents and the form
    template = loader.get_template('app/list.html')
    context = {'documents': documents, 'form': form} 
    return HttpResponse(template.render(context, request))

def add(request):
    # create new examples
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():

	        # grab the file and save it 
            newdoc = Document(docfile=request.FILES['docfile'])
            newdoc.save()
    	
            return HttpResponseRedirect(reverse('add'))

    else:
    	# once example is uploaded, just return back to same page
        form = DocumentForm()

    # Render add page with the documents and the form
    template = loader.get_template('app/add.html')
    context = {'form': form} 
    return HttpResponse(template.render(context, request))