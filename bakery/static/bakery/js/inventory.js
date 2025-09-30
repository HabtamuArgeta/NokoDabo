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

    // When the product type changes, fetch names
    productTypeSelect.addEventListener('change', function () {
        loadProducts(this.value, null);
    });

    // If the form was rendered with a product_type (edit page), auto-load names
    const initialType = productTypeSelect.value;
    // If server-side form populated choices, we don't need AJAX; but loading again is safe.
    if (initialType) {
        // try to read initial selected id from the form's hidden data set by Django form initial
        const initialSelected = document.getElementById("id_product_choice") ? document.getElementById("id_product_choice").value : null;
        loadProducts(initialType, initialSelected);
    }
});
