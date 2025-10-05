# productos/forms.py
from django import forms

class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField(
        label='Archivo',
        required=True,
        widget=forms.FileInput(attrs={'accept': '.xlsx,.xls,.pdf'})  # ✅ aquí permites PDF también
    )