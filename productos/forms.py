# productos/forms.py
from django import forms

class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField(
        label='Archivo',
        required=True,
        widget=forms.FileInput(attrs={'accept': '.xlsx,.xls,.pdf'})  # ✅ aquí permites PDF también
    )

class ArrobaCatalogForm(forms.Form):
    archivo = forms.FileField(
        label='Catálogo de Arroba (.xlsx)',
        help_text='Sube un archivo Excel del proveedor Arroba'
    )

class ProceCatalogForm(forms.Form):
    archivo = forms.FileField(
        label='Catálogo de Proce (.xlsx)',
        help_text='Sube un archivo Excel del proveedor Proce'
    )

class TechsmartCatalogForm(forms.Form):
    archivo = forms.FileField(
        label='Catálogo de Techsmart (.pdf)',
        help_text='Sube un archivo PDF del proveedor Techsmart'
    )