# bakery/forms.py
from django import forms
from .models import Inventory, Bread, Injera, WheatFlour, Yeast, Enhancer, StockTransaction

MODEL_MAP = {
    'bread': Bread,
    'injera': Injera,
    'flour': WheatFlour,
    'yeast': Yeast,
    'enhancer': Enhancer,
}

class StockTransactionForm(forms.ModelForm):
    # product_choice will hold the product id
    product_choice = forms.ChoiceField(choices=[('', '---------')], required=True, label="Product Name")

    class Meta:
        model = StockTransaction
        fields = ['branch', 'product_type', 'product_choice', 'quantity', 'transaction_type']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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

            if self.instance and getattr(self.instance, 'product_name', None):
                try:
                    selected_obj = Model.objects.get(name=self.instance.product_name)
                    self.fields['product_choice'].initial = str(selected_obj.pk)
                except Model.DoesNotExist:
                    self.fields['product_choice'].initial = ''

    def clean_product_choice(self):
        val = self.cleaned_data.get('product_choice')
        if not val:
            raise forms.ValidationError("⚠️ Please select a product.")
        try:
            return int(val)
        except (ValueError, TypeError):
            raise forms.ValidationError("⚠️ Invalid selection.")

    def clean(self):
        """Validate stock availability before saving."""
        cleaned_data = super().clean()
        branch = cleaned_data.get("branch")
        product_type = cleaned_data.get("product_type")
        quantity = cleaned_data.get("quantity")
        transaction_type = cleaned_data.get("transaction_type")

        # Resolve product name
        product_id = cleaned_data.get("product_choice")
        Model = MODEL_MAP.get(product_type)
        product_name = None
        if Model and product_id:
            try:
                obj = Model.objects.get(pk=product_id)
                product_name = obj.name
            except Model.DoesNotExist:
                pass

        if transaction_type == "out" and branch and product_type and product_name:
            from .models import Inventory
            try:
                inventory = Inventory.objects.get(
                    branch=branch,
                    product_type=product_type,
                    product_name=product_name
                )
                if inventory.quantity < quantity:
                    raise forms.ValidationError(
                        f"❌ Not enough stock of {product_name} in {branch}. "
                        f"Available: {inventory.quantity}, requested: {quantity}."
                    )
            except Inventory.DoesNotExist:
                raise forms.ValidationError(
                    f"❌ No inventory record found for {product_name} in {branch}."
                )

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        product_id = self.cleaned_data.get('product_choice')

        Model = MODEL_MAP.get(instance.product_type)
        if Model:
            try:
                obj = Model.objects.get(pk=product_id)
                instance.product_name = obj.name
                instance.product_id = obj.pk
            except Model.DoesNotExist:
                instance.product_name = ""
                instance.product_id = None

        if commit:
            instance.save()
        return instance


    
class InventoryForm(forms.ModelForm):
    # A choice field shown to the user (holds product id values)
    product_choice = forms.ChoiceField(choices=[('', '---------')], required=True, label="Product Name")

    class Meta:
        model = Inventory
        # show only these four fields in the admin form
        fields = ['branch', 'product_type', 'product_choice', 'quantity']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Start with an empty choices list (will be filled by AJAX on new form)
        self.fields['product_choice'].choices = [('', '---------')]

        # Determine the current product_type (from POST, GET or instance)
        product_type = None
        # if form is bound, the product_type is in data
        if self.data.get('product_type'):
            product_type = self.data.get('product_type')
        # if editing existing instance, take existing product_type
        elif self.instance and getattr(self.instance, 'product_type', None):
            product_type = self.instance.product_type

        # If we have a product_type (either editing an instance or a posted value),
        # populate product_choice choices server-side (so the field is usable before JS)
        if product_type in MODEL_MAP:
            Model = MODEL_MAP[product_type]
            qs = Model.objects.all()
            choices = [('', '---------')] + [(str(o.pk), o.name) for o in qs]
            self.fields['product_choice'].choices = choices
            # if instance exists, set initial to the saved product_id
            if self.instance and getattr(self.instance, 'product_id', None):
                self.fields['product_choice'].initial = str(self.instance.product_id)

    def clean_product_choice(self):
        val = self.cleaned_data.get('product_choice')
        if not val:
            raise forms.ValidationError("Please select a product.")
        try:
            return int(val)
        except (ValueError, TypeError):
            raise forms.ValidationError("Invalid selection.")

    def save(self, commit=True):
        # Save model fields branch/product_type/quantity via ModelForm
        instance = super().save(commit=False)

        # product_choice holds the product id (int)
        product_id = self.cleaned_data.get('product_choice')
        instance.product_id = product_id

        # Set product_name from the actual model
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
