// bakery/static/bakery/js/inventory.js
(function($) {
    $(document).ready(function() {
        var $productType = $('#id_product_type');
        var $quantityLabel = $('label[for="id_quantity"]');

        if (!$productType.length || !$quantityLabel.length) return;

        function updateQuantityLabel() {
            var val = $productType.val();
            if (val === 'bread' || val === 'injera') {
                $quantityLabel.text('Quantity (Unit)');
            } else if (val === 'flour' || val === 'yeast' || val === 'enhancer') {
                $quantityLabel.text('Quantity (KG)');
            } else {
                $quantityLabel.text('Quantity');
            }
        }

        // Initial update on page load
        updateQuantityLabel();

        // Update when product type changes
        $productType.on('change', function() {
            updateQuantityLabel();
        });

        // ------------------- Existing AJAX for product choices -------------------
        var $productChoice = $('#id_product_choice');

        function loadProducts(productType, selectedId) {
            if (!productType) {
                $productChoice.html('<option value="">---------</option>');
                return;
            }
            $productChoice.html('<option value="">Loading...</option>');
            $.getJSON('/bakery/get-products/', { product_type: productType })
                .done(function(data) {
                    $productChoice.html('<option value="">---------</option>');
                    $.each(data.products || [], function(_, p) {
                        $productChoice.append($('<option>', { value: p.id, text: p.name }));
                    });
                    if (selectedId) $productChoice.val(selectedId);
                })
                .fail(function() {
                    $productChoice.html('<option value="">Error loading</option>');
                    console.error('Error fetching products');
                });
        }

        $productType.on('change', function() {
            loadProducts(this.value, null);
        });

        // Initial load
        var initialType = $productType.val();
        var initialSelected = $productChoice.val() || null;
        if (initialType) loadProducts(initialType, initialSelected);
    });
})(django.jQuery);