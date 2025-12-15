from django import forms
from django.forms import inlineformset_factory
from .models import Licitacao, Anexo, Cliente


class LicitacaoForm(forms.ModelForm):
    class Meta:
        model = Licitacao
        # MUDANÇA AQUI: Tirei 'orgao' e coloquei 'cliente' na lista
        fields = ['titulo', 'cliente', 'objeto', 'modalidade', 'portal', 'data_abertura', 'valor_estimado', 'status', 'responsavel']
        
        widgets = {
            'data_abertura': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'},
                format='%Y-%m-%dT%H:%M'
            ),
            'objeto': forms.Textarea(attrs={'rows': 3}),
            
            # Adicionei um estilo para o Dropdown do Cliente ficar bonito
            'cliente': forms.Select(attrs={'class': 'form-control form-input'}),
        }

    # Adiciona classe CSS em todos os campos automaticamente
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-input'})

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nome', 'cnpj', 'telefone', 'email', 'endereco', 'portal_padrao', 'observacoes']
        
        widgets = {
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-input'})

class ImportacaoJsonForm(forms.Form):
    arquivo_json = forms.FileField(
        label="Selecione o arquivo JSON",
        help_text="Faça upload do arquivo diário de licitações (.json)",
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.json'})
    )

class RelatorioForm(forms.Form):
    data_inicio = forms.DateField(
        label="De:",
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    data_fim = forms.DateField(
        label="Até:",
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    status = forms.ChoiceField(
        label="Status:",
        choices=[('', 'Todos os Status')] + Licitacao.STATUS_CHOICES, # Adiciona opção "Todos"
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    cliente = forms.ModelChoiceField(
        label="Cliente:",
        queryset=Cliente.objects.all(),
        required=False,
        empty_label="Todos os Clientes",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

# Isso cria um "pacote" de formulários de Anexo ligados à Licitação
AnexosFormSet = inlineformset_factory(
    Licitacao,
    Anexo,
    fields=['descricao', 'arquivo'],
    extra=1,              # Mostra 1 campo vazio para preencher
    can_delete=True       # Permite marcar uma caixinha para apagar anexos antigos
)