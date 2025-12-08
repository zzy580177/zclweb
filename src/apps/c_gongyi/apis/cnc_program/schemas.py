from ninja import ModelSchema
from apps.c_gongyi.models import *


class CNCProgramIn(ModelSchema):
    
    process_id: int
    

    class Meta:
        model = CNCProgram
        fields = ['create_time', 'update_time', 'is_deleted', 'deleted_at', 'deleted_by', 'program_name', 'equipment_model', 'fixture_name', 'simulation_time', 'description', 'path', ]


class CNCProgramOut(ModelSchema):
    class Meta:
        model = CNCProgram
        fields = ['id', 'create_time', 'update_time', 'is_deleted', 'deleted_at', 'deleted_by', 'process', 'program_name', 'equipment_model', 'fixture_name', 'simulation_time', 'description', 'path', ]
