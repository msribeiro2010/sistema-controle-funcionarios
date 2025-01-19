from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Funcionario

class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True)
    nome = forms.CharField(max_length=100)
    matricula = forms.CharField(max_length=20)
    cargo = forms.ChoiceField(choices=Funcionario.CARGO_CHOICES)

    class Meta:
        model = User
        fields = ['username', 'email', 'nome', 'matricula', 'cargo', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = 'Obrigatório. 150 caracteres ou menos. Letras, números e @/./+/-/_ apenas.'
        self.fields['password1'].help_text = '''
            <ul>
                <li>Sua senha não pode ser muito parecida com suas outras informações pessoais.</li>
                <li>Sua senha precisa conter pelo menos 8 caracteres.</li>
                <li>Sua senha não pode ser uma senha comumente utilizada.</li>
                <li>Sua senha não pode ser inteiramente numérica.</li>
            </ul>
        '''
        self.fields['password2'].help_text = 'Digite a mesma senha novamente, para verificação.'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            Funcionario.objects.create(
                usuario=user,
                nome=self.cleaned_data['nome'],
                matricula=self.cleaned_data['matricula'],
                cargo=self.cleaned_data['cargo'],
                dias_ferias_disponiveis=30
            )
        return user 