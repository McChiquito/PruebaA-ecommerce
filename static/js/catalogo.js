// ===== catalogo.js (modal robusto + grid .catalogo-grid + cierre arriba-derecha) =====
(function () {
  if (window.__CATALOGO_JS_LOADED__) return;
  window.__CATALOGO_JS_LOADED__ = true;
  console.log('[catalogo.js] cargado');

  // Helpers
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

  
  function toNum(v) {
    if (v == null) return NaN;
    if (typeof v === 'number') return v;
    return Number(String(v).replace(/[^0-9.]/g, ''));
  }

  function getProveedores(producto) {
    if (Array.isArray(producto.precios_proveedor) && producto.precios_proveedor.length) {
      return producto.precios_proveedor;
    }
    if (Array.isArray(producto.proveedores)) {
      return producto.proveedores;
    }
    return [];
  }

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
  const state = { categoriaId: null, soloStock: false, search: '' };
  // --- Cargar y pintar categorías en #categoria-list (radios)
  async function loadCategorias() {
    try {
      const resp = await fetch('/api/categorias/');
      const cats = await resp.json();

      const box = document.getElementById('categoria-list');
      if (!box) return; // si no existe el contenedor, no hacemos nada

      box.innerHTML = `
        <label style="display:block;margin:4px 0">
          <input type="radio" name="categoria" value="" checked>
          Todas
        </label>
        ${cats.map(c => `
          <label style="display:block;margin:4px 0">
            <input type="radio" name="categoria" value="${c.id}">
            ${c.nombre}
          </label>
        `).join('')}
      `;

      // cuando cambia la categoría, recargamos el catálogo
      box.addEventListener('change', (e) => {
        if (e.target && e.target.name === 'categoria') {
          state.categoriaId = e.target.value || null;
          fetchProductos();
        }
      });
    } catch (err) {
      console.error('Error cargando categorías:', err);
    }
  }
  // API: carga catálogo y pinta tarjetas en .catalogo-grid
async function fetchProductos() {
  try {
    const params = new URLSearchParams();
    if (state.categoriaId) params.set('categoria', state.categoriaId);
    if (state.soloStock)  params.set('stock', '1');
    if (state.search)     params.set('q', state.search);

    const resp = await fetch('/api/productos/' + (params.toString() ? `?${params}` : ''));
    const data = await resp.json();

    const container =
      document.querySelector('.catalogo-grid') ||
      document.getElementById('catalogo-grid');

    const mensajeVacio = document.getElementById('mensaje-vacio');

    if (!container) return;
    container.innerHTML = '';

    if (!data || !data.length) {
      if (mensajeVacio) mensajeVacio.style.display = 'block';
      return;
    } else if (mensajeVacio) {
      mensajeVacio.style.display = 'none';
    }

    data.forEach(p => renderizarProducto(p, container));
  } catch (err) {
    console.error('Error al cargar productos:', err);
  }
}

  // Crea una card de producto
function renderizarProducto(producto, container) {
  const card = document.createElement('div');
  card.className = 'product-card';

  const titulo = producto.nombre || producto.sku;

  // Datos ya calculados por el backend:
  const precioNum   = (typeof producto.precio_minimo === 'number') ? producto.precio_minimo : null;
  const showProv    = !!producto.mostrar_proveedor;  // público = false
  const mejor       = producto.mejor_oferta || null; // null en público
  const stockMejor  = (typeof producto.stock_mejor === 'number') ? producto.stock_mejor : (producto.inventario || 0);

  // Etiqueta de stock:
  const stockLabel = (showProv && mejor)
    ? (mejor.stock > 0
        ? `En existencia: ${mejor.stock} (por ${mejor.proveedor})`
        : `Agotado (por ${mejor.proveedor})`)
    : (stockMejor > 0 ? `En existencia: ${stockMejor}` : 'Agotado');

  // Lista de proveedores: solo si está permitido
  let preciosProveedores = '';
  if (showProv && Array.isArray(producto.precios_proveedor) && producto.precios_proveedor.length) {
    preciosProveedores = `
      <div class="proveedores-lista">
        <h4>Precios por proveedor:</h4>
        <ul>
          ${producto.precios_proveedor.map(p => {
            const precio = (typeof p.precio === 'number') ? p.precio.toFixed(2) : 'N/D';
            const stock = (p.stock != null) ? p.stock : 'N/D';
            return `<li>${p.proveedor}: $${precio} MXN (Stock: ${stock})</li>`;
          }).join('')}
        </ul>
      </div>
    `;
  }

  card.innerHTML = `
    <img src="${producto.imagen || '/static/img/no_image.png'}" alt="${titulo}" class="product-image">
    <p class="product-category">${producto.categoria_nombre || ''}</p>
    <h3 class="product-title">${titulo}</h3>
    <p class="product-price">${precioNum != null ? `$${precioNum.toFixed(2)} MXN` : 'Precio no disponible'}</p>
    <p class="product-stock">${stockLabel}</p>
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
// Muestra el modal con detalle del producto usando la API de detalle por SKU
// Muestra el modal con el detalle de un producto por SKU
async function mostrarDetallesProducto(sku) {
  // ---- refs del DOM ----
  const modal            = document.getElementById('producto-modal');
  const modalImg         = document.getElementById('modal-imagen');
  const modalNombre      = document.getElementById('modal-nombre');
  const modalDesc1       = document.getElementById('modal-descripcion-prod');
  const modalDesc2       = document.getElementById('modal-descripcion2-prod');
  const modalPrecio      = document.getElementById('modal-precio');
  const modalExistencia  = document.getElementById('modal-existencia');
  const modalGarantia    = document.getElementById('modal-garantia');
  const modalCaracUl     = document.getElementById('lista-caracteristicas-adicionales');
  const btnAgregar       = document.getElementById('agregar-modal-carrito');
  const inputCantidad    = document.getElementById('modal-cantidad');
  const provBox          = document.getElementById('modal-proveedores'); // opcional en tu HTML

  const setText = (el, txt) => { if (el) el.textContent = txt ?? ''; };

  try {
    // Nota: si el backend ya decide público/privado por usuario, quita ?public=1.
    const resp = await fetch(`/api/producto/${encodeURIComponent(sku)}/?public=1`, { cache: 'no-store' });
    if (!resp.ok) throw new Error(`No se pudo obtener el producto (HTTP ${resp.status})`);
    const raw = await resp.json();

    // ---- normalización mínima ----
    const nombre   = raw.nombre || raw.sku || '';
    const imagen   = raw.imagen || '/static/img/no_image.png';
    const categoria= raw.categoria_nombre || '';
    const garantia = raw.garantia ?? null;

    // Precio principal (si tu API pública manda otro campo, ajusta aquí)
    const precioMin = (typeof raw.precio_minimo === 'number') ? raw.precio_minimo : null;
    const precioTxt = (precioMin != null) ? `$${precioMin.toFixed(2)} MXN` : 'Precio no disponible';

    // Stock (si staff muestra proveedor; si público, genérico)
    const showProv  = !!raw.mostrar_proveedor;  // backend decide
    const mejor     = raw.mejor_oferta || null; // { proveedor, precio, stock } | null
    const stockCalc = (showProv && mejor) ? (Number(mejor.stock) || 0)
                                          : (Number(raw.stock_mejor) || Number(raw.inventario) || 0);

    const stockTxt  = (showProv && mejor)
      ? (stockCalc > 0
          ? `En existencia: ${stockCalc} (por ${mejor.proveedor})`
          : `Agotado (por ${mejor.proveedor})`)
      : (stockCalc > 0 ? `En existencia: ${stockCalc}` : 'Agotado');

    // ---- pintar cabecera ----
    if (modalImg)    modalImg.src = imagen;
    setText(modalNombre, nombre);

    // Descripción breve (primera línea/oración de la descripción cruda si existe)
    const desc = (raw.descripcion || '').trim();
    const primeraFrase = desc.split(/\.\s+|\n/)[0] || '';
    setText(modalDesc1, primeraFrase);
    setText(modalDesc2, categoria ? `Categoría: ${categoria}` : '');

    // Precio / existencia / garantía
    setText(modalPrecio,     precioTxt);
    setText(modalExistencia, stockTxt);
    setText(modalGarantia,   (garantia != null && garantia !== '') ? `${garantia}` : 'Sin garantía');

    // ---- Características detalladas (lista) ----
    if (modalCaracUl) {
      const basePairs = [];
      if (raw.sku)              basePairs.push(['SKU', raw.sku]);
      if (categoria)            basePairs.push(['Categoría', categoria]);
      if (garantia != null && garantia !== '') basePairs.push(['Garantía', garantia]);

      // lo que parsea el backend desde "descripcion"
      const extras = Array.isArray(raw.caracteristicas) ? raw.caracteristicas : [];

      const baseLis  = basePairs.map(([k, v]) => `<li><strong>${k}:</strong> ${v}</li>`).join('');
      const extraLis = extras.map(txt => `<li>${txt}</li>`).join('');

      modalCaracUl.innerHTML = baseLis + extraLis;
    }

    // ---- Lista de proveedores (solo si staff/privado) ----
    if (provBox) {
      if (showProv && Array.isArray(raw.precios_proveedor) && raw.precios_proveedor.length > 0) {
        provBox.innerHTML = `
          <h4>Precios por proveedor:</h4>
          <ul>
            ${raw.precios_proveedor.map(p => `
              <li><strong>${p.proveedor}</strong>: $${(typeof p.precio === 'number' ? p.precio.toFixed(2) : 'N/D')} MXN
                (Stock: ${p.stock ?? 'N/D'})</li>`).join('')}
          </ul>`;
      } else {
        provBox.innerHTML = '';
      }
    }

    // ---- botón "Agregar al carrito" ----
    if (btnAgregar) {
      btnAgregar.disabled = stockCalc <= 0;
      btnAgregar.onclick = () => {
        const qty = Math.max(1, parseInt(inputCantidad?.value || '1', 10) || 1);
        // Ajusta el objeto a tu función real de carrito
        if (typeof agregarProductoAlCarrito === 'function') {
          agregarProductoAlCarrito(raw.sku, qty, {
            nombre: nombre,
            imagen: imagen,
            precioUnitario: precioMin ?? 0
          });
        }
      };
    }

    // ---- mostrar modal ----
    if (modal) {
      modal.style.display = 'flex';
      document.body.classList.add('modal-open');
    }
  } catch (err) {
    console.error('Error al obtener detalles del producto:', err);
    alert('No se pudieron cargar los detalles del producto.');
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
  // checkbox "Solo en existencia"
  const soloStockChk = document.querySelector('input[type="checkbox"][name="solo_en_existencia"]') ||
                       document.querySelector('#solo-existencia'); // usa el id que tengas
  if (soloStockChk) {
    soloStockChk.addEventListener('change', () => {
      state.soloStock = !!soloStockChk.checked;
      fetchProductos();
    });
  }

  // input de búsqueda
  const searchInput = document.querySelector('input[type="text"][name="busqueda"]') ||
                      document.querySelector('#search-producto'); // usa tu id
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      state.search = e.target.value.trim();
      // debounce si quieres; por simplicidad:
      fetchProductos();
    });
  }

  // carga inicial
  loadCategorias();
  fetchProductos();
});

})();
