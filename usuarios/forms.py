from django import forms


class EmailForm(forms.Form):
    para = forms.CharField(
        widget=forms.Textarea(attrs={'cols': 40, 'rows': 1}), required=True)
    asunto = forms.CharField(
        widget=forms.Textarea(attrs={'cols': 40, 'rows': 1}), required=False)
    mensaje = forms.CharField(
        widget=forms.Textarea(attrs={'cols': 40, 'rows': 15}), required=False)

    personalizado = forms.BooleanField(required=False)
