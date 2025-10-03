// bakery/static/bakery/js/inventory.js
document.addEventListener("DOMContentLoaded", function () {
    const productTypeSelect = document.getElementById("id_product_type");
    const productChoiceSelect = document.getElementById("id_product_choice");

    if (!productTypeSelect || !productChoiceSelect) {
        return; // not on this page
    }

    function loadProducts(productType, selectedId) {
        if (!productType) {
            productChoiceSelect.innerHTML = '<option value="">---------</option>';
            return;
        }
        productChoiceSelect.innerHTML = '<option value="">Loading...</option>';
        fetch('/bakery/get-products/?product_type=' + encodeURIComponent(productType))
            .then(resp => resp.json())
            .then(data => {
                productChoiceSelect.innerHTML = '<option value="">---------</option>';
                (data.products || []).forEach(function (p) {
                    const opt = document.createElement('option');
                    opt.value = p.id;
                    opt.textContent = p.name;
                    productChoiceSelect.appendChild(opt);
                });
                if (selectedId) {
                    productChoiceSelect.value = String(selectedId);
                }
            })
            .catch(err => {
                productChoiceSelect.innerHTML = '<option value="">Error loading</option>';
                console.error("Error fetching products:", err);
            });
    }

    // ------------------- Quantity Label Logic -------------------
    function updateQuantityLabel() {
        // Use a robust selector to find the label
        let quantityInput = document.getElementById('id_quantity');
        if (!quantityInput) return;

        let quantityLabel = quantityInput.closest('.form-row')?.querySelector('label');
        if (!quantityLabel) return;

        const value = productTypeSelect.value;
        if (value === 'bread' || value === 'injera') {
            quantityLabel.textContent = 'Quantity (Unit)';
        } else if (value === 'flour' || value === 'yeast' || value === 'enhancer') {
            quantityLabel.textContent = 'Quantity (KG)';
        } else {
            quantityLabel.textContent = 'Quantity';
        }
    }

    // ------------------- Event Listeners -------------------
    // Update quantity label on page load
    updateQuantityLabel();

    // Update quantity label when product type changes
    productTypeSelect.addEventListener('change', function () {
        loadProducts(this.value, null);
        updateQuantityLabel();
    });

    // If the form has an initial type (edit page), load products
    const initialType = productTypeSelect.value;
    const initialSelected = productChoiceSelect.value || null;
    if (initialType) {
        loadProducts(initialType, initialSelected);
    }
});