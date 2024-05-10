function changeColumn() {
    var type_15m = parseInt(document.getElementById("type_1").value);
    var type_1h = parseInt(document.getElementById("type_2").value);

    if (isNaN(type_15m)) {
        alert("Vui lòng nhập giá trị cho số lượng điểm 15 phút!");
    } else if (isNaN(type_1h)) {
        alert("Vui lòng nhập giá trị cho số lượng điểm 1 tiết!");
    } else if (type_15m < 1 || type_15m > 5) {
        alert("Vui lòng nhập lại! Tối thiểu 1 và tối đa 5 cột điểm 15 phút.");
    } else if (type_1h < 1 || type_1h > 3) {
        alert("Vui lòng nhập lại! Tối thiểu 1 và tối đa 3 bài kiểm tra 1 tiết.");
    } else {
        var td1Elements = document.querySelectorAll('.td_1');
        var td2Elements = document.querySelectorAll('.td_2');

        td1Elements.forEach(function(td) {
            var studentId = td.dataset.studentId;
            var inputsHTML1 = '';
            for (var i = 0; i < type_15m; i++) {
                inputsHTML1 += `<input type="number" class="form-control mt-1" required pattern="^(10|[0-9])$" min="0" max="10" name="score_1_${studentId}_${i}" style="width:150px">`;
            }
            td.innerHTML = inputsHTML1;
        });

        td2Elements.forEach(function(td) {
            var studentId = td.dataset.studentId;
            var inputsHTML2 = '';
            for (var i = 0; i < type_1h; i++) {
                inputsHTML2 += `<input type="number" class="form-control mt-1" required pattern="^(10|[0-9])$" min="0" max="10" name="score_2_${studentId}_${i}" style="width:150px">`;
            }
            td.innerHTML = inputsHTML2;
        });
    }
}
