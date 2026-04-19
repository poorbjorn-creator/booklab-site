<script>
(function(){
var btn=document.querySelector('.hamburger'),ov=document.querySelector('.nav-overlay'),bg=document.querySelector('.nav-overlay-bg');
function toggle(){var o=ov.classList.toggle('open');bg.classList.toggle('open');btn.classList.toggle('active');document.body.classList.toggle('nav-open');}
btn.addEventListener('click',toggle);
bg.addEventListener('click',toggle);
ov.querySelectorAll('a').forEach(function(a){a.addEventListener('click',toggle);});
})();
</script>