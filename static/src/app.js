const heroVid = document.getElementById('hero-vid')
const body = document.querySelector('body')
const radiusText = document.querySelector('.radius_text')
const radiusSlider = document.querySelector('.radius_slider')
const editForm = document.getElementById('user_form')

// Slow home page bg video down
if (heroVid){
    heroVid.playbackRate = .6;
}


body.addEventListener('click', closeFlashedMsg)

function closeFlashedMsg(e){
    if (!e.target.classList.contains('flash-close')) return;
    e.target.closest('.flash-msg').outerHTML = '';
}


body.addEventListener('input', function(e){
    if(!radiusSlider) return;
    radiusText.textContent = radiusSlider.value
}) 


const instrument_select = new SlimSelect({
    select: '#instruments'
})

const genre_select = new SlimSelect({
    select: '#genres'
})