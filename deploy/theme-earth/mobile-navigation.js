(() => {
  if (window.resourceMobileNavigation) return;
  window.resourceMobileNavigation = true;
  const mobile = window.matchMedia('(max-width: 639px)');
  let previousOverflow = '';
  let opener = null;

  function closeMenu() {
    const drawer = document.getElementById('mobile-site-drawer');
    if (drawer?.open) drawer.close();
  }

  document.addEventListener('click', (event) => {
    const drawer = document.getElementById('mobile-site-drawer');
    if (!drawer) return;
    const trigger = event.target.closest('[data-mobile-menu-open]');
    if (trigger && mobile.matches && !drawer.open) {
      opener = trigger;
      previousOverflow = document.documentElement.style.overflow;
      document.documentElement.style.overflow = 'hidden';
      trigger.setAttribute('aria-expanded', 'true');
      drawer.showModal();
      for (const link of drawer.querySelectorAll('a[href]')) {
        const url = new URL(link.href, window.location.href);
        if (url.origin === location.origin && url.pathname === location.pathname) {
          link.setAttribute('aria-current', 'page');
          let parent = link.parentElement;
          while (parent && parent !== drawer) {
            if (parent.tagName === 'DETAILS') parent.open = true;
            parent = parent.parentElement;
          }
        } else link.removeAttribute('aria-current');
      }
    }
    if (event.target.closest('[data-mobile-menu-close]') || event.target.closest('#mobile-site-drawer a[href]')) closeMenu();
    if (event.target === drawer) {
      const box = drawer.getBoundingClientRect();
      if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) closeMenu();
    }
    if (event.target.closest('[data-mobile-search]')) window.SearchWidget?.open();
  });

  // Native dialog handles Escape, focus trapping, and inert page content.
  document.addEventListener('close', (event) => {
    if (event.target.id !== 'mobile-site-drawer') return;
    document.documentElement.style.overflow = previousOverflow;
    opener?.setAttribute('aria-expanded', 'false');
    opener?.focus({ preventScroll: true });
  }, true);
  // Close before theme/plugin keyboard handlers consume Escape.
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && document.getElementById('mobile-site-drawer')?.open) {
      event.preventDefault();
      closeMenu();
    }
  }, true);
  mobile.addEventListener('change', ({ matches }) => { if (!matches) closeMenu(); });
  window.addEventListener('pagehide', closeMenu);
})();
