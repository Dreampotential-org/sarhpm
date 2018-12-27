function init_all() {

    $(".secAction .btnVideo").on('click', function(e) {
        window.location = '/record-video';
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


    //For Firefox we have to handle it in JavaScript
    var vids = $("video");
    $.each(vids, function(){
           this.controls = false;
    });
    //Loop though all Video tags and set Controls as false

    $("video").click(function() {
      //console.log(this);
      if (this.paused) {
        this.play();
      } else {
        this.pause();
      }
    });

    handle_video();
}

function handle_video() {
    var videoBlob;
    const uploadBtn = document.getElementById('btn-upload');
    var options = {
        controls: true,
        width: 1080,
        height: 720,
        fluid: false,
        plugins: {
            record: {
                audio: true,
                video: true,
                maxLength: 3600,
                debug: true
            }
        }
    };
    var player = videojs('myVideo', options, function() {
        // print version information at startup
        var msg = 'Using video.js ' + videojs.VERSION +
            ' with videojs-record ' + videojs.getPluginVersion('record') +
            ' and recordrtc ' + RecordRTC.version;
        document.getElementById('start').addEventListener('click', function() {
            document.getElementsByClassName('vjs-icon-record-start')[0].click()
        });
        document.getElementById('stop').addEventListener('click', function() {
            document.getElementsByClassName('vjs-icon-record-stop')[0].click()
        });
        document.getElementsByClassName('vjs-icon-av-perm')[0].click();

    });
    // error handling
    player.on('deviceError', function() {
        alert('device not supported ' + player.deviceErrorCode);
    });
    player.on('error', function(error) {
        alert('unable to record video');
    });

    // user completed recording and stream is available
    player.on('finishRecord', function() {
        // the blob object contains the recorded data that
        // can be downloaded by the user, stored on server etc.
        console.log('finished recording: ', player.recordedData);
        videoBlob = player.recordedData;
        uploadBtn.disabled = false;
    });
    uploadBtn.addEventListener('click', function() {
        alert('About to upload video.');
        uploadBtn.disabled = true;
        const userObj = JSON.parse(localStorage.getItem('user'));
        var data = new FormData();
        data.append("file", videoBlob, videoBlob.name);
        // data.append("lat", document.getElementById('lat').innerHTML);
        //data.append("lng", document.getElementById('lng').innerHTML);

        data.append("userId", userObj.userId);
        var xhr = new XMLHttpRequest();
        xhr.withCredentials = true;
        xhr.addEventListener("readystatechange", function() {
            if (this.readyState === 4) {
                if (this.status == 200) {
                    alert('data uploaded');
                } else {
                    alert('data upload failed');
                }
            }

        });

        xhr.open("POST", "/api/upload");
        xhr.setRequestHeader("authorization", `Token ${userObj.token}`);
        xhr.send(data);
    });


}


window.addEventListener("DOMContentLoaded", init_all, false);
