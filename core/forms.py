from django import forms
from .models import CreditApplication, CreditProduct

class CreditApplicationForm(forms.ModelForm):
    class Meta:
        model = CreditApplication
        fields = ['product', 'amount', 'phone']
        widgets = {
            'phone': forms.TextInput(attrs={'placeholder': '+79991234567'})
        }

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        product = self.cleaned_data.get('product')

        if product:
            if amount < product.min_amount:
                raise forms.ValidationError(f'Минимальная сумма: {product.min_amount:,} ₽')
            if amount > product.max_amount:
                raise forms.ValidationError(f'Максимальная сумма: {product.max_amount:,} ₽')
        return amount