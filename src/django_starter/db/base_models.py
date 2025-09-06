from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.validators import MinValueValidator 

schema = settings.DATABASES["default"].get("SCHEMA", "default_schema")
bmuiAppName = 'bmui'
pmcuiAppName = 'pmcui'
scgAppName = 'jihuaManagerUI' 

max_charTextLen = 200
max_charNameLen = 100
max_charIdLen = 20
max_charStateLen = 10
BOM_STATUS_CHOICES = [
    ('草稿', '草稿'),
    ('生效', '生效'),
    ('失效', '失效'),
    ('归档', '归档'),
]


class base_model(models.Model):
    """抽象基类，包含通用字段和方法"""
    createTime = models.DateTimeField("创建时间", auto_now_add=True)
    updateTime = models.DateTimeField("更新时间", auto_now=True)
    is_deleted = models.BooleanField("是否删除", default=False, db_index=True)
    deleted_at = models.DateTimeField("删除时间", null=True, blank=True)
    deleted_by = models.CharField("删除人", max_length=50, null=True, blank=True)
    
    class Meta:
        abstract = True  # 抽象基类，不会创建数据库表
    
    def delete(self, using=None, keep_parents=False, deleted_by=None):
        """重写删除方法，实现软删除"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        if deleted_by:
            self.deleted_by = deleted_by
        self.save()
    
    def hard_delete(self, using=None, keep_parents=False):
        """物理删除"""
        super().delete(using=using, keep_parents=keep_parents)
    
    class QuerySet(models.QuerySet):
        def alive(self):
            return self.filter(is_deleted=False)
        
        def deleted(self):
            return self.filter(is_deleted=True)
        
        def delete(self, deleted_by=None):
            return self.update(
                is_deleted=True,
                deleted_at=timezone.now(),
                deleted_by=deleted_by
            )
    
    class Manager(models.Manager):
        def get_queryset(self):
            return base_model.QuerySet(self.model).alive()
        
        def all_with_deleted(self):
            return base_model.QuerySet(self.model)
        
        def only_deleted(self):
            return self.all_with_deleted().deleted()
        
        def restore(self, *args, **kwargs):
            return self.only_deleted().update(
                is_deleted=False,
                deleted_at=None,
                deleted_by=None
            )
        
class AutoCodeField(models.CharField):
    def __init__(self, prefix='MG_', length=5, *args, **kwargs):
        self.prefix = prefix
        self.length = length
        kwargs.setdefault('max_length', 50)  # 设置足够的长度来容纳动态前缀
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname)
        if not value:
            # 获取当前前缀（可能是动态设置的）
            current_prefix = getattr(self, 'prefix', 'MG_')
            
            Model = model_instance.__class__
            # 使用当前前缀进行查询
            last = Model.objects.filter(**{f"{self.attname}__startswith": current_prefix}).order_by(f'-{self.attname}').first()
            
            if last:
                # 从已有的代码中提取数字部分
                last_code = getattr(last, self.attname)
                if last_code.startswith(current_prefix):
                    try:
                        num_part = last_code[len(current_prefix):]
                        num = int(num_part) + 1
                    except (ValueError, IndexError):
                        num = 1
                else:
                    num = 1
            else:
                num = 1
                
            value = f"{current_prefix}{num:0{self.length}d}"
            setattr(model_instance, self.attname, value)
        return value


class Attribute(models.Model):
    """属性表"""
    attribute_id = models.AutoField("属性序号", primary_key=True)
    name = models.CharField("属性名称", max_length=max_charIdLen, unique=True)
    description = models.TextField("描述", null=True, blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        abstract = True

class MaterialGroup(base_model):
    """物料组表"""
    GROUP_CHOICES = [("01", "成品机"), ("02", "半成品件"), ("03", "外购件"), ("04", "中间件")]
    SUB_GROUP_CHOICES = [
        ("01.01", "成品整机"),
        ("01.02", "成品夹具"),
        ("01.03", "客制模具"),
        ("01.04", "成品机部件"),
        ("02.01", "整机钣金件"),
        ("02.02", "夹具钣金件"),
        ("02.03", "整机机加件"),
        ("02.04", "夹具机加件"),
        ("02.05", "ZCL标准机加件"),
        ("02.06", "临时机加件"),
        ("02.07", "返工类机加件"),
        ("02.KZ", "客制模具"),
        ("03.01", "电器类"),
        ("03.02", "气动类"),
        ("03.03", "五金类"),
        ("03.04", "刀具类"),
        ("03.05", "其它类"),
    ]

    group_id = models.AutoField(primary_key=True, verbose_name="序号")
    name = models.CharField("名称", max_length=max_charNameLen)  
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
        related_name="children", verbose_name="父组")
    number = models.CharField("编号", max_length=max_charIdLen, null=True, blank=True)  
    level = models.IntegerField("层级", null=True, blank=True) 
    group = models.CharField("一级分类", max_length=max_charIdLen, null=True, blank=True, choices=GROUP_CHOICES) 
    sub_group = models.CharField("二级分类", max_length=max_charIdLen, null=True, blank=True, choices=SUB_GROUP_CHOICES)  
    min_group = models.CharField("三级分类", max_length=max_charIdLen, null=True, blank=True)  

    def __str__(self):
        if self.number:
            return f"{self.number}"
        return self.name

    def get_parent(self):
        """获取父组"""
        return self.parent

    def get_children(self):
        """获取所有子组"""
        return self.children.all()
    
    def save(self, *args, **kwargs):
        """覆盖 save 方法，自动分配未使用的 group_id"""
        if not self.group_id:
            # 使用AutoField自动分配ID，不需要手动处理
            pass
        super().save(*args, **kwargs)

    class Meta:
        abstract = True

