// ===== catalogo.js (limpio y robusto) =====
(function () {
  if (window.__CATALOGO_JS_LOADED__) return;
  window.__CATALOGO_JS_LOADED__ = true;
  console.log('[catalogo.js] cargado');

  // Helpers
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

  // Crea o reutiliza un modal. Si no hay, genera #auto-modal con .modal-body
  function getOrCreateModal() {
    const candidates = [
      '#producto-modal', '#cart-modal', '#product-modal', '#modal-producto',
      '[data-catalog-modal]', '.catalog-modal', '.modal'
    ];
    for (const s of candidates) {
      const el = document.querySelector(s);
      if (el) {
        let body = el.querySelector('.modal-body') || el.querySelector('.modal-content');
        if (!body) {
          body = document.createElement('div');
          body.className = 'modal-body';
          el.appendChild(body);
        }
        return { modal: el, body };
      }
    }
    // Crear modal de respaldo
    const modal = document.createElement('div');
    modal.id = 'auto-modal';
    Object.assign(modal.style, {
      position: 'fixed', inset: '0', display: 'none', alignItems: 'center',
      justifyContent: 'center', background: 'rgba(0,0,0,0.5)', zIndex: 9999, padding: '16px'
    });
    const inner = document.createElement('div');
    inner.className = 'modal-body';
    Object.assign(inner.style, {
      maxWidth: '720px', width: '100%', maxHeight: '80vh', overflow: 'auto',
      background: '#fff', borderRadius: '12px', padding: '16px', boxShadow: '0 10px 30px rgba(0,0,0,.2)'
    });
    const close = document.createElement('button');
    close.textContent = 'Cerrar';
    Object.assign(close.style, { float: 'right', marginBottom: '8px' });
    close.addEventListener('click', () => { modal.style.display = 'none'; });

    inner.appendChild(close);
    modal.appendChild(inner);

    if (document.body) document.body.appendChild(modal);
    else document.addEventListener('DOMContentLoaded', () => document.body.appendChild(modal), { once: true });

    return { modal, body: inner };
  }

  // Referencias del modal (se crean ya mismo)
  const { modal: productoModal, body: modalBody } = getOrCreateModal();

  // API: carga catálogo y pinta tarjetas en #catalogo-grid
  async function fetchProductos() {
    try {
      const resp = await fetch('/api/productos/');
      const data = await resp.json();

      const container = $('#catalogo-grid');
      const mensajeVacio = $('#mensaje-vacio');

      if (!container) {
        console.warn('No existe #catalogo-grid en el DOM.');
        return;
      }

      container.innerHTML = '';

      if (!data || data.length === 0) {
        if (mensajeVacio) mensajeVacio.style.display = 'block';
        return;
      } else {
        if (mensajeVacio) mensajeVacio.style.display = 'none';
      }

      data.forEach(producto => renderizarProducto(producto, container));

    } catch (err) {
      console.error('Error al cargar productos:', err);
    }
  }

  // Crea una card de producto
  function renderizarProducto(producto, container) {
    const card = document.createElement('div');
    card.className = 'product-card';

    const precioPrincipal = (typeof producto.precio_minimo === 'number')
      ? `$${producto.precio_minimo.toFixed(2)} MXN`
      : 'N/A';

    let preciosProveedores = '';
    if (Array.isArray(producto.precios_proveedor) && producto.precios_proveedor.length > 0) {
      preciosProveedores = `
        <div class="proveedores-lista">
          <h4>Precios por proveedor:</h4>
          <ul>
            ${producto.precios_proveedor.map(p =>
              `<li>${p.proveedor}: $${Number(p.precio).toFixed(2)} MXN (Stock: ${p.stock})</li>`
            ).join('')}
          </ul>
        </div>
      `;
    }

    card.innerHTML = `
      <img src="${producto.imagen || '/static/img/no_image.png'}" alt="${producto.nombre || 'Producto'}" class="product-image">
      <h3 class="product-title">${producto.nombre || producto.sku}</h3>
      <p class="product-category">${producto.categoria_nombre || ''}</p>
      <p class="product-price">${precioPrincipal}</p>
      <p class="product-stock">${(producto.inventario > 0) ? `En existencia: ${producto.inventario}` : 'Agotado'}</p>
      ${preciosProveedores}
      <div class="product-actions">
        <button class="btn btn-primary ver-detalles" data-sku="${producto.sku}">Ver Detalles</button>
      </div>
    `;

    container.appendChild(card);
  }

  // Muestra detalles en el modal (usa tu plantilla si existe; si no, render genérico)
  async function mostrarDetallesProducto(sku) {
    try {
      const resp = await fetch(`/api/producto/${sku}/`);
      if (!resp.ok) throw new Error('Producto no encontrado');

      const producto = await resp.json();

      // Intenta usar tu estructura si existe:
      const modalImagen = $('#modal-imagen');
      const modalNombre = $('#modal-nombre');
      const modalDescripcionProd = $('#modal-descripcion-prod');
      const modalDescripcion2Prod = $('#modal-descripcion2-prod');
      const modalPrecio = $('#modal-precio');
      const modalExistencia = $('#modal-existencia');
      const modalGarantia = $('#modal-garantia');
      const modalProveedores = $('#modal-proveedores');

      const usaPlantillaDetallada =
        modalImagen || modalNombre || modalDescripcionProd || modalPrecio || modalProveedores;

      if (usaPlantillaDetallada) {
        if (modalImagen) modalImagen.src = producto.imagen || '/static/img/no_image.png';
        if (modalNombre) modalNombre.textContent = producto.nombre || 'Sin nombre';
        if (modalDescripcionProd) modalDescripcionProd.textContent = producto.descripcion || '';
        if (modalDescripcion2Prod) modalDescripcion2Prod.textContent = producto.descripcion_2 || '';
        if (modalGarantia) modalGarantia.textContent = producto.garantia || 'Sin garantía';
        if (modalExistencia) {
          modalExistencia.textContent = (producto.inventario > 0)
            ? `En existencia: ${producto.inventario}`
            : 'Agotado';
        }
        if (modalPrecio) {
          modalPrecio.textContent = (producto.precio_mxn != null)
            ? `$${Number(producto.precio_mxn).toFixed(2)} MXN`
            : 'Precio no disponible';
        }
        if (modalProveedores) {
          if (producto.proveedores && producto.proveedores.length > 0) {
            modalProveedores.innerHTML = `
              <h4>💰 Precios por proveedor:</h4>
              <ul>
                ${producto.proveedores.map(p =>
                  `<li><strong>${p.nombre}</strong>: $${Number(p.precio).toFixed(2)} MXN (Stock: ${p.stock})</li>`
                ).join('')}
              </ul>
            `;
          } else {
            modalProveedores.innerHTML = '<p>Sin precios de proveedores disponibles.</p>';
          }
        }
        if (productoModal && productoModal.style) productoModal.style.display = 'flex';
        return;
      }

      // Fallback genérico en modal-body
      if (modalBody) {
        modalBody.innerHTML = `
          <button style="float:right;margin-bottom:8px" id="auto-modal-close">Cerrar</button>
          <h3 style="margin-top:0">${producto.nombre || producto.sku || 'Producto'}</h3>
          <img src="${producto.imagen || '/static/img/no_image.png'}" alt="${producto.nombre || 'Producto'}" style="max-width:100%;margin:8px 0">
          <p><strong>SKU:</strong> ${producto.sku ?? ''}</p>
          <p><strong>Categoría:</strong> ${producto.categoria_nombre ?? ''}</p>
          <p><strong>Garantía:</strong> ${producto.garantia ?? 'Sin garantía'}</p>
          <p><strong>Existencia:</strong> ${(producto.inventario > 0) ? `En existencia: ${producto.inventario}` : 'Agotado'}</p>
          <p><strong>Precio:</strong> ${(producto.precio_mxn != null) ? `$${Number(producto.precio_mxn).toFixed(2)} MXN` : 'No disponible'}</p>
          <div>${producto.descripcion || ''}</div>
        `;
        const btn = $('#auto-modal-close', modalBody);
        if (btn) btn.addEventListener('click', () => { if (productoModal && productoModal.style) productoModal.style.display = 'none'; });
      }
      if (productoModal && productoModal.style) productoModal.style.display = 'flex';

    } catch (err) {
      console.error('Error al obtener detalles del producto:', err);
    }
  }

  // Eventos globales
  document.addEventListener('click', (e) => {
    const btn = e.target.closest('.ver-detalles');
    if (btn) {
      const sku = btn.getAttribute('data-sku');
      if (sku) mostrarDetallesProducto(sku);
    }
  });

  // Cerrar modal (si el DOM propio trae botón/capa)
  const closeProductoModal = $('#close-producto-modal');
  if (closeProductoModal && productoModal) {
    closeProductoModal.addEventListener('click', () => {
      if (productoModal && productoModal.style) productoModal.style.display = 'none';
    });
  }
  window.addEventListener('click', (ev) => {
    if (ev.target === productoModal) {
      if (productoModal && productoModal.style) productoModal.style.display = 'none';
    }
  });

  // Loader (si existe)
  const loader = $('#loader');
  if (loader) loader.style.display = 'none';

  // Utilidad de prueba desde la consola:
  window.__showTestModal = () => {
    if (!productoModal) return console.warn('No hay modal.');
    if (modalBody) {
      modalBody.innerHTML = `
        <button style="float:right;margin-bottom:8px" id="auto-modal-close">Cerrar</button>
        <h3 style="margin-top:0">Prueba de modal</h3>
        <p>Si ves esto, el modal funciona.</p>
      `;
      const btn = $('#auto-modal-close', modalBody);
      if (btn) btn.addEventListener('click', () => { if (productoModal && productoModal.style) productoModal.style.display = 'none'; });
    }
    if (productoModal && productoModal.style) productoModal.style.display = 'flex';
  };

  // Inicio
  document.addEventListener('DOMContentLoaded', () => {
    // Oculta loader al entrar
    const loader2 = $('#loader');
    if (loader2) loader2.style.display = 'none';
    fetchProductos();
  });
})();
