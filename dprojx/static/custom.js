var GLOBAL_FILE = null;
function init_all() {

    $(".secAction .btnVideo").on('click', function(e) {
        e.preventDefault();
        $('#upload-vid').click()
    });

    $('#upload_vid_form').submit(function(e) {
        e.preventDefault();
        alert('About to upload video.');
        // uploadBtn.disabled = true;
        // const userObj = JSON.parse(localStorage.getItem('user'));
        var data = new FormData();
        data.append("file", GLOBAL_FILE, GLOBAL_FILE.name);
        //data.append("lat", document.getElementById('lat').innerHTML);
        //data.append("lng", document.getElementById('lng').innerHTML);
        //data.append("userId", userObj.userId);

        var xhr = new XMLHttpRequest();
        // xhr.withCredentials = true;

        xhr.addEventListener("readystatechange", function() {
            if (this.readyState === 4) {
                if (this.status == 200) {
                    alert('data uploaded');
                } else {
                    alert('data upload failed');
                }

            }
        });

        xhr.open("POST", "/upload/");
        //xhr.setRequestHeader("authorization", `Token ${userObj.token}`);
        xhr.send(data);
    });

    $('#upload-vid').on('change', function(e) {
        e.preventDefault();
        var file = e.target.files[0];
        GLOBAL_FILE = file;
        alert("trigger submit")
        $("#upload_vid_form").submit()
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
