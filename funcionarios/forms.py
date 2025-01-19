from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Funcionario

class RegistroForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    nome = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    matricula = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    cargo = forms.ChoiceField(
        choices=Funcionario.CARGO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text='Letras, números e @/./+/-/_ apenas.'
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Senha'
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Confirme a senha'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'nome', 'matricula', 'cargo', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Nome de usuário'
        self.fields['email'].label = 'E-mail'
        self.fields['nome'].label = 'Nome completo'
        self.fields['matricula'].label = 'Matrícula'
        self.fields['cargo'].label = 'Cargo'
        
        # Personalizando as mensagens de ajuda
        self.fields['username'].help_text = 'Obrigatório. 150 caracteres ou menos. Letras, números e @/./+/-/_ apenas.'
        self.fields['password1'].help_text = '''
            <small class="text-muted">
                <ul>
                    <li>Sua senha não pode ser muito parecida com suas outras informações pessoais.</li>
                    <li>Sua senha precisa conter pelo menos 8 caracteres.</li>
                    <li>Sua senha não pode ser uma senha comumente utilizada.</li>
                    <li>Sua senha não pode ser inteiramente numérica.</li>
                </ul>
            </small>
        '''
        self.fields['password2'].help_text = '<small class="text-muted">Digite a mesma senha novamente, para verificação.</small>'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este e-mail já está em uso.')
        return email

    def clean_matricula(self):
        matricula = self.cleaned_data.get('matricula')
        if Funcionario.objects.filter(matricula=matricula).exists():
            raise forms.ValidationError('Esta matrícula já está em uso.')
        return matricula

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