from django import forms
from django.contrib.auth.forms import AuthenticationForm

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Ingrese su usuario',
        'id': 'username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Ingrese su contraseña',
        'id': 'password'
    }))
    remember = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={
        'class': 'form-check-input',
        'id': 'remember'
    }))

from .models import Carrera, User

class RegistroUsuarioForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control form-control-sm',
        'placeholder': 'email@estudiante.com ,@profesor.com ,@jefedecarrera.com' ,
        'id': 'reg_email'
    }), required=True)
    
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control form-control-sm',
        'placeholder': 'Clave',
        'id': 'reg_password1'
    }), required=True, label="Contraseña")
    
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control form-control-sm',
        'placeholder': 'Repetir',
        'id': 'reg_password2'
    }), required=True, label="Confirmar")

    carrera = forms.ModelChoiceField(
        queryset=Carrera.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select form-select-sm', 'id': 'reg_carrera'}),
        required=True,
        empty_label="Carrera..."
    )

    anio = forms.ChoiceField(
        choices=[(str(i), f"{i}°") for i in range(1, 6)],
        widget=forms.Select(attrs={'class': 'form-select form-select-sm', 'id': 'reg_anio'}),
        required=False,
        label="Año"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control form-control-sm', 
                'placeholder': 'Usuario',
                'id': 'reg_username'
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo electrónico ya está registrado.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        email = cleaned_data.get("email")

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Las contraseñas no coinciden.")

        # Validar lógica de estudiante vs profesor
        if email:
            domain = email.split('@')[-1].lower()
            if 'estudiante.com' in domain:
                if not cleaned_data.get('anio'):
                     self.add_error('anio', "El año es obligatorio para estudiantes.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            # Lógica de creación de perfil
            email = self.cleaned_data.get('email')
            domain = email.split('@')[-1].lower()
            carrera = self.cleaned_data.get('carrera')
            
            if 'profesor.com' in domain or 'jefedecarrera.com' in domain:
                from .models import Profesor
                nivel = 'jefe de carrera' if 'jefedecarrera.com' in domain else 'profesor'
                Profesor.objects.create(user=user, carrera=carrera, nivel=nivel)
            else:
                from .models import Estudiante
                anio = self.cleaned_data.get('anio')
                Estudiante.objects.create(user=user, carrera=carrera, año=anio)
        return user

from .models import Noticia

class NoticiaForm(forms.ModelForm):
    class Meta:
        model = Noticia
        fields = ['titulo', 'contenido', 'categoria', 'visible_para', 'carrera', 'anio']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título de la noticia'}),
            'contenido': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Contenido...'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'visible_para': forms.Select(attrs={'class': 'form-select'}),
            'carrera': forms.Select(attrs={'class': 'form-select'}),
            'anio': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Año (opcional)', 'min': '1', 'max': '5'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        visible_para = cleaned_data.get('visible_para')
        anio = cleaned_data.get('anio')
        carrera = cleaned_data.get('carrera')

        # Validación de rango de año
        if anio is not None:
            if anio < 1 or anio > 5:
                self.add_error('anio', "El año debe estar entre 1 y 5.")

        # Limpiar segmentación si es para todos
        if visible_para == 'todos':
            cleaned_data['carrera'] = None
            cleaned_data['anio'] = None
        
        return cleaned_data


from .models import Materia

class SubirNotasForm(forms.Form):
    archivo = forms.FileField(
        label='Archivo Excel',
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.xlsx,.xls'}),
        help_text='Formato: Columna A (Nombre), Columna B (Nota 0-5)'
    )
    carrera = forms.ModelChoiceField(
        queryset=Carrera.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'notas_carrera'}),
        empty_label="Seleccionar Carrera..."
    )
    anio = forms.ChoiceField(
        choices=[(str(i), f"{i}° Año") for i in range(1, 6)],
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'notas_anio'}),
        label="Año"
    )
    materia = forms.ModelChoiceField(
        queryset=Materia.objects.all(), # Se filtrará via JS y validará en view
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'notas_materia'}),
        empty_label="Seleccionar Materia..."
    )

    def clean_archivo(self):
        archivo = self.cleaned_data.get('archivo')
        if archivo:
            if not archivo.name.endswith(('.xlsx', '.xls')):
                raise forms.ValidationError("Solo se permiten archivos Excel (.xlsx, .xls)")
        return archivo

class SubirHorariosForm(forms.Form):
    archivo = forms.FileField(
        label='Archivo Excel',
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.xlsx,.xls'}),
        help_text='Formato: Materia, Día, Inicio, Fin, Aula'
    )
    carrera = forms.ModelChoiceField(
        queryset=Carrera.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'horarios_carrera'}),
        empty_label="Seleccionar Carrera..."
    )
    anio = forms.ChoiceField(
        choices=[(str(i), f"{i}° Año") for i in range(1, 6)],
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'horarios_anio'}),
        label="Año"
    )
    reemplazar = forms.BooleanField(
        required=False, 
        label="Reemplazar horarios existentes",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'horarios_reemplazar'})
    )

    def clean_archivo(self):
        archivo = self.cleaned_data.get('archivo')
        if archivo:
            if not archivo.name.endswith(('.xlsx', '.xls')):
                raise forms.ValidationError("Solo se permiten archivos Excel (.xlsx, .xls)")
        return archivo

