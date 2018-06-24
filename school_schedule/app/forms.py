from django import forms

# this is a subclass of the Form class from forms
class DocumentForm(forms.Form):

	# this is a FileField object
    docfile = forms.FileField(
        label='Select a file',
        help_text='max. 42 megabytes'
    )