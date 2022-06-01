const heroVid = document.getElementById('hero-vid')
const body = document.querySelector('body')
const radiusText = document.querySelector('.radius_text')
const radiusSlider = document.querySelector('.radius_slider')
const editForm = document.getElementById('user_form')


//Slow down the home page bg video
if (heroVid){heroVid.playbackRate = .6}


body.addEventListener('click', closeFlashedMsg)

function closeFlashedMsg(e){
    if (!e.target.classList.contains('flash-close')) return;
    e.target.closest('.flash-msg').outerHTML = '';
}


function updateRadiusText(){
    if(radiusSlider){
        radiusText.textContent = radiusSlider.value
    }
}

window.addEventListener('load',updateRadiusText)

body.addEventListener('input', function(e){
    if(!radiusSlider) return;
    updateRadiusText();
}) 

if(document.getElementById('instruments')){
    const instrument_select = new SlimSelect({
        select: '#instruments'
    })
}

if(document.getElementById('genres')){
const genre_select = new SlimSelect({
    select: '#genres'
})
}

if(document.getElementById('instruments-search')){
const instrument_search = new SlimSelect({
    select: '#instruments-search'
})
}

if(document.getElementById('genres-search')){
const genre_search = new SlimSelect({
    select: '#genres-search'
})
}


  
