from django import forms
from django.forms import inlineformset_factory
from .models import Licitacao, Anexo


class LicitacaoForm(forms.ModelForm):
    class Meta:
        model = Licitacao
        fields = ['titulo', 'orgao', 'objeto', 'modalidade', 'portal', 'data_abertura', 'valor_estimado', 'status', 'responsavel']
        
        # Vamos deixar os campos bonitos com CSS
        widgets = {
            'data_abertura': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'},
                format='%Y-%m-%dT%H:%M' # <--- ESSA LINHA RESOLVE O PROBLEMA!
            ),
            'objeto': forms.Textarea(attrs={'rows': 3}),
        }

    # Adiciona classe CSS em todos os campos automaticamente
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-input'})

# Isso cria um "pacote" de formulários de Anexo ligados à Licitação
AnexosFormSet = inlineformset_factory(
    Licitacao,
    Anexo,
    fields=['descricao', 'arquivo'],
    extra=1,              # Mostra 1 campo vazio para preencher
    can_delete=True       # Permite marcar uma caixinha para apagar anexos antigos
)