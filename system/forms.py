from django import forms

from .models import AttendanceRecord, CustomUser, Grade


class LoginForm(forms.Form):
    registration_number = forms.CharField(
        max_length=8,
        widget=forms.TextInput(attrs={"placeholder": "Digite seu número de matrícula"}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Digite sua senha"})
    )

    def clean(self):
        cleaned_data = super().clean()
        registration_number = cleaned_data.get("registration_number")
        password = cleaned_data.get("password")

        if not registration_number or not password:
            raise forms.ValidationError("Por favor, preencha todos os campos.")

        elif len(registration_number) < 8 or len(password) < 8:
            raise forms.ValidationError(
                "Número de matrícula e a senha devem ter 8 dígitos."
            )

        elif not CustomUser.objects.filter(
            registration_number=registration_number
        ).exists():
            raise forms.ValidationError("Número de matrícula não cadastrado.")

        return cleaned_data


class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ("value", "bimonthly")
        labels = {
            "value": "Nota",
            "bimonthly": "Bimestre",
        }
        widgets = {
            "value": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "placeholder": "Nota"}
            ),
            "bimonthly": forms.Select(
                attrs={"class": "form-control"},
                choices=[
                    (1, "1º Bimestre"),
                    (2, "2º Bimestre"),
                    (3, "3º Bimestre"),
                    (4, "4º Bimestre"),
                ],
            ),
        }


class GradeUpdateForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ("value", "bimonthly")
        labels = {
            "value": "Nota",
            "bimonthly": "Bimestre",
        }
        widgets = {
            "value": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "placeholder": "Nota"}
            ),
            "bimonthly": forms.Select(
                attrs={"class": "form-control"},
                choices=[
                    (1, "1º Bimestre"),
                    (2, "2º Bimestre"),
                    (3, "3º Bimestre"),
                    (4, "4º Bimestre"),
                ],
            ),
        }

        def save(self, commit=True):
            grade = super().save(commit=False)
            if commit:
                grade.save()
            return grade


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = AttendanceRecord
        fields = ["present"]
