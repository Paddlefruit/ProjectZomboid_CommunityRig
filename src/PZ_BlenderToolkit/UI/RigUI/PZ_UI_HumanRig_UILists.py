# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import UIList

class PZ_UL_BodyTextureList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.label(text=item.name)


class PZ_UL_ClothingMeshList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        row.label(text=item.name)

        viewport_icon = "RESTRICT_VIEW_OFF" if item.slot_hide_viewport else "RESTRICT_VIEW_ON"
        row.prop(item, 'slot_hide_viewport', text="", icon=viewport_icon)

        render_icon = "RESTRICT_RENDER_OFF" if item.slot_hide_render else "RESTRICT_RENDER_ON"
        row.prop(item, 'slot_hide_render', text="", icon=render_icon)


class PZ_UL_PropMeshList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        row.label(text=item.name)
        row.label(text=item.attach_bone)

        viewport_icon = "RESTRICT_VIEW_OFF" if item.slot_hide_viewport else "RESTRICT_VIEW_ON"
        row.prop(item, 'slot_hide_viewport', text="", icon=viewport_icon)

        render_icon = "RESTRICT_RENDER_OFF" if item.slot_hide_render else "RESTRICT_RENDER_ON"
        row.prop(item, 'slot_hide_render', text="", icon=render_icon)

class PZ_UL_EquippedAttachmentList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        row.label(text=item.name)

class PZ_UL_ZombieInjuryList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        row.label(text=item.name)