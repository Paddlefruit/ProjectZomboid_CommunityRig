# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import Menu

class PZ_AddMenuSubmenu(Menu):
    bl_idname = 'PZ_MT_add_menu_submenu'
    bl_label = 'Zomboid'

    def draw(self, context):
        layout = self.layout

        layout.operator('zomboid.create_rig', text='Human Rig')