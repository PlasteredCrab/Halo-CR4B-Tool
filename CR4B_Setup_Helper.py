bl_info = {
    "name": "CR4B Installer",
    "author": "Crab and Austin",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "",
    "description": "Helps instantly reset the settings for CR4B Tool",
    "warning": "",
    "doc_url": "",
    "category": "",
}

import bpy

class SimpleOperator(bpy.types.Operator):
    bl_idname = "object.simple_operator"
    bl_label = "Apply CR4B Settings"
    
    def execute(self, context):
        # Here you can define the value you want to be applied into your CR4B Tool Preferences Panel
        
        #Path to the Export Assets Here folder
        export_path_value = "C:\\Users\\jeffr\\Documents\\CR4B Tool GitHub\\CR4B Tool v17\\Export Assets Here\\"
        
        #Path to the CR4BTool_shaders.blend file
        node_group_file_value = "C:\\Users\\jeffr\\Documents\\CR4B Tool GitHub\\CR4B Tool v20\\GitHub\\CR4BTool_shaders.blend"
        
        #Path to the Python_Modules folder
        python_path_value = "C:\\Users\\jeffr\\Documents\\CR4B Tool GitHub\\CR4B Tool v20\\GitHub\\Python_Modules\\"
        
        #Path to the tags folder of your various mod tools
        halo3_tag_path_value = "D:\\SteamLibrary\\steamapps\\common\\H3EK\\tags\\"
        odst_tag_path_value = "D:\\SteamLibrary\\steamapps\\common\\H3ODSTEK\\tags\\"
        reach_tag_path_value = "D:\\SteamLibrary\\steamapps\\common\\HREK\\tags\\"

        #Path to the Reclaimer CLI folder
        reclaimer_cli_path = "C:\\Users\\jeffr\\Documents\\CR4B Tool GitHub\\CR4B Tool v20\\GitHub\\Reclaimer CLI\\"
        
        hirt_path = "C:\\Users\\jeffr\\Documents\\CR4B Tool GitHub\\CR4B Tool v20\\GitHub\\HIRT CLI\\"
        
        h5bitmaptool_path = "D:\\Halo Stuff\\Halo 5 Xbox Bitmap extractor\\Halo 5 Xbox Extractor CLI\\bitmap converter\\"
        
        #Path to the .map files you want to use with Reclaimer CLI
        haloce_map_path = "D:\\SteamLibrary\\steamapps\\common\\Halo The Master Chief Collection\\halo1\\maps\\"
        halo2_map_path = "D:\\Halo Map Files\\Halo 2\\"
        halo3_map_path = "D:\\Halo Map Files\\Halo 3\\"
        halo3odst_map_path = "D:\\Halo Map Files\\Halo 3 ODST\\"
        haloreach_map_path = "D:\\Halo Map Files\\Halo Reach\\"
        halo4_map_path = "D:\\Halo Map Files\\Halo 4\\"
        halo5_mod_path = "G:\\Halo Builds\\Halo 5\\halo-5-x1\\halo-5-x1\\deploy\\"
        haloinfinite_map_path = "G:\\SteamLibrary\\steamapps\\common\\Halo Infinite\\deploy\\"

        # Name of the current version of CR4BTool
        addon_name = "CR4B_Tool_v20"
        
        # Accessing preferences from another addon
        bpy.context.preferences.addons[addon_name].preferences.export_path = export_path_value
        bpy.context.preferences.addons[addon_name].preferences.node_group_file = node_group_file_value
        bpy.context.preferences.addons[addon_name].preferences.py360convert_path = python_path_value
        
        bpy.context.preferences.addons[addon_name].preferences.halo3_tag_path = halo3_tag_path_value
        bpy.context.preferences.addons[addon_name].preferences.odst_tag_path = odst_tag_path_value
        bpy.context.preferences.addons[addon_name].preferences.reach_tag_path = reach_tag_path_value
        
        bpy.context.preferences.addons[addon_name].preferences.reclaimer_path = reclaimer_cli_path
        bpy.context.preferences.addons[addon_name].preferences.hirt_path = hirt_path
        bpy.context.preferences.addons[addon_name].preferences.h5bitmaptool_path = h5bitmaptool_path
        
        bpy.context.preferences.addons[addon_name].preferences.haloce_map_path = haloce_map_path
        bpy.context.preferences.addons[addon_name].preferences.halo2_map_path = halo2_map_path
        bpy.context.preferences.addons[addon_name].preferences.halo3_map_path = halo3_map_path
        bpy.context.preferences.addons[addon_name].preferences.halo3odst_map_path = halo3odst_map_path
        bpy.context.preferences.addons[addon_name].preferences.haloreach_map_path = haloreach_map_path
        bpy.context.preferences.addons[addon_name].preferences.halo4_map_path = halo4_map_path
        bpy.context.preferences.addons[addon_name].preferences.halo5_map_path = halo5_mod_path
        bpy.context.preferences.addons[addon_name].preferences.haloinfinite_map_path = haloinfinite_map_path

        self.report({'INFO'}, "Preferences Applied")
        return {'FINISHED'}

class SimplePanel(bpy.types.Panel):
    bl_label = "CR4B Tool Setup Tool"
    bl_idname = "PT_SimplePanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'CR4B Setup'
    
    def draw(self, context):
        layout = self.layout
        layout.operator("object.simple_operator", text="Apply CR4B Settings")

def register():
    bpy.utils.register_class(SimpleOperator)
    bpy.utils.register_class(SimplePanel)

def unregister():
    bpy.utils.unregister_class(SimpleOperator)
    bpy.utils.unregister_class(SimplePanel)

if __name__ == "__main__":
    register()
