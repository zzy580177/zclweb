($) => {
    $(document).ready(function() {
        // 监听主分类变化
        $('#changelist-filter select[name="FGroup__FClass__exact"]').change(function() {
            // 获取选中的主分类值
            var primary = $(this).val();
            // 重置子分类
            var GroupCodeSelect = $('#changelist-filter select[name="GroupCode"]');
            GroupCodeSelect.empty();
            url = "{% url 'admin:bmui_material_getgroup' %}"

            if (primary) {
                // 发起 AJAX 请求获取子分类数据
                $.ajax({
                    url: url,
                    method: 'GET',
                    data: { FClass: primary }, // 传递主分类值
                    success: function(response) {
                        // 动态添加选项
                        response.forEach(function(item) {
                            GroupCodeSelect.append(`<option value="${item.FGroupCode}">${item.FGroupCode} - ${item.FName}</option>`);
                        });
                        // 触发 change 事件更新 URL
                        GroupCodeSelect.change();
                    },
                    error: function(xhr, status, error) {
                        console.error('获取子分类数据失败:', error);
                    }
                });
            }
        });
    });
};
(django.jQuery);
