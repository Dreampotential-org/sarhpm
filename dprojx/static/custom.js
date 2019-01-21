// capture all errors and send to slack
window.onerror = function (msg, url, lineNo, columnNo, error) {
    var string = msg.toLowerCase();
    var substring = "script error";
    if (string.indexOf(substring) > -1){
        alert('Script Error: See Browser Console for Detail');
    } else {
        var message = [
            'Message: ' + msg,
            'URL: ' + url,
            'Line: ' + lineNo,
            'Column: ' + columnNo,
            'Error object: ' + JSON.stringify(error)
        ].join(' - ');


        $.ajax({
            url: '/log-errors/',
            data: JSON.stringify({
              'error': message,
            }),
            type: 'post',
            success: function(results) {
                //callback(JSON.parse(results))
            }
        })
    }
    return false;
};


var GLOBAL_FILE = null;
var CURRENT_POSITION = null;

function init_all() {
    // hack email to fix validation
    $("input[name='email']").attr("type", "email")
    $(".secAction .btnVideo").on('click', function(e) {
        e.preventDefault();
        $('#upload-vid').click()
    });

    $('#upload_vid_form').submit(function(e) {
        e.preventDefault();
        // uploadBtn.disabled = true;
        // const userObj = JSON.parse(localStorage.getItem('user'));
        var data = new FormData();
        data.append("file", GLOBAL_FILE, GLOBAL_FILE.name);
        //data.append("lat", document.getElementById('lat').innerHTML);
        //data.append("lng", document.getElementById('lng').innerHTML);
        //data.append("userId", userObj.userId);

        var xhr = new XMLHttpRequest();
        // xhr.withCredentials = true;
        xhr.onprogress = function (e) {
            if (e.lengthComputable) {
                console.log(e.loaded+  " / " + e.total)
            }
        }

        xhr.addEventListener("readystatechange", function() {
            if (this.readyState === 4) {
                if (this.status == 200) {
                    swal({
                      title: "Good job!",
                      text: "Video submitted successfully!",
                      icon: "success",
                    });
                    $("#overlay_loading").hide()
                } else {
                    alert('data upload failed');
                }
            }
        });
        $("#overlay_loading").show()
        xhr.open("POST", "/upload/");
        //xhr.setRequestHeader("authorization", `Token ${userObj.token}`);
        xhr.send(data);
    });

    $('#upload-vid').on('change', function(e) {
        e.preventDefault();
        var file = e.target.files[0];
        GLOBAL_FILE = file;
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
    //$('#locationAuth').on('click', function(e) {
    //  e.preventDefault();
      //$('#LocationModal').addClass('is-visible');
    //});
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


    $('#locationAuth').on('click', function(e) {
        var text = $(".mainContainer textarea").val()
        if (CURRENT_POSITION == null) {
            alert("No GPS Signal. Try again");
            return
        }

        $("#overlay_loading").show()
        $.ajax({
            url: '/gps-checkin/',
            data: {
              'msg': text,
              'lat': CURRENT_POSITION.coords.latitude,
              'long': CURRENT_POSITION.coords.longitude,
            },
            type: 'post',
            success: function(results) {
                if (results.status && results.status == 'okay') {
                    console.log(results)
                    swal({
                      title: "Good job!",
                      text: "Gps and Note submitted successfully!",
                      showCancelButton: false,
                      confirmButtonText: "ok",
                      allowOutsideClick: false,
                      type: "success",
                    }).then(function() {
                        window.location = '/';
                    })
                    $("#overlay_loading").hide()
                }
            }
        });
    });

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
