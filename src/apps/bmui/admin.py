from django.contrib import admin
from django.http import JsonResponse
from django.urls import path
from django.shortcuts import render
from .models import Material, BOM, BOMLevel
import csv
import io


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ['Id', 'Name', 'Type', 'Source', 'Attribute', 'Description']
    change_list_template = "material_changelist.html"  # 自定义模板

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-materials/', self.import_materials, name='import_materials'),
        ]
        return custom_urls + urls

    def import_materials(self, request):
        """处理 Excel 粘贴的快速录入"""
        if request.method == "POST":
            pasted_data = request.POST.get("pasted_data")
            if pasted_data:
                csv_reader = csv.reader(io.StringIO(pasted_data))
                for row in csv_reader:
                    if len(row) >= 4:  # 确保至少有 4 列数据
                        Material.objects.create(
                            Name=row[0],
                            Type=row[1],
                            Source=row[2],
                            Attribute=row[3],
                            Description=row[4] if len(row) > 4 else ""
                        )
                return JsonResponse({"success": True, "message": "物料已成功导入！"})
        return JsonResponse({"success": False, "message": "导入失败，请检查数据格式！"})


#@admin.register(BOM)
class BOMAdmin(admin.ModelAdmin):
    list_display = ['Id','Material','Quantity','ParentBOM',]


#@admin.register(BOMLevel)
class BOMLevelAdmin(admin.ModelAdmin):
    list_display = ['Id','BOM','Level',]



