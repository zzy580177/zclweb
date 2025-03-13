from django.shortcuts import render, redirect
from .models import *
from django.http import HttpResponse
from datetime import datetime, timedelta, time
from django.contrib import messages
from django.db.models import Case, When, Value, IntegerField, Q,F, BooleanField, ExpressionWrapper, DateField


def check_screen_type(request):
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    is_mobile = any(keyword in user_agent for keyword in [
        'Android', 'iPhone', 'iPad', 'iPod', 'BlackBerry', 'Windows Phone'
    ])
    if is_mobile:
        return 1
    else:
        return 3


# Create your views here.
def index(request):
    return render(request, 'amfui/index.html')

def dashboard(request):
    viewsize = check_screen_type(request)
    if request.method=="POST":
        offset = request.POST.get("offset")
    if (viewsize == 3):
        return render(request, 'dashboard.html', {'offset':0,'viewsize':viewsize})
    else:
        return render(request, 'dashboard_min.html', {'offset':0,'viewsize':viewsize})

def extend_home(request):
    offset = 3;
    if request.method=="POST":
        offset = request.POST.get("offset")
    return render(request, 'extend_home.html', {'offset':offset})

def test(request):
    offset = 3;
    if request.method=="POST":
        offset = request.POST.get("offset")
    return render(request, 'test.html')

def worksheet_view(request):
    from .models import WorkSheet, Order  # 延迟导入 WorkSheet 模型
    order_id = request.GET.get('q')
    worksheets = WorkSheet.objects.filter(Order_id=order_id)
    Order = list(Order.objects.filter(OrderId=order_id))
    return render(request, 'amfui/worksheet_list.html', {'worksheets': worksheets, 'Order': Order})

def worksheet_manage_view(request):
    from .models import WorkSheet, Order, Cell  # 延迟导入 WorkSheet 模型
    order_id = request.GET.get('q')
    if request.method == "POST":
        if 'confirm_order' in request.POST:
            order = Order.objects.get(OrderId=order_id)
            order.Product_id = request.POST.get('ProductID')
            order.ReqParts = request.POST.get('ReqParts')
            order.Status = request.POST.get('Status')
            deadline_date = request.POST.get('DeadLine')
            order.DeadLine = datetime.strptime(deadline_date + ' 23:59', '%Y-%m-%d %H:%M')  # 在日期的基础上加上时分部分
            if order.Status == '已完成':
                order.Progress = 100
            order.save()
        elif 'new_worksheet' in request.POST:
            cell_value = request.POST.get('Cell_id')
            cell_id, cell_db_id = cell_value.split('|')
            current_time = datetime.now().strftime('%y%m%d%H%M%S')
            worksheet_id = f"{current_time}-{cell_id}"
            new_worksheet = WorkSheet(
                Id=worksheet_id,
                Order_id=request.POST.get('OrderID'),
                Product_id=request.POST.get('ProductID'),
                Status='未就绪',
                Cell_id=cell_db_id,
                ReqParts=request.POST.get('ReqParts'),
                ProcessID=request.POST.get('ProcessID'),
                FinishParts=0,
                AddReqParts=0
            )
            new_worksheet.save()
        return redirect(f'/amfui/worksheet/manage/?q={order_id}')
    worksheets = WorkSheet.objects.filter(Order_id=order_id)
    Order = list(Order.objects.filter(OrderId=order_id))
    cells = Cell.objects.all()
    return render(request, 'amfui/worksheet_manage.html', {'worksheets': worksheets, 'Order': Order, 'cells': cells})

def delete_worksheet(request, worksheet_id):
    from .models import WorkSheet
    worksheet = WorkSheet.objects.get(Id=worksheet_id)
    if worksheet.Status == '未就绪':
        worksheet.delete()
    return redirect(request.META.get('HTTP_REFERER'))

def delete_order(request):
    from .models import Order, WorkSheet
    order_id = request.GET.get('q')
    order = Order.objects.get(OrderId=order_id)
    worksheets = WorkSheet.objects.filter(Order_id=order_id)
    if not worksheets.exists():
        order.delete()
        return redirect('/amf/amfui/order/')
    else:
        messages.error(request, "订单有关联的工单号，删除失败")
        return redirect('/amf/amfui/order/')

def new_order(request):
    from .models import Order
    if request.method == "POST":
        order_id = request.POST.get('OrderId')
        if Order.objects.filter(OrderId=order_id).exists():
            messages.error(request, "订单编号已存在，新增订单失败")
            return redirect('/amf/amfui/order/')
        product_id = request.POST.get('Product_id')
        req_parts = request.POST.get('ReqParts')
        status = request.POST.get('Status')
        deadLine = request.POST.get('DeadLine')
        try:

            deadline_date = request.POST.get('DeadLine')
            new_order = Order(
                OrderId=order_id,
                Product_id=product_id,
                ReqParts=req_parts,
                DeadLine=datetime.strptime(deadline_date + ' 23:59', '%Y-%m-%d %H:%M'),
                Progress=0,
                Status='未就绪'
            )
            new_order.save()
            return redirect('/amf/amfui/order/')
        except Exception as e:
            print("新订单追加失败:", e)
            messages.error(request, "新订单追加失败")
            return redirect('/amf/amfui/order/')
    return render(request, 'amfui/order_add.html')

def celltask_manage_view(request):
    from .models import Cell, WorkSheet, Order  # 延迟导入 CellTask 模型
    cell_CellID = request.GET.get('q')
    cell = Cell.objects.get(CellID=cell_CellID)
    now_plus_7_days = datetime.now() + timedelta(days=7)
    today = datetime.combine(datetime.now().date(), time(23, 59, 59))  # 设置为当天的23:59:59

    is_due_soon = Case(
        When(Q(Order__DeadLine__lte=now_plus_7_days) & ~Q(Status='已完成'), then=Value(True)),
        default=Value(False),
        output_field=BooleanField()
    )

    is_due_today = Case(
        When(Q(Order__DeadLine__lte=today) & ~Q(Status='已完成'), then=Value(True)),
        default=Value(False),
        output_field=BooleanField()
    )

    worksheets_unready = WorkSheet.objects.filter(Cell_id=cell.id, Status='未就绪').annotate(
        is_due_soon=is_due_soon,
        is_due_today=is_due_today).order_by('Order__DeadLine')
    worksheets = WorkSheet.objects.filter(Cell_id=cell.id).exclude(Status='未就绪').annotate(
        status_order=Case(
            When(Status='就绪', then=Value(2)),
            When(Status='加工中', then=Value(3)),
            When(Status='暂停', then=Value(4)),
            When(Status='已完成', then=Value(5)),
            default=Value(6),
            output_field=IntegerField(),
        ),
        is_due_soon=is_due_soon,
        is_due_today=is_due_today
    ).order_by('status_order', 'Order__DeadLine')
    orders_unready = Order.objects.filter(Status='未就绪').annotate(
        is_due_soon = Case(When(Q(DeadLine__lte=now_plus_7_days), then=Value(True)),
                           default=Value(False),output_field=BooleanField()),
        is_due_today = Case(When(Q(DeadLine__lte=today), then=Value(True)), 
                            default=Value(False),output_field=BooleanField())).order_by('DeadLine')
 
    if request.method == "POST":
        order_id = request.POST.get('OrderID')
        order = Order.objects.get(OrderId=order_id)
        if 'new_worksheet' in request.POST:
            current_time = datetime.now().strftime('%y%m%d%H%M%S')
            worksheet_id = f"{current_time}-{cell_CellID}"
            new_worksheet = WorkSheet(
                Id=worksheet_id,
                Order_id=order_id,
                Product_id=order.Product_id,
                Status='未就绪',
                Cell_id= cell.id,
                ReqParts=request.POST.get('ReqParts'),
                ProcessID=request.POST.get('ProcessID'),
                FinishParts=0,
                AddReqParts=0
            )
            new_worksheet.save()
            return redirect(f'/amfui/celltask/manage/?q={cell_CellID}')

        return redirect(f'/amfui/celltask/manage/?q={cell_CellID}')
    
    return render(request, 'amfui/celltask_manage.html', {'cell': cell, 'worksheets': worksheets, 'worksheets_unready': worksheets_unready, 'orders_unready': orders_unready, 'now_plus_7_days': now_plus_7_days})