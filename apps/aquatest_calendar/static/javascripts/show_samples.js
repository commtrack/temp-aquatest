  function show_samples(year,month,day,area,div_id) {
    $(div_id).jqm({ajax: '/samplepop/?date='+year+'-'+month+'-'+day+'-'+area, trigger: 'div.formtrigger',
                  ajaxText: 'Please wait while we load that for you'});}