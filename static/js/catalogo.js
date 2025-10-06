// ===== catalogo.js (modal robusto + grid .catalogo-grid + cierre arriba-derecha) =====
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
      justifyContent: 'center', background: 'rgba(0,0,0,0.7)', zIndex: 1000, padding: '16px'
    });
    const inner = document.createElement('div');
    inner.className = 'modal-body';
    Object.assign(inner.style, {
      maxWidth: '720px', width: '100%', maxHeight: '80vh', overflow: 'auto',
      background: '#fff', borderRadius: '12px', padding: '16px', boxShadow: '0 10px 30px rgba(0,0,0,.2)',
      position: 'relative'
    });
    const close = document.createElement('button');
    close.textContent = 'Cerrar';
    close.id = 'auto-modal-close';
    close.className = 'auto-close';
    Object.assign(close.style, { position: 'absolute', top: '8px', right: '8px', padding: '6px 10px', borderRadius: '8px', border: '0', cursor: 'pointer' });
    close.addEventListener('click', () => {
      if (modal && modal.style) modal.style.display = 'none';
      document.body.classList.remove('modal-open');
    });

    inner.appendChild(close);
    modal.appendChild(inner);

    if (document.body) document.body.appendChild(modal);
    else document.addEventListener('DOMContentLoaded', () => document.body.appendChild(modal), { once: true });

    return { modal, body: inner };
  }

  // Referencias del modal (se crean ya mismo)
  const { modal: productoModal, body: modalBody } = getOrCreateModal();

  // API: carga catálogo y pinta tarjetas en .catalogo-grid
  async function fetchProductos() {
    try {
      const resp = await fetch('/api/productos/');
      const data = await resp.json();

      // Seleccionamos por CLASE, no por ID
      const container = document.querySelector('.catalogo-grid');
      const mensajeVacio = $('#mensaje-vacio');

      if (!container) {
        console.warn('No existe .catalogo-grid en el DOM.');
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
    const titulo = producto.nombre || producto.sku;  // ← nunca usamos descripcion como título
    const card = document.createElement('div');
    card.className = 'product-card';

    const precioPrincipal = (typeof producto.precio_minimo === 'number')
      ? `$${producto.precio_minimo.toFixed(2)} MXN`
      : (producto.precio_mxn != null ? `$${Number(producto.precio_mxn).toFixed(2)} MXN` : 'N/A');

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
    } else if (Array.isArray(producto.proveedores) && producto.proveedores.length > 0) {
      preciosProveedores = `
        <div class="proveedores-lista">
          <h4>Precios por proveedor:</h4>
          <ul>
            ${producto.proveedores.map(p =>
              `<li>${p.nombre || p.proveedor}: $${Number(p.precio).toFixed(2)} MXN (Stock: ${p.stock})</li>`
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

  // ===== DETALLES: intenta /api/producto/<sku>/ y si no, usa ?sku= o ?search= =====
 
 // Coloca esta función una vez, sobre mostrarDetallesProducto:
function normalizarProducto(p) {
  if (!p) return {};
  const has = v => v !== undefined && v !== null && v !== '';

  // Busca una ruta profunda tipo "data.nombre" o "result[0].titulo"
  const pickDeep = (obj, ...paths) => {
    for (const path of paths) {
      const segs = path.replace(/\[(\d+)\]/g, '.$1').split('.');
      let cur = obj;
      let ok = true;
      for (const s of segs) {
        if (!cur || !Object.prototype.hasOwnProperty.call(cur, s)) { ok = false; break; }
        cur = cur[s];
      }
      if (ok && has(cur)) return cur;
    }
    return null;
  };

  // ===== Campos =====
  const sku = pickDeep(p, 'sku', 'SKU', 'id', 'Id', 'codigo', 'codigo_sku', 'producto.sku');

  // NOMBRE: añadí muchos alias comunes
  const nombre = pickDeep(
    p,
    'nombre', 'Nombre', 'product_name', 'ProductName',
    'nombre_producto', 'NombreProducto', 'Nombre_Producto',
    'descripcion_corta', 'DescripcionCorta',
    'Descripcion', 'Descripción', 'descripcion', 'producto', 'Producto',
    'titulo', 'title',
    'data.nombre', 'data.descripcion', 'result.0.nombre', 'result.0.descripcion'
  );

  // IMAGEN
  const imagen = pickDeep(
    p, 'imagen', 'IMAGEN', 'image', 'image_url', 'url_imagen', 'foto', 'Foto',
    'media.imagen', 'data.imagen'
  );

  // PRECIO
  const precioRaw = pickDeep(
    p, 'precio_mxn', 'precio_minimo', 'precio', 'Precio', 'PrecioMXN',
    'precio_mx', 'price', 'Price', 'precio_final', 'PrecioFinal', 'data.precio'
  );
  const precio_mxn = (precioRaw !== null && !Number.isNaN(Number(precioRaw))) ? Number(precioRaw) : null;

  // INVENTARIO
  const invRaw = pickDeep(
    p, 'inventario', 'stock_total', 'stock', 'Stock', 'existencia', 'Existencia', 'qty', 'cantidad', 'data.stock'
  );
  const inventario = (invRaw !== null && !Number.isNaN(Number(invRaw))) ? Number(invRaw) : 0;

  // CATEGORÍA / GARANTÍA / DESCRIPCIONES
  const categoria_nombre = pickDeep(p, 'categoria_nombre', 'categoria', 'Categoria', 'Cód. categoría producto', 'data.categoria');
  const garantia = pickDeep(p, 'garantia', 'GARANTIA', 'Garantia', 'warranty', 'data.garantia');
  const descripcion = pickDeep(p, 'descripcion', 'Descripción', 'Descripcion', 'detalle', 'CARACTERISTICAS', 'caracteristicas', 'data.descripcion');
  const descripcion_2 = pickDeep(p, 'descripcion_2', 'detalle2', 'data.descripcion2');

  // PROVEEDORES / PRECIOS POR PROVEEDOR
  let proveedores = pickDeep(p, 'proveedores', 'precios_proveedor', 'precios', 'vendors', 'ofertas', 'data.proveedores');
  if (Array.isArray(proveedores)) {
    proveedores = proveedores.map(x => {
      const nombreProv = pickDeep(x, 'nombre', 'proveedor', 'name', 'Vendor', 'Proveedor');
      const precioProvRaw = pickDeep(x, 'precio', 'precio_mxn', 'price', 'Precio');
      const stockProvRaw = pickDeep(x, 'stock', 'existencia', 'qty', 'cantidad');
      const precioProv = (precioProvRaw !== null && !Number.isNaN(Number(precioProvRaw))) ? Number(precioProvRaw) : null;
      const stockProv = (stockProvRaw !== null && !Number.isNaN(Number(stockProvRaw))) ? Number(stockProvRaw) : null;
      return { nombre: nombreProv, precio: precioProv, stock: stockProv };
    });
  } else {
    proveedores = [];
  }

  return {
    sku,
    nombre: has(nombre) ? nombre : (has(sku) ? String(sku) : null), // fallback al SKU como título
    imagen,
    precio_mxn,
    inventario,
    categoria_nombre,
    garantia,
    descripcion,
    descripcion_2,
    proveedores
  };
}

  // Pega esto reemplazando tu función actual:
async function mostrarDetallesProducto(sku) {
  try {
    // 1) Buscar por sku en la lista (evita el 404 del detalle)
    let resp = await fetch(`/api/productos/?sku=${encodeURIComponent(sku)}`);
    if (!resp.ok) {
      // 2) Búsqueda libre
      resp = await fetch(`/api/productos/?search=${encodeURIComponent(sku)}`);
    }
    // 3) Último intento: endpoint de detalle (si lo tienes en el backend)
    if (!resp.ok) {
      resp = await fetch(`/api/producto/${encodeURIComponent(sku)}/`);
    }
    if (!resp.ok) throw new Error('Producto no encontrado');

    // ⬇⬇ ESTA ES LA LÍNEA QUE QUIERES ⬇⬇
    let raw = await resp.json();
    console.log('[DETALLE RAW]', raw);

    // Si vino del listado, puede ser array
    if (Array.isArray(raw)) {
      if (!raw.length) throw new Error('Producto no encontrado');
      raw = raw.find(p => String(p.sku) === String(sku)) || raw[0];
    }

    // Normalizamos nombres de campos (ver función más abajo)
    const producto = normalizarProducto(raw);

    // ---- Relleno del modal (usa tu plantilla si existe) ----
    const modalImagen = document.querySelector('#modal-imagen');
    const modalNombre = document.querySelector('#modal-nombre');
    const modalDescripcionProd = document.querySelector('#modal-descripcion-prod');
    const modalDescripcion2Prod = document.querySelector('#modal-descripcion2-prod');
    const modalPrecio = document.querySelector('#modal-precio');
    const modalExistencia = document.querySelector('#modal-existencia');
    const modalGarantia = document.querySelector('#modal-garantia');
    const modalProveedores = document.querySelector('#modal-proveedores');

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
                `<li><strong>${p.nombre || p.proveedor}</strong>: $${Number(p.precio).toFixed(2)} MXN (Stock: ${p.stock ?? 'N/D'})</li>`
              ).join('')}
            </ul>
          `;
        } else {
          modalProveedores.innerHTML = '<p>Sin precios de proveedores disponibles.</p>';
        }
      }
      if (productoModal && productoModal.style) {
        productoModal.style.display = 'flex';
        document.body.classList.add('modal-open');
      }
      return;
    }

    // ---- Fallback genérico si no tienes plantilla detallada ----
    if (modalBody) {
      modalBody.innerHTML = `
        <button class="auto-close" id="auto-modal-close">Cerrar</button>
        <h3 style="margin-top:0">${producto.nombre || producto.sku || 'Producto'}</h3>
        <img src="${producto.imagen || '/static/img/no_image.png'}" alt="${producto.nombre || 'Producto'}" style="max-width:100%;margin:8px 0">
        <p><strong>SKU:</strong> ${producto.sku ?? ''}</p>
        <p><strong>Categoría:</strong> ${producto.categoria_nombre ?? ''}</p>
        <p><strong>Garantía:</strong> ${producto.garantia ?? 'Sin garantía'}</p>
        <p><strong>Existencia:</strong> ${(producto.inventario > 0) ? `En existencia: ${producto.inventario}` : 'Agotado'}</p>
        <p><strong>Precio:</strong> ${(producto.precio_mxn != null) ? `$${Number(producto.precio_mxn).toFixed(2)} MXN` : 'No disponible'}</p>
        <div>${producto.descripcion || ''}</div>
      `;
      const btn = document.querySelector('#auto-modal-close');
      if (btn) btn.addEventListener('click', () => {
        if (productoModal && productoModal.style) productoModal.style.display = 'none';
        document.body.classList.remove('modal-open');
      });
    }
    if (productoModal && productoModal.style) {
      productoModal.style.display = 'flex';
      document.body.classList.add('modal-open');
    }

  } catch (err) {
    console.error('Error al obtener detalles del producto:', err);
  }
}


  // Delegación: botones "Ver Detalles"
  document.addEventListener('click', (e) => {
    const btn = e.target.closest('.ver-detalles');
    if (btn) {
      const sku = btn.getAttribute('data-sku');
      if (sku) mostrarDetallesProducto(sku);
    }
  });

  // Cerrar modal por click en overlay (si corresponde)
  window.addEventListener('click', (ev) => {
    if (ev.target === productoModal) {
      if (productoModal && productoModal.style) productoModal.style.display = 'none';
      document.body.classList.remove('modal-open');
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
        <button class="auto-close" id="auto-modal-close">Cerrar</button>
        <h3 style="margin-top:0">Prueba de modal</h3>
        <p>Si ves esto, el modal funciona.</p>
      `;
      const btn = $('#auto-modal-close', modalBody);
      if (btn) btn.addEventListener('click', () => {
        if (productoModal && productoModal.style) productoModal.style.display = 'none';
        document.body.classList.remove('modal-open');
      });
    }
    if (productoModal && productoModal.style) {
      productoModal.style.display = 'flex';
      document.body.classList.add('modal-open');
    }
  };

  // Inicio
  document.addEventListener('DOMContentLoaded', () => {
    const loader2 = $('#loader');
    if (loader2) loader2.style.display = 'none';
    fetchProductos();
  });
})();
