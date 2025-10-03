# bakery/forms.py
from django import forms
from .models import Inventory, Bread, Injera, Flour, Yeast, Enhancer
from branches.models import Branch  # <-- use centralized Branch

MODEL_MAP = {
    'bread': Bread,
    'injera': Injera,
    'flour': Flour,
    'yeast': Yeast,
    'enhancer': Enhancer,
}


# ------------------- InventoryForm -------------------
class InventoryForm(forms.ModelForm):
    product_choice = forms.ChoiceField(choices=[('', '---------')], required=True, label="Product Name")

    class Meta:
        model = Inventory
        fields = ['branch', 'product_type', 'product_choice', 'quantity']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Use centralized branches
        self.fields['branch'].queryset = Branch.objects.all()

        self.fields['product_choice'].choices = [('', '---------')]
        product_type = None
        if self.data.get('product_type'):
            product_type = self.data.get('product_type')
        elif self.instance and getattr(self.instance, 'product_type', None):
            product_type = self.instance.product_type

        if product_type in MODEL_MAP:
            Model = MODEL_MAP[product_type]
            qs = Model.objects.all()
            choices = [('', '---------')] + [(str(o.pk), o.name) for o in qs]
            self.fields['product_choice'].choices = choices
            if self.instance and getattr(self.instance, 'product_id', None):
                self.fields['product_choice'].initial = str(self.instance.product_id)

        # ------------------- Quantity Label Customization -------------------
        if product_type in ['bread', 'injera']:
            self.fields['quantity'].label = "Quantity (Unit)"
        elif product_type in ['flour', 'yeast', 'enhancer']:
            self.fields['quantity'].label = "Quantity (KG)"
        else:
            self.fields['quantity'].label = "Quantity"

    def clean_product_choice(self):
        val = self.cleaned_data.get('product_choice')
        if not val:
            raise forms.ValidationError("Please select a product.")
        try:
            return int(val)
        except (ValueError, TypeError):
            raise forms.ValidationError("Invalid selection.")

    def save(self, commit=True):
        instance = super().save(commit=False)
        product_id = self.cleaned_data.get('product_choice')
        instance.product_id = product_id
        Model = MODEL_MAP.get(instance.product_type)
        if Model:
            try:
                obj = Model.objects.get(pk=product_id)
                instance.product_name = obj.name
            except Model.DoesNotExist:
                instance.product_name = ""
        if commit:
            instance.save()
        return instance