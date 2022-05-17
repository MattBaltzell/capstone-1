const heroVid = document.getElementById('hero-vid')
const body = document.querySelector('body')

heroVid.playbackRate = 0.5;

body.addEventListener('click', function(e){
    console.log('here');
    if (!e.target.classList.contains('flash-msg')) return;

    e.target.outerHTML = '';
})