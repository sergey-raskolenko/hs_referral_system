from django import forms


class LoginForm(forms.Form):
	phone = forms.CharField(label="Телефон", widget=forms.TextInput(attrs={'placeholder': 'Введите номер'}))

	def clean_phone(self):
		phone = self.cleaned_data.get('phone')
		return phone
