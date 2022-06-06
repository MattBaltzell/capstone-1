const heroVid = document.getElementById('hero-vid')
const navMenuBtn = document.getElementById('nav-menu_btn')
const navMenu = document.getElementById('nav-menu')
const body = document.querySelector('body')
const radiusText = document.querySelector('.radius_text')
const radiusSlider = document.querySelector('.radius_slider')
const editForm = document.getElementById('user_form')
const messageCount = document.getElementById('message_count')
const loadingContainer = document.getElementById('loading_container')
const contentContainer = document.getElementById('content_container')

const VIDEO_PLAY_SPEED = .6
const BASE_URL = 'http://127.0.0.1:5000/'


//Slow down the home page bg video
if (heroVid){heroVid.playbackRate = VIDEO_PLAY_SPEED}



if(navMenuBtn){
    body.addEventListener('click', function(e){
        if(e.target.classList.contains('nav_menu')){
            navMenu.classList.toggle('hidden')
        } else{
            navMenu.classList.add('hidden')
        }
    })
}

if(messageCount){
    function setMessageCount(n){
        messageCount.text(n);
        messageCount.style.visibility = n ? 'visible' : 'hidden';
    }
}

// Remove Loading spinner & Display Content on DOM Content Loaded
window.addEventListener('DOMContentLoaded', (e) => {
    loadingContainer.remove();
    contentContainer.style.visibility = 'visible';
    contentContainer.style.display = 'block';
});

// Update message notifications
window.addEventListener('load', (e) => {

    let since = 0;
    setInterval( async function(){

        const res = await axios.get('BASE_URL/notifications?since=' + since)
        const notifications = res.data

        for (var i = 0; i < notifications.length; i++) {
            if (notifications[i].name == 'unread_message_count')
                setMessageCount(notifications[i].data);
            since = notifications[i].timestamp;
        }
            
    }, 10000);
})

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


  
