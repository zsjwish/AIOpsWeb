$(function () {
    var table = $('#example1').DataTable({
        'paging': true,
        'lengthChange': true,
        'searching': true,
        'ordering': true,
        'info': true,
        'autoWidth': true,
        "fnRowCallback": function (nRow, aData) {
            if (aData[3] < 0.5) {
                $('td', nRow).css('background-color', 'Orange');
            }
        }
    });

});