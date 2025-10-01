document.addEventListener('DOMContentLoaded', function() {
    console.log("--> catalogo.js cargado y DOMContentLoaded disparado!"); // Añade esta línea
    
    const catalogoGrid = document.getElementById('catalogo-grid');
    const computadorasArmadasGrid = document.getElementById('computadoras-armadas-grid');
    console.log("catalogoGrid encontrado:", catalogoGrid); // Añade esta línea
    console.log("computadorasArmadasGrid encontrado:", computadorasArmadasGrid); // Añade esta línea

    const busquedaProductoInput = document.getElementById('busqueda-producto');
    const filtroExistenciaCheckbox = document.getElementById('filtro-existencia');
    const filtrosCategoriasContainer = document.getElementById('filtros-categorias');
    const prevPageButton = document.getElementById('prev-page');
    const nextPageButton = document.getElementById('next-page');
    const pageNumbersContainer = document.getElementById('page-numbers');
    const totalProductosSpan = document.getElementById('total-productos');
    const pageInfoSpan = document.getElementById('page-info'); // Asegúrate de tener este span en tu HTML

    // Modales y carrito
    /*
    const cartButton = document.getElementById('cart-button');
    const cartModal = document.getElementById('cart-modal');
    const cerrarCartModal = document.getElementById('cerrar-cart-modal');
    const cartItemsContainer = document.getElementById('cart-items-container');
    const cartCountSpan = document.getElementById('cart-count');
    const cartTotalItemsSpan = document.getElementById('cart-total-items');
    const cartTotalPriceSpan = document.getElementById('cart-total-price');
    const emptyCartMessage = document.getElementById('empty-cart-message');
    const clearCartButton = document.getElementById('clear-cart-button');
    */
    // Modal de detalles del producto
    const productoModal = document.getElementById('producto-modal');
    const closeProductoModal = document.getElementById('close-producto-modal');
    const modalImagen = document.getElementById('modal-imagen');
    const modalNombre = document.getElementById('modal-nombre');
    const modalDescripcionProd = document.getElementById('modal-descripcion-prod');
    const modalDescripcion2Prod = document.getElementById('modal-descripcion2-prod');
    const modalPrecio = document.getElementById('modal-precio');
    const modalCantidadInput = document.getElementById('modal-cantidad');
    const agregarModalCarritoButton = document.getElementById('agregar-modal-carrito');
    const modalExistencia = document.getElementById('modal-existencia');
    const modalGarantia = document.getElementById('modal-garantia');
    const listaCaracteristicasAdicionales = document.getElementById('lista-caracteristicas-adicionales');


    // Variables globales
    let productos = [];
    let categorias = [];
    let currentPage = 1;
    let itemsPerPage = 6; // Mostrar 6 productos por página por defecto
    /*let cart = JSON.parse(localStorage.getItem('cart')) || {}; // Cargar carrito de localStorage
    /*
    // Eventos para abrir/cerrar modal de carrito
    if (cartButton && cartModal && cerrarCartModal && clearCartButton) {
        cartButton.addEventListener('click', () => {
            cartModal.style.display = 'block';
            updateCartDisplay();
        });

        cerrarCartModal.addEventListener('click', () => {
            cartModal.style.display = 'none';
        });

        clearCartButton.addEventListener('click', () => {
            if (confirm('¿Estás seguro de que quieres vaciar el carrito?')) {
                cart = {};
                localStorage.setItem('cart', JSON.stringify(cart));
                updateCartDisplay();
            }
        });
    }
    */
    // Evento para cerrar modal al hacer clic fuera
    window.addEventListener('click', (event) => {
     //   if (event.target == cartModal) {
       //     cartModal.style.display = 'none';
        //}
        if (event.target == productoModal) {
            productoModal.style.display = 'none';
        }
    });

    // Evento para cerrar modal de producto
    if (closeProductoModal && productoModal) {
        closeProductoModal.addEventListener('click', () => {
            productoModal.style.display = 'none';
        });
    }

    // >>> Delegación de eventos para los clics en botones de producto (Ver Detalles y Agregar al Carrito) <<<
    // Esto es más robusto para elementos que se cargan dinámicamente
    // Dentro de document.addEventListener('DOMContentLoaded', function() { ...
    if (catalogoGrid) {
        catalogoGrid.addEventListener('click', (e) => {
            console.log('Elemento clicado (e.target):', e.target);        // <-- ¡AÑADE ESTA LÍNEA!
            console.log('Clases del elemento clicado:', e.target.classList); // <-- ¡AÑADE ESTA LÍNEA!

            if (e.target.classList.contains('ver-detalles')) {
                const sku = e.target.dataset.sku;
                console.log('Delegación: Botón "Ver Detalles" clicado para SKU:', sku);
                mostrarDetallesProducto(sku);
            }/* else if (e.target.classList.contains('agregar-carrito')) {
                const sku = e.target.dataset.sku;
                const producto = productos.find(p => p.sku === sku);
                if (producto) {
                    agregarAlCarrito(producto, 1);
                }
            }*/
        });
    }

    if (computadorasArmadasGrid && computadorasArmadasGrid !== catalogoGrid) {
        computadorasArmadasGrid.addEventListener('click', (e) => {
            console.log('Elemento clicado (e.target - Armadas):', e.target);        // <-- ¡AÑADE ESTA LÍNEA!
            console.log('Clases del elemento clicado (Armadas):', e.target.classList); // <-- ¡AÑADE ESTA LÍNEA!

            if (e.target.classList.contains('ver-detalles')) {
                const sku = e.target.dataset.sku;
                console.log('Delegación: Botón "Ver Detalles" (Armadas) clicado para SKU:', sku);
                mostrarDetallesProducto(sku);
            }/* else if (e.target.classList.contains('agregar-carrito')) {
                const sku = e.target.dataset.sku;
                const producto = productos.find(p => p.sku === sku);
                if (producto) {
                    agregarAlCarrito(producto, 1);
                }
            }*/
        });
    }

    // Helper para renderizar un solo producto
    function renderizarProducto(producto, container) {
        const productCard = document.createElement('div');
        productCard.className = 'product-card';
        productCard.innerHTML = `
            <img src="${producto.imagen || '/static/img/no_image.png'}" alt="${producto.nombre}" class="product-image">
            <h3 class="product-title">${producto.nombre}</h3>
            <p class="product-description">${producto.descripcion || ''}</p>
            <p class="product-category">${producto.categoria_nombre}</p>
            <p class="product-price">$${producto.precio_mxn ? parseFloat(producto.precio_mxn).toFixed(2) : 'N/A'} MXN</p>
            <p class="product-stock">${producto.inventario > 0 ? `En existencia: ${producto.inventario}` : 'Agotado'}</p>
            <div class="product-actions">
                <button class="btn btn-primary ver-detalles" data-sku="${producto.sku}">Ver Detalles</button>

                </div>
        `;
        container.appendChild(productCard);
    }

    // Función para cargar productos de la API
    async function fetchProductos() {
        try {
            const response = await fetch('/api/productos/');
            const data = await response.json();
            productos = data;
            console.log('Productos cargados:', productos);
            fetchCategorias(); // Cargar categorías después de los productos
            aplicarFiltros(); // Aplicar filtros iniciales y renderizar
         //   updateCartDisplay(); // Actualizar el carrito al cargar la página
        } catch (error) {
            console.error('Error al cargar productos:', error);
            if (catalogoGrid) {
                catalogoGrid.innerHTML = '<p>Error al cargar los productos. Inténtalo de nuevo más tarde.</p>';
            }
        }
    }

    // Función para cargar y renderizar filtros de categoría
    function fetchCategorias() {
        const uniqueCategories = new Set();
        productos.forEach(p => {
            if (p.categoria_nombre) {
                uniqueCategories.add(p.categoria_nombre);
            }
        });
        categorias = Array.from(uniqueCategories).sort();
        renderizarFiltrosCategorias();
    }

    function renderizarFiltrosCategorias() {
        if (filtrosCategoriasContainer) {
            filtrosCategoriasContainer.innerHTML = '<button class="filtro-categoria active" data-categoria="">Todas</button>';
            categorias.forEach(categoria => {
                const button = document.createElement('button');
                button.className = 'filtro-categoria';
                button.dataset.categoria = categoria;
                button.textContent = categoria;
                filtrosCategoriasContainer.appendChild(button);
            });

            // Event listener para los botones de filtro de categoría
            filtrosCategoriasContainer.addEventListener('click', (e) => {
                if (e.target.classList.contains('filtro-categoria')) {
                    // Remover 'active' de todos los botones
                    document.querySelectorAll('.filtro-categoria').forEach(btn => btn.classList.remove('active'));
                    // Añadir 'active' al botón clickeado
                    e.target.classList.add('active');

                    currentFilters.category = e.target.dataset.categoria || '';
                    currentPage = 1; // Reiniciar paginación al cambiar filtro
                    aplicarFiltros();
                }
            });
        }
    }


    // Objeto para almacenar los filtros actuales
    let currentFilters = {
        searchTerm: '',
        category: '',
        in_stock: false
    };

    // Función para aplicar filtros y renderizar productos
    function aplicarFiltros() {
        let productosFiltrados = [...productos]; // Clonar el array original

        // 1. Filtrar por búsqueda
        if (currentFilters.searchTerm) {
            const searchTermLower = currentFilters.searchTerm.toLowerCase();
            productosFiltrados = productosFiltrados.filter(p =>
                (p.nombre && p.nombre.toLowerCase().includes(searchTermLower)) ||
                (p.descripcion && p.descripcion.toLowerCase().includes(searchTermLower)) ||
                (p.sku && p.sku.toLowerCase().includes(searchTermLower)) ||
                (p.categoria_nombre && p.categoria_nombre.toLowerCase().includes(searchTermLower))
            );
        }

        // 2. Filtrar por categoría
        if (currentFilters.category) {
            productosFiltrados = productosFiltrados.filter(producto =>
                producto.categoria_nombre && producto.categoria_nombre.toLowerCase() === currentFilters.category.toLowerCase()
            );
        }

        // 3. Filtrar por existencia
        if (currentFilters.in_stock) {
            productosFiltrados = productosFiltrados.filter(producto => producto.inventario > 0);
        }

        renderizarProductos(productosFiltrados);
        updatePaginationButtons(productosFiltrados.length);
    }

    // Función para renderizar todos los productos filtrados y paginados
    function renderizarProductos(productosFiltrados) {
        if (catalogoGrid) {
            catalogoGrid.innerHTML = ''; // Limpia el grid principal
        }
        if (computadorasArmadasGrid) {
            computadorasArmadasGrid.innerHTML = ''; // Limpia el grid de computadoras armadas
        }

        // Paginación
        const startIndex = (currentPage - 1) * itemsPerPage;
        const endIndex = startIndex + itemsPerPage;
        const productosPaginados = productosFiltrados.slice(startIndex, endIndex);

        productosPaginados.forEach(producto => {
            renderizarProducto(producto, catalogoGrid);
        });

        // Solo mostrar los 3 primeros productos para el carrusel de "Computadoras Armadas"
        const computadorasArmadas = productosFiltrados.filter(p =>
            p.categoria_nombre && p.categoria_nombre.toLowerCase().includes('computadora armada')
        ).slice(0, 3);

        computadorasArmadas.forEach(producto => {
            renderizarProducto(producto, computadorasArmadasGrid);
        });

        if (totalProductosSpan) {
            totalProductosSpan.textContent = productosFiltrados.length;
        }

        if (pageInfoSpan) {
            const totalPages = Math.ceil(productosFiltrados.length / itemsPerPage);
            pageInfoSpan.textContent = `Página ${currentPage} de ${totalPages || 1}`;
        }
    }


    // Lógica de paginación
    function updatePaginationButtons(totalItems) {
        const totalPages = Math.ceil(totalItems / itemsPerPage);
        if (prevPageButton) prevPageButton.disabled = currentPage === 1;
        if (nextPageButton) nextPageButton.disabled = currentPage === totalPages || totalPages === 0;

        // Renderizar números de página
        if (pageNumbersContainer) {
            pageNumbersContainer.innerHTML = '';
            for (let i = 1; i <= totalPages; i++) {
                const pageButton = document.createElement('button');
                pageButton.className = `page-number ${i === currentPage ? 'active' : ''}`;
                pageButton.textContent = i;
                pageButton.addEventListener('click', () => {
                    currentPage = i;
                    aplicarFiltros();
                });
                pageNumbersContainer.appendChild(pageButton);
            }
        }
    }

    // Event listeners para controles de paginación
    if (prevPageButton) {
        prevPageButton.addEventListener('click', () => {
            if (currentPage > 1) {
                currentPage--;
                aplicarFiltros();
            }
        });
    }

    if (nextPageButton) {
        nextPageButton.addEventListener('click', () => {
            const totalItems = currentFilters.searchTerm || currentFilters.category || currentFilters.in_stock ?
                productos.filter(p => {
                    let match = true;
                    if (currentFilters.searchTerm) {
                        const searchTermLower = currentFilters.searchTerm.toLowerCase();
                        if (!((p.nombre && p.nombre.toLowerCase().includes(searchTermLower)) ||
                                (p.descripcion && p.descripcion.toLowerCase().includes(searchTermLower)) ||
                                (p.sku && p.sku.toLowerCase().includes(searchTermLower)) ||
                                (p.categoria_nombre && p.categoria_nombre.toLowerCase().includes(searchTermLower)))) {
                            match = false;
                        }
                    }
                    if (currentFilters.category && (!p.categoria_nombre || p.categoria_nombre.toLowerCase() !== currentFilters.category.toLowerCase())) {
                        match = false;
                    }
                    if (currentFilters.in_stock && p.inventario <= 0) {
                        match = false;
                    }
                    return match;
                }).length : productos.length; // Si no hay filtros, usa el total de productos

            const totalPages = Math.ceil(totalItems / itemsPerPage);

            if (currentPage < totalPages) {
                currentPage++;
                aplicarFiltros();
            }
        });
    }


    // Event listeners para filtros de búsqueda y existencia
    if (busquedaProductoInput) {
        busquedaProductoInput.addEventListener('input', () => {
            currentFilters.searchTerm = busquedaProductoInput.value;
            currentPage = 1; // Reiniciar paginación
            aplicarFiltros();
        });
    }

    if (filtroExistenciaCheckbox) {
        filtroExistenciaCheckbox.addEventListener('change', () => {
            currentFilters.in_stock = filtroExistenciaCheckbox.checked;
            currentPage = 1; // Reiniciar paginación
            aplicarFiltros();
        });
    }


    // Funciones del carrito de compras
   /*function agregarAlCarrito(producto, cantidad) {
        if (producto.inventario === 0) {
            alert('Producto agotado. No se puede agregar al carrito.');
            return;
        }

        const currentQuantityInCart = cart[producto.sku] ? cart[producto.sku].cantidad : 0;
        const newQuantity = currentQuantityInCart + cantidad;

        if (newQuantity > producto.inventario) {
            alert(`No hay suficiente inventario para agregar ${cantidad} unidades. Solo quedan ${producto.inventario - currentQuantityInCart} unidades disponibles.`);
            return;
        }

        cart[producto.sku] = {
            sku: producto.sku,
            nombre: producto.nombre,
            precio_mxn: parseFloat(producto.precio_mxn),
            cantidad: newQuantity,
            imagen: producto.imagen,
            inventario: producto.inventario // Para referencia en el carrito
        };
        localStorage.setItem('cart', JSON.stringify(cart));
        updateCartDisplay();
    }*/

    /*function removerDelCarrito(sku) {
        if (cart[sku]) {
            delete cart[sku];
            localStorage.setItem('cart', JSON.stringify(cart));
            updateCartDisplay();
        }
    }*/

    /*function actualizarCantidadCarrito(sku, nuevaCantidad) {
        if (cart[sku]) {
            const productoEnStock = productos.find(p => p.sku === sku);
            if (productoEnStock && nuevaCantidad > productoEnStock.inventario) {
                alert(`No puedes agregar más de ${productoEnStock.inventario} unidades de este producto.`);
                nuevaCantidad = productoEnStock.inventario; // Ajustar a la cantidad máxima
            }
            if (nuevaCantidad > 0) {
                cart[sku].cantidad = nuevaCantidad;
            } else {
                delete cart[sku]; // Eliminar si la cantidad es 0 o menos
            }
            localStorage.setItem('cart', JSON.stringify(cart));
            updateCartDisplay();
        }
    }*/

    /*function updateCartDisplay() {
        if (!cartItemsContainer || !cartCountSpan || !cartTotalItemsSpan || !cartTotalPriceSpan || !emptyCartMessage) {
            console.error("Elementos del carrito no encontrados en el DOM.");
            return;
        }

        cartItemsContainer.innerHTML = '';
        let totalItems = 0;
        let totalPrice = 0;

        for (const sku in cart) {
            const item = cart[sku];
            totalItems += item.cantidad;
            totalPrice += item.precio_mxn * item.cantidad;

            const cartItemDiv = document.createElement('div');
            cartItemDiv.className = 'cart-item';
            cartItemDiv.innerHTML = `
                <img src="${item.imagen || '/static/img/no_image.png'}" alt="${item.nombre}" class="cart-item-image">
                <div class="cart-item-details">
                    <h4>${item.nombre}</h4>
                    <p>Precio: $${item.precio_mxn.toFixed(2)} MXN</p>
                    <div class="cart-item-quantity-control">
                        <button class="btn-quantity decrease-quantity" data-sku="${item.sku}">-</button>
                        <input type="number" value="${item.cantidad}" min="1" max="${item.inventario}" class="item-quantity-input" data-sku="${item.sku}">
                        <button class="btn-quantity increase-quantity" data-sku="${item.sku}">+</button>
                    </div>
                    <p>Subtotal: $${(item.precio_mxn * item.cantidad).toFixed(2)} MXN</p>
                </div>
                <button class="btn-remove-item" data-sku="${item.sku}">&times;</button>
            `;
            cartItemsContainer.appendChild(cartItemDiv);
        }

        cartCountSpan.textContent = totalItems;
        cartTotalItemsSpan.textContent = totalItems;
        cartTotalPriceSpan.textContent = totalPrice.toFixed(2);

        if (totalItems === 0) {
            emptyCartMessage.style.display = 'block';
        } else {
            emptyCartMessage.style.display = 'none';
        }

        // Add event listeners for quantity controls and remove buttons
        document.querySelectorAll('.btn-remove-item').forEach(button => {
            button.addEventListener('click', (e) => {
                const sku = e.target.dataset.sku;
                removerDelCarrito(sku);
            });
        });

        document.querySelectorAll('.decrease-quantity').forEach(button => {
            button.addEventListener('click', (e) => {
                const sku = e.target.dataset.sku;
                const input = e.target.nextElementSibling;
                let newQuantity = parseInt(input.value) - 1;
                actualizarCantidadCarrito(sku, newQuantity);
            });
        });

        document.querySelectorAll('.increase-quantity').forEach(button => {
            button.addEventListener('click', (e) => {
                const sku = e.target.dataset.sku;
                const input = e.target.previousElementSibling;
                let newQuantity = parseInt(input.value) + 1;
                actualizarCantidadCarrito(sku, newQuantity);
            });
        });

        document.querySelectorAll('.item-quantity-input').forEach(input => {
            input.addEventListener('change', (e) => {
                const sku = e.target.dataset.sku;
                let newQuantity = parseInt(e.target.value);
                if (isNaN(newQuantity) || newQuantity < 1) {
                    newQuantity = 1; // Default to 1 if invalid
                }
                actualizarCantidadCarrito(sku, newQuantity);
            });
        });
    }*/


    // Función para mostrar detalles del producto en el modal
    function mostrarDetallesProducto(sku) {
        const producto = productos.find(p => p.sku === sku);
            console.log('Intentando mostrar detalles para producto:', producto); // <-- AÑADE ESTA LÍNEA
            console.log('Producto Modal Elemento:', productoModal); // <-- AÑADE ESTA LÍNEA
            console.log('Modal Nombre Elemento:', modalNombre); // <-- AÑADE ESTA LÍNEA

        if (producto && productoModal && modalImagen && modalNombre && modalDescripcionProd && modalPrecio && modalCantidadInput && agregarModalCarritoButton && modalExistencia && modalGarantia && listaCaracteristicasAdicionales) {
            modalImagen.src = producto.imagen || '/static/img/no_image.png';
            modalNombre.textContent = producto.nombre;
            modalDescripcionProd.textContent = producto.descripcion || '';
            modalDescripcion2Prod.textContent = producto.descripcion_corta || ''; // Asume un campo descripcion_corta si existe
            modalPrecio.textContent = `$${producto.precio_mxn ? parseFloat(producto.precio_mxn).toFixed(2) : 'N/A'} MXN`;
            modalCantidadInput.value = 1; // Resetea la cantidad
            modalCantidadInput.max = producto.inventario; // Establece el máximo según el inventario
            

            if (producto.inventario > 0) {
                modalExistencia.textContent = `En existencia: ${producto.inventario}`;
                modalExistencia.style.color = 'green';
           //     agregarModalCarritoButton.disabled = false;
            } else {
                modalExistencia.textContent = 'Agotado';
                modalExistencia.style.color = 'red';
           //     agregarModalCarritoButton.disabled = true;
            }

            modalGarantia.textContent = producto.garantia_meses ? `Garantía: ${producto.garantia_meses} meses` : '';

            // Limpiar y añadir características adicionales (esto es clave)
            listaCaracteristicasAdicionales.innerHTML = '';
            const caracteristicas = [
                { label: "Marca", value: producto.marca },
                { label: "Modelo Fabricante", value: producto.modelo_fabricante },
                { label: "Compatibilidad", value: producto.compatibilidad },
                { label: "Peso (kg)", value: producto.peso_kg },
                { label: "Número de Núcleos", value: producto.num_nucleos },
                { label: "Velocidad (GHz)", value: producto.velocidad_ghz },
                { label: "Memoria (GB)", value: producto.memoria_gb },
                { label: "Tipo de Memoria", value: producto.tipo_memoria },
                { label: "Capacidad (GB)", value: producto.capacidad_gb },
                { label: "Velocidad RAM (MHz)", value: producto.velocidad_mhz },
                { label: "Tipo de RAM", value: producto.tipo_ram },
            ];

            caracteristicas.forEach(char => {
                // Solo añadir si el valor no es null, vacío o indefinido
                if (char.value !== null && char.value !== '' && char.value !== undefined) {
                    const li = document.createElement('li');
                    li.textContent = `${char.label}: ${char.value}`;
                    listaCaracteristicasAdicionales.appendChild(li);
                }
            });

            /*// Configurar botón "Agregar al Carrito" del modal
            agregarModalCarritoButton.onclick = () => {
                const cantidad = parseInt(modalCantidadInput.value, 10);
                if (!isNaN(cantidad) && cantidad > 0 && cantidad <= producto.inventario) {
                    agregarAlCarrito(producto, cantidad);
                    productoModal.style.display = 'none';
                    alert(`Se agregaron ${cantidad} unidades de "${producto.nombre}" al carrito.`);
                } else {
                    alert('Cantidad inválida o excede el inventario disponible.');
                }
            };*/

            productoModal.style.display = 'block'; // Mostrar el modal
        } else {
            console.error('Error: Producto no encontrado o elementos del modal no definidos para SKU:', sku);
        }
    }

    // Iniciar la carga de productos al cargar la página
    fetchProductos();

    // Lógica para carrusel de computadoras armadas (sin paginación, solo desplazamiento)
    const computadorasPrevBtn = document.getElementById('computadoras-prev-btn');
    const computadorasNextBtn = document.getElementById('computadoras-next-btn');
    const computadorasArmadasContainer = document.getElementById('computadoras-armadas-grid'); // Ya tienes computadorasArmadasGrid

    if (computadorasPrevBtn && computadorasNextBtn && computadorasArmadasContainer) {
        computadorasNextBtn.addEventListener('click', () => {
            computadorasArmadasContainer.scrollBy({
                left: 300, // Ajusta este valor según el ancho de tus tarjetas de producto
                behavior: 'smooth'
            });
        });

        computadorasPrevBtn.addEventListener('click', () => {
            computadorasArmadasContainer.scrollBy({
                left: -300, // Ajusta este valor
                behavior: 'smooth'
            });
        });
    }
});