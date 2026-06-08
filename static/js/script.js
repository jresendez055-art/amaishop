/**
 * AMAI SHOP - JavaScript Principal
 * Funcionalidades generales del sitio
 */

// ============================================
// INICIALIZACIÓN
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    console.log('🛍️ Amai Shop - JavaScript cargado correctamente');
    
    // Inicializar tooltips de Bootstrap
    initializeTooltips();
    
    // Inicializar animaciones de entrada
    initializeScrollAnimations();
});

// ============================================
// TOOLTIPS
// ============================================
function initializeTooltips() {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (tooltipTriggerList.length > 0) {
        tooltipTriggerList.forEach(tooltipTriggerEl => {
            new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

// ============================================
// ANIMACIONES AL HACER SCROLL
// ============================================
function initializeScrollAnimations() {
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-visible');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.animate-on-scroll').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
}

// ============================================
// MODO OSCURO (MEJORADO)
// ============================================
function toggleTheme() {
    const html = document.documentElement;
    const currentTheme = html.getAttribute('data-bs-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    // Guardar preferencia en localStorage
    localStorage.setItem('theme', newTheme);
    
    // Aplicar tema
    html.setAttribute('data-bs-theme', newTheme);
    
    // Actualizar icono
    const icon = document.getElementById('themeIcon');
    if (icon) {
        icon.className = newTheme === 'dark' ? 'bi bi-sun' : 'bi bi-moon-stars';
    }
    
    // Enviar al servidor (opcional)
    fetch('/toggle-theme', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({ theme: newTheme })
    }).catch(() => {});
    
    showToast(newTheme === 'dark' ? 'Modo oscuro activado' : 'Modo claro activado', 'info');
}

// ---------- CARGAR TEMA GUARDADO ----------
function loadSavedTheme() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.documentElement.setAttribute('data-bs-theme', savedTheme);
        const icon = document.getElementById('themeIcon');
        if (icon) {
            icon.className = savedTheme === 'dark' ? 'bi bi-sun' : 'bi bi-moon-stars';
        }
    }
}

// Cargar tema al iniciar
loadSavedTheme();

// ============================================
// UTILIDADES UI
// ============================================

// ---------- MOSTRAR TOAST ----------
function showToast(message, type = 'info') {
    const toastContainer = document.querySelector('.toast-container');
    
    if (!toastContainer) {
        console.warn('No se encontró contenedor de toasts');
        return;
    }
    
    const toastId = 'toast-' + Date.now();
    const icons = {
        success: 'check-circle-fill',
        danger: 'exclamation-triangle-fill',
        warning: 'exclamation-circle-fill',
        info: 'info-circle-fill'
    };
    
    const toastHtml = `
        <div id="${toastId}" class="toast align-items-center text-white bg-${type} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="bi bi-${icons[type] || icons.info} me-2"></i>${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, { delay: 3000 });
    toast.show();
    
    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}

// ---------- SCROLL SUAVE ----------
function smoothScrollTo(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}