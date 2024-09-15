from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'amfui/index.html')

def log_index(request):
    return render(request, "building.html", {"Title":"建设中"});

def liveStaterV(self, request):
    #return render(request, "amfui/livestate.html")
    data_list = self.model.objects.all().values_list("Cell_id").distinct()
    header_list=[]
    for field in self.list_display:
        obj = self.model._meta.get_field(field)
        val = obj.verbose_name
        header_list.append(val)
    # 构建数据表单部分 
    new_data_list = []
    for obj in data_list:
        temp = []
        for field in self.list_display: 
            val = getattr(obj,field)
            temp.append(val)
        new_data_list.append(temp)
    return render(request, "amfui/livestate.html" ,locals())