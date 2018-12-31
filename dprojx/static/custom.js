function init_all() {

    $(".secAction .btnVideo").on('click', function(e) {
        $('#upload-vid').click()
    });

    $(".secAction .btnEvent").on('click', function(e) {
        window.location = '/gps-checkin';
    });


    $('#signin').on('click', function(e) {
      e.preventDefault();
      $('#signinModal').addClass('is-visible');
    });
    $('#signup').on('click', function(e) {
      e.preventDefault();
      $('#signupModal').addClass('is-visible');
    });
    $('#locationAuth').on('click', function(e) {
      e.preventDefault();
      $('#LocationModal').addClass('is-visible');
    });
    $('.modal-overlay').on('click', function(e) {
      $('.modal').removeClass('is-visible');
    });
    $('.toggleBar').on('click', function(e) {
      $('.slideMenu').toggle();
        $(this).toggleClass('toggleClose');
    });


    handle_gps()
}


function handle_gps() {
    if (!(window.location.pathname == '/gps-checkin/')) {
        return
    }

   function geo_error() {
      alert("Sorry, no position available.");
    }

    var geo_options = {
      enableHighAccuracy: true,
      maximumAge        : 30000,
      timeout           : 27000
    };

    var wpid = navigator.geolocation.watchPosition(
        geo_success, geo_error, geo_options
    );
    function geo_success(position) {
        CURRENT_POSITION = position
        console.log(position.coords.latitude +
                    " " +  position.coords.longitude);
    }
}

window.addEventListener("DOMContentLoaded", init_all, false);
