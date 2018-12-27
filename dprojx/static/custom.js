function init_all() {

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

}
window.addEventListener("DOMContentLoaded", init_all, false);
