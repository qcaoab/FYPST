function getUrlParameter(sParam)
{
    var sPageURL = window.location.search.substring(1);
    var sURLVariables = sPageURL.split('/');
    for (var i = 0; i < sURLVariables.length; i++) 
    {
      
        //var sParameterName = sURLVariables[i].split('/');
        //for (var j = 0; j < sURLVariables.length; j++) 
        if (sURLVariables[i] == sParam) 
        {
            return sURLVariables[i+1];
        }
           
    }
    return 'nothing'
}
  