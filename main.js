// write the current slider value for each table row
// get second tr (start here)


var params = ['mpwr', 'lpwr', 'ppwr', 'mmod', 'lmod', 'pmod', 'mbkn', 'lbkn', 'pbkn', 'testData'], i, value;
//var params = ['power', 'mode', 'pkt_length', 'pkt_number'], i, value;
var collect_values = function(p) {
  var ret = {}, i;
  for (i = 0; i < p.length; i++) {
    ret[p[i]] = $('input#' + p[i]).val();
  }
  return ret;
//   return JSON.stringify(ret);
};

/*
for (i = 0; i < params.length; i++)
{
  value = $('input#' + params[i]).val();
  $('tr#' + params[i]).append('<td id="' + params[i] + '">' + value + '</td>');
}
*/

$('input[type="range"]').on('change', function(e) {
  var id = $(this).attr('id'),
      min,
      max,
      current_val = $('input#pkt_length').val();

  $('td#' + id).text($(this).val());

  if (id === 'mode') {
    switch ($(this).val()) {
      case '1':
        min = 38;
        break;
      case '2':
        min = 80;
        break;
      case '3':
        min = 122;
        break;
      case '4':
        min = 164;
        break;
      case '5':
        min = 248;
        break;
    }
    max = min*16;

    // change min, max, and value attributes of pkt_length
    $('input#pkt_length').attr('min', min);
    $('input#pkt_length').attr('max', max);

    // if current_val outside the range, move it inside
    if (current_val < min)
    {
      $('input#pkt_length').prop('value', min);
      $('td#pkt_length').text(min);
    }
    else if (current_val > max)
    {
      $('input#pkt_length').prop('value', max);
      $('td#pkt_length').text(max);
    }
  }
});
/*
var send_data = function() {
  console.log(collect_values(params));
  $.ajax({
    method: 'POST',
    url: 'submit.py',
    data: collect_values(params)
  }).done(function() {
    alert(JSON.stringify(collect_values(params)));
  });
};
*/
