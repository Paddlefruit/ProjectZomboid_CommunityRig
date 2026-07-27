# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import UIList

class PZ_UL_RigList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.label(text=item.obj.pz_human_props.rig_name)
        row.label(text=str(item.obj.pz_human_props.rig_instance))