$(document).ready(function() {
  const params = new URLSearchParams(location.search);
  const params_d = params.get('d');

  if (params_d) {
    for (const radio of $('input:radio[name="displaymode"]')) {
      if (radio.value == params_d) {
        radio.checked = true;
      }
    }  
  }

  $('input:radio[name="displaymode"]').change(function(){
    const displaymode = $('input:radio[name="displaymode"]:checked').val();
    location.href = location.pathname + "?d=" + displaymode;
  });
});