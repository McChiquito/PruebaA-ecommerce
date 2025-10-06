// Cargar productos desde la API
async function fetchProductos() {
    try {
        const response = await fetch("/api/productos/");
        const data = await response.json();

        const container = document.getElementById("catalogo-grid");
        const mensajeVacio = document.getElementById("mensaje-vacio");

        container.innerHTML = "";

        if (!data || data.length === 0) {
            mensajeVacio.style.display = "block";
            return;
        } else {
            mensajeVacio.style.display = "none";
        }

        data.forEach(producto => {
            renderizarProducto(producto, container);
        });

    } catch (error) {
        console.error("Error al cargar productos:", error);
    }
}

// Renderizar cada producto en una tarjeta
function renderizarProducto(producto, container) {
    const productCard = document.createElement('div');
    productCard.className = 'product-card';

    // Calcular precio principal (mínimo)
    const precioPrincipal = producto.precio_minimo
        ? `$${producto.precio_minimo.toFixed(2)} MXN`
        : 'N/A';

    // Construir lista de precios por proveedor
    let preciosProveedores = '';
    if (producto.precios_proveedor && producto.precios_proveedor.length > 0) {
        preciosProveedores = `
            <div class="proveedores-lista">
                <h4>Precios por proveedor:</h4>
                <ul>
                    ${producto.precios_proveedor.map(p => `
                        <li>${p.proveedor}: $${p.precio.toFixed(2)} MXN (Stock: ${p.stock})</li>
                    `).join('')}
                </ul>
            </div>
        `;
    }

    productCard.innerHTML = `
        <img src="${producto.imagen || '/static/img/no_image.png'}" alt="${producto.nombre || 'Producto'}" class="product-image">
        <h3 class="product-title">${producto.nombre || producto.sku}</h3>
        <p class="product-category">${producto.categoria_nombre || ''}</p>
        <p class="product-price">${precioPrincipal}</p>
        <p class="product-stock">${producto.inventario > 0 ? `En existencia: ${producto.inventario}` : 'Agotado'}</p>
        ${preciosProveedores}
        <div class="product-actions">
            <button class="btn btn-primary ver-detalles" data-sku="${producto.sku}">Ver Detalles</button>
        </div>
    `;

    container.appendChild(productCard);
}


// ==========================
// 🪟 MODAL DE DETALLES DEL PRODUCTO
// ==========================

const productoModal = document.getElementById('producto-modal');
const closeProductoModal = document.getElementById('close-producto-modal');
const modalImagen = document.getElementById('modal-imagen');
const modalNombre = document.getElementById('modal-nombre');
const modalDescripcionProd = document.getElementById('modal-descripcion-prod');
const modalDescripcion2Prod = document.getElementById('modal-descripcion2-prod');
const modalPrecio = document.getElementById('modal-precio');
const modalExistencia = document.getElementById('modal-existencia');
const modalGarantia = document.getElementById('modal-garantia');
const listaCaracteristicasAdicionales = document.getElementById('lista-caracteristicas-adicionales');
const modalProveedores = document.getElementById('modal-proveedores');
const loader = document.getElementById("loader");
loader.style.display = "block";

// Abrir modal al hacer clic en “Ver Detalles”
document.addEventListener("click", (e) => {
    if (e.target.classList.contains("ver-detalles")) {
        const sku = e.target.getAttribute("data-sku");
        mostrarDetallesProducto(sku);
    }
});

// Cerrar modal
closeProductoModal.addEventListener("click", () => {
    productoModal.style.display = "none";
});
window.addEventListener("click", (event) => {
    if (event.target === productoModal) {
        productoModal.style.display = "none";
    }
});

// Mostrar detalles del producto en el modal
async function mostrarDetallesProducto(sku) {
    try {
        const response = await fetch(`/api/producto/${sku}/`);
        if (!response.ok) throw new Error("Producto no encontrado");

        const producto = await response.json();

        modalImagen.src = producto.imagen || "/static/img/no_image.png";
        modalNombre.textContent = producto.nombre || "Sin nombre";
        modalDescripcionProd.textContent = producto.descripcion || "";
        modalDescripcion2Prod.textContent = producto.descripcion_2 || "";
        modalGarantia.textContent = producto.garantia || "Sin garantía";
        modalExistencia.textContent = producto.inventario > 0
            ? `En existencia: ${producto.inventario}`
            : "Agotado";

        modalPrecio.textContent = producto.precio_mxn
            ? `$${parseFloat(producto.precio_mxn).toFixed(2)} MXN`
            : "Precio no disponible";

        // Renderizar lista de proveedores
        if (producto.proveedores && producto.proveedores.length > 0) {
            modalProveedores.innerHTML = `
                <h4>💰 Precios por proveedor:</h4>
                <ul>
                    ${producto.proveedores.map(p =>
                        `<li><strong>${p.nombre}</strong>: $${parseFloat(p.precio).toFixed(2)} MXN (Stock: ${p.stock})</li>`
                    ).join("")}
                </ul>
            `;
        } else {
            modalProveedores.innerHTML = "<p>Sin precios de proveedores disponibles.</p>";
        }

        productoModal.style.display = "block";

    } catch (error) {
        console.error("Error al obtener detalles del producto:", error);
    }
}

// ==========================
// 🚀 INICIALIZACIÓN
// ==========================
document.addEventListener("DOMContentLoaded", fetchProductos);
