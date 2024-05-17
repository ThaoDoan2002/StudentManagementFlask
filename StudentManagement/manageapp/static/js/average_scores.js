document.addEventListener("DOMContentLoaded", function() {
    var firstSelect = document.getElementById("first-select");
    var secondSelect = document.getElementById("second-select");
    var selectedClassId = ''; // Biến để lưu giữ ID của lớp được chọn
    var isLoading = false; // Biến cờ để kiểm tra xem yêu cầu AJAX trước đã hoàn thành chưa

    // Lắng nghe sự kiện "change" trên select thứ nhất
    firstSelect.addEventListener("change", function() {
        var selectedYear = firstSelect.value;

        // Kiểm tra nếu đã có yêu cầu AJAX đang được xử lý, không gửi yêu cầu mới
        if (isLoading) {
            return;
        }

        // Xóa các option cũ trong select box lớp
        secondSelect.innerHTML = '<option value="">Chọn lớp</option>';

        // Đặt isLoading thành true để chỉ ra rằng yêu cầu AJAX đang được xử lý
        isLoading = true;

        // Gửi yêu cầu Fetch API để lấy danh sách các lớp dựa trên năm đã chọn
        fetch(`/api/classes?year=${selectedYear}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(classes => {
                classes.forEach(cls => {
                    var option = document.createElement("option");
                    option.value = cls.id;
                    option.text = cls.name;
                    secondSelect.appendChild(option);
                });

                // Nếu có ID của lớp được chọn trước đó, chọn lại option đó
                if (selectedClassId) {
                    secondSelect.value = selectedClassId;
                }
            })
            .catch(error => {
                console.error('There was a problem with your fetch operation:', error);
            })
            .finally(() => {
                // Đặt isLoading thành false sau khi yêu cầu AJAX hoàn thành
                isLoading = false;
            });
    });

    // Lắng nghe sự kiện "change" trên select thứ hai để lưu giữ ID của lớp được chọn
    secondSelect.addEventListener("change", function() {
        selectedClassId = secondSelect.value;
    });
});
