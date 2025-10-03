# finance/signals.py
from decimal import Decimal, InvalidOperation
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.apps import apps
from django.utils.module_loading import import_string

# Import Transaction model from finance (local import)
from .models import Transaction

# Try to find the StockTransaction model in common app names.
# Since you said it's under the StockTransaction app, we try that first.
POSSIBLE_STOCK_APPS = [
    ('StockTransaction', 'StockTransaction'),
    ('stocktransaction', 'StockTransaction'),
    ('stock_transaction', 'StockTransaction'),
    ('stock', 'StockTransaction'),
]

StockTransaction = None
for app_label, model_name in POSSIBLE_STOCK_APPS:
    try:
        StockTransaction = apps.get_model(app_label, model_name)
        if StockTransaction:
            break
    except LookupError:
        StockTransaction = None

# Helper to safely turn numbers into Decimals
def to_decimal(value):
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal('0.00')

# Helper to create Transaction records using only fields that exist on the model.
def create_transaction_safe(**kwargs):
    field_names = {f.name for f in Transaction._meta.get_fields() if hasattr(f, 'name')}
    data = {k: v for k, v in kwargs.items() if k in field_names}
    return Transaction.objects.create(**data)

# Only connect the receiver if we found the StockTransaction model
if StockTransaction is not None:
    @receiver(post_save, sender=StockTransaction)
    def handle_stocktransaction(sender, instance, created, **kwargs):
        """
        When a StockTransaction (stock-out of a finished good, or stock-in of raw material)
        is created, compute revenue and expense.

        Expected fields on StockTransaction (best-effort):
         - product_type: 'bread'|'injera'|'flour'|'yeast'|'enhancer'
         - product_id: int (pk of bakery product)
         - product_name: str
         - quantity: numeric
         - transaction_type: 'in' or 'out' (case-insensitive)
         - branch: optional FK (if your Transaction model accepts it)
        """
        if not created:
            return

        txn_dir = getattr(instance, 'transaction_type', '') or getattr(instance, 'type', '')
        txn_dir = str(txn_dir).lower()

        # Only handle stock-out events for finished goods for revenue/expense calculation
        # Consider common synonyms for out
        OUT_SYNS = {'out', 'stock_out', 'sold', 'remove', 'minus'}
        IN_SYNS = {'in', 'stock_in', 'receive', 'added', 'plus'}

        product_type = getattr(instance, 'product_type', None)
        product_id = getattr(instance, 'product_id', None)
        product_name = getattr(instance, 'product_name', None)
        branch = getattr(instance, 'branch', None)
        qty = to_decimal(getattr(instance, 'quantity', 0) or 0)

        # get bakery models via apps to avoid circular imports
        BakeryBread = apps.get_model('bakery', 'Bread')
        BakeryInjera = apps.get_model('bakery', 'Injera')
        BakeryFlour = apps.get_model('bakery', 'Flour')
        BakeryYeast = apps.get_model('bakery', 'Yeast')
        BakeryEnhancer = apps.get_model('bakery', 'Enhancer')

        # ---------- HANDLE FINISHED GOODS (bread, injera) on STOCK-OUT ----------
        if txn_dir in OUT_SYNS and product_type in ('bread', 'injera'):
            # load product instance
            prod = None
            try:
                if product_type == 'bread':
                    prod = BakeryBread.objects.get(pk=product_id) if product_id else None
                elif product_type == 'injera':
                    prod = BakeryInjera.objects.get(pk=product_id) if product_id else None
            except Exception:
                prod = None

            # revenue: selling price * qty
            selling_price = to_decimal(getattr(prod, 'selling_price', 0)) if prod else to_decimal(0)
            total_revenue = selling_price * qty

            # compute per-unit expense exactly as you specified:
            # per_unit = water_birr + electricity_birr
            #          + flour_kg * flour.cost_per_kg
            #          + yeast_kg * yeast.cost_per_kg
            #          + enhancer_kg * enhancer.cost_per_kg

            flour_amt = to_decimal(getattr(prod, 'flour_kg', 0)) if prod else to_decimal(0)
            yeast_amt = to_decimal(getattr(prod, 'yeast_kg', 0)) if prod else to_decimal(0)
            enhancer_amt = to_decimal(getattr(prod, 'enhancer_kg', 0)) if prod else to_decimal(0)
            water_cost = to_decimal(getattr(prod, 'water_birr', 0)) if prod else to_decimal(0)
            electricity_cost = to_decimal(getattr(prod, 'electricity_birr', 0)) if prod else to_decimal(0)

            # For raw-material unit costs, pick the most relevant record if available.
            # Simple/robust approach: use the first record of each raw material model (you can refine this later).
            flour_obj = BakeryFlour.objects.first()
            yeast_obj = BakeryYeast.objects.first()
            enhancer_obj = BakeryEnhancer.objects.first()

            flour_cost_per_kg = to_decimal(getattr(flour_obj, 'cost_per_kg', 0)) if flour_obj else to_decimal(0)
            yeast_cost_per_kg = to_decimal(getattr(yeast_obj, 'cost_per_kg', 0)) if yeast_obj else to_decimal(0)
            enhancer_cost_per_kg = to_decimal(getattr(enhancer_obj, 'cost_per_kg', 0)) if enhancer_obj else to_decimal(0)

            per_unit_raw = (flour_amt * flour_cost_per_kg) + (yeast_amt * yeast_cost_per_kg) + (enhancer_amt * enhancer_cost_per_kg)
            per_unit_total = per_unit_raw + water_cost + electricity_cost

            total_expense = per_unit_total * qty

            # Create revenue Transaction (fields set only if they exist on your Transaction model)
            create_transaction_safe(
                branch=branch,
                product_type=product_type,
                product_name=product_name or (getattr(prod, 'name', '') if prod else ''),
                quantity=float(qty) if 'quantity' in {f.name for f in Transaction._meta.get_fields()} else None,
                unit_price=selling_price,
                total_amount=total_revenue,
                transaction_type='revenue',
                source_app='StockTransaction',
                source_id=str(getattr(instance, 'pk', ''))
            )

            # Create expense Transaction with correct unit_price
            create_transaction_safe(
                branch=branch,
                product_type=product_type,
                product_name=product_name or (getattr(prod, 'name', '') if prod else ''),
                quantity=float(qty) if 'quantity' in {f.name for f in Transaction._meta.get_fields()} else None,
                unit_price=per_unit_total,
                total_amount=total_expense,
                transaction_type='expense',
                source_app='StockTransaction',
                source_id=str(getattr(instance, 'pk', ''))
            )

        # ---------- HANDLE RAW-MATERIAL STOCK-IN (expense) ----------
        elif txn_dir in IN_SYNS and product_type in ('flour', 'yeast', 'enhancer'):
            # For raw material purchases (stock in), cost = qty * cost_per_kg
            # Attempt to find the material record (by id or name), then use its cost_per_kg
            material_model = None
            if product_type == 'flour':
                material_model = BakeryFlour
            elif product_type == 'yeast':
                material_model = BakeryYeast
            elif product_type == 'enhancer':
                material_model = BakeryEnhancer

            material_obj = None
            try:
                if product_id:
                    material_obj = material_model.objects.get(pk=product_id)
            except Exception:
                material_obj = material_model.objects.filter().first() if material_model else None

            unit_cost = to_decimal(getattr(material_obj, 'cost_per_kg', 0)) if material_obj else to_decimal(0)
            total_cost = unit_cost * qty

            create_transaction_safe(
                branch=branch,
                product_type=product_type,
                product_name=product_name or (getattr(material_obj, 'name', '') if material_obj else ''),
                quantity=float(qty) if 'quantity' in {f.name for f in Transaction._meta.get_fields()} else None,
                unit_price=unit_cost,
                total_amount=total_cost,
                transaction_type='expense',
                source_app='StockTransaction',
                source_id=str(getattr(instance, 'pk', ''))
            )

# If StockTransaction could not be found, nothing will be connected (no change to application startup).