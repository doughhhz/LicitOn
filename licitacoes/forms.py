from django import forms
from .models import Licitacao

class LicitacaoForm(forms.ModelForm):
    class Meta:
        model = Licitacao
        fields = ['titulo', 'orgao', 'objeto', 'modalidade', 'portal', 'data_abertura', 'valor_estimado', 'status', 'responsavel']
        
        # Vamos deixar os campos bonitos com CSS
        widgets = {
            'data_abertura': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'objeto': forms.Textarea(attrs={'rows': 3}),
        }

    # Adiciona classe CSS em todos os campos automaticamente
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-input'})