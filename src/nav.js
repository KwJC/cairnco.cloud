/* ---- header: hides on scroll down, returns on scroll up or when the
        cursor reaches the top of the window ---- */
(function(){
  var nav=document.querySelector('.nav'); if(!nav) return;
  var last=window.scrollY, ticking=false;

  function reveal(){ nav.classList.remove('is-hidden'); }

  /* Home only. The header ships with no surface so the hero terrain runs behind
     it. Two rules combine:

       going down from the top   the surface stays at 0 until the header has
                                 hidden, so it is never seen arriving
       coming back up            the surface is a direct function of how far
                                 from the top you are, over the last 100px

     That second rule is the whole point. Nothing is timed, so there is no
     duration to lag behind the scroll and no threshold to snap at: the fade IS
     the visitor's scroll, played back at whatever speed they move. */
  var home=document.querySelector('.page--home');
  var FADE=100, TOP=2, solid=false, menuOpen=false;

  function surface(y){
    if(!home) return;
    if(y<=TOP) solid=false;              /* back at the top, start bare again */
    var v = menuOpen ? 1 : (solid ? Math.min(1, y/FADE) : 0);
    nav.style.setProperty('--nav-surface', v.toFixed(3));
  }

  function upd(){
    var y=window.scrollY;
    nav.classList.toggle('is-stuck', y>10);
    if(menuOpen){ reveal(); }
    else if(y>last && y>160){ nav.classList.add('is-hidden'); solid=true; }
    else if(y<last-4){ reveal(); }
    surface(y);
    last=y; ticking=false;
  }
  /* a restored scroll position must not leave the links bare over content */
  if(home && window.scrollY>TOP) solid=true;
  surface(window.scrollY);
  window.addEventListener('scroll',function(){
    if(!ticking){ ticking=true; requestAnimationFrame(upd); }
  },{passive:true});

  /* reaching into the header's own band brings it back, and it then behaves
     normally: it stays until the next downward scroll. No sensor element, so
     nothing intercepts clicks on the page beneath. */
  var band=parseInt(getComputedStyle(document.documentElement)
              .getPropertyValue('--navh'),10) || 76;
  window.addEventListener('pointermove',function(e){
    if(e.clientY <= band && nav.classList.contains('is-hidden')){
      reveal();
      last=window.scrollY;
    }
  },{passive:true});

  /* the phone menu. the panel is a plain dropdown, so it closes on a link, on
     Escape, on a tap outside, and whenever the layout grows back past the
     breakpoint. */
  var tog=document.getElementById('navToggle'), panel=document.getElementById('navLinks'),
      scrim=document.getElementById('navScrim');
  if(tog&&panel){
    function setOpen(on){
      nav.classList.toggle('is-open',on);
      tog.setAttribute('aria-expanded',on?'true':'false');
      if(scrim) scrim.setAttribute('aria-hidden',on?'false':'true');
      if(on) reveal();
      /* the panel must never open over bare terrain */
      menuOpen=on; surface(window.scrollY);
    }
    tog.addEventListener('click',function(e){
      e.stopPropagation();
      setOpen(!nav.classList.contains('is-open'));
    });
    panel.addEventListener('click',function(e){
      if(e.target.closest('a')) setOpen(false);
    });
    if(scrim) scrim.addEventListener('click',function(){ setOpen(false); });
    /* pointerdown, not click: a tap does not reliably synthesise a click on
       an element with no handler of its own, so an outside tap was leaving the
       menu open on a phone. */
    document.addEventListener('pointerdown',function(e){
      if(nav.classList.contains('is-open') && !nav.contains(e.target)) setOpen(false);
    },true);
    document.addEventListener('keydown',function(e){
      if(e.key==='Escape' && nav.classList.contains('is-open')){ setOpen(false); tog.focus(); }
    });
    window.addEventListener('resize',function(){
      if(window.innerWidth>700 && nav.classList.contains('is-open')) setOpen(false);
    },{passive:true});
  }

  /* Same-page calls ease into their target and leave it below the fixed
     header. Native anchor scrolling remains untouched everywhere else. */
  document.addEventListener('click',function(e){
    var link=e.target.closest('a[href^="#"]');
    if(!link) return;
    var id=link.getAttribute('href').slice(1), target=document.getElementById(id);
    if(!id||!target) return;
    e.preventDefault();
    target.scrollIntoView({
      behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',
      block:'start'
    });
    if(window.history&&window.history.pushState) window.history.pushState(null,'','#'+id);
  });
})();
