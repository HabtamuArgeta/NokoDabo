document.addEventListener("DOMContentLoaded", function () {
    const productTypeSelect = document.getElementById("id_product_type");
    const productChoiceSelect = document.getElementById("id_product_choice");

    if (!productTypeSelect || !productChoiceSelect) return;

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
                if (selectedId) productChoiceSelect.value = String(selectedId);
            })
            .catch(err => {
                productChoiceSelect.innerHTML = '<option value="">Error loading</option>';
                console.error("Error fetching products:", err);
            });
    }

    productTypeSelect.addEventListener('change', function () {
        loadProducts(this.value, null);
    });

    const initialType = productTypeSelect.value;
    const initialSelected = productChoiceSelect.value;
    if (initialType) loadProducts(initialType, initialSelected);
});
