/* ---- header: hides on scroll down, returns on scroll up or when the
        cursor reaches the top of the window ---- */
(function(){
  var nav=document.querySelector('.nav'); if(!nav) return;
  var last=window.scrollY, ticking=false;

  function reveal(){ nav.classList.remove('is-hidden'); }

  function upd(){
    var y=window.scrollY;
    nav.classList.toggle('is-stuck', y>10);
    if(y>last && y>160){ nav.classList.add('is-hidden'); }
    else if(y<last-4){ reveal(); }
    last=y; ticking=false;
  }
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
  var tog=document.getElementById('navToggle'), panel=document.getElementById('navLinks');
  if(tog&&panel){
    function setOpen(on){
      nav.classList.toggle('is-open',on);
      tog.setAttribute('aria-expanded',on?'true':'false');
      if(on) reveal();
    }
    tog.addEventListener('click',function(e){
      e.stopPropagation();
      setOpen(!nav.classList.contains('is-open'));
    });
    panel.addEventListener('click',function(e){
      if(e.target.closest('a')) setOpen(false);
    });
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
})();
