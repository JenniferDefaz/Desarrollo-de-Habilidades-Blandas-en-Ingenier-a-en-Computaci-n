from django import forms
from .models import CustomUser, Role, SystemSetting, SupportTicket


class UserCreateForm(forms.ModelForm):
    """Formulario para crear un nuevo usuario."""
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese contraseña'})
    )
    password2 = forms.CharField(
        label='Confirmar Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirme contraseña'})
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'cedula', 'phone',
                  'institutional_email', 'role', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'cedula': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'institutional_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if self.cleaned_data.get('institutional_email'):
            user.email = self.cleaned_data['institutional_email']
        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    """Formulario para editar un usuario existente (sin contraseña)."""
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'cedula', 'phone',
                  'institutional_email', 'role', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'cedula': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'institutional_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data.get('institutional_email'):
            user.email = self.cleaned_data['institutional_email']
        if commit:
            user.save()
        return user


class ProfileEditForm(forms.ModelForm):
    """Formulario para que el usuario edite su propio perfil."""
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombres'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellidos'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo Electrónico'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'}),
        }


class SystemSettingForm(forms.ModelForm):
    """Formulario de configuración general del sistema (RF23)."""
    class Meta:
        model = SystemSetting
        fields = [
            'max_file_size_mb', 'allowed_file_extensions',
            'smtp_host', 'smtp_port', 'smtp_use_tls', 'system_email',
            'maintenance_mode'
        ]
        widgets = {
            'max_file_size_mb': forms.NumberInput(attrs={'class': 'form-control'}),
            'allowed_file_extensions': forms.TextInput(attrs={'class': 'form-control'}),
            'smtp_host': forms.TextInput(attrs={'class': 'form-control'}),
            'smtp_port': forms.NumberInput(attrs={'class': 'form-control'}),
            'smtp_use_tls': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'system_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'maintenance_mode': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class SupportTicketForm(forms.ModelForm):
    """Formulario para crear tickets de soporte técnico (RF23)."""
    class Meta:
        model = SupportTicket
        fields = ['subject', 'category', 'priority', 'description']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Dificultad al cargar evidencias'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describa en detalle su requerimiento o consulta de soporte...'}),
        }





