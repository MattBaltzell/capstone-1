const heroVid = document.getElementById('hero-vid')
const body = document.querySelector('body')

// Slow home page bg video down
if (heroVid){
    heroVid.playbackRate = .6;
}


body.addEventListener('click', closeFlashedMsg)

function closeFlashedMsg(e){
    if (!e.target.classList.contains('flash-close')) return;
    e.target.closest('.flash-msg').outerHTML = '';
}