# productos/forms.py
from django import forms
from .models import CatalogoProveedor

class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField(label='Selecciona tu archivo Excel (.xlsx)')

class CatalogoProveedorForm(forms.ModelForm):
    class Meta:
        model = CatalogoProveedor
        fields = ['archivo']