$(document).ready(function() {
    objectId = null            
    $(document).keypress(function(event){
        objectId = event.originalEvent.key
        if (objectId.match(/^IRCAM_[a-z0-9]{5}$/)) {
            let url_mask = "{% url 'alessandria:reader_borrow_update' pk=99999 %}".replace(/99999/, objectId);
            document.location.replace(url_mask)
        }
    })
})