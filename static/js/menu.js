(function () {
  "use strict";

  $(function () {
    $(".menu-container").load("{{url_for(filename = 'menu.html')}}");
  });
})();