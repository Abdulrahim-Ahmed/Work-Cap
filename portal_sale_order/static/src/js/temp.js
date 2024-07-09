$(document).ready(function () {

    $(document).on('click', '.add', function () {
        var html = '';

        html += '<tr>';
        html += '<td><select type="text" name="item_name" class="form-control item_name" placeholder="Item"  required="True"></select></td>';
        html += '<td><input type="text" name="item_quantity" class="form-control item_quantity"  placeholder="Quantity"  required="True"/></td>';
        html += '<td><button type="button" name="remove" class="btn btn-danger btn-sm remove"><span class="glyphicon glyphicon-minus">Remove</span></button></td></tr>';
        $('#item_table').append(html);
        var x = document.getElementsByClassName("item_name");
        var i;
        for (i = 0; i < x.length; i++) {

            if(x[i].getAttribute("done")!=1) {
                x[i].innerHTML = document.getElementById("projects").innerText;
                x[i].setAttribute("name", "item" + i);
                x[i].setAttribute("id", "item" + i);
                x[i].setAttribute("done", "1");
            }

        }



        var x = document.getElementsByClassName("item_quantity");
        var i;
        for (i = 0; i < x.length; i++) {
            x[i].setAttribute("name", "q" + i);
        }
    });


    $(document).on('click', '.remove', function () {
        $(this).closest('tr').remove();
    });
});