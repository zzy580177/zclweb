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
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)
    is_deleted = models.BooleanField("是否删除", default=False, db_index=True)
    deleted_at = models.DateTimeField("删除时间", null=True, blank=True)
    deleted_by = models.CharField("删除人", max_length=50, null=True, blank=True)
    
    class Meta:
        abstract = True  # 抽象基类，不会创建数据库表

    # 提供默认 manager（过滤已删除）以及未过滤的原始 manager
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

    objects = Manager()            # 默认 manager：不返回已删除项
    all_objects = models.Manager() # 原始 manager：返回所有项，包括已删除

class AutoCodeField(models.CharField):
    def __init__(self, prefix='MG_', length=5, *args, **kwargs):
        self.prefix = prefix
        self.length = length
        kwargs.setdefault('max_length', 50)
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname)
        if not value:
            current_prefix = getattr(self, 'prefix', 'MG_')

            Model = model_instance.__class__
            manager = getattr(Model, '_default_manager', Model.objects)
            last = manager.filter(**{f"{self.attname}__startswith": current_prefix}).order_by(f'-{self.attname}').first()

            if last:
                last_code = getattr(last, self.attname) or ''
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





