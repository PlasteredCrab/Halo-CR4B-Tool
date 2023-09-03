# Halo CR4B Tool - Completely Ready 4 Blender Tool
#Created by Plastered_Crab
bl_info = {
    "name": "CR4B Tool",
    "description": "An addon that aims to get Halo 3/ODST/Reach levels and objects as close to game accurate as possible with one click",
    "author": "Add-on by Plastered_Crab. Shaders made by Chiefster with help from Soulburnin",
    "version": (2, 5),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar > CR4B Tool",
    "warning": "",
    "category": "3D View"
}

import bmesh
import glob
import bpy
import subprocess
import pathlib
import math
import time
import os
import re
import json
import struct
import ntpath
import sys
from bpy_extras import view3d_utils
import mathutils
from mathutils import Vector
import os.path
from mathutils import Matrix
from time import perf_counter
import cProfile
import pstats
import shutil
import ctypes
import numpy as np




#Start of the program
def Start_CR4B_Tool():

    #reset progress bar
    progress = 0.0
    yield progress

    #DEPENDANCIES NEEDED:
    #-py360convert
    #[INSTRUCTIONS] RUN BLENDER AS ADMINISTRATOR AND THEN USE THE "Install Py360Convert" BUTTON
    
    

    #update the context.scene
    #bpy.context.scene.update()
    
    #MUST SPECIFY THE ROOT FOLDER OF YOUR TAGS FOR HALO 3 HERE!!!!!
    log_to_file("Drop Down option: " + bpy.context.scene.tag_dropdown)
    log_to_file("Colorspace option: " + bpy.context.scene.colorspace_dropdown)
    #Tag_Root = ""
    
    if(bpy.context.scene.colorspace_dropdown == "Blender"):
        log_to_file("Using Blender Colorspace")
        Linear_Colorspace_Name = "Linear" 
    elif (bpy.context.scene.colorspace_dropdown == "AGX"):
        log_to_file("Using AGX Colorspace")
        Linear_Colorspace_Name = "Generic Data"
    
    if(bpy.context.scene.tag_dropdown == "Halo 3"):
        log_to_file("Using Halo 3 Tags")
        Tag_Root = bpy.context.preferences.addons[__name__].preferences.halo3_tag_path 
        log_to_file("halo3_tag_path: " + bpy.context.preferences.addons[__name__].preferences.halo3_tag_path)
    elif (bpy.context.scene.tag_dropdown == "Halo 3: ODST"):
        log_to_file("Using Halo 3: ODST Tags")
        log_to_file("odst_tag_path: " + bpy.context.preferences.addons[__name__].preferences.odst_tag_path)
        Tag_Root = bpy.context.preferences.addons[__name__].preferences.odst_tag_path
    elif (bpy.context.scene.tag_dropdown == "Halo Reach"):
        log_to_file("Using Halo Reach Tags")
        log_to_file("reach_tag_path: " + bpy.context.preferences.addons[__name__].preferences.reach_tag_path)
        Tag_Root = bpy.context.preferences.addons[__name__].preferences.reach_tag_path
    else:
        log_to_file("Error with Tag option property")
    
    
    #MUST SPECIFY THE ROOT FOLDER OF YOUR MODELS YOU RIPPED (FROM DRIVE LETTER -> BASE FOLDER WHERE YOU EXPORT YOUR MODELS, TEXTURES, AND .BLEND FILES)
    Export_Root = bpy.context.preferences.addons[__name__].preferences.export_path
    #Export_Root = "C:/Users/jeffr/Downloads/H3 Material Tool/Test Objects"
    
      
    DEFAULT_BITMAP_DIR = "shaders/default_bitmaps/bitmaps/"
    IMAGE_EXTENSION = bpy.context.scene.image_format_dropdown
    log_to_file(IMAGE_EXTENSION)
    Preferred_Blend = 'BLEND'    #Either 'BLEND' or 'HASHED'

    #################################
    #NODE GRAPH CUSTOMIZING VARIABLES
    #################################

    #end group node placement
    ALPHA_BLEND_HORIZONTAL_SPACING = 250
    ALPHA_TEST_HORIZONTAL_SPACING = 250
    ADDITIVE_GROUP_HORIZONTAL_SPACING = 250
    ADD_SHADER_HORIZONTAL_SPACING = 250

    #main group node placement
    ENVIRONMENT_GROUP_VERTICAL_SPACING = 250
    SELF_ILLUM_VERTICAL_SPACING = 250

    #texture group node placement
    TEXTURE_NODE_VERTICAL_PLACEMENT = 550              # vertical placement of the entire texture node groups
    TEXTURE_NODE_HORIZONTAL_PLACEMENT = 600            # horizontal placment of the entire texture node groups
    TEXTURE_GROUP_VERTICAL_SPACING = 120               # vertical spacing in-between each texture segment
    TEXTURE_MAPPING_HORIZONTAL_SPACING = 200           # horizontal spacing between the mapping node and the texture nodes
    ADDITIONAL_MIRROR_NODE_VERTICAL_SPACING = 100      # adds extra padding between each texture cluster when a mirror node is present
    TEXTURE_MIRROR_NODE_HORIZONTAL_SPACING = 200       # horizontal spacing between the mirror group and texture node
    TEXTURE_COORD_NODE_HORIZONTAL_SPACING = 200        # horizontal spacing between tex coordinate node and mapping node
    TEXTURE_NODE_W_GAMMA_HORIZONTAL_SPACING = 50       # horizontal placement of texture node when it has gamma
    TEXTURE_GAMMA_HORIZONTAL_PLACEMENT = 100           # horizontal placement of the gamma nodes



    #DEBUG VALUES
    debug_textures_values_found = 1              # show debug info for found/unfound texture types and values




    #some global variables
    DefaultNeeded = 0
    ShadersConnected = 0
    ShaderOutputCount = 0
    ShaderGroupList = []


    color_white_rgb = [1.00, 1.00, 1.00, 1.00]
    color_gray_rgb = [0.5, 0.5, 0.5, 1.00]
    color_black_rgb = [0.00, 0.00, 0.00, 1.00]

    class wrap_mode:
        option = 0
        bitmap_type = ""


    class function:
        tsgt_offset = 0x0
        option = 0 #function option
        range_toggle = False #off or on
        # periodic_option1 = 0
        # periodic_option2 = 0
        # transition_option1 = 0
        # transition_option2 = 0
        function_name = ""
        range_name = ""
        
        #main values
        time_period = 0.00
        main_min_value = 0.00
        main_max_value = 0.00
        
        #main values
        left_function_option = 0
        left_frequency_value = 0.00
        left_phase_value = 0.00
        left_min_value = 0.00
        left_max_value = 0.00
        left_exponent_value = 0.00
        
        #used when range is toggled on
        right_function_option = 0
        right_frequency_value = 0.00
        right_phase_value = 0.00
        right_min_value = 0.00
        right_max_value = 0.00
        right_exponent_value = 0.00
        
        #used when it is a color function
        color_option = 0  #the option used for the function
        color_1 = [0.00, 0.00, 0.00, 0.00]
        color_2 = [0.00, 0.00, 0.00, 0.00]
        color_3 = [0.00, 0.00, 0.00, 0.00]
        color_4 = [0.00, 0.00, 0.00, 0.00]
        

    class bitmap:
        name = ""
        directory = ""
        curve_option = 0
        width = 0
        height = 0
        type = ""
        has_scale_x = False
        has_scale_y = False
        has_scale_uniform = False
        has_translation_x = False
        has_translation_y = False
        translation_xy = [0.00, 0.00]
        scale_xy = [1.00, 1.00]
        scale_uniform = 1.00 #gets overritten by xy
        transform_type_list = []
        transform_list = []
        disabled = False
        wrap_option = 0  #3 - mirror uni   4 or 5 - mirror X    9 - mirrorY   13 - both XY
        wrap_option_type = 0 #0 - wrap  1 - clamp   2 - mirror   3 - black_border
        equi_paths = []

    class shader:
        name = ""
        directory = ""
        bitmap_count = 0
        
        #category options
        albedo_option = 0
        bump_mapping_option = 0
        alpha_test_option = 0
        specular_mask_option = 0
        material_model_option = 0
        environment_mapping_option = 0
        self_illumination_option = 0
        blend_mode_option = 0
        parallax_option = 0
        misc_option = 0
        
        #alpha used by type - dictated by alpha_test
        type_w_alpha = ""
        alpha_bitmap_dir = ""
        
        #scaling/colors/values
        albedo_blend = 0.00
        albedo_color = color_white_rgb #BGR 3 decimal values
        albedo_color_alpha = 1.00 #1 decimal
        albedo_color2 = color_white_rgb #BGR 3 decimal values
        albedo_color2_alpha = 1.00 #1 decimal
        albedo_color3 = color_white_rgb #BGR 3 decimal values
        albedo_color3_alpha = 1.00 #1 decimal
        bump_detail_coefficient = 1.00 #1 decimal
        env_tint_color = color_white_rgb #BGR 3 decimal values
        env_roughness_scale = 1.00
        self_illum_color = color_white_rgb #BGR 3 decimal values
        self_illum_intensity = 1.00                                 
        channel_a = color_white_rgb #BGR 3 decimal
        channel_a_alpha = 0.00
        channel_b = color_white_rgb #BGR 3 decimal
        channel_b_alpha = 0.00
        channel_c = color_white_rgb #BGR 3 decimal
        channel_c_alpha = 0.00
        color_medium = color_white_rgb #BGR 3 decimal
        color_medium_alpha = 0.00
        color_wide = color_white_rgb #BGR 3 decimal
        color_wide_alpha = 0.0
        color_sharp = color_white_rgb #BGR 3 decimal
        color_sharp_alpha = 0.00
        thinness_medium = 0.00
        thinness_wide = 0.00
        thinness_sharp = 0.00
        meter_color_on = color_white_rgb #BGR 3 decimal
        meter_color_off = color_white_rgb #BGR 3 decimal
        meter_value = 0.00
        primary_change_color_blend = 0.00
        height_scale = 0.00
        diffuse_coefficient = 1.00                                          #Organism shader has default at 0.00
        specular_coefficient = 0.00
        specular_tint = color_white_rgb #BGR 3 decimal
        specular_power = 10.00
        fresnel_color = color_gray_rgb #BGR 3 decimal
        roughness = 0.40
        environment_map_specular_contribution = 0.00
        use_material_texture = 0.00 #0 to 1   False or True
        uses_detail_map2 = 0 #0 to 1   False or True
        normal_specular_power = 10.00
        normal_specular_tint = color_white_rgb #BGR 3 decimal
        glancing_specular_power = 10.00
        glancing_specular_tint = color_white_rgb #BGR 3 decimal
        fresnel_curve_steepness = 5.00
        albedo_specular_tint_blend = 0.00
        fresnel_curve_bias = 0.00
        fresnel_coefficient = 0.1
        area_specular_contribution = .50
        analytical_specular_contribution = 0.00
        neutral_gray = color_white_rgb #BGR 3 decimal
        
        diffuse_tint = color_white_rgb #BGR 3 decimal
        analytical_specular_coefficient = 0.00
        area_specular_coefficient = 0.00
        environment_map_tint = color_white_rgb #BGR 3 decimal
        rim_tint = color_black_rgb  #BGR 3 decimal
        ambient_tint = color_white_rgb #BGR 3 decimal
        environment_map_coefficient = 0.00
        rim_coefficient = 1.00
        rim_power = 2.00
        rim_start = 0.70
        rim_maps_transition_ratio = 0.00
        ambient_coefficient = 0.00
        subsurface_coefficient = 0.00
        subsurface_tint = color_white_rgb #BGR 3 decimal
        subsurface_propagation_bias = 0.00
        subsurface_normal_detail = 0.00
        transparence_normal_bias = 0.00
        transparence_tint = color_white_rgb #BGR 3 decimal
        transparence_normal_detail = 0.00
        final_tint = color_white_rgb #BGR 3 decimal
        
        
        
        #terrain stuff
          #categories  start 20 bytes after shaders/shaders in terrain_shader file
        blending_option = 0
        environment_mapping_option = 0
        material_0_option = 0
        material_1_option = 0
        material_2_option = 0
        material_3_option = 0
        
        #textures
        # blend_map
        
        # base_map_m_0
        # detail_map_m_0
        # bump_map_m_0
        # detail_bump_m_0
        
        # base_map_m_1
        # detail_map_m_1
        # bump_map_m_1
        # detail_bump_m_1
        
        # base_map_m_2
        # detail_map_m_2
        # bump_map_m_2
        # detail_bump_m_2   
        
        # base_map_m_3
        # detail_map_m_3
        # bump_map_m_3
        # detail_bump_m_3  
        
          #scaling/colors/values
        global_albedo_tint = 1.00
        
        diffuse_coefficient_m_0 = 1.00
        specular_coefficient_m_0 = 0.00
        specular_power_m_0 = 10.00
        specular_tint_m_0 = color_white_rgb
        fresnel_curve_steepness_m_0 = 5.00
        area_specular_contribution_m_0 = 0.50
        analytical_specular_contribution_m_0 = 0.50
        environment_specular_contribution_m_0 = 0.00
        self_illum_color_m_0 = color_white_rgb #BGR 3 decimal values
        self_illum_intensity_m_0 = 1.00
        albedo_specular_tint_blend_m_0 = 0.00
        
        diffuse_coefficient_m_1 = 1.00
        specular_coefficient_m_1 = 0.00
        specular_power_m_1 = 10.00
        specular_tint_m_1 = color_white_rgb
        fresnel_curve_steepness_m_1 = 5.00
        area_specular_contribution_m_1 = 0.50
        analytical_specular_contribution_m_1 = 0.50
        environment_specular_contribution_m_1 = 0.00
        self_illum_color_m_1 = color_white_rgb #BGR 3 decimal values
        self_illum_intensity_m_1 = 1.00
        albedo_specular_tint_blend_m_1 = 0.00
        
        diffuse_coefficient_m_2 = 1.00
        specular_coefficient_m_2 = 0.00
        specular_power_m_2 = 10.00
        specular_tint_m_2 = color_white_rgb
        fresnel_curve_steepness_m_2 = 5.00
        area_specular_contribution_m_2 = 0.50
        analytical_specular_contribution_m_2 = 0.50
        environment_specular_contribution_m_2 = 0.00
        self_illum_color_m_2 = color_white_rgb #BGR 3 decimal values
        self_illum_intensity_m_2 = 1.00
        albedo_specular_tint_blend_m_2 = 0.00
        
        diffuse_coefficient_m_3 = 1.00
        specular_coefficient_m_3 = 0.00
        specular_power_m_3 = 10.00
        specular_tint_m_3 = color_white_rgb
        fresnel_curve_steepness_m_3 = 5.00
        area_specular_contribution_m_3 = 0.50
        analytical_specular_contribution_m_3 = 0.50
        environment_specular_contribution_m_3 = 0.00
        self_illum_color_m_3 = color_white_rgb #BGR 3 decimal values
        self_illum_intensity_m_3 = 1.00
        albedo_specular_tint_blend_m_3 = 0.00 


        #halogram stuff
        warp_option = 0
        overlay_option = 0
        edge_fade_option = 0
        distortion_option = 0
        soft_fade_option = 0

        #used for default textures
        #texture reference offsets
        BaseMap_Offset = 0x0
        DetailMap_Offset = 0x0
        DetailMap2_Offset = 0x0
        DetailMap3_Offset = 0x0
        SpecularMaskTexture_Offset = 0x0
        ChangeColorMap_Offset = 0x0
        BumpMap_Offset = 0x0
        BumpDetailMap_Offset = 0x0
        EnvironmentMap_Offset = 0x0
        FlatEnvironmentMap_Offset = 0x0
        SelfIllumMap_Offset = 0x0
        SelfIllumDetailMap_Offset = 0x0
        
        #offset for Alpha_Test_Map
        AlphaTestMap_Offset = 0x0

        env_map_paths = []

        needed_bitmaps = []
        env_tint_color_offset_list = []
        bitmap_list = []      #list of bitmap class objects for each bitmap used by the shader
        function_list = []
        wrap_mode_list = []
        
        
        
    #some global variables
    ShaderList = []   #list of all shader information
    ShaderList_Index = 0
    Shader_Type = 0


    def Is_Bitmap_Disabled(ShaderItem, BitmapType):
        if (BitmapType == "base_map"): #if albedo option is off
            log_to_file("Albedo Option not disabling: base_map")
            return False
        elif (BitmapType == "detail_map"):
            if(ShaderItem.albedo_option == 2 or ShaderItem.albedo_option == 22 or ShaderItem.albedo_option == 18 or ShaderItem.albedo_option == 17): #if albedo option is off
                log_to_file("Albedo Option disabling: detail_map")
                return True
            else: 
                log_to_file("Albedo Option not disabling: detail_map")
                return False
        elif (BitmapType == "bump_map"):
            if (ShaderItem.bump_mapping_option == 0): #if bump map option is off
                log_to_file("Bump Mapping Option disabling: bump_map")
                return True
            else:
                log_to_file("Bump Mapping Option not disabling: bump_map")
                return False
        elif (BitmapType == "bump_detail_map"):
            if (ShaderItem.bump_mapping_option == 0 or ShaderItem.bump_mapping_option == 1): # if bump mapping option is off or set to standard
                log_to_file("Bump Mapping Option disabling: bump_detail_map")
                return True
            else:
                log_to_file("Bump Mapping Option not disabling: bump_detail_map not disabled")
                return False
        elif (BitmapType == "self_illum_map"):
            if (ShaderItem.self_illumination_option == 0): #if self_illum option is off
                log_to_file("Self Illum Option disabling: self_illum_map")
                return True
            else: #other options
                log_to_file("Self Illum Option not disabling: self_illum_map")
                return False
        elif (BitmapType == "self_illum_detail_map"):
            if (ShaderItem.self_illumination_option != 5 or ShaderItem.self_illumination_option != 10): #if self_illum option is not self_illum_detail or illum_detail_world_space_four_cc 
                log_to_file("Self Illum Option not disabling: self_illum_detail_map")
                return False
            else: #other options
                log_to_file("Self Illum Option disabling: self_illum_detail_map")
                return True
        elif (BitmapType == "environment_map"):
            if (ShaderItem.environment_mapping_option == 0): #if environment option is off
                log_to_file("Environment Option disabling: environment_map")
                return True
            else: #other options
                log_to_file("Environment Option not disabling: environment_map not disabled")
                return False
                
        #terrain shader stuff disabling     
        
        
        else:
            log_to_file("Different Bitmap type trying to be handled")
       

    def convert_to_hex(text):
        hex_representation = b'\x00' + bytes(text, 'utf-8') + b'\x66\x72\x67\x74'
        return hex_representation

    def get_ascii_string(file, offset, size):
        temp_string = ""
        SampleByte = ""
        ASCIIstring = []

        file.seek(offset)
        for pymat_copy in range(size):
            SampleByte = file.read(1).decode("UTF-8")
            ASCIIstring.append(SampleByte)
        
        ASCIIstring = ''.join(ASCIIstring)
        directory_string = ASCIIstring
        directory_string = directory_string
        #log_to_file("type: " + directory_string)
        return directory_string
       
    def get_before_type_offset(file, offset):
        directory_string = ""
        SampleByte = ""
        DirString = []

        file.seek(offset - 0x1)
        while not SampleByte == '\x00':   #while loop to run through the directory lists and build strings until it finds a null byte then saves it to an array
            SampleByte = file.read(1).decode("UTF-8")
            #log_to_file("SampleByte: " + SampleByte)
            if not SampleByte == '\x00':
                if SampleByte == '\\':
                    SampleByte = '/'
                file.seek(file.tell() - 0x2)
        
        return file.tell()


    #Get the directory from the .shader files and remove anything not needed
    def get_dir(file, offset):
        directory_string = ""
        SampleByte = ""
        DirString = []
        
        file.seek(offset)
        while not SampleByte == '\x00':   #while loop to run through the directory lists and build strings until it finds a null byte then saves it to an array
            SampleByte = file.read(1).decode("UTF-8")
            if not SampleByte == '\x00':
                if SampleByte == '\\':
                    SampleByte = '/'

                DirString.append(SampleByte)
        DirString = ''.join(DirString)
        directory_string = DirString
        directory_string = directory_string[:-4]
        return directory_string

    def has_value(file, offset):
        #has_function(file, offset)
        file.seek(offset + 0x2C) #skips 44 bytes from where it is told
        test_bytes = 0
        test_bytes = int.from_bytes(file.read(4), 'little')
        if (test_bytes == 1952936809): #if the next 4 bytes equal 'isgt' then there is no scaling or color values
            return False
        else:
            return True
            
    def median_rgba(FunctionIten):
        #mix colors to be half the rgb value
        temp_r = (FunctionItem.color_1[0] + FunctionItem.color_4[0]) / 2
        temp_g = (FunctionItem.color_1[1] + FunctionItem.color_4[1]) / 2
        temp_b = (FunctionItem.color_1[2] + FunctionItem.color_4[2]) / 2
        temp_a = (FunctionItem.color_1[3] + FunctionItem.color_4[3]) / 2
                        
        temp_rgba = []
        temp_rgba.append(temp_r)
        temp_rgba.append(temp_g)
        temp_rgba.append(temp_b)
        temp_rgba.append(temp_a)
        
        return temp_rgba
                        
                           
            
            
    def has_function(file, offset):
        file.seek(offset + 0x50) #skip 80 bytes from offset to where isgt might be
        test_isgt = 0
        test_empty = 0
        test_after_adgt = 0
        test_isgt = int.from_bytes(file.read(4), 'little')
        test_empty = int.from_bytes(file.read(8), 'little')
        
        #log_to_file("inside has_function()")
        #log_to_file("isgt: " + str(test_isgt))
        
        #seek to test area 8 bytes after adgt
        file.seek(test_find(file.tell(), file, "adgt") + 0x8)
        
        test_after_adgt = int.from_bytes(file.read(2), 'little') #if it is 32 then function doesn't exist
        #log_to_file(" test after adgt value: " + str(test_after_adgt))
        
        if (test_isgt == 1952936809): #if isgt is there
            #log_to_file("  passed isgt test")
            if(test_after_adgt != 32):  #removed (test_empty != 0)  from this
                #log_to_file("There is probably a function here!")
                return True
            else:
                #log_to_file("Probably no function here")
                return False

    #find and return offset of the beginning of an ASCII string
    def get_ASCII_offset(file, offset_start, ASCII): 
        ASCII_byte = bytes(ASCII, 'utf-8')
        file = open(ShaderPath, "rb")
        file_read = file.read()
        
        return file_read.find(ASCII_byte, offset_start)


    #builds function object and returns object
    def get_function_color(file, offset, function_object):
        log_to_file("")
        #ADD CODE HERE LATER

    #builds function object and return that object
    def get_function_data(file, offset, function_object):
        #clear function object
        function_object.tsgt_offset = 0x0
        function_object.option = 0
        function_object.range_toggle = False
        function_object.function_name = ""
        function_object.range_name = ""
        function_object.time_period = 0.00
        function_object.main_min_value = 0.00
        function_object.main_max_value = 0.00
        function_object.left_function_option = 0
        function_object.left_frequency_value = 0.00
        function_object.left_phase_value = 0.00
        function_object.left_min_value = 0.00
        function_object.left_max_value = 0.00
        function_object.left_exponent_value = 0.00
        function_object.right_function_option = 0
        function_object.right_frequency_value = 0.00
        function_object.right_phase_value = 0.00
        function_object.right_min_value = 0.00
        function_object.right_max_value = 0.00
        function_object.right_exponent_value = 0.00
        
        function_name_offset = 0x0 #offset of the start of the function name
        range_name_offset = 0x0 #offset of the start of the range name
        tsgt_offset = 0x0 #offset of right after the potential range name of the function
        range_name_length = 0
        
        #get time_period
        file.seek(offset + 0x2C) #skip 44 bytes to get time_period
        function_object.time_period = struct.unpack('f', file.read(4))[0] #grab the time_period
        
        #get function_name and offset
        file.seek(offset + 0x5C) #skip 92 bytes to get name of function
        function_name_offset = file.tell() #sets the range_name_offset
        function_object.function_name = get_dir(file, function_name_offset) #get name of function
        
        #get range_name_offset
        range_name_offset = file.seek(function_name_offset + len(function_object.function_name) + 0xC) #jump to end of function name and then 12 bytes
        
        #store tsgt_offset
        function_object.tsgt_offset = get_ASCII_offset(file, range_name_offset, "tsgt") #get offset of the start of 'tsgt' right after name of range
        
        #get name of range name
        range_name_length = function_object.tsgt_offset - range_name_offset #gets length of range name
        file.seek(range_name_offset) #seek to start of range name
        range_name_bytes = file.read(range_name_length)
        
        function_object.range_name = range_name_bytes.decode('UTF-8')
        
        #start at tsgt_offset + 24 bytes
        file.seek(function_object.tsgt_offset + 0x18)
        
        #grab function option
        function_object.option = int.from_bytes(file.read(1), 'little')
        
        temp_toggle = int.from_bytes(file.read(1), 'little')
        #grab range_toggle
        if (temp_toggle == 37): #toggle on
            function_object.range_toggle == True
        elif (temp_toggle == 36): #toggle off
            function_object.range_toggle == False
        else:
            log_to_file("Function toggle data issue")
            
        
        #jump to tsgt_offset + 28 bytes 
        file.seek(function_object.tsgt_offset + 0x1C)
        
        #grab both main min and max values
        function_object.main_min_value = struct.unpack('f', file.read(4))[0]
        function_object.main_max_value = struct.unpack('f', file.read(4))[0]

        #grab certain data depending on each option
        if(function_object.option != 1 and function_object.option != 8): #option = basic or curve
            if(function_object.option == 3): #option = periodic
                #jump to tsgt_offset + 56 bytes
                file.seek(function_object.tsgt_offset + 0x38) 
            
                #store left function option
                function_object.left_function_option = int.from_bytes(file.read(1), 'little')

                #jump to tsgt_offset + 60 bytes
                file.seek(function_object.tsgt_offset + 0x3C)
                
                #grab left values
                function_object.left_frequency_value = struct.unpack('f', file.read(4))[0]
                function_object.left_phase_value = struct.unpack('f', file.read(4))[0]
                function_object.left_min_value = struct.unpack('f', file.read(4))[0]
                function_object.left_max_value = struct.unpack('f', file.read(4))[0]
                
                #jump to tsgt_offset + 76 bytes
                file.seek(function_object.tsgt_offset + 0x4C)
                
                #grab Right values
                function_object.right_function_option = int.from_bytes(file.read(1), 'little')
                
                #jump to tsgt_offset + 80 bytes
                file.seek(function_object.tsgt_offset + 0x54)
                
                #grab right values
                function_object.right_frequency_value = struct.unpack('f', file.read(4))[0]
                function_object.right_phase_value = struct.unpack('f', file.read(4))[0]
                function_object.right_min_value = struct.unpack('f', file.read(4))[0]
                function_object.right_max_value = struct.unpack('f', file.read(4))[0]
         
                #repeat again for copy of all values?
                
            elif(function_object.option == 9): #option = exponent
                #jump to tsgt_offset + 56 bytes
                file.seek(function_object.tsgt_offset + 0x38)
                
                #grab left values
                function_object.left_min_value = struct.unpack('f', file.read(4))[0]
                function_object.left_max_value = struct.unpack('f', file.read(4))[0]
                function_object.left_exponent_value = struct.unpack('f', file.read(4))[0]
                
                #grab right values
                function_object.right_min_value = struct.unpack('f', file.read(4))[0]
                function_object.right_max_value = struct.unpack('f', file.read(4))[0]
                function_object.right_exponent_value = struct.unpack('f', file.read(4))[0]
                
                #repeat again for copy of all values?
                
            elif(function_object.option == 2): #option = transition
                
                #jump to tsgt_offset + 56 bytes
                file.seek(function_object.tsgt_offset + 0x38) 
            
                #store left function option
                function_object.left_function_option = int.from_bytes(file.read(1), 'little')

                #jump to tsgt_offset + 60 bytes
                file.seek(function_object.tsgt_offset + 0x3C)
                
                #grab left values
                function_object.left_min_value = struct.unpack('f', file.read(4))[0]
                function_object.left_max_value = struct.unpack('f', file.read(4))[0]
                
                #jump to tsgt_offset + 68 bytes
                file.seek(function_object.tsgt_offset + 0x44)
                
                #grab Right values
                function_object.right_function_option = int.from_bytes(file.read(1), 'little')
                
                #jump to tsgt_offset + 72 bytes
                file.seek(function_object.tsgt_offset + 0x48)
                
                #grab right values
                function_object.right_min_value = struct.unpack('f', file.read(4))[0]
                function_object.right_max_value = struct.unpack('f', file.read(4))[0]
         
                #repeat again for copy of all values?
                
            else:
                log_to_file("Function Option issue")
            
        return function_object


    #for color function data
    def get_color_function_data(file, offset, function_object):
        #clear function object
        function_object.tsgt_offset = 0x0
        function_object.option = 0
        function_object.range_toggle = False
        function_object.function_name = ""
        function_object.range_name = ""
        function_object.time_period = 0.00
        function_object.main_min_value = 0.00
        function_object.main_max_value = 0.00
        function_object.left_function_option = 0
        function_object.left_frequency_value = 0.00
        function_object.left_phase_value = 0.00
        function_object.left_min_value = 0.00
        function_object.left_max_value = 0.00
        function_object.left_exponent_value = 0.00
        function_object.right_function_option = 0
        function_object.right_frequency_value = 0.00
        function_object.right_phase_value = 0.00
        function_object.right_min_value = 0.00
        function_object.right_max_value = 0.00
        function_object.right_exponent_value = 0.00
        
        
        #add color rgb defaults
        function_object.color_option = 0
        function_object.color_1 = [0.00, 0.00, 0.00, 0.00]
        function_object.color_2 = [0.00, 0.00, 0.00, 0.00]
        function_object.color_3 = [0.00, 0.00, 0.00, 0.00]
        function_object.color_4 = [0.00, 0.00, 0.00, 0.00]
        
        #temp color values
        temp_color_R = 0.00
        temp_color_G = 0.00
        temp_color_B = 0.00
        
        function_name_offset = 0x0 #offset of the start of the function name
        range_name_offset = 0x0 #offset of the start of the range name
        tsgt_offset = 0x0 #offset of right after the potential range name of the function
        range_name_length = 0
        
        #get time_period
        file.seek(offset + 0x2C) #skip 44 bytes to get time_period
        function_object.time_period = struct.unpack('f', file.read(4))[0] #grab the time_period
        
        #get function_name and offset
        file.seek(offset + 0x5C) #skip 92 bytes to get name of function
        function_name_offset = file.tell() #sets the range_name_offset
        function_object.function_name = get_dir(file, function_name_offset) #get name of function
        
        #get range_name_offset
        range_name_offset = file.seek(function_name_offset + len(function_object.function_name) + 0xC) #jump to end of function name and then 12 bytes
        
        #store tsgt_offset
        function_object.tsgt_offset = get_ASCII_offset(file, range_name_offset, "tsgt") #get offset of the start of 'tsgt' right after name of range
        
        #get name of range name
        range_name_length = function_object.tsgt_offset - range_name_offset #gets length of range name
        file.seek(range_name_offset) #seek to start of range name
        range_name_bytes = file.read(range_name_length)
        
        function_object.range_name = range_name_bytes.decode('UTF-8')
        
        log_to_file("------Function Found-------")
        
        #start at tsgt_offset + 24 bytes
        file.seek(function_object.tsgt_offset + 0x18)
        
        #grab function option
        function_object.option = int.from_bytes(file.read(1), 'little')
        
        temp_toggle = int.from_bytes(file.read(1), 'little')
        #grab range_toggle
        if (temp_toggle == 37): #toggle on
            function_object.range_toggle == True
        elif (temp_toggle == 36): #toggle off
            function_object.range_toggle == False
        else:
            log_to_file("Function toggle data issue")
            
        #grab color function option
        function_object.color_option = int.from_bytes(file.read(1), 'little')  
        log_to_file("color_option: " + get_color_option(function_object.color_option))
        
        #jump to tsgt_offset + 28 bytes 
        file.seek(function_object.tsgt_offset + 0x1C)
        
        
        #grab color 1
        temp_color_B = float(int.from_bytes(file.read(1), 'little')) / 255
        temp_color_G = float(int.from_bytes(file.read(1), 'little')) / 255
        temp_color_R = float(int.from_bytes(file.read(1), 'little')) / 255
        file.seek(file.tell() + 0x1)
        
        #store color 1
        function_object.color_1.clear() #clear the list to empty it
        function_object.color_1.append(temp_color_R)
        function_object.color_1.append(temp_color_G)
        function_object.color_1.append(temp_color_B)
        function_object.color_1.append(1.00)
        log_to_file("color 1: " + str(function_object.color_1))
        
        
        #grab color 2
        temp_color_B = float(int.from_bytes(file.read(1), 'little')) / 255
        temp_color_G = float(int.from_bytes(file.read(1), 'little')) / 255
        temp_color_R = float(int.from_bytes(file.read(1), 'little')) / 255
        file.seek(file.tell() + 0x1)
        
        #store color 2
        function_object.color_2.clear() #clear the list to empty it
        function_object.color_2.append(temp_color_R)
        function_object.color_2.append(temp_color_G)
        function_object.color_2.append(temp_color_B)
        function_object.color_2.append(1.00)
        log_to_file("color 2: " + str(function_object.color_2))
        
        
        #grab color 3
        temp_color_B = float(int.from_bytes(file.read(1), 'little')) / 255
        temp_color_G = float(int.from_bytes(file.read(1), 'little')) / 255
        temp_color_R = float(int.from_bytes(file.read(1), 'little')) / 255
        file.seek(file.tell() + 0x1)
        
        #store color 3
        function_object.color_3.clear() #clear the list to empty it
        function_object.color_3.append(temp_color_R)
        function_object.color_3.append(temp_color_G)
        function_object.color_3.append(temp_color_B)
        function_object.color_3.append(1.00)
        log_to_file("color 3: " + str(function_object.color_3))

        #grab color 4
        temp_color_B = float(int.from_bytes(file.read(1), 'little')) / 255
        temp_color_G = float(int.from_bytes(file.read(1), 'little')) / 255
        temp_color_R = float(int.from_bytes(file.read(1), 'little')) / 255
        file.seek(file.tell() + 0x1)
        
        #store color 4
        function_object.color_4.clear() #clear the list to empty it
        function_object.color_4.append(temp_color_R)
        function_object.color_4.append(temp_color_G)
        function_object.color_4.append(temp_color_B)
        function_object.color_4.append(1.00)
        log_to_file("color 4: " + str(function_object.color_4))
      
        
        #grab certain data depending on each option
        if(function_object.option != 1 and function_object.option != 8): #option = basic or curve
            if(function_object.option == 3): #option = periodic
                #jump to tsgt_offset + 56 bytes
                file.seek(function_object.tsgt_offset + 0x38) 
            
                #store left function option
                function_object.left_function_option = int.from_bytes(file.read(1), 'little')

                #jump to tsgt_offset + 60 bytes
                file.seek(function_object.tsgt_offset + 0x3C)
                
                #grab left values
                function_object.left_frequency_value = struct.unpack('f', file.read(4))[0]
                function_object.left_phase_value = struct.unpack('f', file.read(4))[0]
                function_object.left_min_value = struct.unpack('f', file.read(4))[0]
                function_object.left_max_value = struct.unpack('f', file.read(4))[0]
                
                #jump to tsgt_offset + 76 bytes
                file.seek(function_object.tsgt_offset + 0x4C)
                
                #grab Right values
                function_object.right_function_option = int.from_bytes(file.read(1), 'little')
                
                #jump to tsgt_offset + 80 bytes
                file.seek(function_object.tsgt_offset + 0x54)
                
                #grab right values
                function_object.right_frequency_value = struct.unpack('f', file.read(4))[0]
                function_object.right_phase_value = struct.unpack('f', file.read(4))[0]
                function_object.right_min_value = struct.unpack('f', file.read(4))[0]
                function_object.right_max_value = struct.unpack('f', file.read(4))[0]
         
                #repeat again for copy of all values?
                
            elif(function_object.option == 9): #option = exponent
                #jump to tsgt_offset + 56 bytes
                file.seek(function_object.tsgt_offset + 0x38)
                
                #grab left values
                function_object.left_min_value = struct.unpack('f', file.read(4))[0]
                function_object.left_max_value = struct.unpack('f', file.read(4))[0]
                function_object.left_exponent_value = struct.unpack('f', file.read(4))[0]
                
                #grab right values
                function_object.right_min_value = struct.unpack('f', file.read(4))[0]
                function_object.right_max_value = struct.unpack('f', file.read(4))[0]
                function_object.right_exponent_value = struct.unpack('f', file.read(4))[0]
                
                #repeat again for copy of all values?
                
            elif(function_object.option == 2): #option = transition
                
                #jump to tsgt_offset + 56 bytes
                file.seek(function_object.tsgt_offset + 0x38) 
            
                #store left function option
                function_object.left_function_option = int.from_bytes(file.read(1), 'little')

                #jump to tsgt_offset + 60 bytes
                file.seek(function_object.tsgt_offset + 0x3C)
                
                #grab left values
                function_object.left_min_value = struct.unpack('f', file.read(4))[0]
                function_object.left_max_value = struct.unpack('f', file.read(4))[0]
                
                #jump to tsgt_offset + 68 bytes
                file.seek(function_object.tsgt_offset + 0x44)
                
                #grab Right values
                function_object.right_function_option = int.from_bytes(file.read(1), 'little')
                
                #jump to tsgt_offset + 72 bytes
                file.seek(function_object.tsgt_offset + 0x48)
                
                #grab right values
                function_object.right_min_value = struct.unpack('f', file.read(4))[0]
                function_object.right_max_value = struct.unpack('f', file.read(4))[0]
         
                #repeat again for copy of all values?
                
            else:
                log_to_file("Function Option issue")
            
        return function_object






    def print_function(function_object):
        log_to_file("----Function----")
        log_to_file("  Name: " + function_object.function_name)
        log_to_file("  Type: " + get_function_option(function_object.option))
        if(function_object.range_toggle == True):
            log_to_file("  Range Toggle: On")
            log_to_file("  Range Name: " + function_object.range_name)
        else:
            log_to_file("  Range Toggle: Off")
        log_to_file("  Time Period: " + str(function_object.time_period) + " seconds")
        log_to_file("  Main Min: " + str(function_object.main_min_value))    
        log_to_file("  Main Max: " + str(function_object.main_max_value))
        
        if(function_object.option == 3): #option = periodic
            log_to_file("  Left Function Option: " + get_periodic_option(function_object.left_function_option))
            log_to_file("  Left Frequency: " + str(function_object.left_frequency_value))
            log_to_file("  Left Phase: " + str(function_object.left_phase_value))    
            log_to_file("  Left Min: " + str(function_object.left_min_value))
            log_to_file("  Left Max: " + str(function_object.left_max_value))
            
            if(function_object.range_toggle == True):
                log_to_file("  Right Function Option: " + get_periodic_option(function_object.right_function_option))
                log_to_file("  Right Frequency: " + str(function_object.right_frequency_value))
                log_to_file("  Right Phase: " + str(function_object.right_phase_value))    
                log_to_file("  Right Min: " + str(function_object.right_min_value))
                log_to_file("  Right Max: " + str(function_object.right_max_value))
        
        if(function_object.option == 9): #option = exponent  
            log_to_file("  Left Min: " + str(function_object.left_min_value))
            log_to_file("  Left Max: " + str(function_object.left_max_value))
            log_to_file("  Left Exponent: " + str(function_object.left_exponent_value))
        
            if(function_object.range_toggle == True):   
                log_to_file("  Right Min: " + str(function_object.right_min_value))
                log_to_file("  Right Max: " + str(function_object.right_max_value))
                log_to_file("  Right Max: " + str(function_object.right_exponent_value))
        
        if(function_object.option == 2): #option = transition
            log_to_file("  Left Function Option: " + get_periodic_option(function_object.left_function_option))  
            log_to_file("  Left Min: " + str(function_object.left_min_value))
            log_to_file("  Left Max: " + str(function_object.left_max_value))
        
            if(function_object.range_toggle == True):
                log_to_file("  Right Function Option: " + get_periodic_option(function_object.right_function_option))   
                log_to_file("  Right Min: " + str(function_object.right_min_value))
                log_to_file("  Right Max: " + str(function_object.right_max_value))
    
    def get_bitmap_resolution(directory, choice):
        width = 0
        height = 0
        
        #open bitmap file in raw binary
        try:    
            bitmapfile = open(directory, "rb")
        except:
            curve_option = 6
            log_to_file("Resolution Error")
            return 6
       
        bitmap = bitmapfile.read()
        Res_Offset_Difference = 0x30
        Res_Offset = 0x0            
            
        #find pattern and save it to variable
        try: 
            Resolution_Offset = bitmap.index(b'\x00\x00\x00\x00\x61\x64\x67\x74\x00\x00\x00\x00\x00\x00\x00\x00\x6C\x62\x67\x74')
        except ValueError:
            log_to_file("Bitmap Curve Options not found!")

        if (Resolution_Offset != 0):
            Res_Offset = Resolution_Offset - Res_Offset_Difference
            
            bitmapfile.seek(Res_Offset)
            
            width = int.from_bytes(bitmapfile.read(2), 'little')
            height = int.from_bytes(bitmapfile.read(2), 'little')
            
            #log_to_file("curve_option: " + str(curve_option))
            bitmapfile.close()
            
            log_to_file("Texture Width: " + str(width))
            log_to_file("Texture Height: " + str(height))
        else:
            log_to_file("Resolution Offset Not Found!")
            
        if (choice == "width"):
            return width
        elif (choice == "height"):
            return height
        else: 
            "Error setting Resolution"
            return 0  
        
    def process_directory(integer, directory):
        hardcoded_directory = "C:/Users/jeffr/Documents/CR4B Tool GitHub/CR4B_Tool_v5/"
        
        if integer == 0:
            # Join the hardcoded directory with the filename to get the complete path
            file_path = os.path.join(hardcoded_directory, 'UnknownCurves.txt')
            
            # Check if the directory path is already present in the file
            with open(file_path, 'a+') as file:
                file.seek(0)  # Move the cursor to the start of the file
                lines = file.readlines()
                # If the directory path is not in the file, append it
                if directory + '\n' not in lines:
                    file.write(directory + '\n')   
        
        
    def get_bitmap_curve (directory):
        curve_option = 0 
        
        #open bitmap file in raw binary
        try:    
            #log_to_file("Trying to open: " + directory)
            bitmapfile = open(directory, "rb")
        except:
            curve_option = 6
            log_to_file("Failed to read bitmap file color curve data")
            #process_directory(curve_option, directory)
            return 6
          
        #if tags selected are for Halo 3 / ODST
        if(bpy.context.scene.tag_dropdown == "Halo 3" or bpy.context.scene.tag_dropdown == "Halo 3: ODST"):    
            bitmap = bitmapfile.read()
            Curve_Offset_Difference = 0x1F
            Curve_Offset = 0x0


            #find pattern and save it to variable
            try: 
                CurveOptions_Offset = bitmap.index(b'\x00\x00\x00\x00\x61\x64\x67\x74\x00\x00\x00\x00\x00\x00\x00\x00\x6C\x62\x67\x74')
            except ValueError:
                log_to_file("Bitmap Curve Options not found!")

            if (CurveOptions_Offset != 0):
                Curve_Offset = CurveOptions_Offset - Curve_Offset_Difference
                
                bitmapfile.seek(Curve_Offset)
                
                curve_option = int.from_bytes(bitmapfile.read(1), 'little')
                
                #log_to_file("curve_option: " + str(curve_option))
                bitmapfile.close()
                
                log_to_file("Curve: " + get_bitmap_curve_option(curve_option))
                #process_directory(curve_option, directory)
            else:
                log_to_file("Curve Options Pre Offset Not Found!")
            return curve_option
        
        
        #if tags selected is for Reach
        elif (bpy.context.scene.tag_dropdown == "Halo Reach"):
            bitmap = bitmapfile.read()
            Curve_Offset_Difference = 0x23
            Curve_Offset = 0x0


            #find pattern and save it to variable
            try: 
                CurveOptions_Offset = bitmap.index(b'\x00\x00\x00\x00\x61\x64\x67\x74\x00\x00\x00\x00\x00\x00\x00\x00\x6C\x62\x67\x74')
            except ValueError:
                log_to_file("Bitmap Curve Options not found!")

            if (CurveOptions_Offset != 0):
                Curve_Offset = CurveOptions_Offset - Curve_Offset_Difference
                
                bitmapfile.seek(Curve_Offset)
                
                curve_option = int.from_bytes(bitmapfile.read(1), 'little')
                
                #log_to_file("curve_option: " + str(curve_option))
                bitmapfile.close()
                
                log_to_file("Curve: " + get_bitmap_curve_option(curve_option))
                #process_directory(curve_option, directory)
            else:
                log_to_file("Curve Options Pre Offset Not Found!")
            return curve_option

    def shift_mirror_wrap(Mirror_Group):
        Mirror_Group.inputs.get("Location").default_value = [0, 3, 0]
        
        return Mirror_Group

    def test_find(offset, shaderfile, type):
        type_byte_pattern = bytes(type, 'utf-8')
        shaderfile = open(ShaderPath, "rb")
        shaderfile_read = shaderfile.read()
        
        offset2 = shaderfile_read.find(type_byte_pattern, offset + len(type))
        #log_to_file("offset 1: " + str(offset))
        #log_to_file("offset 2: " + str(offset2))
        return offset2
        
        
    def make_gamma(node_tree, teximage_node, texture_type, gamma_value):
        if(texture_type == "base_map"):
            #create Gamma Node
            GammaNode_Base = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
            GammaNode_Base.inputs.get("Gamma").default_value = gamma_value

            #link Gamma Node
            pymat_copy.node_tree.links.new(GammaNode_Base.inputs["Color"], teximage_node.outputs["Color"])
        
        elif(texture_type == "detail_map"):
            #create Gamma Node
            GammaNode_Detail = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
            GammaNode_Detail.inputs.get("Gamma").default_value = gamma_value

            #link Gamma Node
            pymat_copy.node_tree.links.new(GammaNode_Detail.inputs["Color"], teximage_node.outputs["Color"])
        
        elif(texture_type == "bump_map"):
            #create Gamma Node
            GammaNode_Bump = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
            GammaNode_Bump.inputs.get("Gamma").default_value = gamma_value

            #link Gamma Node
            pymat_copy.node_tree.links.new(GammaNode_Bump.inputs["Color"], teximage_node.outputs["Color"])
        
        elif(texture_type == "bump_detail_map"):
            #create Gamma Node
            GammaNode_BumpDetail = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
            GammaNode_BumpDetail.inputs.get("Gamma").default_value = gamma_value

            #link Gamma Node
            pymat_copy.node_tree.links.new(GammaNode_BumpDetail.inputs["Color"], teximage_node.outputs["Color"])

        elif(texture_type == "self_illum_map"):
            #create Gamma Node
            GammaNode_SelfIllum = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
            GammaNode_SelfIllum.inputs.get("Gamma").default_value = gamma_value

            #link Gamma Node
            pymat_copy.node_tree.links.new(GammaNode_SelfIllum.inputs["Color"], teximage_node.outputs["Color"])

        elif(texture_type == "self_illum_detail_map"):
            #create Gamma Node
            GammaNode_SelfIllumDetail = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
            GammaNode_SelfIllumDetail.inputs.get("Gamma").default_value = gamma_value

            #link Gamma Node
            pymat_copy.node_tree.links.new(GammaNode_SelfIllumDetail.inputs["Color"], teximage_node.outputs["Color"])
        else:
            log_to_file("Unhandled texture type trying to be assinged a Gamma Node")
            
            
            
            
        # stop = 0
        # count = 0
        # offset = 0x0
        # offset_list = []
        # while stop != 1:
            # if (file.find(type_in_bytes, offset) != -1):
                # offset_list.append(file.find(type_byte_pattern, offset))
                # offset = offset_list[count] + len(type)
                
                # count = count + 1
            # else:
                # stop = 1
        # log_to_file("offset count: " + str(count))
        # log_to_file("offset list: " + offset_list)
        
        
        
        

    # def get_offset_list(file, ShaderItem, type)
        # type_byte_pattern = bytes(type, 'utf-8')
        # fileSizeBytes = os.path.getsize(file)
        
        # s = ConstBitStream(filename=file)
        
        
    # def parse(register_name,byte_data):
        # fileSizeBytes = os.path.getsize(file)
        # fileSizeMegaBytes = GetFileSize(os.path.getsize(bin_file))
        # data = open(bin_file, 'rb')

        # s = ConstBitStream(filename=bin_file)
        # occurances = s.findall(byte_data, bytealigned=True)
        # occurances = list(occurances)
        # totalOccurances = len(occurances)
        # byteOffset = 0                                                      # True start of Byte string 

        # for pymat_copy in range(0, len(occurances)):
            # occuranceOffset = (hex(int(occurances[pymat_copy]/8)))
            # s0f0, length, bitdepth, height, width = s.readlist('hex:16, uint:16, uint:8, 2*uint:16')  
            # s.bitpos = occurances[pymat_copy]
            # data = s.read('hex:32')      
            # log_to_file('Address: ' + str(occuranceOffset) + ' Data: ' + str(data))
            # csvWriter.writerow([register_name, str(occuranceOffset), str(data)])

        
    #DEPRECATED FOR ANOTHER TIME IF NEEDED
    # def has_scale(file, offset, directory_len):
        # scale_check_offset = 0x14
        # scale_check = 0

        # #seek to end of dir
        # dir_offset = file.seek(offset + directory_len) 
        
        # file.seek(file.tell() + scale_check_offset)
        
        # scale_check = int.from_bytes(file.read(1),'little')
        
        # if (scale_check == 2 or scale_check == 3 or scale_check == 4):
            # return True
        # else:
            # return False

    # def get_scale (file, offset, directory_len, scale_type): #scale type 0 = uniform  1 = X   2 = Y
        # scale_check_offset1 = 0x14 #check for 1st spot
        # scale_check_offset2 = 0x38 #check for 2nd spot
        # scale_check_offset3 = 0x5C #check for 3rd spot
        # scale_check1 = 1 
        # scale_check2 = 1
        # scale_check3 = 1
        
        # #seek to end of dir
        # dir_offset = file.seek(offset + directory_len)
        
        # #save temp value for scale check 1
        # file.seek(dir_offset + scale_check_offset1)
        # scale_check1 = int.from_bytes(file.read(1), 'little')
        # log_to_file("scale check1: " + str(scale_check1))
        
        # #save temp value for scale check 2
        # file.seek(dir_offset + scale_check_offset2)
        # scale_check2 = int.from_bytes(file.read(1), 'little')
        # log_to_file("scale check2: " + str(scale_check2))

        # #save temp value for scale check 3
        # file.seek(dir_offset + scale_check_offset3)
        # scale_check3 = int.from_bytes(file.read(1), 'little')
        # log_to_file("scale check3: " + str(scale_check3))    

        # #search for uniform value  when scale_type = 0
        # if(scale_type == 0):
            # if(scale_check1 == 2 or scale_check2 == 2 or scale_check3 == 2): #has uniform scale
                # if(scale_check1 == 2):
                    
                # elif(scale_check2 == 2):
                    
                # elif(scale_check3) == 2):
                    
            # else: #no uniform scaling data
                # return 1.00
        # #search for X value  when scale_type = 1

        
        # #search for Y value  when scale_type = 2


    def has_scale(file, offset, directory_len):
        tsgt = 1952936820 #tsgt in int values  
        no_scale_check_offset = 0x14 #saves 20 bytes ahead
        uniform_check_offset = 0x38 #saves 56 bytes ahead
        xy_scale_check_offset = 0x5C #saves 92 bytes ahead
        
        #seek to end of dir
        dir_offset = file.seek(offset + directory_len)  # + 0x2C) #seeks to offset which is at end of type and then 16 more bytes to get to start of directory for bitmap and skip number of bytes equal to characters in bitmap directory

        #save temp value for no_scale
        file.seek(dir_offset + no_scale_check_offset)
        no_scale_check = int.from_bytes(file.read(4), 'little')
        #log_to_file("no scale check: " + str(no_scale_check))
        
        #save temp value for uniform_scale
        file.seek(dir_offset + uniform_check_offset)
        uniform_scale_check = int.from_bytes(file.read(4), 'little')
        #log_to_file("uniform scale check: " + str(uniform_scale_check))
        
        #save temp value for xy_scale
        file.seek(dir_offset + xy_scale_check_offset)
        xy_scale_check = int.from_bytes(file.read(4), 'little')
        #log_to_file("xy scale check: " + str(xy_scale_check))
        
        #SEEK 20 bytes in from dir end
            #if it is 2 then it is uniform
            #if it is 3 then it is X
            #if it is 4 then it is Y
        
        #SEEK 56 bytes in from dir end
            #if it is 2 then it is uniform
            #if it is 3 then it is X
            #if it is 4 then it is Y
            
        #SEEK 92 bytes in from dir end
            #if it is 2 then it is uniform
            #if it is 3 then it is X
            #if it is 4 then it is Y
        
        if (no_scale_check == tsgt):
            #log_to_file("no scaling data returning 0")
            return 0
        elif (uniform_scale_check == tsgt):
            #log_to_file("Uniform Scale returning 1")
            return 1
        elif (xy_scale_check == tsgt):
            #log_to_file("XY Scale returning 2")
            return 2
        else: 
            #log_to_file("Scale data is fucked up bro")
            return 0

    #send in bitmap object with this to get all this data back
    def get_scale(file, offset, directory_len, bitmap_object):
        tsgt_byte_pattern = bytes("tsgt", 'utf-8')
        adgt_byte_pattern = bytes("adgt", 'utf-8')
        shaderfile = open(ShaderPath, "rb")
        shaderfile_read = shaderfile.read()
        tsgt_main_offset = 0x0
        tsgt_2_offset = 0x0
        isgt_1_offset = 0x0
        isgt_2_offset = 0x0
        adgt_offset = 0x0
        function_name_offset = 0x0
        range_name_offset = 0x0
        test_isgt = 0
        
        #clear data to be used in loops
        break_loop = 0
        test_bytes = 0
        transform_count = 0
        bitmap_object.transform_type_list = []
        bitmap_object.transform_value_list = []
        bitmap_object.function_list = [] #add on function object for each transform, even if empty
        function_object = function()
        function_object.tsgt_offset = 0x0
        function_object.option = 0
        function_object.range_toggle = False
        function_object.function_name = ""
        function_object.range_name = ""
        function_object.time_period = 0.00
        function_object.main_min_value = 0.00
        function_object.main_max_value = 0.00
        function_object.left_function_option = 0
        function_object.left_frequency_value = 0.00
        function_object.left_phase_value = 0.00
        function_object.left_min_value = 0.00
        function_object.left_max_value = 0.00
        function_object.left_exponent_value = 0.00
        function_object.right_function_option = 0
        function_object.right_frequency_value = 0.00
        function_object.right_phase_value = 0.00
        function_object.right_min_value = 0.00
        function_object.right_max_value = 0.00
        function_object.right_exponent_value = 0.00
        
        scaleuniform = 1.00
        scaleX = 1.00
        scaleY = 1.00
        transX = 0.00
        transY = 0.00
        
        
        
        #skip 20 bytes from dir end offset
        file.seek(offset + directory_len + 0x14)
        
        #loop to get all types of transforms present
        while (break_loop == 0):
            #save 4 bytes from current point to be tested
            test_bytes = int.from_bytes(file.read(4), 'little')
            
            #skip 32 bytes ahead
            file.seek(file.tell() + 0x20)
            
            if (test_bytes == 2):
                bitmap_object.transform_type_list.append("uniform")
                log_to_file("uniform scale found")
            elif (test_bytes == 3):
                bitmap_object.transform_type_list.append("scaleX")
                log_to_file("scale X found")
            elif (test_bytes == 4):
                bitmap_object.transform_type_list.append("scaleY")
                log_to_file("scale Y found")
            elif (test_bytes == 5):
                bitmap_object.transform_type_list.append("translateX")
                log_to_file("translation X found")
            elif (test_bytes == 6):
                bitmap_object.transform_type_list.append("translateY")
                log_to_file("translation Y found")
            else:
                #log_to_file("Error reaching transform type bytes")
                break_loop = 1
        #ends at beginning of 'tsgt'        
                
        #save size of array list as variable
        transform_count = len(bitmap_object.transform_type_list)     
        #log_to_file("transform count: " + str(transform_count))
        
        if(transform_count > 0):
            for j in range(transform_count):
            #clear function object
            #----FUNCTION BLOCK START---- basic and curve
            #check if next 4 bytes are tsgt
                #if not skip to offset of next tsgt
                test_tsgt = 0
                test_isgt = 0
                test_tsgt = int.from_bytes(file.read(4), 'little') #read 4 bytes ahead into into
                file.seek(file.tell() - 0x4) #go back 4
                #log_to_file("offset before: " + str(file.tell() - 36))
                if(test_tsgt != 1952936820): #if not equal to tsgt    
                    tsgt_main_offset = get_ASCII_offset(file, file.tell(), "tsgt") #jump to where tsgt starts in case there is a misalignment
                    #log_to_file("offset not at tsgt main")
                else:
                    tsgt_main_offset = file.tell() #save start of main 'tsgt'
                    #log_to_file("offset at tsgt main")
                    
                #log_to_file("tsgt main offset: " + str(tsgt_main_offset - 36))    
                function_name_offset = file.seek(tsgt_main_offset + 0x18) #skip 24 to right before Function Name
                
                #ADD FUNCTIONALITY FOR FUNCTION NAME AND RANGE NAME IF EVER NEEDED HERE
                
                
                # log_to_file("function name offset: " + str(function_name_offset - 36))
                # #test_isgt = int.from_bytes(file.read(4), 'little')  #test value to see if it is isgt  
                # #file.seek(file.tell() - 0x4)  
                # file.seek(function_name_offset)
                # log_to_file("current offset 2: " + str(file.tell() - 36))
                # log_to_file("test isgt: " + str(test_isgt))
                # if (int.from_bytes(file.read(4), 'little') != 1952936809): #if isgt doesn't exist
                    # log_to_file("offset not at isgt 2. function name may be present")
                    # function_name_offset = file.tell()
                    # function_object.function_name = get_dir(file, file.tell()) #save function name
                    # isgt_2_offset = file.tell() + len(function_object.function_name) #skip to end of function name
                # else:
                    # isgt_2_offset = file.tell() #if isgt exists then save this location
                    # log_to_file("offset at isgt 2. no function name")
                
                # log_to_file("isgt 2 offset: " + str(isgt_2_offset - 36))
                # file.seek(isgt_2_offset + 0xC) #jump 12 bytes from isgt 2 offset to start of range name
                # test_tsgt = int.from_bytes(file.read(4), 'little')  #test value to see if it is isgt  
                # file.seek(file.tell() - 0x4)  
                # log_to_file("current offset 3: " + str(file.tell() - 36))
                # log_to_file("test tsgt: " + str(test_tsgt))
                # if (test_tsgt != 1952936820): #if tsgt doesn't exists
                    # log_to_file("offset not at tsgt 2. range name may be present")
                    # range_name_offset = file.tell()
                    # function_object.range_name = get_dir(file, range_name_offset) #save function name
                    # function_object.range_name = (function_object.range_name)[:-1]
                    # tsgt_2_offset = file.tell() + len(function_object.range_name) #skip to end of function name
                # else:
                    # tsgt_2_offset = file.tell() #if isgt exists then save this location
                    # log_to_file("offset at tsgt 2. no range name ")
                    
                #log_to_file("tsgt 2 offset: " + str(tsgt_2_offset - 36))    
                
                #get the offset of 'adgt'
                adgt_offset = get_ASCII_offset(file, tsgt_main_offset, "adgt")
                #log_to_file("adgt offset: " + str(adgt_offset - 36))
                
                #seek from before 'adgt' + 12 bytes
                file.seek(adgt_offset + 0xC)
                
                #grab the function option
                function_object.option = int.from_bytes(file.read(1), 'little')
                
                #grab the range toggle
                function_object.range_toggle = int.from_bytes(file.read(1), 'little')
                
                #skip 2 bytes
                file.seek(file.tell() + 0x2)
                
                #grab main Min and main Max values
                function_object.main_min_value = struct.unpack('f', file.read(4))[0]
                #log_to_file("main min value 1: " + str(function_object.main_min_value))
                function_object.main_max_value = struct.unpack('f', file.read(4))[0]
                #log_to_file("main max value 1: " + str(function_object.main_max_value))
                
                #skip 20 bytes ahead to either end of block OR rest of data
                file.seek(file.tell() + 0x14)
                
                
                # 'tsgt'
                # 8 bytes
                # 'isgt'
                # 8 bytes
                # FUNCTION NAME GOES HERE
                
                # 'isgt'
                # 8 bytes
                
                # RANGE NAME GOES HERE
                
                # 'tsgt'
                # 8 bytes
                
                # 'adgt'
                # 8 bytes
                # type of function [1 byte int]
                # range toggle [1 byte int]
                # 2 bytes
                # Main Min value [4 byte float]
                # Main Max value [4 byte float]
                
                # 20 bytes
                #---Possible end or continuation of function--- exponent, periodic, transitional
                if(function_object.option == 3): #option = periodic    
                    log_to_file("periodic function")
                    #store left function option
                    function_object.left_function_option = int.from_bytes(file.read(1), 'little')

                    #jump 3 bytes
                    file.seek(file.tell() + 0x3)
                    
                    #grab left values
                    function_object.left_frequency_value = struct.unpack('f', file.read(4))[0]
                    function_object.left_phase_value = struct.unpack('f', file.read(4))[0]
                    function_object.left_min_value = struct.unpack('f', file.read(4))[0]
                    function_object.left_max_value = struct.unpack('f', file.read(4))[0]
                    
                    #grab Right values
                    function_object.right_function_option = int.from_bytes(file.read(1), 'little')
                    
                    #jump 3 bytes
                    file.seek(file.tell() + 0x3)
                    
                    #grab right values
                    function_object.right_frequency_value = struct.unpack('f', file.read(4))[0]
                    function_object.right_phase_value = struct.unpack('f', file.read(4))[0]
                    function_object.right_min_value = struct.unpack('f', file.read(4))[0]
                    function_object.right_max_value = struct.unpack('f', file.read(4))[0]
             
                    #repeat again for copy of all values?
                    bitmap_object.function_list.append(function_object)
                
                elif(function_object.option == 9): #option = exponent
                    log_to_file("exponent function")
                    #jump to start of values
                    
                    #grab left values
                    function_object.left_min_value = struct.unpack('f', file.read(4))[0]
                    function_object.left_max_value = struct.unpack('f', file.read(4))[0]
                    function_object.left_exponent_value = struct.unpack('f', file.read(4))[0]
                    
                    #grab right values
                    function_object.right_min_value = struct.unpack('f', file.read(4))[0]
                    function_object.right_max_value = struct.unpack('f', file.read(4))[0]
                    function_object.right_exponent_value = struct.unpack('f', file.read(4))[0]
                    
                    #repeat again for copy of all values?
                    bitmap_object.function_list.append(function_object)
                        
                elif(function_object.option == 2): #option = transition
                    log_to_file("transition function")
                    #jump to start of data if need be
                
                    #store left function option
                    function_object.left_function_option = int.from_bytes(file.read(1), 'little')

                    #jump 3 bytes
                    file.seek(file.tell() + 0x3)
                    
                    #grab left values
                    function_object.left_min_value = struct.unpack('f', file.read(4))[0]
                    function_object.left_max_value = struct.unpack('f', file.read(4))[0]
                    
                    #jump to data
                    
                    #grab Right values
                    function_object.right_function_option = int.from_bytes(file.read(1), 'little')
                    
                    #jump 3 bytes
                    file.seek(file.tell() + 0x3)
                    
                    #grab right values
                    function_object.right_min_value = struct.unpack('f', file.read(4))[0]
                    function_object.right_max_value = struct.unpack('f', file.read(4))[0]
             
                    #repeat again for copy of all values?
                    bitmap_object.function_list.append(function_object)
                else:
                    log_to_file("basic or curve function")
                    #if function option is either curve or basic then save function data
                    bitmap_object.function_list.append(function_object)
            
               # log_to_file("   min value " + str(j) + ": " + str(bitmap_object.function_list[j].main_min_value))
              #  log_to_file("   max value " + str(j) + ": " + str(bitmap_object.function_list[j].main_max_value))    
               # log_to_file("")
                
            
        #build bitmap_object with grabbed data abouts scaling and translation
       # for h in range(transform_count):
               # log_to_file(bitmap_object.transform_type_list[j])
               # log_to_file("main min value " + str(j) + ": " + str(bitmap_object.function_list[j].main_min_value))
                if (bitmap_object.transform_type_list[j] == "uniform"): #transform is uniform scale
                    log_to_file("setting uniform scale")
                    bitmap_object.scale_uniform = bitmap_object.function_list[j].main_min_value
                    if(bitmap_object.function_list[j].range_toggle == 25): #toggle is on
                        #half the value between max and min
                        log_to_file("Toggle found")
                elif (bitmap_object.transform_type_list[j] == "scaleX"): #transform is scale X
                    log_to_file("setting scale X")
                    scaleX = bitmap_object.function_list[j].main_min_value
                    if(bitmap_object.function_list[j].range_toggle == 25): #toggle is on
                        #half the value between max and min
                        log_to_file("Toggle found")
                elif (bitmap_object.transform_type_list[j] == "scaleY"): #transform is scale Y
                    log_to_file("setting scale Y")
                    scaleY = bitmap_object.function_list[j].main_min_value
                    if(bitmap_object.function_list[j].range_toggle == 25): #toggle is on
                        #half the value between max and min 
                        log_to_file("Toggle found")
                elif (bitmap_object.transform_type_list[j] == "translateX"): #transform is scale X
                    log_to_file("setting translation X")
                    transX = bitmap_object.function_list[j].main_min_value
                    if(bitmap_object.function_list[j].range_toggle == 25): #toggle is on
                        #half the value between max and min
                        log_to_file("Toggle found")
                elif (bitmap_object.transform_type_list[j] == "translateY"): #transform is scale X
                    log_to_file("setting translation Y")
                    transY = bitmap_object.function_list[j].main_min_value
                    if(bitmap_object.function_list[j].range_toggle == 25): #toggle is on
                        #half the value between max and min 
                        log_to_file("Toggle found")
                else: 
                    log_to_file("transform type error")
        
        
        log_to_file("scale uniform: " + str(bitmap_object.scale_uniform))
        log_to_file("scale X: " + str(scaleX))
        log_to_file("scale Y: " + str(scaleY))
        log_to_file("translate X: " + str(transX))
        log_to_file("translate Y: " + str(transY))
        
        if(scaleX != 1.0 or scaleY != 1.0):
            temp_list = []
            temp_list.append(scaleX)
            temp_list.append(scaleY)
            bitmap_object.scale_xy = temp_list
        if(transX != 0.0 or transY != 0.0):
            temp_trans_list = []
            temp_trans_list.append(transX)
            temp_trans_list.append(transY)
            bitmap_object.translation_xy = temp_trans_list
        

        log_to_file("bitmap object scale: " + str(bitmap_object.scale_xy))
        return bitmap_object
           
    #checks if bitmap type has mirror mode on       
    def has_mirror_wrap(ShaderItem, bitmap_type):
        temp_val = 0
        index = 0
        max = len(ShaderItem.wrap_mode_list)
        
        log_to_file("checking for mirror for: " + bitmap_type)
        while (temp_val != 1):
            if(ShaderItem.wrap_mode_list[index].bitmap_type == bitmap_type or index == (max - 1)):
                temp_val = 1
            else:
                index = index + 1
        
        if (ShaderItem.wrap_mode_list[index].option == 2):
            log_to_file("    match!")
            return True
            
        else:
            return False
        
        # if (bitmap_type in ShaderItem.wrap_mode_list):
            # if(
        
        # for bitmap in range(len(ShaderItem.wrap_mode_list)):
            # #if bitmap types match
            # #log_to_file("1: " + ShaderItem.wrap_mode_list[bitmap].bitmap_type + "test")
            # #log_to_file("2: " + bitmap_type + "test")
            # if(ShaderItem.wrap_mode_list[bitmap].bitmap_type == bitmap_type):
                # #if wrap mode for that bitmap type is set to mirror
                # if (ShaderItem.wrap_mode_list[bitmap].option == 2):
                    # log_to_file("Mirror mapping found for " + bitmap_type)
                    # return True
            
        # return False
        
        
       
    #get the wrap mode of certain textures
    def get_wrap_mode_list(file, shader_type, ShaderItem):
        wrap_mode_object = wrap_mode()
        num_recorded_bitmaps = len(ShaderItem.bitmap_list)
        
        shaders_count = 0
        mtib_count = 0
        curr_offset = 0x0
        true_bitmap_count = 0
        temp_wrap_list = []
        temp_wrap_option = []
        temp_type_list = []
        last_mtib_offset = 0x0
        type_offset = 0x0
        after_type_offset = 0x0
        
        #log_to_file("get_wrap function")
        if(shader_type == 0):    
            file_read = file.read()
            
            try:
                #search for the first offset of fdmrshaders\shader
                #shader_shader_offset = file_read.index(b'\x66\x64\x6D\x72\x73\x68\x61\x64\x65\x72\x73\x5C\x73\x68\x61\x64\x65\x72\x6C\x62\x67\x74')
                shader_shader_offset = test_find(curr_offset, file, "fdmrshaders\shader")
                #log_to_file("fdmrshaders\shader_offset: " + str(shader_shader_offset))
            except ValueError:
                log_to_file("fmdrshaders\shader not found")
            
            #if the offset exists
            if(shader_shader_offset != 0):
                #loop through all counts of fdmrshaders\shader
                while(test_find(curr_offset, file, "fdmrshaders\shader") != -1):
                    curr_offset = test_find(curr_offset, file, "fdmrshaders\shader") #save next offset if value is found
                    shaders_count = shaders_count + 1
                    
                #reset curr_offset
                curr_offset = 0x0

                #loop through all counts of mtib            
                while(test_find(curr_offset, file, "mtib") != -1):
                    curr_offset = test_find(curr_offset, file, "mtib") #save next offset if value is found
                    mtib_count = mtib_count + 1
                    #log_to_file("mitb curr_dir offset: " + str(curr_offset))
                
                #log_to_file("mtib: " + str(mtib_count))
                if(shaders_count == 1):
                    true_bitmap_count = int(mtib_count / 2)
                elif(shaders_count == 2):
                    true_bitmap_count = int(mtib_count / 4)
                else:
                    log_to_file("something has gone wrong with get_wrap_mode_list function")
                
                #log_to_file("True bitmap count: " + str(true_bitmap_count))
                #loop a search for each mtib
                    #skip 30 bytes after start of each mtib to get option for wrap
                #log_to_file("shader shader: " + str(shader_shader_offset))
                #seek to shaders/shaderlbgt
                file.seek(shader_shader_offset)
                        
                #grab list of wrap options        
                for mtib1 in range(true_bitmap_count):
                    file.seek(test_find(file.tell(), file, "mtib")) #jump to nearest mtib
                    #log_to_file("before 30 bytes: " + str(file.tell()))
                    
                    #current location of memory location
                    #curr_loc = file.tell()
                    
                    file.seek(file.tell() + 0x18) #skip 24 bytes to where the wrap mode is
                    
                    #log_to_file("mitb curr_dir offset: " + str(file.tell()))
                    temp_wrap_list.append(int.from_bytes(file.read(2), 'little')) #store 2 byte value in temp list
                    
                    file.seek(file.tell() + 0x2) #skip to the location that the wrap option is at
                    #file.seek(file.tell() + 0x4 ) #skip 4 bytes ahead to where the wrap mode Option is for that wrap mode
                    
                    temp_wrap_option1 = int.from_bytes(file.read(2), 'little')
                    temp_wrap_option2 = int.from_bytes(file.read(2), 'little')
                    temp_wrap_option3 = int.from_bytes(file.read(2), 'little')
                    
                    if(temp_wrap_option1 != 0):
                        temp_wrap_option.append(temp_wrap_option1)
                    elif(temp_wrap_option2 != 0):
                        temp_wrap_option.append(temp_wrap_option2)
                    elif(temp_wrap_option3 != 0):
                        temp_wrap_option.append(temp_wrap_option3)
                    else:    
                        temp_wrap_option.append(0)
                    
                    
                    #log_to_file("option: " + str(temp_wrap_list[mtib1]))
                    last_mtib_offset = file.tell() #store this location for later
                    file.seek(last_mtib_offset)
                
                log_to_file("List of wrap modes: " + str(temp_wrap_list))
                log_to_file("List of wrap type options: " + str(temp_wrap_option))
                #grab the list of bitmap types
                for mtib2 in range(true_bitmap_count):
                    curr_offset = file.seek(test_find(file.tell(), file, "mtib"))
                    file.seek(curr_offset)
                    after_type_offset = file.tell() - 0xC #go back 12 bytes to end of type name
                    #log_to_file("After type offset: " + str(after_type_offset))
                    type_offset = get_before_type_offset(file, after_type_offset)
                    temp_type_list.append(get_ascii_string(file, type_offset, after_type_offset - type_offset).strip())
                    file.seek(curr_offset + 0x4)
        
            #join together temp_type_list and temp_wrap_list and store within wrap_mode_object
            #iterate through bitmap list that are stored
            for bitmaps in range(num_recorded_bitmaps):
                #iterate through true bitmap list to find matches
                for j in range(true_bitmap_count):
                    #if match is found
                    if(ShaderItem.bitmap_list[bitmaps].type == temp_type_list[j]):
                        #check if option == 2 and if it is then mark it in the bitmap object
                        ShaderItem.bitmap_list[bitmaps].wrap_option = temp_wrap_list[j]
                        ShaderItem.bitmap_list[bitmaps].wrap_option_type = temp_wrap_option[j]
                    
                    
                    #wrap_mode_object.bitmap_type = temp_type_list[j]
                
                    #log_to_file(temp_type_list[j])
                    #log_to_file("option: " + str(temp_wrap_list[j]))
                
                    #wrap_mode_list.append(wrap_mode_object)
        
        return ShaderItem


    def get_scale_uniform(file, offset, directory_len):    
        file.seek(offset + directory_len + 0x78) #skips 120 bytes after dir to where the scaling data is at
        value = struct.unpack('f', file.read(4))[0]
        
        log_to_file("Uniform Scale: " + str(value))
        return value
        
    def get_scale_xy(file, offset, directory_len):
        X_Scale = 1.00
        Y_Scale = 1.00
        Temp_List = []
        
        file.seek(offset + directory_len + 0x9C) #skips 156 bytes from dir to get X scale
        X_Scale = struct.unpack('f', file.read(4))[0]
        
        file.seek(offset + directory_len + 0xF8) #skips 248 bytes from dir to get Y scale
        Y_Scale = struct.unpack('f', file.read(4))[0]
        
        Temp_List.append(X_Scale)
        Temp_List.append(Y_Scale)
        
        log_to_file("XY Scale: " + str(Temp_List))
        
        return Temp_List

    def has_rgb_alpha(file, offset):
        file.seek(offset + 0x84 - 0x4) #skips 132 bytes then back 4
        test_bytes = 0
        test_bytes = int.from_bytes(file.read(4), 'little') #checks for isgt
        if (test_bytes == 1952936809):
            return True #has both!
        else:
            return False

    def has_rgb(file, offset):
        file.seek(offset + 0x84)
        test_float = 0.00
        test_float = struct.unpack('f', file.read(4))[0]
        #log_to_file("test float: " + str(test_float))
        #if (test_float < 0.00 or test_float > 1000): #if float value is too big or too small
        test_float_str = str(test_float)
        if 'e' in test_float_str.lower():
            #log_to_file("Bad Float detected for value. It is color!")
            return True
        else:
            if math.isnan(test_float):
                log_to_file("NaN detected!")
                return True
        
            #log_to_file("Good float detected for value. It is value!")
            return False

    def get_rgb(file, offset, value):
        temp_rgb_list = []
        temp_alpha = 1.00
        
        #log_to_file("rgb 0")
        if (value == "rgb"):
            #log_to_file("rgb 1")
            
            #rgb or alpha can be at either 0xA8 or 0x104
            if(has_rgb_alpha(file, offset) == True): #has both
                #log_to_file("rgba")
                file.seek(offset + 0xA8) #save first value as float to test
                test_float = struct.unpack('f', file.read(4))[0] #save as float
                test_float_str = str(test_float) #turn float into string
                if 'e' in test_float_str.lower(): #if float has e in it then not rgb value
                    file.seek(offset + 0xA8) #skips 168 bytes to where the color data is at

                    A = 1.00
                    B = float(int.from_bytes(file.read(1), 'little')) / 255
                    G = float(int.from_bytes(file.read(1), 'little')) / 255
                    R = float(int.from_bytes(file.read(1), 'little')) / 255
                    
                    temp_rgb_list.append(R)    
                    temp_rgb_list.append(G) 
                    temp_rgb_list.append(B)
                    temp_rgb_list.append(A)
                else:
                    file.seek(offset + 0x104) #skips 260 bytes to where the color data is at

                    A = 1.00
                    B = float(int.from_bytes(file.read(1), 'little')) / 255
                    G = float(int.from_bytes(file.read(1), 'little')) / 255
                    R = float(int.from_bytes(file.read(1), 'little')) / 255
                    
                    temp_rgb_list.append(R)    
                    temp_rgb_list.append(G) 
                    temp_rgb_list.append(B)
                    temp_rgb_list.append(A)   
                if (math.isnan(test_float)): #if FFFF then make default  
                    temp_rgb_list = color_white_rgb
            elif(has_rgb(file, offset) == True): #only rgb
                #log_to_file("rgb3")
                file.seek(offset + 0x84) #skips 132 bytes to where the color data is at

                #THIS IS TO CHECK AND FIX BAD ENV TINT COLORS
                #check if 1 byte to the left of B is 00. If not shift the BGR to the left by 1 byte
                    #check if to the left of that is also 00
                
                file.seek(offset + 0x82) #skip to the left of B value
                temp_leftB2 = float(int.from_bytes(file.read(1), 'little')) / 255
                temp_leftB1 = float(int.from_bytes(file.read(1), 'little')) / 255
                
                file.seek(offset + 0x84) #go back to where it should be
                if (temp_leftB1 == 0.0): #we might be aligned but check to the left of that to make sure it is not 0.0 as well
                    if (temp_leftB2 == 0.0): #we are not aligned set offset + 0x83
                        log_to_file("env_tint_color needs shifted to left by 1 byte")
                        file.seek(offset + 0x83) #shift seek range to left 1
                else: 
                    if (temp_leftB2 == 0.0): #we are not aligned set offset + 0x83
                        log_to_file("env_tint_color needs shifted to left by 1 byte")
                        file.seek(offset + 0x83) #shift seek range to left 1
                        
                A = 1.00
                B = float(int.from_bytes(file.read(1), 'little')) / 255
                G = float(int.from_bytes(file.read(1), 'little')) / 255
                R = float(int.from_bytes(file.read(1), 'little')) / 255
                
                #log_to_file(str(R) + " " + str(G) + " " + str(B) + " " + str(A))
                #log_to_file("rgb test: " + str(temp_rgb_list))
                temp_rgb_list.append(R)    
                temp_rgb_list.append(G) 
                temp_rgb_list.append(B)
                temp_rgb_list.append(A)
                #log_to_file("rgb test: " + str(temp_rgb_list))
            else: #only alpha   
                #log_to_file("rgb4")
                temp_rgb_list.append(1.00)
                temp_rgb_list.append(1.00)
                temp_rgb_list.append(1.00)
                temp_rgb_list.append(1.00)

            #log_to_file("RGB Value: " + str(temp_rgb_list))
            return temp_rgb_list
            
        elif (value == "alpha"): #if value == alpha
            #log_to_file("rgb5")
            if(has_rgb_alpha(file, offset) == True): #has both
                #log_to_file("rgb6")
                file.seek(offset + 0xA8) #save first value as float to test
                test_float = struct.unpack('f', file.read(4))[0] #save as float
                test_float_str = str(test_float) #turn float into string
                if 'e' in test_float_str.lower(): #if float has e in it then not rgb value
                
                    file.seek(offset + 0x104) #skips 268 bytes to where the alpha data is at

                    temp_alpha = struct.unpack('f', file.read(4))[0]
                    
                    if (math.isnan(temp_alpha)): #if FFFF then make default
                        temp_alpha = 1.00
                else:
                    file.seek(offset + 0xA8) #skips 168 bytes to where the alpha data is at

                    temp_alpha = struct.unpack('f', file.read(4))[0]  

                    if (math.isnan(temp_alpha)): #if FFFF then make default
                        temp_alpha = 1.00                
            elif(has_rgb(file, offset) == True): #only rgb
                #log_to_file("rgb7")
                temp_alpha = 1.00
            else: #only alpha   
                #log_to_file("rgb8")
                
                file.seek(offset + 0x84) #skips 132 bytes to where the color data is at

                temp_alpha = struct.unpack('f', file.read(4))[0]
                
                if (math.isnan(temp_alpha)): #if FFFF then make default
                    temp_alpha = 1.00
                
            return temp_alpha
    
    #return size of string in hex size
    def string_length_in_hex(input_string):
        length = len(input_string)
        hex_length = int(hex(length), 16)
        return hex_length
    
    #Make my life so much easier by adding support for values and colors way faster
    def Add_Value_Support(Offset, value_name, value_type, shaderfile, ShaderItem):
        if(value_type == "float"):
            if (Offset != 0): #float
                #save current data
                if(has_value(shaderfile, Offset + string_length_in_hex(value_name) + 0x1) == True):
                    value = get_value(shaderfile, Offset + string_length_in_hex(value_name) + 0x1)
                    setattr(ShaderItem, value_name, value)
                    log_to_file(f"{value_name}: " + str(value))                    
                else:
                    log_to_file(f"{value_name} value/color not found")
                    
                #check for function
                if(has_function(shaderfile, Offset + string_length_in_hex(value_name) + 0x1) == True): #value/color has function
                    FunctionItem = get_function_data(shaderfile, Offset + string_length_in_hex(value_name) + 0x1, FunctionItem) #grab function data and store it
                    print_function(FunctionItem) 
                    
                    #overrite some data for this item with the function data with halved value for testing
                    value = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                    log_to_file("  New Value from function: " + str(value))
                    setattr(ShaderItem, value_name, value)
                    ShaderItem.function_list.append(FunctionItem)
        
        elif(value_type == "color"):    
            if (Offset != 0):  #color
                #save current data
                if(has_value(shaderfile, Offset + string_length_in_hex(value_name) + 0x1) == True):
                    value = get_rgb(shaderfile, Offset + string_length_in_hex(value_name) + 0x1, "rgb")
                    log_to_file(f"{value_name}: " + str(value))                    
                    setattr(ShaderItem, value_name, value)
                else:
                    log_to_file(f"{value_name} value/color not found")
                    
                #check for function                       
                if(has_function(shaderfile, Offset + string_length_in_hex(value_name) + 0x1) == True): #value/color has function
                    FunctionItem = get_color_function_data(shaderfile, Offset + string_length_in_hex(value_name) + 0x1, FunctionItem) #grab function data and store it
                    print_function(FunctionItem) 
                    
                    #overrite some data for this item with the function data with the first color
                    value = (FunctionItem.color_1)
                    log_to_file("  New Value from function: " + str(value))
                    setattr(ShaderItem, value_name, value)
                    ShaderItem.function_list.append(FunctionItem)
    
        return ShaderItem
    
    #Save myself time and mental pain by making it easier to add texture type support
    def Add_Texture_Support(Offset, texture_type, shaderfile, ShaderItem, Tag_Root, Raw_Tag_Root):
        if (Offset != 0):
            #log_to_file("color_mask_map offset: " + str(ColorMaskMap_Offset))
            log_to_file("")
            log_to_file(f"[{texture_type}]") 
            shaderfile.seek(Offset + string_length_in_hex(texture_type) + 0x10 + 0x1)
            
            DefaultNeeded = 0
            
            #clear old bitmap data
            Bitmap = bitmap()
            Bitmap.directory = ""
            Bitmap.type = ""
            Bitmap.curve_option = 0
            Bitmap.width = 0
            Bitmap.height = 0
            Bitmap.equi_paths = []
            
            #save current data
            Bitmap.directory = get_dir(shaderfile, Offset + string_length_in_hex(texture_type) + 0x10 + 0x1)
            log_to_file("Dir: " + Bitmap.directory)
            Bitmap.type = f"{texture_type}"
            ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
            ShaderItem.bitmap_list.append(Bitmap)
            if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                 DefaultNeeded = 1 

            if (DefaultNeeded != 1):
                #try to do something with the file to get it to see if it exists
                handle_missing_texture(Bitmap.directory, bpy.context.preferences.addons[__name__].preferences.export_path + "/" + Bitmap.directory)  
            
                try:
                    if (has_prefix != True):
                        #get Curve for bitmap
                        Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                        
                        #Get Resolution of bitmap
                        Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                        Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                    else:
                        #get Curve for bitmap
                        Bitmap.curve_option = get_bitmap_curve(Raw_Tag_Root + Bitmap.directory + ".bitmap")
                        
                        #Get Resolution of bitmap
                        Bitmap.width = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "width")
                        Bitmap.height = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "height")
                except OSError:
                    log_to_file("Bitmap Directory not referenced. Please use Default Data")
           
            Bitmap = get_scale(shaderfile, (Offset + string_length_in_hex(texture_type) + 0x10 + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

            #check scaling is correct:
            log_to_file("[" + Bitmap.type + "] Scale: " + str(Bitmap.scale_xy))

            DefaultNeeded = 0
        else:
            #bitmap not referenced but might be needed
            if(is_texture_needed(ShaderItem, texture_type)):
                log_to_file("")
                log_to_file(f"[{texture_type}]")
                #DirOffset = shaderfile.tell()
                
                #clear old bitmap data
                Bitmap = bitmap()
                Bitmap.directory = ""
                Bitmap.type = ""
                Bitmap.curve_option = 0
                Bitmap.width = 0
                Bitmap.height = 0
                Bitmap.equi_paths = []
                
                Bitmap.type = texture_type
                Bitmap.directory = correct_default_dir(texture_type)
                ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                ShaderItem.bitmap_list.append(Bitmap)
    
        return ShaderItem
        
    def get_value(file, offset):
        file.seek(offset + 0x84) #skips to 132 bytes to where values live
        value = struct.unpack('f', file.read(4))[0]
        #log_to_file("Value: " + str(value))
        return value
        
    #Check the directory of the prefix for Halo 3
    #trim extra \ from directory afterwards!!
    def get_prefix_dir_h3(prefix):
        if prefix == "g":
            return "scenarios/shaders/generic";
        elif prefix == "n":
            return "scenarios/shaders/nature";
        elif prefix == "m":
            return "scenarios/shaders/multi";
        elif prefix == "shared":
            return "scenarios/shaders/shared/shaders";
        elif prefix == "ui":
            return "scenarios/shaders/ui";
        elif prefix == "mainmenu":
            return "scenarios/shaders/ui/mainmenu";
        elif prefix == "mm":
            return "levels/ui/mainmenu/shaders";
        elif prefix == "gen":
            return "levels/shared/shaders/generic";
        elif prefix == "simple":
            return "levels/shared/shaders/simple";
        elif prefix == "mpshare":
            return "levels/shared/shaders/multi";
        elif prefix == "shared":
            return "levels/shared/shaders";
        elif prefix == "test_box":
            return "levels/test/box";
        elif prefix == "shr":
            return "levels/shared/shaders";
        elif prefix == "jun":
            return "levels/solo/010_jungle";
        elif prefix == "base":
            return "levels/solo/020_base";
        elif prefix == "city":
            return "levels/solo/03a_oldmombasa";
        elif prefix == "zanzibar":
            return "levels/solo/03a_oldmombasa";
        elif prefix == "temple":
            return "levels/solo/05a_deltaapproach";
        elif prefix == "voi":
            return "levels/solo/040_voi";
        elif prefix == "fvoi":
            return "levels/solo/050_floodvoi";
        elif prefix == "fz":
            return "levels/solo/06b_floodzone";
        elif prefix == "fs":
            return "levels/solo/110_hc/shaders";
        elif prefix == "out":
            return "levels/solo/030_outskirts";
        elif prefix == "hc":
            return "levels/solo/110_hc";
        elif prefix == "gf":
            return "levels/solo/080_forest";
        elif prefix == "waste":
            return "levels/solo/070_waste";
        elif prefix == "cit":
            return "levels/solo/100_citadel";
        elif prefix == "halo":
            return "levels/solo/120_halo";
        elif prefix == "shadow":
            return "levels/solo/055_shadow";
        elif prefix == "s3dtut":
            return "levels/solo/s3d_tutorial";
        elif prefix == "temp":
            return "levels/temp";
        elif prefix == "play":
            return "levels/temp/scarab_playground";
        elif prefix == "concrete":
            return "levels/temp/concrete";
        elif prefix == "destructo":
            return "levels/temp/destructo";
        elif prefix == "re":
            return "levels/temp/reservoir";
        elif prefix == "lt":
            return "levels/temp/lighting_test";
        elif prefix == "omega":
            return "levels/temp/barry/omega";
        elif prefix == "mptemp":
            return "levels/temp/mp_temp_shaders";
        elif prefix == "mpsky":
            return "levels/temp/mp_temp_sky";
        elif prefix == "chill":
            return "levels/multi/chill";
        elif prefix == "sal":
            return "levels/multi/salvation";     
        elif prefix == "shaft":
            return "levels/multi/shaft";
        elif prefix == "ph":
            return "levels/multi/pump_haus";
        elif prefix == "sb":
            return "levels/multi/snowbound";
        elif prefix == "iso":
            return "levels/multi/isolation";
        elif prefix == "shr":
            return "levels/multi/shrine";
        elif prefix == "con":
            return "levels/multi/construct";
        elif prefix == "dead":
            return "levels/multi/deadlock";
        elif prefix == "guardian":
            return "levels/multi/guardian";
        elif prefix == "river":
            return "levels/multi/riverworld";
        elif prefix == "zan":
            return "levels/multi/zanzibar";
        elif prefix == "cyber":
            return "levels/multi/cyberdyne";
        elif prefix == "s3dava":
            return "levels/multi/s3d_avalanche";
        elif prefix == "s3ddale":
            return "levels/multi/s3d_dale";
        elif prefix == "s3dedge":
            return "levels/multi/s3d_edge";
        elif prefix == "s3dhangar":
            return "levels/multi/s3d_hangar";
        elif prefix == "s3dreactor":
            return "levels/multi/s3d_reactor";
        elif prefix == "s3drock":
            return "levels/multi/s3d_rock";
        elif prefix == "s3dside":
            return "levels/multi/s3d_sidewinder";
        elif prefix == "s3dturf":
            return "levels/multi/s3d_turf";
        elif prefix == "s3dunder":
            return "levels/multi/s3d_underwater";
        elif prefix == "s3dwell":
            return "levels/multi/s3d_well";
        elif prefix == "s3dpwhs":
            return "levels/multi/s3d_powerhouse";
        elif prefix == "s3dwtf":
            return "levels/multi/s3d_waterfall";
        elif prefix == "s3dcntdw":
            return "levels/multi/s3d_countdown";
        elif prefix == "s3dskybr":
            return "levels/multi/s3d_sky_bridgenew";
        elif prefix == "s3dlock":
            return "levels/multi/s3d_lockout";
        elif prefix == "s3dhvn":
            return "levels/multi/s3d_haven";
        elif prefix == "s3ddrd":
            return "levels/multi/s3d_drydock";
        elif prefix == "s3dbms":
            return "levels/multi/s3d_burial_mounds";
        elif prefix == "s3dchill":
            return "levels/multi/s3d_chillout";
        elif prefix == "s3dbvr":
            return "levels/multi/s3d_beaver_creek";
        elif prefix == "obj_sh":
            return "objects/levels/shared";
        elif prefix == "phantom":
            return "objects/vehicles/phantom";
        elif prefix == "wraith":
            return "objects/vehicles/wraith";
        elif prefix == "cruis":
            return "objects/vehicles/cov_cruiser";
        elif prefix == "voi_obj":
            return "objects/levels/solo/040_voi";
        elif prefix == "pelican":
            return "objects/vehicles/pelican";
        elif prefix == "lod":
            return "objects/vehicles/lod";
        elif prefix == "civ":
            return "objects/vehicles/civilian";
        elif prefix == "humanmil":
            return "objects/gear/human/military";
        elif prefix == "humanind":
            return "objects/gear/human/industrial";
        elif prefix == "dlobj":
            return "objects/levels/multi/deadlock";
        elif prefix == "scarab":
            return "objects/giants/scarab";
        elif prefix == "salobj":
            return "objects/levels/multi/salvation";
        elif prefix == "frigate":
            return "objects/cinematics/human/frigate";
        elif prefix == "plas_turret":
            return "objects/weapons/turret/plasma_cannon";
        elif prefix == "char":
            return "objects/characters";
        elif prefix == "ware":
            return "levels/dlc/warehouse";
        elif prefix == "dock":
            return "levels/dlc/docks";
        elif prefix == "camp":
            return "levels/dlc/spacecamp";
        elif prefix == "side":
            return "levels/dlc/sidewinder";
        elif prefix == "beach":
            return "levels/dlc/beachhead";
        elif prefix == "descent":
            return "levels/dlc/descent";
        elif prefix == "lock":
            return "levels/dlc/lockout";
        elif prefix == "bunk":
            return "levels/dlc/bunkerworld";
        elif prefix == "vol":
            return "levels/dlc/volcano";
        elif prefix == "gash":
            return "levels/dlc/the_gash";
        elif prefix == "arm":
            return "levels/dlc/armory";
        elif prefix == "land":
            return "levels/dlc/landslide";
        elif prefix == "pump":
            return "levels/dlc/pump_haus";
        elif prefix == "shaft":
            return "levels/dlc/shaft";
        elif prefix == "wart":
            return "levels/dlc/warthog_inc";
        elif prefix == "ghost":
            return "levels/dlc/ghosttown";
        elif prefix == "chillout":
            return "levels/dlc/chillout";
        elif prefix == "midship":
            return "levels/dlc/midship";
        elif prefix == "fort":
            return "levels/dlc/fortress";
        else:
            return "error"

        
    #Halo 3 ODST prefix
    def get_prefix_dir_h3odst(prefix):
        if prefix == "g":
            return "scenarios/shaders/generic";
        elif prefix == "n":
            return "scenarios/shaders/nature";
        elif prefix == "m":
            return "scenarios/shaders/multi";
        elif prefix == "shared":
            return "scenarios/shaders/shared/shaders";
        elif prefix == "ui":
            return "scenarios/shaders/ui";
        elif prefix == "mainmenu":
            return "scenarios/shaders/ui/mainmenu";
        elif prefix == "gen":
            return "levels/shared/shaders/generic";
        elif prefix == "simple":
            return "levels/shared/shaders/simple";
        elif prefix == "mpshare":
            return "levels/shared/shaders/multi";
        elif prefix == "shared":
            return "levels/shared/shaders";
        elif prefix == "def":
            return "levels/atlas/shared/default/shaders";
        elif prefix == "deftest":
            return "levels/atlas/shared/default/shaders/temp";
        elif prefix == "atlas":
            return "levels/atlas/shared/shaders";
        elif prefix == "test_box":
            return "levels/test/box";
        elif prefix == "shr":
            return "levels/shared/shaders";
        elif prefix == "jun":
            return "levels/solo/010_jungle";
        elif prefix == "base":
            return "levels/solo/020_base";
        elif prefix == "city":
            return "levels/solo/03a_oldmombasa";
        elif prefix == "zanzibar":
            return "levels/solo/03a_oldmombasa";
        elif prefix == "temple":
            return "levels/solo/05a_deltaapproach";
        elif prefix == "voi":
            return "levels/solo/040_voi";
        elif prefix == "fvoi":
            return "levels/solo/050_floodvoi";
        elif prefix == "fz":
            return "levels/solo/06b_floodzone";
        elif prefix == "fs":
            return "levels/solo/110_hc/shaders";
        elif prefix == "out":
            return "levels/solo/030_outskirts";
        elif prefix == "hc":
            return "levels/solo/110_hc";
        elif prefix == "gf":
            return "levels/solo/080_forest";
        elif prefix == "waste":
            return "levels/solo/070_waste";
        elif prefix == "cit":
            return "levels/solo/100_citadel";
        elif prefix == "halo":
            return "levels/solo/120_halo";
        elif prefix == "shadow":
            return "levels/solo/055_shadow";
        elif prefix == "temp":
            return "levels/temp";
        elif prefix == "play":
            return "levels/temp/scarab_playground";
        elif prefix == "concrete":
            return "levels/temp/concrete";
        elif prefix == "destructo":
            return "levels/temp/destructo";
        elif prefix == "re":
            return "levels/temp/reservoir";
        elif prefix == "lt":
            return "levels/temp/lighting_test";
        elif prefix == "omega":
            return "levels/temp/barry/omega";
        elif prefix == "mptemp":
            return "levels/temp/mp_temp_shaders";
        elif prefix == "mpsky":
            return "levels/temp/mp_temp_sky";
        elif prefix == "bp":
            return "levels/atlas/shared";
        elif prefix == "hut":
            return "levels/temp/kdal";
        elif prefix == "chill":
            return "levels/multi/chill";
        elif prefix == "sal":
            return "levels/multi/salvation";
        elif prefix == "shaft":
            return "levels/multi/shaft";
        elif prefix == "ph":
            return "levels/multi/pump_haus";
        elif prefix == "sb":
            return "levels/multi/snowbound";
        elif prefix == "iso":
            return "levels/multi/isolation";
        elif prefix == "shrine":
            return "levels/multi/shrine";
        elif prefix == "con":
            return "levels/multi/construct";
        elif prefix == "dead":
            return "levels/multi/deadlock";
        elif prefix == "guardian":
            return "levels/multi/guardian";
        elif prefix == "river":
            return "levels/multi/riverworld";
        elif prefix == "zan":
            return "levels/multi/zanzibar";
        elif prefix == "cyber":
            return "levels/multi/cyberdyne";
        elif prefix == "obj_sh":
            return "objects/levels/shared";
        elif prefix == "phantom":
            return "objects/vehicles/phantom";
        elif prefix == "wraith":
            return "objects/vehicles/wraith";
        elif prefix == "cruis":
            return "objects/vehicles/cov_cruiser";
        elif prefix == "voi_obj":
            return "objects/levels/solo/040_voi";
        elif prefix == "pelican":
            return "objects/vehicles/pelican";
        elif prefix == "lod":
            return "objects/vehicles/lod";
        elif prefix == "civ":
            return "objects/vehicles/civilian";
        elif prefix == "humanmil":
            return "objects/gear/human/military";
        elif prefix == "humanind":
            return "objects/gear/human/industrial";
        elif prefix == "dlobj":
            return "objects/levels/multi/deadlock";
        elif prefix == "scarab":
            return "objects/giants/scarab";
        elif prefix == "salobj":
            return "objects/levels/multi/salvation";
        elif prefix == "frigate":
            return "objects/cinematics/human/frigate";
        elif prefix == "plas_turret":
            return "objects/weapons/turret/plasma_cannon";
        elif prefix == "char":
            return "objects/characters";
        elif prefix == "smon":
            return "objects/levels/dlc/spacecamp";
        elif prefix == "gciv":
            return "objects/gear/atlas/civilian";
        elif prefix == "sign":
            return "objects/levels/atlas/shared/signage";
        elif prefix == "obj_tether":
            return "objects/levels/atlas/tether_chunks";
        elif prefix == "obj_l200":
            return "objects/levels/atlas/l200";
        elif prefix == "ware":
            return "levels/dlc/warehouse";
        elif prefix == "dock":
            return "levels/dlc/docks";
        elif prefix == "camp":
            return "levels/dlc/spacecamp";
        elif prefix == "side":
            return "levels/dlc/sidewinder";
        elif prefix == "beach":
            return "levels/dlc/beachhead";
        elif prefix == "descent":
            return "levels/dlc/descent";
        elif prefix == "lock":
            return "levels/dlc/lockout";
        elif prefix == "bunk":
            return "levels/dlc/bunkerworld";
        elif prefix == "vol":
            return "levels/dlc/volcano";
        elif prefix == "gash":
            return "levels/dlc/the_gash";
        elif prefix == "arm":
            return "levels/dlc/armory";
        elif prefix == "land":
            return "levels/dlc/landslide";
        elif prefix == "pump":
            return "levels/dlc/pump_haus";
        elif prefix == "shaft":
            return "levels/dlc/shaft";
        elif prefix == "wart":
            return "levels/dlc/warthog_inc";
        elif prefix == "ghost":
            return "levels/dlc/ghosttown";
        elif prefix == "chillout":
            return "levels/dlc/chillout";
        elif prefix == "midship":
            return "levels/dlc/midship";
        elif prefix == "proto":
            return "levels/temp/prototypes";
        elif prefix == "hev":
            return "levels/atlas/c100";
        elif prefix == "mom":
            return "levels/atlas/h100";
        elif prefix == "street":
            return "levels/atlas/l100";
        elif prefix == "Plaza":
            return "levels/atlas/sc100";
        elif prefix == "park":
            return "levels/atlas/sc110";
        elif prefix == "park_shared":
            return "levels/atlas/sc110/shaders/shared";
        elif prefix == "convoy":
            return "levels/atlas/sc120";
        elif prefix == "oni":
            return "levels/atlas/sc130";
        elif prefix == "roof":
            return "levels/atlas/sc140";
        elif prefix == "train":
            return "levels/atlas/sc150";
        elif prefix == "sewer":
            return "levels/atlas/l200";
        elif prefix == "high":
            return "levels/atlas/l300";
        elif prefix == "excav":
            return "levels/atlas/c200";
        elif prefix == "basehang":
            return "levels/atlas/c300";
        elif prefix == "shared_atlas":
            return "levels/atlas/shared";
        elif prefix == "atlas_shared":
            return "levels/atlas/shared";
        elif prefix == "roof_sky":
            return "levels/atlas/sc140/sky";
        else:
            return "error"

    def get_prefix_dir_reach(prefix):
        if prefix == "g":
            return "scenarios/shaders/generic";
        elif prefix == "n":
            return "scenarios/shaders/nature";
        elif prefix == "m":
            return "scenarios/shaders/multi";
        elif prefix == "shared":
            return "scenarios/shaders/shared/shaders";
        elif prefix == "ui":
            return "scenarios/shaders/ui";
        elif prefix == "mainmenu":
            return "scenarios/shaders/ui/mainmenu";
        elif prefix == "gen":
            return "levels/shared/shaders/generic";
        elif prefix == "simple":
            return "levels/shared/shaders/simple";
        elif prefix == "mpshare":
            return "levels/shared/shaders/multi";
        elif prefix == "shared":
            return "levels/shared/shaders";
        elif prefix == "test_box":
            return "levels/test/box";
        elif prefix == "shr":
            return "levels/shared/shaders";
        elif prefix == "jun":
            return "levels/solo/010_jungle";
        elif prefix == "base":
            return "levels/solo/020_base";
        elif prefix == "city":
            return "levels/solo/03a_oldmombasa";
        elif prefix == "zanzibar":
            return "levels/solo/03a_oldmombasa";
        elif prefix == "temple":
            return "levels/solo/05a_deltaapproach";
        elif prefix == "voi":
            return "levels/solo/040_voi";
        elif prefix == "fvoi":
            return "levels/solo/050_floodvoi";
        elif prefix == "fz":
            return "levels/solo/06b_floodzone";
        elif prefix == "fs":
            return "levels/solo/110_hc/shaders";
        elif prefix == "out":
            return "levels/temp/niles/outskirts_test/shaders";
        elif prefix == "hc":
            return "levels/solo/110_hc";
        elif prefix == "gf":
            return "levels/solo/080_forest";
        elif prefix == "waste":
            return "levels/solo/070_waste";
        elif prefix == "cit":
            return "levels/solo/100_citadel";
        elif prefix == "halo":
            return "levels/solo/120_halo";
        elif prefix == "shadow":
            return "levels/solo/055_shadow";
        elif prefix == "cra":
            return "levels/missions/mission_40";
        elif prefix == "temp":
            return "levels/temp";
        elif prefix == "play":
            return "levels/temp/scarab_playground";
        elif prefix == "concrete":
            return "levels/temp/concrete";
        elif prefix == "destructo":
            return "levels/temp/destructo";
        elif prefix == "re":
            return "levels/temp/reservoir";
        elif prefix == "lt":
            return "levels/temp/lighting_test";
        elif prefix == "omega":
            return "levels/temp/barry/omega";
        elif prefix == "mptemp":
            return "levels/temp/mp_temp_shaders";
        elif prefix == "mpsky":
            return "levels/temp/mp_temp_sky";
        elif prefix == "ref":
            return "levels/reference/material_samples/shaders/building";
        elif prefix == "chill":
            return "levels/multi/chill";
        elif prefix == "sal":
            return "levels/multi/salvation";
        elif prefix == "shaft":
            return "levels/multi/shaft";
        elif prefix == "ph":
            return "levels/multi/pump_haus";
        elif prefix == "sb":
            return "levels/multi/snowbound";
        elif prefix == "iso":
            return "levels/multi/isolation";
        elif prefix == "shr":
            return "levels/multi/shrine";
        elif prefix == "con":
            return "levels/multi/construct";
        elif prefix == "dead":
            return "levels/multi/deadlock";
        elif prefix == "guardian":
            return "levels/multi/guardian";
        elif prefix == "river":
            return "levels/multi/riverworld";
        elif prefix == "zan":
            return "levels/multi/zanzibar";
        elif prefix == "cyber":
            return "levels/multi/cyberdyne";
        elif prefix == "spartan":
            return "levels/multi/spartanland";
        elif prefix == "settle":
            return "levels/multi/10_settlement";
        elif prefix == "obj_sh":
            return "objects/levels/shared/";
        elif prefix == "phantom":
            return "objects/vehicles/phantom";
        elif prefix == "wraith":
            return "objects/vehicles/wraith";
        elif prefix == "cruis":
            return "objects/vehicles/cov_cruiser";
        elif prefix == "voi_obj":
            return "objects/levels/solo/040_voi";
        elif prefix == "pelican":
            return "objects/vehicles/human/pelican";
        elif prefix == "lod":
            return "objects/vehicles/lod";
        elif prefix == "civ":
            return "objects/vehicles/civilian";
        elif prefix == "humanmil":
            return "objects/gear/human/military";
        elif prefix == "humanind":
            return "objects/gear/human/industrial";
        elif prefix == "dlobj":
            return "objects/levels/multi/deadlock";
        elif prefix == "scarab":
            return "objects/giants/scarab";
        elif prefix == "salobj":
            return "objects/levels/multi/salvation";
        elif prefix == "frigate":
            return "objects/cinematics/human/frigate";
        elif prefix == "plas_turret":
            return "objects/weapons/turret/plasma_cannon";
        elif prefix == "char":
            return "objects/characters";
        elif prefix == "elite":
            return "objects/characters/elite";
        elif prefix == "ware":
            return "levels/dlc/warehouse";
        elif prefix == "dock":
            return "levels/dlc/docks";
        elif prefix == "camp":
            return "levels/dlc/spacecamp";
        elif prefix == "side":
            return "levels/dlc/sidewinder";
        elif prefix == "beach":
            return "levels/dlc/beachhead";
        elif prefix == "descent":
            return "levels/dlc/descent";
        elif prefix == "lock":
            return "levels/dlc/lockout";
        elif prefix == "bunk":
            return "levels/dlc/bunkerworld";
        elif prefix == "vol":
            return "levels/dlc/volcano";
        elif prefix == "gash":
            return "levels/dlc/the_gash";
        elif prefix == "arm":
            return "levels/dlc/armory";
        elif prefix == "land":
            return "levels/dlc/landslide";
        elif prefix == "pump":
            return "levels/dlc/pump_haus";
        elif prefix == "shaft":
            return "levels/dlc/shaft";
        elif prefix == "wart":
            return "levels/dlc/warthog_inc";
        else:
            return "error"
    
    
    #Checks if a directory is valid or not
    def is_valid_dir(directory):
        if (directory.split('/')[0] == 'ai' or directory.split('/')[0] == 'camera' or directory.split('/')[0] == 'cinematics' or directory.split('/')[0] == 'effects' or directory.split('/')[0] == 'fx' or directory.split('/')[0] == 'globals' or directory.split('/')[0] == 'levels' or directory.split('/')[0] == 'multiplayer' or directory.split('/')[0] == 'objects' or directory.split('/')[0] == 'rasterizer' or directory.split('/')[0] == 'shaders' or directory.split('/')[0] == 'sound' or directory.split('/')[0] == 'ui' or directory.split('/')[0] == ''):
            return True
        else:
            return False
        
    def get_albedo_foliage_option(option):  
        if (option == 0):
            return "default"
        else:
            return "error reading value"

    def get_alpha_foliage_option(option):  
        if (option == 0):
            return "none"
        elif (option == 1):
            return "simple"
        else:
            return "error reading value"

    def get_material_foliage_option(option):  
        if (option == 0):
            return "default"
        else:
            return "error reading value"

    def get_color_option(option):  
        if (option == 2):
            return "2-color"
        elif (option == 3):
            return "3-color"
        elif (option == 4):
            return "4-color"
        else:
            return "error reading color option value"

    #If it is FF then it is the default option of Category
    
    def get_albedo_option(option):
        if (option == 0):
            return "default"
        elif (option == 1):
            return "detail_blend"
        elif (option == 2):
            return "constant_color"
        elif (option == 3):
            return "two_change_color"
        elif (option == 4):
            return "four_change_color"
        elif (option == 5):
            return "three_detail_blend"
        elif (option == 6):
            return "two_detail_overlay"
        elif (option == 7):
            return "two_detail"
        elif (option == 8):
            return "color_mask"
        elif (option == 9):
            return "two_detail_black_point"
        elif (option == 10):
            return "two_change_color_anim_overlay"
        elif (option == 11):
            return "chameleon"
        elif (option == 12):
            return "two_change_color_chameleon"
        elif (option == 13):
            return "chameleon_masked"   
        elif (option == 14):
            return "color_mask_hard_light"   
        elif (option == 15):
            return "two_change_color_tex_overlay"   
        elif (option == 16):
            return "chameleon_albedo_masked"   
        elif (option == 17):
            return "custom_cube"   
        elif (option == 18):
            return "two_color"           
        elif (option == 19):
            return "scrolling_cube_mask"   
        elif (option == 20):
            return "scrolling_cube"   
        elif (option == 21):
            return "scrolling_texture_uv"   
        elif (option == 22):
            return "texture_from_misc"   
        else:
            return "ERROR"
    
    #HALO 3 DECAL SHADER ALBEDO OPTIONS
    def get_h3_albedo_decal_option(option):
        if (option == 0):
            return "diffuse_only"
        elif (option == 1):
            return "palettized"
        elif (option == 2):
            return "palettized_plus_alpha"
        elif (option == 3):
            return "diffuse_plus_alpha"
        elif (option == 4):
            return "emblem_change_color"
        elif (option == 5):
            return "change_color"
        elif (option == 6):
            return "diffuse_plus_alpha_mask"
        elif (option == 7):
            return "palettized_plus_alpha_mask"
        elif (option == 8):
            return "vector_alpha"
        elif (option == 9):
            return "vector_alpha_drop_shadow" 
        else:
            return "ERROR"
    
    #halo 3 .shader_custom albedo option
    def get_albedo_custom_option(option):
        if (option == 0):
            return "default"
        elif (option == 1):
            return "detail_blend"
        elif (option == 2):
            return "constant_color"
        elif (option == 3):
            return "two_change_color"
        elif (option == 4):
            return "four_change_color"
        elif (option == 5):
            return "three_detail_blend"
        elif (option == 6):
            return "two_detail_overlay"
        elif (option == 7):
            return "two_detail"
        elif (option == 8):
            return "color_mask"
        elif (option == 9):
            return "two_detail_black_point"
        elif (option == 10):
            return "waterfall"
        elif (option == 11):
            return "multiply_map"
        else:
            return "ERROR"
    
    def get_reach_albedo_option(option):
        if (option == 0 or option == int("FF", 16)):
            return "default"
        elif (option == 1):
            return "detail_blend"
        elif (option == 2):
            return "constant_color"
        elif (option == 3):
            return "two_change_color"
        elif (option == 4):
            return "four_change_color"
        elif (option == 5):
            return "three_detail_blend"
        elif (option == 6):
            return "two_detail_overlay"
        elif (option == 7):
            return "two_detail"
        elif (option == 8):
            return "color_mask"
        elif (option == 9):
            return "two_detail_black_point"
        elif (option == 10):
            return "four_change_color_applying_to_specular"
        elif (option == 11):
            return "simple"
        else:
            return "ERROR"
        
            
    def get_bump_mapping_option(option):
        if (option == 0):
            return "off"
        elif (option == 1):
            return "standard"
        elif (option == 2):
            return "detail"   
        elif (option == 3):
            return "detail_masked"
        elif (option == 4):
            return "detail_plus_detail_masked"
        elif (option == 5):
            return "detail_unorm"
        else:
            return "ERROR"
            
    #halo 3 decal shader bump mapping option        
    def get_h3_bump_mapping_decal_option(option):
        if (option == 0):
            return "leave"
        elif (option == 1):
            return "standard"
        elif (option == 2):
            return "standard_mask"   
        else:
            return "ERROR"
            
    #halo 3 decal shader tinting option        
    def get_h3_tinting_decal_option(option):
        if (option == 0):
            return "none"
        elif (option == 1):
            return "unmodulated"
        elif (option == 2):
            return "partially_modulated"  
        elif (option == 3):
            return "fully_modulated"             
        else:
            return "ERROR"
            
    def get_reach_bump_mapping_option(option):
        if (option == 0 or option == int("FF", 16)):
            return "off"
        elif (option == 1):
            return "standard"
        elif (option == 2):
            return "detail"   
        elif (option == 3):
            return "detail_blend"
        elif (option == 4):
            return "three_detail_blend"
        elif (option == 5):
            return "standard_wrinkle"
        elif (option == 6):
            return "detail_wrinkle"
        else:
            return "ERROR"        
    
    #both 3/ODST/Reach    
    def get_alpha_test_option(option):
        if (option == 0 or option == int("FF", 16)):
            return "none"
        elif (option == 1):
            return "simple"
        elif (option == 2):
            return "multiply_map"
        else:
            return "ERROR"
            
    def get_specular_mask_option(option):        
        if (option == 0):
            return "no_specular_mask"
        elif (option == 1):
            return "specular_mask_from_diffuse"
        elif (option == 2):
            return "specular_mask_from_texture"
        elif (option == 3):
            return "specular_mask_from_color_texture"
        else:
            return "ERROR"
            
    def get_reach_specular_mask_option(option):        
        if (option == 0 or option == int("FF", 16)):
            return "no_specular_mask"
        elif (option == 1):
            return "specular_mask_from_diffuse"
        elif (option == 2):
            return "specular_mask_mult_diffuse"
        elif (option == 3):
            return "specular_mask_from_texture"
        else:
            return "ERROR"
            
    def get_material_model_option(option):
        if (option == 0):
            return "diffuse_only"    
        elif (option == 1):
            return "cook_torrance"
        elif (option == 2):
            return "two_lobe_phong"
        elif (option == 3):
            return "foliage"
        elif (option == 4):
            return "none"
        elif (option == 5):
            return "glass"
        elif (option == 6):
            return "organism"
        elif (option == 7):
            return "single_lobe_phong"        
        elif (option == 8):
            return "car_paint"
        elif (option == 9):
            return "cook_torrance_custom_cube"
        elif (option == 10):
            return "cook_torrance_pbr_maps"
        elif (option == 11):
            return "cook_torrance_two_color_spec_tint"    
        elif (option == 12):
            return "two_lobe_phong_tint_map"    
        elif (option == 13):
            return "cook_torrance_scrolling_cube_mask"    
        elif (option == 14):
            return "cook_torrance_rim_fresnel"
        elif (option == 15):
            return "cook_torrance_scrolling_cube"        
        elif (option == 16):
            return "cook_torrance_from_albedo"   
        else:
            return "ERROR"
            
    #halo 3 shader_custom material model options         
    def get_material_model_custom_option(option):
        if (option == 0):
            return "diffuse_only"    
        elif (option == 1):
            return "two_lobe_phong"
        elif (option == 2):
            return "foliage"
        elif (option == 3):
            return "none"
        elif (option == 4):
            return "custom_specular"
        else:
            return "ERROR"
            
    def get_reach_material_model_option(option):
        if (option == 0 or option == int("FF", 16)):
            return "diffuse_only"    
        elif (option == 1):
            return "cook_torrance"
        elif (option == 2):
            return "two_lobe_phong"
        elif (option == 3):
            return "foliage"
        elif (option == 4):
            return "none"
        elif (option == 5):
            return "organism"
        elif (option == 6):
            return "hair"
        else:
            return "ERROR"
            
    #both 3/ODST/Reach        
    def get_environment_mapping_option(option):
        if (option == 0 or option == int("FF", 16)):
            return "none"
        elif (option == 1):
            return "per_pixel"   
        elif (option == 2):
            return "dynamic"     
        elif (option == 3):
            return "from_flat_texture"     
        elif (option == 4):
            return "custom_map"     
        elif (option == 5):
            return "from_flat_exture_as_cubemap"     
        else:
            return "ERROR"
            
    def get_self_illumination_option(option):
        if (option == 0):
            return "off"
        elif (option == 1):
            return "simple" 
        elif (option == 2):
            return "3_channel_self_illum" 
        elif (option == 3):
            return "plasma" 
        elif (option == 4):
            return "from_diffuse" 
        elif (option == 5):
            return "illum_detail" 
        elif (option == 6):
            return "meter" 
        elif (option == 7):
            return "self_illum_times_diffuse" 
        elif (option == 8):
            return "simple_with_alpha_mask" 
        elif (option == 9):
            return "simple_four_change_color"         
        elif (option == 10):
            return "illum_detail_world_space_four_cc"     
        elif (option == 11):
            return "illum_change_color" 
        else:
            return "ERROR"
            
    #halo 3 shader_custom self illum options
    def get_self_illumination_custom_option(option):
        if (option == 0):
            return "off"
        elif (option == 1):
            return "simple" 
        elif (option == 2):
            return "3_channel_self_illum" 
        elif (option == 3):
            return "plasma" 
        elif (option == 4):
            return "from_diffuse" 
        elif (option == 5):
            return "illum_detail" 
        elif (option == 6):
            return "meter" 
        elif (option == 7):
            return "self_illum_times_diffuse" 
        elif (option == 8):
            return "window_room" 
        else:
            return "ERROR"
            
    def get_reach_self_illumination_option(option):
        if (option == 0 or option == int("FF", 16)):
            return "off"
        elif (option == 1):
            return "simple" 
        elif (option == 2):
            return "3_channel_self_illum" 
        elif (option == 3):
            return "plasma" 
        elif (option == 4):
            return "from_diffuse" 
        elif (option == 5):
            return "illum_detail" 
        elif (option == 6):
            return "meter" 
        elif (option == 7):
            return "self_illum_times_diffuse" 
        elif (option == 8):
            return "simple_with_alpha_mask" 
        elif (option == 9):
            return "multilayer_additive"         
        elif (option == 10):
            return "palettized_plasma"     
        elif (option == 11):
            return "change_color" 
        elif (option == 12):
            return "change_color_detail" 
        else:
            return "ERROR"
            
    
    def get_halogram_self_illumination_option(option):
        if (option == 0):
            return "off"
        elif (option == 1):
            return "simple" 
        elif (option == 2):
            return "3_channel_self_illum" 
        elif (option == 3):
            return "plasma" 
        elif (option == 4):
            return "from_diffuse" 
        elif (option == 5):
            return "illum_detail" 
        elif (option == 6):
            return "meter" 
        elif (option == 7):
            return "self_illum_times_diffuse" 
        elif (option == 8):
            return "multilayer_additive" 
        elif (option == 9):
            return "scope_blur"         
        elif (option == 10):
            return "ml_add_four_change_color"     
        elif (option == 11):
            return "ml_add_five_change_color" 
        elif (option == 12):
            return "plasma_wide_and_sharp_five_change_color"     
        elif (option == 13):
            return "self_illum_holograms" 
        else:
            return "ERROR"     
    
    #both 3/ODST/Reach
    def get_blend_mode_option(option):
        if (option == 0 or option == int("FF", 16)):
            return "opaque"
        elif (option == 1):
            return "additive"             
        elif (option == 2):
            return "multiply"             
        elif (option == 3):
            return "alpha_blend"             
        elif (option == 4):
            return "double_multiply"             
        elif (option == 5):
            return "pre_multiplied_alpha"             
        else:
            return "ERROR"
            
    def get_h3_blend_mode_decal_option(option):
        if (option == 0 or option == int("FF", 16)):
            return "opaque"
        elif (option == 1):
            return "additive"             
        elif (option == 2):
            return "multiply"             
        elif (option == 3):
            return "alpha_blend"             
        elif (option == 4):
            return "double_multiply"             
        elif (option == 5):
            return "maximum"  
        elif (option == 6):
            return "multiply_add"             
        elif (option == 7):
            return "add_src_times_dstalpha"             
        elif (option == 8):
            return "add_src_times_srcalpha"   
        elif (option == 9):
            return "inv_alpha_blend" 
        elif (option == 10):
            return "pre_multiplied_alpha"  
        else:
            return "ERROR"
            
    def get_parallax_option(option):
        if(option == 0 or option == int("FF", 16)):
            return "off"
        elif (option == 1):
            return "simple"             
        elif (option == 2):
            return "interpolated"             
        elif (option == 3):
            return "simple_detail" 
        else:
            return "ERROR"
            
    def get_misc_option(option):
        if(option == 0):
            return "first_person_never"
        elif (option == 1):
            return "first_person_sometimes" 
        elif (option == 2):
            return "first_person_always"    
        elif (option == 3):
            return "first_person_never_w/rotating_bitmaps"             
        else:
            return "ERROR"
            
    def get_reach_misc_option(option):
        if(option == 0 or option == int("FF", 16)):
            return "default"
        elif (option == 1):
            return "rotating_bitmaps_super_slow"        
        else:
            return "ERROR"

    def get_reach_wetness_option(option):
        if(option == 0 or option == int("FF", 16)):
            return "default"
        elif (option == 1):
            return "flood" 
        elif (option == 2):
            return "proof"    
        elif (option == 3):
            return "simple"  
        elif (option == 4):
            return "ripples"  
        else:
            return "ERROR"

    def get_reach_alpha_blend_source_option(option):
        if(option == 0 or option == int("FF", 16)):
            return "from_albedo_alpha_without_fresnel"
        elif (option == 1):
            return "from_albedo_alpha" 
        elif (option == 2):
            return "from_opacity_map_alpha"    
        elif (option == 3):
            return "from_opacity_map_rgb"  
        elif (option == 4):
            return "from_opacity_map_alpha_and_albedo_alpha"  
        else:
            return "ERROR"

    def get_bitmap_curve_option(option):
        if (option == 0):
            return "unknown"   #has gamma SOMETIMES, mostly not tho
        elif (option == 1):
            return "xRGB"      #has gamma
        elif (option == 2):
            return "gamma 2.0" #has gamma
        elif (option == 3):
            return "linear"
        elif (option == 4):
            return "offset log"
        elif (option == 5):
            return "sRGB"
        elif (option == 6):
            return "Default Data"
        else:
            return "ERROR"
            
    def get_function_option(option):
        if(option == 1):
            return "basic"
        elif(option == 8):
            return "curve"
        elif(option == 3):
            return "periodic"
        elif(option == 9):
            return "exponent"
        elif(option == 2):
            return "transition"
        else:
            return "Error getting function option"
            
    def get_periodic_option(option):
        if(option == 0):
            return "one"
        elif(option == 1):
            return "zero"
        elif(option == 2):
            return "cosine"
        elif(option == 3):
            return "cosine [variable period]"
        elif(option == 4):
            return "diagonal wave"
        elif(option == 5):
            return "diagonal wave [variable period]"
        elif(option == 6):
            return "slide"
        elif(option == 7):
            return "slide [variable period]"
        elif(option == 8):
            return "noise"        
        elif(option == 9):
            return "jitter"
        elif(option == 10):
            return "wander"
        elif(option == 11):
            return "spark"
        else:
            return "Error getting periodic option"        

    def get_transition_option(option):
        if(option == 0):
            return "linear"
        elif(option == 1):
            return "early"
        elif(option == 2):
            return "very early"
        elif(option == 3):
            return "late"
        elif(option == 4):
            return "very late"
        elif(option == 5):
            return "cosine"
        elif(option == 6):
            return "one"
        elif(option == 7):
            return "zero"
        else:
            return "Error getting transition option"


    def get_blending_option(option):
        if(option == 0):
            return "morph"
        elif(option == 1):
            return "dynamic morph"
        else:
            return "Error getting Blending Option"

    def get_environment_map_terr_option(option):
        if(option == 0):
            return "none"
        elif(option == 1):
            return "per_pixel"
        elif(option == 2):
            return "dynamic"    
        return "Error getting Environment Map Terr Option"

    def get_material_0_option(option):
        if(option == 0):
            return "diffuse_only"
        elif(option == 1):
            return "diffuse_plus_specular"
        elif(option == 2):
            return "off"
        elif(option == 3):
            return "diffuse_only_plus_self_illum"
        elif(option == 4):
            return "diffuse_plus_specular_plus_self_illum"
        elif(option == 5):
            return "diffuse_plus_specular_plus_heightmap"
        elif(option == 6):
            return "diffuse_plus_two_detail"
        elif(option == 7):
            return "diffuse_plus_specular_plus_up_vector_plus_heightmap"
        else:
            return "Error getting Material_0 option"

    def get_material_1_option(option):
        if(option == 0):
            return "diffuse_only"
        elif(option == 1):
            return "diffuse_plus_specular"
        elif(option == 2):
            return "off"
        elif(option == 3):
            return "diffuse_only_plus_self_illum"
        elif(option == 4):
            return "diffuse_plus_specular_plus_self_illum"
        elif(option == 5):
            return "diffuse_plus_specular_plus_heightmap"
        elif(option == 6):
            return "diffuse_plus_two_detail"
        elif(option == 7):
            return "diffuse_plus_specular_plus_up_vector_plus_heightmap"
        else:
            return "Error getting Material_1 option"

    def get_material_2_option(option):
        if(option == 0):
            return "diffuse_only"
        elif(option == 1):
            return "diffuse_plus_specular"
        elif(option == 2):
            return "off"
        elif(option == 3):
            return "diffuse_only_plus_self_illum"
        elif(option == 4):
            return "diffuse_plus_specular_plus_self_illum"
        else:
            return "Error getting Material_2 option"

    def get_material_3_option(option):
        if(option == 0):
            return "off"
        elif(option == 1):
            return "diffuse_only_(four_material_shaders_disable_detail_bump)"
        elif(option == 2):
            return "diffuse__plus_specular_(four_material_shaders_disable_detail_bump)"
        else:
            return "Error getting Material_3 option"


            
    def get_warp_option(option):
        if (option == 0):
            return "none"
        elif (option == 1):
            return "from_texture" 
        elif (option == 2):
            return "parallax_simple" 
        else:
            return "ERROR"        
            
    def get_overlay_option(option):
        if (option == 0):
            return "none"
        elif (option == 1):
            return "additive" 
        elif (option == 2):
            return "additive_detail" 
        elif (option == 3):
            return "multiply" 
        elif (option == 4):
            return "multiply_and_additive_detail" 
        else:
            return "ERROR"        
            
    def get_edge_fade_option(option):
        if (option == 0):
            return "none"
        elif (option == 1):
            return "simple" 
        else:
            return "ERROR"

    def get_distortion_option(option):
        if (option == 0):
            return "off"
        elif (option == 1):
            return "on" 
        else:
            return "ERROR"
      
    def get_soft_fade_option(option):
        if (option == 0):
            return "off"
        elif (option == 1):
            return "on" 
        else:
            return "ERROR"
      

    def uses_gray_50(type):
        if (type == "base_map"):
            return True
        elif (type == "change_color_map"):
            return True
        elif (type == "secondary_color_map"):
            return True
        elif (type == "base_masked_map"):
            return True
        elif (type == "custom_cube"):
            return True
        elif (type == "blend_map"):
            return True
        elif (type == "color_blend_mask_cubemap"):
            return True
        elif (type == "color_cubemap"):
            return True
        elif (type == "color_texture"):
            return True
        elif (type == "material_model"):
            return True
        elif (type == "material_texture"):
            return True
        elif (type == "custom_cube"):
            return True
        elif (type == "spec_tint_map"):
            return True
        elif (type == "spec_blend_map"):
            return True
        elif (type == "normal_specular_tint_map"):
            return True
        elif (type == "glancing_specular_tint_map"):
            return True
        elif (type == "tint_blend_mask_cubemap"):
            return True
        elif (type == "spec_tint_cubemap"):
            return True
        elif (type == "self_illum_map"):
            return True
        elif (type == "noise_map_a"):
            return True
        elif (type == "noise_map_b"):
            return True
        elif (type == "height_map"):
            return True
        elif (type == "height_scale_map"):
            return True
        elif (type == "base_map_m_0"):
            return True
        elif (type == "base_map_m_1"):
            return True
        elif (type == "base_map_m_2"):
            return True
        elif (type == "base_map_m_3"):
            return True
        else:
            return False
            
    def uses_default_detail(type):
        if (type == "detail_map"):
            return True
        elif (type == "detail_map2"):
            return True
        elif (type == "detail_map3"):
            return True
        elif (type == "detail_map_overlay"):
            return True
        elif (type == "self_illum_detail_map"):
            return True
        elif (type == "detail_map_m_0"):
            return True
        elif (type == "detail_map_m_1"):
            return True
        elif (type == "detail_map_m_2"):
            return True
        elif (type == "detail_map_m_3"):
            return True
        else:
            return False
            
    def uses_default_vector(type):
        if (type == "bump_map"):
            return True
        elif (type == "bump_detail_map"):
            return True
        elif (type == "bump_detail_masked_map"):
            return True
        elif (type == "distort_map"):
            return True
        elif (type == "bump_map_m_0"):
            return True
        elif (type == "detail_bump_m_0"):
            return True
        elif (type == "bump_map_m_1"):
            return True
        elif (type == "detail_bump_m_1"):
            return True
        elif (type == "bump_map_m_2"):
            return True
        elif (type == "detail_bump_m_2"):
            return True
        elif (type == "bump_map_m_3"):
            return True  
        elif (type == "detail_bump_m_3"):
            return True
        else:
            return False
            
    def uses_color_white(type):
        if (type == "chameleon_mask_map"):
            return True
        elif (type == "bump_map_mask_map"):
            return True
        elif (type == "specular_mask_map"):
            return True
        elif (type == "specular_map"):
            return True
        elif (type == "occlusion_parameter_map"):
            return True
        elif (type == "subsurface_map"):
            return True
        elif (type == "transparence_map"):
            return True
        else:
            return False
          
  
    def uses_reference_grids(type):
        if (type == "color_mask_map"):
            return True
        else:
            return False
            
    def uses_default_alpha_test(type):
        if (type == "alpha_test_map"):
            return True
        else:
            return False        

    def uses_default_dynamic_cube_map(type):
        if (type == "environment_map"):
            return True
        else:
            return False         
            
    def uses_color_red(type):
        if (type == "flat_environment_map"):
            return True
        else:
            return False          

    def uses_monochrome_alpha_grid(type):
        if (type == "meter_map"):
            return True
        else:
            return False         

    # def TextureNameEdit(ImageTexNode, BitmapType):
        # ImageTexNode.name = "[" + BitmapType + "]  " + ImageTexNode.name
        # return ImageTexNode


    def is_texture_needed(ShaderItem, texture_type):
        log_to_file("Checking if " + texture_type + " is needed")
        if texture_type in ShaderItem.needed_bitmaps:
            return True
        else:
            return False

    def correct_default_dir(bitmap_type):
        default_dir = ""
        
        if(uses_gray_50(bitmap_type) == True):
            default_dir = "shaders/default_bitmaps/bitmaps/gray_50_percent"
        elif(uses_color_white(bitmap_type) == True):
            default_dir = "shaders/default_bitmaps/bitmaps/color_white"
        elif(uses_default_vector(bitmap_type) == True):
            default_dir = "shaders/default_bitmaps/bitmaps/default_vector"
        elif(uses_reference_grids(bitmap_type) == True):    
            default_dir = "shaders/default_bitmaps/bitmaps/reference_grids"
        elif(uses_default_alpha_test(bitmap_type) == True):    
            default_dir = "shaders/default_bitmaps/bitmaps/default_alpha_test"
        elif(uses_default_dynamic_cube_map(bitmap_type) == True):    
            default_dir =  "shaders/default_bitmaps/bitmaps/default_dynamic_cube_map"
        elif(uses_color_red(bitmap_type) == True):    
            default_dir = "shaders/default_bitmaps/bitmaps/color_red"
        elif(uses_monochrome_alpha_grid(bitmap_type) == True):    
            default_dir = "shaders/default_bitmaps/bitmaps/monochrome_alpha_grid"
        else:
            default_dir = "shaders/default_bitmaps/bitmaps/default_detail"
        
        return default_dir

    #function to check if certain NodeGroup has what it needs for default textures
    def build_texture_list(ShaderItem, Shader_Type):
        #check needed bitmaps for the used categories
    
        ShaderItem.needed_bitmaps = []

        

    ########################################
    #.shader files and .shader_foliage files
    ########################################

        if(Shader_Type == 0 or Shader_Type == 2):
        #albedo options
            if(ShaderItem.albedo_option == 0): #H3RCategory: albedo - default 
                ShaderItem.needed_bitmaps.append("base_map")
                ShaderItem.needed_bitmaps.append("detail_map")
            elif(ShaderItem.albedo_option == 1): #H3Category: albedo - detail_blend
                ShaderItem.needed_bitmaps.append("base_map")
                ShaderItem.needed_bitmaps.append("detail_map")
                ShaderItem.needed_bitmaps.append("detail_map2")
            elif(ShaderItem.albedo_option == 2): #H3RCategory: albedo - constant_color
                log_to_file("constant color doesn't need bitmaps")
            elif(ShaderItem.albedo_option == 3): #H3RCategory: albedo - two_change_color
                ShaderItem.needed_bitmaps.append("base_map")
                ShaderItem.needed_bitmaps.append("detail_map")
                ShaderItem.needed_bitmaps.append("change_color_map")
            elif(ShaderItem.albedo_option == 4): #H3RCategory: albedo - four_change_color
                ShaderItem.needed_bitmaps.append("base_map")
                ShaderItem.needed_bitmaps.append("detail_map")
                ShaderItem.needed_bitmaps.append("change_color_map")
            elif(ShaderItem.albedo_option == 5): #H3RCategory: albedo - three_detail_blend
                ShaderItem.needed_bitmaps.append("base_map")
                ShaderItem.needed_bitmaps.append("detail_map")
                ShaderItem.needed_bitmaps.append("detail_map2")
                ShaderItem.needed_bitmaps.append("detail_map3")
            elif(ShaderItem.albedo_option == 6): #H3RCategory: albedo - two_detail_overlay
                ShaderItem.needed_bitmaps.append("base_map")
                ShaderItem.needed_bitmaps.append("detail_map")
                ShaderItem.needed_bitmaps.append("detail_map2")
                ShaderItem.needed_bitmaps.append("detail_map_overlay")
            elif(ShaderItem.albedo_option == 7): #H3RCategory: albedo - two_detail
                ShaderItem.needed_bitmaps.append("base_map")
                ShaderItem.needed_bitmaps.append("detail_map")
                ShaderItem.needed_bitmaps.append("detail_map2")
            elif(ShaderItem.albedo_option == 8): #H3RCategory: albedo - color_mask    
                ShaderItem.needed_bitmaps.append("base_map")
                ShaderItem.needed_bitmaps.append("detail_map")
                ShaderItem.needed_bitmaps.append("color_mask_map")
            elif(ShaderItem.albedo_option == 9): #H3RCategory: albedo - two_detail_black_point    
                ShaderItem.needed_bitmaps.append("base_map")
                ShaderItem.needed_bitmaps.append("detail_map")
                ShaderItem.needed_bitmaps.append("detail_map2")
            elif(ShaderItem.albedo_option == 17): #H3Category: albedo - custom_cube
                ShaderItem.needed_bitmaps.append("base_map")
                ShaderItem.needed_bitmaps.append("custom_cube")
            elif(ShaderItem.albedo_option == 18): #H3Category: albedo - two_color
                ShaderItem.needed_bitmaps.append("base_map")
                ShaderItem.needed_bitmaps.append("blend_map")
            elif(ShaderItem.albedo_option == 21): #H3Category: albedo - scrolling_texture_uv
                ShaderItem.needed_bitmaps.append("base_map")
                ShaderItem.needed_bitmaps.append("color_texture")
            elif(ShaderItem.albedo_option == 22): #H3Category: albedo - texture_from_misc
                ShaderItem.needed_bitmaps.append("base_map")
                ShaderItem.needed_bitmaps.append("color_texture")
        #bump_map group
            if(ShaderItem.bump_mapping_option == 1): #H3RCategory: bump_mapping - standard
                ShaderItem.needed_bitmaps.append("bump_map")       
            if(ShaderItem.bump_mapping_option == 2): #H3Category: bump_mapping - detail
                ShaderItem.needed_bitmaps.append("bump_map")
                ShaderItem.needed_bitmaps.append("bump_detail_map")
            elif(ShaderItem.bump_mapping_option == 3): #H3Category: bump_mapping - detail_masked
                ShaderItem.needed_bitmaps.append("bump_map")
                ShaderItem.needed_bitmaps.append("bump_detail_map")
                ShaderItem.needed_bitmaps.append("bump_detail_mask_map")
            elif(ShaderItem.bump_mapping_option == 4): #H3Category: bump_mapping - detail_plus_detail_masked
                ShaderItem.needed_bitmaps.append("bump_map")
                ShaderItem.needed_bitmaps.append("bump_detail_map")
                ShaderItem.needed_bitmaps.append("bump_detail_mask_map")
                ShaderItem.needed_bitmaps.append("bump_detail_masked_map")
            #elif(ShaderItem.bump_mapping_option == 5): #H3Category: bump_mapping - detail_unorm
                #NodeGroup.inputs.get("bump_detail_coefficient").default_value = ShaderItem.bump_detail_coefficient            
            
        #environment map group    
            if(ShaderItem.environment_mapping_option == 1 or ShaderItem.environment_mapping_option == 1): #H3RCategory: environment_mapping - per_pixel
                ShaderItem.needed_bitmaps.append("environment_map")
            elif(ShaderItem.environment_mapping_option == 2 or ShaderItem.environment_mapping_option == 2): #H3RCategory: environment_mapping - dynamic
                log_to_file("dynamic env group needs no textures")
                
        #material model group        
            #if(ShaderItem.material_model_option == 0): #H3Category: material_model - diffuse_only
                #no values needed
            if(ShaderItem.material_model_option == 6): #H3Category: material_model - organism
                ShaderItem.needed_bitmaps.append("specular_map")
                ShaderItem.needed_bitmaps.append("occlusion_parameter_map")
                ShaderItem.needed_bitmaps.append("subsurface_map")
                ShaderItem.needed_bitmaps.append("transparence_map")
            #elif(ShaderItem.material_model_option == 2): #H3Category: material_model - two_lobe_phong
                          
            #elif(ShaderItem.material_model_option == 5): #H3Category: material_model - glass
                          
            #elif(ShaderItem.material_model_option == 7): #H3Category: material_model - single_lobe_phong
                
                    
        #self illum group
            if(ShaderItem.self_illumination_option == 1): #H3RCategory: self_illumination - simple
                ShaderItem.needed_bitmaps.append("self_illum_map")
            elif(ShaderItem.self_illumination_option == 2): #H3RCategory: self_illumination - 3_channel_self_illum
                ShaderItem.needed_bitmaps.append("self_illum_map")           
            elif(ShaderItem.self_illumination_option == 3): #H3Category: self_illumination - plasma
                ShaderItem.needed_bitmaps.append("noise_map_a")
                ShaderItem.needed_bitmaps.append("noise_map_b")
                ShaderItem.needed_bitmaps.append("alpha_mask_map")
            #elif(ShaderItem.self_illumination_option == 4): #H3RCategory: self_illumination - from_diffuse
                
            elif(ShaderItem.self_illumination_option == 5): #H3RCategory: self_illumination - illum_detail
                ShaderItem.needed_bitmaps.append("self_illum_map")
                ShaderItem.needed_bitmaps.append("self_illum_detail_map")
            elif(ShaderItem.self_illumination_option == 6): #H3RCategory: self_illumination - meter
                ShaderItem.needed_bitmaps.append("meter_map")
            elif(ShaderItem.self_illumination_option == 7): #H3RCategory: self_illumination - self_illum_times_diffuse
                ShaderItem.needed_bitmaps.append("self_illum_map")
            elif(ShaderItem.self_illumination_option == 8): #H3RCategory: self_illumination - simple_with_alpha_mask    
                ShaderItem.needed_bitmaps.append("self_illum_map")
            elif(ShaderItem.self_illumination_option == 11): #H3RCategory: self_illumination - simple_with_alpha_mask    
                ShaderItem.needed_bitmaps.append("self_illum_map")
               
        
            
        ##############    
        #terrain group
        ##############
        
        if(Shader_Type == 1):
            ShaderItem.needed_bitmaps.append("blend_map")
            
            ShaderItem.needed_bitmaps.append("base_map_m_0")
            ShaderItem.needed_bitmaps.append("detail_map_m_0")
            ShaderItem.needed_bitmaps.append("bump_map_m_0")
            ShaderItem.needed_bitmaps.append("detail_bump_m_0")
            
            ShaderItem.needed_bitmaps.append("base_map_m_1")
            ShaderItem.needed_bitmaps.append("detail_map_m_1")
            ShaderItem.needed_bitmaps.append("bump_map_m_1")
            ShaderItem.needed_bitmaps.append("detail_bump_m_1")
            
            ShaderItem.needed_bitmaps.append("base_map_m_2")
            ShaderItem.needed_bitmaps.append("detail_map_m_2")
            ShaderItem.needed_bitmaps.append("bump_map_m_2")
            ShaderItem.needed_bitmaps.append("detail_bump_m_2")

            ShaderItem.needed_bitmaps.append("base_map_m_3")
            ShaderItem.needed_bitmaps.append("detail_map_m_3")
            ShaderItem.needed_bitmaps.append("bump_map_m_3")
            ShaderItem.needed_bitmaps.append("detail_bump_m_3")
        


        #######################
        #.shader_halogram files
        #######################

        if(Shader_Type == 3):        
            if(ShaderItem.self_illumination_option == 8): #H3Category: self_illumination - multilayer_additive
                #add these in later
                log_to_file("self_illumination - multilayer_additive")
            elif(ShaderItem.self_illumination_option == 9): #H3Category: self_illumination - scope_blur
                #add these in later
                log_to_file("self_illumination - scope_blur")
            elif(ShaderItem.self_illumination_option == 10): #H3Category: self_illumination - ml_add_four_change_color
                #add these in later
                log_to_file("self_illumination - ml_add_four_change_color")
            elif(ShaderItem.self_illumination_option == 11): #H3Category: self_illumination - ml_add_five_change_color
                #add these in later
                log_to_file("self_illumination - ml_add_five_change_color")
            elif(ShaderItem.self_illumination_option == 12): #H3Category: self_illumination - plasma_wide_and_sharp_five_change_color
                #add these in later
                log_to_file("self_illumination - plasma_wide_and_sharp_five_change_color")
            elif(ShaderItem.self_illumination_option == 13): #H3Category: self_illumination - self_illum_holograms
                #add these in later
                log_to_file("self_illumination - self_illum_holograms")
        
        return ShaderItem


    #Apply values from ShaderItem to Shader 
    def apply_group_values(NodeGroup, ShaderItem, category):
        
        #name of the shader node group sent in
        Node_Name = NodeGroup.node_tree.name
        
        log_to_file(Node_Name)
        
        input_list = []
        
        # Iterate through the node group's inputs
        for input in NodeGroup.inputs:
            # Check if the input type is VALUE or RGBA, you can add other conditions here as well
            if (input.type == 'VALUE' or input.type == 'RGBA') and not input.hide_value and "Gamma Curve" not in input.name and "primary_change_color" not in input.name and "secondary_change_color" not in input.name and "tertiary_change_color" not in input.name and "quaternary_change_color" not in input.name and "Location" not in input.name and "Scale" not in input.name:
                input_list.append(input.name)

        # You can now iterate through this list and set the values as required
        for index, input_name in enumerate(input_list):
            log_to_file("Applying value from ShaderItem." + input_name)
            NodeGroup.inputs.get(input_name).default_value = getattr(ShaderItem, input_name)
        
        # #albedo/base_map group
        # if(category == "albedo"):
            # if(Node_Name == "H3RCategory: albedo - default"): #H3RCategory: albedo - default 
                # NodeGroup.inputs.get("albedo_color").default_value = ShaderItem.albedo_color
                # NodeGroup.inputs.get("albedo_color_alpha").default_value = ShaderItem.albedo_color_alpha
            # #elif(ShaderItem.albedo_option == 1): #H3Category: albedo - detail_blend
                # #no values needed?
            # elif(Node_Name == "H3RCategory: albedo - constant_color"): #H3RCategory: albedo - constant_color
                # NodeGroup.inputs.get("albedo_color").default_value = ShaderItem.albedo_color
                # NodeGroup.inputs.get("albedo_color_alpha").default_value = ShaderItem.albedo_color_alpha
            # #elif(ShaderItem.albedo_option == 3): #H3RCategory: albedo - two_change_color
                # #no values needed?
            # #elif(ShaderItem.albedo_option == 4): #H3RCategory: albedo - four_change_color
                # #no values needed?
            # #elif(ShaderItem.albedo_option == 5): #H3RCategory: albedo - three_detail_blend
                # #no values needed?
            # #elif(ShaderItem.albedo_option == 6): #H3RCategory: albedo - two_detail_overlay
                # #no values needed?     
            # #elif(ShaderItem.albedo_option == 7): #H3RCategory: albedo - two_detail
                # #no values needed?
            # elif(Node_Name == "H3RCategory: albedo - color_mask"): #H3RCategory: albedo - color_mask
                # NodeGroup.inputs.get("albedo_color").default_value = ShaderItem.albedo_color
                # NodeGroup.inputs.get("albedo_color_alpha").default_value = ShaderItem.albedo_color_alpha
                # NodeGroup.inputs.get("albedo_color2").default_value = ShaderItem.albedo_color2
                # NodeGroup.inputs.get("albedo_color2_alpha").default_value = ShaderItem.albedo_color2_alpha
                # NodeGroup.inputs.get("albedo_color3").default_value = ShaderItem.albedo_color3
                # NodeGroup.inputs.get("albedo_color3_alpha").default_value = ShaderItem.albedo_color3_alpha
                
        # #bump_map group
        # elif(category == "bump"):
            # #if(ShaderItem.bump_mapping_option == 1): #H3RCategory: bump_mapping - standard
                # #no values needed?        
            # if(Node_Name == "H3Category: bump_mapping - detail"): #H3Category: bump_mapping - detail
                # NodeGroup.inputs.get("bump_detail_coefficient").default_value = ShaderItem.bump_detail_coefficient
            # elif(Node_Name == "H3Category: bump_mapping - detail_masked"): #H3Category: bump_mapping - detail_masked
                # NodeGroup.inputs.get("bump_detail_coefficient").default_value = ShaderItem.bump_detail_coefficient
                # #invert_mask?
            # elif(Node_Name == "H3Category: bump_mapping - detail_plus_detail_masked"): #H3Category: bump_mapping - detail_plus_detail_masked
                # NodeGroup.inputs.get("bump_detail_coefficient").default_value = ShaderItem.bump_detail_coefficient
                # #bump_detail_masked_coefficient  
            # #elif(ShaderItem.bump_mapping_option == 5): #H3Category: bump_mapping - detail_unorm
                # #NodeGroup.inputs.get("bump_detail_coefficient").default_value = ShaderItem.bump_detail_coefficient            
            
        # #environment map group    
        # elif(category == "env map"):
            # if(Node_Name == "H3RCategory: environment_mapping - per_pixel"): #H3RCategory: environment_mapping - per_pixel
                # NodeGroup.inputs.get("env_tint_color").default_value = ShaderItem.env_tint_color
            # elif(Node_Name == "H3RCategory: environment_mapping - dynamic"): #H3RCategory: environment_mapping - dynamic
                # NodeGroup.inputs.get("env_tint_color").default_value = ShaderItem.env_tint_color        
                # NodeGroup.inputs.get("env_roughness_scale").default_value = ShaderItem.env_roughness_scale  
                
        # #material model group    
        # elif(category == "mat model"):    
            # #if(ShaderItem.material_model_option == 0): #H3Category: material_model - diffuse_only
                # #no values needed
            # if(Node_Name == "H3Category: material_model - cook_torrance"): #H3Category: material_model - cook_torrance
                # NodeGroup.inputs.get("diffuse_coefficient").default_value = ShaderItem.diffuse_coefficient
                # NodeGroup.inputs.get("specular_coefficient").default_value = ShaderItem.specular_coefficient
                # NodeGroup.inputs.get("specular_tint").default_value = ShaderItem.specular_tint
                # NodeGroup.inputs.get("fresnel_color").default_value = ShaderItem.fresnel_color
                # NodeGroup.inputs.get("roughness").default_value = ShaderItem.roughness
                # NodeGroup.inputs.get("environment_map_specular_contribution").default_value = ShaderItem.environment_map_specular_contribution
                # NodeGroup.inputs.get("use_material_texture").default_value = ShaderItem.use_material_texture
                # NodeGroup.inputs.get("albedo_blend").default_value = ShaderItem.albedo_blend            
                # NodeGroup.inputs.get("analytical_specular_contribution").default_value = ShaderItem.analytical_specular_contribution
                # NodeGroup.inputs.get("area_specular_contribution").default_value = ShaderItem.area_specular_contribution
            # elif(Node_Name == "H3Category: material_model - two_lobe_phong"): #H3Category: material_model - two_lobe_phong
                # NodeGroup.inputs.get("diffuse_coefficient").default_value = ShaderItem.diffuse_coefficient   
                # NodeGroup.inputs.get("specular_coefficient").default_value = ShaderItem.specular_coefficient
                # NodeGroup.inputs.get("normal_specular_power").default_value = ShaderItem.normal_specular_power
                # NodeGroup.inputs.get("normal_specular_tint").default_value = ShaderItem.normal_specular_tint
                # NodeGroup.inputs.get("glancing_specular_power").default_value = ShaderItem.glancing_specular_power
                # NodeGroup.inputs.get("glancing_specular_tint").default_value = ShaderItem.glancing_specular_tint
                # NodeGroup.inputs.get("fresnel_curve_steepness").default_value = ShaderItem.fresnel_curve_steepness
                # NodeGroup.inputs.get("area_specular_contribution").default_value = ShaderItem.area_specular_contribution
                # NodeGroup.inputs.get("environment_map_specular_contribution").default_value = ShaderItem.environment_map_specular_contribution
                # NodeGroup.inputs.get("albedo_specular_tint_blend").default_value = ShaderItem.albedo_specular_tint_blend   
                # NodeGroup.inputs.get("analytical_specular_contribution").default_value = ShaderItem.analytical_specular_contribution            
            # elif(Node_Name == "H3Category: material_model - glass"): #H3Category: material_model - glass
                # NodeGroup.inputs.get("diffuse_coefficient").default_value = ShaderItem.diffuse_coefficient   
                # NodeGroup.inputs.get("specular_coefficient").default_value = ShaderItem.specular_coefficient
                # NodeGroup.inputs.get("roughness").default_value = ShaderItem.roughness
                # NodeGroup.inputs.get("fresnel_coefficient").default_value = ShaderItem.fresnel_coefficient              
                # NodeGroup.inputs.get("fresnel_curve_steepness").default_value = ShaderItem.fresnel_curve_steepness
                # NodeGroup.inputs.get("area_specular_contribution").default_value = ShaderItem.area_specular_contribution                
                # NodeGroup.inputs.get("fresnel_curve_bias").default_value = ShaderItem.fresnel_curve_bias                
                # NodeGroup.inputs.get("analytical_specular_contribution").default_value = ShaderItem.analytical_specular_contribution            
            # elif(Node_Name == "H3Category: material_model - single_lobe_phong"): #H3Category: material_model - single_lobe_phong
                # NodeGroup.inputs.get("diffuse_coefficient").default_value = ShaderItem.diffuse_coefficient
                # NodeGroup.inputs.get("specular_coefficient").default_value = ShaderItem.specular_coefficient        
                # NodeGroup.inputs.get("specular_tint").default_value = ShaderItem.specular_tint    
                # NodeGroup.inputs.get("roughness").default_value = ShaderItem.roughness            
                # NodeGroup.inputs.get("environment_map_specular_contribution").default_value = ShaderItem.environment_map_specular_contribution
                # NodeGroup.inputs.get("area_specular_contribution").default_value = ShaderItem.area_specular_contribution  
                # NodeGroup.inputs.get("analytical_specular_contribution").default_value = ShaderItem.analytical_specular_contribution
                    
        # #self illum group
        # elif(category == "self illum"):
            # if(Node_Name == "H3RCategory: self_illumination - simple"): #H3RCategory: self_illumination - simple
                # NodeGroup.inputs.get("self_illum_color").default_value = ShaderItem.self_illum_color
                # NodeGroup.inputs.get("self_illum_intensity").default_value = ShaderItem.self_illum_intensity            
            # elif(Node_Name == "H3RCategory: self_illumination - 3_channel_self_illum"): #H3RCategory: self_illumination - 3_channel_self_illum
                # NodeGroup.inputs.get("channel_a").default_value = ShaderItem.channel_a
                # NodeGroup.inputs.get("channel_a_alpha").default_value = ShaderItem.channel_a_alpha
                # NodeGroup.inputs.get("channel_b").default_value = ShaderItem.channel_b
                # NodeGroup.inputs.get("channel_b_alpha").default_value = ShaderItem.channel_b_alpha
                # NodeGroup.inputs.get("channel_c").default_value = ShaderItem.channel_c
                # NodeGroup.inputs.get("channel_c_alpha").default_value = ShaderItem.channel_c_alpha            
            # elif(Node_Name == "H3Category: self_illumination - plasma"): #H3Category: self_illumination - plasma
                # NodeGroup.inputs.get("color_wide").default_value = ShaderItem.color_wide
                # NodeGroup.inputs.get("color_wide_alpha").default_value = ShaderItem.color_wide_alpha
                # NodeGroup.inputs.get("color_sharp").default_value = ShaderItem.color_sharp
                # NodeGroup.inputs.get("color_sharp_alpha").default_value = ShaderItem.color_sharp_alpha
                # NodeGroup.inputs.get("color_medium").default_value = ShaderItem.color_medium
                # NodeGroup.inputs.get("color_medium_alpha").default_value = ShaderItem.color_medium_alpha
                # NodeGroup.inputs.get("self_illum_intensity").default_value = ShaderItem.self_illum_intensity
                # NodeGroup.inputs.get("thinness_medium").default_value = ShaderItem.thinness_medium
                # NodeGroup.inputs.get("thinness_wide").default_value = ShaderItem.thinness_wide
                # NodeGroup.inputs.get("thinness_sharp").default_value = ShaderItem.thinness_sharp
            # elif(Node_Name == "H3RCategory: self_illumination - from_diffuse"): #H3RCategory: self_illumination - from_diffuse
                # NodeGroup.inputs.get("self_illum_color").default_value = ShaderItem.self_illum_color
                # NodeGroup.inputs.get("self_illum_intensity").default_value = ShaderItem.self_illum_intensity
            # elif(Node_Name == "H3RCategory: self_illumination - illum_detail"): #H3RCategory: self_illumination - illum_detail
                # NodeGroup.inputs.get("self_illum_color").default_value = ShaderItem.self_illum_color
                # NodeGroup.inputs.get("self_illum_intensity").default_value = ShaderItem.self_illum_intensity
            # elif(Node_Name == "H3RCategory: self_illumination - meter"): #H3RCategory: self_illumination - meter
                # NodeGroup.inputs.get("meter_color_off").default_value = ShaderItem.meter_color_off
                # NodeGroup.inputs.get("meter_color_on").default_value = ShaderItem.meter_color_on
                # NodeGroup.inputs.get("meter_value").default_value = ShaderItem.meter_value
            # elif(Node_Name == "H3RCategory: self_illumination - self_illum_times_diffuse"): #H3RCategory: self_illumination - self_illum_times_diffuse
                # NodeGroup.inputs.get("self_illum_color").default_value = ShaderItem.self_illum_color
                # NodeGroup.inputs.get("self_illum_intensity").default_value = ShaderItem.self_illum_intensity
                # NodeGroup.inputs.get("primary_change_color_blend").default_value = ShaderItem.primary_change_color_blend
            # # elif(Shader_Type == 3 and ShaderItem.self_illumination_option == 8): #H3Category: self_illumination - multilayer_additive
                # # #add these in later
                # # log_to_file("self_illumination - multilayer_additive")
            # # elif(Shader_Type == 3 and ShaderItem.self_illumination_option == 9): #H3Category: self_illumination - scope_blur
                # # #add these in later
                # # log_to_file("self_illumination - scope_blur")
            # # elif(Shader_Type == 3 and ShaderItem.self_illumination_option == 10): #H3Category: self_illumination - ml_add_four_change_color
                # # #add these in later
                # # log_to_file("self_illumination - ml_add_four_change_color")
            # elif(Node_Name == "H3Category: self_illumination - illum_change_color"): #H3Category: self_illumination - illum_change_color
                # NodeGroup.inputs.get("self_illum_intensity").default_value = ShaderItem.self_illum_intensity
                # NodeGroup.inputs.get("primary_change_color_blend").default_value = ShaderItem.primary_change_color_blend
                # #NodeGroup.inputs.get("primary_change_color").default_value = ShaderItem.primary_change_color
            # # elif(Shader_Type == 3 and ShaderItem.self_illumination_option == 12): #H3Category: self_illumination - plasma_wide_and_sharp_five_change_color
                # # #add these in later
                # # log_to_file("self_illumination - plasma_wide_and_sharp_five_change_color")
            # # elif(Shader_Type == 3 and ShaderItem.self_illumination_option == 13): #H3Category: self_illumination - self_illum_holograms
                # # #add these in later
                # # log_to_file("self_illumination - self_illum_holograms")
            
            
            
            
            
        # ##############    
        # #terrain group
        # ##############
        
        # #Halo3TerrainCategory - material - diffuse_only
        # #material 0
        # #elif(category == "terrain1_m0"):             
            # #no values for this group
        # #material 1
        # #elif(category == "terrain1_m1"):             
            # #no values for this group
        # #material 2
        # #elif(category == "terrain1_m2"):             
            # #no values for this group
        # #material 3
        # #elif(category == "terrain1_m3"):             
            # #no values for this group

        # #Halo3TerrainCategory - material - diffuse_plus_specular
        # #all materials
        # elif(category == "terrain"):
            # NodeGroup.inputs.get("diffuse_coefficient_m_0").default_value = ShaderItem.diffuse_coefficient_m_0
            # NodeGroup.inputs.get("specular_coefficient_m_0").default_value = ShaderItem.specular_coefficient_m_0
            # NodeGroup.inputs.get("specular_power_m_0").default_value = ShaderItem.specular_power_m_0
            # NodeGroup.inputs.get("specular_tint_m_0").default_value = ShaderItem.specular_tint_m_0
            # NodeGroup.inputs.get("analytical_specular_contribution_m_0").default_value = ShaderItem.analytical_specular_contribution_m_0
            # NodeGroup.inputs.get("area_specular_contribution_m_0").default_value = ShaderItem.area_specular_contribution_m_0
            # NodeGroup.inputs.get("fresnel_curve_steepness_m_0").default_value = ShaderItem.fresnel_curve_steepness_m_0
            # NodeGroup.inputs.get("environment_specular_contribution_m_0").default_value = ShaderItem.environment_specular_contribution_m_0
            # NodeGroup.inputs.get("albedo_specular_tint_blend_m_0").default_value = ShaderItem.albedo_specular_tint_blend_m_0
            # NodeGroup.inputs.get("diffuse_coefficient_m_1").default_value = ShaderItem.diffuse_coefficient_m_1
            # NodeGroup.inputs.get("specular_coefficient_m_1").default_value = ShaderItem.specular_coefficient_m_1
            # NodeGroup.inputs.get("specular_power_m_1").default_value = ShaderItem.specular_power_m_1
            # NodeGroup.inputs.get("specular_tint_m_1").default_value = ShaderItem.specular_tint_m_1
            # NodeGroup.inputs.get("analytical_specular_contribution_m_1").default_value = ShaderItem.analytical_specular_contribution_m_1
            # NodeGroup.inputs.get("area_specular_contribution_m_1").default_value = ShaderItem.area_specular_contribution_m_1
            # NodeGroup.inputs.get("fresnel_curve_steepness_m_1").default_value = ShaderItem.fresnel_curve_steepness_m_1
            # NodeGroup.inputs.get("environment_specular_contribution_m_1").default_value = ShaderItem.environment_specular_contribution_m_1
            # NodeGroup.inputs.get("albedo_specular_tint_blend_m_1").default_value = ShaderItem.albedo_specular_tint_blend_m_1    
            # NodeGroup.inputs.get("diffuse_coefficient_m_2").default_value = ShaderItem.diffuse_coefficient_m_2
            # NodeGroup.inputs.get("specular_coefficient_m_2").default_value = ShaderItem.specular_coefficient_m_2
            # NodeGroup.inputs.get("specular_power_m_2").default_value = ShaderItem.specular_power_m_2
            # NodeGroup.inputs.get("specular_tint_m_2").default_value = ShaderItem.specular_tint_m_2
            # NodeGroup.inputs.get("analytical_specular_contribution_m_2").default_value = ShaderItem.analytical_specular_contribution_m_2
            # NodeGroup.inputs.get("area_specular_contribution_m_2").default_value = ShaderItem.area_specular_contribution_m_2
            # NodeGroup.inputs.get("fresnel_curve_steepness_m_2").default_value = ShaderItem.fresnel_curve_steepness_m_2
            # NodeGroup.inputs.get("environment_specular_contribution_m_2").default_value = ShaderItem.environment_specular_contribution_m_2
            # NodeGroup.inputs.get("albedo_specular_tint_blend_m_2").default_value = ShaderItem.albedo_specular_tint_blend_m_2    
            # NodeGroup.inputs.get("diffuse_coefficient_m_3").default_value = ShaderItem.diffuse_coefficient_m_3
            # NodeGroup.inputs.get("specular_coefficient_m_3").default_value = ShaderItem.specular_coefficient_m_3
            # NodeGroup.inputs.get("specular_power_m_3").default_value = ShaderItem.specular_power_m_3
            # NodeGroup.inputs.get("specular_tint_m_3").default_value = ShaderItem.specular_tint_m_3
            # NodeGroup.inputs.get("analytical_specular_contribution_m_3").default_value = ShaderItem.analytical_specular_contribution_m_3
            # NodeGroup.inputs.get("area_specular_contribution_m_3").default_value = ShaderItem.area_specular_contribution_m_3
            # NodeGroup.inputs.get("fresnel_curve_steepness_m_3").default_value = ShaderItem.fresnel_curve_steepness_m_3
            # NodeGroup.inputs.get("environment_specular_contribution_m_3").default_value = ShaderItem.environment_specular_contribution_m_3
            # NodeGroup.inputs.get("albedo_specular_tint_blend_m_3").default_value = ShaderItem.albedo_specular_tint_blend_m_3

            # #disable certain values if materials are off or are certain values
            # if(ShaderItem.material_0_option == 0 or ShaderItem.material_0_option == 2 or ShaderItem.material_0_option == 3): #if off or diffuse only
                # NodeGroup.inputs.get("specular_coefficient_m_0").default_value = 0.00
            # elif(ShaderItem.material_1_option == 0 or ShaderItem.material_1_option == 2 or ShaderItem.material_1_option == 3): #if off or diffuse only
                # NodeGroup.inputs.get("specular_coefficient_m_1").default_value = 0.00            
            # elif(ShaderItem.material_2_option == 0 or ShaderItem.material_2_option == 2 or ShaderItem.material_2_option == 3): #if off or diffuse only
                # NodeGroup.inputs.get("specular_coefficient_m_2").default_value = 0.00
            # elif(ShaderItem.material_3_option == 0 or ShaderItem.material_3_option == 1): #if off or diffuse only
                # NodeGroup.inputs.get("specular_coefficient_m_3").default_value = 0.00


        
        # elif(category == "terrain2_m0"): 
            # #log_to_file("applying values to m0")
            # NodeGroup.inputs.get("diffuse_coefficient").default_value = ShaderItem.diffuse_coefficient_m_0
            # NodeGroup.inputs.get("specular_coefficient").default_value = ShaderItem.specular_coefficient_m_0
            # NodeGroup.inputs.get("specular_power").default_value = ShaderItem.specular_power_m_0
            # NodeGroup.inputs.get("specular_tint").default_value = ShaderItem.specular_tint_m_0
            # NodeGroup.inputs.get("analytical_specular_contribution").default_value = ShaderItem.analytical_specular_contribution_m_0
            # NodeGroup.inputs.get("fresnel_curve_steepness").default_value = ShaderItem.fresnel_curve_steepness_m_0
            # NodeGroup.inputs.get("environment_specular_contribution").default_value = ShaderItem.environment_specular_contribution_m_0
            # NodeGroup.inputs.get("albedo_specular_tint_blend").default_value = ShaderItem.albedo_specular_tint_blend_m_0
        # #material 1
        # elif(category == "terrain2_m1"):   
            # #log_to_file("applying values to m1")
            # NodeGroup.inputs.get("diffuse_coefficient").default_value = ShaderItem.diffuse_coefficient_m_1
            # NodeGroup.inputs.get("specular_coefficient").default_value = ShaderItem.specular_coefficient_m_1
            # NodeGroup.inputs.get("specular_power").default_value = ShaderItem.specular_power_m_1
            # NodeGroup.inputs.get("specular_tint").default_value = ShaderItem.specular_tint_m_1
            # NodeGroup.inputs.get("analytical_specular_contribution").default_value = ShaderItem.analytical_specular_contribution_m_1
            # NodeGroup.inputs.get("fresnel_curve_steepness").default_value = ShaderItem.fresnel_curve_steepness_m_1
            # NodeGroup.inputs.get("environment_specular_contribution").default_value = ShaderItem.environment_specular_contribution_m_1
            # NodeGroup.inputs.get("albedo_specular_tint_blend").default_value = ShaderItem.albedo_specular_tint_blend_m_1    
        # #material 2
        # elif(category == "terrain2_m2"):      
            # #log_to_file("applying values to m2")    
            # NodeGroup.inputs.get("diffuse_coefficient").default_value = ShaderItem.diffuse_coefficient_m_2
            # NodeGroup.inputs.get("specular_coefficient").default_value = ShaderItem.specular_coefficient_m_2
            # NodeGroup.inputs.get("specular_power").default_value = ShaderItem.specular_power_m_2
            # NodeGroup.inputs.get("specular_tint").default_value = ShaderItem.specular_tint_m_2
            # NodeGroup.inputs.get("analytical_specular_contribution").default_value = ShaderItem.analytical_specular_contribution_m_2
            # NodeGroup.inputs.get("fresnel_curve_steepness").default_value = ShaderItem.fresnel_curve_steepness_m_2
            # NodeGroup.inputs.get("environment_specular_contribution").default_value = ShaderItem.environment_specular_contribution_m_2
            # NodeGroup.inputs.get("albedo_specular_tint_blend").default_value = ShaderItem.albedo_specular_tint_blend_m_2
        # #material 3
        # elif(category == "terrain2_m3"):  
            # #log_to_file("applying values to m3")    
            # NodeGroup.inputs.get("diffuse_coefficient").default_value = ShaderItem.diffuse_coefficient_m_3
            # NodeGroup.inputs.get("specular_coefficient").default_value = ShaderItem.specular_coefficient_m_3
            # NodeGroup.inputs.get("specular_power").default_value = ShaderItem.specular_power_m_3
            # NodeGroup.inputs.get("specular_tint").default_value = ShaderItem.specular_tint_m_3
            # NodeGroup.inputs.get("analytical_specular_contribution").default_value = ShaderItem.analytical_specular_contribution_m_3
            # NodeGroup.inputs.get("fresnel_curve_steepness").default_value = ShaderItem.fresnel_curve_steepness_m_3
            # NodeGroup.inputs.get("environment_specular_contribution").default_value = ShaderItem.environment_specular_contribution_m_3
            # NodeGroup.inputs.get("albedo_specular_tint_blend").default_value = ShaderItem.albedo_specular_tint_blend_m_3
            
        return NodeGroup
    
       




    #MERGE DUPLICATE MATERIAL NAMES
    def merge_materials_on_objects(objects, materials):
        # Sort materials by name
        materials_sorted = sorted(materials, key=lambda m: m.name)

        # Find materials with the same name and merge them
        for obj in objects:
            material_slots = [slot for slot in obj.material_slots if slot.material is not None and not slot.is_property_readonly('material')]
            for slot in material_slots:
                material = slot.material
                material_name = material.name[:-4] if re.match('.*.\d{3}$', material.name) else material.name
                material_name_escaped = re.escape(material_name)
                material_cond = re.compile('^' + material_name_escaped + '$|^' + material_name_escaped + '.\d{3}$')
                material_to_change = next(iter([m for m in materials_sorted if re.match(material_cond, m.name)]), None)
                if material_to_change and material != material_to_change:
                    slot.material = material_to_change
                    

    merge_materials_on_objects(bpy.data.objects, bpy.data.materials)

                                        #################
                                        #START OF PROGRAM 
                                        #################    
    #get material count for the progress bar
    total_mats = len(bpy.data.materials)
    

    #mat = bpy.data.materials[999]                                    
                                        
    pymat = bpy.data.materials
    #log_to_file("---MATERIALS LIST---" + str(bpy.data.materials))
    
    for idx, i in enumerate(pymat):
        mat_name = ""
        
        
        #get material count for the progress bar and keep the count current
        total_mats = len(bpy.data.materials)
        
        #reset has_prefix and prefix
        has_prefix = False
        prefix = ""
        
        #reset the Tag_Root each pass
        if(bpy.context.scene.tag_dropdown == "Halo 3"):
            #log_to_file("Using Halo 3 Tags")
            Tag_Root = bpy.context.preferences.addons[__name__].preferences.halo3_tag_path 
            Raw_Tag_Root = bpy.context.preferences.addons[__name__].preferences.halo3_tag_path
            #log_to_file("halo3_tag_path: " + bpy.context.preferences.addons[__name__].preferences.halo3_tag_path)
        elif (bpy.context.scene.tag_dropdown == "Halo 3: ODST"):
            #log_to_file("Using Halo 3: ODST Tags")
            #log_to_file("odst_tag_path: " + bpy.context.preferences.addons[__name__].preferences.odst_tag_path)
            Tag_Root = bpy.context.preferences.addons[__name__].preferences.odst_tag_path
            Raw_Tag_Root = bpy.context.preferences.addons[__name__].preferences.odst_tag_path
        elif (bpy.context.scene.tag_dropdown == "Halo Reach"):
            #log_to_file("Using Halo Reach Tags")
            #log_to_file("reach_tag_path: " + bpy.context.preferences.addons[__name__].preferences.reach_tag_path)
            Tag_Root = bpy.context.preferences.addons[__name__].preferences.reach_tag_path
            Raw_Tag_Root = bpy.context.preferences.addons[__name__].preferences.reach_tag_path
        else:
            log_to_file("Error with Tag option property")
        

        Game_Source = ""
        
        if(bpy.context.scene.tag_dropdown == "Halo 3"):
            Game_Source = "H3"
        elif (bpy.context.scene.tag_dropdown == "Halo 3: ODST"):
            Game_Source = "H3ODST"
        elif (bpy.context.scene.tag_dropdown == "Halo Reach"):
            Game_Source = "Reach"
        else:
            log_to_file("Error with dropdown option property")


        
        #try to handle any prefixes (from using mod tools to rip .ass files)
        split_i = i.name.split(' ', 1)
        log_to_file(split_i)
        #mat_name = split_i;
        
        if len(split_i) > 1:
            mat_name = split_i[1]
            prefix = split_i[0] #store the prefix for the current material name
            
            #handles random prefixes that aren't in the library
            if (Game_Source == "H3" and get_prefix_dir_h3(prefix) != "error"):
                has_prefix = True
            elif (Game_Source == "H3ODST" and get_prefix_dir_h3odst(prefix) != "error"):
                has_prefix = True
            elif (Game_Source == "Reach" and get_prefix_dir_reach(prefix) != "error"):
                has_prefix = True
            else:
                log_to_file("-Error has occured with prefix of Material that is not hardcoded to be handled. Likely a Blender value or custom material created by user.");
            
            if has_prefix == True:
                split_mat_name = mat_name.split(' ', 1);
                
                #tests to see if there is a suffix
                if len(split_mat_name) > 1:
                    mat_name = split_mat_name[0];
        else:
            # Handle the case where the delimiter isn't found in the string
            mat_name = i.name
        
        #try to ignore symbols like ! and %
        symbols_to_remove = "%#?!@*$^-&=.;)><|~({}['] "  #removed 0 from the list
        mat_name = mat_name.rstrip(symbols_to_remove);
        
        
        ShaderName = mat_name + ".shader"                          # Shader_Type = 0
        ShaderName_Terrain_Shader = mat_name + ".shader_terrain"   # Shader_Type = 1
        ShaderName_Foliage_Shader = mat_name + ".shader_foliage"   # Shader_Type = 2
        ShaderName_Halogram_Shader = mat_name + ".shader_halogram" # Shader_Type = 3
        ShaderName_Custom_Shader = mat_name + ".shader_custom"     # Shader_Type = 4
        ShaderName_Black_Shader = mat_name + ".shader_black"       # Shader_Type = 5
        ShaderName_Decal_Shader = mat_name + ".shader_decal"       # Shader_Type = 6
        ShaderPath = ""
        ShaderItem = shader() 
        Shader_Type = 0   #resets Shader_Type back to 0
        
        
        #Try to handle multiple shader files of the same name
        file_found = False
        
        pymat_copy = i
       
        

            
        #edit tag_root per each prefix found
        if has_prefix == True:
            log_to_file("PREFIX FOUND-----------------------------------------------------------------");
            log_to_file("Prefix = " + prefix);
            if Game_Source == "H3":
                Tag_Root = Tag_Root + "/" + get_prefix_dir_h3(prefix);
            elif Game_Source == "H3ODST":
                Tag_Root = Tag_Root + "/" + get_prefix_dir_h3odst(prefix);
            elif Game_Source == "Reach":
                Tag_Root = Tag_Root + "/" + get_prefix_dir_reach(prefix);

        log_to_file("Tag Root: " + Tag_Root)
        log_to_file("prefix: " + prefix)
        log_to_file("mat_name: " + mat_name)

            
        #find shader files and deal with each one
        for root, dirs, files in os.walk(Tag_Root):
            if (ShaderName_Terrain_Shader in files):
                ShaderName = ShaderName_Terrain_Shader
                Shader_Type = 1
                log_to_file("Terrain Shader Found!")
            elif (ShaderName_Foliage_Shader in files):
                ShaderName = ShaderName_Foliage_Shader
                Shader_Type = 2
                log_to_file("Foliage Shader Found!")
            # elif (ShaderName_Halogram_Shader in files):
                # ShaderName = ShaderName_Halogram_Shader
                # Shader_Type = 3
                # log_to_file("Halogram Shader Found!")
            elif (ShaderName_Custom_Shader in files):
                ShaderName = ShaderName_Custom_Shader
                Shader_Type = 4
                log_to_file("Custom Shader Found!")
            elif (ShaderName_Black_Shader in files):
                ShaderName = ShaderName_Black_Shader
                Shader_Type = 5
                log_to_file("Black Shader Found!")
            elif (ShaderName_Decal_Shader in files):
                ShaderName = ShaderName_Decal_Shader
                Shader_Type = 6
                log_to_file("Decal Shader Found!")
            

            if (ShaderName in files):
            
                if (file_found == True and has_prefix != True):
                    #create a new material with the same name but add a suffix to it and append it to pymat
                    #copy all this new data to that newly created material
                    
                    # If multiple files found, add a suffix to the material name
                    suffix = '.' + str(pymat.find(i.name) + 1).zfill(3)
                    pymat_copy = i.copy()
                    pymat_copy.name = i.name + suffix
                    pymat_copy = pymat.new(name=pymat_copy.name) 
                    log_to_file("Creating new Material in scene: " + pymat_copy.name)
                    #break
                    
                    #retargets i to be the newly created material
                    #i = pymat_copy #this might need to go at the end of the script
                    
                else:
                    log_to_file("first shader file")
                    #first iteration, do nothing
                    
                file_found = True #shader file was found
            
            
            
            
                log_to_file("------------New Shader-----------")
                log_to_file("")
                log_to_file("--[Shader Name]--")
                log_to_file(ShaderName)
                log_to_file("")
                
                #creates a blank Shader class object and clears data before each iteration
                ShaderItem = shader() 
                ShaderItem.name = ""
                ShaderItem.directory = ""
                ShaderItem.bitmap_count = 0
                ShaderItem.albedo_option = 0
                ShaderItem.bump_mapping_option = 0
                ShaderItem.alpha_test_option = 0
                ShaderItem.specular_mask_option = 0
                ShaderItem.material_model_option = 0
                ShaderItem.environment_mapping_option = 0
                ShaderItem.self_illumination_option = 0
                ShaderItem.blend_mode_option = 0
                ShaderItem.parallax_option = 0
                ShaderItem.misc_option = 0
                ShaderItem.bitmap_list = []
                ShaderItem.function_list = []
                ShaderItem.needed_bitmaps = []
                ShaderItem.env_map_paths = []
                ShaderItem.wetness_option = 0
                ShaderItem.tinting_option = 0
                ShaderItem.alpha_blend_source_option = 0
                
                
                
                #used for default textures
                #Clear the found texture offsets for each new ShaderItem
                ShaderItem.BaseMap_Offset = 0x0
                ShaderItem.DetailMap_Offset = 0x0
                ShaderItem.DetailMap2_Offset = 0x0
                ShaderItem.DetailMap3_Offset = 0x0
                ShaderItem.DetailMapOverlay_Offset = 0x0
                ShaderItem.SpecularMaskTexture_Offset = 0x0
                ShaderItem.ChangeColorMap_Offset = 0x0
                ShaderItem.BumpMap_Offset = 0x0
                ShaderItem.BumpDetailMap_Offset = 0x0
                ShaderItem.EnvironmentMap_Offset = 0x0
                ShaderItem.FlatEnvironmentMap_Offset = 0x0
                ShaderItem.SelfIllumMap_Offset = 0x0
                ShaderItem.SelfIllumDetailMap_Offset = 0x0
                
                
                
                
                
                
                #create blank function object
                FunctionItem = function()
                FunctionItem.tsgt_offset = 0x0
                FunctionItem.option = 0
                FunctionItem.range_toggle = False
                FunctionItem.function_name = ""
                FunctionItem.range_name = ""
                FunctionItem.time_period = 0.00
                FunctionItem.main_min_value = 0.00
                FunctionItem.main_max_value = 0.00
                FunctionItem.left_function_option = 0
                FunctionItem.left_frequency_value = 0.00
                FunctionItem.left_phase_value = 0.00
                FunctionItem.left_min_value = 0.00
                FunctionItem.left_max_value = 0.00
                FunctionItem.left_exponent_value = 0.00
                FunctionItem.right_function_option = 0
                FunctionItem.right_frequency_value = 0.00
                FunctionItem.right_phase_value = 0.00
                FunctionItem.right_min_value = 0.00
                FunctionItem.right_max_value = 0.00
                FunctionItem.right_exponent_value = 0.00
                
                ShaderOutputCount = 0
                ShadersConnected = 0
                EnvTexCount = 2
                BitmapCount = 10
                ImageTextureNodeList = []
                ImageTextureNodeList = [BitmapCount] #store all image texture nodes
                EnvTextureNodeList = []
                EnvTextureNodeList = [EnvTexCount]
                
                ShaderGroupList = [1] # used for keeping track of the order of the shader groups created
                
                
                #offsets for the shader
                CategoryOptions_Offset = 0x0
                BaseMap_Offset = 0x0
                #BaseMap2_Offset = 0x0    #for terrain shader later on
                DetailMap_Offset = 0x0
                DetailMap2_Offset = 0x0
                DetailMap3_Offset = 0x0
                DetailMapOverlay_Offset = 0x0
                SpecularMaskTexture_Offset = 0x0
                ChangeColorMap_Offset = 0x0
                BumpMap_Offset = 0x0
                BumpDetailMap_Offset = 0x0
                ColorMaskMap_Offset = 0x0
                EnvironmentMap_Offset = 0x0
                FlatEnvironmentMap_Offset = 0x0
                SelfIllumMap_Offset = 0x0
                SelfIllumDetailMap_Offset = 0x0
                
                MaterialTexture_Offset = 0x0
                SpecTintMap_Offset = 0x0
                
                SpecularMap_Offset = 0x0
                OcclusionParameterMap_Offset = 0x0
                SubsurfaceMap_Offset = 0x0
                TransparenceMap_Offset = 0x0
                
                Pallete_Offset = 0x0
                AlphaMap_Offset = 0x0
                
                #offset for Alpha_Test_Map
                AlphaTestMap_Offset = 0x0
                
                #Offsets for values, scales and colors
                Albedo_Blend_Offset = 0x0
                Albedo_Color_Offset = 0x0
                Albedo_Color_Alpha_Offset = 0x0
                Albedo_Color2_Offset = 0x0
                Albedo_Color2_Alpha_Offset = 0x0
                Albedo_Color3_Offset = 0x0
                Albedo_Color3_Alpha_Offset = 0x0
                Bump_Detail_Coefficient_Offset = 0x0
                Env_Tint_Color_Offset  = 0x0
                Env_Roughness_Scale_Offset = 0x0
                Self_Illum_Color_Offset = 0x0
                Self_Illum_Intensity_Offset  = 0x0
                Channel_A_Offset  = 0x0
                Channel_A_Alpha_Offset = 0x0
                Channel_B_Offset  = 0x0
                Channel_B_Alpha_Offset  = 0x0
                Channel_C_Offset  = 0x0
                Channel_C_Alpha_Offset  = 0x0
                Color_Medium_Offset  = 0x0
                Color_Medium_Alpha_Offset  = 0x0
                Color_Wide_Offset  = 0x0
                Color_Wide_Alpha_Offset  = 0x0
                Color_Sharp_Offset  = 0x0
                Color_Sharp_Alpha_Offset  = 0x0
                Thinness_Medium_Offset  = 0x0
                Thinness_Wide_Offset = 0x0
                Thinness_Sharp_Offset  = 0x0
                Meter_Color_On_Offset  = 0x0
                Meter_Color_Off_Offset  = 0x0
                Meter_Value_Offset  = 0x0
                Primary_Change_Color_blend_Offset  = 0x0
                Height_Scale_Offset  = 0x0
                Diffuse_Coefficient_Offset = 0x0
                Specular_Coefficient_Offset  = 0x0
                Specular_Tint_Offset  = 0x0
                Fresnel_Color_Offset  = 0x0
                Roughness_Offset  = 0x0
                Environment_Map_Specular_Contribution_Offset = 0x0 
                Use_Material_Texture_Offset  = 0x0
                Normal_Specular_Power_Offset  = 0x0
                Normal_Specular_Tint_Offset  = 0x0
                Glancing_Specular_Power_Offset  = 0x0
                Glancing_Specular_Tint_Offset  = 0x0
                Fresnel_Curve_Steepness_Offset = 0x0
                Albedo_Specular_Tint_Blend_Offset  = 0x0
                Fresnel_Curve_Bias_Offset = 0x0
                Fresnel_Coefficient_Offset = 0x0
                Analytical_Specular_Contribution_Offset = 0x0
                Area_Specular_Contribution_Offset = 0x0
                Neutral_Gray_Offset = 0x0
                
                Specular_Power_Offset = 0x0
                Diffuse_Tint_Offset = 0x0
                Analytical_Specular_Coefficient_Offset = 0x0
                Area_Specular_Coefficient_Offset = 0x0
                Environment_Map_Tint_Offset = 0x0
                Rim_Tint_Offset = 0x0
                Ambient_Tint_Offset = 0x0
                Environment_Map_Coefficient_Offset = 0x0
                Rim_Coefficient_Offset = 0x0
                Rim_Power_Offset = 0x0
                Rim_Start_Offset = 0x0
                Rim_Maps_Transition_Ratio_Offset = 0x0
                Ambient_Coefficient_Offset = 0x0
                Subsurface_Coefficient_Offset = 0x0
                Subsurface_Tint_Offset = 0x0
                Subsurface_Propagation_Bias_Offset = 0x0
                Subsurface_Normal_Detail_Offset = 0x0
                Transparence_Coefficient_Offset = 0x0
                Transparence_Normal_Bias_Offset = 0x0
                Transparence_Tint_Offset = 0x0
                Transparence_Normal_Detail_Offset = 0x0
                Final_Tint_Offset = 0x0
                
                
                


                #terrain shaders stuff
                #bitmaps
                Terrain_Options_Offset = 0x0
                Blend_Map_Offset = 0x0

                Base_Map_M_0_Offset = 0x0
                Detail_Map_M_0_Offset = 0x0
                Bump_Map_M_0_Offset = 0x0
                Detail_Bump_M_0_Offset = 0x0
                
                Base_Map_M_1_Offset = 0x0
                Detail_Map_M_1_Offset = 0x0
                Bump_Map_M_1_Offset = 0x0
                Detail_Bump_M_1_Offset = 0x0
                
                Base_Map_M_2_Offset = 0x0
                Detail_Map_M_2_Offset = 0x0
                Bump_Map_M_2_Offset = 0x0
                Detail_Bump_M_2_Offset = 0x0
                
                Base_Map_M_3_Offset = 0x0
                Detail_Map_M_3_Offset = 0x0
                Bump_Map_M_3_Offset = 0x0
                Detail_Bump_M_3_Offset = 0x0
                
                
                #colors/values etc
                Global_Albedo_Tint_Offset = 0x0
                
                Diffuse_Coefficient_M_0_Offset = 0x0
                Specular_Coefficient_M_0_Offset = 0x0
                Specular_Power_M_0_Offset = 0x0
                Specular_Tint_M_0_Offset = 0x0
                Fresnel_Curve_Steepness_M_0_Offset = 0x00
                Area_Specular_Contribution_M_0_Offset = 0x0
                Analytical_Specular_Contribution_M_0_Offset = 0x0
                Environment_Specular_Contribution_M_0_Offset = 0x0
                Albedo_Specular_Tint_Blend_M_0_Offset = 0x0
                
                Diffuse_Coefficient_M_1_Offset = 0x0
                Specular_Coefficient_M_1_Offset = 0x0
                Specular_Power_M_1_Offset = 0x0
                Specular_Tint_M_1_Offset = 0x0
                Fresnel_Curve_Steepness_M_1_Offset = 0x0
                Area_Specular_Contribution_M_1_Offset = 0x0
                Analytical_Specular_Contribution_M_1_Offset = 0x0
                Environment_Specular_Contribution_M_1_Offset = 0x0
                Albedo_Specular_Tint_Blend_M_1_Offset = 0x0
                
                Diffuse_Coefficient_M_2_Offset = 0x0
                Specular_Coefficient_M_2_Offset = 0x0
                Specular_Power_M_2_Offset = 0x0
                Specular_Tint_M_2_Offset = 0x0
                Fresnel_Curve_Steepness_M_2_Offset = 0x0
                Area_Specular_Contribution_M_2_Offset = 0x0
                Analytical_Specular_Contribution_M_2_Offset = 0x0
                Environment_Specular_Contribution_M_2_Offset = 0x0
                Albedo_Specular_Tint_Blend_M_2_Offset = 0x0
                
                Diffuse_Coefficient_M_3_Offset = 0x0
                Specular_Coefficient_M_3_Offset = 0x0
                Specular_Power_M_3_Offset = 0x0
                Specular_Tint_M_3_Offset = 0x0
                Fresnel_Curve_Steepness_M_3_Offset = 0x0
                Area_Specular_Contribution_M_3_Offset = 0x0
                Analytical_Specular_Contribution_M_3_Offset = 0x0
                Environment_Specular_Contribution_M_3_Offset = 0x0
                Albedo_Specular_Tint_Blend_M_3_Offset = 0x0
                        
                #Halogram shaders
                Halogram_Options_Offset = 0x0
                        
                        
                        
                ShaderPath = root + "/" + ShaderName
                log_to_file("Shader exists!")
                
                log_to_file("")
                log_to_file("--[Shader Directory]--")
                log_to_file(ShaderPath)
                
                #open shader file in raw binary
                shaderfile = open(ShaderPath, "rb")
                shaderfile_read = shaderfile.read()
                
                log_to_file("")
                log_to_file("[Texture Types Not Found/Needed]")
                
                                            ################
                                            #FINDING OFFSETS
                                            ################
                ###################################
                # .shader files and foliage shaders
                ###################################
                
                #if shader file is .shader or foliage or halogram shaders
                if (Shader_Type == 0 or Shader_Type == 2 or Shader_Type == 3 or Shader_Type == 4 or Shader_Type == 6):   #then search for this data below
                
                    #GET START OFFSETS FOR DATA FROM SHADER FILE              maybe add the crap after the type name tp make sure it is legit full type name IF lbgt is 12bytes after end of type name then no directory
                    try: 
                        CategoryOptions_Offset = shaderfile_read.index(b'\x73\x68\x61\x64\x65\x72\x73\x5C\x73\x68\x61\x64\x65\x72')
                    except ValueError:
                        if(debug_textures_values_found != 0):
                            log_to_file("Category Options not found!")
                    
                    #foliage
                    if(Shader_Type == 2):
                        try: 
                            CategoryOptions_Offset = shaderfile_read.index(b'\x73\x68\x61\x64\x65\x72\x73\x5C\x66\x6F\x6C\x69\x61\x67\x65\x6C\x62\x67\x74')
                        except ValueError:
                            if(debug_textures_values_found != 0):                        
                                log_to_file("Category Options not found!")                    

                    #halogram
                    if(Shader_Type == 3):
                        try: 
                            CategoryOptions_Offset = shaderfile_read.index(b'\x73\x68\x61\x64\x65\x72\x73\x5C\x68\x61\x6C\x6F\x67\x72\x61\x6D\x6C\x62\x67\x74')
                        except ValueError:
                            if(debug_textures_values_found != 0):                        
                                log_to_file("Category Options not found!") 
                    
                    #shader_custom
                    if(Shader_Type == 4):
                        try: 
                            CategoryOptions_Offset = shaderfile_read.index(b'\x73\x68\x61\x64\x65\x72\x73\x5C\x63\x75\x73\x74\x6F\x6D\x6C\x62\x67\x74')
                        except ValueError:
                            if(debug_textures_values_found != 0):                        
                                log_to_file("Category Options not found!")
                    
                    #shader_decal
                    if(Shader_Type == 6):
                        try: 
                            CategoryOptions_Offset = shaderfile_read.index(b'\x73\x68\x61\x64\x65\x72\x73\x5C\x64\x65\x63\x61\x6C\x6C\x62\x67\x74')
                        except ValueError:
                            if(debug_textures_values_found != 0):                        
                                log_to_file("Category Options not found!")
                                
                    
                    #CHECK FOR TEXTURE OFFSETS    
                    try: #check for base_map
                        BaseMap_Offset = shaderfile_read.index(b'\x00\x62\x61\x73\x65\x5F\x6D\x61\x70\x66\x72\x67\x74')
                        ShaderItem.BaseMap_Offset = BaseMap_Offset
                    except ValueError:
                        if(debug_textures_values_found != 0):                        
                            log_to_file("base_map not found!")
                    try: 
                        DetailMap_Offset = shaderfile_read.index(b'\x00\x64\x65\x74\x61\x69\x6c\x5f\x6d\x61\x70\x66\x72\x67\x74')
                        ShaderItem.DetailMap_Offset = DetailMap_Offset
                    except ValueError:
                        if(debug_textures_values_found != 0):
                            log_to_file("detail_map not found!")
                    try: 
                        DetailMap2_Offset = shaderfile_read.index(b'\x00\x64\x65\x74\x61\x69\x6c\x5f\x6d\x61\x70\x32\x66\x72\x67\x74')
                        ShaderItem.DetailMap2_Offset = DetailMap2_Offset
                    except ValueError:
                        if(debug_textures_values_found != 0):
                            log_to_file("detail_map2 not found!")
                    try: 
                        DetailMap3_Offset = shaderfile_read.index(b'\x00\x64\x65\x74\x61\x69\x6c\x5f\x6d\x61\x70\x33\x66\x72\x67\x74')
                        ShaderItem.DetailMap3_Offset = DetailMap3_Offset
                    except ValueError:
                        if(debug_textures_values_found != 0):
                            log_to_file("detail_map3 not found!")
                    
                    try: 
                        DetailMapOverlay_Offset = shaderfile_read.index(b'\x00\x64\x65\x74\x61\x69\x6C\x5F\x6D\x61\x70\x5F\x6F\x76\x65\x72\x6C\x61\x79\x66\x72\x67\x74')
                        ShaderItem.DetailMapOverlay_Offset = DetailMapOverlay_Offset
                    except ValueError:
                        if(debug_textures_values_found != 0):
                            log_to_file("detail_map_overlay not found!")                                          
                    try: 
                        SpecularMaskTexture_Offset = shaderfile_read.index(b'\x00\x73\x70\x65\x63\x75\x6C\x61\x72\x5F\x6D\x61\x73\x6B\x5F\x74\x65\x78\x74\x75\x72\x65\x66\x72\x67\x74')
                        ShaderItem.SpecularMaskTexture_Offset = SpecularMaskTexture_Offset
                    except ValueError:
                        if(debug_textures_values_found != 0):                    
                            log_to_file("specular_mask_texture not found!")    
                    try: 
                        ChangeColorMap_Offset = shaderfile_read.index(b'\x00\x63\x68\x61\x6e\x67\x65\x5f\x63\x6f\x6c\x6f\x72\x5f\x6d\x61\x70\x66\x72\x67\x74')
                        ShaderItem.ChangeColorMap_Offset = ChangeColorMap_Offset
                    except ValueError:
                        if(debug_textures_values_found != 0):                    
                            log_to_file("change_color not found!")     
                    try: 
                        BumpMap_Offset = shaderfile_read.index(b'\x00\x62\x75\x6d\x70\x5f\x6d\x61\x70\x66\x72\x67\x74')
                        ShaderItem.BumpMap_Offset = BumpMap_Offset
                    except ValueError:
                        if(debug_textures_values_found != 0):                    
                            log_to_file("bump_map not found!")
                    try: 
                        BumpDetailMap_Offset = shaderfile_read.index(b'\x00\x62\x75\x6d\x70\x5f\x64\x65\x74\x61\x69\x6c\x5f\x6d\x61\x70\x66\x72\x67\x74')
                        ShaderItem.BumpDetailMap_Offset = BumpDetailMap_Offset
                    except ValueError:
                        if(debug_textures_values_found != 0):                    
                            log_to_file("bump_detail_map not found!")       
                    try: 
                        EnvironmentMap_Offset = shaderfile_read.index(b'\x00\x65\x6e\x76\x69\x72\x6f\x6e\x6d\x65\x6e\x74\x5f\x6d\x61\x70\x66\x72\x67\x74')
                        ShaderItem.EnvironmentMap_Offset = EnvironmentMap_Offset
                    except ValueError:
                        if(debug_textures_values_found != 0):                    
                            log_to_file("environment_map not found!")     
                    try: 
                        FlatEnvironmentMap_Offset = shaderfile_read.index(b'\x00\x66\x6C\x61\x74\x5F\x65\x6E\x76\x69\x72\x6F\x6E\x6D\x65\x6E\x74\x5F\x6D\x61\x70\x66\x72\x67\x74')
                        ShaderItem.FlatEnvironmentMap_Offset = FlatEnvironmentMap_Offset
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("flat_environment_map not found!")     
                    try: 
                        SelfIllumMap_Offset = shaderfile_read.index(b'\x00\x73\x65\x6c\x66\x5f\x69\x6c\x6c\x75\x6d\x5f\x6d\x61\x70\x66\x72\x67\x74')
                        ShaderItem.SelfIllumMap_Offset = SelfIllumMap_Offset
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("self_illum_map not found!")     
                    try: 
                        SelfIllumDetailMap_Offset = shaderfile_read.index(b'\x00\x73\x65\x6c\x66\x5f\x69\x6c\x6c\x75\x6d\x5f\x64\x65\x74\x61\x69\x6c\x5f\x6d\x61\x70\x66\x72\x67\x74')
                        ShaderItem.SelfIllumDetailMap_Offset = SelfIllumDetailMap_Offset
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("self_illum_detail_map not found!")
                            
                    try: #check for color_mask_map
                        ColorMaskMap_Offset = shaderfile_read.index(b'\x00\x63\x6F\x6C\x6F\x72\x5F\x6D\x61\x73\x6B\x5F\x6D\x61\x70\x66\x72\x67\x74')
                        ShaderItem.ColorMaskMap_Offset = ColorMaskMap_Offset
                    except ValueError:
                        if(debug_textures_values_found != 0):                        
                            log_to_file("color_mask_map not found!")      

                    try: #check for material_texture
                        MaterialTexture_Offset = shaderfile_read.index(convert_to_hex("material_texture"))
                        ShaderItem.MaterialTexture_Offset = MaterialTexture_Offset
                    except ValueError:
                        if(debug_textures_values_found != 0):                        
                            log_to_file("material_texture not found!")      

                    try: #check for spec_tint_map
                        SpecTintMap_Offset = shaderfile_read.index(convert_to_hex("spec_tint_map"))
                        ShaderItem.SpecTintMap_Offset = SpecTintMap_Offset
                    except ValueError:
                        if(debug_textures_values_found != 0):                        
                            log_to_file("spec_tint_map not found!")
                    
                    try: #check for specular_map
                        SpecularMap_Offset = shaderfile_read.index(convert_to_hex("specular_map"))
                        ShaderItem.SpecularMap_Offset = SpecularMap_Offset
                    except ValueError:
                        if(debug_textures_values_found != 0):                        
                            log_to_file("specular_map not found!")                    
                    try: #check for occlusion_parameter_map
                        OcclusionParameterMap_Offset = shaderfile_read.index(convert_to_hex("occlusion_parameter_map"))
                        ShaderItem.OcclusionParameterMap_Offset = OcclusionParameterMap_Offset
                    except ValueError:
                        if(debug_textures_values_found != 0):                        
                            log_to_file("occlusion_parameter_map not found!")
                    
                    try: #check for subsurface_map
                        SubsurfaceMap_Offset = shaderfile_read.index(convert_to_hex("subsurface_map"))
                        ShaderItem.SubsurfaceMap_Offset = SubsurfaceMap_Offset
                    except ValueError:
                        if(debug_textures_values_found != 0):                        
                            log_to_file("subsurface_map not found!")
                    
                    try: #check for transparence_map
                        TransparenceMap_Offset = shaderfile_read.index(convert_to_hex("transparence_map"))
                        ShaderItem.TransparenceMap_Offset = TransparenceMap_Offset
                    except ValueError:
                        if(debug_textures_values_found != 0):                        
                            log_to_file("transparence_map not found!")
                            
                            
                            
                            

                    #Check for Alpha_Map
                    try: 
                        AlphaTestMap_Offset = shaderfile_read.index(b'\x00\x61\x6C\x70\x68\x61\x5F\x74\x65\x73\x74\x5F\x6D\x61\x70\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("alpha_test_map not found!")

                    #CHECK FOR SCALE, COLOR, AND VALUE  
                    try: 
                        Albedo_Blend_Offset = shaderfile_read.index(b'\x00\x61\x6C\x62\x65\x64\x6F\x5F\x62\x6C\x65\x6E\x64\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("albedo_blend not found!")
                    try: 
                        Albedo_Color_Offset = shaderfile_read.index(b'\x00\x61\x6c\x62\x65\x64\x6f\x5f\x63\x6f\x6c\x6f\x72\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("albedo_color not found!")
                    try: 
                        Albedo_Color_Alpha_Offset = shaderfile_read.index(b'\x00\x61\x6c\x62\x65\x64\x6f\x5f\x63\x6f\x6c\x6f\x72\x5f\x61\x6c\x70\x68\x61\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("albedo_color_alpha not found!")    
                    try: 
                        Albedo_Color2_Offset = shaderfile_read.index(b'\x00\x61\x6c\x62\x65\x64\x6f\x5f\x63\x6f\x6c\x6f\x72\x32\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("albedo_color not found!")
                    try: 
                        Albedo_Color2_Alpha_Offset = shaderfile_read.index(b'\x00\x61\x6c\x62\x65\x64\x6f\x5f\x63\x6f\x6c\x6f\x72\x32\x5f\x61\x6c\x70\x68\x61\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("albedo_color_alpha not found!") 
                    try: 
                        Albedo_Color3_Offset = shaderfile_read.index(b'\x00\x61\x6c\x62\x65\x64\x6f\x5f\x63\x6f\x6c\x6f\x72\x33\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("albedo_color not found!")
                    try: 
                        Albedo_Color3_Alpha_Offset = shaderfile_read.index(b'\x00\x61\x6c\x62\x65\x64\x6f\x5f\x63\x6f\x6c\x6f\x72\x33\x5f\x61\x6c\x70\x68\x61\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("albedo_color_alpha not found!") 
                    try: 
                        Bump_Detail_Coefficient_Offset = shaderfile_read.index(b'\x00\x62\x75\x6d\x70\x5f\x64\x65\x74\x61\x69\x6c\x5f\x63\x6f\x65\x66\x66\x69\x63\x69\x65\x6e\x74\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("bump_detail_coefficient not found!")    
                    try: 
                        Env_Tint_Color_Offset = shaderfile_read.index(b'\x00\x65\x6e\x76\x5f\x74\x69\x6e\x74\x5f\x63\x6f\x6c\x6f\x72\x66\x72\x67\x74')
                        
                        #IF FOR SOME GOD AWFUL REASON THERE IS A SECOND COLOR VALUE THEN THIS WILL GRAB THAT INSTEAD
                        if (test_find(Env_Tint_Color_Offset, shaderfile, "env_tint_color") != -1):
                            log_to_file("grabbing second env tint color offset")
                            Env_Tint_Color_Offset = test_find(Env_Tint_Color_Offset, shaderfile, "env_tint_color")
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("env_tint_color not found!")
                    try: 
                        Env_Roughness_Scale_Offset = shaderfile_read.index(b'\x00\x65\x6e\x76\x5f\x72\x6f\x75\x67\x68\x6e\x65\x73\x73\x5f\x73\x63\x61\x6c\x65\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("env_roughness_scale not found!")    
                    try: 
                        Self_Illum_Color_Offset = shaderfile_read.index(b'\x00\x73\x65\x6c\x66\x5f\x69\x6c\x6c\x75\x6d\x5f\x63\x6f\x6c\x6f\x72\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("self_illum_color not found!")    
                    try: 
                        Self_Illum_Intensity_Offset = shaderfile_read.index(b'\x00\x73\x65\x6c\x66\x5f\x69\x6c\x6c\x75\x6d\x5f\x69\x6e\x74\x65\x6e\x73\x69\x74\x79\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("self_illum_intensity not found!")    
                    try: 
                        Channel_A_Offset = shaderfile_read.index(b'\x00\x63\x68\x61\x6e\x6e\x65\x6c\x5f\x61\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("channel_a not found!")    
                    try: 
                        Channel_A_Alpha_Offset = shaderfile_read.index(b'\x00\x63\x68\x61\x6e\x6e\x65\x6c\x5f\x61\x5f\x61\x6c\x70\x68\x61\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("channel_a_alpha not found!")    
                    try: 
                        Channel_B_Offset = shaderfile_read.index(b'\x00\x63\x68\x61\x6e\x6e\x65\x6c\x5f\x62\x66\x72\x67\x74')
                    except ValueError:
                        if(Channel_A_Offset != 0):
                            #add default data
                            ShaderItem.channel_b = color_white_rgb
                            if(debug_textures_values_found != 0): 
                                log_to_file("channel_b not found, but others were. Adding default data to channel_b")
                        else:
                            ShaderItem.channel_b = color_white_rgb
                            if(debug_textures_values_found != 0): 
                                log_to_file("channel_b not found!")   
                    try: 
                        Channel_B_Alpha_Offset = shaderfile_read.index(b'\x00\x63\x68\x61\x6e\x6e\x65\x6c\x5f\x62\x5f\x61\x6c\x70\x68\x61\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("channel_b_alpha not found!")    
                    try: 
                        Channel_C_Offset = shaderfile_read.index(b'\x00\x63\x68\x61\x6e\x6e\x65\x6c\x5f\x63\x66\x72\x67\x74')
                    except ValueError:
                        if(Channel_A_Offset != 0 or Channel_B_Offset != 0):
                            #add default data
                            ShaderItem.channel_c = color_white_rgb
                            if(debug_textures_values_found != 0): 
                                log_to_file("channel_c not found, but others were. Adding default data to channel_c")
                        else:
                            if(debug_textures_values_found != 0): 
                                log_to_file("channel_c not found!")    
                    try: 
                        Channel_C_Alpha_Offset = shaderfile_read.index(b'\x00\x63\x68\x61\x6e\x6e\x65\x6c\x5f\x63\x5f\x61\x6c\x70\x68\x61\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("channel_c_alpha not found!")    
                    try: 
                        Color_Medium_Offset = shaderfile_read.index(b'\x00\x63\x6f\x6c\x6f\x72\x5f\x6d\x65\x64\x69\x75\x6d\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("color_medium not found!")    
                    try: 
                        Color_Medium_Alpha_Offset = shaderfile_read.index(b'\x00\x63\x6f\x6c\x6f\x72\x5f\x6d\x65\x64\x69\x75\x6d\x5f\x61\x6c\x70\x68\x61\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("color_medium_alpha not found!")    
                    try: 
                        Color_Wide_Offset = shaderfile_read.index(b'\x00\x63\x6f\x6c\x6f\x72\x5f\x77\x69\x64\x65\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("color_wide not found!")    
                    try: 
                        Color_Wide_Alpha_Offset = shaderfile_read.index(b'\x00\x63\x6f\x6c\x6f\x72\x5f\x77\x69\x64\x65\x5f\x61\x6c\x70\x68\x61\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("color_wide_alpha not found!")    
                    try: 
                        Color_Sharp_Offset = shaderfile_read.index(b'\x00\x63\x6f\x6c\x6f\x72\x5f\x73\x68\x61\x72\x70\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("color_sharp not found!")    
                    try: 
                        Color_Sharp_Alpha_Offset = shaderfile_read.index(b'\x00\x63\x6f\x6c\x6f\x72\x5f\x73\x68\x61\x72\x70\x5f\x61\x6c\x70\x68\x61\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("color_sharp_alpha not found!")    
                    try: 
                        Thinness_Medium_Offset = shaderfile_read.index(b'\x00\x74\x68\x69\x6e\x6e\x65\x73\x73\x5f\x6d\x65\x64\x69\x75\x6d\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("thinness_medium not found!")    
                    try: 
                        Thinness_Wide_Offset = shaderfile_read.index(b'\x00\x74\x68\x69\x6e\x6e\x65\x73\x73\x5f\x77\x69\x64\x65\x66\x72\x67x\74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("thinness_wide not found!")    
                    try: 
                        Thinness_Sharp_Offset = shaderfile_read.index(b'\x00\x74\x68\x69\x6e\x6e\x65\x73\x73\x5f\x73\x68\x61\x72\x70\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("thinness_sharp not found!")    
                    try: 
                        Meter_Color_On_Offset = shaderfile_read.index(b'\x00\x6d\x65\x74\x65\x72\x5f\x63\x6f\x6c\x6f\x72\x5f\x6f\x6e\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("meter_color_on not found!")    
                    try: 
                        Meter_Color_Off_Offset = shaderfile_read.index(b'\x00\x6d\x65\x74\x65\x72\x5f\x63\x6f\x6c\x6f\x72\x5f\x6f\x66\x66\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("meter_color_off not found!")    
                    try: 
                        Meter_Value_Offset = shaderfile_read.index(b'\x00\x6d\x65\x74\x65\x72\x5f\x76\x61\x6c\x75\x65\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("meter_value not found!")    
                    try: 
                        Primary_Change_Color_blend_Offset = shaderfile_read.index(b'\x00\x70\x72\x69\x6d\x61\x72\x79\x5f\x63\x68\x61\x6e\x67\x65\x5f\x63\x6f\x6c\x6f\x72\x5f\x62\x6c\x65\x6e\x64\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("primary_change_color_blend not found!")    
                    try: 
                        Height_Scale_Offset = shaderfile_read.index(b'\x00\x68\x65\x69\x67\x68\x74\x5f\x73\x63\x61\x6c\x65\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("height_scale not found!")    
                    try: 
                        Diffuse_Coefficient_Offset = shaderfile_read.index(b'\x00\x64\x69\x66\x66\x75\x73\x65\x5f\x63\x6f\x65\x66\x66\x69\x63\x69\x65\x6e\x74\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("diffuse_coefficient not found!")    
                    try: 
                        Specular_Coefficient_Offset = shaderfile_read.index(b'\x00\x73\x70\x65\x63\x75\x6c\x61\x72\x5f\x63\x6f\x65\x66\x66\x69\x63\x69\x65\x6e\x74\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("specular_coefficient not found!")    
                    try: 
                        Specular_Tint_Offset = shaderfile_read.index(b'\x00\x73\x70\x65\x63\x75\x6c\x61\x72\x5f\x74\x69\x6e\x74\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("specular_tint not found!")    
                    try: 
                        Fresnel_Color_Offset = shaderfile_read.index(b'\x00\x66\x72\x65\x73\x6e\x65\x6c\x5f\x63\x6f\x6c\x6f\x72\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("fresnel_color not found!")    
                    try: 
                        Roughness_Offset = shaderfile_read.index(b'\x00\x72\x6f\x75\x67\x68\x6e\x65\x73\x73\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("roughness not found!")    
                    try: 
                        Environment_Map_Specular_Contribution_Offset = shaderfile_read.index(b'\x00\x65\x6e\x76\x69\x72\x6f\x6e\x6d\x65\x6e\x74\x5f\x6d\x61\x70\x5f\x73\x70\x65\x63\x75\x6c\x61\x72\x5f\x63\x6f\x6e\x74\x72\x69\x62\x75\x74\x69\x6f\x6e\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("environment_map_specular_contribution not found!")    
                    try: 
                        Use_Material_Texture_Offset = shaderfile_read.index(b'\x00\x75\x73\x65\x5f\x6d\x61\x74\x65\x72\x69\x61\x6c\x5f\x74\x65\x78\x74\x75\x72\x65\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("use_material_texture not found!")    
                    try: 
                        Normal_Specular_Power_Offset = shaderfile_read.index(b'\x00\x6e\x6f\x72\x6d\x61\x6c\x5f\x73\x70\x65\x63\x75\x6c\x61\x72\x5f\x70\x6f\x77\x65\x72\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("normal_specular_power not found!")    
                    try: 
                        Normal_Specular_Tint_Offset = shaderfile_read.index(b'\x00\x6e\x6f\x72\x6d\x61\x6c\x5f\x73\x70\x65\x63\x75\x6c\x61\x72\x5f\x74\x69\x6e\x74\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("normal_specular_tint not found!")                #6E 6F 72 6D 61 6C 5F 73 70 65 63 75 6C 61 72 5F 74 69 6E 74
                    try: 
                        Glancing_Specular_Power_Offset = shaderfile_read.index(b'\x00\x67\x6c\x61\x6e\x63\x69\x6e\x67\x5f\x73\x70\x65\x63\x75\x6c\x61\x72\x5f\x70\x6f\x77\x65\x72\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("glancing_specular_power not found!")    
                    try: 
                        Glancing_Specular_Tint_Offset = shaderfile_read.index(b'\x00\x67\x6c\x61\x6e\x63\x69\x6e\x67\x5f\x73\x70\x65\x63\x75\x6c\x61\x72\x5f\x74\x69\x6e\x74\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("glancing_specular_tint not found!")                #67 6C 61 6E 63 69 6E 67 5F 73 70 65 63 75 6C 61 72 5F 74 69 6E 74
                    try: 
                        Fresnel_Curve_Steepness_Offset = shaderfile_read.index(b'\x00\x66\x72\x65\x73\x6e\x65\x6c\x5f\x63\x75\x72\x76\x65\x5f\x73\x74\x65\x65\x70\x6e\x65\x73\x73\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("fresnel_curve_steepness not found!")    
                    try: 
                        Albedo_Specular_Tint_Blend_Offset = shaderfile_read.index(b'\x00\x61\x6c\x62\x65\x64\x6f\x5f\x73\x70\x65\x63\x75\x6c\x61\x72\x5f\x74\x69\x6e\x74\x5f\x62\x6c\x65\x6e\x64\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("albedo_specular_tint_blend not found!")    
                    try: 
                        Fresnel_Curve_Bias_Offset_Offset = shaderfile_read.index(b'\x00\x66\x72\x65\x73\x6E\x65\x6C\x5F\x63\x75\x72\x76\x65\x5F\x62\x69\x61\x73\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("fresnel_curve_bias not found!")
                    try: 
                        Fresnel_Coefficient_Offset = shaderfile_read.index(b'\x00\x66\x72\x65\x73\x6E\x65\x6C\x5F\x63\x6F\x65\x66\x66\x69\x63\x69\x65\x6E\x74\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("fresnel_coefficient not found!")
                    try: 
                        Analytical_Specular_Contribution_Offset = shaderfile_read.index(b'\x00\x61\x6E\x61\x6C\x79\x74\x69\x63\x61\x6C\x5F\x73\x70\x65\x63\x75\x6C\x61\x72\x5F\x63\x6F\x6E\x74\x72\x69\x62\x75\x74\x69\x6F\x6E\x66\x72\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("analytical_specular_contribution not found!")         
                    try: 
                        Area_Specular_Contribution_Offset = shaderfile_read.index(b'\x00\x61\x72\x65\x61\x5F\x73\x70\x65\x63\x75\x6C\x61\x72\x5F\x63\x6F\x6E\x74\x72\x69\x62\x75\x74\x69\x6F\x6E\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("area_specular_contribution not found!")
                    try: 
                        Neutral_Gray_Offset = shaderfile_read.index(convert_to_hex("neutral_gray")) 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("neutral_gray not found!")
                    
                    try: 
                        Specular_Power_Offset = shaderfile_read.index(convert_to_hex("specular_power")) 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("specular_power not found!")
                    try: 
                        Diffuse_Tint_Offset = shaderfile_read.index(convert_to_hex("diffuse_tint")) 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("diffuse_tint not found!")
                    try: 
                        Analytical_Specular_Coefficient_Offset = shaderfile_read.index(convert_to_hex("analytical_specular_coefficient")) 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("analytical_specular_coefficient not found!")
                    try: 
                        Area_Specular_Coefficient_Offset = shaderfile_read.index(convert_to_hex("area_specular_coefficient")) 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("area_specular_coefficient not found!")
                    try: 
                        Environment_Map_Tint_Offset = shaderfile_read.index(convert_to_hex("environment_map_tint")) 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("environment_map_tint not found!")
                    try: 
                        Rim_Tint_Offset = shaderfile_read.index(convert_to_hex("rim_tint")) 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("rim_tint not found!")
                    try: 
                        Ambient_Tint_Offset = shaderfile_read.index(convert_to_hex("ambient_tint")) 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("ambient_tint not found!")
                    try: 
                        Environment_Map_Coefficient_Offset = shaderfile_read.index(convert_to_hex("environment_map_coefficient")) 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("environment_map_coefficient not found!")
                    try: 
                        Rim_Coefficient_Offset = shaderfile_read.index(convert_to_hex("rim_coefficient")) 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("rim_coefficient not found!")
                    try: 
                        Rim_Power_Offset = shaderfile_read.index(convert_to_hex("rim_power")) 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("rim_power not found!")
                    try: 
                        Rim_Start_Offset = shaderfile_read.index(convert_to_hex("rim_start")) 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("rim_start not found!")
                    try: 
                        Rim_Maps_Transition_Ratio_Offset = shaderfile_read.index(convert_to_hex("rim_maps_transition_ratio")) 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("rim_maps_transition_ratio not found!")
                    try: 
                        Ambient_Coefficient_Offset = shaderfile_read.index(convert_to_hex("ambient_coefficient")) 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("ambient_coefficient not found!")
                    try: 
                        Subsurface_Coefficient_Offset = shaderfile_read.index(convert_to_hex("subsurface_coefficient")) 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("subsurface_coefficient not found!")
                    try: 
                        Subsurface_Tint_Offset = shaderfile_read.index(convert_to_hex("subsurface_tint")) 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("subsurface_tint not found!")
                    try: 
                        Subsurface_Propagation_Bias_Offset = shaderfile_read.index(convert_to_hex("subsurface_propagation_bias")) 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("subsurface_propagation_bias not found!")
                    try: 
                        Subsurface_Normal_Detail_Offset = shaderfile_read.index(convert_to_hex("subsurface_normal_detail")) 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("subsurface_normal_detail not found!")
                    try: 
                        Transparence_Coefficient_Offset = shaderfile_read.index(convert_to_hex("transparence_coefficient")) 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("transparence_coefficient not found!")
                    try: 
                        Transparence_Normal_Bias_Offset = shaderfile_read.index(convert_to_hex("transparence_normal_bias")) 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("transparence_normal_bias not found!")
                    try: 
                        Transparence_Tint_Offset = shaderfile_read.index(convert_to_hex("transparence_tint")) 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("transparence_tint not found!")
                    try: 
                        Transparence_Normal_Detail_Offset = shaderfile_read.index(convert_to_hex("transparence_normal_detail")) 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("transparence_normal_detail not found!")
                    try: 
                        Final_Tint_Offset = shaderfile_read.index(convert_to_hex("final_tint")) 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("final_tint not found!")
                    
                    ####################
                    #   DECAL SHADERS
                    ####################
                    if (Shader_Type == 6):
                        try: 
                            Pallete_Offset = shaderfile_read.index(convert_to_hex("pallete")) 
                        except ValueError:
                            if(debug_textures_values_found != 0): 
                                log_to_file("pallete not found!")
                        try: 
                            AlphaMap_Offset = shaderfile_read.index(convert_to_hex("alpha_map")) 
                        except ValueError:
                            if(debug_textures_values_found != 0): 
                                log_to_file("alpha_map not found!")
                    

                    #######################
                    #TERRAIN SHADER OFFSETS
                    #######################
                        
                #if shader file is .shader_terrain
                if (Shader_Type == 1):
                 
                    ###########
                    #Categories
                    ###########
                    
                    try: 
                        CategoryOptions_Offset = shaderfile_read.index(b'\x00\x66\x64\x6D\x72\x73\x68\x61\x64\x65\x72\x73\x5C\x74\x65\x72\x72\x61\x69\x6E\x6C\x62\x67\x74')
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("Category Options not found!")
                    
                    #########
                    #Textures
                    #########
                    try: 
                        Blend_Map_Offset = shaderfile_read.index(b'\x00\x62\x6C\x65\x6E\x64\x5F\x6D\x61\x70\x66\x72\x67\x74') #
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("blend_map not found!")   
                    try: 
                        Base_Map_M_0_Offset = shaderfile_read.index(b'\x00\x62\x61\x73\x65\x5F\x6D\x61\x70\x5F\x6D\x5F\x30\x66\x72\x67\x74') #
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("base_map_m_0 not found!") 
                    try: 
                        Detail_Map_M_0_Offset = shaderfile_read.index(b'\x00\x64\x65\x74\x61\x69\x6C\x5F\x6D\x61\x70\x5F\x6D\x5F\x30\x66\x72\x67\x74') #
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("detail_map_m_0 not found!") 
                    try: 
                        Bump_Map_M_0_Offset = shaderfile_read.index(b'\x00\x62\x75\x6D\x70\x5F\x6D\x61\x70\x5F\x6D\x5F\x30\x66\x72\x67\x74') #
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("bump_map_m_0 not found!") 
                    try: 
                        Detail_Bump_M_0_Offset = shaderfile_read.index(b'\x00\x64\x65\x74\x61\x69\x6C\x5F\x62\x75\x6D\x70\x5F\x6D\x5F\x30\x66\x72\x67\x74') #
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("detail_bump_m_0 not found!") 
                    try: 
                        Base_Map_M_1_Offset = shaderfile_read.index(b'\x00\x62\x61\x73\x65\x5F\x6D\x61\x70\x5F\x6D\x5F\x31\x66\x72\x67\x74') #
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("base_map_m_1 not found!") 
                    try: 
                        Detail_Map_M_1_Offset = shaderfile_read.index(b'\x00\x64\x65\x74\x61\x69\x6C\x5F\x6D\x61\x70\x5F\x6D\x5F\x31\x66\x72\x67\x74')#
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("detail_map_m_1 not found!") 
                    try: 
                        Bump_Map_M_1_Offset = shaderfile_read.index(b'\x00\x62\x75\x6D\x70\x5F\x6D\x61\x70\x5F\x6D\x5F\x31\x66\x72\x67\x74') #
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("bump_map_m_1 not found!") 
                    try: 
                        Detail_Bump_M_1_Offset = shaderfile_read.index(b'\x00\x64\x65\x74\x61\x69\x6C\x5F\x6D\x61\x70\x5F\x6D\x5F\x31\x66\x72\x67\x74') #
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("detail_bump_m_1 not found!") 
                    try: 
                        Base_Map_M_2_Offset = shaderfile_read.index(b'\x00\x62\x61\x73\x65\x5F\x6D\x61\x70\x5F\x6D\x5F\x32\x66\x72\x67\x74') #
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("base_map_m_2 not found!") 
                    try: 
                        Detail_Map_M_2_Offset = shaderfile_read.index(b'\x00\x64\x65\x74\x61\x69\x6C\x5F\x6D\x61\x70\x5F\x6D\x5F\x32\x66\x72\x67\x74')#
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("detail_map_m_2 not found!") 
                    try: 
                        Bump_Map_M_2_Offset = shaderfile_read.index(b'\x00\x62\x75\x6D\x70\x5F\x6D\x61\x70\x5F\x6D\x5F\x32\x66\x72\x67\x74') #
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("bump_map_m_2 not found!") 
                    try: 
                        Detail_Bump_M_2_Offset = shaderfile_read.index(b'\x00\x64\x65\x74\x61\x69\x6C\x5F\x6D\x61\x70\x5F\x6D\x5F\x32\x66\x72\x67\x74') #
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("detail_bump_m_2 not found!") 
                    try:  
                        Base_Map_M_3_Offset = shaderfile_read.index(b'\x00\x62\x61\x73\x65\x5F\x6D\x61\x70\x5F\x6D\x5F\x33\x66\x72\x67\x74') #
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("base_map_m_3 not found!") 
                    try: 
                        Detail_Map_M_3_Offset = shaderfile_read.index(b'\x00\x64\x65\x74\x61\x69\x6C\x5F\x6D\x61\x70\x5F\x6D\x5F\x33\x66\x72\x67\x74') #
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("detail_map_m_3 not found!") 
                    try: 
                        Bump_Map_M_3_Offset = shaderfile_read.index(b'\x00\x62\x75\x6D\x70\x5F\x6D\x61\x70\x5F\x6D\x5F\x33\x66\x72\x67\x74') #
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("bump_map_m_3 not found!") 
                    try: 
                        Detail_Bump_M_3_Offset = shaderfile_read.index(b'\x00\x64\x65\x74\x61\x69\x6C\x5F\x6D\x61\x70\x5F\x6D\x5F\x33\x66\x72\x67\x74') #
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("detail_bump_m_3 not found!") 
                    

                    
                       
                    ##############
                    #COLORS/VALUES
                    ##############
                    
                    try: 
                        Global_Albedo_Tint_Offset = shaderfile_read.index(b'\x00\x67\x6C\x6F\x62\x61\x6C\x5F\x61\x6C\x62\x65\x64\x6F\x5F\x74\x69\x6E\x74\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("global_albedo_tint not found!")   
                    
                    try: 
                        Diffuse_Coefficient_M_0_Offset = shaderfile_read.index(b'\x00\x64\x69\x66\x66\x75\x73\x65\x5F\x63\x6F\x65\x66\x66\x69\x63\x69\x65\x6E\x74\x5F\x6D\x5F\x30\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("diffuse_coefficient_m_0 not found!")
                    try: 
                        Specular_Coefficient_M_0_Offset = shaderfile_read.index(b'\x00\x73\x70\x65\x63\x75\x6C\x61\x72\x5F\x63\x6F\x65\x66\x66\x69\x63\x69\x65\x6E\x74\x5F\x6D\x5F\x30\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("specular_coefficient_m_0 not found!")
                    try: 
                        Specular_Power_M_0_Offset = shaderfile_read.index(b'\x00\x73\x70\x65\x63\x75\x6C\x61\x72\x5F\x70\x6F\x77\x65\x72\x5F\x6D\x5F\x30\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("specular_power_m_0 not found!")
                    try: 
                        Specular_Tint_M_0_Offset = shaderfile_read.index(b'\x00\x73\x70\x65\x63\x75\x6C\x61\x72\x5F\x74\x69\x6E\x74\x5F\x6D\x5F\x30\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("specular_tint_m_0 not found!")
                    try: 
                        Fresnel_Curve_Steepness_M_0_Offset = shaderfile_read.index(b'\x00\x66\x72\x65\x73\x6e\x65\x6c\x5f\x63\x75\x72\x76\x65\x5f\x73\x74\x65\x65\x70\x6e\x65\x73\x73\x5f\x6d\x5f\x30\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("fresnel_curve_steepness_m_0 not found!")
                    try: 
                        Area_Specular_Contribution_M_0_Offset = shaderfile_read.index(b'\x00\x61\x72\x65\x61\x5F\x73\x70\x65\x63\x75\x6C\x61\x72\x5F\x63\x6F\x6E\x74\x72\x69\x62\x75\x74\x69\x6F\x6E\x5F\x6D\x5F\x30\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("area_specular_contribution_m_0 not found!")
                    try: 
                        Analytical_Specular_Contribution_M_0_Offset = shaderfile_read.index(b'\x00\x61\x6E\x61\x6C\x79\x74\x69\x63\x61\x6C\x5F\x73\x70\x65\x63\x75\x6C\x61\x72\x5F\x63\x6F\x6E\x74\x72\x69\x62\x75\x74\x69\x6F\x6E\x5F\x6D\x5F\x30\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("analytical_specular_contribution_m_0 not found!")
                    try: 
                        Environment_Specular_Contribution_M_0_Offset = shaderfile_read.index(b'\x00\x65\x6e\x76\x69\x72\x6f\x6e\x6d\x65\x6e\x74\x5f\x73\x70\x65\x63\x75\x6c\x61\x72\x5f\x63\x6f\x6e\x74\x72\x69\x62\x75\x74\x69\x6f\x6e\x5f\x6d\x5f\x30\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("environment_specular_contribution_m_0 not found!")
                    try: 
                        Self_Illum_Color_M_0_Offset = shaderfile_read.index(convert_to_hex("self_illum_color_m_0")) 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("self_illum_color_m_0 not found!")
                    try: 
                        Self_Illum_Intensity_M_0_Offset = shaderfile_read.index(convert_to_hex("self_illum_intensity_m_0")) 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("self_illum_intensity_m_0 not found!")                
                    try: 
                        Albedo_Specular_Tint_Blend_M_0_Offset = shaderfile_read.index(b'\x00\x61\x6c\x62\x65\x64\x6f\x5f\x73\x70\x65\x63\x75\x6c\x61\x72\x5f\x74\x69\x6e\x74\x5f\x62\x6c\x65\x6e\x64\x5f\x6d\x5f\x30\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("albedo_specular_tint_blend_m_0 not found!")
                    try: 
                        Diffuse_Coefficient_M_1_Offset = shaderfile_read.index(b'\x00\x64\x69\x66\x66\x75\x73\x65\x5F\x63\x6F\x65\x66\x66\x69\x63\x69\x65\x6E\x74\x5F\x6D\x5F\x31\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("diffuse_coefficient_m_1 not found!")
                    try: 
                        Specular_Coefficient_M_1_Offset = shaderfile_read.index(b'\x00\x73\x70\x65\x63\x75\x6C\x61\x72\x5F\x63\x6F\x65\x66\x66\x69\x63\x69\x65\x6E\x74\x5F\x6D\x5F\x31\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("specular_coefficient_m_1 not found!")
                    try: 
                        Specular_Power_M_1_Offset = shaderfile_read.index(b'\x00\x73\x70\x65\x63\x75\x6C\x61\x72\x5F\x70\x6F\x77\x65\x72\x5F\x6D\x5F\x31\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("specular_power_m_1 not found!")
                    try: 
                        Specular_Tint_M_1_Offset = shaderfile_read.index(b'\x00\x73\x70\x65\x63\x75\x6C\x61\x72\x5F\x74\x69\x6E\x74\x5F\x6D\x5F\x31\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("specular_tint_m_1 not found!")
                    try: 
                        Fresnel_Curve_Steepness_M_1_Offset = shaderfile_read.index(b'\x00\x66\x72\x65\x73\x6e\x65\x6c\x5f\x63\x75\x72\x76\x65\x5f\x73\x74\x65\x65\x70\x6e\x65\x73\x73\x5f\x6d\x5f\x31\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("fresnel_curve_steepness_m_1 not found!")
                    try: 
                        Area_Specular_Contribution_M_1_Offset = shaderfile_read.index(b'\x00\x61\x72\x65\x61\x5F\x73\x70\x65\x63\x75\x6C\x61\x72\x5F\x63\x6F\x6E\x74\x72\x69\x62\x75\x74\x69\x6F\x6E\x5F\x6D\x5F\x31\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("area_specular_contribution_m_1 not found!")
                    try: 
                        Analytical_Specular_Contribution_M_1_Offset = shaderfile_read.index(b'\x00\x61\x6E\x61\x6C\x79\x74\x69\x63\x61\x6C\x5F\x73\x70\x65\x63\x75\x6C\x61\x72\x5F\x63\x6F\x6E\x74\x72\x69\x62\x75\x74\x69\x6F\x6E\x5F\x6D\x5F\x31\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("analytical_specular_contribution_m_1 not found!")
                    try: 
                        Environment_Specular_Contribution_M_1_Offset = shaderfile_read.index(b'\x00\x65\x6e\x76\x69\x72\x6f\x6e\x6d\x65\x6e\x74\x5f\x73\x70\x65\x63\x75\x6c\x61\x72\x5f\x63\x6f\x6e\x74\x72\x69\x62\x75\x74\x69\x6f\x6e\x5f\x6d\x5f\x31\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("environment_specular_contribution_m_1 not found!")
                    try: 
                        Self_Illum_Color_M_1_Offset = shaderfile_read.index(convert_to_hex("self_illum_color_m_1")) 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("self_illum_color_m_1 not found!")
                    try: 
                        Self_Illum_Intensity_M_1_Offset = shaderfile_read.index(convert_to_hex("self_illum_intensity_m_1")) 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("self_illum_intensity_m_1 not found!")  
                    try: 
                        Albedo_Specular_Tint_Blend_M_1_Offset = shaderfile_read.index(b'\x00\x61\x6c\x62\x65\x64\x6f\x5f\x73\x70\x65\x63\x75\x6c\x61\x72\x5f\x74\x69\x6e\x74\x5f\x62\x6c\x65\x6e\x64\x5f\x6d\x5f\x31\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("albedo_specular_tint_blend_m_1 not found!")
                    try: 
                        Diffuse_Coefficient_M_2_Offset = shaderfile_read.index(b'\x00\x64\x69\x66\x66\x75\x73\x65\x5F\x63\x6F\x65\x66\x66\x69\x63\x69\x65\x6E\x74\x5F\x6D\x5F\x32\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("diffuse_coefficient_m_2 not found!")
                    try: 
                        Specular_Coefficient_M_2_Offset = shaderfile_read.index(b'\x00\x73\x70\x65\x63\x75\x6C\x61\x72\x5F\x63\x6F\x65\x66\x66\x69\x63\x69\x65\x6E\x74\x5F\x6D\x5F\x32\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("specular_coefficient_m_2 not found!")
                    try: 
                        Specular_Power_M_2_Offset = shaderfile_read.index(b'\x00\x73\x70\x65\x63\x75\x6C\x61\x72\x5F\x70\x6F\x77\x65\x72\x5F\x6D\x5F\x32\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("specular_power_m_2 not found!")
                    try:  
                        Specular_Tint_M_2_Offset = shaderfile_read.index(b'\x00\x73\x70\x65\x63\x75\x6C\x61\x72\x5F\x74\x69\x6E\x74\x5F\x6D\x5F\x32\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("specular_tint_m_2 not found!")
                    try: 
                        Fresnel_Curve_Steepness_M_2_Offset = shaderfile_read.index(b'\x00\x66\x72\x65\x73\x6e\x65\x6c\x5f\x63\x75\x72\x76\x65\x5f\x73\x74\x65\x65\x70\x6e\x65\x73\x73\x5f\x6d\x5f\x32\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("fresnel_curve_steepness_m_2 not found!")
                    try: 
                        Area_Specular_Contribution_M_2_Offset = shaderfile_read.index(b'\x00\x61\x72\x65\x61\x5F\x73\x70\x65\x63\x75\x6C\x61\x72\x5F\x63\x6F\x6E\x74\x72\x69\x62\x75\x74\x69\x6F\x6E\x5F\x6D\x5F\x32\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("area_specular_contribution_m_2 not found!")
                    try: 
                        Analytical_Specular_Contribution_M_2_Offset = shaderfile_read.index(b'\x00\x61\x6E\x61\x6C\x79\x74\x69\x63\x61\x6C\x5F\x73\x70\x65\x63\x75\x6C\x61\x72\x5F\x63\x6F\x6E\x74\x72\x69\x62\x75\x74\x69\x6F\x6E\x5F\x6D\x5F\x32\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("analytical_specular_contribution_m_2 not found!")
                    try: 
                        Environment_Specular_Contribution_M_2_Offset = shaderfile_read.index(b'\x00\x65\x6e\x76\x69\x72\x6f\x6e\x6d\x65\x6e\x74\x5f\x73\x70\x65\x63\x75\x6c\x61\x72\x5f\x63\x6f\x6e\x74\x72\x69\x62\x75\x74\x69\x6f\x6e\x5f\x6d\x5f\x32\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("environment_specular_contribution_m_2 not found!")
                    try: 
                        Self_Illum_Color_M_2_Offset = shaderfile_read.index(convert_to_hex("self_illum_color_m_2")) 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("self_illum_color_m_2 not found!")
                    try: 
                        Self_Illum_Intensity_M_2_Offset = shaderfile_read.index(convert_to_hex("self_illum_intensity_m_2")) 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("self_illum_intensity_m_2 not found!")  
                    try: 
                        Albedo_Specular_Tint_Blend_M_2_Offset = shaderfile_read.index(b'\x00\x61\x6c\x62\x65\x64\x6f\x5f\x73\x70\x65\x63\x75\x6c\x61\x72\x5f\x74\x69\x6e\x74\x5f\x62\x6c\x65\x6e\x64\x5f\x6d\x5f\x32\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("albedo_specular_tint_blend_m_2 not found!")
                    try: 
                        Diffuse_Coefficient_M_3_Offset = shaderfile_read.index(b'\x00\x64\x69\x66\x66\x75\x73\x65\x5F\x63\x6F\x65\x66\x66\x69\x63\x69\x65\x6E\x74\x5F\x6D\x5F\x33\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("diffuse_coefficient_m_3 not found!")
                    try: 
                        Specular_Coefficient_M_3_Offset = shaderfile_read.index(b'\x00\x73\x70\x65\x63\x75\x6C\x61\x72\x5F\x63\x6F\x65\x66\x66\x69\x63\x69\x65\x6E\x74\x5F\x6D\x5F\x33\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("specular_coefficient_m_3 not found!")
                    try: 
                        Specular_Power_M_3_Offset = shaderfile_read.index(b'\x00\x73\x70\x65\x63\x75\x6C\x61\x72\x5F\x70\x6F\x77\x65\x72\x5F\x6D\x5F\x33\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("specular_power_m_3 not found!")
                    try: 
                        Specular_Tint_M_3_Offset = shaderfile_read.index(b'\x00\x73\x70\x65\x63\x75\x6C\x61\x72\x5F\x74\x69\x6E\x74\x5F\x6D\x5F\x33\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("specular_tint_m_3 not found!")
                    try: 
                        Fresnel_Curve_Steepness_M_3_Offset = shaderfile_read.index(b'\x00\x66\x72\x65\x73\x6e\x65\x6c\x5f\x63\x75\x72\x76\x65\x5f\x73\x74\x65\x65\x70\x6e\x65\x73\x73\x5f\x6d\x5f\x33\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("fresnel_curve_steepness_m_3 not found!")
                    try: 
                        Area_Specular_Contribution_M_3_Offset = shaderfile_read.index(b'\x00\x61\x72\x65\x61\x5F\x73\x70\x65\x63\x75\x6C\x61\x72\x5F\x63\x6F\x6E\x74\x72\x69\x62\x75\x74\x69\x6F\x6E\x5F\x6D\x5F\x33\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("area_specular_contribution_m_3 not found!")
                    try: 
                        Analytical_Specular_Contribution_M_3_Offset = shaderfile_read.index(b'\x00\x61\x6E\x61\x6C\x79\x74\x69\x63\x61\x6C\x5F\x73\x70\x65\x63\x75\x6C\x61\x72\x5F\x63\x6F\x6E\x74\x72\x69\x62\x75\x74\x69\x6F\x6E\x5F\x6D\x5F\x33\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("analytical_specular_contribution_m_3 not found!")
                    try: 
                        Environment_Specular_Contribution_M_3_Offset = shaderfile_read.index(b'\x00\x65\x6e\x76\x69\x72\x6f\x6e\x6d\x65\x6e\x74\x5f\x73\x70\x65\x63\x75\x6c\x61\x72\x5f\x63\x6f\x6e\x74\x72\x69\x62\x75\x74\x69\x6f\x6e\x5f\x6d\x5f\x33\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("environment_specular_contribution_m_3 not found!")
                    try: 
                        Self_Illum_Color_M_3_Offset = shaderfile_read.index(convert_to_hex("self_illum_color_m_3")) 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("self_illum_color_m_3 not found!")
                    try: 
                        Self_Illum_Intensity_M_3_Offset = shaderfile_read.index(convert_to_hex("self_illum_intensity_m_3")) 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("self_illum_intensity_m_3 not found!")  
                    try: 
                        Albedo_Specular_Tint_Blend_M_3_Offset = shaderfile_read.index(b'\x00\x61\x6c\x62\x65\x64\x6f\x5f\x73\x70\x65\x63\x75\x6c\x61\x72\x5f\x74\x69\x6e\x74\x5f\x62\x6c\x65\x6e\x64\x5f\x6d\x5f\x33\x66\x72\x67\x74') 
                    except ValueError:
                        if(debug_textures_values_found != 0): 
                            log_to_file("albedo_specular_tint_blend_m_3 not found!")                
                


      
                                        #################
                                        #CATEGORY OPTIONS
                                        #################
                                      
                ### HALO 3 AND ODST CATEGORIES ###
                if (Game_Source == "H3" or Game_Source == "H3ODST"):
                    ########
                    #SHADERS
                    ########             
                    
                    #if Shader file is .shader
                    if (Shader_Type == 0):
                        #store category options for the material
                        log_to_file("")
                        log_to_file("--[Category Options]--")
                        if (CategoryOptions_Offset != 0):
                                shaderfile.seek(CategoryOptions_Offset + 0x22) #skips to start of Category options
                                ShaderItem.albedo_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.bump_mapping_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.alpha_test_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.specular_mask_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.material_model_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.environment_mapping_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.self_illumination_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.blend_mode_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.parallax_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.misc_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.distortion_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.soft_fade_option = int.from_bytes(shaderfile.read(2), 'little')
                                
                                log_to_file("albedo option: " + get_albedo_option(ShaderItem.albedo_option))
                                log_to_file("bump_mapping option: " + get_bump_mapping_option(ShaderItem.bump_mapping_option))
                                log_to_file("alpha_test option: " + get_alpha_test_option(ShaderItem.alpha_test_option))
                                log_to_file("specular_mask option: " + get_specular_mask_option(ShaderItem.specular_mask_option))
                                log_to_file("material_model option: " + get_material_model_option(ShaderItem.material_model_option))
                                log_to_file("environment_mapping option: " + get_environment_mapping_option(ShaderItem.environment_mapping_option))
                                log_to_file("self_illumination option: " + get_self_illumination_option(ShaderItem.self_illumination_option))
                                log_to_file("blend_mode option: " + get_blend_mode_option(ShaderItem.blend_mode_option))
                                log_to_file("parallax option: " + get_parallax_option(ShaderItem.parallax_option))
                                log_to_file("misc option: " + get_misc_option(ShaderItem.misc_option))
                                log_to_file("distortion option: " + get_parallax_option(ShaderItem.distortion_option))
                                log_to_file("soft fade option: " + get_misc_option(ShaderItem.soft_fade_option))

                    ################
                    #TERRAIN SHADERS
                    ################

                    #if Shader file is .shader_terrain
                    elif (Shader_Type == 1):
                        #store category options for the material
                        log_to_file("")
                        log_to_file("--[Category Options]--")
                        if (CategoryOptions_Offset != 0):
                                shaderfile.seek(CategoryOptions_Offset + 0x28) #skips to start of Category options
                                ShaderItem.blending_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.environment_mapping_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.material_0_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.material_1_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.material_2_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.material_3_option = int.from_bytes(shaderfile.read(2), 'little')
                                
                                log_to_file("blending option: " + get_blending_option(ShaderItem.blending_option))
                                log_to_file("environment_map option: " + get_environment_map_terr_option(ShaderItem.environment_mapping_option))
                                log_to_file("material_0 option: " + get_material_0_option(ShaderItem.material_0_option))
                                log_to_file("material_1 option: " + get_material_1_option(ShaderItem.material_1_option))
                                log_to_file("material_2 option: " + get_material_2_option(ShaderItem.material_2_option))
                                log_to_file("material_3 option: " + get_material_3_option(ShaderItem.material_3_option))

                    
                    ################
                    #FOLIAGE SHADERS
                    ################
                    #if Shader file is .shader_foliage
                    elif (Shader_Type == 2):
                        #store category options for the material
                        log_to_file("")
                        log_to_file("--[Category Options]--")
                        if (CategoryOptions_Offset != 0):
                                shaderfile.seek(CategoryOptions_Offset + 0x23) #skips to start of Category options
                                ShaderItem.albedo_option = int.from_bytes(shaderfile.read(2), 'little')                       
                                ShaderItem.alpha_test_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.material_model_option = int.from_bytes(shaderfile.read(2), 'little')
                                
                                log_to_file("albedo option: " + get_albedo_foliage_option(ShaderItem.albedo_option))
                                log_to_file("alpha_test option: " + get_alpha_foliage_option(ShaderItem.alpha_test_option))
                                log_to_file("material_model option: " + get_material_foliage_option(ShaderItem.material_model_option))

                    #################
                    #HALOGRAM SHADERS
                    #################
                    elif (Shader_Type == 3):
                        #store category options for the material
                        log_to_file("")
                        log_to_file("--[Category Options]--")
                        if (CategoryOptions_Offset != 0):
                                shaderfile.seek(CategoryOptions_Offset + 0x24) #skips to start of Category options
                                ShaderItem.albedo_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.self_illumination_option = int.from_bytes(shaderfile.read(2), 'little')   
                                ShaderItem.blend_mode_option = int.from_bytes(shaderfile.read(2), 'little')    
                                ShaderItem.misc_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.warp_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.overlay_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.edge_fade_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.distortion_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.soft_fade_option = int.from_bytes(shaderfile.read(2), 'little')

                                
                                log_to_file("albedo option: " + get_albedo_option(ShaderItem.albedo_option))
                                log_to_file("self_illumination option: " + get_halogram_self_illumination_option(ShaderItem.self_illumination_option))
                                log_to_file("blend_mode option: " + get_blend_mode_option(ShaderItem.blend_mode_option))                        
                                log_to_file("misc option: " + get_misc_option(ShaderItem.misc_option))                        
                                
                                log_to_file("warp_option option: " + get_warp_option(ShaderItem.warp_option))
                                log_to_file("overlay_option option: " + get_overlay_option(ShaderItem.overlay_option))
                                log_to_file("edge_fade_option option: " + get_edge_fade_option(ShaderItem.edge_fade_option))
                                log_to_file("distortion_option option: " + get_distortion_option(ShaderItem.distortion_option))
                                log_to_file("soft_fade_option option: " + get_soft_fade_option(ShaderItem.soft_fade_option))
                
                    #################
                    #Custom SHADERS
                    #################
                    #if Shader file is .shader_custom
                    elif (Shader_Type == 4):
                        #store category options for the material
                        log_to_file("")
                        log_to_file("--[Category Options]--")
                        if (CategoryOptions_Offset != 0):
                                shaderfile.seek(CategoryOptions_Offset + 0x22) #skips to start of Category options
                                ShaderItem.albedo_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.bump_mapping_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.alpha_test_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.specular_mask_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.material_model_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.environment_mapping_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.self_illumination_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.blend_mode_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.parallax_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.misc_option = int.from_bytes(shaderfile.read(2), 'little')
                                
                                log_to_file("albedo option: " + get_albedo_custom_option(ShaderItem.albedo_option))
                                log_to_file("bump_mapping option: " + get_bump_mapping_option(ShaderItem.bump_mapping_option))
                                log_to_file("alpha_test option: " + get_alpha_test_option(ShaderItem.alpha_test_option))
                                log_to_file("specular_mask option: " + get_specular_mask_option(ShaderItem.specular_mask_option))
                                log_to_file("material_model option: " + get_material_model_custom_option(ShaderItem.material_model_option))
                                log_to_file("environment_mapping option: " + get_environment_mapping_option(ShaderItem.environment_mapping_option))
                                log_to_file("self_illumination option: " + get_self_illumination_custom_option(ShaderItem.self_illumination_option))
                                log_to_file("blend_mode option: " + get_blend_mode_option(ShaderItem.blend_mode_option))
                                log_to_file("parallax option: " + get_parallax_option(ShaderItem.parallax_option))
                                log_to_file("misc option: " + get_misc_option(ShaderItem.misc_option))
                
                    #################
                    #Decal SHADERS
                    #################
                    #if Shader file is .shader_decal
                    elif (Shader_Type == 6):
                        #store category options for the material
                        log_to_file("")
                        log_to_file("--[Category Options]--")
                        if (CategoryOptions_Offset != 0):
                                shaderfile.seek(CategoryOptions_Offset + 0x21) #skips to start of Category options
                                ShaderItem.albedo_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.blend_mode_option = int.from_bytes(shaderfile.read(2), 'little')
                                #render pass skip 2 bytes
                                #specular skip 2 bytes
                                ShaderItem.bump_mapping_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.tinting_option = int.from_bytes(shaderfile.read(2), 'little')
                                
                                log_to_file("albedo option: " + get_h3_albedo_decal_option(ShaderItem.albedo_option))
                                log_to_file("blend_mode option: " + get_h3_blend_mode_decal_option(ShaderItem.blend_mode_option))
                                #render pass
                                #specular
                                log_to_file("bump_mapping option: " + get_h3_bump_mapping_decal_option(ShaderItem.bump_mapping_option))
                                log_to_file("tinting option: " + get_h3_tinting_decal_option(ShaderItem.tinting_option))
                
                ### HALO REACH CATEGORIES ###
                elif (Game_Source == "Reach"):
                    ########
                    #SHADERS
                    ########             
                    
                    #if Shader file is .shader
                    if (Shader_Type == 0):
                        #store category options for the material
                        log_to_file("")
                        log_to_file("--[Category Options]--")
                        if (CategoryOptions_Offset != 0):
                                shaderfile.seek(CategoryOptions_Offset + 0x2E) #skips to start of Category options
                                ShaderItem.albedo_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.bump_mapping_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.alpha_test_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.specular_mask_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.material_model_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.environment_mapping_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.self_illumination_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.blend_mode_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.parallax_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.misc_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.wetness_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.alpha_blend_source = int.from_bytes(shaderfile.read(2), 'little')
                                
                                log_to_file("albedo option: " + get_reach_albedo_option(ShaderItem.albedo_option))
                                log_to_file("bump_mapping option: " + get_reach_bump_mapping_option(ShaderItem.bump_mapping_option))
                                log_to_file("alpha_test option: " + get_alpha_test_option(ShaderItem.alpha_test_option))
                                log_to_file("specular_mask option: " + get_reach_specular_mask_option(ShaderItem.specular_mask_option))
                                log_to_file("material_model option: " + get_reach_material_model_option(ShaderItem.material_model_option))
                                log_to_file("environment_mapping option: " + get_environment_mapping_option(ShaderItem.environment_mapping_option))
                                log_to_file("self_illumination option: " + get_reach_self_illumination_option(ShaderItem.self_illumination_option))
                                log_to_file("blend_mode option: " + get_blend_mode_option(ShaderItem.blend_mode_option))
                                log_to_file("parallax option: " + get_parallax_option(ShaderItem.parallax_option))
                                log_to_file("misc option: " + get_reach_misc_option(ShaderItem.misc_option))
                                log_to_file("wetness option: " + get_reach_wetness_option(ShaderItem.wetness_option))
                                log_to_file("alpha blend source option: " + get_reach_alpha_blend_source_option(ShaderItem.alpha_blend_source_option))



                    ################
                    #TERRAIN SHADERS
                    ################

                    #if Shader file is .shader_terrain
                    elif (Shader_Type == 1):
                        #store category options for the material
                        log_to_file("")
                        log_to_file("--[Category Options]--")
                        if (CategoryOptions_Offset != 0):
                                shaderfile.seek(CategoryOptions_Offset + 0x28) #skips to start of Category options
                                ShaderItem.blending_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.environment_mapping_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.material_0_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.material_1_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.material_2_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.material_3_option = int.from_bytes(shaderfile.read(2), 'little')
                                
                                log_to_file("blending option: " + get_blending_option(ShaderItem.blending_option))
                                log_to_file("environment_map option: " + get_environment_map_terr_option(ShaderItem.environment_mapping_option))
                                log_to_file("material_0 option: " + get_material_0_option(ShaderItem.material_0_option))
                                log_to_file("material_1 option: " + get_material_1_option(ShaderItem.material_1_option))
                                log_to_file("material_2 option: " + get_material_2_option(ShaderItem.material_2_option))
                                log_to_file("material_3 option: " + get_material_3_option(ShaderItem.material_3_option))

                    
                    ################
                    #FOLIAGE SHADERS
                    ################
                    #if Shader file is .shader_terrain
                    elif (Shader_Type == 2):
                        #store category options for the material
                        log_to_file("")
                        log_to_file("--[Category Options]--")
                        if (CategoryOptions_Offset != 0):
                                shaderfile.seek(CategoryOptions_Offset + 0x23) #skips to start of Category options
                                ShaderItem.albedo_option = int.from_bytes(shaderfile.read(2), 'little')                       
                                ShaderItem.alpha_test_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.material_model_option = int.from_bytes(shaderfile.read(2), 'little')
                                
                                log_to_file("albedo option: " + get_albedo_foliage_option(ShaderItem.albedo_option))
                                log_to_file("alpha_test option: " + get_alpha_foliage_option(ShaderItem.alpha_test_option))
                                log_to_file("material_model option: " + get_material_foliage_option(ShaderItem.material_model_option))

                    #################
                    #HALOGRAM SHADERS
                    #################
                    if (Shader_Type == 3):
                        #store category options for the material
                        log_to_file("")
                        log_to_file("--[Category Options]--")
                        if (CategoryOptions_Offset != 0):
                                shaderfile.seek(CategoryOptions_Offset + 0x24) #skips to start of Category options
                                ShaderItem.albedo_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.self_illumination_option = int.from_bytes(shaderfile.read(2), 'little')   
                                ShaderItem.blend_mode_option = int.from_bytes(shaderfile.read(2), 'little')    
                                ShaderItem.misc_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.warp_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.overlay_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.edge_fade_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.distortion_option = int.from_bytes(shaderfile.read(2), 'little')
                                ShaderItem.soft_fade_option = int.from_bytes(shaderfile.read(2), 'little')

                                
                                log_to_file("albedo option: " + get_albedo_option(ShaderItem.albedo_option))
                                log_to_file("self_illumination option: " + get_halogram_self_illumination_option(ShaderItem.self_illumination_option))
                                log_to_file("blend_mode option: " + get_blend_mode_option(ShaderItem.blend_mode_option))                        
                                log_to_file("misc option: " + get_misc_option(ShaderItem.misc_option))                        
                                
                                log_to_file("warp_option option: " + get_warp_option(ShaderItem.warp_option))
                                log_to_file("overlay_option option: " + get_overlay_option(ShaderItem.overlay_option))
                                log_to_file("edge_fade_option option: " + get_edge_fade_option(ShaderItem.edge_fade_option))
                                log_to_file("distortion_option option: " + get_distortion_option(ShaderItem.distortion_option))
                                log_to_file("soft_fade_option option: " + get_soft_fade_option(ShaderItem.soft_fade_option))




                #Gather needed texture list
                ShaderItem = build_texture_list(ShaderItem, Shader_Type)

                                        #############
                                        #TEXTURE DATA
                                        #############
                                        
                ########
                # .SHADER FILES
                ########
                
                log_to_file("")
                log_to_file("--[Existing Texture Types]--")
                if (BaseMap_Offset != 0):
                    #log_to_file("base_map offset: " + str(BaseMap_Offset))
                    log_to_file("")
                    log_to_file("[base_map]")
                    #DirOffset = shaderfile.tell()
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    Bitmap.equi_paths = []
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, BaseMap_Offset + 0x18 + 0x1) 
                    log_to_file("Dir: " + Bitmap.directory)
                    Bitmap.type = "base_map"
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1                 

                    if(DefaultNeeded != 1):
                        #try to do something with the file to get it to see if it exists
                        handle_missing_texture(Bitmap.directory, bpy.context.preferences.addons[__name__].preferences.export_path + "/" + Bitmap.directory)    
                        
                        try:
                            if (has_prefix != True):
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                            else:
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Raw_Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "height")
                        except ValueError:
                            log_to_file("Bitmap Directory not referenced. Please use Default Data")
                    
                    #get scaling data for bitmap
                    Bitmap = get_scale(shaderfile, (BaseMap_Offset + 0x18 + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 
                        
                    #check scaling is correct:
                    log_to_file("[" + Bitmap.type + "] Scale: " + str(Bitmap.scale_xy))
                    
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    DefaultNeeded = 0
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "base_map")):
                        log_to_file("")
                        log_to_file("[base_map]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        Bitmap.equi_paths = []
                        
                        Bitmap.type = "base_map"
                        Bitmap.directory = correct_default_dir("base_map")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)
                        
                if (DetailMap_Offset != 0):
                    #log_to_file("detail_map offset: " + str(DetailMap_Offset))
                    log_to_file("")
                    log_to_file("[detail_map]")
                    shaderfile.seek(DetailMap_Offset + 0x1A + 0x1)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    Bitmap.equi_paths = []
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, DetailMap_Offset + 0x1A + 0x1)
                    log_to_file("Dir: " + Bitmap.directory)
                    Bitmap.type = "detail_map"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1                 

                    
                    #try to correct directory empty issue from default values
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "  "):
                        #replace Bitmap.directory with default .bitmap directory
                        if(uses_gray_50(Bitmap.type) == True):
                            Bitmap.directory = "shaders/default_bitmaps/bitmaps/gray_50_percent"
                        elif(uses_color_white(Bitmap.type) == True):
                            Bitmap.directory = "shaders/default_bitmaps/bitmaps/color_white"
                        elif(uses_default_vector(Bitmap.type) == True):
                            Bitmap.directory = "shaders/default_bitmaps/bitmaps/default_vector"
                        elif(uses_reference_grids(Bitmap.type) == True):    
                            Bitmap.directory = "shaders/default_bitmaps/bitmaps/reference_grids"
                        elif(uses_default_alpha_test(Bitmap.type) == True):    
                            Bitmap.directory = "shaders/default_bitmaps/bitmaps/default_alpha_test"
                        elif(uses_default_dynamic_cube_map(Bitmap.type) == True):    
                            Bitmap.directory =  "shaders/default_bitmaps/bitmaps/default_dynamic_cube_map"
                        elif(uses_color_red(Bitmap.type) == True):    
                            Bitmap.directory = "shaders/default_bitmaps/bitmaps/color_red"
                        elif(uses_monochrome_alpha_grid(Bitmap.type) == True):    
                            Bitmap.directory = "shaders/default_bitmaps/bitmaps/monochrome_alpha_grid"
                        else:
                            Bitmap.directory = "shaders/default_bitmaps/bitmaps/default_detail"
                



                #if((Bitmap.type != "detail_map" and ShaderItem.detail_map_option != 0 ):
                    if (DefaultNeeded != 1):
                        #try to do something with the file to get it to see if it exists
                        handle_missing_texture(Bitmap.directory, bpy.context.preferences.addons[__name__].preferences.export_path + "/" + Bitmap.directory)  
                    
                        try:
                            if (has_prefix != True):
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                            else:
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Raw_Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "height")
                        except ValueError:
                            log_to_file("Bitmap Directory not referenced. Please use Default Data")

                    #get scaling data for bitmap
                    Bitmap = get_scale(shaderfile, (DetailMap_Offset + 0x1A + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    #check scaling is correct:
                    log_to_file("[" + Bitmap.type + "] Scale: " + str(Bitmap.scale_xy))

                    DefaultNeeded = 0
                
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "detail_map")):
                        log_to_file("")
                        log_to_file("[detail_map]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        Bitmap.equi_paths = []
                        
                        Bitmap.type = "detail_map"
                        Bitmap.directory = correct_default_dir("detail_map")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)
                
                if (DetailMap2_Offset != 0):
                    #log_to_file("detail_map2 offset: " + str(DetailMap2_Offset)) 
                    log_to_file("")                
                    log_to_file("[detail_map2]")                
                    #shaderfile.seek(DetailMap2_Offset + 0x1B)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    Bitmap.equi_paths = []
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, DetailMap2_Offset + 0x1B + 0x1)
                    log_to_file("Dir: " + Bitmap.directory)
                    Bitmap.type = "detail_map2"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1                 

                    if (DefaultNeeded != 1):
                        #try to do something with the file to get it to see if it exists
                        handle_missing_texture(Bitmap.directory, bpy.context.preferences.addons[__name__].preferences.export_path + "/" + Bitmap.directory)  
                    
                        try:
                            if (has_prefix != True):
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                            else:
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Raw_Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "height")
                        except OSError:
                            log_to_file("Bitmap Directory not referenced. Please use Default Data")
                   
                    Bitmap = get_scale(shaderfile, (DetailMap2_Offset + 0x1B + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    #check scaling is correct:
                    log_to_file("[" + Bitmap.type + "] Scale: " + str(Bitmap.scale_xy))

                    DefaultNeeded = 0
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "detail_map2")):
                        log_to_file("")
                        log_to_file("[detail_map2]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        Bitmap.equi_paths = []
                        
                        Bitmap.type = "detail_map2"
                        Bitmap.directory = correct_default_dir("detail_map2")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)
                
                if (DetailMap3_Offset != 0):
                    #log_to_file("detail_map3 offset: " + str(DetailMap3_Offset))
                    log_to_file("")
                    log_to_file("[detail_map3]") 
                    shaderfile.seek(DetailMap3_Offset + 0x1B + 0x1)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    Bitmap.equi_paths = []
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, DetailMap3_Offset + 0x1B + 0x1)
                    log_to_file("Dir: " + Bitmap.directory)
                    Bitmap.type = "detail_map3"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1 
                         
                    if (DefaultNeeded != 1):
                        #try to do something with the file to get it to see if it exists
                        handle_missing_texture(Bitmap.directory, bpy.context.preferences.addons[__name__].preferences.export_path + "/" + Bitmap.directory)  
                    
                        try:
                            if (has_prefix != True):
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                            else:
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Raw_Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "height")
                        except ValueError:
                            log_to_file("Bitmap Directory not referenced. Please use Default Data")
                   
                    Bitmap = get_scale(shaderfile, (DetailMap3_Offset + 0x1B + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    #check scaling is correct:
                    log_to_file("[" + Bitmap.type + "] Scale: " + str(Bitmap.scale_xy))

                    DefaultNeeded = 0
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "detail_map3")):
                        log_to_file("")
                        log_to_file("[detail_map3]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        Bitmap.equi_paths = []
                        
                        Bitmap.type = "detail_map3"
                        Bitmap.directory = correct_default_dir("detail_map3")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)

                if (DetailMapOverlay_Offset != 0):
                    
                    log_to_file("")
                    log_to_file("[detail_map_overlay]") 
                    shaderfile.seek(DetailMapOverlay_Offset + 0x22 + 0x1)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    Bitmap.equi_paths = []
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, DetailMapOverlay_Offset + 0x22 + 0x1)
                    log_to_file("Dir: " + Bitmap.directory)
                    Bitmap.type = "detail_map_overlay"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1 
                         
                    if (DefaultNeeded != 1):
                        #try to do something with the file to get it to see if it exists
                        handle_missing_texture(Bitmap.directory, bpy.context.preferences.addons[__name__].preferences.export_path + "/" + Bitmap.directory)  
                    
                        try:
                            if (has_prefix != True):
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                            else:
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Raw_Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "height")
                        except ValueError:
                            log_to_file("Bitmap Directory not referenced. Please use Default Data")
                   
                    Bitmap = get_scale(shaderfile, (DetailMapOverlay_Offset + 0x22 + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    #check scaling is correct:
                    log_to_file("[" + Bitmap.type + "] Scale: " + str(Bitmap.scale_xy))

                    DefaultNeeded = 0
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "detail_map_overlay")):
                        log_to_file("")
                        log_to_file("[detail_map_overlay]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        Bitmap.equi_paths = []
                        
                        Bitmap.type = "detail_map_overlay"
                        Bitmap.directory = correct_default_dir("detail_map_overlay")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)


                if (SpecularMaskTexture_Offset != 0):
                    #log_to_file("specular_mask_texture offset: " + str(SpecularMaskTexture_Offset))
                    log_to_file("")
                    log_to_file("[specular_mask_texture]") 
                    shaderfile.seek(SpecularMaskTexture_Offset + 0x25 + 0x1)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    Bitmap.equi_paths = []
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, SpecularMaskTexture_Offset + 0x25 + 0x1)
                    log_to_file("Dir: " + Bitmap.directory)
                    Bitmap.type = "specular_mask_texture"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1 

                    if (DefaultNeeded != 1):
                        #try to do something with the file to get it to see if it exists
                        handle_missing_texture(Bitmap.directory, bpy.context.preferences.addons[__name__].preferences.export_path + "/" + Bitmap.directory)  
                    
                        try:
                            if (has_prefix != True):
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                            else:
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Raw_Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "height")
                        except OSError:
                            log_to_file("Bitmap Directory not referenced. Please use Default Data")
                   
                    Bitmap = get_scale(shaderfile, (SpecularMaskTexture_Offset + 0x25 + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    #check scaling is correct:
                    log_to_file("[" + Bitmap.type + "] Scale: " + str(Bitmap.scale_xy))

                    DefaultNeeded = 0
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "specular_mask_texture")):
                        log_to_file("")
                        log_to_file("[specular_mask_texture]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        Bitmap.equi_paths = []
                        
                        Bitmap.type = "specular_mask_texture"
                        Bitmap.directory = correct_default_dir("specular_mask_texture")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)
    
                if (ChangeColorMap_Offset != 0):
                    #log_to_file("change_color_map offset: " + str(ChangeColorMap_Offset))
                    log_to_file("")
                    log_to_file("[change_color_map]") 
                    shaderfile.seek(ChangeColorMap_Offset + 0x20 + 0x1)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    Bitmap.equi_paths = []
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, ChangeColorMap_Offset + 0x20 + 0x1)
                    log_to_file("Dir: " + Bitmap.directory)
                    Bitmap.type = "change_color_map"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1 

                    if (DefaultNeeded != 1):
                        #try to do something with the file to get it to see if it exists
                        handle_missing_texture(Bitmap.directory, bpy.context.preferences.addons[__name__].preferences.export_path + "/" + Bitmap.directory)  
                    
                        try:
                            if (has_prefix != True):
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                            else:
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Raw_Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "height")
                        except OSError:
                            log_to_file("Bitmap Directory not referenced. Please use Default Data")
                   
                    Bitmap = get_scale(shaderfile, (ChangeColorMap_Offset + 0x20 + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    #check scaling is correct:
                    log_to_file("[" + Bitmap.type + "] Scale: " + str(Bitmap.scale_xy))

                    DefaultNeeded = 0
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "change_color_map")):
                        log_to_file("")
                        log_to_file("[change_color_map]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        Bitmap.equi_paths = []
                        
                        Bitmap.type = "change_color_map"
                        Bitmap.directory = correct_default_dir("change_color_map")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)
                        
                if (ColorMaskMap_Offset != 0):
                    #log_to_file("color_mask_map offset: " + str(ColorMaskMap_Offset))
                    log_to_file("")
                    log_to_file("[color_mask_map]") 
                    shaderfile.seek(ColorMaskMap_Offset + 0x1E + 0x1)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    Bitmap.equi_paths = []
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, ColorMaskMap_Offset + 0x1E + 0x1)
                    log_to_file("Dir: " + Bitmap.directory)
                    Bitmap.type = "color_mask_map"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1 

                    if (DefaultNeeded != 1):
                        #try to do something with the file to get it to see if it exists
                        handle_missing_texture(Bitmap.directory, bpy.context.preferences.addons[__name__].preferences.export_path + "/" + Bitmap.directory)  
                    
                        try:
                            if (has_prefix != True):
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                            else:
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Raw_Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "height")
                        except OSError:
                            log_to_file("Bitmap Directory not referenced. Please use Default Data")
                   
                    Bitmap = get_scale(shaderfile, (ColorMaskMap_Offset + 0x1E + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    #check scaling is correct:
                    log_to_file("[" + Bitmap.type + "] Scale: " + str(Bitmap.scale_xy))

                    DefaultNeeded = 0
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "color_mask_map")):
                        log_to_file("")
                        log_to_file("[color_mask_map]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        Bitmap.equi_paths = []
                        
                        Bitmap.type = "color_mask_map"
                        Bitmap.directory = correct_default_dir("color_mask_map")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)

                if (BumpMap_Offset != 0):
                    #log_to_file("bump_map offset: " + str(BumpMap_Offset))
                    log_to_file("")
                    log_to_file("[bump_map]") 
                    shaderfile.seek(BumpMap_Offset + 0x18 + 0x1)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    Bitmap.equi_paths = []
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, BumpMap_Offset + 0x18 + 0x1)
                    log_to_file("Dir: " + Bitmap.directory)
                    Bitmap.type = "bump_map"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1                 
                    
                    #log_to_file("bump mapping option: " + str(ShaderItem.bump_mapping_option))
                    if not (ShaderItem.bump_mapping_option == 0):
                        if (DefaultNeeded != 1):
                            #try to do something with the file to get it to see if it exists
                            handle_missing_texture(Bitmap.directory, bpy.context.preferences.addons[__name__].preferences.export_path + "/" + Bitmap.directory)  
                        
                            try:
                                if (has_prefix != True):
                                    #get Curve for bitmap
                                    Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                                    
                                    #Get Resolution of bitmap
                                    Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                                    Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                                else:
                                    #get Curve for bitmap
                                    Bitmap.curve_option = get_bitmap_curve(Raw_Tag_Root + Bitmap.directory + ".bitmap")
                                    
                                    #Get Resolution of bitmap
                                    Bitmap.width = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "width")
                                    Bitmap.height = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "height")
                            except OSError:
                                log_to_file("Bitmap Directory not referenced. Please use Default Data")
                    

                    Bitmap = get_scale(shaderfile, (BumpMap_Offset + 0x18 + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    #check scaling is correct:
                    log_to_file("[" + Bitmap.type + "] Scale: " + str(Bitmap.scale_xy))

                    DefaultNeeded = 0
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "bump_map")):
                        log_to_file("")
                        log_to_file("[bump_map]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        Bitmap.equi_paths = []
                        
                        Bitmap.type = "bump_map"
                        Bitmap.directory = correct_default_dir("bump_map")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)

                if (BumpDetailMap_Offset != 0):
                    #log_to_file("bump_detail_map offset: " + str(BumpDetailMap_Offset))
                    log_to_file("")
                    log_to_file("[bump_detail_map]")                
                    shaderfile.seek(BumpDetailMap_Offset + 0x1F + 0x1)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    Bitmap.equi_paths = []
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, BumpDetailMap_Offset + 0x1F + 0x1)
                    log_to_file("Dir: " + Bitmap.directory)
                    Bitmap.type = "bump_detail_map"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1 
                    
                    #do this stuff if certain options aren't turned off
                    if (ShaderItem.environment_mapping_option != 1 and ShaderItem.environment_mapping_option != 0):
                        if (DefaultNeeded != 1):
                            #try to do something with the file to get it to see if it exists
                            handle_missing_texture(Bitmap.directory, bpy.context.preferences.addons[__name__].preferences.export_path + "/" + Bitmap.directory)  
                        
                            try:
                                if (has_prefix != True):
                                    #get Curve for bitmap
                                    Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                                    
                                    #Get Resolution of bitmap
                                    Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                                    Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                                else:
                                    #get Curve for bitmap
                                    Bitmap.curve_option = get_bitmap_curve(Raw_Tag_Root + Bitmap.directory + ".bitmap")
                                    
                                    #Get Resolution of bitmap
                                    Bitmap.width = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "width")
                                    Bitmap.height = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "height")
                            except OSError:
                                log_to_file("Bitmap Directory not referenced. Please use Default Data")
                        
                    Bitmap = get_scale(shaderfile, (BumpDetailMap_Offset + 0x1F + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    #check scaling is correct:
                    log_to_file("[" + Bitmap.type + "] Scale: " + str(Bitmap.scale_xy))

                    DefaultNeeded = 0
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "bump_detail_map")):
                        log_to_file("")
                        log_to_file("[bump_detail_map]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        Bitmap.equi_paths = []
                        
                        Bitmap.type = "bump_detail_map"
                        Bitmap.directory = correct_default_dir("bump_detail_map")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)

                if (EnvironmentMap_Offset != 0):
                    #log_to_file("environment_map offset: " + str(EnvironmentMap_Offset))
                    log_to_file("")
                    log_to_file("[environment_map]")                
                    shaderfile.seek(EnvironmentMap_Offset + 0x1F + 0x1)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    Bitmap.equi_paths = []
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, EnvironmentMap_Offset + 0x1F + 0x1)
                    log_to_file("Dir: " + Bitmap.directory)
                    Bitmap.type = "environment_map"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    
                    if(Bitmap.directory != "" and Bitmap.directory != " " and Bitmap.directory != "   " and ShaderItem.environment_mapping_option != 0 and ShaderItem.environment_mapping_option != 2):
                        #try to do something with the file to get it to see if it exists
                        handle_missing_texture(Bitmap.directory, bpy.context.preferences.addons[__name__].preferences.export_path + "/" + Bitmap.directory)  
                        
                        #Grab the Environment Map and convert it to equirectangular
                        Bitmap.equi_paths = convert_cubemap_to_equirectangular(Bitmap.directory)
                    
                    
                    
                    
                    
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1 
                         
                    #if the environment_map is default then use default cubemap     
                    if (DefaultNeeded == 1):
                        default_dir = correct_default_dir(Bitmap.type)
                        
                        #try to do something with the file to get it to see if it exists
                        #handle_missing_texture(Bitmap.directory, bpy.context.preferences.addons[__name__].preferences.export_path + "/" + default_dir)  
                        
                        #Grab the Environment Map and convert it to equirectangular
                        Bitmap.equi_paths = convert_cubemap_to_equirectangular(default_dir)
                        
                        Bitmap.directory = default_dir
                        
                    ShaderItem.bitmap_list.append(Bitmap)
                    
                    if (ShaderItem.environment_mapping_option == 3):
                        
                        if (FlatEnvironmentMap_Offset != 0):
                            #log_to_file("environment_map offset: " + str(EnvironmentMap_Offset))
                            log_to_file("")
                            log_to_file("[flat_environment_map]")                
                            shaderfile.seek(FlatEnvironmentMap_Offset + 0x24 + 0x1)
                            
                            #clear old bitmap data
                            Bitmap = bitmap()
                            Bitmap.directory = ""
                            Bitmap.type = ""
                            Bitmap.curve_option = 0
                            Bitmap.width = 0
                            Bitmap.height = 0
                            Bitmap.equi_paths = []
                            
                            #save current data
                            Bitmap.directory = get_dir(shaderfile, FlatEnvironmentMap_Offset + 0x24 + 0x1)
                            log_to_file("Dir: " + Bitmap.directory)
                            Bitmap.type = "flat_environment_map"
                            ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                            ShaderItem.bitmap_list.append(Bitmap)
                            
                            #resets DefaultNeeded value due to it being in another layer starting over
                            DefaultNeeded = 0
                            
                            if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                                DefaultNeeded = 1 

                            if (ShaderItem.environment_mapping_option != 0):
                                if(DefaultNeeded != 1):
                                    #try to do something with the file to get it to see if it exists
                                    handle_missing_texture(Bitmap.directory, bpy.context.preferences.addons[__name__].preferences.export_path + "/" + Bitmap.directory)  
                                
                                    try:
                                        if (has_prefix != True):
                                            #get Curve for bitmap
                                            Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                                            
                                            #Get Resolution of bitmap
                                            Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                                            Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                                        else:
                                            #get Curve for bitmap
                                            Bitmap.curve_option = get_bitmap_curve(Raw_Tag_Root + Bitmap.directory + ".bitmap")
                                            
                                            #Get Resolution of bitmap
                                            Bitmap.width = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "width")
                                            Bitmap.height = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "height")
                                    except OSError:
                                        log_to_file("Bitmap Directory not referenced. Please use Default Data")
                               
                                Bitmap = get_scale(shaderfile, (FlatEnvironmentMap_Offset + 0x24 + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                                #check scaling is correct:
                                log_to_file("[" + Bitmap.type + "] Scale: " + str(Bitmap.scale_xy))
                                
                        
                    elif (ShaderItem.environment_mapping_option != 0):
                        if (DefaultNeeded != 1):
                            #try to do something with the file to get it to see if it exists
                            handle_missing_texture(Bitmap.directory, bpy.context.preferences.addons[__name__].preferences.export_path + "/" + Bitmap.directory)  
                        
                            try:
                                if (has_prefix != True):
                                    #get Curve for bitmap
                                    Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                                    
                                    #Get Resolution of bitmap
                                    Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                                    Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                                else:
                                    #get Curve for bitmap
                                    Bitmap.curve_option = get_bitmap_curve(Raw_Tag_Root + Bitmap.directory + ".bitmap")
                                    
                                    #Get Resolution of bitmap
                                    Bitmap.width = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "width")
                                    Bitmap.height = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "height")
                            except OSError:
                                log_to_file("Bitmap Directory not referenced. Please use Default Data")
                            
                        #get scaling data for bitmap
                        Bitmap = get_scale(shaderfile, (EnvironmentMap_Offset + 0x1F + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                        #check scaling is correct:
                        log_to_file("[" + Bitmap.type + "] Scale: " + str(Bitmap.scale_xy))
                  
                    #Probably can delete this last if statement section
                    # if (DefaultNeeded != 1):
                            # try:
                                # #get Curve for bitmap
                                # Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                                
                                # #Get Resolution of bitmap
                                # Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                                # Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                            
                                # if(ShaderItem.environment_mapping_option != 0 and ShaderItem.environment_mapping_option != 2):
                                    # #Grab the Environment Map and convert it to equirectangular
                                    # Bitmap.equi_paths = convert_cubemap_to_equirectangular(Bitmap.directory)
                            
                            # except OSError:
                                # log_to_file("Bitmap Directory not referenced. Please use Default Data")
                    
                    
                    
                    DefaultNeeded = 0

                if (SelfIllumMap_Offset != 0):
                    #log_to_file("self_illum_map offset: " + str(SelfIllumMap_Offset))
                    log_to_file("")
                    log_to_file("[self_illum_map]") 
                    shaderfile.seek(SelfIllumMap_Offset + 0x1E + 0x1)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    Bitmap.equi_paths = []
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, SelfIllumMap_Offset + 0x1E + 0x1)
                    log_to_file("Dir: " + Bitmap.directory)
                    Bitmap.type = "self_illum_map"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1 
                
                    if (ShaderItem.self_illumination_option != 0):
                        if(DefaultNeeded != 1):
                            #try to do something with the file to get it to see if it exists
                            handle_missing_texture(Bitmap.directory, bpy.context.preferences.addons[__name__].preferences.export_path + "/" + Bitmap.directory)  
                        
                            try:
                                if (has_prefix != True):
                                    #get Curve for bitmap
                                    Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                                    
                                    #Get Resolution of bitmap
                                    Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                                    Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                                else:
                                    #get Curve for bitmap
                                    Bitmap.curve_option = get_bitmap_curve(Raw_Tag_Root + Bitmap.directory + ".bitmap")
                                    
                                    #Get Resolution of bitmap
                                    Bitmap.width = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "width")
                                    Bitmap.height = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "height")
                            except OSError:
                                log_to_file("Bitmap Directory not referenced. Please use Default Data")
                    
                    #get scaling data for bitmap
                    Bitmap = get_scale(shaderfile, (SelfIllumMap_Offset + 0x1E + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    #check scaling is correct:
                    log_to_file("[" + Bitmap.type + "] Scale: " + str(Bitmap.scale_xy))

                    DefaultNeeded = 0
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "self_illum_map")):
                        log_to_file("")
                        log_to_file("[self_illum_map]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        Bitmap.equi_paths = []
                        
                        Bitmap.type = "self_illum_map"
                        Bitmap.directory = correct_default_dir("self_illum_map")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)
                
                if (SelfIllumDetailMap_Offset != 0):
                    #log_to_file("self_illum_detail_map offset: " + str(SelfIllumDetailMap_Offset))
                    log_to_file("")
                    log_to_file("[self_illum_detail_map]")
                    shaderfile.seek(SelfIllumDetailMap_Offset + 0x25 + 0x1)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    Bitmap.equi_paths = []
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, SelfIllumDetailMap_Offset + 0x25 + 0x1)
                    log_to_file("Dir: " + Bitmap.directory)
                    Bitmap.type = "self_illum_detail_map"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1 
                    
                    if(DefaultNeeded != 1 and ShaderItem.self_illumination_option != 0 and  ShaderItem.self_illumination_option != 1):
                        #try to do something with the file to get it to see if it exists
                        handle_missing_texture(Bitmap.directory, bpy.context.preferences.addons[__name__].preferences.export_path + "/" + Bitmap.directory)  
                    
                        try:
                            if (has_prefix != True):
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                            else:
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Raw_Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "height")
                        except OSError:
                            log_to_file("Bitmap Directory not referenced. Please use Default Data")
                    
                    #get scaling data for bitmap
                    Bitmap = get_scale(shaderfile, (SelfIllumDetailMap_Offset + 0x25 + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    #check scaling is correct:
                    log_to_file("[" + Bitmap.type + "] Scale: " + str(Bitmap.scale_xy))

                    DefaultNeeded = 0
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "self_illum_detail_map")):
                        log_to_file("")
                        log_to_file("[self_illum_detail_map]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        Bitmap.equi_paths = []
                        
                        Bitmap.type = "self_illum_detail_map"
                        Bitmap.directory = correct_default_dir("self_illum_detail_map")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)

                #ALPHA_TEST_MAP
                if (AlphaTestMap_Offset != 0):
                    #log_to_file("base_map offset: " + str(BaseMap_Offset))
                    log_to_file("")
                    log_to_file("[alpha_test_map]")
                    #DirOffset = shaderfile.tell()
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    Bitmap.equi_paths = []
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, AlphaTestMap_Offset + 0x1E + 0x1)
                    log_to_file("Dir: " + Bitmap.directory)
                    Bitmap.type = "alpha_test_map"
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1                 

                    #store the alpha_test_map directory for later
                    if(DefaultNeeded != 1):
                        ShaderItem.alpha_bitmap_dir = Bitmap.directory

                    if(DefaultNeeded != 1):
                        #try to do something with the file to get it to see if it exists
                        handle_missing_texture(Bitmap.directory, bpy.context.preferences.addons[__name__].preferences.export_path + "/" + Bitmap.directory)  
                    
                        try:
                            if (has_prefix != True):
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                            else:
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Raw_Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "height")
                        except OSError:
                            log_to_file("Bitmap Directory not referenced. Please use Default Data")
                    
                    #get scaling data for bitmap
                    Bitmap = get_scale(shaderfile, (AlphaTestMap_Offset + 0x1E + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    #check scaling is correct:
                    log_to_file("[" + Bitmap.type + "] Scale: " + str(Bitmap.scale_xy))
                        
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    
                    DefaultNeeded = 0

                #Check for material_texture
                ShaderItem = Add_Texture_Support(MaterialTexture_Offset, "material_texture", shaderfile, ShaderItem, Tag_Root, Raw_Tag_Root)
                
                #Check for spec_tint_map
                ShaderItem = Add_Texture_Support(SpecTintMap_Offset, "spec_tint_map", shaderfile, ShaderItem, Tag_Root, Raw_Tag_Root)

                #Check for specular_map
                ShaderItem = Add_Texture_Support(SpecularMap_Offset, "specular_map", shaderfile, ShaderItem, Tag_Root, Raw_Tag_Root)
                
                #Check for occlusion_parameter_map
                ShaderItem = Add_Texture_Support(OcclusionParameterMap_Offset, "occlusion_parameter_map", shaderfile, ShaderItem, Tag_Root, Raw_Tag_Root)
                
                #Check for subsurface_map
                ShaderItem = Add_Texture_Support(SubsurfaceMap_Offset, "subsurface_map", shaderfile, ShaderItem, Tag_Root, Raw_Tag_Root)
                
                #Check for transparence_map
                ShaderItem = Add_Texture_Support(TransparenceMap_Offset, "transparence_map", shaderfile, ShaderItem, Tag_Root, Raw_Tag_Root)
                
                #Check for pallete
                ShaderItem = Add_Texture_Support(Pallete_Offset, "pallete", shaderfile, ShaderItem, Tag_Root, Raw_Tag_Root)
                
                #Check for alpha_map
                ShaderItem = Add_Texture_Support(AlphaMap_Offset, "alpha_map", shaderfile, ShaderItem, Tag_Root, Raw_Tag_Root)
                
                #################
                #TERRAIN SHADERS
                #################
                
                #BLEND_MAP OFFSET
                if (Blend_Map_Offset != 0):
                    #log_to_file("self_illum_map offset: " + str(SelfIllumMap_Offset))
                    log_to_file("")
                    log_to_file("[blend_map]") 
                    shaderfile.seek(Blend_Map_Offset + 0x10 + 0x9 + 0x1)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    Bitmap.equi_paths = []
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, Blend_Map_Offset + 0x10 + 0x9 + 0x1)
                    log_to_file("Dir: " + Bitmap.directory)
                    Bitmap.type = "blend_map"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1 
                
                    if(DefaultNeeded != 1):
                        #try to do something with the file to get it to see if it exists
                        handle_missing_texture(Bitmap.directory, bpy.context.preferences.addons[__name__].preferences.export_path + "/" + Bitmap.directory)  
                    
                        try:
                            if (has_prefix != True):
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                            else:
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Raw_Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "height")
                        except OSError:
                            log_to_file("Bitmap Directory not referenced. Please use Default Data")
                    
                    #get scaling data for bitmap
                    Bitmap = get_scale(shaderfile, (Blend_Map_Offset + 0x10 + 0x9 + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    #check scaling is correct:
                    log_to_file("[" + Bitmap.type + "] Scale: " + str(Bitmap.scale_xy))

                    DefaultNeeded = 0
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "blend_map")):
                        log_to_file("")
                        log_to_file("[blend_map]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        Bitmap.equi_paths = []
                        
                        Bitmap.type = "blend_map"
                        Bitmap.directory = correct_default_dir("blend_map")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)
                
                #BASE_MAP_M_0 OFFSET
                if (Base_Map_M_0_Offset != 0):
                    #log_to_file("self_illum_map offset: " + str(SelfIllumMap_Offset))
                    log_to_file("")
                    log_to_file("[base_map_m_0]") 
                    shaderfile.seek(Base_Map_M_0_Offset + 0x10 + 0xC + 0x1)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    Bitmap.equi_paths = []
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, Base_Map_M_0_Offset + 0x10 + 0xC + 0x1)
                    log_to_file("Dir: " + Bitmap.directory)
                    Bitmap.type = "base_map_m_0"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1 
                
                    if(DefaultNeeded != 1):
                        #try to do something with the file to get it to see if it exists
                        handle_missing_texture(Bitmap.directory, bpy.context.preferences.addons[__name__].preferences.export_path + "/" + Bitmap.directory)  
                    
                        try:
                            if (has_prefix != True):
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                            else:
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Raw_Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "height")
                        except OSError:
                            log_to_file("Bitmap Directory not referenced. Please use Default Data")
                    
                    #get scaling data for bitmap
                    Bitmap = get_scale(shaderfile, (Base_Map_M_0_Offset + 0x10 + 0xC + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    #check scaling is correct:
                    log_to_file("[" + Bitmap.type + "] Scale: " + str(Bitmap.scale_xy))

                    DefaultNeeded = 0            
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "base_map_m_0")):
                        log_to_file("")
                        log_to_file("[base_map_m_0]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        Bitmap.equi_paths = []
                        
                        Bitmap.type = "base_map_m_0"
                        Bitmap.directory = correct_default_dir("base_map_m_0")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)
                
                #DETAIL_MAP_M_0 OFFSET
                if (Detail_Map_M_0_Offset != 0):
                    #log_to_file("self_illum_map offset: " + str(SelfIllumMap_Offset))
                    log_to_file("")
                    log_to_file("[detail_map_m_0]") 
                    shaderfile.seek(Detail_Map_M_0_Offset + 0x10 + 0xE + 0x1)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    Bitmap.equi_paths = []
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, Detail_Map_M_0_Offset + 0x10 + 0xE + 0x1)
                    log_to_file("Dir: " + Bitmap.directory)
                    Bitmap.type = "detail_map_m_0"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1 
                
                    if(DefaultNeeded != 1):
                        #try to do something with the file to get it to see if it exists
                        handle_missing_texture(Bitmap.directory, bpy.context.preferences.addons[__name__].preferences.export_path + "/" + Bitmap.directory)  
                    
                        try:
                            if (has_prefix != True):
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                            else:
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Raw_Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "height")
                        except OSError:
                            log_to_file("Bitmap Directory not referenced. Please use Default Data")
                    
                    #get scaling data for bitmap
                    Bitmap = get_scale(shaderfile, (Detail_Map_M_0_Offset + 0x10 + 0xE + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    #check scaling is correct:
                    log_to_file("[" + Bitmap.type + "] Scale: " + str(Bitmap.scale_xy))

                    DefaultNeeded = 0             
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "detail_map_m_0")):
                        log_to_file("")
                        log_to_file("[detail_map_m_0]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        Bitmap.equi_paths = []
                        
                        Bitmap.type = "detail_map_m_0"
                        Bitmap.directory = correct_default_dir("detail_map_m_0")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)
                
                #BUMP_MAP_M_0 OFFSET
                if (Bump_Map_M_0_Offset != 0):
                    #log_to_file("self_illum_map offset: " + str(SelfIllumMap_Offset))
                    log_to_file("")
                    log_to_file("[bump_map_m_0]") 
                    shaderfile.seek(Bump_Map_M_0_Offset + 0x10 + 0xC + 0x1)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    Bitmap.equi_paths = []
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, Bump_Map_M_0_Offset + 0x10 + 0xC + 0x1)
                    log_to_file("Dir: " + Bitmap.directory)
                    Bitmap.type = "bump_map_m_0"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1 
                
                    if(DefaultNeeded != 1):
                        #try to do something with the file to get it to see if it exists
                        handle_missing_texture(Bitmap.directory, bpy.context.preferences.addons[__name__].preferences.export_path + "/" + Bitmap.directory)  
                    
                        try:
                            if (has_prefix != True):
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                            else:
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Raw_Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "height")
                        except OSError:
                            log_to_file("Bitmap Directory not referenced. Please use Default Data")
                    
                    #get scaling data for bitmap
                    Bitmap = get_scale(shaderfile, (Bump_Map_M_0_Offset + 0x10 + 0xC + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    #check scaling is correct:
                    log_to_file("[" + Bitmap.type + "] Scale: " + str(Bitmap.scale_xy))

                    DefaultNeeded = 0  
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "bump_map_m_0")):
                        log_to_file("")
                        log_to_file("[bump_map_m_0]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        Bitmap.equi_paths = []
                        
                        Bitmap.type = "bump_map_m_0"
                        Bitmap.directory = correct_default_dir("bump_map_m_0")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)
                
                #Detail_Bump_M_0_Offset OFFSET
                if (Detail_Bump_M_0_Offset != 0):
                    #log_to_file("self_illum_map offset: " + str(SelfIllumMap_Offset))
                    log_to_file("")
                    log_to_file("[detail_bump_m_0]") 
                    shaderfile.seek(Detail_Bump_M_0_Offset + 0x10 + 0xF + 0x1)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    Bitmap.equi_paths = []
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, Detail_Bump_M_0_Offset + 0x10 + 0xF + 0x1)
                    log_to_file("Dir: " + Bitmap.directory)
                    Bitmap.type = "detail_bump_m_0"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1 
                
                    if(DefaultNeeded != 1):
                        #try to do something with the file to get it to see if it exists
                        handle_missing_texture(Bitmap.directory, bpy.context.preferences.addons[__name__].preferences.export_path + "/" + Bitmap.directory)  
                    
                        try:
                            if (has_prefix != True):
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                            else:
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Raw_Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "height")
                        except OSError:
                            log_to_file("Bitmap Directory not referenced. Please use Default Data")
                    
                    #get scaling data for bitmap
                    Bitmap = get_scale(shaderfile, (Detail_Bump_M_0_Offset + 0x10 + 0xF + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    #check scaling is correct:
                    log_to_file("[" + Bitmap.type + "] Scale: " + str(Bitmap.scale_xy))

                    DefaultNeeded = 0 
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "detail_bump_m_0")):
                        log_to_file("")
                        log_to_file("[detail_bump_m_0]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        Bitmap.equi_paths = []
                        
                        Bitmap.type = "detail_bump_m_0"
                        Bitmap.directory = correct_default_dir("detail_bump_m_0")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)

                #BASE_MAP_M_1 OFFSET
                if (Base_Map_M_1_Offset != 0):
                    #log_to_file("self_illum_map offset: " + str(SelfIllumMap_Offset))
                    log_to_file("")
                    log_to_file("[base_map_m_1]") 
                    shaderfile.seek(Base_Map_M_1_Offset + 0x10 + 0xC + 0x1)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    Bitmap.equi_paths = []
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, Base_Map_M_1_Offset + 0x10 + 0xC + 0x1)
                    log_to_file("Dir: " + Bitmap.directory)
                    Bitmap.type = "base_map_m_1"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1 
                
                    if(DefaultNeeded != 1):
                        #try to do something with the file to get it to see if it exists
                        handle_missing_texture(Bitmap.directory, bpy.context.preferences.addons[__name__].preferences.export_path + "/" + Bitmap.directory)  
                    
                        try:
                            if (has_prefix != True):
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                            else:
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Raw_Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "height")
                        except OSError:
                            log_to_file("Bitmap Directory not referenced. Please use Default Data")
                    
                    #get scaling data for bitmap
                    Bitmap = get_scale(shaderfile, (Base_Map_M_1_Offset + 0x10 + 0xC + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    #check scaling is correct:
                    log_to_file("[" + Bitmap.type + "] Scale: " + str(Bitmap.scale_xy))

                    DefaultNeeded = 0            
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "base_map_m_1")):
                        log_to_file("")
                        log_to_file("[base_map_m_1]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        Bitmap.equi_paths = []
                        
                        Bitmap.type = "base_map_m_1"
                        Bitmap.directory = correct_default_dir("base_map_m_1")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)
                
                #DETAIL_MAP_M_1 OFFSET
                if (Detail_Map_M_1_Offset != 0):
                    #log_to_file("self_illum_map offset: " + str(SelfIllumMap_Offset))
                    log_to_file("")
                    log_to_file("[detail_map_m_1]") 
                    shaderfile.seek(Detail_Map_M_1_Offset + 0x10 + 0xE + 0x1)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    Bitmap.equi_paths = []
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, Detail_Map_M_1_Offset + 0x10 + 0xE + 0x1)
                    log_to_file("Dir: " + Bitmap.directory)
                    Bitmap.type = "detail_map_m_1"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1 
                
                    if(DefaultNeeded != 1):
                        #try to do something with the file to get it to see if it exists
                        handle_missing_texture(Bitmap.directory, bpy.context.preferences.addons[__name__].preferences.export_path + "/" + Bitmap.directory)  
                    
                        try:
                            if (has_prefix != True):
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                            else:
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Raw_Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "height")
                        except OSError:
                            log_to_file("Bitmap Directory not referenced. Please use Default Data")
                    
                    #get scaling data for bitmap
                    Bitmap = get_scale(shaderfile, (Detail_Map_M_1_Offset + 0x10 + 0xE + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    #check scaling is correct:
                    log_to_file("[" + Bitmap.type + "] Scale: " + str(Bitmap.scale_xy))

                    DefaultNeeded = 0             
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "detail_map_m_1")):
                        log_to_file("")
                        log_to_file("[detail_map_m_1]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        Bitmap.equi_paths = []
                        
                        Bitmap.type = "detail_map_m_1"
                        Bitmap.directory = correct_default_dir("detail_map_m_1")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)
                
                #BUMP_MAP_M_1 OFFSET
                if (Bump_Map_M_1_Offset != 0):
                    #log_to_file("self_illum_map offset: " + str(SelfIllumMap_Offset))
                    log_to_file("")
                    log_to_file("[bump_map_m_1]") 
                    shaderfile.seek(Bump_Map_M_1_Offset + 0x10 + 0xC + 0x1)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    Bitmap.equi_paths = []
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, Bump_Map_M_1_Offset + 0x10 + 0xC + 0x1)
                    log_to_file("Dir: " + Bitmap.directory)
                    Bitmap.type = "bump_map_m_1"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1 
                
                    if(DefaultNeeded != 1):
                        #try to do something with the file to get it to see if it exists
                        handle_missing_texture(Bitmap.directory, bpy.context.preferences.addons[__name__].preferences.export_path + "/" + Bitmap.directory)  
                    
                        try:
                            if (has_prefix != True):
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                            else:
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Raw_Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "height")
                        except OSError:
                            log_to_file("Bitmap Directory not referenced. Please use Default Data")
                    
                    #get scaling data for bitmap
                    Bitmap = get_scale(shaderfile, (Bump_Map_M_1_Offset + 0x10 + 0xC + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    #check scaling is correct:
                    log_to_file("[" + Bitmap.type + "] Scale: " + str(Bitmap.scale_xy))

                    DefaultNeeded = 0  
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "bump_map_m_1")):
                        log_to_file("")
                        log_to_file("[bump_map_m_1]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        Bitmap.equi_paths = []
                        
                        Bitmap.type = "bump_map_m_1"
                        Bitmap.directory = correct_default_dir("bump_map_m_1")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)
                
                #Detail_Bump_M_1_Offset OFFSET
                if (Detail_Bump_M_1_Offset != 0):
                    #log_to_file("self_illum_map offset: " + str(SelfIllumMap_Offset))
                    log_to_file("")
                    log_to_file("[detail_bump_m_1]") 
                    shaderfile.seek(Detail_Bump_M_1_Offset + 0x10 + 0xE + 0x1)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    Bitmap.equi_paths = []
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, Detail_Bump_M_1_Offset + 0x10 + 0xE + 0x1)
                    log_to_file("Dir: " + Bitmap.directory)
                    Bitmap.type = "detail_bump_m_1"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1 
                
                    if(DefaultNeeded != 1):
                        #try to do something with the file to get it to see if it exists
                        handle_missing_texture(Bitmap.directory, bpy.context.preferences.addons[__name__].preferences.export_path + "/" + Bitmap.directory)  
                    
                        try:
                            if (has_prefix != True):
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                            else:
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Raw_Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "height")
                        except OSError:
                            log_to_file("Bitmap Directory not referenced. Please use Default Data")
                    
                    #get scaling data for bitmap
                    Bitmap = get_scale(shaderfile, (Detail_Bump_M_1_Offset + 0x10 + 0xE + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    #check scaling is correct:
                    log_to_file("[" + Bitmap.type + "] Scale: " + str(Bitmap.scale_xy))

                    DefaultNeeded = 0 
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "detail_bump_m_1")):
                        log_to_file("")
                        log_to_file("[detail_bump_m_1]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        Bitmap.equi_paths = []
                        
                        Bitmap.type = "detail_bump_m_1"
                        Bitmap.directory = correct_default_dir("detail_bump_m_1")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)
                
                #BASE_MAP_M_2 OFFSET
                if (Base_Map_M_2_Offset != 0):
                    #log_to_file("self_illum_map offset: " + str(SelfIllumMap_Offset))
                    log_to_file("")
                    log_to_file("[base_map_m_2]") 
                    shaderfile.seek(Base_Map_M_2_Offset + 0x10 + 0xC + 0x1)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    Bitmap.equi_paths = []
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, Base_Map_M_2_Offset + 0x10 + 0xC + 0x1)
                    log_to_file("Dir: " + Bitmap.directory)
                    Bitmap.type = "base_map_m_2"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1 
                
                    if(DefaultNeeded != 1):
                        #try to do something with the file to get it to see if it exists
                        handle_missing_texture(Bitmap.directory, bpy.context.preferences.addons[__name__].preferences.export_path + "/" + Bitmap.directory)  
                    
                        try:
                            if (has_prefix != True):
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                            else:
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Raw_Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "height")
                        except OSError:
                            log_to_file("Bitmap Directory not referenced. Please use Default Data")
                    
                    #get scaling data for bitmap
                    Bitmap = get_scale(shaderfile, (Base_Map_M_2_Offset + 0x10 + 0xC + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    #check scaling is correct:
                    log_to_file("[" + Bitmap.type + "] Scale: " + str(Bitmap.scale_xy))

                    DefaultNeeded = 0            
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "base_map_m_2")):
                        log_to_file("")
                        log_to_file("[base_map_m_2]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        Bitmap.equi_paths = []
                        
                        Bitmap.type = "base_map_m_2"
                        Bitmap.directory = correct_default_dir("base_map_m_2")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)
                
                #DETAIL_MAP_M_2 OFFSET
                if (Detail_Map_M_2_Offset != 0):
                    #log_to_file("self_illum_map offset: " + str(SelfIllumMap_Offset))
                    log_to_file("")
                    log_to_file("[detail_map_m_2]") 
                    shaderfile.seek(Detail_Map_M_2_Offset + 0x10 + 0xE + 0x1)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    Bitmap.equi_paths = []
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, Detail_Map_M_2_Offset + 0x10 + 0xE + 0x1)
                    log_to_file("Dir: " + Bitmap.directory)
                    Bitmap.type = "detail_map_m_2"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1 
                
                    if(DefaultNeeded != 1):
                        #try to do something with the file to get it to see if it exists
                        handle_missing_texture(Bitmap.directory, bpy.context.preferences.addons[__name__].preferences.export_path + "/" + Bitmap.directory)  
                    
                        try:
                            if (has_prefix != True):
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                            else:
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Raw_Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "height")
                        except OSError:
                            log_to_file("Bitmap Directory not referenced. Please use Default Data")
                    
                    #get scaling data for bitmap
                    Bitmap = get_scale(shaderfile, (Detail_Map_M_2_Offset + 0x10 + 0xE + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    #check scaling is correct:
                    log_to_file("[" + Bitmap.type + "] Scale: " + str(Bitmap.scale_xy))

                    DefaultNeeded = 0             
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "detail_map_m_2")):
                        log_to_file("")
                        log_to_file("[detail_map_m_2]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        Bitmap.equi_paths = []
                        
                        Bitmap.type = "detail_map_m_2"
                        Bitmap.directory = correct_default_dir("detail_map_m_2")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)
                
                #BUMP_MAP_M_2 OFFSET
                if (Bump_Map_M_2_Offset != 0):
                    #log_to_file("self_illum_map offset: " + str(SelfIllumMap_Offset))
                    log_to_file("")
                    log_to_file("[bump_map_m_2]") 
                    shaderfile.seek(Bump_Map_M_2_Offset + 0x10 + 0xC + 0x1)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    Bitmap.equi_paths = []
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, Bump_Map_M_2_Offset + 0x10 + 0xC + 0x1)
                    log_to_file("Dir: " + Bitmap.directory)
                    Bitmap.type = "bump_map_m_2"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1 
                
                    if(DefaultNeeded != 1):
                        #try to do something with the file to get it to see if it exists
                        handle_missing_texture(Bitmap.directory, bpy.context.preferences.addons[__name__].preferences.export_path + "/" + Bitmap.directory)  
                    
                        try:
                            if (has_prefix != True):
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                            else:
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Raw_Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "height")
                        except OSError:
                            log_to_file("Bitmap Directory not referenced. Please use Default Data")
                    
                    #get scaling data for bitmap
                    Bitmap = get_scale(shaderfile, (Bump_Map_M_2_Offset + 0x10 + 0xC + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    #check scaling is correct:
                    log_to_file("[" + Bitmap.type + "] Scale: " + str(Bitmap.scale_xy))

                    DefaultNeeded = 0  
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "bump_map_m_2")):
                        log_to_file("")
                        log_to_file("[bump_map_m_2]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        Bitmap.equi_paths = []
                        
                        Bitmap.type = "bump_map_m_2"
                        Bitmap.directory = correct_default_dir("bump_map_m_2")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)
                
                #Detail_Bump_M_3_Offset OFFSET
                if (Detail_Bump_M_3_Offset != 0):
                    #log_to_file("self_illum_map offset: " + str(SelfIllumMap_Offset))
                    log_to_file("")
                    log_to_file("[detail_bump_m_3]") 
                    shaderfile.seek(Detail_Bump_M_3_Offset + 0x10 + 0xE + 0x1)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    Bitmap.equi_paths = []
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, Detail_Bump_M_3_Offset + 0x10 + 0xE + 0x1)
                    log_to_file("Dir: " + Bitmap.directory)
                    Bitmap.type = "detail_bump_m_3"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1 
                
                    if(DefaultNeeded != 1):
                        #try to do something with the file to get it to see if it exists
                        handle_missing_texture(Bitmap.directory, bpy.context.preferences.addons[__name__].preferences.export_path + "/" + Bitmap.directory)  
                    
                        try:
                            if (has_prefix != True):
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                            else:
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Raw_Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "height")
                        except OSError:
                            log_to_file("Bitmap Directory not referenced. Please use Default Data")
                    
                    #get scaling data for bitmap
                    Bitmap = get_scale(shaderfile, (Detail_Bump_M_3_Offset + 0x10 + 0xE + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    #check scaling is correct:
                    log_to_file("[" + Bitmap.type + "] Scale: " + str(Bitmap.scale_xy))

                    DefaultNeeded = 0 
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "detail_bump_m_3")):
                        log_to_file("")
                        log_to_file("[detail_bump_m_3]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        Bitmap.equi_paths = []
                        
                        Bitmap.type = "detail_bump_m_3"
                        Bitmap.directory = correct_default_dir("detail_bump_m_3")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)
                
                #BASE_MAP_M_3 OFFSET
                if (Base_Map_M_3_Offset != 0):
                    #log_to_file("self_illum_map offset: " + str(SelfIllumMap_Offset))
                    log_to_file("")
                    log_to_file("[base_map_m_3]") 
                    shaderfile.seek(Base_Map_M_3_Offset + 0x10 + 0xC + 0x1)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    Bitmap.equi_paths = []
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, Base_Map_M_3_Offset + 0x10 + 0xC + 0x1)
                    log_to_file("Dir: " + Bitmap.directory)
                    Bitmap.type = "base_map_m_3"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1 
                
                    if(DefaultNeeded != 1):
                        #try to do something with the file to get it to see if it exists
                        handle_missing_texture(Bitmap.directory, bpy.context.preferences.addons[__name__].preferences.export_path + "/" + Bitmap.directory)  
                    
                        try:
                            if (has_prefix != True):
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                            else:
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Raw_Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "height")
                        except OSError:
                            log_to_file("Bitmap Directory not referenced. Please use Default Data")
                    
                    #get scaling data for bitmap
                    Bitmap = get_scale(shaderfile, (Base_Map_M_3_Offset + 0x10 + 0xC + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    #check scaling is correct:
                    log_to_file("[" + Bitmap.type + "] Scale: " + str(Bitmap.scale_xy))

                    DefaultNeeded = 0            
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "base_map_m_3")):
                        log_to_file("")
                        log_to_file("[base_map_m_3]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        Bitmap.equi_paths = []
                        
                        Bitmap.type = "base_map_m_3"
                        Bitmap.directory = correct_default_dir("base_map_m_3")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)
                
                #DETAIL_MAP_M_3 OFFSET
                if (Detail_Map_M_3_Offset != 0):
                    #log_to_file("self_illum_map offset: " + str(SelfIllumMap_Offset))
                    log_to_file("")
                    log_to_file("[detail_map_m_3]") 
                    shaderfile.seek(Detail_Map_M_3_Offset + 0x10 + 0xE + 0x1)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    Bitmap.equi_paths = []
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, Detail_Map_M_3_Offset + 0x10 + 0xE + 0x1)
                    log_to_file("Dir: " + Bitmap.directory)
                    Bitmap.type = "detail_map_m_3"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1 
                
                    if(DefaultNeeded != 1):
                        #try to do something with the file to get it to see if it exists
                        handle_missing_texture(Bitmap.directory, bpy.context.preferences.addons[__name__].preferences.export_path + "/" + Bitmap.directory)  
                    
                        try:
                            if (has_prefix != True):
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                            else:
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Raw_Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "height")
                        except OSError:
                            log_to_file("Bitmap Directory not referenced. Please use Default Data")
                    
                    #get scaling data for bitmap
                    Bitmap = get_scale(shaderfile, (Detail_Map_M_3_Offset + 0x10 + 0xE + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    #check scaling is correct:
                    log_to_file("[" + Bitmap.type + "] Scale: " + str(Bitmap.scale_xy))

                    DefaultNeeded = 0             
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "detail_map_m_3")):
                        log_to_file("")
                        log_to_file("[detail_map_m_3]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        Bitmap.equi_paths = []
                        
                        Bitmap.type = "detail_map_m_3"
                        Bitmap.directory = correct_default_dir("detail_map_m_3")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)
                
                #BUMP_MAP_M_3 OFFSET
                if (Bump_Map_M_3_Offset != 0):
                    #log_to_file("self_illum_map offset: " + str(SelfIllumMap_Offset))
                    log_to_file("")
                    log_to_file("[bump_map_m_3]") 
                    shaderfile.seek(Bump_Map_M_3_Offset + 0x10 + 0xC + 0x1)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    Bitmap.equi_paths = []
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, Bump_Map_M_3_Offset + 0x10 + 0xC + 0x1)
                    log_to_file("Dir: " + Bitmap.directory)
                    Bitmap.type = "bump_map_m_3"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1 
                
                    if(DefaultNeeded != 1):
                        #try to do something with the file to get it to see if it exists
                        handle_missing_texture(Bitmap.directory, bpy.context.preferences.addons[__name__].preferences.export_path + "/" + Bitmap.directory)  
                    
                        try:
                            if (has_prefix != True):
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                            else:
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Raw_Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "height")
                        except OSError:
                            log_to_file("Bitmap Directory not referenced. Please use Default Data")
                    
                    #get scaling data for bitmap
                    Bitmap = get_scale(shaderfile, (Bump_Map_M_3_Offset + 0x10 + 0xC + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    #check scaling is correct:
                    log_to_file("[" + Bitmap.type + "] Scale: " + str(Bitmap.scale_xy))

                    DefaultNeeded = 0  
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "bump_map_m_3")):
                        log_to_file("")
                        log_to_file("[bump_map_m_3]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        Bitmap.equi_paths = []
                        
                        Bitmap.type = "bump_map_m_3"
                        Bitmap.directory = correct_default_dir("bump_map_m_3")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)
                
                #Detail_Bump_M_3_Offset OFFSET
                if (Detail_Bump_M_3_Offset != 0):
                    #log_to_file("self_illum_map offset: " + str(SelfIllumMap_Offset))
                    log_to_file("")
                    log_to_file("[detail_bump_m_3]") 
                    shaderfile.seek(Detail_Bump_M_3_Offset + 0x10 + 0xE + 0x1)
                    
                    #clear old bitmap data
                    Bitmap = bitmap()
                    Bitmap.directory = ""
                    Bitmap.type = ""
                    Bitmap.curve_option = 0
                    Bitmap.width = 0
                    Bitmap.height = 0
                    Bitmap.equi_paths = []
                    
                    #save current data
                    Bitmap.directory = get_dir(shaderfile, Detail_Bump_M_3_Offset + 0x10 + 0xE + 0x1)
                    log_to_file("Dir: " + Bitmap.directory)
                    Bitmap.type = "detail_bump_m_3"
                    ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                    ShaderItem.bitmap_list.append(Bitmap)
                    if (Bitmap.directory == "" or Bitmap.directory == " " or Bitmap.directory == "   "):
                         DefaultNeeded = 1 
                
                    if(DefaultNeeded != 1):
                        #try to do something with the file to get it to see if it exists
                        handle_missing_texture(Bitmap.directory, bpy.context.preferences.addons[__name__].preferences.export_path + "/" + Bitmap.directory)  
                    
                        try:
                            if (has_prefix != True):
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Tag_Root + Bitmap.directory + ".bitmap", "height")
                            else:
                                #get Curve for bitmap
                                Bitmap.curve_option = get_bitmap_curve(Raw_Tag_Root + Bitmap.directory + ".bitmap")
                                
                                #Get Resolution of bitmap
                                Bitmap.width = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "width")
                                Bitmap.height = get_bitmap_resolution(Raw_Tag_Root + Bitmap.directory + ".bitmap", "height")
                        except OSError:
                            log_to_file("Bitmap Directory not referenced. Please use Default Data")
                    
                    #get scaling data for bitmap
                    Bitmap = get_scale(shaderfile, (Detail_Bump_M_3_Offset + 0x10 + 0xE + 0x1), len(Bitmap.directory), Bitmap) #uniform scaling 

                    #check scaling is correct:
                    log_to_file("[" + Bitmap.type + "] Scale: " + str(Bitmap.scale_xy))

                    DefaultNeeded = 0 
                else:
                    #bitmap not referenced but might be needed
                    if(is_texture_needed(ShaderItem, "detail_bump_m_3")):
                        log_to_file("")
                        log_to_file("[detail_bump_m_3]")
                        #DirOffset = shaderfile.tell()
                        
                        #clear old bitmap data
                        Bitmap = bitmap()
                        Bitmap.directory = ""
                        Bitmap.type = ""
                        Bitmap.curve_option = 0
                        Bitmap.width = 0
                        Bitmap.height = 0
                        Bitmap.equi_paths = []
                        
                        Bitmap.type = "detail_bump_m_3"
                        Bitmap.directory = correct_default_dir("detail_bump_m_3")
                        ShaderItem.bitmap_count = ShaderItem.bitmap_count + 1
                        ShaderItem.bitmap_list.append(Bitmap)

                                                    ##############
                                                    #COLORS/VALUES
                                                    ##############
                #############
                #SHADER FILES
                #############

                #COLOR/SCALE/VALUES    - Might use functions!                 -   CHECK THESE VALUES!!!
                log_to_file("")
                log_to_file("--[Existing Scaling/Color Values Types]--")
                if (Albedo_Blend_Offset != 0): #float
                    #log_to_file("albedo_blend offset: " + str(Albedo_Blend_Offset))
                    
                    
                    #save current data
                    if(has_value(shaderfile, Albedo_Blend_Offset + 0xC + 0x1) == True):
                        ShaderItem.albedo_blend = get_value(shaderfile, Albedo_Blend_Offset + 0xC + 0x1)
                        log_to_file("albedo_blend: " + str(ShaderItem.albedo_blend))
                    else:
                        log_to_file("albedo_blend value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Albedo_Blend_Offset + 0xC + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Albedo_Blend_Offset + 0xC + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.albedo_blend = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.albedo_blend))
                        ShaderItem.function_list.append(FunctionItem)
                        
                if (Albedo_Color_Offset != 0):  #color
                    #log_to_file("albedo_color offset: " + str(Albedo_Color_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Albedo_Color_Offset + 0xC + 0x1) == True):
                        ShaderItem.albedo_color = get_rgb(shaderfile, Albedo_Color_Offset + 0xC + 0x1, "rgb")
                        log_to_file("albedo_color: " + str(ShaderItem.albedo_color))
                        ShaderItem.albedo_color_alpha = get_rgb(shaderfile, Albedo_Color_Offset + 0xC + 0x1, "alpha")
                        log_to_file("albedo_color_alpha: " + str(ShaderItem.albedo_color_alpha))
                    else: #use default value
                        ShaderItem.albedo_color = color_white_rgb
                        log_to_file("albedo_color value/color not found. Using Default Value")
                        
                    #check for function                       
                    if(has_function(shaderfile, Albedo_Color_Offset + 0xC + 0x1) == True): #value/color has function
                        FunctionItem = get_color_function_data(shaderfile, Albedo_Color_Offset + 0xC + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with the first color
                        ShaderItem.albedo_color = (FunctionItem.color_1)
                        log_to_file("  New Value from function: " + str(ShaderItem.albedo_color))
                        ShaderItem.function_list.append(FunctionItem)   
                if (Albedo_Color2_Offset != 0):  #color
                    #log_to_file("albedo_color2 offset: " + str(Albedo_Color2_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Albedo_Color2_Offset + 0xD + 0x1) == True):
                        ShaderItem.albedo_color2 = get_rgb(shaderfile, Albedo_Color2_Offset + 0xD + 0x1, "rgb")
                        log_to_file("albedo_color2: " + str(ShaderItem.albedo_color2))
                        ShaderItem.albedo_color2_alpha = get_rgb(shaderfile, Albedo_Color2_Offset + 0xD + 0x1, "alpha")
                        log_to_file("albedo_color2_alpha: " + str(ShaderItem.albedo_color2_alpha))
                    else: #use default value
                        ShaderItem.albedo_color2 = color_white_rgb
                        log_to_file("albedo_color2 value/color not found. Using Default Value")
                        
                    #check for function                       
                    if(has_function(shaderfile, Albedo_Color2_Offset + 0xD + 0x1) == True): #value/color has function
                        FunctionItem = get_color_function_data(shaderfile, Albedo_Color2_Offset + 0xD + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with the first color
                        ShaderItem.albedo_color2 = (FunctionItem.color_1)
                        log_to_file("  New Value from function: " + str(ShaderItem.albedo_color2))
                        ShaderItem.function_list.append(FunctionItem)     
                if (Albedo_Color3_Offset != 0):  #color
                    #log_to_file("albedo_color3 offset: " + str(Albedo_Color3_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Albedo_Color3_Offset + 0xD + 0x1) == True):
                        ShaderItem.albedo_color3 = get_rgb(shaderfile, Albedo_Color3_Offset + 0xD + 0x1, "rgb")
                        log_to_file("albedo_color3: " + str(ShaderItem.albedo_color3))
                        ShaderItem.albedo_color3_alpha = get_rgb(shaderfile, Albedo_Color3_Offset + 0xD + 0x1, "alpha")
                        log_to_file("albedo_color3_alpha: " + str(ShaderItem.albedo_color3_alpha))
                    else: #use default value
                        ShaderItem.albedo_color3 = color_white_rgb
                        log_to_file("albedo_color3 value/color not found. Using Default Value")
                        
                    #check for function                       
                    if(has_function(shaderfile, Albedo_Color3_Offset + 0xD + 0x1) == True): #value/color has function
                        FunctionItem = get_color_function_data(shaderfile, Albedo_Color3_Offset + 0xD + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with the first color
                        ShaderItem.albedo_color3 = (FunctionItem.color_1)
                        log_to_file("  New Value from function: " + str(ShaderItem.albedo_color3))
                        ShaderItem.function_list.append(FunctionItem)     

                if (Bump_Detail_Coefficient_Offset != 0): #float
                    #log_to_file("bump_detail_coefficient offset: " + str(Bump_Detail_Coefficient_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Bump_Detail_Coefficient_Offset + 0x17 + 0x1) == True):
                        ShaderItem.bump_detail_coefficient = get_value(shaderfile, Bump_Detail_Coefficient_Offset + 0x17 + 0x1)
                        log_to_file("bump_detail_coefficient: " + str(ShaderItem.bump_detail_coefficient))                    
                    else:
                        log_to_file("bump_detail_coefficient value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Bump_Detail_Coefficient_Offset + 0x17 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Bump_Detail_Coefficient_Offset + 0x17 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.bump_detail_coefficient = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.bump_detail_coefficient))
                        ShaderItem.function_list.append(FunctionItem)
                        
                if (Env_Tint_Color_Offset != 0):  #color
                    #log_to_file("env_tint_color offset: " + str(Env_Tint_Color_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Env_Tint_Color_Offset + 0xE + 0x1) == True):
                        ShaderItem.env_tint_color = get_rgb(shaderfile, Env_Tint_Color_Offset + 0xE + 0x1, "rgb")
                        log_to_file("env_tint_color: " + str(ShaderItem.env_tint_color))                    
                    else:
                        ShaderItem.env_tint_color = color_white_rgb
                        log_to_file("env_tint_color value/color not found")
                        
                    #check for function                       
                    if(has_function(shaderfile, Env_Tint_Color_Offset + 0xE + 0x1) == True): #value/color has function
                        FunctionItem = get_color_function_data(shaderfile, Env_Tint_Color_Offset + 0xE + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with the first color
                        ShaderItem.env_tint_color = (FunctionItem.color_1)
                        log_to_file("  New Value from function: " + str(ShaderItem.env_tint_color))
                        ShaderItem.function_list.append(FunctionItem)      
                        
                if (Env_Roughness_Scale_Offset != 0): #float
                    #log_to_file("env_roughness_scale offset: " + str(Env_Roughness_Scale_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Env_Roughness_Scale_Offset + 0x13 + 0x1) == True):
                        ShaderItem.env_roughness_scale = get_value(shaderfile, Env_Roughness_Scale_Offset + 0x13 + 0x1)
                        log_to_file("env_roughness_scale: " + str(ShaderItem.env_roughness_scale))                    
                    else:
                        log_to_file("env_roughness_scale value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Env_Roughness_Scale_Offset + 0x13 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Env_Roughness_Scale_Offset + 0x13 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.env_roughness_scale = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.env_roughness_scale))
                        ShaderItem.function_list.append(FunctionItem)                  
                        
                if (Self_Illum_Color_Offset != 0):  #color
                    #log_to_file("self_illum_color offset: " + str(Env_Tint_Color_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Self_Illum_Color_Offset + 0x10 + 0x1) == True):
                        ShaderItem.self_illum_color = get_rgb(shaderfile, Self_Illum_Color_Offset + 0x10 + 0x1, "rgb")
                        log_to_file("self_illum_color: " + str(ShaderItem.self_illum_color))                    
                    else:
                        log_to_file("self_illum_color value/color not found")
                        
                    #check for function                       
                    if(has_function(shaderfile, Self_Illum_Color_Offset + 0x10 + 0x1) == True): #value/color has function
                        FunctionItem = get_color_function_data(shaderfile, Self_Illum_Color_Offset + 0x10 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with the first color
                        ShaderItem.self_illum_color = (FunctionItem.color_1)
                        log_to_file("  New Value from function: " + str(ShaderItem.self_illum_color))
                        ShaderItem.function_list.append(FunctionItem)      
                        
                if (Self_Illum_Intensity_Offset != 0): #float
                    #log_to_file("self_illum_intensity offset: " + str(Self_Illum_Intensity_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Self_Illum_Intensity_Offset + 0x14 + 0x1) == True):
                        ShaderItem.self_illum_intensity = get_value(shaderfile, Self_Illum_Intensity_Offset + 0x14 + 0x1)
                        log_to_file("self_illum_intensity: " + str(ShaderItem.self_illum_intensity))                    
                    else:
                        log_to_file("self_illum_intensity value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Self_Illum_Intensity_Offset + 0x14 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Self_Illum_Intensity_Offset + 0x14 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.self_illum_intensity = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.self_illum_intensity))
                        ShaderItem.function_list.append(FunctionItem)
                        
                if (Channel_A_Offset != 0):  #color
                    #log_to_file("channel_a offset: " + str(Channel_A_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Channel_A_Offset + 0x9 + 0x1) == True):
                        ShaderItem.channel_a = get_rgb(shaderfile, Channel_A_Offset + 0x9 + 0x1, "rgb")
                        log_to_file("channel_a: " + str(ShaderItem.channel_a))                    
                    else:
                        log_to_file("channel_a value/color not found")
                       
                    #check for function                       
                    if(has_function(shaderfile, Channel_A_Offset + 0x9 + 0x1) == True): #value/color has function
                        FunctionItem = get_color_function_data(shaderfile, Channel_A_Offset + 0x9 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with the first color
                        ShaderItem.channel_a = (FunctionItem.color_1)
                        log_to_file("  New Value from function: " + str(ShaderItem.channel_a))
                        ShaderItem.function_list.append(FunctionItem)   
                        
                if (Channel_A_Alpha_Offset != 0): #float
                    #log_to_file("channel_a_alpha offset: " + str(Channel_A_Alpha_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Channel_A_Alpha_Offset + 0xF + 0x1) == True):
                        ShaderItem.channel_a_alpha = get_value(shaderfile, Channel_A_Alpha_Offset + 0xF + 0x1)
                        log_to_file("channel_a_alpha: " + str(ShaderItem.channel_a_alpha))                    
                    else:
                        log_to_file("channel_a_alpha value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Channel_A_Alpha_Offset + 0xF + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Channel_A_Alpha_Offset + 0xF + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.channel_a_alpha = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.channel_a_alpha))
                        ShaderItem.function_list.append(FunctionItem)                    
                        
                if (Channel_B_Offset != 0):  #color
                    #log_to_file("channel_b offset: " + str(Channel_B_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Channel_B_Offset + 0x9 + 0x1) == True):
                        ShaderItem.channel_b = get_rgb(shaderfile, Channel_B_Offset + 0x9 + 0x1, "rgb")
                        log_to_file("channel_b: " + str(ShaderItem.channel_b))                    
                    else:
                        log_to_file("channel_b value/color not found")
                        
                    #check for function                       
                    if(has_function(shaderfile, Channel_B_Offset + 0x9 + 0x1) == True): #value/color has function
                        FunctionItem = get_color_function_data(shaderfile, Channel_B_Offset + 0x9 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        
                        #overrite some data for this item with the function data with the first color
                        ShaderItem.channel_b = median_rgba(FunctionItem)
                        
                        
                        log_to_file("  New Value from function: " + str(ShaderItem.channel_b))
                        ShaderItem.function_list.append(FunctionItem)     
                    else:
                        log_to_file("Channel_B set to default")     
                if (Channel_B_Alpha_Offset != 0): #float
                    #log_to_file("channel_b_alpha offset: " + str(Channel_B_Alpha_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Channel_B_Alpha_Offset + 0xF + 0x1) == True):
                        ShaderItem.channel_b_alpha = get_value(shaderfile, Channel_B_Alpha_Offset + 0xF + 0x1)
                        log_to_file("channel_b_alpha: " + str(ShaderItem.channel_b_alpha))                    
                    else:
                        log_to_file("channel_b_alpha value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Channel_B_Alpha_Offset + 0xF + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Channel_B_Alpha_Offset + 0xF + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.channel_b_alpha = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.channel_b_alpha))
                        ShaderItem.function_list.append(FunctionItem)                      
                        
                if (Channel_C_Offset != 0):  #color
                    #log_to_file("channel_c offset: " + str(Channel_C_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Channel_C_Offset + 0x9 + 0x1) == True):
                        ShaderItem.channel_c = get_rgb(shaderfile, Channel_C_Offset + 0x9 + 0x1, "rgb")
                        log_to_file("channel_c: " + str(ShaderItem.channel_c))                    
                    else:
                        log_to_file("channel_c value/color not found")
                        
                    #check for function                       
                    if(has_function(shaderfile, Channel_C_Offset + 0x9 + 0x1) == True): #value/color has function
                        FunctionItem = get_color_function_data(shaderfile, Channel_C_Offset + 0x9 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with the first color
                        ShaderItem.channel_c = (FunctionItem.color_1)
                        log_to_file("  New Value from function: " + str(ShaderItem.channel_c))
                        ShaderItem.function_list.append(FunctionItem) 

                if (Channel_C_Alpha_Offset != 0): #float
                    #log_to_file("channel_c_alpha offset: " + str(Channel_C_Alpha_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Channel_C_Alpha_Offset + 0xF + 0x1) == True):
                        ShaderItem.channel_c_alpha = get_value(shaderfile, Channel_C_Alpha_Offset + 0xF + 0x1)
                        log_to_file("channel_c_alpha: " + str(ShaderItem.channel_c_alpha))                    
                    else:
                        log_to_file("channel_c_alpha value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Channel_C_Alpha_Offset + 0xF + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Channel_C_Alpha_Offset + 0xF + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.channel_c_alpha = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.channel_c_alpha))
                        ShaderItem.function_list.append(FunctionItem)                     
                        
                if (Color_Medium_Offset != 0):  #color
                    #log_to_file("color_medium offset: " + str(Color_Medium_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Color_Medium_Offset + 0xC + 0x1) == True):
                        ShaderItem.color_medium = get_rgb(shaderfile, Color_Medium_Offset + 0xC + 0x1, "rgb")
                        log_to_file("color_medium: " + str(ShaderItem.color_medium))                    
                    else:
                        log_to_file("color_medium value/color not found")
                        
                    #check for function                       
                    if(has_function(shaderfile, Color_Medium_Offset + 0xC + 0x1) == True): #value/color has function
                        FunctionItem = get_color_function_data(shaderfile, Color_Medium_Offset + 0xC + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with the first color
                        ShaderItem.color_medium = (FunctionItem.color_1)
                        log_to_file("  New Value from function: " + str(ShaderItem.color_medium))
                        ShaderItem.function_list.append(FunctionItem)        
                        
                if (Color_Medium_Alpha_Offset != 0): #float
                    #log_to_file("color_medium_alpha offset: " + str(Color_Medium_Alpha_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Color_Medium_Alpha_Offset + 0x12 + 0x1) == True):
                        ShaderItem.color_medium_alpha = get_value(shaderfile, Color_Medium_Alpha_Offset + 0x12 + 0x1)
                        log_to_file("color_medium_alpha: " + str(ShaderItem.color_medium_alpha))                    
                    else:
                        log_to_file("color_medium_alpha value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Color_Medium_Alpha_Offset + 0x12 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Color_Medium_Alpha_Offset + 0x12 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.color_medium_alpha = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.color_medium_alpha))
                        ShaderItem.function_list.append(FunctionItem)     
                        
                if (Color_Wide_Offset != 0):  #color
                    #log_to_file("color_wide offset: " + str(Color_Wide_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Color_Wide_Offset + 0xA + 0x1) == True):
                        ShaderItem.color_wide = get_rgb(shaderfile, Color_Wide_Offset + 0xA + 0x1, "rgb")
                        log_to_file("color_wide: " + str(ShaderItem.color_wide))                    
                    else:
                        log_to_file("color_wide value/color not found")
                        
                    #check for function                       
                    if(has_function(shaderfile, Color_Wide_Offset + 0xA + 0x1) == True): #value/color has function
                        FunctionItem = get_color_function_data(shaderfile, Color_Wide_Offset + 0xA + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with the first color
                        ShaderItem.color_wide = (FunctionItem.color_1)
                        log_to_file("  New Value from function: " + str(ShaderItem.color_wide))
                        ShaderItem.function_list.append(FunctionItem)   
                        
                if (Color_Wide_Alpha_Offset != 0): #float
                    #log_to_file("color_wide_alpha offset: " + str(Color_Wide_Alpha_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Color_Wide_Alpha_Offset + 0x10 + 0x1) == True):
                        ShaderItem.channel_a_alpha = get_value(shaderfile, Color_Wide_Alpha_Offset + 0x10 + 0x1)
                        log_to_file("color_wide_alpha: " + str(ShaderItem.color_wide_alpha))                    
                    else:
                        log_to_file("color_wide_alpha value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Color_Wide_Alpha_Offset + 0x10 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Color_Wide_Alpha_Offset + 0x10 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.color_wide_alpha = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.color_wide_alpha))
                        ShaderItem.function_list.append(FunctionItem)    
                        
                if (Color_Sharp_Offset != 0):  #color
                    #log_to_file("color_sharp offset: " + str(Color_Sharp_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Color_Sharp_Offset + 0xB + 0x1) == True):
                        ShaderItem.color_sharp = get_rgb(shaderfile, Color_Sharp_Offset + 0xB + 0x1, "rgb")
                        log_to_file("color_sharp: " + str(ShaderItem.color_sharp))                    
                    else:
                        log_to_file("color_sharp value/color not found")
                        
                    #check for function                       
                    if(has_function(shaderfile, Color_Sharp_Offset + 0xB + 0x1) == True): #value/color has function
                        FunctionItem = get_color_function_data(shaderfile, Color_Sharp_Offset + 0xB + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with the first color
                        ShaderItem.color_sharp = (FunctionItem.color_1)
                        log_to_file("  New Value from function: " + str(ShaderItem.color_sharp))
                        ShaderItem.function_list.append(FunctionItem)    
                        
                if (Color_Sharp_Alpha_Offset != 0): #float
                    #log_to_file("color_sharp_alpha offset: " + str(Color_Sharp_Alpha_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Color_Sharp_Alpha_Offset + 0x11 + 0x1) == True):
                        ShaderItem.color_sharp_alpha = get_value(shaderfile, Color_Sharp_Alpha_Offset + 0x11 + 0x1)
                        log_to_file("color_sharp_alpha: " + str(ShaderItem.color_sharp_alpha))                    
                    else:
                        log_to_file("color_sharp_alpha value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Color_Sharp_Alpha_Offset + 0x11 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Color_Sharp_Alpha_Offset + 0x11 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.color_sharp_alpha = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.color_sharp_alpha))
                        ShaderItem.function_list.append(FunctionItem)                     
                        
                if (Thinness_Medium_Offset != 0): #float
                    #log_to_file("thinness_medium offset: " + str(Thinness_Medium_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Thinness_Medium_Offset + 0xF + 0x1) == True):
                        ShaderItem.thinness_medium = get_value(shaderfile, Thinness_Medium_Offset + 0xF + 0x1)
                        log_to_file("thinness_medium: " + str(ShaderItem.thinness_medium))                    
                    else:
                        log_to_file("thinness_medium value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Thinness_Medium_Offset + 0xF + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Thinness_Medium_Offset + 0xF + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.thinness_medium = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.thinness_medium))
                        ShaderItem.function_list.append(FunctionItem)                              
                        
                if (Thinness_Wide_Offset != 0): #float
                    #log_to_file("thinness_wide offset: " + str(Thinness_Wide_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Thinness_Wide_Offset + 0xD + 0x1) == True):
                        ShaderItem.thinness_wide = get_value(shaderfile, Thinness_Wide_Offset + 0xD + 0x1)
                        log_to_file("thinness_wide: " + str(ShaderItem.thinness_wide))                    
                    else:
                        log_to_file("thinness_wide value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Thinness_Wide_Offset + 0xD + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Thinness_Wide_Offset + 0xD + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.thinness_wide = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.thinness_wide))
                        ShaderItem.function_list.append(FunctionItem)                     
                        
                if (Thinness_Sharp_Offset != 0): #float
                    #log_to_file("thinness_sharp offset: " + str(Thinness_Sharp_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Thinness_Sharp_Offset + 0xE + 0x1) == True):
                        ShaderItem.thinness_sharp = get_value(shaderfile, Thinness_Sharp_Offset + 0xE + 0x1)
                        log_to_file("thinness_sharp: " + str(ShaderItem.thinness_sharp))                    
                    else:
                        log_to_file("thinness_sharp value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Thinness_Sharp_Offset + 0xE + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Thinness_Sharp_Offset + 0xE + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.thinness_sharp = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.thinness_sharp))
                        ShaderItem.function_list.append(FunctionItem)                    
                        
                if (Meter_Color_On_Offset != 0):  #color
                    #log_to_file("meter_color_on offset: " + str(Meter_Color_On_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Meter_Color_On_Offset + 0xE + 0x1) == True):
                        ShaderItem.meter_color_on = get_rgb(shaderfile, Meter_Color_On_Offset + 0xE + 0x1, "rgb")
                        log_to_file("meter_color_on: " + str(ShaderItem.meter_color_on))                    
                    else:
                        log_to_file("meter_color_on value/color not found")
                        
                    #check for function                       
                    if(has_function(shaderfile, Meter_Color_On_Offset + 0xE + 0x1) == True): #value/color has function
                        FunctionItem = get_color_function_data(shaderfile, Meter_Color_On_Offset + 0xE + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with the first color
                        ShaderItem.meter_color_on = (FunctionItem.color_1)
                        log_to_file("  New Value from function: " + str(ShaderItem.meter_color_on))
                        ShaderItem.function_list.append(FunctionItem)     
                        
                if (Meter_Color_Off_Offset != 0):  #color
                    #log_to_file("meter_color_off offset: " + str(Meter_Color_Off_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Meter_Color_Off_Offset + 0xF + 0x1) == True):
                        ShaderItem.meter_color_off = get_rgb(shaderfile, Meter_Color_Off_Offset + 0xF + 0x1, "rgb")
                        log_to_file("meter_color_off: " + str(ShaderItem.meter_color_off))                    
                    else:
                        log_to_file("meter_color_off value/color not found")
                        
                    #check for function                       
                    if(has_function(shaderfile, Meter_Color_Off_Offset + 0xF + 0x1) == True): #value/color has function
                        FunctionItem = get_color_function_data(shaderfile, Meter_Color_Off_Offset + 0xF + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with the first color
                        ShaderItem.meter_color_off = (FunctionItem.color_1)
                        log_to_file("  New Value from function: " + str(ShaderItem.meter_color_off))
                        ShaderItem.function_list.append(FunctionItem)                            
                        
                if (Meter_Value_Offset != 0): #float
                    #log_to_file("meter_value offset: " + str(Meter_Value_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Meter_Value_Offset + 0xB + 0x1) == True):
                        ShaderItem.meter_value = get_value(shaderfile, Meter_Value_Offset + 0xB + 0x1)
                        log_to_file("meter_value: " + str(ShaderItem.meter_value))                    
                    else:
                        log_to_file("meter_value value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Meter_Value_Offset + 0xB + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Meter_Value_Offset + 0xB + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.meter_value = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.meter_value))
                        ShaderItem.function_list.append(FunctionItem)                      
                        
                if (Primary_Change_Color_blend_Offset != 0): #float
                    #log_to_file("primary_change_color_blend offset: " + str(Primary_Change_Color_blend_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Primary_Change_Color_blend_Offset + 0x1A + 0x1) == True):
                        ShaderItem.primary_change_color_blend = get_value(shaderfile, Primary_Change_Color_blend_Offset + 0x1A + 0x1)
                        log_to_file("primary_change_color_blend: " + str(ShaderItem.primary_change_color_blend))                    
                    else:
                        log_to_file("primary_change_color_blend value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Primary_Change_Color_blend_Offset + 0x1A + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Primary_Change_Color_blend_Offset + 0x1A + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.primary_change_color_blend = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.primary_change_color_blend))
                        ShaderItem.function_list.append(FunctionItem)                     
                        
                if (Height_Scale_Offset != 0): #float
                    #log_to_file("height_scale offset: " + str(Height_Scale_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Height_Scale_Offset + 0xC + 0x1) == True):
                        ShaderItem.height_scale = get_value(shaderfile, Height_Scale_Offset + 0xC + 0x1)
                        log_to_file("height_scale: " + str(ShaderItem.height_scale))                    
                    else:
                        log_to_file("height_scale value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Height_Scale_Offset + 0xC + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Height_Scale_Offset + 0xC + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.height_scale = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.height_scale))
                        ShaderItem.function_list.append(FunctionItem)                     
                        
                if (Diffuse_Coefficient_Offset != 0): #float
                    #log_to_file("diffuse_coefficient offset: " + str(Diffuse_Coefficient_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Diffuse_Coefficient_Offset + 0x13 + 0x1) == True):
                        ShaderItem.diffuse_coefficient = get_value(shaderfile, Diffuse_Coefficient_Offset + 0x13 + 0x1)
                        log_to_file("diffuse_coefficient: " + str(ShaderItem.diffuse_coefficient))                    
                    else:
                        log_to_file("diffuse_coefficient value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Diffuse_Coefficient_Offset + 0x13 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Diffuse_Coefficient_Offset + 0x13 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.diffuse_coefficient = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.diffuse_coefficient))
                        ShaderItem.function_list.append(FunctionItem)                      
                        
                if (Specular_Coefficient_Offset != 0): #float
                    #log_to_file("specular_coefficient offset: " + str(Specular_Coefficient_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Specular_Coefficient_Offset + 0x14 + 0x1) == True):
                        ShaderItem.specular_coefficient = get_value(shaderfile, Specular_Coefficient_Offset + 0x14 + 0x1)
                        log_to_file("specular_coefficient: " + str(ShaderItem.specular_coefficient))                    
                    else:
                        log_to_file("specular_coefficient value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Specular_Coefficient_Offset + 0x14 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Specular_Coefficient_Offset + 0x14 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.specular_coefficient = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.specular_coefficient))
                        ShaderItem.function_list.append(FunctionItem)                      
                        
                if (Specular_Tint_Offset != 0):  #color
                    #log_to_file("specular_tint offset: " + str(Specular_Tint_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Specular_Tint_Offset + 0xD + 0x1) == True):
                        ShaderItem.specular_tint = get_rgb(shaderfile, Specular_Tint_Offset + 0xD + 0x1, "rgb")
                        log_to_file("specular_tint: " + str(ShaderItem.specular_tint))                    
                    else:
                        ShaderItem.specular_tint = color_white_rgb
                        log_to_file("specular_tint value/color not found")
                        
                    #check for function                       
                    if(has_function(shaderfile, Specular_Tint_Offset + 0xD + 0x1) == True): #value/color has function
                        FunctionItem = get_color_function_data(shaderfile, Specular_Tint_Offset + 0xD + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with the first color
                        ShaderItem.specular_tint = (FunctionItem.color_1)
                        log_to_file("  New Value from function: " + str(ShaderItem.specular_tint))
                        ShaderItem.function_list.append(FunctionItem)                        
                        
                if (Fresnel_Color_Offset != 0):  #color
                    #log_to_file("fresnel_color offset: " + str(Fresnel_Color_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Fresnel_Color_Offset + 0xD + 0x1) == True):
                        ShaderItem.fresnel_color = get_rgb(shaderfile, Fresnel_Color_Offset + 0xD + 0x1, "rgb")
                        log_to_file("fresnel_color: " + str(ShaderItem.fresnel_color))                    
                    else:
                        log_to_file("fresnel_color value/color not found")
                        
                    #check for function                       
                    if(has_function(shaderfile, Fresnel_Color_Offset + 0xD + 0x1) == True): #value/color has function
                        FunctionItem = get_color_function_data(shaderfile, Fresnel_Color_Offset + 0xD + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with the first color
                        ShaderItem.fresnel_color = (FunctionItem.color_1)
                        log_to_file("  New Value from function: " + str(ShaderItem.fresnel_color))
                        ShaderItem.function_list.append(FunctionItem)                      
                        
                if (Roughness_Offset != 0): #float
                    #log_to_file("roughness offset: " + str(Roughness_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Roughness_Offset + 0x9 + 0x1) == True):
                        ShaderItem.roughness = get_value(shaderfile, Roughness_Offset + 0x9 + 0x1)
                        log_to_file("roughness: " + str(ShaderItem.roughness))                    
                    else:
                        log_to_file("roughness value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Roughness_Offset + 0x9 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Roughness_Offset + 0x9 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.roughness = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.roughness))
                        ShaderItem.function_list.append(FunctionItem)                    
                        
                if (Environment_Map_Specular_Contribution_Offset != 0): #float
                    #log_to_file("environment_map_specular_contribution offset: " + str(Environment_Map_Specular_Contribution_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Environment_Map_Specular_Contribution_Offset + 0x25 + 0x1) == True):
                        ShaderItem.environment_map_specular_contribution = get_value(shaderfile, Environment_Map_Specular_Contribution_Offset + 0x25 + 0x1)
                        log_to_file("environment_map_specular_contribution: " + str(ShaderItem.environment_map_specular_contribution))                    
                    else:
                        log_to_file("environment_map_specular_contribution value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Environment_Map_Specular_Contribution_Offset + 0x25 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Environment_Map_Specular_Contribution_Offset + 0x25 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.environment_map_specular_contribution = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.environment_map_specular_contribution))
                        ShaderItem.function_list.append(FunctionItem)                    
                        
                if (Use_Material_Texture_Offset != 0): #float
                    #log_to_file("use_material_texture offset: " + str(Use_Material_Texture_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Use_Material_Texture_Offset + 0x14 + 0x1) == True):
                        ShaderItem.use_material_texture = get_value(shaderfile, Use_Material_Texture_Offset + 0x14 + 0x1)
                        log_to_file("use_material_texture: " + str(ShaderItem.use_material_texture))                    
                    else:
                        log_to_file("use_material_texture value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Use_Material_Texture_Offset + 0x14 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Use_Material_Texture_Offset + 0x14 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.use_material_texture = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.use_material_texture))
                        ShaderItem.function_list.append(FunctionItem)                     
                        
                if (Normal_Specular_Power_Offset != 0): #float
                    #log_to_file("normal_specular_power offset: " + str(Normal_Specular_Power_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Normal_Specular_Power_Offset + 0x15 + 0x1) == True):
                        ShaderItem.normal_specular_power = get_value(shaderfile, Normal_Specular_Power_Offset + 0x15 + 0x1)
                        log_to_file("normal_specular_power: " + str(ShaderItem.normal_specular_power))                    
                    else:
                        log_to_file("normal_specular_power value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Normal_Specular_Power_Offset + 0x15 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Normal_Specular_Power_Offset + 0x15 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.normal_specular_power = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.normal_specular_power))
                        ShaderItem.function_list.append(FunctionItem)                    
                        
                if (Normal_Specular_Tint_Offset != 0):  #color
                    #log_to_file("normal_specular_tint offset: " + str(Normal_Specular_Tint_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Normal_Specular_Tint_Offset + 0x14 + 0x1) == True):
                        ShaderItem.normal_specular_tint = get_rgb(shaderfile, Normal_Specular_Tint_Offset + 0x14 + 0x1, "rgb")
                        log_to_file("normal_specular_tint: " + str(ShaderItem.normal_specular_tint))                    
                    else:
                        log_to_file("normal_specular_tint value/color not found")
                                               
                    #check for function                       
                    if(has_function(shaderfile, Normal_Specular_Tint_Offset + 0x14 + 0x1) == True): #value/color has function
                        FunctionItem = get_color_function_data(shaderfile, Normal_Specular_Tint_Offset + 0x14 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with the first color
                        ShaderItem.normal_specular_tint = (FunctionItem.color_1)
                        log_to_file("  New Value from function: " + str(ShaderItem.normal_specular_tint))
                        ShaderItem.function_list.append(FunctionItem)  

                        
                if (Glancing_Specular_Power_Offset != 0): #float
                    #log_to_file("glancing_specular_power offset: " + str(Glancing_Specular_Power_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Glancing_Specular_Power_Offset + 0x17 + 0x1) == True):
                        ShaderItem.glancing_specular_power = get_value(shaderfile, Glancing_Specular_Power_Offset + 0x17 + 0x1)
                        log_to_file("glancing_specular_power: " + str(ShaderItem.glancing_specular_power))                    
                    else:
                        log_to_file("glancing_specular_power value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Glancing_Specular_Power_Offset + 0x17 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Glancing_Specular_Power_Offset + 0x17 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.glancing_specular_power = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.glancing_specular_power))
                        ShaderItem.function_list.append(FunctionItem)                     
                        
                if (Glancing_Specular_Tint_Offset != 0):  #color
                    #log_to_file("glancing_specular_tint offset: " + str(Glancing_Specular_Tint_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Glancing_Specular_Tint_Offset + 0x16 + 0x1) == True):
                        ShaderItem.glancing_specular_tint = get_rgb(shaderfile, Glancing_Specular_Tint_Offset + 0x16 + 0x1, "rgb")
                        log_to_file("glancing_specular_tint: " + str(ShaderItem.glancing_specular_tint))                    
                    else:
                        log_to_file("glancing_specular_tint value/color not found")
                        
                    #check for function                       
                    if(has_function(shaderfile, Glancing_Specular_Tint_Offset + 0x16 + 0x1) == True): #value/color has function
                        FunctionItem = get_color_function_data(shaderfile, Glancing_Specular_Tint_Offset + 0x16 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with the first color
                        ShaderItem.glancing_specular_tint = (FunctionItem.color_1)
                        log_to_file("  New Value from function: " + str(ShaderItem.glancing_specular_tint))
                        ShaderItem.function_list.append(FunctionItem)  

      
                if (Fresnel_Curve_Steepness_Offset != 0): #float
                    #log_to_file("fresnel_curve_steepness offset: " + str(Fresnel_Curve_Steepness_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Fresnel_Curve_Steepness_Offset + 0x17 + 0x1) == True):
                        ShaderItem.fresnel_curve_steepness = get_value(shaderfile, Fresnel_Curve_Steepness_Offset + 0x17 + 0x1)
                        log_to_file("fresnel_curve_steepness: " + str(ShaderItem.fresnel_curve_steepness))                    
                    else:
                        log_to_file("fresnel_curve_steepness value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Fresnel_Curve_Steepness_Offset + 0x17 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Fresnel_Curve_Steepness_Offset + 0x17 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.fresnel_curve_steepness = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.fresnel_curve_steepness))
                        ShaderItem.function_list.append(FunctionItem)                      
                        
                if (Albedo_Specular_Tint_Blend_Offset != 0): #float
                    #log_to_file("albedo_specular_tint_blend offset: " + str(Albedo_Specular_Tint_Blend_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Albedo_Specular_Tint_Blend_Offset + 0x1A + 0x1) == True):
                        ShaderItem.albedo_specular_tint_blend = get_value(shaderfile, Albedo_Specular_Tint_Blend_Offset + 0x1A + 0x1)
                        log_to_file("albedo_specular_tint_blend: " + str(ShaderItem.albedo_specular_tint_blend))                    
                    else:
                        log_to_file("albedo_specular_tint_blend value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Albedo_Specular_Tint_Blend_Offset + 0x1A + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Albedo_Specular_Tint_Blend_Offset + 0x1A + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.albedo_specular_tint_blend = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.albedo_specular_tint_blend))
                        ShaderItem.function_list.append(FunctionItem)                     
                        
                if (Fresnel_Curve_Bias_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Fresnel_Curve_Bias_Offset + 0x12 + 0x1) == True):
                        ShaderItem.fresnel_curve_bias = get_value(shaderfile, Fresnel_Curve_Bias_Offset + 0x12 + 0x1)
                        log_to_file("fresnel_curve_bias: " + str(ShaderItem.fresnel_curve_bias))                    
                    else:
                        log_to_file("fresnel_curve_bias value/color not found")

                    #check for function
                    if(has_function(shaderfile, Fresnel_Curve_Bias_Offset + 0x12 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Fresnel_Curve_Bias_Offset + 0x12 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.fresnel_curve_bias = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.fresnel_curve_bias))
                        ShaderItem.function_list.append(FunctionItem)   
                        
                if (Fresnel_Coefficient_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Fresnel_Coefficient_Offset + 0x13 + 0x1) == True):
                        ShaderItem.fresnel_curve_bias = get_value(shaderfile, Fresnel_Coefficient_Offset + 0x13 + 0x1)
                        log_to_file("fresnel_coefficient: " + str(ShaderItem.fresnel_coefficient))                    
                    else:
                        log_to_file("fresnel_coefficient value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Fresnel_Coefficient_Offset + 0x13 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Fresnel_Coefficient_Offset + 0x13 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.fresnel_coefficient = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.fresnel_coefficient))
                        ShaderItem.function_list.append(FunctionItem)                     
                        
                if (Analytical_Specular_Contribution_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Analytical_Specular_Contribution_Offset + 0x20 + 0x1) == True):
                        ShaderItem.analytical_specular_contribution = get_value(shaderfile, Analytical_Specular_Contribution_Offset + 0x20 + 0x1)
                        log_to_file("analytical_specular_contribution: " + str(ShaderItem.analytical_specular_contribution))                    
                    else:
                        log_to_file("analytical_specular_contribution value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Analytical_Specular_Contribution_Offset + 0x20 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Analytical_Specular_Contribution_Offset + 0x20 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.analytical_specular_contribution = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.analytical_specular_contribution))
                        ShaderItem.function_list.append(FunctionItem)        
 
                if (Area_Specular_Contribution_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Area_Specular_Contribution_Offset + 0x1A + 0x1) == True):
                        ShaderItem.area_specular_contribution = get_value(shaderfile, Area_Specular_Contribution_Offset + 0x1A + 0x1)
                        log_to_file("area_specular_contribution: " + str(ShaderItem.area_specular_contribution))                    
                    else:
                        log_to_file("area_specular_contribution value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Area_Specular_Contribution_Offset + 0x1A + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Area_Specular_Contribution_Offset + 0x1A + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.area_specular_contribution = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.area_specular_contribution))
                        ShaderItem.function_list.append(FunctionItem)
                       
                if (Neutral_Gray_Offset != 0):  #color
                    #log_to_file("neutral_gray offset: " + str(Glancing_Specular_Tint_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Neutral_Gray_Offset + 0xC + 0x1) == True):
                        ShaderItem.neutral_gray = get_rgb(shaderfile, Neutral_Gray_Offset + 0xC + 0x1, "rgb")
                        log_to_file("neutral_gray: " + str(ShaderItem.neutral_gray))                    
                    else:
                        log_to_file("neutral_gray value/color not found")
                        
                    #check for function                       
                    if(has_function(shaderfile, Neutral_Gray_Offset + 0xC + 0x1) == True): #value/color has function
                        FunctionItem = get_color_function_data(shaderfile, Neutral_Gray_Offset + 0xC + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with the first color
                        ShaderItem.neutral_gray = (FunctionItem.color_1)
                        log_to_file("  New Value from function: " + str(ShaderItem.neutral_gray))
                        ShaderItem.function_list.append(FunctionItem)
                        
                Add_Value_Support(Specular_Power_Offset, "specular_power", "float", shaderfile, ShaderItem)        
                Add_Value_Support(Diffuse_Tint_Offset, "diffuse_tint", "color", shaderfile, ShaderItem)        
                Add_Value_Support(Analytical_Specular_Coefficient_Offset, "analytical_specular_coefficient", "float", shaderfile, ShaderItem)
                Add_Value_Support(Area_Specular_Coefficient_Offset, "area_specular_coefficient", "float", shaderfile, ShaderItem)
                Add_Value_Support(Environment_Map_Tint_Offset, "environment_map_tint", "color", shaderfile, ShaderItem)
                Add_Value_Support(Rim_Tint_Offset, "rim_tint", "color", shaderfile, ShaderItem)
                Add_Value_Support(Ambient_Tint_Offset, "ambient_tint", "color", shaderfile, ShaderItem)
                Add_Value_Support(Environment_Map_Coefficient_Offset, "environment_map_coefficient", "float", shaderfile, ShaderItem)
                Add_Value_Support(Rim_Coefficient_Offset, "rim_coefficient", "float", shaderfile, ShaderItem)
                Add_Value_Support(Rim_Power_Offset, "rim_power", "float", shaderfile, ShaderItem)
                Add_Value_Support(Rim_Start_Offset, "rim_start", "float", shaderfile, ShaderItem)
                Add_Value_Support(Rim_Maps_Transition_Ratio_Offset, "rim_maps_transition_ratio", "float", shaderfile, ShaderItem)
                Add_Value_Support(Ambient_Coefficient_Offset, "ambient_coefficient", "float", shaderfile, ShaderItem)
                Add_Value_Support(Subsurface_Coefficient_Offset, "subsurface_coefficient", "float", shaderfile, ShaderItem)
                Add_Value_Support(Subsurface_Tint_Offset, "subsurface_tint", "color", shaderfile, ShaderItem)
                Add_Value_Support(Subsurface_Propagation_Bias_Offset, "subsurface_propagation_bias", "float", shaderfile, ShaderItem)
                Add_Value_Support(Subsurface_Normal_Detail_Offset, "subsurface_normal_detail", "float", shaderfile, ShaderItem)
                Add_Value_Support(Transparence_Coefficient_Offset, "transparence_coefficient", "float", shaderfile, ShaderItem)
                Add_Value_Support(Transparence_Normal_Bias_Offset, "transparence_normal_bias", "float", shaderfile, ShaderItem)
                Add_Value_Support(Transparence_Tint_Offset, "transparence_tint", "color", shaderfile, ShaderItem)
                Add_Value_Support(Transparence_Normal_Detail_Offset, "transparence_normal_detail", "float", shaderfile, ShaderItem)
                Add_Value_Support(Final_Tint_Offset, "final_tint", "color", shaderfile, ShaderItem)
                
                
                ################
                #TERRAIN SHADERS
                ################
                
                if (Global_Albedo_Tint_Offset != 0):  #float
                    #log_to_file("global_albedo_tint offset: " + str(Global_Albedo_Tint_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Global_Albedo_Tint_Offset + 0x12 + 0x1) == True):
                        ShaderItem.global_albedo_tint = get_value(shaderfile, Global_Albedo_Tint_Offset + 0x12 + 0x1)
                        log_to_file("global_albedo_tint: " + str(ShaderItem.global_albedo_tint))                    
                    else:
                        log_to_file("global_albedo_tint value/color not found")
                        
                    #check for function                       
                    if(has_function(shaderfile, Global_Albedo_Tint_Offset + 0x12 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Global_Albedo_Tint_Offset + 0x12 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with the first color
                        ShaderItem.global_albedo_tint = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.global_albedo_tint))
                        ShaderItem.function_list.append(FunctionItem)      
                
                #Material 0
                if (Diffuse_Coefficient_M_0_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Diffuse_Coefficient_M_0_Offset + 0x17 + 0x1) == True):
                        ShaderItem.diffuse_coefficient_m_0 = get_value(shaderfile, Diffuse_Coefficient_M_0_Offset + 0x17 + 0x1)
                        log_to_file("diffuse_coefficient_m_0: " + str(ShaderItem.diffuse_coefficient_m_0))                    
                    else:
                        log_to_file("diffuse_coefficient_m_0 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Diffuse_Coefficient_M_0_Offset + 0x17 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Diffuse_Coefficient_M_0_Offset + 0x17 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.diffuse_coefficient_m_0 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.diffuse_coefficient_m_0))
                        ShaderItem.function_list.append(FunctionItem)

                if (Specular_Coefficient_M_0_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Specular_Coefficient_M_0_Offset + 0x18 + 0x1) == True):
                        ShaderItem.specular_coefficient_m_0 = get_value(shaderfile, Specular_Coefficient_M_0_Offset + 0x18 + 0x1)
                        log_to_file("specular_coefficient_m_0: " + str(ShaderItem.specular_coefficient_m_0))                    
                    else:
                        log_to_file("specular_coefficient_m_0 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Specular_Coefficient_M_0_Offset + 0x18 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Specular_Coefficient_M_0_Offset + 0x18 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.specular_coefficient_m_0 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.specular_coefficient_m_0))
                        ShaderItem.function_list.append(FunctionItem)

                if (Specular_Power_M_0_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Specular_Power_M_0_Offset + 0x12 + 0x1) == True):
                        ShaderItem.specular_power_m_0 = get_value(shaderfile, Specular_Power_M_0_Offset + 0x12 + 0x1)
                        log_to_file("specular_power_m_0: " + str(ShaderItem.specular_power_m_0))                    
                    else:
                        log_to_file("specular_power_m_0 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Specular_Power_M_0_Offset + 0x12 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Specular_Power_M_0_Offset + 0x12 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.specular_power_m_0 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.specular_power_m_0))
                        ShaderItem.function_list.append(FunctionItem)

                if (Specular_Tint_M_0_Offset != 0):  #color
                    #log_to_file("global_albedo_tint offset: " + str(Specular_Tint_M_0_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Specular_Tint_M_0_Offset + 0x11 + 0x1) == True):
                        ShaderItem.specular_tint_m_0 = get_rgb(shaderfile, Specular_Tint_M_0_Offset + 0x11 + 0x1, "rgb")
                        log_to_file("specular_tint_m_0: " + str(ShaderItem.specular_tint_m_0))                    
                    else:
                        log_to_file("specular_tint_m_0 value/color not found")
                        
                    #check for function                       
                    if(has_function(shaderfile, Specular_Tint_M_0_Offset + 0x11 + 0x1) == True): #value/color has function
                        FunctionItem = get_color_function_data(shaderfile, Specular_Tint_M_0_Offset + 0x11 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with the first color
                        ShaderItem.specular_tint_m_0 = (FunctionItem.color_1)
                        log_to_file("  New Value from function: " + str(ShaderItem.specular_tint_m_0))
                        ShaderItem.function_list.append(FunctionItem)   

                if (Fresnel_Curve_Steepness_M_0_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Fresnel_Curve_Steepness_M_0_Offset + 0x1B + 0x1) == True):
                        ShaderItem.fresnel_curve_steepness_m_0 = get_value(shaderfile, Fresnel_Curve_Steepness_M_0_Offset + 0x1B + 0x1)
                        log_to_file("fresnel_curve_steepness_m_0: " + str(ShaderItem.fresnel_curve_steepness_m_0))                    
                    else:
                        log_to_file("fresnel_curve_steepness_m_0 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Fresnel_Curve_Steepness_M_0_Offset + 0x1B + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Fresnel_Curve_Steepness_M_0_Offset + 0x1B + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.fresnel_curve_steepness_m_0 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.fresnel_curve_steepness_m_0))
                        ShaderItem.function_list.append(FunctionItem)

                if (Area_Specular_Contribution_M_0_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Area_Specular_Contribution_M_0_Offset + 0x1E + 0x1) == True):
                        ShaderItem.area_specular_contribution_m_0 = get_value(shaderfile, Area_Specular_Contribution_M_0_Offset + 0x1E + 0x1)
                        log_to_file("area_specular_contribution_m_0: " + str(ShaderItem.area_specular_contribution_m_0))                    
                    else:
                        log_to_file("area_specular_contribution_m_0 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Area_Specular_Contribution_M_0_Offset + 0x1E + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Area_Specular_Contribution_M_0_Offset + 0x1E + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.area_specular_contribution_m_0 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.area_specular_contribution_m_0))
                        ShaderItem.function_list.append(FunctionItem)


                if (Analytical_Specular_Contribution_M_0_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Analytical_Specular_Contribution_M_0_Offset + 0x24 + 0x1) == True):
                        ShaderItem.analytical_specular_contribution_m_0 = get_value(shaderfile, Analytical_Specular_Contribution_M_0_Offset + 0x24 + 0x1)
                        log_to_file("analytical_specular_contribution_m_0: " + str(ShaderItem.analytical_specular_contribution_m_0))                    
                    else:
                        log_to_file("analytical_specular_contribution_m_0 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Analytical_Specular_Contribution_M_0_Offset + 0x24 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Analytical_Specular_Contribution_M_0_Offset + 0x24 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.analytical_specular_contribution_m_0 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.analytical_specular_contribution_m_0))
                        ShaderItem.function_list.append(FunctionItem)

                if (Environment_Specular_Contribution_M_0_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Environment_Specular_Contribution_M_0_Offset + 0x25 + 0x1) == True):
                        ShaderItem.environment_specular_contribution_m_0 = get_value(shaderfile, Environment_Specular_Contribution_M_0_Offset + 0x25 + 0x1)
                        log_to_file("environment_specular_contribution_m_0: " + str(ShaderItem.environment_specular_contribution_m_0))                    
                    else:
                        log_to_file("environment_specular_contribution_m_0 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Environment_Specular_Contribution_M_0_Offset + 0x25 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Environment_Specular_Contribution_M_0_Offset + 0x25 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.environment_specular_contribution_m_0 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.environment_specular_contribution_m_0))
                        ShaderItem.function_list.append(FunctionItem)

                if (Albedo_Specular_Tint_Blend_M_0_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Albedo_Specular_Tint_Blend_M_0_Offset + 0x1E + 0x1) == True):
                        ShaderItem.albedo_specular_tint_blend_m_0 = get_value(shaderfile, Albedo_Specular_Tint_Blend_M_0_Offset + 0x1E + 0x1)
                        log_to_file("albedo_specular_tint_blend_m_0: " + str(ShaderItem.albedo_specular_tint_blend_m_0))                    
                    else:
                        log_to_file("albedo_specular_tint_blend_m_0 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Albedo_Specular_Tint_Blend_M_0_Offset + 0x1E + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Albedo_Specular_Tint_Blend_M_0_Offset + 0x1E + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.albedo_specular_tint_blend_m_0 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.albedo_specular_tint_blend_m_0))
                        ShaderItem.function_list.append(FunctionItem)

                #Material 1
                if (Diffuse_Coefficient_M_1_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Diffuse_Coefficient_M_1_Offset + 0x17 + 0x1) == True):
                        ShaderItem.diffuse_coefficient_m_1 = get_value(shaderfile, Diffuse_Coefficient_M_1_Offset + 0x17 + 0x1)
                        log_to_file("diffuse_coefficient_m_1: " + str(ShaderItem.diffuse_coefficient_m_1))                    
                    else:
                        log_to_file("diffuse_coefficient_m_1 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Diffuse_Coefficient_M_1_Offset + 0x17 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Diffuse_Coefficient_M_1_Offset + 0x17 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.diffuse_coefficient_m_1 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.diffuse_coefficient_m_1))
                        ShaderItem.function_list.append(FunctionItem)

                if (Specular_Coefficient_M_1_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Specular_Coefficient_M_1_Offset + 0x18 + 0x1) == True):
                        ShaderItem.specular_coefficient_m_1 = get_value(shaderfile, Specular_Coefficient_M_1_Offset + 0x18 + 0x1)
                        log_to_file("specular_coefficient_m_1: " + str(ShaderItem.specular_coefficient_m_1))                    
                    else:
                        log_to_file("specular_coefficient_m_1 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Specular_Coefficient_M_1_Offset + 0x18 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Specular_Coefficient_M_1_Offset + 0x18 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.specular_coefficient_m_1 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.specular_coefficient_m_1))
                        ShaderItem.function_list.append(FunctionItem)

                if (Specular_Power_M_1_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Specular_Power_M_1_Offset + 0x12 + 0x1) == True):
                        ShaderItem.specular_power_m_1 = get_value(shaderfile, Specular_Power_M_1_Offset + 0x12 + 0x1)
                        log_to_file("specular_power_m_1: " + str(ShaderItem.specular_power_m_1))                    
                    else:
                        log_to_file("specular_power_m_1 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Specular_Power_M_1_Offset + 0x12 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Specular_Power_M_1_Offset + 0x12 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.specular_power_m_1 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.specular_power_m_1))
                        ShaderItem.function_list.append(FunctionItem)

                if (Specular_Tint_M_1_Offset != 0):  #color
                    #log_to_file("global_albedo_tint offset: " + str(Specular_Tint_M_1_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Specular_Tint_M_1_Offset + 0x11 + 0x1) == True):
                        ShaderItem.specular_tint_m_1 = get_rgb(shaderfile, Specular_Tint_M_1_Offset + 0x11 + 0x1, "rgb")
                        log_to_file("specular_tint_m_1: " + str(ShaderItem.specular_tint_m_1))                    
                    else:
                        log_to_file("specular_tint_m_1 value/color not found")
                        
                    #check for function                       
                    if(has_function(shaderfile, Specular_Tint_M_1_Offset + 0x11 + 0x1) == True): #value/color has function
                        FunctionItem = get_color_function_data(shaderfile, Specular_Tint_M_1_Offset + 0x11 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with the first color
                        ShaderItem.specular_tint_m_1 = (FunctionItem.color_1)
                        log_to_file("  New Value from function: " + str(ShaderItem.specular_tint_m_1))
                        ShaderItem.function_list.append(FunctionItem)   

                if (Fresnel_Curve_Steepness_M_1_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Fresnel_Curve_Steepness_M_1_Offset + 0x1B + 0x1) == True):
                        ShaderItem.fresnel_curve_steepness_m_1 = get_value(shaderfile, Fresnel_Curve_Steepness_M_1_Offset + 0x1B + 0x1)
                        log_to_file("fresnel_curve_steepness_m_1: " + str(ShaderItem.fresnel_curve_steepness_m_1))                    
                    else:
                        log_to_file("fresnel_curve_steepness_m_1 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Fresnel_Curve_Steepness_M_1_Offset + 0x1B + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Fresnel_Curve_Steepness_M_1_Offset + 0x1B + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.fresnel_curve_steepness_m_1 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.fresnel_curve_steepness_m_1))
                        ShaderItem.function_list.append(FunctionItem)

                if (Area_Specular_Contribution_M_1_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Area_Specular_Contribution_M_1_Offset + 0x1E + 0x1) == True):
                        ShaderItem.area_specular_contribution_m_1 = get_value(shaderfile, Area_Specular_Contribution_M_1_Offset + 0x1E + 0x1)
                        log_to_file("area_specular_contribution_m_1: " + str(ShaderItem.area_specular_contribution_m_1))                    
                    else:
                        log_to_file("area_specular_contribution_m_1 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Area_Specular_Contribution_M_1_Offset + 0x1E + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Area_Specular_Contribution_M_1_Offset + 0x1E + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.area_specular_contribution_m_1 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.area_specular_contribution_m_1))
                        ShaderItem.function_list.append(FunctionItem)


                if (Analytical_Specular_Contribution_M_1_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Analytical_Specular_Contribution_M_1_Offset + 0x24 + 0x1) == True):
                        ShaderItem.analytical_specular_contribution_m_1 = get_value(shaderfile, Analytical_Specular_Contribution_M_1_Offset + 0x24 + 0x1)
                        log_to_file("analytical_specular_contribution_m_1: " + str(ShaderItem.analytical_specular_contribution_m_1))                    
                    else:
                        log_to_file("analytical_specular_contribution_m_1 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Analytical_Specular_Contribution_M_1_Offset + 0x24 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Analytical_Specular_Contribution_M_1_Offset + 0x24 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.analytical_specular_contribution_m_1 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.analytical_specular_contribution_m_1))
                        ShaderItem.function_list.append(FunctionItem)

                if (Environment_Specular_Contribution_M_1_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Environment_Specular_Contribution_M_1_Offset + 0x25 + 0x1) == True):
                        ShaderItem.environment_specular_contribution_m_1 = get_value(shaderfile, Environment_Specular_Contribution_M_1_Offset + 0x25 + 0x1)
                        log_to_file("environment_specular_contribution_m_1: " + str(ShaderItem.environment_specular_contribution_m_1))                    
                    else:
                        log_to_file("environment_specular_contribution_m_1 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Environment_Specular_Contribution_M_1_Offset + 0x25 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Environment_Specular_Contribution_M_1_Offset + 0x25 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.environment_specular_contribution_m_1 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.environment_specular_contribution_m_1))
                        ShaderItem.function_list.append(FunctionItem)

                if (Albedo_Specular_Tint_Blend_M_1_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Albedo_Specular_Tint_Blend_M_1_Offset + 0x1E + 0x1) == True):
                        ShaderItem.albedo_specular_tint_blend_m_1 = get_value(shaderfile, Albedo_Specular_Tint_Blend_M_1_Offset + 0x1E + 0x1)
                        log_to_file("albedo_specular_tint_blend_m_1: " + str(ShaderItem.albedo_specular_tint_blend_m_1))                    
                    else:
                        log_to_file("albedo_specular_tint_blend_m_1 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Albedo_Specular_Tint_Blend_M_1_Offset + 0x1E + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Albedo_Specular_Tint_Blend_M_1_Offset + 0x1E + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.albedo_specular_tint_blend_m_1 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.albedo_specular_tint_blend_m_1))
                        ShaderItem.function_list.append(FunctionItem)
                        
                #Material 2        
                if (Diffuse_Coefficient_M_2_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Diffuse_Coefficient_M_2_Offset + 0x17 + 0x1) == True):
                        ShaderItem.diffuse_coefficient_m_2 = get_value(shaderfile, Diffuse_Coefficient_M_2_Offset + 0x17 + 0x1)
                        log_to_file("diffuse_coefficient_m_2: " + str(ShaderItem.diffuse_coefficient_m_2))                    
                    else:
                        log_to_file("diffuse_coefficient_m_2 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Diffuse_Coefficient_M_2_Offset + 0x17 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Diffuse_Coefficient_M_2_Offset + 0x17, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.diffuse_coefficient_m_2 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.diffuse_coefficient_m_2))
                        ShaderItem.function_list.append(FunctionItem)

                if (Specular_Coefficient_M_2_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Specular_Coefficient_M_2_Offset + 0x18 + 0x1) == True):
                        ShaderItem.specular_coefficient_m_2 = get_value(shaderfile, Specular_Coefficient_M_2_Offset + 0x18 + 0x1)
                        log_to_file("specular_coefficient_m_2: " + str(ShaderItem.specular_coefficient_m_2))                    
                    else:
                        log_to_file("specular_coefficient_m_2 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Specular_Coefficient_M_2_Offset + 0x18 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Specular_Coefficient_M_2_Offset + 0x18 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.specular_coefficient_m_2 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.specular_coefficient_m_2))
                        ShaderItem.function_list.append(FunctionItem)

                if (Specular_Power_M_2_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Specular_Power_M_2_Offset + 0x12 + 0x1) == True):
                        ShaderItem.specular_power_m_2 = get_value(shaderfile, Specular_Power_M_2_Offset + 0x12 + 0x1)
                        log_to_file("specular_power_m_2: " + str(ShaderItem.specular_power_m_2))                    
                    else:
                        log_to_file("specular_power_m_2 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Specular_Power_M_2_Offset + 0x12 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Specular_Power_M_2_Offset + 0x12 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.specular_power_m_2 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.specular_power_m_2))
                        ShaderItem.function_list.append(FunctionItem)

                if (Specular_Tint_M_2_Offset != 0):  #color
                    #log_to_file("global_albedo_tint offset: " + str(Specular_Tint_M_2_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Specular_Tint_M_2_Offset + 0x11 + 0x1) == True):
                        ShaderItem.specular_tint_m_2 = get_rgb(shaderfile, Specular_Tint_M_2_Offset + 0x11 + 0x1, "rgb")
                        log_to_file("specular_tint_m_2: " + str(ShaderItem.specular_tint_m_2))                    
                    else:
                        log_to_file("specular_tint_m_2 value/color not found")
                        
                    #check for function                       
                    if(has_function(shaderfile, Specular_Tint_M_2_Offset + 0x11 + 0x1) == True): #value/color has function
                        FunctionItem = get_color_function_data(shaderfile, Specular_Tint_M_2_Offset + 0x11 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with the first color
                        ShaderItem.specular_tint_m_2 = (FunctionItem.color_1)
                        log_to_file("  New Value from function: " + str(ShaderItem.specular_tint_m_2))
                        ShaderItem.function_list.append(FunctionItem)    

                if (Fresnel_Curve_Steepness_M_2_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Fresnel_Curve_Steepness_M_2_Offset + 0x1B + 0x1) == True):
                        ShaderItem.fresnel_curve_steepness_m_2 = get_value(shaderfile, Fresnel_Curve_Steepness_M_2_Offset + 0x1B + 0x1)
                        log_to_file("fresnel_curve_steepness_m_2: " + str(ShaderItem.fresnel_curve_steepness_m_2))                    
                    else:
                        log_to_file("fresnel_curve_steepness_m_2 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Fresnel_Curve_Steepness_M_2_Offset + 0x1B + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Fresnel_Curve_Steepness_M_2_Offset + 0x1B + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.fresnel_curve_steepness_m_2 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.fresnel_curve_steepness_m_2))
                        ShaderItem.function_list.append(FunctionItem)

                if (Area_Specular_Contribution_M_2_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Area_Specular_Contribution_M_2_Offset + 0x1E + 0x1) == True):
                        ShaderItem.area_specular_contribution_m_2 = get_value(shaderfile, Area_Specular_Contribution_M_2_Offset + 0x1E + 0x1)
                        log_to_file("area_specular_contribution_m_2: " + str(ShaderItem.area_specular_contribution_m_2))                    
                    else:
                        log_to_file("area_specular_contribution_m_2 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Area_Specular_Contribution_M_2_Offset + 0x1E + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Area_Specular_Contribution_M_2_Offset + 0x1E + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.area_specular_contribution_m_2 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.area_specular_contribution_m_2))
                        ShaderItem.function_list.append(FunctionItem)


                if (Analytical_Specular_Contribution_M_2_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Analytical_Specular_Contribution_M_2_Offset + 0x24 + 0x1) == True):
                        ShaderItem.analytical_specular_contribution_m_2 = get_value(shaderfile, Analytical_Specular_Contribution_M_2_Offset + 0x24 + 0x1)
                        log_to_file("analytical_specular_contribution_m_2: " + str(ShaderItem.analytical_specular_contribution_m_2))                    
                    else:
                        log_to_file("analytical_specular_contribution_m_2 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Analytical_Specular_Contribution_M_2_Offset + 0x24 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Analytical_Specular_Contribution_M_2_Offset + 0x24 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.analytical_specular_contribution_m_2 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.analytical_specular_contribution_m_2))
                        ShaderItem.function_list.append(FunctionItem)

                if (Environment_Specular_Contribution_M_2_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Environment_Specular_Contribution_M_2_Offset + 0x25 + 0x1) == True):
                        ShaderItem.environment_specular_contribution_m_2 = get_value(shaderfile, Environment_Specular_Contribution_M_2_Offset + 0x25 + 0x1)
                        log_to_file("environment_specular_contribution_m_2: " + str(ShaderItem.environment_specular_contribution_m_2))                    
                    else:
                        log_to_file("environment_specular_contribution_m_2 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Environment_Specular_Contribution_M_2_Offset + 0x25 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Environment_Specular_Contribution_M_2_Offset + 0x25 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.environment_specular_contribution_m_2 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.environment_specular_contribution_m_2))
                        ShaderItem.function_list.append(FunctionItem)

                if (Albedo_Specular_Tint_Blend_M_2_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Albedo_Specular_Tint_Blend_M_2_Offset + 0x1E + 0x1) == True):
                        ShaderItem.albedo_specular_tint_blend_m_2 = get_value(shaderfile, Albedo_Specular_Tint_Blend_M_2_Offset + 0x1E + 0x1)
                        log_to_file("albedo_specular_tint_blend_m_2: " + str(ShaderItem.albedo_specular_tint_blend_m_2))                    
                    else:
                        log_to_file("albedo_specular_tint_blend_m_2 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Albedo_Specular_Tint_Blend_M_2_Offset + 0x1E + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Albedo_Specular_Tint_Blend_M_2_Offset + 0x1E + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.albedo_specular_tint_blend_m_2 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.albedo_specular_tint_blend_m_2))
                        ShaderItem.function_list.append(FunctionItem)

                #Material 3
                if (Diffuse_Coefficient_M_3_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Diffuse_Coefficient_M_3_Offset + 0x17 + 0x1) == True):
                        ShaderItem.diffuse_coefficient_m_3 = get_value(shaderfile, Diffuse_Coefficient_M_3_Offset + 0x17 + 0x1)
                        log_to_file("diffuse_coefficient_m_3: " + str(ShaderItem.diffuse_coefficient_m_3))                    
                    else:
                        log_to_file("diffuse_coefficient_m_3 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Diffuse_Coefficient_M_3_Offset + 0x17 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Diffuse_Coefficient_M_3_Offset + 0x17 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.diffuse_coefficient_m_3 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.diffuse_coefficient_m_3))
                        ShaderItem.function_list.append(FunctionItem)

                if (Specular_Coefficient_M_3_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Specular_Coefficient_M_3_Offset + 0x18 + 0x1) == True):
                        ShaderItem.specular_coefficient_m_3 = get_value(shaderfile, Specular_Coefficient_M_3_Offset + 0x18 + 0x1)
                        log_to_file("specular_coefficient_m_3: " + str(ShaderItem.specular_coefficient_m_3))                    
                    else:
                        log_to_file("specular_coefficient_m_3 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Specular_Coefficient_M_3_Offset + 0x18 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Specular_Coefficient_M_3_Offset + 0x18 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.specular_coefficient_m_3 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.specular_coefficient_m_3))
                        ShaderItem.function_list.append(FunctionItem)

                if (Specular_Power_M_3_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Specular_Power_M_3_Offset + 0x12 + 0x1) == True):
                        ShaderItem.specular_power_m_3 = get_value(shaderfile, Specular_Power_M_3_Offset + 0x12 + 0x1)
                        log_to_file("specular_power_m_3: " + str(ShaderItem.specular_power_m_3))                    
                    else:
                        log_to_file("specular_power_m_3 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Specular_Power_M_3_Offset + 0x12 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Specular_Power_M_3_Offset + 0x12 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.specular_power_m_3 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.specular_power_m_3))
                        ShaderItem.function_list.append(FunctionItem)

                if (Specular_Tint_M_3_Offset != 0):  #color
                    #log_to_file("global_albedo_tint offset: " + str(Specular_Tint_M_3_Offset))
                    
                    #save current data
                    if(has_value(shaderfile, Specular_Tint_M_3_Offset + 0x11 + 0x1) == True):
                        ShaderItem.specular_tint_m_3 = get_rgb(shaderfile, Specular_Tint_M_3_Offset + 0x11 + 0x1, "rgb")
                        log_to_file("specular_tint_m_3: " + str(ShaderItem.specular_tint_m_3))                    
                    else:
                        log_to_file("specular_tint_m_3 value/color not found")
                        
                    #check for function 
                    if(has_function(shaderfile, Specular_Tint_M_3_Offset + 0x11 + 0x1) == True): #value/color has function
                        FunctionItem = get_color_function_data(shaderfile, Specular_Tint_M_3_Offset + 0x11 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with the first color
                        ShaderItem.specular_tint_m_3 = (FunctionItem.color_1)
                        log_to_file("  New Value from function: " + str(ShaderItem.specular_tint_m_3))
                        ShaderItem.function_list.append(FunctionItem)

                if (Fresnel_Curve_Steepness_M_3_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Fresnel_Curve_Steepness_M_3_Offset + 0x1B + 0x1) == True):
                        ShaderItem.fresnel_curve_steepness_m_3 = get_value(shaderfile, Fresnel_Curve_Steepness_M_3_Offset + 0x1B + 0x1)
                        log_to_file("fresnel_curve_steepness_m_3: " + str(ShaderItem.fresnel_curve_steepness_m_3))                    
                    else:
                        log_to_file("fresnel_curve_steepness_m_3 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Fresnel_Curve_Steepness_M_3_Offset + 0x1B + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Fresnel_Curve_Steepness_M_3_Offset + 0x1B + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.fresnel_curve_steepness_m_3 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.fresnel_curve_steepness_m_3))
                        ShaderItem.function_list.append(FunctionItem)

                if (Area_Specular_Contribution_M_3_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Area_Specular_Contribution_M_3_Offset + 0x1E + 0x1) == True):
                        ShaderItem.area_specular_contribution_m_3 = get_value(shaderfile, Area_Specular_Contribution_M_3_Offset + 0x1E + 0x1)
                        log_to_file("area_specular_contribution_m_3: " + str(ShaderItem.area_specular_contribution_m_3))                    
                    else:
                        log_to_file("area_specular_contribution_m_3 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Area_Specular_Contribution_M_3_Offset + 0x1E + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Area_Specular_Contribution_M_3_Offset + 0x1E + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.area_specular_contribution_m_3 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.area_specular_contribution_m_3))
                        ShaderItem.function_list.append(FunctionItem)


                if (Analytical_Specular_Contribution_M_3_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Analytical_Specular_Contribution_M_3_Offset + 0x24 + 0x1) == True):
                        ShaderItem.analytical_specular_contribution_m_3 = get_value(shaderfile, Analytical_Specular_Contribution_M_3_Offset + 0x24 + 0x1)
                        log_to_file("analytical_specular_contribution_m_3: " + str(ShaderItem.analytical_specular_contribution_m_3))                    
                    else:
                        log_to_file("analytical_specular_contribution_m_3 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Analytical_Specular_Contribution_M_3_Offset + 0x24 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Analytical_Specular_Contribution_M_3_Offset + 0x24 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.analytical_specular_contribution_m_3 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.analytical_specular_contribution_m_3))
                        ShaderItem.function_list.append(FunctionItem)

                if (Environment_Specular_Contribution_M_3_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Environment_Specular_Contribution_M_3_Offset + 0x25 + 0x1) == True):
                        ShaderItem.environment_specular_contribution_m_3 = get_value(shaderfile, Environment_Specular_Contribution_M_3_Offset + 0x25 + 0x1)
                        log_to_file("environment_specular_contribution_m_3: " + str(ShaderItem.environment_specular_contribution_m_3))                    
                    else:
                        log_to_file("environment_specular_contribution_m_3 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Environment_Specular_Contribution_M_3_Offset + 0x25 + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Environment_Specular_Contribution_M_3_Offset + 0x25 + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.environment_specular_contribution_m_3 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.environment_specular_contribution_m_3))
                        ShaderItem.function_list.append(FunctionItem)

                if (Albedo_Specular_Tint_Blend_M_3_Offset != 0): #float
                    #save current data
                    if(has_value(shaderfile, Albedo_Specular_Tint_Blend_M_3_Offset + 0x1E + 0x1) == True):
                        ShaderItem.albedo_specular_tint_blend_m_3 = get_value(shaderfile, Albedo_Specular_Tint_Blend_M_3_Offset + 0x1E + 0x1)
                        log_to_file("albedo_specular_tint_blend_m_3: " + str(ShaderItem.albedo_specular_tint_blend_m_3))                    
                    else:
                        log_to_file("albedo_specular_tint_blend_m_3 value/color not found")
                        
                    #check for function
                    if(has_function(shaderfile, Albedo_Specular_Tint_Blend_M_3_Offset + 0x1E + 0x1) == True): #value/color has function
                        FunctionItem = get_function_data(shaderfile, Albedo_Specular_Tint_Blend_M_3_Offset + 0x1E + 0x1, FunctionItem) #grab function data and store it
                        print_function(FunctionItem) 
                        
                        #overrite some data for this item with the function data with halved value for testing
                        ShaderItem.albedo_specular_tint_blend_m_3 = (FunctionItem.main_max_value + FunctionItem.main_min_value) / 2
                        log_to_file("  New Value from function: " + str(ShaderItem.albedo_specular_tint_blend_m_3))
                        ShaderItem.function_list.append(FunctionItem)                    

                            ######################
                            #GATHER WRAP MODE INFO
                            ######################
        
                #ShaderItem.wrap_mode_list = get_wrap_mode_list(shaderfile, Shader_Type, ShaderItem.wrap_mode_list)                    
                ShaderItem = get_wrap_mode_list(shaderfile, Shader_Type, ShaderItem)                    

                log_to_file("built wrap_mode_list")           
                shaderfile.close()
                
                
                #search for shader file in directory
                
                #open file in rb mode
                
                #build all data from shader file
                    #bitmap count
                    #list of Bitmap class object
                        #name of bitmap
                        #directory of bitmap
                        #bitmap curve option
                
                #Set Blend Method of Material
                if(Shader_Type == 0): #if .shader file
                    if (ShaderItem.blend_mode_option == 0):
                        pymat_copy.blend_method = 'OPAQUE'
                    elif (ShaderItem.blend_mode_option == 1):
                        pymat_copy.blend_method = Preferred_Blend
                    elif (ShaderItem.blend_mode_option == 3 or ShaderItem.blend_mode_option == 5):
                        pymat_copy.blend_method = Preferred_Blend
                    else:
                        pymat_copy.blend_method = 'OPAQUE'
                        
                    if (ShaderItem.alpha_test_option == 1):
                        pymat_copy.blend_method = Preferred_Blend 
                
                #foliage
                if (Shader_Type == 2):
                    pymat_copy.blend_method = Preferred_Blend
                    
                #decals shaders    
                if (Shader_Type == 6):
                    if(ShaderItem.blend_mode_option != 0): #if it is not opaque
                        pymat_copy.blend_method = Preferred_Blend
                
                #instantiate_group(bpy.context.object.material_slots[0].material.node_tree.nodes, 'NodeGroup')    
                    
                log_to_file("Bitmap Count: " + str(ShaderItem.bitmap_count)) 
                log_to_file("")
                log_to_file("")        
                pymat_copy.use_nodes = True
                log_to_file("  Clearing Old Nodes-------------------------------------------------------")
                pymat_copy.node_tree.nodes.clear() #clear all nodes from the current tree
                
                
                
                # #location
                # imgtx1.location = Vector((200.0, 400.0))

                # imgtx2.location.x = 100
                # imgtx2.location.y = 200

                # #size
                # # only width changes are allowed within the values of 
                # # node.bl_width_min and node.bl_width_max
                # imgtx2.width = 200
                # imgtx2.width_hidden = 100
                
                #Texture.hide = True         collapses the nodes
                
                #Global variables for node placement
                last_node_x = 0.00
                last_node_y = 0.00
                end_group_x = 0.00
                end_group_y = 0.00
                mat_group_x = 0.00
                mat_group_y = 0.00
                alb_group_x = 0.00
                alb_group_y = 0.00
                bump_group_x = 0.00
                bump_group_y = 0.00
                terr_group_x = 0.00
                terr_group_y = 0.00
                last_texture_x = 0.00
                last_texture_y = 0.00
                
                before_no_tex_x = 0.00
                before_no_tex_y = 0.00
                
                albedo_group_made = 0
                mat_group_made = 0
                bump_group_made = 0
                env_group_made = 0
                illum_group_made = 0
                texture_node_made = 0
                gamma_node_made = 0
                mirror_node_made = 0
                trans_node_made = 0    
                
                
                 
                #Function for making bigger node groups
                def instantiate_group(nodes, data_block_name):
                    group = nodes.new(type='ShaderNodeGroup')
                    group.node_tree = bpy.data.node_groups[data_block_name]
                    return group


                                    ############################    
                                    #Material Output Node Create
                                    ############################
                ############
                #all shaders
                ############
                
                pymat_copy.node_tree.nodes.new('ShaderNodeOutputMaterial')
                material_output = pymat_copy.node_tree.nodes.get("Material Output")
                
                log_to_file("Count of Shader Outputs: " + str(ShaderOutputCount))    

                #locations of group    
                last_node_x = material_output.location.x
                last_node_y = material_output.location.y

                                    #########################
                                    #Alpha Blend Group Create
                                    #########################
                #.shader files and .shader_halogram
                if((Shader_Type == 0 or Shader_Type == 3 or Shader_Type == 4) and (ShaderItem.blend_mode_option == 3 or ShaderItem.blend_mode_option == 5)):
                    AlphaBlendGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3RCategory: blend_mode - alpha_blend")

                    #locations of group
                    AlphaBlendGroup.location.x = last_node_x - ALPHA_BLEND_HORIZONTAL_SPACING
                    AlphaBlendGroup.location.y = last_node_y
                        
                    last_node_x = AlphaBlendGroup.location.x
                    last_node_y = AlphaBlendGroup.location.y
                    

                                    ########################
                                    #Alpha Test Group Create
                                    ########################
                # .shader files                           #if alpha_test is simple
                if((Shader_Type == 0 or Shader_Type == 2 or Shader_Type == 4) and (ShaderItem.alpha_test_option == 1)): #H3RCategory: alpha_test - simple 
                    AlphaTestGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3RCategory: alpha_test - simple")

                    #locations of group
                    AlphaTestGroup.location.x = last_node_x - ALPHA_TEST_HORIZONTAL_SPACING
                    AlphaTestGroup.location.y = last_node_y
                        
                    last_node_x = AlphaTestGroup.location.x
                    last_node_y = AlphaTestGroup.location.y
                    
                elif((Shader_Type == 0 or Shader_Type == 2 or Shader_Type == 4) and (ShaderItem.alpha_test_option == 2)): #H3RCategory_Custom: alpha_test - multiply_map
                    AlphaTestGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3RCategory_Custom: alpha_test - multiply_map")

                    #locations of group
                    AlphaTestGroup.location.x = last_node_x - ALPHA_TEST_HORIZONTAL_SPACING
                    AlphaTestGroup.location.y = last_node_y
                        
                    last_node_x = AlphaTestGroup.location.x
                    last_node_y = AlphaTestGroup.location.y

                                    ######################
                                    #Additive Group Create
                                    ######################
                # .shader files
                if((Shader_Type == 0 or Shader_Type == 3 or Shader_Type == 4) and ShaderItem.blend_mode_option == 1):
                    AdditiveGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3RCategory: blend_mode - additive")
                    
                    #locations of group
                    AdditiveGroup.location.x = last_node_x - ADDITIVE_GROUP_HORIZONTAL_SPACING
                    AdditiveGroup.location.y = last_node_y
                        
                    last_node_x = AdditiveGroup.location.x
                    last_node_y = AdditiveGroup.location.y


                                    ########################################
                                    #  Blend Mode Group Create Decal Shaders
                                    ########################################
                albedo_blend_group_made = 0
                
                if(Shader_Type == 6): 
                    if (ShaderItem.blend_mode_option == 0): #H3RCategory: blend_mode - opaque
                        # AlphaBlendGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3RCategory: blend_mode - opaque")
                        # #AlbedoGroup = apply_group_values(AlbedoGroup, ShaderItem, "albedo")
                        # ShaderGroupList.append("alpha_blend")
                        # ShaderGroupList.append("alpha_blend") #extra option for an additional texture being needed IN the order they get connected
                        # albedo_blend_group_made = 1
                        log_to_file("Blend mode is Opaque. Not making Node Group.")
                    elif (ShaderItem.blend_mode_option == 1 or ShaderItem.blend_mode_option == 2): #H3RCategory: blend_mode - additive or multiply
                        AlphaBlendGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3RCategory: blend_mode - additive")
                        #AlbedoGroup = apply_group_values(AlbedoGroup, ShaderItem, "albedo")
                        ShaderGroupList.append("alpha_blend")
                        ShaderGroupList.append("alpha_blend") #extra option for an additional texture being needed IN the order they get connected
                        albedo_blend_group_made = 1    
                            
                    elif (ShaderItem.blend_mode_option == 3): #H3RCategory: blend_mode - alpha_blend
                        AlphaBlendGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3RCategory: blend_mode - alpha_blend")
                        #AlbedoGroup = apply_group_values(AlbedoGroup, ShaderItem, "albedo")
                        ShaderGroupList.append("alpha_blend")
                        ShaderGroupList.append("alpha_blend") #extra option for an additional texture being needed IN the order they get connected
                        albedo_blend_group_made = 1
                    
                    if (albedo_blend_group_made == 1):
                        #locations of group
                        AlphaBlendGroup.location.x = last_node_x - ADDITIVE_GROUP_HORIZONTAL_SPACING
                        AlphaBlendGroup.location.y = last_node_y
                            
                        last_node_x = AlphaBlendGroup.location.x
                        last_node_y = AlphaBlendGroup.location.y

                                    #  SHADER OUTPUT FIXING
                                    #############################
                                    #environment map group create
                                    #############################
                ###############
                # .shader files
                ###############
                
                if((Shader_Type == 0 or Shader_Type == 4) and (ShaderItem.environment_mapping_option >= 1 and ShaderItem.environment_mapping_option <= 5)): #H3RCategory: environment_mapping - per_pixel
                    ShaderOutputCount = ShaderOutputCount + 1
                elif((Shader_Type == 0 or Shader_Type == 4) and ShaderItem.environment_mapping_option == 2): #H3RCategory: environment_mapping - dynamic
                    ShaderOutputCount = ShaderOutputCount + 1

                                    ########################
                                    #self illum group create
                                    ########################
                ###############
                # .shader files
                ###############
                
                if((Shader_Type == 0 or Shader_Type == 4) and (ShaderItem.self_illumination_option >= 1 and ShaderItem.self_illumination_option <= 11)): #all of them
                    ShaderOutputCount = ShaderOutputCount + 1
                elif((Shader_Type == 0 or Shader_Type == 4) and ShaderItem.self_illumination_option == 2): #H3RCategory: self_illumination - 3_channel_self_illum
                    ShaderOutputCount = ShaderOutputCount + 1
                elif((Shader_Type == 0 or Shader_Type == 4) and ShaderItem.self_illumination_option == 3): #H3Category: self_illumination - plasma
                    ShaderOutputCount = ShaderOutputCount + 1
                elif((Shader_Type == 0 or Shader_Type == 4) and ShaderItem.self_illumination_option == 4): #H3RCategory: self_illumination - from_diffuse
                    ShaderOutputCount = ShaderOutputCount + 1
                elif((Shader_Type == 0 or Shader_Type == 4) and ShaderItem.self_illumination_option == 5): #H3RCategory: self_illumination - illum_detail
                    ShaderOutputCount = ShaderOutputCount + 1
                elif((Shader_Type == 0 or Shader_Type == 4) and ShaderItem.self_illumination_option == 6): #H3RCategory: self_illumination - meter
                    ShaderOutputCount = ShaderOutputCount + 1
                elif((Shader_Type == 0 or Shader_Type == 4) and ShaderItem.self_illumination_option == 7): #H3RCategory: self_illumination - self_illum_times_diffuse
                    ShaderOutputCount = ShaderOutputCount + 1
                    
                ########################
                # .shader_halogram files
                ########################
                
                if(Shader_Type == 3 and ShaderItem.self_illumination_option == 1): #H3RCategory: self_illumination - simple
                    ShaderOutputCount = ShaderOutputCount + 1
                elif(Shader_Type == 3 and ShaderItem.self_illumination_option == 2): #H3RCategory: self_illumination - 3_channel_self_illum
                    ShaderOutputCount = ShaderOutputCount + 1
                elif(Shader_Type == 3 and ShaderItem.self_illumination_option == 3): #H3Category: self_illumination - plasma
                    ShaderOutputCount = ShaderOutputCount + 1
                elif(Shader_Type == 3 and ShaderItem.self_illumination_option == 4): #H3RCategory: self_illumination - from_diffuse
                    ShaderOutputCount = ShaderOutputCount + 1
                elif(Shader_Type == 3 and ShaderItem.self_illumination_option == 5): #H3RCategory: self_illumination - illum_detail
                    ShaderOutputCount = ShaderOutputCount + 1
                elif(Shader_Type == 3 and ShaderItem.self_illumination_option == 6): #H3RCategory: self_illumination - meter
                    ShaderOutputCount = ShaderOutputCount + 1
                elif(Shader_Type == 3 and ShaderItem.self_illumination_option == 7): #H3RCategory: self_illumination - self_illum_times_diffuse
                    ShaderOutputCount = ShaderOutputCount + 1    
                elif(Shader_Type == 3 and ShaderItem.self_illumination_option == 8): #H3Category: self_illumination - multilayer_additive
                    ShaderOutputCount = ShaderOutputCount + 1  
                elif(Shader_Type == 3 and ShaderItem.self_illumination_option == 9): #H3Category: self_illumination - scope_blur
                    ShaderOutputCount = ShaderOutputCount + 1  
                elif(Shader_Type == 3 and ShaderItem.self_illumination_option == 10): #H3Category: self_illumination - ml_add_four_change_color
                    ShaderOutputCount = ShaderOutputCount + 1  
                elif(Shader_Type == 3 and ShaderItem.self_illumination_option == 11): #H3Category: self_illumination - ml_add_five_change_color
                    ShaderOutputCount = ShaderOutputCount + 1  
                elif(Shader_Type == 3 and ShaderItem.self_illumination_option == 12): #H3Category: self_illumination - plasma_wide_and_sharp_five_change_color
                    ShaderOutputCount = ShaderOutputCount + 1  
                elif(Shader_Type == 3 and ShaderItem.self_illumination_option == 13): #H3Category: self_illumination - self_illum_holograms
                    ShaderOutputCount = ShaderOutputCount + 1  
                    
                                    ############################
                                    #material model group create
                                    ############################
                ###############
                # .shader files
                ###############
                
                if((Shader_Type == 0 or Shader_Type == 2) and ShaderItem.material_model_option == 0): #H3Category: materrial_model - diffuse_only
                    ShaderOutputCount = ShaderOutputCount + 1
                elif((Shader_Type == 0) and ShaderItem.material_model_option == 1): #H3Category: material_model - cook_torrance
                    ShaderOutputCount = ShaderOutputCount + 1
                elif((Shader_Type == 0) and ShaderItem.material_model_option == 2): #H3Category: material_model - two_lobe_phong
                    ShaderOutputCount = ShaderOutputCount + 1
                elif((Shader_Type == 0) and ShaderItem.material_model_option == 3): #H3Category: material_model - foliage                           #Using Diffuse Only FOR NOW FIX LATER
                    ShaderOutputCount = ShaderOutputCount + 1
                elif((Shader_Type == 0) and ShaderItem.material_model_option == 4): #H3Category: material_model - none
                    log_to_file("Mat Model Option: none")
                elif((Shader_Type == 0) and ShaderItem.material_model_option == 5): #H3Category: material_model - glass
                    ShaderOutputCount = ShaderOutputCount + 1
                elif((Shader_Type == 0) and ShaderItem.material_model_option == 6): #H3Category: material_model - organism                          USING COOK_TORRANCE FOR NOW FIX LATER
                    ShaderOutputCount = ShaderOutputCount + 1
                elif((Shader_Type == 0) and ShaderItem.material_model_option == 7): #H3Category: material_model - single_lobe_phong
                    ShaderOutputCount = ShaderOutputCount + 1
                elif((Shader_Type == 0) and ShaderItem.material_model_option == 8): #H3Category: material_model - car_paint
                    ShaderOutputCount = ShaderOutputCount + 1
                elif((Shader_Type == 0) and ShaderItem.material_model_option == 9): #H3Category: material_model - cook_torrance_custom_cube
                    ShaderOutputCount = ShaderOutputCount + 1
                elif((Shader_Type == 0) and ShaderItem.material_model_option == 10): #H3Category: material_model - cook_torrance_pbr_maps
                    ShaderOutputCount = ShaderOutputCount + 1
                elif((Shader_Type == 0) and ShaderItem.material_model_option == 11): #H3Category: material_model - cook_torrance_two_color_spec_tint
                    ShaderOutputCount = ShaderOutputCount + 1
                elif((Shader_Type == 0) and ShaderItem.material_model_option == 12): #H3Category: material_model - two_lobe_phong_tint_map                          USING COOK_TORRANCE FOR NOW FIX LATER
                    ShaderOutputCount = ShaderOutputCount + 1
                elif((Shader_Type == 0) and ShaderItem.material_model_option == 13): #H3Category: material_model - cook_torrance_scrolling_cube_mask
                    ShaderOutputCount = ShaderOutputCount + 1
                elif((Shader_Type == 0) and ShaderItem.material_model_option == 14): #H3Category: material_model - cook_torrance_rim_fresnel
                    ShaderOutputCount = ShaderOutputCount + 1
                elif((Shader_Type == 0) and ShaderItem.material_model_option == 15): #H3Category: material_model - cook_torrance_scrolling_cube
                    ShaderOutputCount = ShaderOutputCount + 1
                elif((Shader_Type == 0) and ShaderItem.material_model_option == 16): #H3Category: material_model - cook_torrance_from_albedo
                    ShaderOutputCount = ShaderOutputCount + 1
                    
                #shader_custom    
                if((Shader_Type == 4) and ShaderItem.material_model_option == 0): #H3Category: materrial_model - diffuse_only
                    ShaderOutputCount = ShaderOutputCount + 1
                elif((Shader_Type == 4) and ShaderItem.material_model_option == 1): #H3Category: material_model - two_lobe_phong
                    ShaderOutputCount = ShaderOutputCount + 1
                elif((Shader_Type == 4) and ShaderItem.material_model_option == 2): #H3Category: material_model - foliage
                    ShaderOutputCount = ShaderOutputCount + 1
                elif((Shader_Type == 4) and ShaderItem.material_model_option == 3): #H3Category: material_model - none                           #Using Diffuse Only FOR NOW FIX LATER
                    log_to_file("Mat Model Option: none")
                elif((Shader_Type == 4) and ShaderItem.material_model_option == 4): #H3Category: material_model - custom_specular
                    ShaderOutputCount = ShaderOutputCount + 1
                
                 

                            ######################################################################################
                            #create Add Shader Node or Shader3Group depending on how many Shader Outputs there are
                            ######################################################################################
                #log_to_file("Count of Shader Outputs: " + str(ShaderOutputCount))
                
                # .shader files
                if((Shader_Type == 0 or Shader_Type == 4 or Shader_Type == 6) and ShaderOutputCount <= 2): #if only less than 1 or 2
                    pymat_copy.node_tree.nodes.new('ShaderNodeAddShader')
                    AddShader = pymat_copy.node_tree.nodes.get("Add Shader")
                elif ((Shader_Type == 0 or Shader_Type == 4 or Shader_Type == 6) and ShaderOutputCount == 3): #if there are 3
                    Add3Group = instantiate_group(pymat_copy.node_tree.nodes, "CR4BUtility: Add 3 Shader")
                else:
                    log_to_file("ShaderOutputCount Issue!")
                    
                    
                # .shader_terrain files
                if(Shader_Type == 1 and ShaderOutputCount <= 2): #if only less than 1 or 2 Shader outputs
                    pymat_copy.node_tree.nodes.new('ShaderNodeAddShader')
                    AddShader = pymat_copy.node_tree.nodes.get("Add Shader")
                # elif (Shader_Type == 1 and ShaderOutputCount == 3): #if there are 3
                    # Add3Group = instantiate_group(pymat_copy.node_tree.nodes, "CR4BUtility: Add 3 Shader")
                # elif (Shader_Type == 1 and ShaderOutputCount == 4): #if there are 4
                    # Add4Group = instantiate_group(pymat_copy.node_tree.nodes, "CR4BUtility: Add 4 Shader")   
                # elif (Shader_Type == 1 and ShaderOutputCount == 5): #if there are 5
                    # Add5Group = instantiate_group(pymat_copy.node_tree.nodes, "CR4BUtility: Add 5 Shader")    

                #foliage shader
                if(ShaderItem == 2):
                    #log_to_file("  making add shader")
                    pymat_copy.node_tree.nodes.new('ShaderNodeAddShader')
                    AddShader = pymat_copy.node_tree.nodes.get("Add Shader")

                #locations of group
                if(ShaderOutputCount <= 2 or Shader_Type == 2):
                    AddShader.location.x = last_node_x - ADD_SHADER_HORIZONTAL_SPACING
                    AddShader.location.y = last_node_y
                        
                    last_node_x = AddShader.location.x
                    last_node_y = AddShader.location.y

                    end_group_x = AddShader.location.x
                    end_group_y = AddShader.location.y        
                elif(ShaderOutputCount == 3):
                    Add3Group.location.x = last_node_x - ADD_SHADER_HORIZONTAL_SPACING
                    Add3Group.location.y = last_node_y
                        
                    last_node_x = Add3Group.location.x
                    last_node_y = Add3Group.location.y 
                    
                    end_group_x = Add3Group.location.x
                    end_group_y = Add3Group.location.y
                    
                                    #############################
                                    #environment map group create
                                    #############################
                ###############
                # .shader files
                ###############
                
                if((Shader_Type == 0 or Shader_Type == 4) and ShaderItem.environment_mapping_option == 1): #H3RCategory: environment_mapping - per_pixel
                    EnvGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3RCategory: environment_mapping - per_pixel")
                    EnvGroup = apply_group_values(EnvGroup, ShaderItem, "env map")
                    #ShaderOutputCount = ShaderOutputCount + 1
                    ShaderGroupList.append("environment")
                    
                    EnvGroup.location.x = last_node_x
                    EnvGroup.location.y = last_node_y - ENVIRONMENT_GROUP_VERTICAL_SPACING
                        
                    last_node_x = EnvGroup.location.x
                    last_node_y = EnvGroup.location.y 
                elif((Shader_Type == 0 or Shader_Type == 4) and ShaderItem.environment_mapping_option == 2): #H3RCategory: environment_mapping - dynamic
                    EnvGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3RCategory: environment_mapping - dynamic")
                    EnvGroup = apply_group_values(EnvGroup, ShaderItem, "env map")
                    #ShaderOutputCount = ShaderOutputCount + 1
                    ShaderGroupList.append("environment")

                    EnvGroup.location.x = last_node_x
                    EnvGroup.location.y = last_node_y - ENVIRONMENT_GROUP_VERTICAL_SPACING
                        
                    last_node_x = EnvGroup.location.x
                    last_node_y = EnvGroup.location.y 
                    # if (Game_Source == "H3" or Game_Source == "H3ODST"):    
                        # EnvGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: environment_mapping - dynamic")
                        # EnvGroup = apply_group_values(EnvGroup, ShaderItem, "env map")
                        # #ShaderOutputCount = ShaderOutputCount + 1
                        # ShaderGroupList.append("environment")

                        # EnvGroup.location.x = last_node_x
                        # EnvGroup.location.y = last_node_y - ENVIRONMENT_GROUP_VERTICAL_SPACING
                            
                        # last_node_x = EnvGroup.location.x
                        # last_node_y = EnvGroup.location.y 
                    # elif (Game_Source == "Reach"):
                        # EnvGroup = instantiate_group(pymat_copy.node_tree.nodes, "HRCategory: environment_mapping - dynamic")
                        # EnvGroup = apply_group_values(EnvGroup, ShaderItem, "env map")
                        # #ShaderOutputCount = ShaderOutputCount + 1
                        # ShaderGroupList.append("environment")

                        # EnvGroup.location.x = last_node_x
                        # EnvGroup.location.y = last_node_y - ENVIRONMENT_GROUP_VERTICAL_SPACING
                            
                        # last_node_x = EnvGroup.location.x
                        # last_node_y = EnvGroup.location.y 

                                    ########################
                                    #self illum group create
                                    ########################
                ###############
                # .shader files
                ###############
                
                if((Shader_Type == 0 or Shader_Type == 3 or Shader_Type == 4) and ShaderItem.self_illumination_option == 1): #H3RCategory: self_illumination - simple
                    SelfIllumGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3RCategory: self_illumination - simple")
                    SelfIllumGroup = apply_group_values(SelfIllumGroup, ShaderItem, "self illum")
                    #ShaderOutputCount = ShaderOutputCount + 1
                    ShaderGroupList.append("self_illum")
                    illum_group_made = 1
                elif((Shader_Type == 0 or Shader_Type == 3 or Shader_Type == 4) and ShaderItem.self_illumination_option == 2): #H3RCategory: self_illumination - 3_channel_self_illum
                    SelfIllumGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3RCategory: self_illumination - 3_channel_self_illum")
                    SelfIllumGroup = apply_group_values(SelfIllumGroup, ShaderItem, "self illum")
                    #ShaderOutputCount = ShaderOutputCount + 1
                    ShaderGroupList.append("self_illum")
                    illum_group_made = 1
                elif((Shader_Type == 0 or Shader_Type == 3 or Shader_Type == 4) and ShaderItem.self_illumination_option == 3): #H3Category: self_illumination - plasma
                    SelfIllumGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: self_illumination - plasma")
                    SelfIllumGroup = apply_group_values(SelfIllumGroup, ShaderItem, "self illum")
                    #ShaderOutputCount = ShaderOutputCount + 1
                    ShaderGroupList.append("self_illum")
                    illum_group_made = 1
                elif((Shader_Type == 0 or Shader_Type == 3 or Shader_Type == 4) and ShaderItem.self_illumination_option == 4): #H3RCategory: self_illumination - from_diffuse
                    SelfIllumGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3RCategory: self_illumination - from_diffuse")
                    SelfIllumGroup = apply_group_values(SelfIllumGroup, ShaderItem, "self illum")
                    #ShaderOutputCount = ShaderOutputCount + 1
                    ShaderGroupList.append("self_illum")
                    illum_group_made = 1
                elif((Shader_Type == 0 or Shader_Type == 3 or Shader_Type == 4) and ShaderItem.self_illumination_option == 5): #H3RCategory: self_illumination - illum_detail
                    SelfIllumGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3RCategory: self_illumination - illum_detail")
                    SelfIllumGroup = apply_group_values(SelfIllumGroup, ShaderItem, "self illum")
                    #ShaderOutputCount = ShaderOutputCount + 1
                    ShaderGroupList.append("self_illum")
                    illum_group_made = 1
                elif((Shader_Type == 0 or Shader_Type == 3 or Shader_Type == 4) and ShaderItem.self_illumination_option == 6): #H3RCategory: self_illumination - meter
                    SelfIllumGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3RCategory: self_illumination - meter")
                    SelfIllumGroup = apply_group_values(SelfIllumGroup, ShaderItem, "self illum")
                    #ShaderOutputCount = ShaderOutputCount + 1
                    ShaderGroupList.append("self_illum")
                    illum_group_made = 1
                elif((Shader_Type == 0 or Shader_Type == 3 or Shader_Type == 4) and ShaderItem.self_illumination_option == 7): #H3RCategory: self_illumination - self_illum_times_diffuse
                    SelfIllumGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3RCategory: self_illumination - self_illum_times_diffuse")
                    SelfIllumGroup = apply_group_values(SelfIllumGroup, ShaderItem, "self illum")
                    #ShaderOutputCount = ShaderOutputCount + 1
                    ShaderGroupList.append("self_illum")
                    illum_group_made = 1
                elif((Shader_Type == 0 or Shader_Type == 3 or Shader_Type == 4) and ShaderItem.self_illumination_option == 11): #H3Category: self_illumination - illum_change_color
                    SelfIllumGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: self_illumination - illum_change_color")
                    SelfIllumGroup = apply_group_values(SelfIllumGroup, ShaderItem, "self illum")
                    #ShaderOutputCount = ShaderOutputCount + 1
                    ShaderGroupList.append("self_illum")
                    illum_group_made = 1

                ########################
                # .shader_halogram files
                ########################
                 
                elif(Shader_Type == 3 and ShaderItem.self_illumination_option == 8): #H3Category: self_illumination - multilayer_additive
                    SelfIllumGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: self_illumination - multilayer_additive")
                    SelfIllumGroup = apply_group_values(SelfIllumGroup, ShaderItem, "self illum")
                    #ShaderOutputCount = ShaderOutputCount + 1
                    ShaderGroupList.append("self_illum")
                    illum_group_made = 1
                elif(Shader_Type == 3 and ShaderItem.self_illumination_option == 9): #H3Category: self_illumination - scope_blur
                    SelfIllumGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: self_illumination - scope_blur")
                    SelfIllumGroup = apply_group_values(SelfIllumGroup, ShaderItem, "self illum")
                    #ShaderOutputCount = ShaderOutputCount + 1
                    ShaderGroupList.append("self_illum")
                    illum_group_made = 1 
                elif(Shader_Type == 3 and ShaderItem.self_illumination_option == 10): #H3Category: self_illumination - ml_add_four_change_color
                    SelfIllumGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: self_illumination - ml_add_four_change_color")
                    SelfIllumGroup = apply_group_values(SelfIllumGroup, ShaderItem, "self illum")
                    #ShaderOutputCount = ShaderOutputCount + 1
                    ShaderGroupList.append("self_illum")
                    illum_group_made = 1   
                elif(Shader_Type == 3 and ShaderItem.self_illumination_option == 11): #H3Category: self_illumination - ml_add_five_change_color
                    SelfIllumGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: self_illumination - ml_add_five_change_color")
                    SelfIllumGroup = apply_group_values(SelfIllumGroup, ShaderItem, "self illum")
                    #ShaderOutputCount = ShaderOutputCount + 1
                    ShaderGroupList.append("self_illum")
                    illum_group_made = 1   
                elif(Shader_Type == 3 and ShaderItem.self_illumination_option == 12): #H3Category: self_illumination - plasma_wide_and_sharp_five_change_color
                    SelfIllumGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: self_illumination - plasma_wide_and_sharp_five_change_color")
                    SelfIllumGroup = apply_group_values(SelfIllumGroup, ShaderItem, "self illum")
                    #ShaderOutputCount = ShaderOutputCount + 1
                    ShaderGroupList.append("self_illum")
                    illum_group_made = 1  
                elif(Shader_Type == 3 and ShaderItem.self_illumination_option == 13): #H3Category: self_illumination - self_illum_holograms
                    SelfIllumGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: self_illumination - self_illum_holograms")
                    SelfIllumGroup = apply_group_values(SelfIllumGroup, ShaderItem, "self illum")
                    #ShaderOutputCount = ShaderOutputCount + 1
                    ShaderGroupList.append("self_illum")
                    illum_group_made = 1 



                #location of node group
                if(illum_group_made == 1):
                    SelfIllumGroup.location.x = last_node_x
                    SelfIllumGroup.location.y = last_node_y - SELF_ILLUM_VERTICAL_SPACING
                        
                    last_node_x = SelfIllumGroup.location.x
                    last_node_y = SelfIllumGroup.location.y         

                                    ############################
                                    #material model group create
                                    ############################
                ###############
                # .shader files
                ###############
                
                if((Shader_Type == 0 or Shader_Type == 2) and ShaderItem.material_model_option == 0): #H3Category: materrial_model - diffuse_only
                    MatModelGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3RCategory: material_model - diffuse_only")
                    MatModelGroup = apply_group_values(MatModelGroup, ShaderItem, "mat model")
                    #ShaderOutputCount = ShaderOutputCount + 1
                    ShaderGroupList.append("material")
                    mat_group_made = 1
                elif((Shader_Type == 0) and ShaderItem.material_model_option == 1): #H3Category: material_model - cook_torrance
                    MatModelGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: material_model - cook_torrance")
                    MatModelGroup = apply_group_values(MatModelGroup, ShaderItem, "mat model")
                    #ShaderOutputCount = ShaderOutputCount + 1
                    ShaderGroupList.append("material")
                    mat_group_made = 1
                elif((Shader_Type == 0) and ShaderItem.material_model_option == 2): #H3Category: material_model - two_lobe_phong
                    MatModelGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: material_model - two_lobe_phong")
                    MatModelGroup = apply_group_values(MatModelGroup, ShaderItem, "mat model")
                    #ShaderOutputCount = ShaderOutputCount + 1
                    ShaderGroupList.append("material")
                    mat_group_made = 1
                elif((Shader_Type == 0) and ShaderItem.material_model_option == 3): #H3Category: material_model - foliage                           #Using Diffuse Only FOR NOW FIX LATER
                    MatModelGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3RCategory: material_model - diffuse_only")
                    MatModelGroup = apply_group_values(MatModelGroup, ShaderItem, "mat model")
                    #ShaderOutputCount = ShaderOutputCount + 1
                    ShaderGroupList.append("material") 
                    mat_group_made = 1
                elif((Shader_Type == 0) and ShaderItem.material_model_option == 4): #H3Category: material_model - none
                    log_to_file("Mat Model Option: none")
                elif((Shader_Type == 0) and ShaderItem.material_model_option == 5): #H3Category: material_model - glass
                    MatModelGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: material_model - glass")
                    MatModelGroup = apply_group_values(MatModelGroup, ShaderItem, "mat model")
                    #ShaderOutputCount = ShaderOutputCount + 1
                    ShaderGroupList.append("material")
                    mat_group_made = 1
                elif((Shader_Type == 0) and ShaderItem.material_model_option == 6): #H3Category: material_model - organism                          USING COOK_TORRANCE FOR NOW FIX LATER
                    MatModelGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: material_model - organism")
                    MatModelGroup = apply_group_values(MatModelGroup, ShaderItem, "mat model")
                    #ShaderOutputCount = ShaderOutputCount + 1
                    ShaderGroupList.append("material")  
                    mat_group_made = 1
                elif((Shader_Type == 0) and ShaderItem.material_model_option == 7): #H3Category: material_model - single_lobe_phong
                    MatModelGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: material_model - single_lobe_phong")
                    MatModelGroup = apply_group_values(MatModelGroup, ShaderItem, "mat model")
                    #ShaderOutputCount = ShaderOutputCount + 1
                    ShaderGroupList.append("material")
                    mat_group_made = 1
                elif((Shader_Type == 0) and ShaderItem.material_model_option == 9): #H3Category: material_model - cook_torrance_custom_cube
                    MatModelGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: material_model - cook_torrance")      #USING COOK_TORRANCE FOR NOW FIX LATER
                    MatModelGroup = apply_group_values(MatModelGroup, ShaderItem, "mat model")
                    #ShaderOutputCount = ShaderOutputCount + 1
                    ShaderGroupList.append("material")
                    mat_group_made = 1
                elif((Shader_Type == 0) and ShaderItem.material_model_option == 10): #H3Category: material_model - single_lobe_phong
                    MatModelGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: material_model - cook_torrance_pbr_maps")
                    MatModelGroup = apply_group_values(MatModelGroup, ShaderItem, "mat model")
                    #ShaderOutputCount = ShaderOutputCount + 1
                    ShaderGroupList.append("material")
                    mat_group_made = 1
                
                #shader_custom                
                if((Shader_Type == 4) and ShaderItem.material_model_option == 0): #H3Category: materrial_model - diffuse_only
                    MatModelGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3RCategory: material_model - diffuse_only")
                    MatModelGroup = apply_group_values(MatModelGroup, ShaderItem, "mat model")
                    #ShaderOutputCount = ShaderOutputCount + 1
                    ShaderGroupList.append("material")
                    mat_group_made = 1
                elif((Shader_Type == 4) and ShaderItem.material_model_option == 1): #H3Category: material_model - two_lobe_phong
                    MatModelGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: material_model - two_lobe_phong")
                    MatModelGroup = apply_group_values(MatModelGroup, ShaderItem, "mat model")
                    #ShaderOutputCount = ShaderOutputCount + 1
                    ShaderGroupList.append("material")
                    mat_group_made = 1
                elif((Shader_Type == 4) and ShaderItem.material_model_option == 2): #H3Category: material_model - foliage
                    MatModelGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: material_model - diffuse_only")
                    MatModelGroup = apply_group_values(MatModelGroup, ShaderItem, "mat model")
                    #ShaderOutputCount = ShaderOutputCount + 1
                    ShaderGroupList.append("material")
                    mat_group_made = 1
                elif((Shader_Type == 4) and ShaderItem.material_model_option == 3): #H3Category: material_model - none                           #Using Diffuse Only FOR NOW FIX LATER
                    log_to_file("Mat Model Option: none")
                elif((Shader_Type == 4) and ShaderItem.material_model_option == 4): #H3Category: material_model - custom_specular
                    MatModelGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: material_model - custom_specular")
                    MatModelGroup = apply_group_values(MatModelGroup, ShaderItem, "mat model")
                    #ShaderOutputCount = ShaderOutputCount + 1
                    ShaderGroupList.append("material")
                    mat_group_made = 1
                    
                
                #location of node group
                if(mat_group_made == 1):
                    MatModelGroup.location.x = end_group_x - 300
                    MatModelGroup.location.y = end_group_y
                        
                    mat_group_x = MatModelGroup.location.x
                    mat_group_y = MatModelGroup.location.y         

                    last_node_x = MatModelGroup.location.x
                    last_node_y = MatModelGroup.location.y 

            #create variable for each category maybe to correct any misassignment?
                                    ####################
                                    #Albedo group create
                                    ####################
                ##############
                # .shader file
                ##############
                
                if((Shader_Type == 0 or Shader_Type == 3 or Shader_Type == 2 or Shader_Type == 4) and ShaderItem.albedo_option == 0): #H3RCategory: albedo - default 
                    AlbedoGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3RCategory: albedo - default")
                    AlbedoGroup = apply_group_values(AlbedoGroup, ShaderItem, "albedo")
                    ShaderGroupList.append("albedo")
                    ShaderGroupList.append("albedo") #extra option for an additional texture being needed IN the order they get connected
                    albedo_group_made = 1
                elif((Shader_Type == 0 or Shader_Type == 3 or Shader_Type == 4) and ShaderItem.albedo_option == 1): #H3Category: albedo - detail_blend
                    AlbedoGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: albedo - detail_blend")
                    AlbedoGroup = apply_group_values(AlbedoGroup, ShaderItem, "albedo")
                    ShaderGroupList.append("albedo")
                    ShaderGroupList.append("albedo")
                    albedo_group_made = 1
                elif((Shader_Type == 0 or Shader_Type == 3 or Shader_Type == 4) and ShaderItem.albedo_option == 2): #H3RCategory: albedo - constant_color
                    AlbedoGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3RCategory: albedo - constant_color")
                    AlbedoGroup = apply_group_values(AlbedoGroup, ShaderItem, "albedo")
                    ShaderGroupList.append("albedo")
                    albedo_group_made = 1        
                elif((Shader_Type == 0 or Shader_Type == 3 or Shader_Type == 4) and ShaderItem.albedo_option == 3): #H3RCategory: albedo - two_change_color
                    AlbedoGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3RCategory: albedo - two_change_color")
                    AlbedoGroup = apply_group_values(AlbedoGroup, ShaderItem, "albedo")
                    ShaderGroupList.append("albedo")
                    ShaderGroupList.append("albedo")
                    albedo_group_made = 1
                elif((Shader_Type == 0 or Shader_Type == 3 or Shader_Type == 4) and ShaderItem.albedo_option == 4): #H3RCategory: albedo - four_change_color
                    AlbedoGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3RCategory: albedo - four_change_color")
                    AlbedoGroup = apply_group_values(AlbedoGroup, ShaderItem, "albedo")
                    ShaderGroupList.append("albedo")
                    ShaderGroupList.append("albedo")
                    albedo_group_made = 1
                elif((Shader_Type == 0 or Shader_Type == 3 or Shader_Type == 4) and ShaderItem.albedo_option == 5): #H3RCategory: albedo - three_detail_blend
                    AlbedoGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3RCategory: albedo - three_detail_blend")
                    AlbedoGroup = apply_group_values(AlbedoGroup, ShaderItem, "albedo")
                    ShaderGroupList.append("albedo")
                    ShaderGroupList.append("albedo")
                    albedo_group_made = 1
                elif((Shader_Type == 0 or Shader_Type == 3 or Shader_Type == 4) and ShaderItem.albedo_option == 6): #H3RCategory: albedo - two_detail_overlay
                    AlbedoGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3RCategory: albedo - two_detail_overlay")
                    AlbedoGroup = apply_group_values(AlbedoGroup, ShaderItem, "albedo")
                    ShaderGroupList.append("albedo")
                    ShaderGroupList.append("albedo")
                    albedo_group_made = 1
                elif((Shader_Type == 0 or Shader_Type == 3 or Shader_Type == 4) and ShaderItem.albedo_option == 7): #H3RCategory: albedo - two_detail
                    AlbedoGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3RCategory: albedo - two_detail")
                    AlbedoGroup = apply_group_values(AlbedoGroup, ShaderItem, "albedo")
                    ShaderGroupList.append("albedo")
                    ShaderGroupList.append("albedo")
                    albedo_group_made = 1
                elif((Shader_Type == 0 or Shader_Type == 3 or Shader_Type == 4) and ShaderItem.albedo_option == 8): #H3RCategory: albedo - color_mask
                    AlbedoGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3RCategory: albedo - color_mask")
                    AlbedoGroup = apply_group_values(AlbedoGroup, ShaderItem, "albedo")
                    ShaderGroupList.append("albedo")
                    ShaderGroupList.append("albedo")
                    albedo_group_made = 1
                elif((Shader_Type == 0 or Shader_Type == 3 or Shader_Type == 4) and ShaderItem.albedo_option == 9): #H3RCategory: albedo - two_detail_black_point
                    AlbedoGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3RCategory: albedo - two_detail_black_point")
                    AlbedoGroup = apply_group_values(AlbedoGroup, ShaderItem, "albedo")
                    ShaderGroupList.append("albedo")
                    ShaderGroupList.append("albedo")
                    ShaderGroupList.append("albedo")
                    albedo_group_made = 1
                elif((Shader_Type == 4) and ShaderItem.albedo_option == 10): #H3RCategory_Custom: albedo - waterfall
                    AlbedoGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3RCategory_Custom: albedo - waterfall")
                    AlbedoGroup = apply_group_values(AlbedoGroup, ShaderItem, "albedo")
                    ShaderGroupList.append("albedo")
                    ShaderGroupList.append("albedo")
                    ShaderGroupList.append("albedo")
                    ShaderGroupList.append("albedo")
                    albedo_group_made = 1
                elif(Shader_Type == 0 and ShaderItem.albedo_option == 17): #H3Category: albedo - custom_cube
                    AlbedoGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: albedo - custom_cube")
                    AlbedoGroup = apply_group_values(AlbedoGroup, ShaderItem, "albedo")
                    ShaderGroupList.append("albedo")
                    albedo_group_made = 1
                elif(Shader_Type == 0 and ShaderItem.albedo_option == 18): #H3Category: albedo - two_color
                    AlbedoGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: albedo - two_color")
                    AlbedoGroup = apply_group_values(AlbedoGroup, ShaderItem, "albedo")
                    ShaderGroupList.append("albedo")
                    albedo_group_made = 1
                elif(Shader_Type == 0 and ShaderItem.albedo_option == 22): #H3Category: albedo - texture_from_misc
                    AlbedoGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: albedo - texture_from_misc")
                    AlbedoGroup = apply_group_values(AlbedoGroup, ShaderItem, "albedo")
                    ShaderGroupList.append("albedo")
                    albedo_group_made = 1

                
                albedo_vector_group_made = 0

                                    ####################################
                                    #  Albedo Group Create Decal Shaders
                                    ####################################
                if(Shader_Type == 6):
                    if (ShaderItem.albedo_option == 0): #H3RCategory_Decal: albedo - diffuse_only
                        AlbedoGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3RCategory_Decal: albedo - diffuse_only")
                        AlbedoGroup = apply_group_values(AlbedoGroup, ShaderItem, "albedo")
                        ShaderGroupList.append("albedo")
                        ShaderGroupList.append("albedo") #extra option for an additional texture being needed IN the order they get connected
                        albedo_group_made = 1
                    elif (ShaderItem.albedo_option == 1): #H3RCategory_Decal: albedo - palletized
                        AlbedoVectorGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3RCategory_Decal: albedo - palletized vector")
                        #AlbedoGroup = apply_group_values(AlbedoGroup, ShaderItem, "albedo")
                        ShaderGroupList.append("albedo")
                        ShaderGroupList.append("albedo") #extra option for an additional texture being needed IN the order they get connected
                        AlbedoGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3RCategory_Decal: albedo - palletized")
                        #AlbedoGroup = apply_group_values(AlbedoGroup, ShaderItem, "albedo")
                        ShaderGroupList.append("albedo")
                        ShaderGroupList.append("albedo")
                        albedo_group_made = 1    
                        albedo_vector_group_made = 1
                    elif (ShaderItem.albedo_option == 2): #H3RCategory_Decal: albedo - palletized_plus_alpha
                        AlbedoGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3RCategory_Decal: albedo - palletized_plus_alpha vector")
                        #AlbedoGroup = apply_group_values(AlbedoGroup, ShaderItem, "albedo")
                        ShaderGroupList.append("albedo")
                        ShaderGroupList.append("albedo") #extra option for an additional texture being needed IN the order they get connected
                        AlbedoGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3RCategory_Decal: albedo - palletized_plus_alpha")
                        #AlbedoGroup = apply_group_values(AlbedoGroup, ShaderItem, "albedo")
                        ShaderGroupList.append("albedo")
                        ShaderGroupList.append("albedo") 
                        albedo_group_made = 1    
                        albedo_vector_group_made = 1
                    else:
                        print("ALBEDO GROUP NOT SETUP TO BE MADE YET FOR THIS ALEBDO OPTION FOR DECALS")
                           
                


                #location of node group
                if(albedo_group_made == 1):
                    AlbedoGroup.location.x = last_node_x - 350
                    AlbedoGroup.location.y = last_node_y
                        
                    alb_group_x = AlbedoGroup.location.x
                    alb_group_y = AlbedoGroup.location.y    

                #location of node group
                if(albedo_vector_group_made == 1):
                    AlbedoVectorGroup.location.x = last_node_x - 350
                    AlbedoVectorGroup.location.y = last_node_y
                        
                    alb_group_x = AlbedoVectorGroup.location.x
                    alb_group_y = AlbedoVectorGroup.location.y

                                    ######################
                                    #bump map group create
                                    ######################
                ###############
                # .shader files
                ###############
                
                if((Shader_Type == 0 or Shader_Type == 4) and ShaderItem.bump_mapping_option == 1): #H3RCategory: bump_mapping - standard
                    BumpGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3RCategory: bump_mapping - standard")
                    BumpGroup = apply_group_values(BumpGroup, ShaderItem, "bump")
                    ShaderGroupList.append("bump")
                    bump_group_made = 1
                elif((Shader_Type == 0 or Shader_Type == 4) and ShaderItem.bump_mapping_option == 2): #H3Category: bump_mapping - detail
                    BumpGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: bump_mapping - detail")
                    BumpGroup = apply_group_values(BumpGroup, ShaderItem, "bump")
                    ShaderGroupList.append("bump")
                    ShaderGroupList.append("bump")
                    bump_group_made = 1
                elif((Shader_Type == 0 or Shader_Type == 4) and ShaderItem.bump_mapping_option == 3): #H3Category: bump_mapping - detail_masked
                    BumpGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: bump_mapping - detail_masked")
                    BumpGroup = apply_group_values(BumpGroup, ShaderItem, "bump")
                    ShaderGroupList.append("bump")
                    ShaderGroupList.append("bump")
                    bump_group_made = 1
                elif((Shader_Type == 0 or Shader_Type == 4) and ShaderItem.bump_mapping_option == 4): #H3Category: bump_mapping - detail_plus_detail_masked
                    BumpGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: bump_mapping - detail_plus_detail_masked")
                    BumpGroup = apply_group_values(BumpGroup, ShaderItem, "bump")
                    ShaderGroupList.append("bump")
                    ShaderGroupList.append("bump")
                    bump_group_made = 1
                elif((Shader_Type == 0 or Shader_Type == 4) and ShaderItem.bump_mapping_option == 5): #H3Category: bump_mapping - detail_unorm
                    BumpGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3Category: bump_mapping - detail")
                    BumpGroup = apply_group_values(BumpGroup, ShaderItem, "bump")
                    ShaderGroupList.append("bump")
                    ShaderGroupList.append("bump")
                    bump_group_made = 1
                   
                
                #location of node group    
                if(bump_group_made == 1):
                    BumpGroup.location.x = alb_group_x
                    BumpGroup.location.y = alb_group_y - 400
                        
                    bump_group_x = BumpGroup.location.x
                    bump_group_y = BumpGroup.location.y        
                    
                    last_node_x = BumpGroup.location.x
                    last_node_y = BumpGroup.location.y        

                    
                    
                                    #######################################
                                    #Environment_map Reflector group create
                                    #######################################
                #reset value
                env_reflect_group_made = 0
                
                if((Shader_Type == 0 or Shader_Type == 4) and ShaderItem.environment_mapping_option == 1): #CR4BUtility: environment_map Reflector
                    EnvReflGroup = instantiate_group(pymat_copy.node_tree.nodes, "CR4BUtility: environment_map Reflector")
                    env_reflect_group_made = 1
                
                #location of node group    
                if(env_reflect_group_made == 1):
                    EnvReflGroup.location.x = alb_group_x
                    EnvReflGroup.location.y = alb_group_y - 600
                        
                    bump_group_x = EnvReflGroup.location.x
                    bump_group_y = EnvReflGroup.location.y        
                    
                    last_node_x = EnvReflGroup.location.x
                    last_node_y = EnvReflGroup.location.y    
                    

                
                # #CREATE ALPHATEXTURE
                # if(Shader_Type == 0 and ShaderItem.alpha_test_option == 1 or ShaderItem.specular_mask_option == 2)):
                    # try:
                        # AlphaTexture = pymat_copy.node_tree.nodes.new('ShaderNodeTexImage')
                        # AlphaTexture.image = bpy.data.images.load(Export_Root + '/' + ShaderItem.alpha_bitmap_dir + IMAGE_EXTENSION)
                    # except: 
                        # log_to_file(ShaderItem.bitmap_list[bitm].type + " texture not found")
                            
                        # #default texture for it
                        # #log_to_file(directory + '/' + DEFAULT_BITMAP_DIR + "gray_50_percent" + IMAGE_EXTENSION)


                                        #################################
                                        #TERRAIN ENVIRONMENT GROUP CREATE
                                        #################################
                if(Shader_Type == 1 and ShaderItem.environment_mapping_option != 0):
                    if(ShaderItem.environment_mapping_option == 1): #per pixel
                        TerrainEnvGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3RCategory: environment_mapping - per_pixel")
                        TerrainEnvGroup = apply_group_values(TerrainEnvGroup, ShaderItem, "env map")
                    if(ShaderItem.environment_mapping_option == 2): #dynamic
                        TerrainEnvGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3RCategory: environment_mapping - dynamic")
                        TerrainEnvGroup = apply_group_values(TerrainEnvGroup, ShaderItem, "env map")
                    
                    TerrainEnvGroup.location.x = end_group_x
                    TerrainEnvGroup.location.y = end_group_y - 300        
                    
                    
             
                                    ############################
                                    #TERRAIN SHADER GROUP CREATE
                                    ############################
                #################                    
                # .shader_terrain
                #################
                
                if(Shader_Type == 1):
                    TerrainGroup = instantiate_group(pymat_copy.node_tree.nodes, "H3RCategory: Master Terrain Material")
                    TerrainGroup = apply_group_values(TerrainGroup, ShaderItem, "terrain")
                    
                    #location of node groups
                    TerrainGroup.location.x = end_group_x - 300
                    TerrainGroup.location.y = end_group_y  

                    last_node_x = TerrainGroup.location.x
                    last_node_y = TerrainGroup.location.y
                    
                    # if(ShaderItem.material_0_option != 2): #if option for m_0 is not off
                        # if(ShaderItem.material_0_option == 0): #if = diffuse_only 
                            # TerrainGroupM0 = instantiate_group(pymat_copy.node_tree.nodes, "Halo3TerrainCategory - material - diffuse_only")
                            # TerrainGroupM0 = apply_group_values(TerrainGroupM0, ShaderItem, "terrain1_m0")
                            # #log_to_file("making diffuse only for m0")
                        # if(ShaderItem.material_0_option == 1): #if = diffuse_plus_specular 
                            # TerrainGroupM0 = instantiate_group(pymat_copy.node_tree.nodes, "Halo3TerrainCategory - material - diffuse_plus_specular")
                            # TerrainGroupM0 = apply_group_values(TerrainGroupM0, ShaderItem, "terrain2_m0")
                            # #log_to_file("making diffuse spec for m0")
                        # ShaderOutputCount = ShaderOutputCount + 1
                        # ShaderGroupList.append("m_0")
                        # ShaderGroupList.append("m_0")
                        # ShaderGroupList.append("m_0")
                        # ShaderGroupList.append("m_0")
                    
                    # if(ShaderItem.material_1_option != 2): #if option for m_1 is not off
                        # if(ShaderItem.material_1_option == 0): #if = diffuse_only 
                            # TerrainGroupM1 = instantiate_group(pymat_copy.node_tree.nodes, "Halo3TerrainCategory - material - diffuse_only")
                            # TerrainGroupM1 = apply_group_values(TerrainGroupM1, ShaderItem, "terrain1_m1")
                            # #log_to_file("making diffuse only for m1")
                        # if(ShaderItem.material_1_option == 1): #if = diffuse_plus_specular 
                            # TerrainGroupM1 = instantiate_group(pymat_copy.node_tree.nodes, "Halo3TerrainCategory - material - diffuse_plus_specular") 
                            # TerrainGroupM1 = apply_group_values(TerrainGroupM1, ShaderItem, "terrain2_m1")
                            # #log_to_file("making diffuse spec for m1")
                        # ShaderOutputCount = ShaderOutputCount + 1
                        # ShaderGroupList.append("m_1")
                        # ShaderGroupList.append("m_1")
                        # ShaderGroupList.append("m_1")
                        # ShaderGroupList.append("m_1")                
                
                    # if(ShaderItem.material_2_option != 2): #if option for m_2 is not off
                        # if(ShaderItem.material_2_option == 0): #if = diffuse_only 
                            # TerrainGroupM2 = instantiate_group(pymat_copy.node_tree.nodes, "Halo3TerrainCategory - material - diffuse_only")
                            # TerrainGroupM2 = apply_group_values(TerrainGroupM2, ShaderItem, "terrain1_m2")
                            # #log_to_file("making diffuse only for m2")
                        # if(ShaderItem.material_2_option == 1): #if = diffuse_plus_specular 
                            # TerrainGroupM2 = instantiate_group(pymat_copy.node_tree.nodes, "Halo3TerrainCategory - material - diffuse_plus_specular")     
                            # TerrainGroupM2 = apply_group_values(TerrainGroupM2, ShaderItem, "terrain2_m2")
                            # #log_to_file("making diffuse spec for m2")
                        # ShaderOutputCount = ShaderOutputCount + 1
                        # ShaderGroupList.append("m_2")
                        # ShaderGroupList.append("m_2")
                        # ShaderGroupList.append("m_2")
                        # ShaderGroupList.append("m_2")
                        
                    # if(ShaderItem.material_3_option != 0): #if option for m_3 is not off
                        # if(ShaderItem.material_3_option == 1): #if = diffuse_only 
                            # TerrainGroupM3 = instantiate_group(pymat_copy.node_tree.nodes, "Halo3TerrainCategory - material - diffuse_only")
                            # TerrainGroupM3 = apply_group_values(TerrainGroupM3, ShaderItem, "terrain1_m3")
                            # #log_to_file("making diffuse only for m3")
                        # if(ShaderItem.material_3_option == 2): #if = diffuse_plus_specular 
                            # TerrainGroupM3 = instantiate_group(pymat_copy.node_tree.nodes, "Halo3TerrainCategory - material - diffuse_plus_specular")   
                            # TerrainGroupM3 = apply_group_values(TerrainGroupM3, ShaderItem, "terrain2_m3")  
                            # #log_to_file("making diffuse spec for m3")                
                        # ShaderOutputCount = ShaderOutputCount + 1
                        # ShaderGroupList.append("m_3")
                        # ShaderGroupList.append("m_3")
                        # ShaderGroupList.append("m_3")
                        # ShaderGroupList.append("m_3")    
                
                                                            





                           
                                   
                                   
                                                   ##################
                                                   #GROUP CONNECTIONS
                                                   ##################
                ###############
                # .shader files
                ###############
                
                #CONNECT "ALBEDO GROUP" TO "MATERIAL MODEL" GROUP
                if((Shader_Type == 0 or Shader_Type == 4) and ShaderItem.material_model_option != 0 and ShaderItem.material_model_option != 4 and ShaderItem.material_model_option != 3 and ShaderItem.material_model_option != 6): #every option but "diffuse_only"
                    pymat_copy.node_tree.links.new(MatModelGroup.inputs["albedo.rgb"], AlbedoGroup.outputs["albedo.rgb"])
                    pymat_copy.node_tree.links.new(MatModelGroup.inputs["albedo.a"], AlbedoGroup.outputs["albedo.a"])
                
                
                
                if((Shader_Type == 0 or Shader_Type == 4) and (ShaderItem.material_model_option == 0 or ShaderItem.material_model_option == 3 or ShaderItem.material_model_option == 6)): #if material model is diffuse only
                    pymat_copy.node_tree.links.new(MatModelGroup.inputs["albedo.rgb"], AlbedoGroup.outputs["albedo.rgb"])
             
                if(Shader_Type == 2): #if foliage shader
                    pymat_copy.node_tree.links.new(MatModelGroup.inputs["albedo.rgb"], AlbedoGroup.outputs["albedo.rgb"])

             
                #CONNECT "ALBEDO" GROUP TO "SELF ILLUM" GROUP
                if ((Shader_Type == 0 or Shader_Type == 4) and (ShaderItem.self_illumination_option == 7 or ShaderItem.self_illumination_option == 4)):
                    pymat_copy.node_tree.links.new(SelfIllumGroup.inputs["albedo.rgb"], AlbedoGroup.outputs["albedo.rgb"])
                
                # #CONNECT ALPHA TEXTURE TO ALPHA TEST GROUP
                # if(Shader_Type == 0 and ShaderItem.alpha_test_option == 1 or ShaderItem.specular_mask_option == 2)):
                    # pymat_copy.node_tree.links.new(AlphaTestGroup.inputs["alpha_test_map.a"], AlphaTexture.outputs["Alpha"])
                
                
                #CONNECT "BUMP GROUP" TO "MATERIAL MODEL" GROUP
                if((Shader_Type == 0 or Shader_Type == 4) and ShaderItem.bump_mapping_option != 0): #as long as bump mapping isn't turned off
                    pymat_copy.node_tree.links.new(MatModelGroup.inputs["Normal"], BumpGroup.outputs["Normal"])
                
                log_to_file(str(Shader_Type) + " " + str(ShaderItem.bump_mapping_option) + " " + str(ShaderItem.environment_mapping_option))
                #CONNECT "BUMP GROUP" TO "ENVIRONMENT MODEL" GROUP
                if((Shader_Type == 0 or Shader_Type == 4) and ShaderItem.bump_mapping_option != 0 and (ShaderItem.environment_mapping_option == 1 or ShaderItem.environment_mapping_option == 2)): #when Environment Mapping Option is "dynamic"
                    pymat_copy.node_tree.links.new(EnvGroup.inputs["Normal"], BumpGroup.outputs["Normal"])
                    
                #CONNECT "BUMP GROUP" TO "ENVIRONMENT REFLECTION MODEL" GROUP
                if((Shader_Type == 0 or Shader_Type == 4) and ShaderItem.bump_mapping_option != 0 and (ShaderItem.environment_mapping_option == 1)): #when Environment Mapping Option is "dynamic"
                    pymat_copy.node_tree.links.new(EnvReflGroup.inputs["Normal"], BumpGroup.outputs["Normal"])    
                    
                    
                    
                #CONNECT "MATERIAL MODEL" TO "ENVIRONMENT MAP" GROUP
                if((Shader_Type == 0 or Shader_Type == 4) and ShaderItem.environment_mapping_option != 0 and ShaderItem.material_model_option != 4): #as long as environment option is not none or diffuse only
                    pymat_copy.node_tree.links.new(EnvGroup.inputs["specular_reflectance_and_roughness.rgb"], MatModelGroup.outputs["specular_reflectance_and_roughness.rgb"])
                    if(ShaderItem.environment_mapping_option == 2 and (ShaderItem.material_model_option == 0 or ShaderItem.material_model_option == 1 or ShaderItem.material_model_option == 2 or ShaderItem.material_model_option == 5 or ShaderItem.material_model_option == 7 or ShaderItem.material_model_option == 9 or ShaderItem.material_model_option == 10)): #if environment option is dynamic
                        pymat_copy.node_tree.links.new(EnvGroup.inputs["specular_reflectance_and_roughness.a"], MatModelGroup.outputs["specular_reflectance_and_roughness.a"])
                
                #CONNECT "MATERIAL MODEL" TO "ENVIRONMENT REFLECTOR MAP" GROUP
                if((Shader_Type == 0 or Shader_Type == 4) and ShaderItem.environment_mapping_option == 1 and ShaderItem.material_model_option != 4 and ShaderItem.material_model_option != 0): #as long as environment option is not none or diffuse only
                    pymat_copy.node_tree.links.new(EnvReflGroup.inputs["specular_reflectance_and_roughness.a"], MatModelGroup.outputs["specular_reflectance_and_roughness.a"])
                    if(ShaderItem.environment_mapping_option == 2 and (ShaderItem.material_model_option == 1 or ShaderItem.material_model_option == 2 or ShaderItem.material_model_option == 5 or ShaderItem.material_model_option == 7 or ShaderItem.material_model_option == 9 or ShaderItem.material_model_option == 10)): #if environment option is dynamic
                        pymat_copy.node_tree.links.new(EnvGroup.inputs["specular_reflectance_and_roughness.a"], MatModelGroup.outputs["specular_reflectance_and_roughness.a"])

                
                #  DECAL SHADER GROUP CONNECTIONS
                
                # Connect Albedo Vector group to main albedo_group
                if((Shader_Type == 6) and ShaderItem.blend_mode_option == 0): #albedo option: diffuse only  blend_mode: opaque
                    #connect the Albedo Group directly to the AddShader
                    pymat_copy.node_tree.links.new(AddShader.inputs["Shader"], AlbedoGroup.outputs["Shader"])
                    
                
                
                # DECAL SHADER CONNECT BLEND MODE IF NEEDED
                if (Shader_Type == 6):
                    if(ShaderItem.blend_mode_option == 1): #additive
                        pymat_copy.node_tree.links.new(AlphaBlendGroup.inputs["Shader"], AlbedoGroup.outputs["Shader"])
                    
                        pymat_copy.node_tree.links.new(AddShader.inputs["Shader"], AlphaBlendGroup.outputs["Shader"])
                    
                    elif(ShaderItem.blend_mode_option == 3): #alpha_blend
                        print("trying to link AlebdoGroup to AlphaBlendGroup")
                        pymat_copy.node_tree.links.new(AlphaBlendGroup.inputs["Shader"], AlbedoGroup.outputs["Shader"])
                        pymat_copy.node_tree.links.new(AlphaBlendGroup.inputs["base_map.a"], AlbedoGroup.outputs["alpha"])
                        
                        #connect blend_mode to add shader if it exists
                        pymat_copy.node_tree.links.new(AddShader.inputs["Shader"], AlphaBlendGroup.outputs["Shader"])
                
                
                
                
                #CONNECT END SHADER GROUPS TO "ADD SHADER" NODE
                    #material model group
                #rint("mat option: " + str(ShaderItem.material_model_option))
                if ((Shader_Type == 0 or Shader_Type == 4) and (ShaderItem.material_model_option == 0 or ShaderItem.material_model_option == 1 or ShaderItem.material_model_option == 2 or ShaderItem.material_model_option == 3 or ShaderItem.material_model_option == 5 or ShaderItem.material_model_option == 6 or ShaderItem.material_model_option == 7 or ShaderItem.material_model_option == 9 or ShaderItem.material_model_option == 10)):
                    #log_to_file("0")
                    #log_to_file("shaders needed: " + str(ShaderOutputCount))
                    if(ShaderOutputCount <= 2): #if only less than 1 or 2 Shader outputs needed
                        #log_to_file("fart")
                        if (ShadersConnected == 0):
                            #log_to_file("test a")
                            pymat_copy.node_tree.links.new(AddShader.inputs[0], MatModelGroup.outputs["Shader"])
                            ShadersConnected = ShadersConnected + 1
                        elif (ShadersConnected == 1):
                            #log_to_file("test b")
                            pymat_copy.node_tree.links.new(AddShader.inputs[1], MatModelGroup.outputs["Shader"])
                            ShadersConnected = ShadersConnected + 1                
                    elif(ShaderOutputCount == 3): #3 Shader outputs needed
                        if (ShadersConnected == 0):                
                            #log_to_file("test c")
                            pymat_copy.node_tree.links.new(Add3Group.inputs[0], MatModelGroup.outputs["Shader"])
                            ShadersConnected = ShadersConnected + 1
                        elif (ShadersConnected == 1): 
                            #log_to_file("test d")
                            pymat_copy.node_tree.links.new(Add3Group.inputs[1], MatModelGroup.outputs["Shader"])
                            ShadersConnected = ShadersConnected + 1            
                        elif (ShadersConnected == 2):
                            #log_to_file("test e")
                            pymat_copy.node_tree.links.new(Add3Group.inputs[2], MatModelGroup.outputs["Shader"])
                            ShadersConnected = ShadersConnected + 1 
                elif ((Shader_Type == 0 or Shader_Type == 4) and ShaderItem.material_model_option == 4): #if mat model set to "none" - plug albedo group into Add Shader
                    if(ShaderOutputCount <= 2): #if only less than 1 or 2 Shader outputs needed
                        if (ShadersConnected == 0):
                            #log_to_file("test f")
                        
                            pymat_copy.node_tree.links.new(AddShader.inputs[0], AlbedoGroup.outputs["albedo.rgb"])
                            ShadersConnected = ShadersConnected + 1
                        elif (ShadersConnected == 1):
                            #log_to_file("test g")
                            pymat_copy.node_tree.links.new(AddShader.inputs[1], AlbedoGroup.outputs["albedo.rgb"])
                            ShadersConnected = ShadersConnected + 1                
                    elif(ShaderOutputCount == 3): #3 Shader outputs needed
                        if (ShadersConnected == 0):                
                            #log_to_file("test h")
                            pymat_copy.node_tree.links.new(Add3Group.inputs[0], AlbedoGroup.outputs["albedo.rgb"])
                            ShadersConnected = ShadersConnected + 1
                        elif (ShadersConnected == 1): 
                            #log_to_file("test pymat_copy")
                            pymat_copy.node_tree.links.new(Add3Group.inputs[1], AlbedoGroup.outputs["albedo.rgb"])
                            ShadersConnected = ShadersConnected + 1            
                        elif (ShadersConnected == 2):
                            #log_to_file("test j")
                            pymat_copy.node_tree.links.new(Add3Group.inputs[2], AlbedoGroup.outputs["albedo.rgb"])
                            ShadersConnected = ShadersConnected + 1
                # #foliage shaders
                # elif(Shader_Type == 2):
                    # pymat_copy.node_tree.links.new(AddShader.inputs[0], AlbedoGroup.outputs["albedo.rgb"])
                    # ShadersConnected = ShadersConnected + 1        
                log_to_file("Shader Outputs Connected: " + str(ShadersConnected))
                    #evnironment map group
                if ((Shader_Type == 0 or Shader_Type == 4) and (ShaderItem.environment_mapping_option == 1 or ShaderItem.environment_mapping_option == 2)):
                    if(ShaderOutputCount <= 2): #if only less than 1 or 2 Shader outputs needed
                        if (ShadersConnected == 0):
                            log_to_file(str(Shader_Type))
                            log_to_file("test k")
                            pymat_copy.node_tree.links.new(AddShader.inputs[0], EnvGroup.outputs["Shader"])
                            ShadersConnected = ShadersConnected + 1
                        elif (ShadersConnected == 1):
                            #log_to_file("test l")
                            pymat_copy.node_tree.links.new(AddShader.inputs[1], EnvGroup.outputs["Shader"])
                            ShadersConnected = ShadersConnected + 1                
                    elif(ShaderOutputCount == 3): #3 Shader outputs needed
                        if (ShadersConnected == 0):                
                            #log_to_file("test m")
                            pymat_copy.node_tree.links.new(Add3Group.inputs[0], EnvGroup.outputs["Shader"])
                            ShadersConnected = ShadersConnected + 1
                        elif (ShadersConnected == 1): 
                            #log_to_file("test n")
                            pymat_copy.node_tree.links.new(Add3Group.inputs[1], EnvGroup.outputs["Shader"])
                            ShadersConnected = ShadersConnected + 1            
                        elif (ShadersConnected == 2):
                            #log_to_file("test o")
                            pymat_copy.node_tree.links.new(Add3Group.inputs[2], EnvGroup.outputs["Shader"])
                            ShadersConnected = ShadersConnected + 1
                log_to_file("Shader Outputs Connected: " + str(ShadersConnected))                
                if ((Shader_Type == 0 or Shader_Type == 4) and (ShaderItem.self_illumination_option >= 1 and ShaderItem.self_illumination_option <= 11)):                
                    if(ShaderOutputCount <= 2): #if only less than 1 or 2 Shader outputs needed
                        if (ShadersConnected == 0):
                            #log_to_file("test p")
                            pymat_copy.node_tree.links.new(AddShader.inputs[0], SelfIllumGroup.outputs[0])
                            ShadersConnected = ShadersConnected + 1
                        elif (ShadersConnected == 1):
                            #log_to_file("test q")
                            pymat_copy.node_tree.links.new(AddShader.inputs[1], SelfIllumGroup.outputs[0])
                            ShadersConnected = ShadersConnected + 1                
                    elif(ShaderOutputCount == 3): #3 Shader outputs needed
                        if (ShadersConnected == 0):                
                            # log_to_file("test r")
                            pymat_copy.node_tree.links.new(Add3Group.inputs[0], SelfIllumGroup.outputs[0])
                            ShadersConnected = ShadersConnected + 1
                        elif (ShadersConnected == 1): 
                            # log_to_file("test s")
                            pymat_copy.node_tree.links.new(Add3Group.inputs[1], SelfIllumGroup.outputs[0])
                            ShadersConnected = ShadersConnected + 1            
                        elif (ShadersConnected == 2):
                            #log_to_file("test t")
                            pymat_copy.node_tree.links.new(Add3Group.inputs[2], SelfIllumGroup.outputs[0])
                            ShadersConnected = ShadersConnected + 1   
                log_to_file("Shader Outputs Connected: " + str(ShadersConnected))
                #CONNECT ALBEDO.rgb GROUP output TO SELF ILLUM if self illum option is "from_diffuse"

                
                #if alpha test exists then alpha test goes right after last add shader and before the material output
                        
                #IF BLEND MODE = additive then add additional Add Shader node and then plug transparency BSDF into that

                        
                        
                #connect "Add Shader" and/or "Materiol Output" and/or "Additive Group" and/or AlphaBlendGroup
                if ((Shader_Type == 0 or Shader_Type == 3 or Shader_Type == 4) and ShaderOutputCount <= 2):
                    if (ShaderItem.alpha_test_option == 0): #alpha test = off
                        if (ShaderItem.blend_mode_option == 1):
                            #log_to_file("test 1")
                            pymat_copy.node_tree.links.new(AdditiveGroup.inputs["Shader"], AddShader.outputs["Shader"])                
                            pymat_copy.node_tree.links.new(material_output.inputs["Surface"], AdditiveGroup.outputs["Shader"])
                        elif(ShaderItem.blend_mode_option == 3 or ShaderItem.blend_mode_option == 5):
                            #log_to_file("test 2")
                            pymat_copy.node_tree.links.new(AlphaBlendGroup.inputs["Shader"], AddShader.outputs["Shader"])
                            pymat_copy.node_tree.links.new(material_output.inputs["Surface"], AlphaBlendGroup.outputs["Shader"])
                        else:
                            #log_to_file("test 3")
                            pymat_copy.node_tree.links.new(material_output.inputs["Surface"], AddShader.outputs["Shader"])            
                    elif (ShaderItem.alpha_test_option == 1): #alpha test = simple
                        if(ShaderItem.blend_mode_option == 1):
                            #log_to_file("test 4")
                            pymat_copy.node_tree.links.new(AlphaTestGroup.inputs["Shader"], AddShader.outputs["Shader"])             
                            pymat_copy.node_tree.links.new(AdditiveGroup.inputs["Shader"], AlphaTestGroup.outputs["Shader"])                
                            pymat_copy.node_tree.links.new(material_output.inputs["Surface"], AdditiveGroup.outputs["Shader"]) 
                        elif(ShaderItem.blend_mode_option == 3 or ShaderItem.blend_mode_option == 5):
                            #log_to_file("test 5")
                            pymat_copy.node_tree.links.new(AlphaTestGroup.inputs["Shader"], AddShader.outputs["Shader"])
                            pymat_copy.node_tree.links.new(AlphaBlendGroup.inputs["Shader"], AlphaTestGroup.outputs["Shader"])
                            pymat_copy.node_tree.links.new(material_output.inputs["Surface"], AlphaBlendGroup.outputs["Shader"])            
                        else:
                            #log_to_file("test 6")
                            pymat_copy.node_tree.links.new(material_output.inputs["Surface"], AlphaTestGroup.outputs["Shader"])
                            pymat_copy.node_tree.links.new(AlphaTestGroup.inputs["Shader"], AddShader.outputs["Shader"])
                if(Shader_Type == 6):
                    pymat_copy.node_tree.links.new(material_output.inputs["Surface"], AddShader.outputs["Shader"])
                
                if ((Shader_Type == 0 or Shader_Type == 3 or Shader_Type == 4) and ShaderOutputCount == 3):
                    if (ShaderItem.alpha_test_option == 0): #alpha test = off
                        if (ShaderItem.blend_mode_option == 1):
                            pymat_copy.node_tree.links.new(AdditiveGroup.inputs["Shader"], Add3Group.outputs["Shader"])                
                            pymat_copy.node_tree.links.new(material_output.inputs["Surface"], AdditiveGroup.outputs["Shader"])
                        elif(ShaderItem.blend_mode_option == 3 or ShaderItem.blend_mode_option == 5):
                            pymat_copy.node_tree.links.new(AlphaBlendGroup.inputs["Shader"], Add3Group.outputs["Shader"])
                            pymat_copy.node_tree.links.new(material_output.inputs["Surface"], AlphaBlendGroup.outputs["Shader"])            
                        else:
                            pymat_copy.node_tree.links.new(material_output.inputs["Surface"], Add3Group.outputs["Shader"])            
                    elif (ShaderItem.alpha_test_option == 1): #alpha test = simple
                        if(ShaderItem.blend_mode_option == 1):
                            pymat_copy.node_tree.links.new(AlphaTestGroup.inputs["Shader"], Add3Group.outputs["Shader"])             
                            pymat_copy.node_tree.links.new(AdditiveGroup.inputs["Shader"], AlphaTestGroup.outputs["Shader"])                
                            pymat_copy.node_tree.links.new(material_output.inputs["Surface"], AdditiveGroup.outputs["Shader"]) 
                        elif(ShaderItem.blend_mode_option == 3 or ShaderItem.blend_mode_option == 5):
                            pymat_copy.node_tree.links.new(AlphaBlendGroup.inputs["Shader"], Add3Group.outputs["Shader"])
                            pymat_copy.node_tree.links.new(material_output.inputs["Surface"], AlphaBlendGroup.outputs["Shader"])            
                        else:
                            pymat_copy.node_tree.links.new(material_output.inputs["Surface"], AlphaTestGroup.outputs["Shader"])
                            pymat_copy.node_tree.links.new(AlphaTestGroup.inputs["Shader"], Add3Group.outputs["Shader"])
                    
                      
                #######################      
                # .shader_terrain files      
                #######################
                
                #Add Shader Groups to Material Output
                if(Shader_Type == 1):
                    if(ShaderOutputCount <= 2):
                        pymat_copy.node_tree.links.new(material_output.inputs["Surface"], AddShader.outputs["Shader"])
                    else:
                        #log_to_file("Count of Shader Outputs 3: " + str(ShaderOutputCount))
                        log_to_file("Shader Output value bigger than expected")
                # elif(Shader_Type == 1 and ShaderOutputCount == 3):          
                    # pymat_copy.node_tree.links.new(material_output.inputs["Surface"], Add3Group.outputs["Shader"])          
                # elif(Shader_Type == 1 and ShaderOutputCount == 4):          
                    # pymat_copy.node_tree.links.new(material_output.inputs["Surface"], Add4Group.outputs["Shader"])           
                # elif(Shader_Type == 1 and ShaderOutputCount == 5):          
                    # pymat_copy.node_tree.links.new(material_output.inputs["Surface"], Add5Group.outputs["Shader"])           
                      
                # #separate Color node to terrain shader groups
                # if(Shader_Type == 1):
                    # if(ShaderItem.material_0_option != 2): #if material_0 is not off
                        # pymat_copy.node_tree.links.new(TerrainGroupM0.inputs["blend_map_channel"], SeparateColorGroup.outputs["Red"]) 
                    # if(ShaderItem.material_1_option != 2): #if material_1 is not off
                        # pymat_copy.node_tree.links.new(TerrainGroupM1.inputs["blend_map_channel"], SeparateColorGroup.outputs["Green"])           
                    # if(ShaderItem.material_2_option != 2): #if material_2 is not off
                        # pymat_copy.node_tree.links.new(TerrainGroupM2.inputs["blend_map_channel"], SeparateColorGroup.outputs["Blue"])           
                      
                #connect Terrain shader groups and environment shader groups to AddShader groups      
                if(Shader_Type == 1):
                    connected_shaders = 0 #helps keep track of what spot on AddShader to plug into
                    
                    if(ShaderOutputCount <= 2): #if there are 2 or less shader outputs needed            
                        pymat_copy.node_tree.links.new(AddShader.inputs[0], TerrainGroup.outputs["Shader"])
                        
                        if (ShaderItem.environment_mapping_option == 1): # per_pixel
                            #Connect TerrainGroup to TerrainEnvGroup
                            pymat_copy.node_tree.links.new(TerrainEnvGroup.inputs[0], TerrainGroup.outputs[1])
                            
                            #Connect TerrainEvnGroup to AddShader
                            pymat_copy.node_tree.links.new(AddShader.inputs[1], TerrainEnvGroup.outputs[0])
                        elif (ShaderItem.environment_mapping_option == 2): # dynamic
                            #Connect TerrainGroup to TerrainEnvGroup
                            pymat_copy.node_tree.links.new(TerrainEnvGroup.inputs[0], TerrainGroup.outputs[1])  
                            pymat_copy.node_tree.links.new(TerrainEnvGroup.inputs[1], TerrainGroup.outputs[2])
                            pymat_copy.node_tree.links.new(TerrainEnvGroup.inputs["Normal"], TerrainGroup.outputs["Normal"])
                            
                            #connect TerrainEnvGroup to AddShader
                            pymat_copy.node_tree.links.new(AddShader.inputs[1], TerrainEnvGroup.outputs[0])
                       

                       # if(ShaderItem.material_0_option != 2): #if material_0 is not off
                            # pymat_copy.node_tree.links.new(AddShader.inputs[connected_shaders], TerrainGroupM0.outputs["Shader"]) 
                            # connected_shaders = connected_shaders + 1
                        # if(ShaderItem.material_1_option != 2): #if material_1 is not off
                            # pymat_copy.node_tree.links.new(AddShader.inputs[connected_shaders], TerrainGroupM1.outputs["Shader"]) 
                            # connected_shaders = connected_shaders + 1              
                        # if(ShaderItem.material_2_option != 2): #if material_2 is not off
                            # pymat_copy.node_tree.links.new(AddShader.inputs[connected_shaders], TerrainGroupM2.outputs["Shader"]) 
                            # connected_shaders = connected_shaders + 1    
                        # if(ShaderItem.material_3_option != 0): #if material_3 is not off
                            # pymat_copy.node_tree.links.new(AddShader.inputs[connected_shaders], TerrainGroupM3.outputs["Shader"]) 
                            # connected_shaders = connected_shaders + 1                    

                    # elif(ShaderOutputCount == 3): #if there are 2 or less shader outputs needed            
                        # if(ShaderItem.material_0_option != 2): #if material_0 is not off
                            # pymat_copy.node_tree.links.new(Add3Group.inputs[connected_shaders], TerrainGroupM0.outputs["Shader"]) 
                            # connected_shaders = connected_shaders + 1
                        # if(ShaderItem.material_1_option != 2): #if material_1 is not off
                            # pymat_copy.node_tree.links.new(Add3Group.inputs[connected_shaders], TerrainGroupM1.outputs["Shader"]) 
                            # connected_shaders = connected_shaders + 1              
                        # if(ShaderItem.material_2_option != 2): #if material_2 is not off
                            # pymat_copy.node_tree.links.new(Add3Group.inputs[connected_shaders], TerrainGroupM2.outputs["Shader"]) 
                            # connected_shaders = connected_shaders + 1    
                        # if(ShaderItem.material_3_option != 0): #if material_3 is not off
                            # pymat_copy.node_tree.links.new(Add3Group.inputs[connected_shaders], TerrainGroupM3.outputs["Shader"]) 
                            # connected_shaders = connected_shaders + 1                    

                    # elif(ShaderOutputCount == 4): #if there are 2 or less shader outputs needed            
                        # if(ShaderItem.material_0_option != 2): #if material_0 is not off
                            # pymat_copy.node_tree.links.new(Add4Group.inputs[connected_shaders], TerrainGroupM0.outputs["Shader"]) 
                            # connected_shaders = connected_shaders + 1
                        # if(ShaderItem.material_1_option != 2): #if material_1 is not off
                            # pymat_copy.node_tree.links.new(Add4Group.inputs[connected_shaders], TerrainGroupM1.outputs["Shader"]) 
                            # connected_shaders = connected_shaders + 1              
                        # if(ShaderItem.material_2_option != 2): #if material_2 is not off
                            # pymat_copy.node_tree.links.new(Add4Group.inputs[connected_shaders], TerrainGroupM2.outputs["Shader"]) 
                            # connected_shaders = connected_shaders + 1    
                        # if(ShaderItem.material_3_option != 0): #if material_3 is not off
                            # pymat_copy.node_tree.links.new(Add4Group.inputs[connected_shaders], TerrainGroupM3.outputs["Shader"]) 
                            # connected_shaders = connected_shaders + 1 

                    # elif(ShaderOutputCount == 5): #if there are 2 or less shader outputs needed            
                        # if(ShaderItem.material_0_option != 2): #if material_0 is not off
                            # pymat_copy.node_tree.links.new(Add5Group.inputs[connected_shaders], TerrainGroupM0.outputs["Shader"]) 
                            # connected_shaders = connected_shaders + 1
                        # if(ShaderItem.material_1_option != 2): #if material_1 is not off
                            # pymat_copy.node_tree.links.new(Add5Group.inputs[connected_shaders], TerrainGroupM1.outputs["Shader"]) 
                            # connected_shaders = connected_shaders + 1              
                        # if(ShaderItem.material_2_option != 2): #if material_2 is not off
                            # pymat_copy.node_tree.links.new(Add5Group.inputs[connected_shaders], TerrainGroupM2.outputs["Shader"]) 
                            # connected_shaders = connected_shaders + 1    
                        # if(ShaderItem.material_3_option != 0): #if material_3 is not off
                            # pymat_copy.node_tree.links.new(Add5Group.inputs[connected_shaders], TerrainGroupM3.outputs["Shader"]) 
                            # connected_shaders = connected_shaders + 1       

             

                #######################      
                # .shader_foliage files      
                #######################

                if(Shader_Type == 2):
                    if (ShaderItem.alpha_test_option != 0):
                        log_to_file("      foliage 1")
                        pymat_copy.node_tree.links.new(material_output.inputs["Surface"], AlphaTestGroup.outputs["Shader"])
                        pymat_copy.node_tree.links.new(AlphaTestGroup.inputs["Shader"], MatModelGroup.outputs["Shader"])
                    else:
                        pymat_copy.node_tree.links.new(material_output.inputs["Surface"], MatModelGroup.outputs["Shader"])
                        log_to_file("      foliage 2")


                #######################      
                # .shader_halogram files      
                #######################

                






                ##Output bitmap_list for testing   
                #log_to_file("bitmap list:  " + str(ShaderItem.bitmap_list))









                


                #prep the area for textures
                last_texture_x = alb_group_x - TEXTURE_NODE_HORIZONTAL_PLACEMENT
                last_texture_y = alb_group_y + TEXTURE_NODE_VERTICAL_PLACEMENT
                MIRROR_PADDING = 0



                #fix texture location for terrain files
                if (Shader_Type == 1):
                    last_texture_x = last_texture_x - 400


                env_tex_index = 0

                                    ####################################
                                    #CREATE TEXTURE NODES AND OTHER DATA  
                                    ####################################   
                #loop through all bitmaps and create new image texture nodes for each one and scaling nodes        
                for bitm in range(ShaderItem.bitmap_count): 
                 
                    
                 
                    #adjust location     
                    last_texture_x = last_texture_x
                    last_texture_y = last_texture_y - TEXTURE_GROUP_VERTICAL_SPACING - MIRROR_PADDING
                
                    #fix texture start position if it is too high up
                    if(last_texture_y > 400):
                        last_texture_y = 100
                
                
                    #correct texture node placement when there is no texture made
                    before_no_tex_x = last_texture_x
                    before_no_tex_y = last_texture_y
                    
                    log_to_file("last_texture_x: " + str(last_texture_x))
                    log_to_file("last_texture_y: " + str(last_texture_y))
                    
                    gamma_node_made = 0
                    texture_node_made = 0
                    mirror_node_made = 0
                    trans_node_made = 0
                 
                    #might be needed if I make two env tex nodes
                    index_buffer = 1
                 
                    #mapping and scaling node with values
                    #image texture node
                    #connect the nodes together
                    #TexImage.bl_idname = "TexImage" + str(bitm)
                    #log_to_file("bitm: " + str(bitm))
                    #log_to_file(ShaderItem.bitmap_list[bitm].type)
                    #DO A TRY BLOCK HERE IN CASE A TEXTURE CANNOT BE FOUND!!!!!!!!!!!

                    #CREATE NEEDED TEXTURE And ENVIRONMENT NODES
                    if (ShaderItem.bitmap_list[bitm].type == "environment_map"):
                        ImageTextureNodeList.append(pymat_copy.node_tree.nodes.new('ShaderNodeTexImage')) #add this to just make the code happy
                        EnvTextureNodeList.append(pymat_copy.node_tree.nodes.new('ShaderNodeTexEnvironment'))
                        EnvTextureNodeList.append(pymat_copy.node_tree.nodes.new('ShaderNodeTexEnvironment'))
                        bitmap_error = 0
                    else:    
                        ImageTextureNodeList.append(pymat_copy.node_tree.nodes.new('ShaderNodeTexImage')) #add image texture for each bitmap needed
                        bitmap_error = 0

                    #Create Textures IF the option for them are not turned off
                    if (Is_Bitmap_Disabled(ShaderItem, ShaderItem.bitmap_list[bitm].type) != True):
                        log_to_file(ShaderItem.bitmap_list[bitm].type + " is not disabled")
                        #log_to_file(ImageTextureNodeList)
                        
                        if (is_valid_dir(ShaderItem.bitmap_list[bitm].directory) == True):    
                            filepath = bpy.data.filepath
                            directory = os.path.dirname(filepath)
                            
                            if (directory == "" or directory == " " or directory == "  "):
                                directory = Export_Root
                            
                            try:
                                #CUBEMAP CONVERSION CODE TESTING
                                #if (ShaderItem.bitmap_list[bitm].type == "environment_map"):
                                    #convert texture to equirectangular map
                                    #os.system("python convert_cube.py " + ShaderItem.bitmap_list[bitm].directory + IMAGE_EXTENSION + " " + IMAGE_EXTENSION)
                                #else:
                                
                                #if bitmap is supposed to be environment_map texture then create 2 env node group instead
                                if (ShaderItem.bitmap_list[bitm].type == "environment_map"):
                                    ImageTextureNodeList[bitm + 1].image = bpy.data.images.load(directory + '/' + ShaderItem.bitmap_list[bitm].directory + IMAGE_EXTENSION)
                                    log_to_file(ShaderItem.bitmap_list[bitm].equi_paths)
                                    EnvTextureNodeList[env_tex_index + 1].image = bpy.data.images.load(ShaderItem.bitmap_list[bitm].equi_paths[0])
                                    EnvTextureNodeList[env_tex_index + 1].image.colorspace_settings.name = Linear_Colorspace_Name
                                    EnvTextureNodeList[env_tex_index + 2].image = bpy.data.images.load(ShaderItem.bitmap_list[bitm].equi_paths[1])
                                    EnvTextureNodeList[env_tex_index + 2].image.colorspace_settings.name = Linear_Colorspace_Name
                                    texture_node_made = 2
                                
                                #if bitmap is not environment_map                                
                                else:    
                                    ImageTextureNodeList[bitm + 1].image = bpy.data.images.load(directory + '/' + ShaderItem.bitmap_list[bitm].directory + IMAGE_EXTENSION)
                                    log_to_file("Created type: " + ShaderItem.bitmap_list[bitm].type)
                                    texture_node_made = 1
                                
                            except: 
                                log_to_file(ShaderItem.bitmap_list[bitm].type + " texture not found")
                                    
                                #if statements for default_detail and gray_50_percent
                                if (uses_gray_50(ShaderItem.bitmap_list[bitm].type) == True):
                                    log_to_file(directory + '/' + DEFAULT_BITMAP_DIR + "gray_50_percent" + IMAGE_EXTENSION)
                                    ImageTextureNodeList[bitm + 1].image = bpy.data.images.load(directory + '/' + DEFAULT_BITMAP_DIR + "gray_50_percent" + IMAGE_EXTENSION)
                                    log_to_file("gray_50_percent has been added to" + ShaderItem.bitmap_list[bitm].type)
                                    #BE SURE TO ADD IN DEFAULT DATA AS WELL LATER
                                    texture_node_made = 1
                                elif (uses_default_detail(ShaderItem.bitmap_list[bitm].type) == True):
                                    ImageTextureNodeList[bitm + 1].image = bpy.data.images.load(directory + '/' + DEFAULT_BITMAP_DIR + "default_detail" + IMAGE_EXTENSION)
                                    log_to_file("default detail has been added to " + ShaderItem.bitmap_list[bitm].type)
                                    #BE SURE TO ADD IN DEFAULT DATA AS WELL LATER
                                    texture_node_made = 1
                                elif (uses_default_vector(ShaderItem.bitmap_list[bitm].type) == True):
                                    ImageTextureNodeList[bitm + 1].image = bpy.data.images.load(directory + '/' + DEFAULT_BITMAP_DIR + "default_vector" + IMAGE_EXTENSION)
                                    log_to_file("default vector has been added to " + ShaderItem.bitmap_list[bitm].type)
                                    #BE SURE TO ADD IN DEFAULT DATA AS WELL LATER
                                    texture_node_made = 1
                                elif (uses_default_dynamic_cube_map(ShaderItem.bitmap_list[bitm].type) == True):
                                    ImageTextureNodeList[bitm + 1].image = bpy.data.images.load(directory + '/' + DEFAULT_BITMAP_DIR + "default_dynamic_cube_map" + IMAGE_EXTENSION)
                                    log_to_file("default dynamic cubemap has been added to " + ShaderItem.bitmap_list[bitm].type)
                                    #BE SURE TO ADD IN DEFAULT DATA AS WELL LATER
                                    texture_node_made = 1
                                elif (uses_color_white(ShaderItem.bitmap_list[bitm].type) == True):
                                    ImageTextureNodeList[bitm + 1].image = bpy.data.images.load(directory + '/' + DEFAULT_BITMAP_DIR + "color_white" + IMAGE_EXTENSION)
                                    log_to_file("color_white has been added to " + ShaderItem.bitmap_list[bitm].type)
                                    #BE SURE TO ADD IN DEFAULT DATA AS WELL LATER
                                    texture_node_made = 1
                                # elif (uses_monochrome_alpha_grid(ShaderItem.bitmap_list[bitm].type) == True):
                                    # ImageTextureNodeList[bitm + 1].image = bpy.data.images.load(directory + '/' + DEFAULT_BITMAP_DIR + "monochrome_alpha_grid" + IMAGE_EXTENSION)
                                    # log_to_file("monochrome_alpha_grid has been added to " + ShaderItem.bitmap_list[bitm].type)
                                    # #BE SURE TO ADD IN DEFAULT DATA AS WELL LATER
                                    # texture_node_made = 1
                                elif (uses_color_red(ShaderItem.bitmap_list[bitm].type) == True):
                                    ImageTextureNodeList[bitm + 1].image = bpy.data.images.load(directory + '/' + DEFAULT_BITMAP_DIR + "color_red" + IMAGE_EXTENSION)
                                    log_to_file("color_red has been added to " + ShaderItem.bitmap_list[bitm].type)
                                    #BE SURE TO ADD IN DEFAULT DATA AS WELL LATER
                                    texture_node_made = 1
                                # elif (uses_default_alpha_test(ShaderItem.bitmap_list[bitm].type) == True):
                                    # ImageTextureNodeList[bitm + 1].image = bpy.data.images.load(directory + '/' + DEFAULT_BITMAP_DIR + "default_alpha_test" + IMAGE_EXTENSION)
                                    # log_to_file("alpha_test_map has been added to " + ShaderItem.bitmap_list[bitm].type)
                                    # #BE SURE TO ADD IN DEFAULT DATA AS WELL LATER
                                    # texture_node_made = 1
                                # elif (uses_reference_grids(ShaderItem.bitmap_list[bitm].type) == True):
                                    # ImageTextureNodeList[bitm + 1].image = bpy.data.images.load(directory + '/' + DEFAULT_BITMAP_DIR + "reference_grids" + IMAGE_EXTENSION)
                                    # log_to_file("reference_grids has been added to " + ShaderItem.bitmap_list[bitm].type)
                                    # #BE SURE TO ADD IN DEFAULT DATA AS WELL LATER
                                    # texture_node_made = 1
                                
                                
                                else:
                                    bitmap_error = 1
                                    log_to_file("NoneType Created for: " + ShaderItem.bitmap_list[bitm].type)
                            
                            
                            # #Specular data linking to main group shaders
                            # if(bitmap_error != 1 and (ShaderItem.specular_mask_option == 1)):
                                # log_to_file(ShaderItem.bitmap_list[bitm].type + " Image has alpha data")
                            # elif (bitmap_error != 1 and ShaderItem.specular_mask_option == 0):
                                # log_to_file("No Specular")
                            # else:
                                # log_to_file("Possible specular data")
                            
                            #Edit the names of the created Image Texture nodes
                            try:
                                if (ShaderItem.bitmap_list[bitm].type == "environment_map"):
                                    EnvTextureNodeList[env_tex_index + 1].image.name =  "[" + ShaderItem.bitmap_list[bitm].type + "_rgb]  " + EnvTextureNodeList[env_tex_index + 1].image.name
                                    EnvTextureNodeList[env_tex_index + 2].image.name =  "[" + ShaderItem.bitmap_list[bitm].type + "_alpha]  " + EnvTextureNodeList[env_tex_index + 2].image.name
                                    log_to_file(EnvTextureNodeList[env_tex_index + 1].name)
                                    log_to_file(EnvTextureNodeList[env_tex_index + 2].name)
                                else:    
                                    ImageTextureNodeList[bitm + 1].image.name =  "[" + ShaderItem.bitmap_list[bitm].type + "]  " + ImageTextureNodeList[bitm + 1].image.name
                                    log_to_file(ImageTextureNodeList[bitm + 1].name)
                            except:
                                log_to_file("Couldn't rename NoneType!")
                            
                                
                                                ###################
                                                #CREATE GAMMA NODES
                                                ###################
                            #Handle Curve/Colorspace Data
                            #gamma_value = 1.00
                            
                            if(ShaderItem.bitmap_list[bitm].curve_option == 0 and bitmap_error != 1): #curve = unknown  CHECK WITH CHIEF
                                ImageTextureNodeList[bitm + 1].image.colorspace_settings.name = Linear_Colorspace_Name                    
                                #Check library of unknown textures for Gamma values
                                log_to_file("Using 'unknown' curve value, setting value to 1.00")
                                gamma_value = 1.00
                                gamma_node_made = 1
                            elif(ShaderItem.bitmap_list[bitm].curve_option == 1 and bitmap_error != 1): #curve = xRGB
                                ImageTextureNodeList[bitm + 1].image.colorspace_settings.name = Linear_Colorspace_Name
                                gamma_value = 1.95
                                gamma_node_made = 1
                                
                            elif(ShaderItem.bitmap_list[bitm].curve_option == 2 and bitmap_error != 1): #curve = gamma 2.0
                                ImageTextureNodeList[bitm + 1].image.colorspace_settings.name = Linear_Colorspace_Name
                                gamma_value = 2.00
                                gamma_node_made = 1

                                if(ShaderItem.bitmap_list[bitm].type == "base_map"):
                                    #create Gamma Node
                                    GammaNode_Base = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_Base.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_Base.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                
                                    GammaNode_Base.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_Base.location.y = last_texture_y                     
                                    GammaNode_Base.hide = True
                                elif(ShaderItem.bitmap_list[bitm].type == "detail_map"):
                                    #create Gamma Node
                                    GammaNode_Detail = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_Detail.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_Detail.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])

                                    GammaNode_Detail.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_Detail.location.y = last_texture_y                     
                                    GammaNode_Detail.hide = True
                                elif(ShaderItem.bitmap_list[bitm].type == "detail_map2"):
                                    #create Gamma Node
                                    GammaNode_Detail = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_Detail.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_Detail.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])

                                    GammaNode_Detail.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_Detail.location.y = last_texture_y                     
                                    GammaNode_Detail.hide = True
                                elif(ShaderItem.bitmap_list[bitm].type == "detail_map3"):
                                    #create Gamma Node
                                    GammaNode_Detail = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_Detail.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_Detail.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])

                                    GammaNode_Detail.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_Detail.location.y = last_texture_y                     
                                    GammaNode_Detail.hide = True                     
                                elif(ShaderItem.bitmap_list[bitm].type == "detail_map_overlay"):
                                    #create Gamma Node
                                    GammaNode_Detail = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_Detail.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_Detail.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])

                                    GammaNode_Detail.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_Detail.location.y = last_texture_y                     
                                    GammaNode_Detail.hide = True
                                elif(ShaderItem.bitmap_list[bitm].type == "bump_map"):
                                    #create Gamma Node
                                    GammaNode_Bump = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_Bump.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_Bump.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])

                                    GammaNode_Bump.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_Bump.location.y = last_texture_y                     
                                    GammaNode_Bump.hide = True
                                elif(ShaderItem.bitmap_list[bitm].type == "bump_detail_map"):
                                    #create Gamma Node
                                    GammaNode_BumpDetail = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_BumpDetail.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_BumpDetail.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])

                                    GammaNode_BumpDetail.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_BumpDetail.location.y = last_texture_y 
                                    GammaNode_BumpDetail.hide = True
                                elif(ShaderItem.bitmap_list[bitm].type == "self_illum_map"):
                                    #create Gamma Node
                                    GammaNode_SelfIllum = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_SelfIllum.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_SelfIllum.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])

                                    GammaNode_SelfIllum.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_SelfIllum.location.y = last_texture_y 
                                    GammaNode_SelfIllum.hide = True
                                elif(ShaderItem.bitmap_list[bitm].type == "self_illum_detail_map"):
                                    #create Gamma Node
                                    GammaNode_SelfIllumDetail = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_SelfIllumDetail.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_SelfIllumDetail.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])

                                    GammaNode_SelfIllumDetail.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_SelfIllumDetail.location.y = last_texture_y                         
                                    GammaNode_SelfIllumDetail.hide = True
                                #terrain shaders    
                                elif(ShaderItem.bitmap_list[bitm].type == "base_map_m_0"):
                                    #create Gamma Node
                                    GammaNode_Base_M0 = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_Base_M0.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_Base_M0.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])

                                    GammaNode_Base_M0.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_Base_M0.location.y = last_texture_y                     
                                    GammaNode_Base_M0.hide = True
                                elif(ShaderItem.bitmap_list[bitm].type == "base_map_m_1"):
                                    #create Gamma Node
                                    GammaNode_Base_M1 = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_Base_M1.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_Base_M1.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])

                                    GammaNode_Base_M1.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_Base_M1.location.y = last_texture_y                         
                                    GammaNode_Base_M1.hide = True
                                elif(ShaderItem.bitmap_list[bitm].type == "base_map_m_2"):
                                    #create Gamma Node
                                    GammaNode_Base_M2 = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_Base_M2.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_Base_M2.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])

                                    GammaNode_Base_M2.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_Base_M2.location.y = last_texture_y 
                                    GammaNode_Base_M2.hide = True
                                elif(ShaderItem.bitmap_list[bitm].type == "base_map_m_3"):
                                    #create Gamma Node
                                    GammaNode_Base_M3 = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_Base_M3.inputs.get("Gamma").default_value = gamma_value

                                    #link Gamma Node
                                    pymat_copy.node_tree.links.new(GammaNode_Base_M3.inputs["Color"], ImageTextureNodeList[bitm + 1].outputs["Color"])   
             
                                    GammaNode_Base_M3.location.x = last_texture_x + TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                                    GammaNode_Base_M3.location.y = last_texture_y  
                                    GammaNode_Base_M3.hide = True
                                elif(ShaderItem.bitmap_list[bitm].type == "detail_map_m_0"):
                                    #create Gamma Node
                                    GammaNode_Detail_M0 = pymat_copy.node_tree.nodes.new("ShaderNodeGamma")
                                    GammaNode_Detail_M0.inputs.get("Gamma").default_value = gamma_value


                            elif(ShaderItem.bitmap_list[bitm].curve_option == 3 and bitmap_error != 1): #curve = linear
                                ImageTextureNodeList[bitm + 1].image.colorspace_settings.name = Linear_Colorspace_Name
                                gamma_value = 1
                                gamma_node_made = 1
                                
                            elif(ShaderItem.bitmap_list[bitm].curve_option == 4 and bitmap_error != 1): #curve = offset log
                                ImageTextureNodeList[bitm + 1].image.colorspace_settings.name = Linear_Colorspace_Name
                                log_to_file("WARNING: OFFSET LOG CURVE DATA FOUND! MIGHT NOT BE ACCURATE")
                                #unknown at this time ask Chief
                                gamma_value = 1
                                gamma_node_made = 1
                            elif(ShaderItem.bitmap_list[bitm].curve_option == 5 and bitmap_error != 1): #curve = sRGB
                                ImageTextureNodeList[bitm + 1].image.colorspace_settings.name = Linear_Colorspace_Name
                                gamma_value = 2.2
                                gamma_node_made = 1
                                
                            #Why is this here??? Just to suffer?!?!
                            # elif(ShaderItem.bitmap_list[bitm].curve_option == 6 and bitmap_error != 1): #curve = Default Data
                                # ImageTextureNodeList[bitm + 1].image.colorspace_settings.name = Linear_Colorspace_Name
                                # log_to_file("Curve Option 6, please check!")
                                # gamma_value = 1.00
                                # gamma_node_made = 1
                            else:
                                gamma_value = 1
                                log_to_file("Curve Data Error!")
                            
                            
                            #location of texture and gamma nodes
                            if(texture_node_made == 1):
                                if(gamma_node_made == 1):
                                    ImageTextureNodeList[bitm + 1].location.x = last_texture_x 
                                    ImageTextureNodeList[bitm + 1].location.y = last_texture_y - TEXTURE_NODE_W_GAMMA_HORIZONTAL_SPACING
                                    
                                    last_node_x = last_texture_x 
                                    last_node_y = last_texture_y - TEXTURE_NODE_W_GAMMA_HORIZONTAL_SPACING

                                    
                                    ImageTextureNodeList[bitm + 1].hide = True               
                                else:   
                                    ImageTextureNodeList[bitm + 1].location.x = last_texture_x
                                    ImageTextureNodeList[bitm + 1].location.y = last_texture_y                        
                                    
                                    last_node_x = last_texture_x
                                    last_node_y = last_texture_y          
                                  
                                    ImageTextureNodeList[bitm + 1].hide = True
                            elif(texture_node_made == 2):
                                
                                temp_location_x = last_texture_x
                                temp_location_y = last_texture_y
                                
                                
                                #place environment_texture in the column for reference
                                ImageTextureNodeList[bitm + 1].location.x = last_texture_x + 820
                                ImageTextureNodeList[bitm + 1].location.y = last_texture_y - 150
                                
                                last_node_x = last_texture_x + 820
                                last_node_y = last_texture_y - 150

                                last_texture_x = last_node_x
                                last_texture_y = last_node_y
                                
                                ImageTextureNodeList[bitm + 1].hide = True  
                                
                                #Place the two Environment Texture nodes in the right spot
                                EnvTextureNodeList[1].location.x = last_texture_x 
                                EnvTextureNodeList[1].location.y = last_texture_y - 50
                            
                                last_node_x = last_texture_x 
                                last_node_y = last_texture_y - 50
                                
                                last_texture_x = last_node_x
                                last_texture_y = last_node_y
                            
                                EnvTextureNodeList[1].hide = True 
                                
                                EnvTextureNodeList[2].location.x = last_texture_x 
                                EnvTextureNodeList[2].location.y = last_texture_y - 50
                            
                                last_node_x = last_texture_x 
                                last_node_y = last_texture_y - 50
                            
                                EnvTextureNodeList[2].hide = True
                            
                                last_texture_x = temp_location_x
                                last_texture_y = temp_location_y
                            
                            #all shader files
                            #Sets all textures to Channel Packed
                            if(bitmap_error != 1):
                                ImageTextureNodeList[bitm + 1].image.alpha_mode = "CHANNEL_PACKED"
                            


                            #log_to_file("scale uniform entering if: " + str(ShaderItem.bitmap_list[bitm].scale_uniform))
                            #log_to_file("scale xy entering if: " + str(ShaderItem.bitmap_list[bitm].scale_xy))
                            #log_to_file("trans xy entering if: " + str(ShaderItem.bitmap_list[bitm].translation_xy))
                            
                            log_to_file("Transform Data: scale_uniform = " + str(ShaderItem.bitmap_list[bitm].scale_uniform) + "  scale_xy = " + str(ShaderItem.bitmap_list[bitm].scale_xy))
                            
                            #CREATE SCALING NODES IF SCALING VALUES EXIST
                            if(ShaderItem.bitmap_list[bitm].scale_uniform != 1.00 or ShaderItem.bitmap_list[bitm].scale_xy != [1.00,1.00] or ShaderItem.bitmap_list[bitm].translation_xy != [0.00,0.00]): #if the scale values are not default
                                #create scaling node
                                TexCoordNode = pymat_copy.node_tree.nodes.new('ShaderNodeTexCoord')
                                
                                #create mapping node
                                MappingNode = pymat_copy.node_tree.nodes.new('ShaderNodeMapping')
                                
                                #link together the TexCoord node and the Mapping node
                                pymat_copy.node_tree.links.new(MappingNode.inputs["Vector"],TexCoordNode.outputs["UV"]) #connects UV to Vector
                                
                                trans_node_made = 1
                                
                                log_to_file("TRANSFORM DATA FOUND. MAKING MAPPING NODES")
                                #Change the values for scale uniform and XY
                                if(ShaderItem.bitmap_list[bitm].scale_uniform != 1.00):
                                    MappingNode.inputs.get("Scale").default_value = [ShaderItem.bitmap_list[bitm].scale_uniform, ShaderItem.bitmap_list[bitm].scale_uniform, 1.00]
                                    
                                    #link to texture node
                                    #pymat_copy.node_tree.links.new(ImageTextureNodeList[bitm + 1].inputs["Vector"], MappingNode.outputs["Vector"])
                                    
                                if(ShaderItem.bitmap_list[bitm].scale_xy != [1.00,1.00]):
                                    MappingNode.inputs.get("Scale").default_value = [ShaderItem.bitmap_list[bitm].scale_xy[0], ShaderItem.bitmap_list[bitm].scale_xy[1], 1.00]
                                    
                                    #link to texture node
                                    #pymat_copy.node_tree.links.new(ImageTextureNodeList[bitm + 1].inputs["Vector"], MappingNode.outputs["Vector"])
                                if(ShaderItem.bitmap_list[bitm].translation_xy != [0.00,0.00]):
                                    MappingNode.inputs.get("Location").default_value = [ShaderItem.bitmap_list[bitm].translation_xy[0], ShaderItem.bitmap_list[bitm].translation_xy[1], 0.00]
                                    
                                    #link to texture node
                                    #pymat_copy.node_tree.links.new(ImageTextureNodeList[bitm + 1].inputs["Vector"], MappingNode.outputs["Vector"])
                            
                                log_to_file("Wrap Option: " + str(ShaderItem.bitmap_list[bitm].wrap_option))
                                if (ShaderItem.bitmap_list[bitm].wrap_option == 3 or ShaderItem.bitmap_list[bitm].wrap_option == 13 or ShaderItem.bitmap_list[bitm].wrap_option == 2):
                                    #if wrap option type is set to mirror
                                    if(ShaderItem.bitmap_list[bitm].wrap_option_type == 2):
                                        log_to_file("making mirror map for " + ShaderItem.bitmap_list[bitm].type)
                                        
                                        #link texture to mirror group node
                                        MirrorGroup = instantiate_group(pymat_copy.node_tree.nodes, "CR4BUtility: XY Mirror Wrap")
                                        pymat_copy.node_tree.links.new(ImageTextureNodeList[bitm + 1].inputs["Vector"], MirrorGroup.outputs["Vector"])
                                        
                                        #link mapping to mirror group node
                                        pymat_copy.node_tree.links.new(MirrorGroup.inputs["Vector"], MappingNode.outputs["Vector"])
                                    
                                        #works for current iteration of the Mirror Nodes being at 47 meters in both X and Y
                                        #Check for extra shift due to texture resolution ratio
                                        if(ShaderItem.bitmap_list[bitm].width / ShaderItem.bitmap_list[bitm].height == (2/2)): #if the ratio is 1:1 then shift down Y by 3 meters
                                            MirrorGroup = shift_mirror_wrap(MirrorGroup)
                                    
                                        mirror_node_made = 1
                                    
                                    #if wrap option type is set to clamp
                                    elif(ShaderItem.bitmap_list[bitm].wrap_option_type == 1):
                                        #change the extension type of the image texture to CLIP
                                        log_to_file("Changing Extension mode to Clip!")
                                        ImageTextureNodeList[bitm + 1].extension = 'CLIP'
                                    else: 
                                        log_to_file("Unhandled Wrap Option Type! Type: " + str(ShaderItem.bitmap_list[bitm].wrap_option_type))
                                     
                                elif (ShaderItem.bitmap_list[bitm].wrap_option == 4 or ShaderItem.bitmap_list[bitm].wrap_option == 5):
                                    #if wrap option type is set to mirror
                                    if(ShaderItem.bitmap_list[bitm].wrap_option_type == 2):    
                                        log_to_file("making mirror map for " + ShaderItem.bitmap_list[bitm].type)
                                        
                                        #link texture to mirror group node
                                        MirrorGroup = instantiate_group(pymat_copy.node_tree.nodes, "CR4BUtility: X Mirror Wrap")
                                        pymat_copy.node_tree.links.new(ImageTextureNodeList[bitm + 1].inputs["Vector"], MirrorGroup.outputs["Vector"])
                                        
                                        #link mapping to mirror group node
                                        pymat_copy.node_tree.links.new(MirrorGroup.inputs["Vector"], MappingNode.outputs["Vector"])                    
                                    
                                        #Check for extra shift due to texture resolution ratio
                                        if(ShaderItem.bitmap_list[bitm].width / ShaderItem.bitmap_list[bitm].height == (2/2)): #if the ratio is 1:1 then shift down Y by 3 meters
                                            MirrorGroup = shift_mirror_wrap(MirrorGroup)
                                            
                                        mirror_node_made = 1
                                    #if wrap option type is set to clamp
                                    elif(ShaderItem.bitmap_list[bitm].wrap_option_type == 1):
                                        #change the extension type of the image texture to CLIP
                                        log_to_file("Changing Extension mode to Clip!")
                                        ImageTextureNodeList[bitm + 1].extension = 'CLIP'
                                    else: 
                                        log_to_file("Unhandled Wrap Option Type! Type: " + str(ShaderItem.bitmap_list[bitm].wrap_option_type))
                                elif (ShaderItem.bitmap_list[bitm].wrap_option == 9 or ShaderItem.bitmap_list[bitm].wrap_option == 8):
                                    #if wrap option type is set to mirror
                                    if(ShaderItem.bitmap_list[bitm].wrap_option_type == 2):
                                        log_to_file("making mirror map for " + ShaderItem.bitmap_list[bitm].type)
                                        
                                        #link texture to mirror group node
                                        MirrorGroup = instantiate_group(pymat_copy.node_tree.nodes, "CR4BUtility: Y Mirror Wrap")
                                        pymat_copy.node_tree.links.new(ImageTextureNodeList[bitm + 1].inputs["Vector"], MirrorGroup.outputs["Vector"])
                                        
                                        #link mapping to mirror group node
                                        pymat_copy.node_tree.links.new(MirrorGroup.inputs["Vector"], MappingNode.outputs["Vector"]) 
                                        
                                        #Check for extra shift due to texture resolution ratio
                                        if(ShaderItem.bitmap_list[bitm].width / ShaderItem.bitmap_list[bitm].height == (2/2)): #if the ratio is 1:1 then shift down Y by 3 meters
                                            MirrorGroup = shift_mirror_wrap(MirrorGroup)
                                            
                                        mirror_node_made = 1
                                    #if wrap option type is set to clamp
                                    elif(ShaderItem.bitmap_list[bitm].wrap_option_type == 1):
                                        #change the extension type of the image texture to CLIP
                                        log_to_file("Changing Extension mode to Clip!")
                                        ImageTextureNodeList[bitm + 1].extension = 'CLIP'
                                    else: 
                                        log_to_file("Unhandled Wrap Option Type! Type: " + str(ShaderItem.bitmap_list[bitm].wrap_option_type))
                                else:    
                                    #link to texture node
                                    pymat_copy.node_tree.links.new(ImageTextureNodeList[bitm + 1].inputs["Vector"], MappingNode.outputs["Vector"])
                            
                            #if no scale or translation data found BUT it is mirrored
                            else:
                                log_to_file("No scaling values found. Might make Mirror Node anyways")
                                log_to_file("Wrap Option: " + str(ShaderItem.bitmap_list[bitm].wrap_option))
                                
                                #Check for XY Mirror Map
                                if(ShaderItem.bitmap_list[bitm].wrap_option == 3 or ShaderItem.bitmap_list[bitm].wrap_option == 13 or ShaderItem.bitmap_list[bitm].wrap_option == 2):
                                    #if wrap option type is set to mirror
                                    if(ShaderItem.bitmap_list[bitm].wrap_option_type == 2):    
                                        log_to_file("making mirror map for " + ShaderItem.bitmap_list[bitm].type)
                                        #create scaling node
                                        TexCoordNode = pymat_copy.node_tree.nodes.new('ShaderNodeTexCoord')
                                        
                                        #create mapping node
                                        MappingNode = pymat_copy.node_tree.nodes.new('ShaderNodeMapping')
                                        
                                        #link together the TexCoord node and the Mapping node
                                        pymat_copy.node_tree.links.new(MappingNode.inputs["Vector"],TexCoordNode.outputs["UV"]) #connects UV to Vector
                                        
                                        #link texture to mirror group node
                                        MirrorGroup = instantiate_group(pymat_copy.node_tree.nodes, "CR4BUtility: XY Mirror Wrap")
                                        pymat_copy.node_tree.links.new(ImageTextureNodeList[bitm + 1].inputs["Vector"], MirrorGroup.outputs["Vector"])
                                  
                                        #link mapping to mirror group node
                                        pymat_copy.node_tree.links.new(MirrorGroup.inputs["Vector"], MappingNode.outputs["Vector"])       
                                  
                                        #Check for extra shift due to texture resolution ratio
                                        if(ShaderItem.bitmap_list[bitm].width / ShaderItem.bitmap_list[bitm].height == (2/2)): #if the ratio is 1:1 then shift down Y by 3 meters
                                            MirrorGroup = shift_mirror_wrap(MirrorGroup)
                                            
                                        mirror_node_made = 1
                                        trans_node_made = 1
                                    #if wrap option type is set to clamp
                                    elif(ShaderItem.bitmap_list[bitm].wrap_option_type == 1):
                                        #change the extension type of the image texture to CLIP
                                        log_to_file("Changing Extension mode to Clip!")
                                        ImageTextureNodeList[bitm + 1].extension = 'CLIP'
                                    else: 
                                        log_to_file("Unhandled Wrap Option Type! Type: " + str(ShaderItem.bitmap_list[bitm].wrap_option_type))
                                
                                #Check for X Mirror Map
                                elif(ShaderItem.bitmap_list[bitm].wrap_option == 4 or ShaderItem.bitmap_list[bitm].wrap_option == 5):
                                    #if wrap option type is set to mirror
                                    if(ShaderItem.bitmap_list[bitm].wrap_option_type == 2):        
                                        log_to_file("making mirror map for " + ShaderItem.bitmap_list[bitm].type)
                                        #create scaling node
                                        TexCoordNode = pymat_copy.node_tree.nodes.new('ShaderNodeTexCoord')
                                        
                                        #create mapping node
                                        MappingNode = pymat_copy.node_tree.nodes.new('ShaderNodeMapping')
                                        
                                        #link together the TexCoord node and the Mapping node
                                        pymat_copy.node_tree.links.new(MappingNode.inputs["Vector"],TexCoordNode.outputs["UV"]) #connects UV to Vector
                                        
                                        #link texture to mirror group node
                                        MirrorGroup = instantiate_group(pymat_copy.node_tree.nodes, "CR4BUtility: X Mirror Wrap")
                                        pymat_copy.node_tree.links.new(ImageTextureNodeList[bitm + 1].inputs["Vector"], MirrorGroup.outputs["Vector"])
                                  
                                        #link mapping to mirror group node
                                        pymat_copy.node_tree.links.new(MirrorGroup.inputs["Vector"], MappingNode.outputs["Vector"])                      
                                    
                                        #Check for extra shift due to texture resolution ratio
                                        if(ShaderItem.bitmap_list[bitm].width / ShaderItem.bitmap_list[bitm].height == (2/2)): #if the ratio is 1:1 then shift down Y by 3 meters
                                            MirrorGroup = shift_mirror_wrap(MirrorGroup)
                                            
                                        #If ratio is not 1:1 and if it is Y mirror wrap but if height > width then add 3m to Y translation
                                        
                                        #If ratio is not 1:1 and if it is X mirror wrap but if height < width then add 3m to X translation? DO NOT DO THIS PART YET
                                        
                                        #else:
                                        
                                            
                                        mirror_node_made = 1
                                        trans_node_made = 1
                                    #if wrap option type is set to clamp
                                    elif(ShaderItem.bitmap_list[bitm].wrap_option_type == 1):
                                        #change the extension type of the image texture to CLIP
                                        log_to_file("Changing Extension mode to Clip!")
                                        ImageTextureNodeList[bitm + 1].extension = 'CLIP'
                                    else: 
                                        log_to_file("Unhandled Wrap Option Type! Type: " + str(ShaderItem.bitmap_list[bitm].wrap_option_type))
                                
                                #Check for Y Mirror Map
                                elif (ShaderItem.bitmap_list[bitm].wrap_option == 9 or ShaderItem.bitmap_list[bitm].wrap_option == 8): #9 needs shifted Y by 3m for some things 8 is not
                                    #if wrap option type is set to mirror
                                    if(ShaderItem.bitmap_list[bitm].wrap_option_type == 2):        
                                        log_to_file("making mirror map for " + ShaderItem.bitmap_list[bitm].type)
                                        
                                        #if 
                                        #create scaling node
                                        TexCoordNode = pymat_copy.node_tree.nodes.new('ShaderNodeTexCoord')
                                        
                                        #create mapping node
                                        MappingNode = pymat_copy.node_tree.nodes.new('ShaderNodeMapping')
                                        
                                        #link together the TexCoord node and the Mapping node
                                        pymat_copy.node_tree.links.new(MappingNode.inputs["Vector"],TexCoordNode.outputs["UV"]) #connects UV to Vector
                                        
                                        #link texture to mirror group node
                                        MirrorGroup = instantiate_group(pymat_copy.node_tree.nodes, "CR4BUtility: Y Mirror Wrap")
                                        pymat_copy.node_tree.links.new(ImageTextureNodeList[bitm + 1].inputs["Vector"], MirrorGroup.outputs["Vector"])
                                  
                                        #link mapping to mirror group node
                                        pymat_copy.node_tree.links.new(MirrorGroup.inputs["Vector"], MappingNode.outputs["Vector"])        
                     
                                        #Check for extra shift due to texture resolution ratio
                                        if(ShaderItem.bitmap_list[bitm].width / ShaderItem.bitmap_list[bitm].height == (2/2)): #if the ratio is 1:1 then shift down Y by 3 meters
                                            MirrorGroup = shift_mirror_wrap(MirrorGroup)
                                            
                                        mirror_node_made = 1
                                        trans_node_made = 1
                                    #if wrap option type is set to clamp
                                    elif(ShaderItem.bitmap_list[bitm].wrap_option_type == 1):
                                        #change the extension type of the image texture to CLIP
                                        log_to_file("Changing Extension mode to Clip!")
                                        ImageTextureNodeList[bitm + 1].extension = 'CLIP'
                                    else: 
                                        log_to_file("Unhandled Wrap Option Type! Type: " + str(ShaderItem.bitmap_list[bitm].wrap_option_type))
                            
                            #locations of scaling and mirror nodes
                            if(mirror_node_made == 1):
                                MirrorGroup.location.x = last_node_x - TEXTURE_MIRROR_NODE_HORIZONTAL_SPACING
                                MirrorGroup.location.y = last_node_y
                                
                                last_node_x = MirrorGroup.location.x
                                last_node_y = MirrorGroup.location.y
                            if(trans_node_made == 1):
                                MappingNode.location.x = last_node_x - TEXTURE_MAPPING_HORIZONTAL_SPACING
                                MappingNode.location.y = last_node_y
                                
                                last_node_x = MappingNode.location.x
                                last_node_y = MappingNode.location.y
                            
                                TexCoordNode.location.x = last_node_x - TEXTURE_COORD_NODE_HORIZONTAL_SPACING
                                TexCoordNode.location.y = last_node_y
                                
                                last_node_x = TexCoordNode.location.x
                                last_node_y = TexCoordNode.location.y                
                            
                                MappingNode.hide = True
                                TexCoordNode.hide = True
                            #POSSIBLY NOT NEEDED AT ALL
                            #LABEL TEXTURE GROUPS
                            if(ShaderItem.bitmap_list[bitm].type == "base_map"):
                                BaseMap = ImageTextureNodeList[bitm + 1].image
                            elif(ShaderItem.bitmap_list[bitm].type == "detail_map"):
                                DetailMap = ImageTextureNodeList[bitm + 1].image
                            elif(ShaderItem.bitmap_list[bitm].type == "bump_map"):
                                BumpMap = ImageTextureNodeList[bitm + 1].image            
                            elif(ShaderItem.bitmap_list[bitm].type == "bump_detail_map"):
                                BumpDetailMap = ImageTextureNodeList[bitm + 1].image            
                            elif(ShaderItem.bitmap_list[bitm].type == "self_illum_map"):
                                SelfIllumMap = ImageTextureNodeList[bitm + 1].image  
                            elif(ShaderItem.bitmap_list[bitm].type == "self_illum_detail_map"):
                                SelfIllumDetailMap = ImageTextureNodeList[bitm + 1].image 
                            #elif(ShaderItem.bitmap_list[bitm].type == "environment_map"):
                                #EnvironmentMap = EnvTextureNodeList[bitm + 1].image    
                            else:
                                log_to_file("Texture is of a different type")            


                                                #ADD MORE POSSIBILITIES
                                                ###########################
                                                #CONNECT TEXTURES TO GROUPS
                                                ###########################

                            # .shader files
                                               
                            #BASE_MAP
                            #log_to_file("before base")
                            if((Shader_Type == 0 or Shader_Type == 2 or Shader_Type == 4) and ShaderItem.bitmap_list[bitm].type == "base_map"): # and ShaderGroupList[bitm + 1] == "albedo"):
                                #if albedo option = constant_color
                                log_to_file("  trying to link base_map")
                                if (ShaderItem.albedo_option == 2):
                                    #- rgb node
                                    #if curve uses Gamma
                                    #log_to_file("  base 0a")
                                    if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                        #link gamma to albedo
                                        #pymat_copy.node_tree.links.new(AlbedoGroup.inputs[0], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        #log_to_file("  base 0a1")
                                    
                                        log_to_file("not doing anything with base map because Albedo Option is Constant Color")
                                    
                                        #Edit value of Gamma on node group
                                        #AlbedoGroup.inputs["base_map Gamma Curve"].default_value = gamma_value
                                        #log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                    
                                    else:
                                        #log_to_file("  base 0a2")
                                        #link base_map to albedo
                                        #pymat_copy.node_tree.links.new(AlbedoGroup.inputs[0], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        
                                        log_to_file("not doing anything with base map because Albedo Option is Constant Color")
                                        
                                        #Edit value of Gamma on node group
                                        #AlbedoGroup.inputs["base_map Gamma Curve"].default_value = gamma_value
                                        #log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                #if albedo option is not constant color
                                
                                elif (ShaderItem.albedo_option != 2):
                                    #- rgb node
                                    #if curve uses Gamma
                                    #log_to_file("  base 1a")
                                    
                                    #if specular_mask_option is specular_mask_from_texture then do not connect alpha from base_map
                                    if(ShaderItem.specular_mask_option == 2):
                                        if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                            log_to_file(str(ShaderItem.bitmap_list[bitm].curve_option))
                                            #log_to_file("  base 1a1")
                                            #link gamma to albedo
                                            pymat_copy.node_tree.links.new(AlbedoGroup.inputs[0], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                            #pymat_copy.node_tree.links.new(AlbedoGroup.inputs[1], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                        
                                            #Edit value of Gamma on node group
                                            AlbedoGroup.inputs["base_map Gamma Curve"].default_value = gamma_value
                                            log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                        
                                        else:
                                            #log_to_file("  base 1a2")
                                            #link base_map to albedo
                                            pymat_copy.node_tree.links.new(AlbedoGroup.inputs[0], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                            #pymat_copy.node_tree.links.new(AlbedoGroup.inputs[1], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                            
                                            #Edit value of Gamma on node group
                                            AlbedoGroup.inputs["base_map Gamma Curve"].default_value = gamma_value
                                            log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                    
                                    #otherwise connect alpha from base_map like normal
                                    elif(ShaderItem.specular_mask_option != 2):
                                        if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                            log_to_file(str(ShaderItem.bitmap_list[bitm].curve_option))
                                            #log_to_file("  base 1a1")
                                            #link gamma to albedo
                                            pymat_copy.node_tree.links.new(AlbedoGroup.inputs[0], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                            pymat_copy.node_tree.links.new(AlbedoGroup.inputs[1], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                        
                                            #Edit value of Gamma on node group
                                            AlbedoGroup.inputs["base_map Gamma Curve"].default_value = gamma_value
                                            log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                        
                                        else:
                                            #log_to_file("  base 1a2")
                                            #link base_map to albedo
                                            pymat_copy.node_tree.links.new(AlbedoGroup.inputs[0], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                            pymat_copy.node_tree.links.new(AlbedoGroup.inputs[1], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                            
                                            #Edit value of Gamma on node group
                                            AlbedoGroup.inputs["base_map Gamma Curve"].default_value = gamma_value
                                            log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                            
                            elif(Shader_Type == 6 and ShaderItem.bitmap_list[bitm].type == "base_map"): #Decal use of base_map linking
                                log_to_file("  trying to link base_map")
                                if (ShaderItem.albedo_option == 0):
                                    pymat_copy.node_tree.links.new(AlbedoGroup.inputs["base_map.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                    pymat_copy.node_tree.links.new(AlbedoGroup.inputs["base_map.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                if (ShaderItem.albedo_option == 1 or ShaderItem.albedo_option == 2):
                                    #connect base_map to ALbedoVectorGroup if palletized
                                    pymat_copy.node_tree.links.new(AlbedoVectorGroup.inputs["base_map.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                           
                           
                           
                           
                                    #- a/spec node
                                    #if spec data comes from diffuse
                                    
                                    # if(ShaderItem.specular_mask_option == 1):
                                        # #log_to_file("  base 1a3")
                                        # pymat_copy.node_tree.links.new(AlbedoGroup.inputs[1], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                            #log_to_file("before detail map")
                            #DETAIL_MAP
                            if((Shader_Type == 0 or Shader_Type == 2 or Shader_Type == 4) and ShaderItem.bitmap_list[bitm].type == "detail_map"): # and ShaderGroupList[bitm + 1] == "albedo"):
                                log_to_file("  trying to link detail_map------------------")
                                #if albedo option is not constant color
                                if (ShaderItem.albedo_option != 2 and ShaderItem.albedo_option != 22 and ShaderItem.material_model_option != 0):
                                    log_to_file("  detail 0a - alebdo option is not constant color and mat model is NOT diffuse only-------------------")
                                    #- rgb node
                                    #if curve uses Gamma
                                    if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                        #link gamma to albedo
                                        #log_to_file("  detail 0b")
                                        pymat_copy.node_tree.links.new(AlbedoGroup.inputs["detail_map.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        pymat_copy.node_tree.links.new(AlbedoGroup.inputs["detail_map.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                    
                                        #Edit value of Gamma on node group
                                        AlbedoGroup.inputs["detail_map Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                    
                                    else:
                                        #link base_map to albedo
                                        log_to_file("  detail 0c linking------------------")
                                        pymat_copy.node_tree.links.new(AlbedoGroup.inputs["detail_map.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        pymat_copy.node_tree.links.new(AlbedoGroup.inputs["detail_map.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                    
                                        #Edit value of Gamma on node group
                                        AlbedoGroup.inputs["detail_map Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                    
                                    #- a/spec node
                                    #if spec data comes from diffuse
                                    # if(ShaderItem.specular_mask_option == 1):
                                        # #log_to_file("  detail 0d")
                                        # pymat_copy.node_tree.links.new(AlbedoGroup.inputs["detail_map.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                elif (ShaderItem.albedo_option != 2 and ShaderItem.material_model_option == 0):
                                    log_to_file("  detail 0b - alebdo option is not constant color and mat model is diffuse only---------------")
                                    #- rgb node
                                    #if curve uses Gamma
                                    if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                        #link gamma to albedo
                                        #log_to_file("  detail 0b")
                                        pymat_copy.node_tree.links.new(AlbedoGroup.inputs["detail_map.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        pymat_copy.node_tree.links.new(AlbedoGroup.inputs["detail_map.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                    
                                        #Edit value of Gamma on node group
                                        AlbedoGroup.inputs["detail_map Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                    
                                    else:
                                        #link base_map to albedo
                                        log_to_file("  detail 0c linking------------------")
                                        pymat_copy.node_tree.links.new(AlbedoGroup.inputs["detail_map.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        pymat_copy.node_tree.links.new(AlbedoGroup.inputs["detail_map.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                        
                                        #Edit value of Gamma on node group
                                        AlbedoGroup.inputs["detail_map Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                    #- a/spec node
                                    #if spec data comes from diffuse
                                    # if(ShaderItem.specular_mask_option == 1):
                                        # #log_to_file("  detail 0d")
                                        # pymat_copy.node_tree.links.new(AlbedoGroup.inputs["detail_map.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                
                            #DETAIL_MAP2
                            if((Shader_Type == 0 or Shader_Type == 2 or Shader_Type == 4) and ShaderItem.bitmap_list[bitm].type == "detail_map2"): # and ShaderGroupList[bitm + 1] == "albedo"):
                                log_to_file("  trying to link detail_map2")
                                #if albedo option is not constant color
                                
                                #if ((ShaderItem.albedo_option == 1 or ShaderItem.albedo_option == 5 or ShaderItem.albedo_option == 6 or ShaderItem.albedo_option == 7 or ShaderItem.albedo_option == 9) and ShaderItem.material_model_option != 0):
                                if (ShaderItem.albedo_option == 1 or ShaderItem.albedo_option == 5 or ShaderItem.albedo_option == 6 or ShaderItem.albedo_option == 7 or ShaderItem.albedo_option == 9):
                                    #log_to_file("  detail 0a")
                                    #- rgb node
                                    #if curve uses Gamma
                                    if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                        #link gamma to albedo
                                        #log_to_file("  detail 0b")
                                        pymat_copy.node_tree.links.new(AlbedoGroup.inputs["detail_map2.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        pymat_copy.node_tree.links.new(AlbedoGroup.inputs["detail_map2.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                    
                                        #Edit value of Gamma on node group
                                        AlbedoGroup.inputs["detail_map2 Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                    
                                    else:
                                        #link base_map to albedo
                                        #log_to_file("  detail 0c")
                                        pymat_copy.node_tree.links.new(AlbedoGroup.inputs["detail_map2.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        pymat_copy.node_tree.links.new(AlbedoGroup.inputs["detail_map2.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                        
                                        #Edit value of Gamma on node group
                                        AlbedoGroup.inputs["detail_map2 Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                    #- a/spec node
                                    #if spec data comes from diffuse
                                    # if(ShaderItem.specular_mask_option == 1):
                                        # #log_to_file("  detail 0d")
                                        # pymat_copy.node_tree.links.new(AlbedoGroup.inputs["detail_map.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])

                            #DETAIL_MAP3
                            if((Shader_Type == 0 or Shader_Type == 2 or Shader_Type == 4) and ShaderItem.bitmap_list[bitm].type == "detail_map3"): # and ShaderGroupList[bitm + 1] == "albedo"):
                                log_to_file("  trying to link detail_map3")
                                #if albedo option is not constant color
                                if (ShaderItem.albedo_option == 5):
                                    #log_to_file("  detail 0a")
                                    #- rgb node
                                    #if curve uses Gamma
                                    if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                        #link gamma to albedo
                                        #log_to_file("  detail 0b")
                                        pymat_copy.node_tree.links.new(AlbedoGroup.inputs["detail_map3.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        pymat_copy.node_tree.links.new(AlbedoGroup.inputs["detail_map3.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                    
                                        #Edit value of Gamma on node group
                                        AlbedoGroup.inputs["detail_map3 Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                    
                                    else:
                                        #link base_map to albedo
                                        #log_to_file("  detail 0c")
                                        pymat_copy.node_tree.links.new(AlbedoGroup.inputs["detail_map3.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        pymat_copy.node_tree.links.new(AlbedoGroup.inputs["detail_map3.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                        
                                        #Edit value of Gamma on node group
                                        AlbedoGroup.inputs["detail_map3 Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                    #- a/spec node
                                    #if spec data comes from diffuse
                                    # if(ShaderItem.specular_mask_option == 1):
                                        # #log_to_file("  detail 0d")
                                        # pymat_copy.node_tree.links.new(AlbedoGroup.inputs["detail_map.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                            #DETAIL_MAP_OVERLAY
                            if((Shader_Type == 0 or Shader_Type == 2 or Shader_Type == 4) and ShaderItem.bitmap_list[bitm].type == "detail_map_overlay"): # and ShaderGroupList[bitm + 1] == "albedo"):
                                log_to_file("  trying to link detail_map_overlay")
                                #if albedo option is not constant color
                                if (ShaderItem.albedo_option == 6):
                                    #log_to_file("  detail 0a")
                                    #- rgb node
                                    #if curve uses Gamma
                                    if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                        #link gamma to albedo
                                        #log_to_file("  detail 0b")
                                        pymat_copy.node_tree.links.new(AlbedoGroup.inputs["detail_map_overlay.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        pymat_copy.node_tree.links.new(AlbedoGroup.inputs["detail_map_overlay.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                    
                                        #Edit value of Gamma on node group
                                        AlbedoGroup.inputs["detail_map_overlay Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                    
                                    else:
                                        #link base_map to albedo
                                        #log_to_file("  detail 0c")
                                        pymat_copy.node_tree.links.new(AlbedoGroup.inputs["detail_map_overlay.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        pymat_copy.node_tree.links.new(AlbedoGroup.inputs["detail_map_overlay.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                        
                                        #Edit value of Gamma on node group
                                        AlbedoGroup.inputs["detail_map_overlay Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                    #- a/spec node
                                    #if spec data comes from diffuse
                                    # if(ShaderItem.specular_mask_option == 1):
                                        # #log_to_file("  detail 0d")
                                        # pymat_copy.node_tree.links.new(AlbedoGroup.inputs["detail_map.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])

                            #CHANGE_COLOR_MAP LINK
                            if((Shader_Type == 0 or Shader_Type == 2 or Shader_Type == 4) and ShaderItem.bitmap_list[bitm].type == "change_color_map"): # and ShaderGroupList[bitm + 1] == "albedo"):
                                log_to_file("  trying to link change_color_map")
                                #if albedo option is not constant color
                                if ((ShaderItem.albedo_option == 4 or ShaderItem.albedo_option == 3) and ShaderItem.material_model_option != 0):
                                    #log_to_file("  detail 0a")
                                    #- rgb node
                                    #if curve uses Gamma
                                    if (ShaderItem.albedo_option == 3): #two_change_color option
                                        if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                            #link gamma to albedo
                                            #log_to_file("  detail 0b")
                                            pymat_copy.node_tree.links.new(AlbedoGroup.inputs["change_color_map.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                                                                    
                                            #Edit value of Gamma on node group
                                            AlbedoGroup.inputs["change_color_map Gamma Curve"].default_value = gamma_value
                                            log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                        
                                        else:
                                            #link base_map to albedo
                                            #log_to_file("  detail 0c")
                                            pymat_copy.node_tree.links.new(AlbedoGroup.inputs["change_color_map.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                                                                        
                                            #Edit value of Gamma on node group
                                            AlbedoGroup.inputs["change_color_map Gamma Curve"].default_value = gamma_value
                                            log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                    elif(ShaderItem.albedo_option == 4): #four_change_color option
                                        if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                            #link gamma to albedo
                                            #log_to_file("  detail 0b")
                                            pymat_copy.node_tree.links.new(AlbedoGroup.inputs["change_color_map.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                            pymat_copy.node_tree.links.new(AlbedoGroup.inputs["change_color_map.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                        
                                            #Edit value of Gamma on node group
                                            AlbedoGroup.inputs["change_color_map Gamma Curve"].default_value = gamma_value
                                            log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                        
                                        else:
                                            #link base_map to albedo
                                            #log_to_file("  detail 0c")
                                            pymat_copy.node_tree.links.new(AlbedoGroup.inputs["change_color_map.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                            pymat_copy.node_tree.links.new(AlbedoGroup.inputs["change_color_map.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                            
                                            #Edit value of Gamma on node group
                                            AlbedoGroup.inputs["change_color_map Gamma Curve"].default_value = gamma_value
                                            log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                            
                            
                            #Color_Mask_Map LINK
                            if((Shader_Type == 0 or Shader_Type == 2 or Shader_Type == 4) and ShaderItem.bitmap_list[bitm].type == "color_mask_map"): # and ShaderGroupList[bitm + 1] == "albedo"):
                                log_to_file("  trying to link color_mask_map")
                                #if albedo option is not constant color
                                if ((ShaderItem.albedo_option == 8) and ShaderItem.material_model_option != 0):
                                    #log_to_file("  detail 0a")
                                    #- rgb node
                                    #if curve uses Gamma
                                    if (ShaderItem.albedo_option == 8): #color_mask
                                        if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                            #link gamma to albedo
                                            #log_to_file("  detail 0b")
                                            pymat_copy.node_tree.links.new(AlbedoGroup.inputs["color_mask_map.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                                                                    
                                            #Edit value of Gamma on node group
                                            AlbedoGroup.inputs["color_mask_map Gamma Curve"].default_value = gamma_value
                                            log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                        
                                        else:
                                            #link base_map to albedo
                                            #log_to_file("  detail 0c")
                                            pymat_copy.node_tree.links.new(AlbedoGroup.inputs["color_mask_map.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                                                                        
                                            #Edit value of Gamma on node group
                                            AlbedoGroup.inputs["color_mask_map Gamma Curve"].default_value = gamma_value
                                            log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                   
                                    #- a/spec node
                                    #if spec data comes from diffuse
                                    # if(ShaderItem.specular_mask_option == 1):
                                        # #log_to_file("  detail 0d")
                                        # pymat_copy.node_tree.links.new(AlbedoGroup.inputs["detail_map.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                            
                            
                            #material_texture LINK
                            if((Shader_Type == 0 or Shader_Type == 2 or Shader_Type == 4) and ShaderItem.bitmap_list[bitm].type == "material_texture"): # and ShaderGroupList[bitm + 1] == "albedo"):
                                log_to_file("  trying to link material_texture")
                                #if albedo option is not constant color
                                if (ShaderItem.material_model_option == 10 or ShaderItem.material_model_option == 11):
                                    #log_to_file("  detail 0a")
                                    #- rgb node
                                    #if curve uses Gamma
                                    # if (ShaderItem.albedo_option == 8): #color_mask
                                    if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                        #link gamma to albedo
                                        #log_to_file("  detail 0b")
                                        pymat_copy.node_tree.links.new(MatModelGroup.inputs["material_texture.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                                                                
                                        #Edit value of Gamma on node group
                                        MatModelGroup.inputs["material_texture Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                    
                                    else:
                                        #link base_map to albedo
                                        #log_to_file("  detail 0c")
                                        pymat_copy.node_tree.links.new(MatModelGroup.inputs["material_texture.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                                                                    
                                        #Edit value of Gamma on node group
                                        MatModelGroup.inputs["material_texture Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))

                            #spec_tint_map LINK
                            if((Shader_Type == 0 or Shader_Type == 2 or Shader_Type == 4) and ShaderItem.bitmap_list[bitm].type == "spec_tint_map"): # and ShaderGroupList[bitm + 1] == "albedo"):
                                log_to_file("  trying to link spec_tint_map")
                                #if albedo option is not constant color
                                if (ShaderItem.material_model_option == 10 or ShaderItem.material_model_option == 11):
                                    #log_to_file("  detail 0a")
                                    #- rgb node
                                    #if curve uses Gamma
                                    # if (ShaderItem.albedo_option == 8): #color_mask
                                    if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                        #link gamma to albedo
                                        #log_to_file("  detail 0b")
                                        pymat_copy.node_tree.links.new(MatModelGroup.inputs["spec_tint_map.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                                                                
                                        #Edit value of Gamma on node group
                                        MatModelGroup.inputs["spec_tint_map Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                    
                                    else:
                                        #link base_map to albedo
                                        #log_to_file("  detail 0c")
                                        pymat_copy.node_tree.links.new(MatModelGroup.inputs["spec_tint_map.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                                                                    
                                        #Edit value of Gamma on node group
                                        MatModelGroup.inputs["spec_tint_map Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))

                            #BUMP MAP
                            #log_to_file("before bump")
                            if((Shader_Type == 0 or Shader_Type == 2 or Shader_Type == 4) and ShaderItem.bitmap_list[bitm].type == "bump_map"): # and ShaderGroupList[bitm + 1] == "bump"):
                                log_to_file("  trying to link bump_map")
                                if (ShaderItem.bump_mapping_option != 0): #if bump_map option is not off    
                                    #log_to_file("  bump 0a")
                                    #if gamma exists
                                    #if(ShaderItem.bitmap_list[bitm].curve_option == 0, ShaderItem.bitmap_list[bitm].curve_option == 1, ShaderItem.bitmap_list[bitm].curve_option == 2):
                                    #    pymat_copy.node_tree.links.new(BumpGroup.inputs["bump_map"], GammaNode.outputs[0])
                                    #else: 
                                    pymat_copy.node_tree.links.new(BumpGroup.inputs["bump_map"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                            
                                    #Edit value of Gamma on node group
                                    BumpGroup.inputs["bump_map Gamma Curve"].default_value = gamma_value
                                    log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                            
                            #DETAIL BUMP MAP
                            #log_to_file("before detail bump")
                            if((Shader_Type == 0 or Shader_Type == 2 or Shader_Type == 4) and ShaderItem.bitmap_list[bitm].type == "bump_detail_map"): # and ShaderGroupList[bitm + 1] == "bump"):
                                log_to_file("  trying to link bump_detail_map")
                                if (ShaderItem.bump_mapping_option != 0 and ShaderItem.bump_mapping_option != 1): #if bump option is not off and not standard
                                    #log_to_file("  detail bump 0a")
                                    #if gamma exists
                                    #if(ShaderItem.bitmap_list[bitm].curve_option == 0, ShaderItem.bitmap_list[bitm].curve_option == 1, ShaderItem.bitmap_list[bitm].curve_option == 2):
                                    #    pymat_copy.node_tree.links.new(BumpGroup.inputs["bump_detail_map"], GammaNode.outputs[0])
                                    #else:
                                    pymat_copy.node_tree.links.new(BumpGroup.inputs["bump_detail_map"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                    
                                    BumpGroup.inputs["bump_detail_map Gamma Curve"].default_value = gamma_value
                                    log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))

                            #SELF ILLUM MAP
                            if((Shader_Type == 0 or Shader_Type == 2 or Shader_Type == 4) and ShaderItem.bitmap_list[bitm].type == "self_illum_map" and ShaderItem.self_illumination_option != 0):
                                log_to_file("  trying to link self_illum_map")
                                #if self illumination option == 1 2 5 7 8 9 10 11
                                if (ShaderItem.self_illumination_option == 1 or ShaderItem.self_illumination_option == 2 or ShaderItem.self_illumination_option == 5 or ShaderItem.self_illumination_option == 7 or ShaderItem.self_illumination_option == 8 or ShaderItem.self_illumination_option == 9 or ShaderItem.self_illumination_option == 10 or ShaderItem.self_illumination_option == 11):
                                    #if bitmap curve data uses Gamma then connect that
                                    if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                        pymat_copy.node_tree.links.new(SelfIllumGroup.inputs["self_illum_map.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                    
                                        #Edit value of Gamma on node group
                                        SelfIllumGroup.inputs["self_illum_map Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                    
                                    else:
                                        pymat_copy.node_tree.links.new(SelfIllumGroup.inputs["self_illum_map.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        
                                        #Edit value of Gamma on node group
                                        SelfIllumGroup.inputs["self_illum_map Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                            
                            #SELF ILLUM DETAIL MAP
                            if((Shader_Type == 0 or Shader_Type == 2 or Shader_Type == 4) and ShaderItem.bitmap_list[bitm].type == "self_illum_detail_map" and ShaderItem.self_illumination_option == 5):
                                log_to_file("  trying to link self_illum_detail_map")
                                #if self illumination option == 1 2 5 7 8 9 10 11
                                if (ShaderItem.self_illumination_option == 5 or ShaderItem.self_illumination_option == 10):
                                    #if bitmap curve data uses Gamma then connect that
                                    if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                        pymat_copy.node_tree.links.new(SelfIllumGroup.inputs["self_illum_detail_map.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        
                                        #Edit value of Gamma on node group
                                        SelfIllumGroup.inputs["self_illum_detail_map Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                    
                                    else:
                                        pymat_copy.node_tree.links.new(SelfIllumGroup.inputs["self_illum_detail_map.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        
                                        #Edit value of Gamma on node group
                                        SelfIllumGroup.inputs["self_illum_detail_map Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))

                            #log_to_file(str(Shader_Type) + "  " + str(ShaderItem.environment_mapping_option) + "  " + ShaderItem.bitmap_list[bitm].type)
                            #ENVIRONMENT MAP 
                            if((Shader_Type == 0 or Shader_Type == 2 or Shader_Type == 4) and (ShaderItem.environment_mapping_option != 0 and ShaderItem.environment_mapping_option != 2) and (ShaderItem.bitmap_list[bitm].type == "environment_map" or ShaderItem.bitmap_list[bitm].type == "flat_environment_map")):
                                log_to_file("  trying to link environment_map")
                                log_to_file("bitm: " + str(bitm))
                                log_to_file(EnvTextureNodeList)
                                pymat_copy.node_tree.links.new(EnvGroup.inputs["environment_map.rgb"], EnvTextureNodeList[env_tex_index + 1].outputs["Color"])
                                pymat_copy.node_tree.links.new(EnvGroup.inputs["environment_map.a"], EnvTextureNodeList[env_tex_index + 2].outputs["Color"])
                                pymat_copy.node_tree.links.new(EnvTextureNodeList[env_tex_index + 1].inputs["Vector"], EnvReflGroup.outputs["Vector"])
                                pymat_copy.node_tree.links.new(EnvTextureNodeList[env_tex_index + 2].inputs["Vector"], EnvReflGroup.outputs["Vector"])
                                EnvReflGroup

                                #read library maybe for unknown curve values?
                                #EnvGroup.inputs["bump_map Gamma Curve"].default_value = gamma_value
                            
                            #ALPHA_TEST_MAP
                            if((Shader_Type == 0 or Shader_Type == 2 or Shader_Type == 4) and ShaderItem.alpha_test_option != 0 and ShaderItem.bitmap_list[bitm].type == "alpha_test_map" and (ShaderItem.alpha_test_option == 1 or ShaderItem.specular_mask_option == 2)):
                                try:
                                    # Get the image data from the Image Texture Node
                                    image_data = ImageTextureNodeList[bitm + 1].image

                                    # Convert the pixels to a NumPy array
                                    pixels = np.array(image_data.pixels[:])

                                    # Reshape the array to separate the RGBA channels
                                    pixels = pixels.reshape((-1, 4))

                                    # Check if all alpha values are 1
                                    all_alpha_one = np.all(pixels[:, 3] == 1.0)

                                    # Connect the appropriate output
                                    if all_alpha_one:
                                        pymat_copy.node_tree.links.new(AlphaTestGroup.inputs["alpha_test_map.a"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                    else:
                                        pymat_copy.node_tree.links.new(AlphaTestGroup.inputs["alpha_test_map.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])     
                                except Exception:
                                    print("There was a bitmap curve data error! Not normal, please look into it.")

                            #specular_map
                            if((Shader_Type == 0 or Shader_Type == 2 or Shader_Type == 4) and ShaderItem.bitmap_list[bitm].type == "specular_map"): # and ShaderGroupList[bitm + 1] == "albedo"):
                                log_to_file("  trying to link specular_map")
                                #if albedo option is not constant color
                                
                                #if ((ShaderItem.albedo_option == 1 or ShaderItem.albedo_option == 5 or ShaderItem.albedo_option == 6 or ShaderItem.albedo_option == 7 or ShaderItem.albedo_option == 9) and ShaderItem.material_model_option != 0):
                                if (ShaderItem.material_model_option == 6):
                                    #log_to_file("  detail 0a")
                                    #- rgb node
                                    #if curve uses Gamma
                                    if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                        #link gamma to albedo
                                        #log_to_file("  detail 0b")
                                        pymat_copy.node_tree.links.new(MatModelGroup.inputs["specular_map.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        pymat_copy.node_tree.links.new(MatModelGroup.inputs["specular_map.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                    
                                        #Edit value of Gamma on node group
                                        MatModelGroup.inputs["specular_map Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                    
                                    else:
                                        #link base_map to albedo
                                        #log_to_file("  detail 0c")
                                        pymat_copy.node_tree.links.new(MatModelGroup.inputs["specular_map.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        pymat_copy.node_tree.links.new(MatModelGroup.inputs["specular_map.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                        
                                        #Edit value of Gamma on node group
                                        MatModelGroup.inputs["specular_map Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                            
                            #occlusion_parameter_map
                            if((Shader_Type == 0 or Shader_Type == 2 or Shader_Type == 4) and ShaderItem.bitmap_list[bitm].type == "occlusion_parameter_map"): 
                                log_to_file("  trying to link occlusion_parameter_map")
                                #if albedo option is not constant color
                                
                                #if ((ShaderItem.albedo_option == 1 or ShaderItem.albedo_option == 5 or ShaderItem.albedo_option == 6 or ShaderItem.albedo_option == 7 or ShaderItem.albedo_option == 9) and ShaderItem.material_model_option != 0):
                                if (ShaderItem.material_model_option == 6):
                                    #log_to_file("  detail 0a")
                                    #- rgb node
                                    #if curve uses Gamma
                                    if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                        #link gamma to albedo
                                        #log_to_file("  detail 0b")
                                        pymat_copy.node_tree.links.new(MatModelGroup.inputs["occlusion_parameter_map.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        #pymat_copy.node_tree.links.new(MatModelGroup.inputs["occlusion_parameter_map.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                    
                                        #Edit value of Gamma on node group
                                        MatModelGroup.inputs["occlusion_parameter_map Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                    
                                    else:
                                        #link base_map to albedo
                                        #log_to_file("  detail 0c")
                                        pymat_copy.node_tree.links.new(MatModelGroup.inputs["occlusion_parameter_map.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        #pymat_copy.node_tree.links.new(MatModelGroup.inputs["occlusion_parameter_map.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                        
                                        #Edit value of Gamma on node group
                                        MatModelGroup.inputs["occlusion_parameter_map Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))

                            
                            #subsurface_map
                            if((Shader_Type == 0 or Shader_Type == 2 or Shader_Type == 4) and ShaderItem.bitmap_list[bitm].type == "subsurface_map"): # and ShaderGroupList[bitm + 1] == "albedo"):
                                log_to_file("  trying to link subsurface_map")
                                #if albedo option is not constant color
                                
                                #if ((ShaderItem.albedo_option == 1 or ShaderItem.albedo_option == 5 or ShaderItem.albedo_option == 6 or ShaderItem.albedo_option == 7 or ShaderItem.albedo_option == 9) and ShaderItem.material_model_option != 0):
                                if (ShaderItem.material_model_option == 6):
                                    #log_to_file("  detail 0a")
                                    #- rgb node
                                    #if curve uses Gamma
                                    if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                        #link gamma to albedo
                                        #log_to_file("  detail 0b")
                                        pymat_copy.node_tree.links.new(MatModelGroup.inputs["subsurface_map.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        pymat_copy.node_tree.links.new(MatModelGroup.inputs["subsurface_map.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                    
                                        #Edit value of Gamma on node group
                                        MatModelGroup.inputs["subsurface_map Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                    
                                    else:
                                        #link base_map to albedo
                                        #log_to_file("  detail 0c")
                                        pymat_copy.node_tree.links.new(MatModelGroup.inputs["subsurface_map.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        pymat_copy.node_tree.links.new(MatModelGroup.inputs["subsurface_map.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                        
                                        #Edit value of Gamma on node group
                                        MatModelGroup.inputs["subsurface_map Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))

                            
                            
                            #transparence_map
                            if((Shader_Type == 0 or Shader_Type == 2 or Shader_Type == 4) and ShaderItem.bitmap_list[bitm].type == "transparence_map"): # and ShaderGroupList[bitm + 1] == "albedo"):
                                log_to_file("  trying to link transparence_map")
                                #if albedo option is not constant color
                                
                                #if ((ShaderItem.albedo_option == 1 or ShaderItem.albedo_option == 5 or ShaderItem.albedo_option == 6 or ShaderItem.albedo_option == 7 or ShaderItem.albedo_option == 9) and ShaderItem.material_model_option != 0):
                                if (ShaderItem.material_model_option == 6):
                                    #log_to_file("  detail 0a")
                                    #- rgb node
                                    #if curve uses Gamma
                                    if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                        #link gamma to albedo
                                        #log_to_file("  detail 0b")
                                        pymat_copy.node_tree.links.new(MatModelGroup.inputs["transparence_map.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        pymat_copy.node_tree.links.new(MatModelGroup.inputs["transparence_map.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                    
                                        #Edit value of Gamma on node group
                                        MatModelGroup.inputs["transparence_map Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                    
                                    else:
                                        #link base_map to albedo
                                        #log_to_file("  detail 0c")
                                        pymat_copy.node_tree.links.new(MatModelGroup.inputs["transparence_map.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        pymat_copy.node_tree.links.new(MatModelGroup.inputs["transparence_map.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                        
                                        #Edit value of Gamma on node group
                                        MatModelGroup.inputs["transparence_map Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))

                            #PALLETE
                            if((Shader_Type == 6) and ShaderItem.bitmap_list[bitm].type == "pallete"):
                                log_to_file("  trying to link pallete")
                                #if albedo option is not constant color
                                if (ShaderItem.albedo_option == 1): #palletized
                                    #log_to_file("  detail 0a")
                                    #- rgb node
                                    #if curve uses Gamma
                                    if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                        #link gamma to albedo
                                        #log_to_file("  detail 0b")
                                        
                                        pymat_copy.node_tree.links.new(ImageTextureNodeList[bitm + 1].inputs["Vector"], AlbedoVectorGroup.outputs["Vector"])
                                        
                                        pymat_copy.node_tree.links.new(AlbedoGroup.inputs["pallete.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        pymat_copy.node_tree.links.new(AlbedoGroup.inputs["pallete.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                    
                                        #Edit value of Gamma on node group
                                        AlbedoGroup.inputs["pallete Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                    
                                    else:
                                        #link base_map to albedo
                                        #log_to_file("  detail 0c")
                                        pymat_copy.node_tree.links.new(ImageTextureNodeList[bitm + 1].inputs["Vector"], AlbedoVectorGroup.outputs["Vector"])
                                        
                                        pymat_copy.node_tree.links.new(AlbedoGroup.inputs["pallete.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        pymat_copy.node_tree.links.new(AlbedoGroup.inputs["pallete.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                    
                                        #Edit value of Gamma on node group
                                        AlbedoGroup.inputs["pallete Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                
                                elif (ShaderItem.albedo_option == 2): #palletized_plus_alpha
                                    #log_to_file("  detail 0a")
                                    #- rgb node
                                    #if curve uses Gamma
                                    if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                        #link gamma to albedo
                                        #log_to_file("  detail 0b")
                                        
                                        pymat_copy.node_tree.links.new(ImageTextureNodeList[bitm + 1].inputs["Vector"], AlbedoVectorGroup.outputs["Vector"])
                                        
                                        pymat_copy.node_tree.links.new(AlbedoGroup.inputs["pallete.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])                        
                                    
                                        #Edit value of Gamma on node group
                                        AlbedoGroup.inputs["pallete Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                    
                                    else:
                                        #link base_map to albedo
                                        #log_to_file("  detail 0c")
                                        pymat_copy.node_tree.links.new(ImageTextureNodeList[bitm + 1].inputs["Vector"], AlbedoVectorGroup.outputs["Vector"])
                                        
                                        pymat_copy.node_tree.links.new(AlbedoGroup.inputs["pallete.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                    
                                        #Edit value of Gamma on node group
                                        AlbedoGroup.inputs["pallete Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                    #- a/spec node
                                    #if spec data comes from diffuse
                                    # if(ShaderItem.specular_mask_option == 1):
                                        # #log_to_file("  detail 0d")
                                        # pymat_copy.node_tree.links.new(AlbedoGroup.inputs["detail_map.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                            
                            #ALPHA_MAP
                            if((Shader_Type == 6) and ShaderItem.bitmap_list[bitm].type == "alpha_map"):
                                log_to_file("  trying to link alpha_map")
                                #if albedo option is not constant color
                                if (ShaderItem.albedo_option == 2): #palletized_plus_alpha
                                    #log_to_file("  detail 0a")
                                    #- rgb node
                                    #if curve uses Gamma
                                    if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                        #link gamma to albedo
                                        #log_to_file("  detail 0b")
                                        
                                        pymat_copy.node_tree.links.new(AlbedoGroup.inputs["alpha_map.a"], ImageTextureNodeList[bitm + 1].outputs["Color"])                        
                                    
                                        #Edit value of Gamma on node group
                                        AlbedoGroup.inputs["pallete Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                    
                                    else:
                                        #link base_map to albedo
                                        #log_to_file("  detail 0c")
                                        
                                        pymat_copy.node_tree.links.new(AlbedoGroup.inputs["alpha_map.a"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                    
                                        #Edit value of Gamma on node group
                                        AlbedoGroup.inputs["pallete Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                            
                            
                            #SPECULAR_MASK_TEXTURE
                            if((Shader_Type == 0 or Shader_Type == 4) and ShaderItem.bitmap_list[bitm].type == "specular_mask_texture" and ShaderItem.specular_mask_option == 2 and ShaderItem.albedo_option != 2):
                                pymat_copy.node_tree.links.new(AlbedoGroup.inputs["base_map.a/specular_mask"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])                
                            
                            #Alpha_blend
                            if((Shader_Type == 0 or Shader_Type == 4) and ShaderItem.bitmap_list[bitm].type == "base_map" and ShaderItem.blend_mode_option == 3):
                                pymat_copy.node_tree.links.new(AlphaBlendGroup.inputs["base_map.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])                 
                            elif((Shader_Type == 0 or Shader_Type == 4) and ShaderItem.bitmap_list[bitm].type == "specular_mask_texture" and ShaderItem.blend_mode_option == 5):
                                pymat_copy.node_tree.links.new(AlphaBlendGroup.inputs["base_map.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])                 
                            
                            
                            #######################
                            # .shader_terrain files
                            #######################
                            
                            
                            if(Shader_Type == 1):
                                #MATERIAL 0 LINK
                                if(ShaderItem.bitmap_list[bitm].type == "base_map_m_0" and ShaderItem.material_0_option != 2):
                                    #log_to_file("  trying to link base_map_m_0")
                                    #- rgb node
                                    #if curve uses Gamma
                                    if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                        #link gamma to albedo
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["base_map_m_0.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["base_map_m_0.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                        
                                        #Edit value of Gamma on node group
                                        TerrainGroup.inputs["base_map_m_0 Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                        
                                    else:
                                        #link base_map_m_0 to terrain group m0
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["base_map_m_0.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["base_map_m_0.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                        
                                        #Edit value of Gamma on node group
                                        TerrainGroup.inputs["base_map_m_0 Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                        
                                elif(ShaderItem.bitmap_list[bitm].type == "detail_map_m_0" and ShaderItem.material_0_option != 2):
                                    #log_to_file("  trying to link detail_map_m_0")
                                    #- rgb node
                                    #if curve uses Gamma
                                    if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                        #link gamma to albedo
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["detail_map_m_0.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["detail_map_m_0.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                        
                                        #Edit value of Gamma on node group
                                        TerrainGroup.inputs["detail_map_m_0 Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                        
                                    else:
                                        #link detail_map_m_0 to terrain group m0
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["detail_map_m_0.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["detail_map_m_0.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                        
                                        #Edit value of Gamma on node group
                                        TerrainGroup.inputs["detail_map_m_0 Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                        
                                elif(ShaderItem.bitmap_list[bitm].type == "bump_map_m_0" and ShaderItem.material_0_option != 2):
                                    #log_to_file("  trying to link bump_map_m_0")
                                    #- rgb node
                                    #if curve uses Gamma
                                    if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                        #link gamma to albedo
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["bump_map_m_0"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        
                                        #Edit value of Gamma on node group
                                        TerrainGroup.inputs["bump_map_m_0 Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                        
                                    else:
                                        #link bump_map_m_0 to terrain group m0
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["bump_map_m_0"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        
                                        #Edit value of Gamma on node group
                                        TerrainGroup.inputs["bump_map_m_0 Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                        
                                elif(ShaderItem.bitmap_list[bitm].type == "detail_bump_m_0" and ShaderItem.material_0_option != 2):
                                    #log_to_file("  trying to link detail_bump_m_0")
                                    #- rgb node
                                    #if curve uses Gamma
                                    if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                        #link gamma to albedo
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["detail_bump_m_0"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        
                                        #Edit value of Gamma on node group
                                        TerrainGroup.inputs["detail_bump_m_0 Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                        
                                    else:
                                        #link detail_bump_m_0 to terrain group m0
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["detail_bump_m_0"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        
                                        #Edit value of Gamma on node group
                                        TerrainGroup.inputs["detail_bump_m_0 Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                
                                #MATERIAL 1 LINK
                                if(ShaderItem.bitmap_list[bitm].type == "base_map_m_1" and ShaderItem.material_1_option != 2):
                                    #log_to_file("  trying to link base_map_m_1")
                                    #- rgb node
                                    #if curve uses Gamma
                                    if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                        #link gamma to albedo
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["base_map_m_1.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["base_map_m_1.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                        
                                        #Edit value of Gamma on node group
                                        TerrainGroup.inputs["base_map_m_1 Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                        
                                    else:
                                        #link base_map_m_1 to terrain group M1
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["base_map_m_1.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["base_map_m_1.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                        
                                        #Edit value of Gamma on node group
                                        TerrainGroup.inputs["base_map_m_1 Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                        
                                elif(ShaderItem.bitmap_list[bitm].type == "detail_map_m_1" and ShaderItem.material_1_option != 2):
                                    #log_to_file("  trying to link detail_map_m_1")
                                    #- rgb node
                                    #if curve uses Gamma
                                    if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                        #link gamma to albedo
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["detail_map_m_1.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["detail_map_m_1.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                        
                                        #Edit value of Gamma on node group
                                        TerrainGroup.inputs["detail_map_m_1 Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                        
                                    else:
                                        #link detail_map_m_1 to terrain group M1
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["detail_map_m_1.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["detail_map_m_1.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                        
                                        #Edit value of Gamma on node group
                                        TerrainGroup.inputs["detail_map_m_1 Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                        
                                elif(ShaderItem.bitmap_list[bitm].type == "bump_map_m_1" and ShaderItem.material_1_option != 2):
                                    #log_to_file("  trying to link bump_map_m_1")
                                    #- rgb node
                                    #if curve uses Gamma
                                    if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                        #link gamma to albedo
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["bump_map_m_1"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        
                                        #Edit value of Gamma on node group
                                        TerrainGroup.inputs["bump_map_m_1 Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                    else:
                                        #link bump_map_m_1 to terrain group M1
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["bump_map_m_1"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        
                                        #Edit value of Gamma on node group
                                        TerrainGroup.inputs["bump_map_m_1 Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                        
                                elif(ShaderItem.bitmap_list[bitm].type == "detail_bump_m_1" and ShaderItem.material_1_option != 2):
                                    #log_to_file("  trying to link detail_bump_m_1")
                                    #- rgb node
                                    #if curve uses Gamma
                                    if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                        #link gamma to albedo
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["detail_bump_m_1"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        
                                        #Edit value of Gamma on node group
                                        TerrainGroup.inputs["detail_bump_m_1 Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                        
                                    else:
                                        #link detail_bump_m_1 to terrain group M1
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["detail_bump_m_1"], ImageTextureNodeList[bitm + 1].outputs["Color"])  

                                        #Edit value of Gamma on node group
                                        TerrainGroup.inputs["detail_bump_m_1 Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                        

                                #MATERIAL 2 LINK
                                if(ShaderItem.bitmap_list[bitm].type == "base_map_m_2" and ShaderItem.material_2_option != 2):
                                    #log_to_file("  trying to link base_map_m_2")
                                    #- rgb node
                                    #if curve uses Gamma
                                    if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                        #link gamma to albedo
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["base_map_m_2.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["base_map_m_2.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                        
                                        #Edit value of Gamma on node group
                                        TerrainGroup.inputs["base_map_m_2 Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                        
                                    else:
                                        #link base_map_m_2 to terrain group M2
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["base_map_m_2.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["base_map_m_2.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                        
                                        #Edit value of Gamma on node group
                                        TerrainGroup.inputs["base_map_m_2 Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                        
                                elif(ShaderItem.bitmap_list[bitm].type == "detail_map_m_2" and ShaderItem.material_2_option != 2):
                                    #log_to_file("  trying to link detail_map_m_2")
                                    #- rgb node
                                    #if curve uses Gamma
                                    if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                        #link gamma to albedo
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["detail_map_m_2.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["detail_map_m_2.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                        
                                        #Edit value of Gamma on node group
                                        TerrainGroup.inputs["detail_map_m_2 Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                        
                                    else:
                                        #link detail_map_m_2 to terrain group M2
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["detail_map_m_2.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["detail_map_m_2.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                        
                                        #Edit value of Gamma on node group
                                        TerrainGroup.inputs["detail_map_m_2 Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                        
                                elif(ShaderItem.bitmap_list[bitm].type == "bump_map_m_2" and ShaderItem.material_2_option != 2):
                                    #log_to_file("  trying to link bump_map_m_2")
                                    #- rgb node
                                    #if curve uses Gamma
                                    if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                        #link gamma to albedo
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["bump_map_m_2"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        
                                        #Edit value of Gamma on node group
                                        TerrainGroup.inputs["bump_map_m_2 Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                        
                                    else:
                                        #link bump_map_m_2 to terrain group M2
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["bump_map_m_2"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        
                                        #Edit value of Gamma on node group
                                        TerrainGroup.inputs["bump_map_m_2 Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                        
                                elif(ShaderItem.bitmap_list[bitm].type == "detail_bump_m_2" and ShaderItem.material_2_option != 2):
                                    #log_to_file("  trying to link detail_bump_m_2")
                                    #- rgb node
                                    #if curve uses Gamma
                                    if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                        #link gamma to albedo
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["detail_bump_m_2"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        
                                        #Edit value of Gamma on node group
                                        TerrainGroup.inputs["detail_bump_m_2 Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                        
                                    else:
                                        #link detail_bump_m_2 to terrain group M2
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["detail_bump_m_2"], ImageTextureNodeList[bitm + 1].outputs["Color"]) 
                                        
                                        #Edit value of Gamma on node group
                                        TerrainGroup.inputs["detail_bump_m_2 Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                        

                                #MATERIAL 3 LINK
                                if(ShaderItem.bitmap_list[bitm].type == "base_map_m_3" and ShaderItem.material_3_option != 0):
                                    #log_to_file("  trying to link base_map_m_3")
                                    #- rgb node
                                    #if curve uses Gamma
                                    if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                        #link gamma to albedo
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["base_map_m_3.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["base_map_m_3.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                        
                                        #Edit value of Gamma on node group
                                        TerrainGroup.inputs["base_map_m_3 Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                        
                                    else:
                                        #link base_map_m_3 to terrain group M3
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["base_map_m_3.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["base_map_m_3.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                        
                                        #Edit value of Gamma on node group
                                        TerrainGroup.inputs["base_map_m_3 Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                        
                                elif(ShaderItem.bitmap_list[bitm].type == "detail_map_m_3" and ShaderItem.material_3_option != 0):
                                    #log_to_file("  trying to link detail_map_m_3")
                                    #- rgb node
                                    #if curve uses Gamma
                                    if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                        #link gamma to albedo
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["detail_map_m_3.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["detail_map_m_3.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                        
                                        #Edit value of Gamma on node group
                                        TerrainGroup.inputs["detail_map_m_3 Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                        
                                    else:
                                        #link detail_map_m_3 to terrain group M3
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["detail_map_m_3.rgb"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["detail_map_m_3.a"], ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                        
                                        #Edit value of Gamma on node group
                                        TerrainGroup.inputs["detail_map_m_3 Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                        
                                elif(ShaderItem.bitmap_list[bitm].type == "bump_map_m_3" and ShaderItem.material_3_option != 0):
                                    #log_to_file("  trying to link bump_map_m_3")
                                    #- rgb node
                                    #if curve uses Gamma
                                    if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                        #link gamma to albedo
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["bump_map_m_3"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        
                                        #Edit value of Gamma on node group
                                        TerrainGroup.inputs["bump_map_m_3 Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                        
                                    else:
                                        #link bump_map_m_3 to terrain group M3
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["bump_map_m_3"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        
                                        #Edit value of Gamma on node group
                                        TerrainGroup.inputs["bump_map_m_3 Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                        
                                elif(ShaderItem.bitmap_list[bitm].type == "detail_bump_m_3" and ShaderItem.material_3_option != 0):
                                    #log_to_file("  trying to link detail_bump_m_3" and ShaderItem.material_3_option != 0)
                                    #- rgb node
                                    #if curve uses Gamma
                                    if(ShaderItem.bitmap_list[bitm].curve_option == 1 or ShaderItem.bitmap_list[bitm].curve_option == 2):
                                        #link gamma to albedo
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["detail_bump_m_3"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        
                                        #Edit value of Gamma on node group
                                        TerrainGroup.inputs["detail_bump_m_3 Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                        
                                    else:
                                        #link detail_bump_m_3 to terrain group M3
                                        pymat_copy.node_tree.links.new(TerrainGroup.inputs["detail_bump_m_3"], ImageTextureNodeList[bitm + 1].outputs["Color"])
                                        
                                        #Edit value of Gamma on node group
                                        TerrainGroup.inputs["detail_bump_m_3 Gamma Curve"].default_value = gamma_value
                                        log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))

                            
                                                #########################
                                                #SEPARATE COLOR NODE LINK
                                                #########################      
                                                # NOW BLEND TEXTURE LINK
                            
                            if(ShaderItem.bitmap_list[bitm].type == "blend_map" and Shader_Type == 1):
                                pymat_copy.node_tree.links.new(TerrainGroup.inputs["blend_map.rgb"],ImageTextureNodeList[bitm + 1].outputs["Color"])
                                pymat_copy.node_tree.links.new(TerrainGroup.inputs["blend_map.a"],ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                
                                #Edit value of Gamma on node group
                                TerrainGroup.inputs["blend_map Gamma Curve"].default_value = gamma_value
                                log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
                                
                                #pymat_copy.node_tree.links.new(SeparateColorGroup.inputs["Color"],ImageTextureNodeList[bitm + 1].outputs["Color"])
                                
                               # if(ShaderItem.material_3_option != 0): #if material 3 is not off
                                    #pymat_copy.node_tree.links.new(TerrainGroupM3.inputs["blend_map_channel"],ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                            # #LINK TEXTURES TO GROUPS
                            # if (ShaderItem.albedo_option == 2): #albedo option = constant color
                                # pymat_copy.node_tree.links.new(AlbedoGroup.inputs["albedo.rgb"], GammaNode.outputs["Color"])
                            elif(ShaderItem.bitmap_list[bitm].type == "blend_map" and Shader_Type != 1):
                                pymat_copy.node_tree.links.new(AlbedoGroup.inputs["blend_map.rgb"],ImageTextureNodeList[bitm + 1].outputs["Color"])
                                #pymat_copy.node_tree.links.new(AlbedoGroup.inputs["blend_map.a"],ImageTextureNodeList[bitm + 1].outputs["Alpha"])
                                
                                #Edit value of Gamma on node group
                                AlbedoGroup.inputs["blend_map Gamma Curve"].default_value = gamma_value
                                log_to_file("Changing Gamma Value of " + ShaderItem.bitmap_list[bitm].type + " to: " + str(gamma_value))
        
                        
                        #reset MIRROR_PADDING
                        MIRROR_PADDING = 0
                        
                        #add extra padding if mirror node was made
                        if(mirror_node_made == 1):
                            MIRROR_PADDING = TEXTURE_GAMMA_HORIZONTAL_PLACEMENT
                            
                            
                        if (ImageTextureNodeList[bitm + 1] is None and ImageTextureNodeList[bitm + 1].type != "environment_map"):
                            #delete the NoneType blank image texture
                            pymat_copy.node_tree.nodes.remove(ImageTextureNodeList[bitm + 1])
                            
                            last_texture_x = before_no_tex_x
                            last_texture_y = before_no_tex_y
                    else:
                        log_to_file(ShaderItem.bitmap_list[bitm].type + " is disabled") 
                        
                        #delete the NoneType blank image texture
                        pymat_copy.node_tree.nodes.remove(ImageTextureNodeList[bitm + 1])
                        
                        last_texture_x = before_no_tex_x
                        last_texture_y = before_no_tex_y

                ShaderList.append(ShaderItem)
                ShaderList_Index = ShaderList_Index + 1
                
        #Report the progress to the user
        progress = (idx / total_mats) * 100
        yield progress
       
        
        #wm.progress_end()
    # #Enable and activate Node Arrange
    # bpy.ops.preferences.addon_enable(module = "node_arrange")
    # #bpy.ops.node.button()
    # for area in bpy.context.screen.areas:
        # if area.type == 'NODE_EDITOR':
            # for region in area.regions:
                # if region.type == 'WINDOW':
                    # ctx = bpy.context.copy()
                    # ctx['area'] = area
                    # ctx['region'] = region
                    # bpy.ops.node.button(ctx, "INVOKE_DEFAULT")
        
    # bpy.ops.node.button()


#classes for the add-on





#Add-On Properties
class CR4BAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__
    export_path: bpy.props.StringProperty(
        name="Halo Asset Export Path",
        subtype='FILE_PATH'
    )
    node_group_file: bpy.props.StringProperty(
        name="Shader .blend File",
        subtype='FILE_PATH'
    )
    halo3_tag_path: bpy.props.StringProperty(
        name="Halo 3 Tags",
        subtype='FILE_PATH'
    )
    odst_tag_path: bpy.props.StringProperty(
        name="Halo 3: ODST Tags",
        subtype='FILE_PATH'
    )
    reach_tag_path: bpy.props.StringProperty(
        name="Halo Reach Tags",
        subtype='FILE_PATH'
    )
    py360convert_path: bpy.props.StringProperty(
        name="Python_Modules",
        subtype='DIR_PATH'
    )
    reclaimer_path: bpy.props.StringProperty(
        name="Reclaimer CLI",
        subtype='FILE_PATH'
    )
    haloce_map_path: bpy.props.StringProperty(
        name="Halo CE Maps",
        subtype='FILE_PATH'
    )
    halo2_map_path: bpy.props.StringProperty(
        name="Halo 2 Maps",
        subtype='FILE_PATH'
    )
    halo3_map_path: bpy.props.StringProperty(
        name="Halo 3 Maps",
        subtype='FILE_PATH'
    )
    halo3odst_map_path: bpy.props.StringProperty(
        name="Halo 3: ODST Maps",
        subtype='FILE_PATH'
    )
    haloreach_map_path: bpy.props.StringProperty(
        name="Halo Reach Maps",
        subtype='FILE_PATH'
    )
    halo4_map_path: bpy.props.StringProperty(
        name="Halo 4 Maps",
        subtype='FILE_PATH'
    )
    halo5_map_path: bpy.props.StringProperty(
        name="Halo 5 Deploy",
        subtype='FILE_PATH'
    )
    
    def draw(self, context):
        layout = self.layout
        layout.row().label(text="Directory of ripped Halo Assets:")
        layout.row().label(text="NOTE: Save the .blend files you want to use CR4B Tool on here", icon="INFO")
        layout.row().prop(self, "export_path")
        layout.row().label(text="Directory CR4BTool_shades.blend file:")
        layout.row().prop(self, "node_group_file")
        layout.row().label(text="Directory of Python_Modules folder:")
        layout.row().prop(self, "py360convert_path")
        layout.row().label(text="Directory Locations of Tag Folders:")
        layout.row().prop(self, "halo3_tag_path")
        layout.row().prop(self, "odst_tag_path")
        layout.row().prop(self, "reach_tag_path")
        
        layout.row().label(text="Directory Location of the Reclaimer CLI Folder:")
        layout.row().prop(self, "reclaimer_path")
        
        layout.row().label(text="Directory Locations of .map files for each game:")
        layout.row().prop(self, "haloce_map_path")
        layout.row().prop(self, "halo2_map_path")
        layout.row().prop(self, "halo3_map_path")
        layout.row().prop(self, "halo3odst_map_path")
        layout.row().prop(self, "haloreach_map_path")
        layout.row().prop(self, "halo4_map_path")
        layout.row().prop(self, "halo5_map_path")

class ProgressBarPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_progress_bar"
    bl_label = "Progress Bar"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    
    def draw(self, context):
        layout = self.layout
        
        # Create a progress bar in the center of the panel
        progress = context.window_manager.progress
        
        row = layout.row()
        row.label(text="Setting Up Materials:")
        row.prop(progress, "value", text="")

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

class CR4BProgressUpdater(bpy.types.Operator):
    bl_idname = "object.cr4b_progress_updater"
    bl_label = "CR4B Progress Updater"

    def modal(self, context, event):
        if event.type == 'TIMER':
            progress = context.scene.cr4b_progress_temp
            context.scene.cr4b_progress = progress
            return {'FINISHED'}

        return {'PASS_THROUGH'}

    def execute(self, context):
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}



#check if the given texture exists  
def texture_exists(texture_path):
    if os.path.isfile(texture_path):
        return True
    else:
        return False

#check to see if a texture was not extracted that is needed by CR4B Tool - do this before trying to process each image into the scene maybe
def handle_missing_texture(bitmap_path, texture_path):
    #bitmap_path is tags/level/multi/zanzibar/ etc etc
    #texture_path is where it was looking for the texture originally (might need to remove the extension)
    
    if(texture_exists(texture_path + bpy.context.scene.image_format_dropdown) == True):
        log_to_file("Texture Exists!")
    else:
        log_to_file("Texture not found. Trying to create a new one.")
        
        log_to_file("Running Tool.exe")
        #Run Tool.exe to create texture
        tool_ran_outcome = run_exe_tool(bitmap_path,texture_path)
        
        if (tool_ran_outcome == 0): #failed
            log_to_file("Tool.exe had an issue creating texture")
        
        elif (tool_ran_outcome == 2): #equirectangular map created
            log_to_file("Created Equirectangular map from cubes!")
            
        else: #created tga texture
            
            #edit the filename of the newly created texture
            
            
            #create output path location to target
            output_path = os.path.dirname(texture_path) + "/"
            
            log_to_file("Converting tga image")
            #convert the texture to needed format
            
           
            
            format = (bpy.context.scene.image_format_dropdown).replace(".","") #replace . with nothing
            convert_image_format(texture_path + ".tga", output_path, format)
        
#convert images as needed using the PIL library
def convert_image_format(input_image_path, output_path, output_format):
    from PIL import Image
    
    # Open the image file
    img = Image.open(input_image_path)
    # Create the new filename
    output_file_path = os.path.join(output_path, os.path.splitext(os.path.basename(input_image_path))[0] + '.' + output_format)
    # Save the image in the new format
    img.save(output_file_path)
    log_to_file(f'Saved {output_file_path}')
    # Close the image file
    img.close()
    # Remove the original image file
    os.remove(input_image_path)
    log_to_file(f'Removed {input_image_path}')



#Run tool.exe to convert missing .bitmaps
def run_exe_tool(bitmap_path, path_out):
    # depending on the toggle for the game choose the path for tool.exe
    if(bpy.context.scene.tag_dropdown == "Halo 3"):
        Tool_Root = (bpy.context.preferences.addons[__name__].preferences.halo3_tag_path).replace('H3EK\\tags\\', 'H3EK\\tool.exe')
        Tags_Root = bpy.context.preferences.addons[__name__].preferences.halo3_tag_path
    elif (bpy.context.scene.tag_dropdown == "Halo 3: ODST"):  
        Tool_Root = bpy.context.preferences.addons[__name__].preferences.odst_tag_path.replace('H3ODSTEK\\tags\\', 'H3ODSTEK\\tool.exe')
        Tags_Root = bpy.context.preferences.addons[__name__].preferences.odst_tag_path
    elif (bpy.context.scene.tag_dropdown == "Halo Reach"):
        Tool_Root = bpy.context.preferences.addons[__name__].preferences.reach_tag_path.replace('HREK\\tags\\', 'HREK\\tool.exe')
        Tags_Root = bpy.context.preferences.addons[__name__].preferences.reach_tag_path
    else:
        log_to_file("Error with Tag option property")
    
    # create accurate bitmap path with MAIN DIRECTORY_PATH + bitmap_path
    full_bitmap_path = os.path.normpath(Tags_Root + bitmap_path)
    path_out = os.path.normpath(path_out)

    # Subtract tool root from full bitmap path to get the relative path
    relative_bitmap_path = (os.path.relpath(full_bitmap_path, os.path.dirname(Tool_Root))).replace("tags\\", "")
    
    filename = os.path.basename(path_out)
    tga_path = os.path.dirname(path_out) + "/"
    
    # Check if the directory exists, and if not, create it
    os.makedirs(tga_path, exist_ok=True)

    # create the command string
    cmd = f'tool export-bitmap-tga "{relative_bitmap_path}" "{tga_path}"'

    # Remember the current directory
    original_dir = os.getcwd()

    try:
        # Change to the directory of the tool
        os.chdir(os.path.dirname(Tool_Root))

        # run the command
        log_to_file(f'Running command: {cmd}')
        os.system(cmd)
        #bpy.ops.wm.console_toggle()
        
    except Exception as e:
        log_to_file(f'The tool caused an error: {str(e)}')

    finally:
        # Change back to the original directory
        os.chdir(original_dir)

        # Rename the file to get rid of _00_00 UNTIL MAYBE LATER WE WANT TO DO VARIATIONS OF THE BITMAPS LIKE AN ARRAY
        versions = ["_00_00", "_00_01", "_00_02", "_00_03", "_00_04", "_00_05"]
        image_paths = [tga_path + filename + version + ".tga" for version in versions]
        if all(os.path.exists(path) for path in image_paths):
            # If all versions exist, convert them to the desired format and create a cubemap and convert it to an equirectangular map
            converted_image_paths = []
            
            
            
            
            for path in image_paths:
                image_format = bpy.context.scene.image_format_dropdown
    
                if image_format.startswith('.'):
                    image_format = image_format[1:]  # remove the leading dot
                image_format = image_format  # convert to uppercase
            
                
            
                # Convert the image to the desired format
                convert_image_format(path, os.path.dirname(path), image_format)
                # Add the converted image path to the list
                converted_image_paths.append(os.path.splitext(path)[0] + bpy.context.scene.image_format_dropdown)
            
            #log_to_file(str(converted_image_paths))
            
            
            log_to_file("converted_image_paths: " + str(converted_image_paths))
            cubemap_image_path = create_cubemap_and_convert_to_equirectangular(converted_image_paths)
            
            
            log_to_file("cubemap_image_path: " + cubemap_image_path)
            
            cubemap_image_path = cubemap_image_path.replace(bpy.context.preferences.addons[__name__].preferences.export_path, "")
            #log_to_file(cubemap_image_path)
            cubemap_image_path = cubemap_image_path.replace(bpy.context.scene.image_format_dropdown, "")
            #cubemap_to_convert = os.path.basename(cubemap_image_path)
            equirectangular_image_paths = convert_cubemap_to_equirectangular(cubemap_image_path)
            
            #converted_image_paths[25]
            
            return 2 #success! new equirectangular map exists
        else:
            # If not all versions exist, continue as normal
            old_file_path = tga_path + filename + "_00_00.tga"
            new_file_path = tga_path + filename + ".tga"
            if os.path.exists(old_file_path):
                try:
                    os.rename(old_file_path, new_file_path)
                    log_to_file(f'Renamed {old_file_path} to {new_file_path}')
                    
                    return 1 #success! tga now exists
                except FileExistsError:
                    log_to_file(f'File {new_file_path} already exists. Did not rename {old_file_path}.')
            
            else:
                log_to_file(f'File {old_file_path} not found, could not rename')
                return 0 #failed


#replace file extension for file path
def replace_extension(file_path, new_extension):
    # Check if the new extension starts with a dot; if not, add one
    if not new_extension.startswith('.'):
        new_extension = '.' + new_extension
    
    # Split the file path into the root and the current extension
    root, _ = os.path.splitext(file_path)
    
    # Combine the root with the new extension
    new_file_path = root + new_extension
    
    return new_file_path

#Run tool.exe to export model files either .ass or .jms
def run_exe_tool_export(tag_directory, format):

    # depending on the toggle for the game choose the path for tool.exe
    if(bpy.context.scene.halo_version_dropdown == "Halo 3"):
        Tool_Root = (bpy.context.preferences.addons[__name__].preferences.halo3_tag_path).replace('H3EK\\tags\\', 'H3EK\\tool.exe')
        #Tags_Root = bpy.context.preferences.addons[__name__].preferences.halo3_tag_path
    elif (bpy.context.scene.halo_version_dropdown == "Halo 3: ODST"):  
        Tool_Root = bpy.context.preferences.addons[__name__].preferences.odst_tag_path.replace('H3ODSTEK\\tags\\', 'H3ODSTEK\\tool.exe')
        #Tags_Root = bpy.context.preferences.addons[__name__].preferences.odst_tag_path
    elif (bpy.context.scene.halo_version_dropdown == "Halo Reach"):
        Tool_Root = bpy.context.preferences.addons[__name__].preferences.reach_tag_path.replace('HREK\\tags\\', 'HREK\\tool.exe')
        #Tags_Root = bpy.context.preferences.addons[__name__].preferences.reach_tag_path
    else:
        log_to_file("Error with Tag option property")

    #list that will contain the files Tool made
    created_file_list = [] 

    # create the command string
    cmd = f'tool extract-import-info "{tag_directory}"' 

    print("Trying to run CMD: " + cmd)

    try:
        # Change to the directory of the tool
        os.chdir(os.path.dirname(Tool_Root))
    
        final_path = ""
    
        # Run the command and capture the output
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)

        # Print the output
        print(result.stdout)

        # Search for the line starting with "done:"
        done_line = [line for line in result.stdout.splitlines() if 'done:' in line]
        if done_line:
            done_path = done_line[0].split('done: ')[1].strip()
            print("Extracted path:", done_path)

            
        else:
            print("Done path not found in the output.")
        
        
        
        #move newly created file from new path to Export folder and overwrite any existing file with that name
        
        # Change the directory as per the pattern
        new_directory = tag_directory.replace('\\tags\\', '\\data\\')
        last_folder_index = new_directory.rfind('\\')
        if (format == ".ass"):
            new_directory = new_directory[:last_folder_index] + '\\structure' + new_directory[last_folder_index:]
        elif (format == ".jms"):
            new_directory = new_directory[:last_folder_index] + '\\render' + new_directory[last_folder_index:]
        
        # Replace the extension with the desired format
        new_file_path = replace_extension(new_directory, format)


        #alter the new path with what Tool said
        # Split the existing path at the "\data\" part
        new_file_path, _ = new_file_path.split("\\data\\", 1)

        # Combine the base directory with the done_path
        new_file_path = os.path.join(new_file_path, done_path)

        # Check if the new file exists
        if os.path.exists(new_file_path):
            # Get the export directory
            export_directory = bpy.context.preferences.addons[__name__].preferences.export_path

            # Create the destination path
            destination_path = os.path.join(export_directory, os.path.basename(new_file_path))

            # Move and overwrite the file to the export directory
            shutil.move(new_file_path, destination_path)

            print(f"File moved to: {destination_path}")
        else:
            print(f"File not found at: {new_file_path}")
            
        final_path = destination_path
        
        return final_path
        
        
        
    except Exception as e:
        print(f'The tool caused an error: {str(e)}')
        
        return "Tool had error exporting model file"
        
    


def create_cubemap_and_convert_to_equirectangular(image_paths):
    import py360convert
    import scipy
    import numpy as np

    # Load the images
    images = [bpy.data.images.load(path) for path in image_paths]
    # Convert the images to numpy arrays and store them in a list
    cubemaps = [np.array(img.pixels[:]).reshape((img.size[1], img.size[0], 4)) for img in images]

    # Apply transformations
    cubemaps[5] = np.rot90(cubemaps[5], 2)  # Rotate Down 180 degrees
    cubemaps[1] = np.rot90(cubemaps[1], -1)  # Rotate Left 90 degrees
    cubemaps[0] = np.rot90(cubemaps[0], 1)  # Rotate Right 90 degrees
    cubemaps[2] = np.rot90(cubemaps[2], 2)  # Rotate Back 180 degrees

    # Create a cubemap from the images in dice format
    cubemap = np.zeros((images[0].size[1]*3, images[0].size[0]*4, 4))
    cubemap[0:images[0].size[1], images[0].size[0]:images[0].size[0]*2] = cubemaps[5]  # Up   _00_04  for some reason it is index 5 not 4
    cubemap[images[0].size[1]:images[0].size[1]*2, 0:images[0].size[0]] = cubemaps[1]  # Left  _00_01
    cubemap[images[0].size[1]:images[0].size[1]*2, images[0].size[0]:images[0].size[0]*2] = cubemaps[3]  # Front   _00_03
    cubemap[images[0].size[1]:images[0].size[1]*2, images[0].size[0]*2:images[0].size[0]*3] = cubemaps[0]  # Right _00_00
    cubemap[images[0].size[1]:images[0].size[1]*2, images[0].size[0]*3:images[0].size[0]*4] = cubemaps[2]  # Back  _00_02
    cubemap[images[0].size[1]*2:images[0].size[1]*3, images[0].size[0]:images[0].size[0]*2] = cubemaps[4]  # Down  _00_05  for some reason it is index 4 not 5


    # Save the cubemap
    cubemap_image = bpy.data.images.new("Cubemap Image", width=cubemap.shape[1], height=cubemap.shape[0])
    cubemap_image.pixels = cubemap.flatten().tolist()

    cubemap_file_name = os.path.join(os.path.dirname(image_paths[0]), os.path.basename(image_paths[0]).replace("_00_00", ""))

        
    log_to_file("cubemap_file_name: " + cubemap_file_name)
    
    cubemap_image.filepath_raw = cubemap_file_name
    # Depending on the file format entered in the preferences panel change the format of the image
    image_format = bpy.context.scene.image_format_dropdown
    
    if image_format.startswith('.'):
        image_format = image_format[1:]  # remove the leading dot
    image_format = image_format.upper()  # convert to uppercase
    
    if (image_format == "TIF"):
        image_format = "TIFF"
        
    cubemap_image.file_format = image_format
    cubemap_image.save()
    log_to_file(f"Saving cubemap image to: {cubemap_file_name}")

    return cubemap_file_name

#function that takes in the path of a cubemap and spits out an equirectangular map
def convert_cubemap_to_equirectangular(cubemap_image_path):
    import py360convert
    import scipy
    
    log_to_file("Trying to convert Environment Map to Equirectangular! Path: " + cubemap_image_path)
    
    og_image_path = cubemap_image_path
    
    if (cubemap_image_path == "" or cubemap_image_path == " "):
        cubemap_image_path = "shaders/default_bitmaps/bitmaps/default_dynamic_cube_map"
    
    
    # Load the cubemap image
    cubemap_image_path = bpy.context.preferences.addons[__name__].preferences.export_path + "/" + cubemap_image_path + bpy.context.scene.image_format_dropdown
    
    log_to_file("Full Cubemap Path: " + cubemap_image_path)
    cubemap_image = bpy.data.images.load(cubemap_image_path)
    cubemap_np = np.array(cubemap_image.pixels[:]).reshape((cubemap_image.size[1], cubemap_image.size[0], 4))  # reshape to 2D array with RGBA channels

    

    # Check if the image has the correct dimensions
    height, width, _ = cubemap_np.shape
    if (width != height * 4 / 3):
        #if not the right dimensions then it is likely a default bitmap so return it
        return og_image_path
        
        # Resize the image to the correct dimensions
        #new_width = int(height * 4 / 3)
        #cubemap_np = np.resize(cubemap_np, (height, new_width, 4))

    # Separate the alpha channel into an additional cubemap image
    alpha_cubemap_np = np.zeros_like(cubemap_np)  # Create a new cubemap with the same shape as the original
    alpha_cubemap_np[:, :, :3] = cubemap_np[:, :, 3, np.newaxis]  # Copy the alpha channel to the RGB channels
    alpha_cubemap_np[:, :, 3] = 1  # Set alpha channel to fully opaque
    rgb_cubemap_np = cubemap_np.copy()  # Copy the original cubemap
    rgb_cubemap_np[:, :, 3] = 1  # Set alpha channel to fully opaque

    # Get the resolution of the input image
    height, width, _ = rgb_cubemap_np.shape
    equirectangular_width = int(width * 1.5)
    equirectangular_height = height

    try:

        # Convert the RGB cubemap to an equirectangular image
        rgb_equirectangular_np = py360convert.c2e(rgb_cubemap_np, h=equirectangular_height, w=equirectangular_width, cube_format='dice')
        # Convert the Alpha cubemap to an equirectangular image
        alpha_equirectangular_np = py360convert.c2e(alpha_cubemap_np, h=equirectangular_height, w=equirectangular_width, cube_format='dice')

        # Create new images and assign the pixels
        rgb_equirectangular_image = bpy.data.images.new("RGB Equirectangular Image", width=equirectangular_width, height=equirectangular_height)
        alpha_equirectangular_image = bpy.data.images.new("Alpha Equirectangular Image", width=equirectangular_width, height=equirectangular_height)
        rgb_equirectangular_image.pixels = rgb_equirectangular_np.flatten().tolist()
        alpha_equirectangular_image.pixels = alpha_equirectangular_np.flatten().tolist()

        # Save the equirectangular images
        dir_name = os.path.dirname(cubemap_image_path)
        base_name = os.path.basename(cubemap_image_path)
        file_name, ext = os.path.splitext(base_name)
        rgb_file_name = f"{file_name}_rgb_equirectangular{ext}"
        alpha_file_name = f"{file_name}_alpha_equirectangular{ext}"
        rgb_equirectangular_image_path = os.path.join(dir_name, rgb_file_name)
        alpha_equirectangular_image_path = os.path.join(dir_name, alpha_file_name)
        rgb_equirectangular_image.filepath_raw = rgb_equirectangular_image_path
        alpha_equirectangular_image.filepath_raw = alpha_equirectangular_image_path
        
        # Depending on the file format entered in the preferences panel change the format of the image
        image_format = bpy.context.scene.image_format_dropdown
        
        if image_format.startswith('.'):
            image_format = image_format[1:]  # remove the leading dot
        image_format = image_format.upper()  # convert to uppercase
        
        if (image_format == "TIF"):
            image_format = "TIFF"
            
        
        rgb_equirectangular_image.file_format = image_format
        alpha_equirectangular_image.file_format = image_format

        rgb_equirectangular_image.save()
        alpha_equirectangular_image.save()

        log_to_file(f"Saving RGB equirectangular image to: {rgb_equirectangular_image_path}")
        log_to_file(f"Saving Alpha equirectangular image to: {alpha_equirectangular_image_path}")

        #maybe return array of both paths of rgb and alpha image paths for later? TODO
        
        equirectangular_paths = []
        equirectangular_paths.append(rgb_equirectangular_image_path)
        equirectangular_paths.append(alpha_equirectangular_image_path)
        
        
        
        return equirectangular_paths



    except Exception as e:
        log_to_file(f"Error converting {cubemap_image_path}: {e}")


def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

class InstallPy360ConvertOperator(bpy.types.Operator):
    bl_idname = "myaddon.install_py360convert"
    bl_label = "Install Python Modules"

    def execute(self, context):
        import numpy
        import subprocess
    
        # Check numpy version
        #scipy_version = scipy__version__
        numpy_version = numpy.__version__
        log_to_file("numpy version:", numpy_version)
        if numpy_version >= '1.24.0':
            # Uninstall numpy
            subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "-y", "numpy"])
            # Install specific numpy version
            subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy==1.22.0"])

        # if not (scipy_version):
            # # Uninstall numpy
            # subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "-y", "scipy"])

        try:
            import scipy
            log_to_file("scipy version:", scipy.__version__)
        except ImportError:
            log_to_file("scipy is not installed. Installing now...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "scipy"])


        #editing this so it is just a single folder for the user to target
        py360convert_path = bpy.context.preferences.addons[__name__].preferences.py360convert_path + "/py360convert/"
        #py360convert_path = preferences.library_path
        scipy_path = py360convert_path.replace("py360convert", "scipy")
        PIL_path = py360convert_path.replace("py360convert", "PIL")


        python_executable_path = sys.executable
        site_packages_path = os.path.join(os.path.dirname(python_executable_path), 'lib', 'site-packages')

        # Check if the path ends with 'bin\lib\site-packages' and modify it
        if site_packages_path.endswith('bin\\lib\\site-packages'):
            site_packages_path = site_packages_path.replace('bin\\lib', 'lib')

        py360convert_dest_path = os.path.join(site_packages_path, 'py360convert')
        scipy_dest_path = os.path.join(site_packages_path, 'scipy')
        PIL_dest_path = os.path.join(site_packages_path, 'PIL')

        if os.path.exists(py360convert_dest_path):
            self.report({'INFO'}, "Py360convert is already installed!")
        else:
            #copy py360convert libraries to needed destination
            shutil.copytree(py360convert_path, py360convert_dest_path)
 
            self.report({'INFO'}, "Py360convert installed successfully")
        
        if os.path.exists(scipy_dest_path):
            self.report({'INFO'}, "Scipy is already installed!")
        else:
            #copy scipy libraries to needed destination
            shutil.copytree(scipy_path, scipy_dest_path)

            self.report({'INFO'}, "scipy installed successfully")
            
        if os.path.exists(PIL_dest_path):
            self.report({'INFO'}, "PIL is already installed!")
        else:
            #copy PIL libraries to needed destination
            shutil.copytree(PIL_path, PIL_dest_path)
 
            self.report({'INFO'}, "PIL installed successfully")    
        

        return {'FINISHED'}

#for modifying the names of filenames before they are displayed in the List view
def modify_filename(file_name, Tag_Root):
    # Check the file_name and modify it as needed
    
    #SCENARIO_STRUCTURE_BSP
    
    #print(Tag_Root)
    
    #Halo 3 Multiplayer
    if (file_name == "armory"):
        file_name = file_name + " - (Rat's Nest)"
    elif (file_name == "bunkerworld"):
        file_name = file_name + " - (Standoff)"
    elif (file_name == "chillout"):
        file_name = file_name + " - (Cold Storage)"
    elif (file_name == "chill"):
        file_name = file_name + " - (Narrows)"
    elif (file_name == "construct"):
        file_name = file_name + " - (Construct)"
    elif (file_name == "cyberdyne"):
        file_name = file_name + " - (The Pit)"
    elif (file_name == "deadlock"):
        file_name = file_name + " - (Highground)"    
    elif (file_name == "descent"):
        file_name = file_name + " - (Assembly)"
    elif (file_name == "docks"):
        file_name = file_name + " - (Longshore)"
    elif (file_name == "fortress"):
        file_name = file_name + " - (Citadel)"
    elif (file_name == "ghosttown"):
        file_name = file_name + " - (Ghost Town)"
    elif (file_name == "guardian"):
        file_name = file_name + " - (Guardian)"
    elif (file_name == "isolation"):
        file_name = file_name + " - (Isolation)"
    elif (file_name == "lockout"):
        file_name = file_name + " - (Blackout)"    
    elif (file_name == "midship"):
        file_name = file_name + " - (Heretic)"
    elif (file_name == "riverworld"):
        file_name = file_name + " - (Valhalla)"
    elif (file_name == "s3d_edge"):
        file_name = file_name + " - (Edge)"
    elif (file_name == "s3d_turf"):
        file_name = file_name + " - (Icebox)"
    elif (file_name == "s3d_waterfall"):
        file_name = file_name + " - (Waterfall)"
    elif (file_name == "salvation"):
        file_name = file_name + " - (Epitaph)"
    elif (file_name == "sandbox"):
        file_name = file_name + " - (Sandbox)"    
    elif (file_name == "shrine"):
        file_name = file_name + " - (Sandtrap)"
    elif (file_name == "sidewinder"):
        file_name = file_name + " - (Avalanche)"
    elif (file_name == "snowbound"):
        file_name = file_name + " - (Snowbound)"
    elif (file_name == "spacecamp"):
        file_name = file_name + " - (Orbital)"
    elif (file_name == "warehouse"):
        file_name = file_name + " - (Foundry)"
    elif (file_name == "zanzibar"):
        file_name = file_name + " - (Last Resort)"

    
    #Halo 3 Campaign
    # elif ("010_bsp" in file_name and "010_jungle" in Tag_Root):
        # file_name = file_name + " (The Arrival)"
    elif ("010_bsp" in file_name):
        file_name = file_name + " - (Sierra 117)"
    elif ("020_bsp" in file_name):
        file_name = file_name + " - (Crow's Nest)"
    elif ("030_bsp" in file_name):
        file_name = file_name + " - (Tsavo Highway)"
    elif ("040_bsp" in file_name):
        file_name = file_name + " - (The Storm)"
    elif ("050_bsp" in file_name):
        file_name = file_name + " - (Floodgate)"
    elif ("070_bsp" in file_name):
        file_name = file_name + " - (The Ark)"    
    elif ("100_citadel" in Tag_Root and "bsp_" in file_name):
        file_name = file_name + " - (The Covenant)"
    elif ("110_bsp" in file_name):
        file_name = file_name + " - (Cortana)"
    elif ("120_bsp" in file_name):
        file_name = file_name + " - (Halo)"
    elif ("130_bsp" in file_name):
        file_name = file_name + " - (Epilogue)"
        
    #Halo 3: ODST Campaign    
    elif (file_name == "c100" or file_name == "c100b"):
        file_name = file_name + " - (Prepare to Drop)"
    elif (file_name == "c200" or file_name == "c300" or ("c200" in Tag_Root and file_name == "l200_020")):
        file_name = file_name + " - (Costal Highway)"
    elif ("l300" in Tag_Root and ("h100_" in file_name or "l300_" in file_name)):
        file_name = file_name + " - (Costal Highway)" #again for some reason
    elif ("sc100" in Tag_Root and ("h100_" in file_name)):
        file_name = file_name + " - (Tayari Plaza)" 
    elif ("sc110" in Tag_Root and ("h100_" in file_name or "sc110_" in file_name)):
        file_name = file_name + " - (Uplift Reserve)" 
    elif ("sc120" in Tag_Root and ("h100_" in file_name)):
        file_name = file_name + " - (Kizingo Blvd)" 
    elif ("sc130" in file_name):
        file_name = file_name + " - (Oni Alpha Site)" 
    elif ("sc140" in file_name):
        file_name = file_name + " - (New Mombasa Police Dep. HQ)"
    elif ("sc150" in Tag_Root and ("bsp_" in file_name or "h100_" in file_name)):
        file_name = file_name + " - (Kikiwani Station)"
    elif ("h100_" in file_name):
        file_name = file_name + " - (Mombasa Streets)"    
    elif ("l200_" in file_name):
        file_name = file_name + " - (Data Hive)"
        
        
    # RENDER_MODEL Halo 3     
     
        #Halo 3 Multiplayer Skyboxes
    elif("\\sky\\" in Tag_Root):
        if ("\\armory\\" in Tag_Root):
            file_name = file_name + " - (Rat's Nest Skybox)"
        elif ("\\bunkerworld\\" in Tag_Root):
            file_name = file_name + " - (Standoff Skybox)"
        elif ("\\chillout\\" in Tag_Root):
            file_name = file_name + " - (Cold Storage Skybox)"
        elif ("\\chill\\" in Tag_Root):
            file_name = file_name + " - (Narrows Skybox)"
        elif ("\\construct\\" in Tag_Root):
            file_name = file_name + " - (Construct Skybox)"
        elif ("\\cyberdyne\\" in Tag_Root):
            file_name = file_name + " - (The Pit Skybox)"
        elif ("\\deadlock\\" in Tag_Root):
            file_name = file_name + " - (Highground Skybox)"    
        elif ("\\descent\\" in Tag_Root):
            file_name = file_name + " - (Assembly Skybox)"
        elif ("\\docks\\" in Tag_Root):
            file_name = file_name + " - (Longshore Skybox)"
        elif ("\\fortress\\" in Tag_Root):
            file_name = file_name + " - (Citadel Skybox)"
        elif ("\\ghosttown\\" in Tag_Root):
            file_name = file_name + " - (Ghost Town Skybox)"
        elif ("\\guardian\\" in Tag_Root):
            file_name = file_name + " - (Guardian Skybox)"
        elif ("\\isolation\\" in Tag_Root):
            file_name = file_name + " - (Isolation Skybox)"
        elif ("\\lockout\\" in Tag_Root):
            file_name = file_name + " - (Blackout Skybox)"    
        elif ("\\midship\\" in Tag_Root):
            file_name = file_name + " - (Heretic Skybox)"
        elif ("\\riverworld\\" in Tag_Root):
            file_name = file_name + " - (Valhalla Skybox)"
        elif ("\\s3d_edge\\" in Tag_Root):
            file_name = file_name + " - (Edge Skybox)"
        elif ("\\s3d_turf\\" in Tag_Root):
            file_name = file_name + " - (Icebox Skybox)"
        elif ("\\s3d_waterfall\\" in Tag_Root):
            file_name = file_name + " - (Waterfall Skybox)"
        elif ("\\salvation\\" in Tag_Root):
            file_name = file_name + " - (Epitaph Skybox)"
        elif ("\\sandbox\\" in Tag_Root):
            file_name = file_name + " - (Sandbox Skybox)"    
        elif ("\\shrine\\" in Tag_Root):
            file_name = file_name + " - (Sandtrap Skybox)"
        elif ("\\sidewinder\\" in Tag_Root):
            file_name = file_name + " - (Avalanche Skybox)"
        elif ("\\snowbound\\" in Tag_Root):
            file_name = file_name + " - (Snowbound Skybox)"
        elif ("\\spacecamp\\" in Tag_Root):
            file_name = file_name + " - (Orbital Skybox)"
        elif ("\\warehouse\\" in Tag_Root):
            file_name = file_name + " - (Foundry Skybox)"
        elif ("\\zanzibar\\" in Tag_Root):
            file_name = file_name + " - (Last Resort Skybox)"
        
        #Halo 3 Campaign Skyboxes
        elif ("\\010_jungle\\" in Tag_Root):
            file_name = file_name + " - (Sierra 117 Skybox)"
        elif ("\\020_base\\" in Tag_Root):
            file_name = file_name + " - (Crow's Nest Skybox)"
        elif ("\\030_outskirts\\" in Tag_Root):
            file_name = file_name + " - (Tsavo Highway Skybox)"
        elif ("\\040_voi\\" in Tag_Root):
            file_name = file_name + " - (The Storm Skybox)"
        elif ("\\050_floodvoi\\" in Tag_Root):
            file_name = file_name + " - (Floodgate Skybox)"
        elif ("\\055_shadow\\" in Tag_Root):
            file_name = file_name + " - (Unknown Skybox)"
        elif ("\\070_waste\\" in Tag_Root):
            file_name = file_name + " - (The Ark Skybox)"    
        elif ("\\100_citadel\\" in Tag_Root):
            file_name = file_name + " - (The Covenant Skybox)"
        elif ("\\110_hc\\" in Tag_Root):
            file_name = file_name + " - (Cortana Skybox)"
        elif ("\\120_halo\\" in Tag_Root):
            file_name = file_name + " - (Halo Skybox)"
        elif ("\\130_epilogue\\" in Tag_Root):
            file_name = file_name + " - (Epilogue Skybox)"
        
    if("\\decorators\\" in Tag_Root):
        file_name = file_name + " - (Decorator: Will not Import)"
        
    #More later for dlc or added files etc    
    # elif (file_name == "riverworld"):
        # file_name = file_name + " (Valhalla)"
    # elif (file_name == "s3d_edge"):
        # file_name = file_name + " (Edge)"
    # elif (file_name == "s3d_turf"):
        # file_name = file_name + " (Icebox)"
    # elif (file_name == "s3d_waterfall"):
        # file_name = file_name + " (Waterfall)"
    # elif (file_name == "salvation"):
        # file_name = file_name + " (Epitaph)"
    # elif (file_name == "sandbox"):
        # file_name = file_name + " (Sandbox)"    
    # elif (file_name == "shrine"):
        # file_name = file_name + " (Sandtrap)"
    # elif (file_name == "sidewinder"):
        # file_name = file_name + " (Avalanche)"
    # elif (file_name == "snowbound"):
        # file_name = file_name + " (Snowbound)"
    # elif (file_name == "spacecamp"):
        # file_name = file_name + " (Orbital)"
    # elif (file_name == "warehouse"):
        # file_name = file_name + " (Foundry)"
    # elif (file_name == "zanzibar"):
        # file_name = file_name + " (Last Resort)"
    # elif (file_name == "bunkerworld"):
        # file_name = file_name + " (Standoff)"    
    # elif (file_name == "bunkerworld"):
        # file_name = file_name + " (Standoff)"

    return file_name

#Property for storing file lists for Panel
class CR4B_FileItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="File Name")
    path: bpy.props.StringProperty(name="File Path")
    map: bpy.props.StringProperty(name="Map Path")
    select: bpy.props.BoolProperty(name="Select", default=False)  # Added for multi-selection

#hide certain file format options depending on the Game Title
def get_file_format_items(self, context):
    if context.scene.halo_version_dropdown in ("Halo 3", "Halo 3: ODST"):
        return [
            ("amf", "amf", "amf format"),
            ("obj", "obj", "obj format"),
            ("dae", "dae", "collada"),
            ("ass/jms", "ass/jms", "ass or jms format")
        ]
    else:
        return [
            ("amf", "amf", "amf format"),
            ("obj", "obj", "obj format"),
            ("dae", "dae", "collada")
        ]

#Scanning for scenario_structure_bsp files within tags
class CR4B_ScanScenarioStructureBSP(bpy.types.Operator):
    bl_idname = "cr4b.scan_scenario_structure_bsp"
    bl_label = "Scan for .scenario_structure_bsp files"

    def execute(self, context):
        # Clear the existing list
        context.scene.cr4b_file_list.clear()
        
        #store some recent values
        context.scene.cr4b_last_button = "scenario_structure_bsp"
        context.scene.cr4b_last_tag = context.scene.halo_version_dropdown
        
        file_format = context.scene.file_format_dropdown
        
        halo_title = context.scene.halo_version_dropdown
        
        if (halo_title == "Halo CE"):
            halo_title = "HaloCE"
        elif (halo_title == "Halo 2"):
            halo_title = "Halo2"
        elif (halo_title == "Halo 3"):
            if (file_format == "ass/jms"):
                halo_title = "H3EK"
            else:
                halo_title = "Halo3"
        elif (halo_title == "Halo 3: ODST"):
            if (file_format == "ass/jms"):
                halo_title = "H3ODSTEK"
            else:
                halo_title = "Halo3ODST"
        elif (halo_title == "Halo Reach"):
            halo_title = "HaloReach"
        elif (halo_title == "Halo 4"):
            halo_title = "Halo4"
        elif (halo_title == "Halo 5"):
            halo_title = "Halo5"
        
        file_format = context.scene.file_format_dropdown
        
        #if format is ass/jms then use this logic
        if (file_format == "ass/jms"):
            if(bpy.context.scene.halo_version_dropdown == "Halo 3"):
                log_to_file("Using Halo 3 Tags")
                Tag_Root = bpy.context.preferences.addons[__name__].preferences.halo3_tag_path 
                log_to_file("halo3_tag_path: " + bpy.context.preferences.addons[__name__].preferences.halo3_tag_path)
            elif (bpy.context.scene.halo_version_dropdown == "Halo 3: ODST"):
                log_to_file("Using Halo 3: ODST Tags")
                log_to_file("odst_tag_path: " + bpy.context.preferences.addons[__name__].preferences.odst_tag_path)
                Tag_Root = bpy.context.preferences.addons[__name__].preferences.odst_tag_path
            elif (bpy.context.scene.halo_version_dropdown == "Halo Reach"):
                log_to_file("Using Halo Reach Tags")
                log_to_file("reach_tag_path: " + bpy.context.preferences.addons[__name__].preferences.reach_tag_path)
                Tag_Root = bpy.context.preferences.addons[__name__].preferences.reach_tag_path
            else:
                log_to_file("Error with Tag option property")
        
        
            for file_path in glob.glob(os.path.join(Tag_Root, '**/*.scenario_structure_bsp'), recursive=True):
                item = context.scene.cr4b_file_list.add()
                file_name_without_extension = os.path.splitext(os.path.basename(file_path))[0]
                modified_file_name = modify_filename(file_name_without_extension, file_path) # Call the modify function
                item.name = modified_file_name # Use the modified file name
                item.path = file_path
        
        #if format is anything else use Reclaimer to build list
        else:
            if(bpy.context.scene.halo_version_dropdown == "Halo CE"):
                halo_ver = "HaloCE"
            elif(bpy.context.scene.halo_version_dropdown == "Halo 2"):
                halo_ver = "Halo2"
            elif(bpy.context.scene.halo_version_dropdown == "Halo 3"):
                halo_ver = "Halo3"
            elif(bpy.context.scene.halo_version_dropdown == "Halo 3: ODST"):
                halo_ver = "Halo3ODST"
            elif(bpy.context.scene.halo_version_dropdown == "Halo Reach"):
                halo_ver = "HaloReach"
            elif(bpy.context.scene.halo_version_dropdown == "Halo 4"):
                halo_ver = "Halo4"
            elif(bpy.context.scene.halo_version_dropdown == "Halo 5"):
                halo_ver = "Halo5"
                
            export_dir = bpy.context.preferences.addons[__name__].preferences.export_path
            
            print("Trying to read the level list for " + halo_ver)
            
            
            tags_report_path = os.path.join(export_dir + "Reports\\", halo_ver + '_level_report.txt')

            
            with open(tags_report_path, 'r') as f:
                lines = f.readlines()
            #loop through final version of the tags_report.txt file created to generate list of models and their paths
            #for loop here that iterates through each line of the tags_report.txt file
            for line in lines:
                # Extract map directory
                if line.startswith('['):
                    map = line.split('] ')[1].strip()
                else:
                    tag = line
                
                    #If current line is a tag line then create an entry in the list
                    item = context.scene.cr4b_file_list.add()
                    file_name_without_extension = os.path.splitext(os.path.basename(tag))[0]
                    modified_file_name = modify_filename(file_name_without_extension, tag) # Call the modify function
                    item.map = map
                    item.name = modified_file_name # Use the modified file name
                    item.path = tag
                
   
        
        context.scene.cr4b_header_suffix = " Levels"
        
        return {'FINISHED'}

#Scanning for render_model files within tags
class CR4B_ScanRenderModel(bpy.types.Operator):
    bl_idname = "cr4b.scan_render_model"
    bl_label = "Scan for .render_model files"

    def execute(self, context):
        # Clear the existing list
        context.scene.cr4b_file_list.clear()
        
        #store some recent values
        context.scene.cr4b_last_button = "render_model"
        context.scene.cr4b_last_tag = context.scene.halo_version_dropdown
        
        file_format = context.scene.file_format_dropdown
        
        #if format is ass/jms then use this logic
        if (file_format == "ass/jms"):
            if(bpy.context.scene.halo_version_dropdown == "Halo 3"):
                log_to_file("Using Halo 3 Tags")
                Tag_Root = bpy.context.preferences.addons[__name__].preferences.halo3_tag_path 
                log_to_file("halo3_tag_path: " + bpy.context.preferences.addons[__name__].preferences.halo3_tag_path)
            elif (bpy.context.scene.halo_version_dropdown == "Halo 3: ODST"):
                log_to_file("Using Halo 3: ODST Tags")
                log_to_file("odst_tag_path: " + bpy.context.preferences.addons[__name__].preferences.odst_tag_path)
                Tag_Root = bpy.context.preferences.addons[__name__].preferences.odst_tag_path
            elif (bpy.context.scene.halo_version_dropdown == "Halo Reach"):
                log_to_file("Using Halo Reach Tags")
                log_to_file("reach_tag_path: " + bpy.context.preferences.addons[__name__].preferences.reach_tag_path)
                Tag_Root = bpy.context.preferences.addons[__name__].preferences.reach_tag_path
            else:
                log_to_file("Error with Tag option property")
        
        
            for file_path in glob.glob(os.path.join(Tag_Root, '**/*.render_model'), recursive=True):
                item = context.scene.cr4b_file_list.add()
                file_name_without_extension = os.path.splitext(os.path.basename(file_path))[0]
                modified_file_name = modify_filename(file_name_without_extension, file_path) # Call the modify function
                item.name = modified_file_name # Use the modified file name
                item.path = file_path
        
        #if format is anything else use Reclaimer to build list
        else:
            if(bpy.context.scene.halo_version_dropdown == "Halo CE"):
                halo_ver = "HaloCE"
            elif(bpy.context.scene.halo_version_dropdown == "Halo 2"):
                halo_ver = "Halo2"
            elif(bpy.context.scene.halo_version_dropdown == "Halo 3"):
                halo_ver = "Halo3"
            elif(bpy.context.scene.halo_version_dropdown == "Halo 3: ODST"):
                halo_ver = "Halo3ODST"
            elif(bpy.context.scene.halo_version_dropdown == "Halo Reach"):
                halo_ver = "HaloReach"
            elif(bpy.context.scene.halo_version_dropdown == "Halo 4"):
                halo_ver = "Halo4"
            elif(bpy.context.scene.halo_version_dropdown == "Halo 5"):
                halo_ver = "Halo5"
                
            export_dir = bpy.context.preferences.addons[__name__].preferences.export_path
            
            print("Trying to read the model list for " + halo_ver)
            
            #clear all data from the tags_report.txt file within the Export Directory
            tags_report_path = os.path.join(export_dir + "Reports\\", halo_ver + '_model_report.txt')

            
            with open(tags_report_path, 'r') as f:
                lines = f.readlines()
            #loop through final version of the tags_report.txt file created to generate list of models and their paths
            #for loop here that iterates through each line of the tags_report.txt file
            for line in lines:
                # Extract map directory
                if line.startswith('['):
                    map = line.split('] ')[1].strip()
                else:
                    tag = line
                
                    #If current line is a tag line then create an entry in the list
                    item = context.scene.cr4b_file_list.add()
                    file_name_without_extension = os.path.splitext(os.path.basename(tag))[0]
                    modified_file_name = modify_filename(file_name_without_extension, tag) # Call the modify function
                    item.map = map
                    item.name = modified_file_name # Use the modified file name
                    item.path = tag
                
   
        
        context.scene.cr4b_header_suffix = " Models"
        
        return {'FINISHED'}

# Functions for file extraction
def Tool_Ass_Extract(files):
    # Process the files and return a new directory list
    exported_file_list = []
    
    for dir in files:
        exported_file_list.append(run_exe_tool_export(dir, ".ass"))
    
    return exported_file_list  # Modify as needed

def Tool_Jms_Extract(files):
    # Process the files and return a new directory list
    exported_file_list = []
    
    for dir in files:
        exported_file_list.append(run_exe_tool_export(dir, ".jms"))
    
    return exported_file_list  # Modify as needed

#build model report using Reclaimer
def Reclaimer_Report(map_path, export_dir, tag_type, halo_ver):
    #talk to Reclaimer and send a report command to it along with the other arguments

    # create the command string
    #export_dir = export_dir + "Reports\\"
    
    export_dir = remove_ending_backslash(export_dir)
    
    if tag_type == "render_model":
        cmd = f'reclaimer report "{map_path}" "{export_dir}" render_model {halo_ver}' 
    elif tag_type == "scenario_structure_bsp":
        cmd = f'reclaimer report "{map_path}" "{export_dir}" scenario_structure_bsp {halo_ver}' 
    elif tag_type == "gbxmodel":
        cmd = f'reclaimer report "{map_path}" "{export_dir}" gbxmodel {halo_ver}'
    else:
        print("unsupported tag type for Reclaimer Report")

    print("Trying to run CMD: " + cmd)

    reclaimer_path = bpy.context.preferences.addons[__name__].preferences.reclaimer_path

    try:
        # Change to the directory of the tool
        os.chdir(os.path.dirname(reclaimer_path))
    
        final_path = ""
    
        # Run the command and capture the output
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)

        # Print the output
        print(result.stdout)

    except Exception as e:
        print(f'Reclaimer did not like the command it was sent: {str(e)}')
        
        pass 
    pass

#export model using Reclaimer
def Reclaimer_Export(map_path, tag_file, export_dir, tag_type):
    #talk to Reclaimer and send an export command to it along with the other arguments

    # create the command string
    
    #remove any bad characters from the beginning and end of the strings
    map_path = map_path.strip()
    tag_file = tag_file.strip()
    export_dir = export_dir.strip()
    tag_type = tag_type.strip()
    
    
    export_dir = remove_ending_backslash(export_dir)
    export_format = bpy.context.scene.file_format_dropdown
    reclaimer_path = bpy.context.preferences.addons[__name__].preferences.reclaimer_path
    img_format = bpy.context.scene.image_format_dropdown
    settings_dir = reclaimer_path + "Settings\\"
    
    if(export_format =="dae"):
        export_format = "collada"
    
    cmd = f'reclaimer export "{map_path}" "{tag_file}" "{export_dir}" {export_format} {img_format}'
    
    #EDIT THE SETTINGS FILE TO MAKE SURE PROMPT DATA FOLDER IS DISABLRD
    #EDIT THE FIELD IN SETTINGS TO CHANGE THE DATA FOLDER
    
    #new_data_folder_path = export_dir
    #file_path = settings_dir + "settings.json"
    #update_json_file(file_path, new_data_folder_path)
    
    print("Trying to update settings file and setting Data Folder to: " + export_dir)
    
    # if tag_type == "render_model":
        # cmd = f'reclaimer export "{map_path}" "{tag_file}" "{export_dir}" {export_format}' 
    # elif tag_type == "scenario_structure_bsp":
        # cmd = f'reclaimer export "{map_path}" "{tag_file}" "{export_dir}" {export_format}' 
    # elif tag_type == "gbxmodel":
        # cmd = f'reclaimer export "{map_path}" "{tag_file}" "{export_dir}" {export_format}'
    # else:
        # print("unsupported tag type for Reclaimer Export")

    print("Trying to run CMD: " + cmd)

    

    try:
        # Change to the directory of the tool
        os.chdir(os.path.dirname(reclaimer_path))
    
        final_path = ""
    
        # Run the command and capture the output
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)

        # Print the output
        print(result.stdout)

    except Exception as e:
        print(f'Reclaimer did not like the command it was sent: {str(e)}')
        
        pass 
    pass

#remove ending backslash from string
def remove_ending_backslash(s):
    if s.endswith("\\"):
        return s[:-1]
    return s

#save console log to the Export Directory
def log_to_file(message, *args):
    file_path = bpy.context.preferences.addons[__name__].preferences.export_path + "[CR4B_console_log].txt"
    
    #print(f"Log file path: {file_path}")
    
    # Ensure the directory exists
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Check if the file exists
    if not os.path.exists(file_path):
        print("Log file does not exist. Creating a new one.")

    # Convert message to string if it's a list
    if isinstance(message, list):
        message = ' '.join(map(str, message))
        
    # Concatenating additional arguments to the message
    full_message = message + ''.join(str(arg) for arg in args)
    
    try:
        with open(file_path, 'a+') as log_file:
            log_file.write(full_message + "\n")
    except Exception as e:
        print(f"Error writing to log file: {e}")



#logic for importing various file formats (.ass and .jms for example)
class CR4B_ImportFile(bpy.types.Operator):
    bl_idname = "cr4b.import_file"
    bl_label = "Import File"

    def execute(self, context):
        selected_files = [item.path for item in context.scene.cr4b_file_list if item.select]
        selected_items_reclaimer = [
            {'path': item.path, 'map': item.map} for item in context.scene.cr4b_file_list if item.select
        ]
        
        export_dir = bpy.context.preferences.addons[__name__].preferences.export_path
        
        last_button = context.scene.cr4b_last_button
    
        texture_format = context.scene.image_format_dropdown

        import_type = ""
        format_type = context.scene.file_format_dropdown


        new_path_list = []

        if last_button == "scenario_structure_bsp":
            tag_type = last_button
            
            #talk to Tool to extract the models
            if format_type == "ass/jms":
                new_files = Tool_Ass_Extract(selected_files)
                import_type = "ass"
            #Talk to Reclaimer to extract the models
            else:
                print("Using Reclaimer to extract model")
                
                if (format_type == "dae"):
                    reclaimer_export_format = "collada"
                else:
                    reclaimer_export_format = format_type
                
                for item in selected_items_reclaimer:
                    item_path = item['path']
                    item_map = item['map']
                    
                    print(item_map)
                    print(item_path)
                    
                    # Call Reclaimer_Export function
                    Reclaimer_Export(item_map, item_path, export_dir, reclaimer_export_format)
        
                    # Extract the filename without extension from item_path
                    filename_without_extension = os.path.splitext(os.path.basename(item_path))[0]

                    # Create the new string
                    new_path = os.path.join(export_dir, f"{filename_without_extension}.{format_type}")

                    # Append the new string to the list
                    new_path_list.append(new_path)
        
        elif last_button == "render_model":
            if (bpy.context.scene.halo_version_dropdown == "Halo CE"):
                tag_type = "gbxmodel"
            else:
                tag_type = last_button
            
            #Talk to tool to extract the models
            if format_type == "ass/jms":
                
                new_files = Tool_Jms_Extract(selected_files)
                import_type = "jms"
            #talk to Reclaimer to extract the models
            else:    
                print("Using Reclaimer to extract model")
                
                if (format_type == "dae"):
                    reclaimer_export_format = "collada"
                else:
                    reclaimer_export_format = format_type
                
                for item in selected_items_reclaimer:
                    item_path = item['path']
                    item_map = item['map']
                    
                    print(item_map)
                    print(item_path)
                    
                    # Call Reclaimer_Export function
                    Reclaimer_Export(item_map, item_path, export_dir, reclaimer_export_format)
        
                    # Extract the filename without extension from item_path
                    filename_without_extension = os.path.splitext(os.path.basename(item_path))[0]

                    # Create the new string
                    new_path = os.path.join(export_dir, f"{filename_without_extension}.{format_type}")

                    # Append the new string to the list
                    new_path_list.append(new_path)
                
        else:
            print("i hope this never gets hit")
            return {'CANCELLED'}

        #add try block here maybe to catch Decorators and other bad formats
        
        #use Halo Blender Asset Development Toolkit to import the models
        if format_type == "ass/jms":
            log_to_file("Using General_101's ass/jms import code")
            if (import_type == "ass"):
                for file_path in new_files:
                    try:
                        # Call the other add-on's import function
                        bpy.ops.import_scene.ass(filepath=file_path)
                    except Exception as e:
                        log_to_file(f"Blender Toolset Could Not Import the file!")    
            elif (import_type == "jms"):
                for file_path in new_files:
                    try:    
                        # Call the other add-on's import function
                        bpy.ops.import_scene.jms(filepath=file_path)
                    except Exception as e:
                        log_to_file(f"Blender Toolset Could Not Import the file!") 
        
        #use Gravemind's amf importer
        elif format_type == "amf":
            log_to_file("Using Gravemind's amf import code")
            for file_path in new_path_list:
                    try:    
                        # Call the other add-on's import function
                        print("trying to import: " + file_path)
                        
                        bpy.ops.import_scene.amf(filepath=file_path, bitmap_ext=texture_format)
                    except Exception as e:
                        log_to_file(f"AMF importer Could Not Import the file!") 
        elif format_type == "obj":
            log_to_file("Using Blender's obj import code")
            for file_path in new_path_list:
                    try:    
                        # Call the other add-on's import function
                        print("trying to import: " + file_path)
                        
                        bpy.ops.wm.obj_import(filepath=file_path)
                    except Exception as e:
                        log_to_file(f"Blender OBJ Could Not Import the file!") 
        elif format_type == "dae":
            log_to_file("Using Blender's dae import code")
            for file_path in new_path_list:
                    try:    
                        # Call the other add-on's import function
                        print("trying to import: " + file_path)
                        
                        bpy.ops.wm.collada_import(filepath=file_path)
                    except Exception as e:
                        log_to_file(f"Blender Collada Could Not Import the file!")
        #use Blender's built in import code
        else: 
            log_to_file("Using Blender's import code")
            
        # You can now pass selected_files to another function
        
        
        return {'FINISHED'}

#Button for creating new model lists for the UI
class CR4B_CreateModelReport(bpy.types.Operator):
    bl_idname = "cr4b.create_model_report"
    bl_label = "Create Model Report"
    bl_description = "Generate model reports and erase existing .txt file"

    def execute(self, context):
        self.create_report()
        return {'FINISHED'}

    def create_report(self):
        export_dir = bpy.context.preferences.addons[__name__].preferences.export_path + "Reports\\"
        
        #depending on the options in the preferences build report files      
    #HaloCE
        if (bpy.context.preferences.addons[__name__].preferences.haloce_map_path != ""):
            #create level/model report for HCE
            halo_ver = "HaloCE"
            format = ".map"
            Map_Root = bpy.context.preferences.addons[__name__].preferences.haloce_map_path
            
            map_index = 0 
            
            #LEVELS
            #clear all data from the tags_report.txt file within the Export Directory
            tags_report_path = os.path.join(export_dir, halo_ver + '_level_report.txt')

            report_dir = os.path.dirname(tags_report_path)
            if not os.path.exists(report_dir):
                os.makedirs(report_dir)
            
            # Clear existing content in tags_report.txt
            with open(tags_report_path, 'w') as f:
                f.write("")
                
            #Loop through given .map files of selected game
            for map in glob.glob(os.path.join(Map_Root, '**/*' + format), recursive=True):
                #add a new line in the tags_report.txt file within the Export Directory with [map_index] at the front of the line and the directory to map right after
                # Write to tags_report.txt
                with open(tags_report_path, 'a') as f:
                    f.write(f"[{map_index}] {map}\n")
                    
                #call function called Reclaimer_Report() that takes map, export_dir, and "scenario_structure_bsp"
                Reclaimer_Report(map, export_dir, "scenario_structure_bsp", halo_ver)

                map_index += 1
            
            map_index = 0 
            
            #MODELS
            #clear all data from the tags_report.txt file within the Export Directory
            tags_report_path = os.path.join(export_dir, halo_ver + '_model_report.txt')

            report_dir = os.path.dirname(tags_report_path)
            if not os.path.exists(report_dir):
                os.makedirs(report_dir)
            
            # Clear existing content in tags_report.txt
            with open(tags_report_path, 'w') as f:
                f.write("")
                
            #Loop through given .map files of selected game
            for map in glob.glob(os.path.join(Map_Root, '**/*' + format), recursive=True):
                #add a new line in the tags_report.txt file within the Export Directory with [map_index] at the front of the line and the directory to map right after
                # Write to tags_report.txt
                with open(tags_report_path, 'a') as f:
                    f.write(f"[{map_index}] {map}\n")
                    
                #call function called Reclaimer_Report() that takes map, export_dir, and "scenario_structure_bsp"
                Reclaimer_Report(map, export_dir, "gbxmodel", halo_ver)

                map_index += 1
 
    #Halo2
        if (bpy.context.preferences.addons[__name__].preferences.halo2_map_path != ""):
            #create level/model report for H2
            halo_ver = "Halo2"
            format = ".map"
            Map_Root = bpy.context.preferences.addons[__name__].preferences.halo2_map_path
            
            map_index = 0
            
            #LEVELS
            #clear all data from the tags_report.txt file within the Export Directory
            tags_report_path = os.path.join(export_dir, halo_ver + '_level_report.txt')

            report_dir = os.path.dirname(tags_report_path)
            if not os.path.exists(report_dir):
                os.makedirs(report_dir)
            
            # Clear existing content in tags_report.txt
            with open(tags_report_path, 'w') as f:
                f.write("")
                
            #Loop through given .map files of selected game
            for map in glob.glob(os.path.join(Map_Root, '**/*' + format), recursive=True):
                #add a new line in the tags_report.txt file within the Export Directory with [map_index] at the front of the line and the directory to map right after
                # Write to tags_report.txt
                with open(tags_report_path, 'a') as f:
                    f.write(f"[{map_index}] {map}\n")
                    
                #call function called Reclaimer_Report() that takes map, export_dir, and "scenario_structure_bsp"
                Reclaimer_Report(map, export_dir, "scenario_structure_bsp", halo_ver)

                map_index += 1
            
            map_index = 0
            
            #MODELS
            #clear all data from the tags_report.txt file within the Export Directory
            tags_report_path = os.path.join(export_dir, halo_ver + '_model_report.txt')

            report_dir = os.path.dirname(tags_report_path)
            if not os.path.exists(report_dir):
                os.makedirs(report_dir)

            # Clear existing content in tags_report.txt
            with open(tags_report_path, 'w') as f:
                f.write("")
                
            #Loop through given .map files of selected game
            for map in glob.glob(os.path.join(Map_Root, '**/*' + format), recursive=True):
                #add a new line in the tags_report.txt file within the Export Directory with [map_index] at the front of the line and the directory to map right after
                # Write to tags_report.txt
                with open(tags_report_path, 'a') as f:
                    f.write(f"[{map_index}] {map}\n")
                    
                #call function called Reclaimer_Report() that takes map, export_dir, and "scenario_structure_bsp"
                Reclaimer_Report(map, export_dir, "render_model", halo_ver)

                map_index += 1
    #Halo3
        if (bpy.context.preferences.addons[__name__].preferences.halo3_map_path != ""):
            #create level/model report for H3
            halo_ver = "Halo3"
            format = ".map"
            Map_Root = bpy.context.preferences.addons[__name__].preferences.halo3_map_path
            
            map_index = 0
            
            #LEVELS
            #clear all data from the tags_report.txt file within the Export Directory
            tags_report_path = os.path.join(export_dir, halo_ver + '_level_report.txt')

            report_dir = os.path.dirname(tags_report_path)
            if not os.path.exists(report_dir):
                os.makedirs(report_dir)

            # Clear existing content in tags_report.txt
            with open(tags_report_path, 'w') as f:
                f.write("")
                
            #Loop through given .map files of selected game
            for map in glob.glob(os.path.join(Map_Root, '**/*' + format), recursive=True):
                #add a new line in the tags_report.txt file within the Export Directory with [map_index] at the front of the line and the directory to map right after
                # Write to tags_report.txt
                with open(tags_report_path, 'a') as f:
                    f.write(f"[{map_index}] {map}\n")
                    
                #call function called Reclaimer_Report() that takes map, export_dir, and "scenario_structure_bsp"
                Reclaimer_Report(map, export_dir, "scenario_structure_bsp", halo_ver)

                map_index += 1
            
            map_index = 0
            
            #MODELS
            #clear all data from the tags_report.txt file within the Export Directory
            tags_report_path = os.path.join(export_dir, halo_ver + '_model_report.txt')

            report_dir = os.path.dirname(tags_report_path)
            if not os.path.exists(report_dir):
                os.makedirs(report_dir)
            
            # Clear existing content in tags_report.txt
            with open(tags_report_path, 'w') as f:
                f.write("")
                
            #Loop through given .map files of selected game
            for map in glob.glob(os.path.join(Map_Root, '**/*' + format), recursive=True):
                #add a new line in the tags_report.txt file within the Export Directory with [map_index] at the front of the line and the directory to map right after
                # Write to tags_report.txt
                with open(tags_report_path, 'a') as f:
                    f.write(f"[{map_index}] {map}\n")
                    
                #call function called Reclaimer_Report() that takes map, export_dir, and "scenario_structure_bsp"
                Reclaimer_Report(map, export_dir, "render_model", halo_ver)

                map_index += 1
    #Halo3ODST
        if (bpy.context.preferences.addons[__name__].preferences.halo3odst_map_path != ""):
            #create level/model report for H3ODST
            halo_ver = "Halo3ODST"
            format = ".map"
            Map_Root = bpy.context.preferences.addons[__name__].preferences.halo3odst_map_path
            
            map_index = 0
            
            #LEVELS
            #clear all data from the tags_report.txt file within the Export Directory
            tags_report_path = os.path.join(export_dir, halo_ver + '_level_report.txt')

            report_dir = os.path.dirname(tags_report_path)
            if not os.path.exists(report_dir):
                os.makedirs(report_dir)
            
            # Clear existing content in tags_report.txt
            with open(tags_report_path, 'w') as f:
                f.write("")
                
            #Loop through given .map files of selected game
            for map in glob.glob(os.path.join(Map_Root, '**/*' + format), recursive=True):
                #add a new line in the tags_report.txt file within the Export Directory with [map_index] at the front of the line and the directory to map right after
                # Write to tags_report.txt
                with open(tags_report_path, 'a') as f:
                    f.write(f"[{map_index}] {map}\n")
                    
                #call function called Reclaimer_Report() that takes map, export_dir, and "scenario_structure_bsp"
                Reclaimer_Report(map, export_dir, "scenario_structure_bsp", halo_ver)

                map_index += 1
            
            map_index = 0
            
            #MODELS
            #clear all data from the tags_report.txt file within the Export Directory
            tags_report_path = os.path.join(export_dir, halo_ver + '_model_report.txt')

            report_dir = os.path.dirname(tags_report_path)
            if not os.path.exists(report_dir):
                os.makedirs(report_dir)
            
            # Clear existing content in tags_report.txt
            with open(tags_report_path, 'w') as f:
                f.write("")
                
            #Loop through given .map files of selected game
            for map in glob.glob(os.path.join(Map_Root, '**/*' + format), recursive=True):
                #add a new line in the tags_report.txt file within the Export Directory with [map_index] at the front of the line and the directory to map right after
                # Write to tags_report.txt
                with open(tags_report_path, 'a') as f:
                    f.write(f"[{map_index}] {map}\n")
                    
                #call function called Reclaimer_Report() that takes map, export_dir, and "scenario_structure_bsp"
                Reclaimer_Report(map, export_dir, "render_model", halo_ver)

                map_index += 1
                
    #HaloReach
        if (bpy.context.preferences.addons[__name__].preferences.haloreach_map_path != ""):
            #create level/model report for HReach
            halo_ver = "HaloReach"
            format = ".map"
            Map_Root = bpy.context.preferences.addons[__name__].preferences.haloreach_map_path
            
            map_index = 0
            
            #LEVELS
            #clear all data from the tags_report.txt file within the Export Directory
            tags_report_path = os.path.join(export_dir, halo_ver + '_level_report.txt')

            report_dir = os.path.dirname(tags_report_path)
            if not os.path.exists(report_dir):
                os.makedirs(report_dir)
            
            # Clear existing content in tags_report.txt
            with open(tags_report_path, 'w') as f:
                f.write("")
                
            #Loop through given .map files of selected game
            for map in glob.glob(os.path.join(Map_Root, '**/*' + format), recursive=True):
                #add a new line in the tags_report.txt file within the Export Directory with [map_index] at the front of the line and the directory to map right after
                # Write to tags_report.txt
                with open(tags_report_path, 'a') as f:
                    f.write(f"[{map_index}] {map}\n")
                    
                #call function called Reclaimer_Report() that takes map, export_dir, and "scenario_structure_bsp"
                Reclaimer_Report(map, export_dir, "scenario_structure_bsp", halo_ver)

                map_index += 1
            
            map_index = 0
            
            #MODELS
            #clear all data from the tags_report.txt file within the Export Directory
            tags_report_path = os.path.join(export_dir, halo_ver + '_model_report.txt')

            report_dir = os.path.dirname(tags_report_path)
            if not os.path.exists(report_dir):
                os.makedirs(report_dir)
            
            # Clear existing content in tags_report.txt
            with open(tags_report_path, 'w') as f:
                f.write("")
                
            #Loop through given .map files of selected game
            for map in glob.glob(os.path.join(Map_Root, '**/*' + format), recursive=True):
                #add a new line in the tags_report.txt file within the Export Directory with [map_index] at the front of the line and the directory to map right after
                # Write to tags_report.txt
                with open(tags_report_path, 'a') as f:
                    f.write(f"[{map_index}] {map}\n")
                    
                #call function called Reclaimer_Report() that takes map, export_dir, and "scenario_structure_bsp"
                Reclaimer_Report(map, export_dir, "render_model", halo_ver)

                map_index += 1  

    #Halo4
        if (bpy.context.preferences.addons[__name__].preferences.halo4_map_path != ""):
            #create level/model report for H4
            halo_ver = "Halo4"
            format = ".map"
            Map_Root = bpy.context.preferences.addons[__name__].preferences.halo4_map_path
            
            map_index = 0
            
            #LEVELS
            #clear all data from the tags_report.txt file within the Export Directory
            tags_report_path = os.path.join(export_dir, halo_ver + '_level_report.txt')

            report_dir = os.path.dirname(tags_report_path)
            if not os.path.exists(report_dir):
                os.makedirs(report_dir)
            
            # Clear existing content in tags_report.txt
            with open(tags_report_path, 'w') as f:
                f.write("")
                
            #Loop through given .map files of selected game
            for map in glob.glob(os.path.join(Map_Root, '**/*' + format), recursive=True):
                #add a new line in the tags_report.txt file within the Export Directory with [map_index] at the front of the line and the directory to map right after
                # Write to tags_report.txt
                with open(tags_report_path, 'a') as f:
                    f.write(f"[{map_index}] {map}\n")
                    
                #call function called Reclaimer_Report() that takes map, export_dir, and "scenario_structure_bsp"
                Reclaimer_Report(map, export_dir, "scenario_structure_bsp", halo_ver)

                map_index += 1
            
            map_index = 0
            
            #MODELS
            #clear all data from the tags_report.txt file within the Export Directory
            tags_report_path = os.path.join(export_dir, halo_ver + '_model_report.txt')

            report_dir = os.path.dirname(tags_report_path)
            if not os.path.exists(report_dir):
                os.makedirs(report_dir)
            
            # Clear existing content in tags_report.txt
            with open(tags_report_path, 'w') as f:
                f.write("")
                
            #Loop through given .map files of selected game
            for map in glob.glob(os.path.join(Map_Root, '**/*' + format), recursive=True):
                #add a new line in the tags_report.txt file within the Export Directory with [map_index] at the front of the line and the directory to map right after
                # Write to tags_report.txt
                with open(tags_report_path, 'a') as f:
                    f.write(f"[{map_index}] {map}\n")
                    
                #call function called Reclaimer_Report() that takes map, export_dir, and "scenario_structure_bsp"
                Reclaimer_Report(map, export_dir, "render_model", halo_ver)

                map_index += 1
                
    #Halo5
        if (bpy.context.preferences.addons[__name__].preferences.halo5_map_path != ""):
            #create level/model report for H5
            halo_ver = "Halo5"
            format = ".module"
            Map_Root = bpy.context.preferences.addons[__name__].preferences.halo5_map_path
            
            map_index = 0
            
            #LEVELS
            #clear all data from the tags_report.txt file within the Export Directory
            tags_report_path = os.path.join(export_dir, halo_ver + '_level_report.txt')

            report_dir = os.path.dirname(tags_report_path)
            if not os.path.exists(report_dir):
                os.makedirs(report_dir)
            
            # Clear existing content in tags_report.txt
            with open(tags_report_path, 'w') as f:
                f.write("")
                
            #Loop through given .map files of selected game
            for map in glob.glob(os.path.join(Map_Root, '**/*' + format), recursive=True):
                #add a new line in the tags_report.txt file within the Export Directory with [map_index] at the front of the line and the directory to map right after
                # Write to tags_report.txt
                with open(tags_report_path, 'a') as f:
                    f.write(f"[{map_index}] {map}\n")
                    
                #call function called Reclaimer_Report() that takes map, export_dir, and "scenario_structure_bsp"
                Reclaimer_Report(map, export_dir, "scenario_structure_bsp", halo_ver)

                map_index += 1
            
            map_index = 0
            
            #MODELS
            #clear all data from the tags_report.txt file within the Export Directory
            tags_report_path = os.path.join(export_dir, halo_ver + '_model_report.txt')

            report_dir = os.path.dirname(tags_report_path)
            if not os.path.exists(report_dir):
                os.makedirs(report_dir)
            
            # Clear existing content in tags_report.txt
            with open(tags_report_path, 'w') as f:
                f.write("")
                
            #Loop through given .map files of selected game
            for map in glob.glob(os.path.join(Map_Root, '**/*' + format), recursive=True):
                #add a new line in the tags_report.txt file within the Export Directory with [map_index] at the front of the line and the directory to map right after
                # Write to tags_report.txt
                with open(tags_report_path, 'a') as f:
                    f.write(f"[{map_index}] {map}\n")
                    
                #call function called Reclaimer_Report() that takes map, export_dir, and "scenario_structure_bsp"
                Reclaimer_Report(map, export_dir, "render_model", halo_ver)

                map_index += 1
    
#update Settings.JSON file for data folder    
def update_json_file(file_path, new_data_folder_path):
    # Step 1: Read the JSON file into a Python dictionary
    with open(file_path, 'r') as f:
        json_data = json.load(f)
    
    try:
        # Navigate to the specific section
        # Update the "DataFolder" value
        json_data["PluginSettings"]["Reclaimer.Plugins.BatchExtractPlugin"]["DataFolder"] = new_data_folder_path
        
        # Write the updated dictionary back to the JSON file
        with open(file_path, 'w') as f:
            json.dump(json_data, f, indent=4)
    except KeyError as e:
        print(f"KeyError: {e}. Please ensure that the JSON structure is correct.")


class CR4B_FileListUI(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        file_name_without_extension = os.path.splitext(item.name)[0] # This will now have the modified name
        layout.prop(item, "select", text=file_name_without_extension)

#import file panel
class CR4BImportPanel(bpy.types.Panel):
    bl_label = "CR4B Import Tool"
    bl_idname = "OBJECT_PT_CR4B_Import_Tool"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'CR4B Tool'
    bl_order = 2

    @classmethod
    def poll(cls, context):
        return context.scene.cr4b_show_import_menu

    def draw(self, context):
        layout = self.layout

        # Conditional display of file scanning and importing options
        if context.scene.cr4b_show_import_menu:
            
            layout.operator("cr4b.create_model_report", text="Create Model Reports")
            
            #new row
            row = layout.row(align=True)    
            
            #label and dropdown for Halo Game
            row.label(text="Halo Title:")
            row.prop(context.scene, "halo_version_dropdown", text="")

            #new row
            row = layout.row(align=True)

            #label and dropdown for File Format
            row.label(text="File Format:")
            row.prop(context.scene, "file_format_dropdown", text="")
            
            if (context.scene.file_format_dropdown == "ass/jms"):
                layout.row().label(text="Needs: Halo Asset Blender Toolset", icon='INFO')
            elif (context.scene.file_format_dropdown == "amf"):
                layout.row().label(text="Needs: CLI Reclaimer + Amf Importer", icon='INFO')
            else:
                layout.row().label(text="Needs: CLI Reclaimer", icon='INFO')
            
            layout.row().label(text="Scan for Files:")
            row = layout.row(align=True)
            row.operator("cr4b.scan_scenario_structure_bsp", text="Levels")
            row.operator("cr4b.scan_render_model", text="Models/Props")

            # Check if the last selected tag is one of the desired options
            if context.scene.cr4b_last_tag in ("Halo CE", "Halo 2", "Halo 3", "Halo 3: ODST", "Halo Reach", "Halo 4", "Halo 5"):
                # Create a box for the header
                box = layout.box()
                # Create a row for the header
                header_row = box.row()
                # Align the label to the center of the row
                header_row.alignment = 'CENTER'
                # Add the label with the text of the last selected tag
                header_row.label(text= (context.scene.cr4b_last_tag + context.scene.cr4b_header_suffix))

            # File list section
            layout.template_list(
                "CR4B_FileListUI", "",
                context.scene, "cr4b_file_list",
                context.scene, "cr4b_file_list_index",
                rows=5
            )

            layout.operator("cr4b.import_file", text="Import File")

#Panel Properties
class CR4BAddonPanel(bpy.types.Panel):
    bl_label = "CR4B Tool"
    bl_idname = "OBJECT_PT_CR4B_Tool"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'CR4B Tool'
    bl_order = 1

    def draw(self, context):
        layout = self.layout
        

        #Area on Panel for Appending node groups
        layout.row().label(text="Install Modules [Run as Admin]")
        layout.operator("myaddon.install_py360convert")
        layout.row().label(text="Only required once ever", icon='INFO')
       
        layout.row().label(text="")
        
        
        # Checkbox property
        layout.prop(context.scene, "cr4b_show_import_menu")
        
        #Area on Panel for Starting CR4B Tool
        layout.row().label(text="Select Tags to use")
        layout.row().prop(context.scene, "tag_dropdown")
        layout.row().label(text="Texture Image Format")
        layout.row().prop(context.scene, "image_format_dropdown")
        layout.row().label(text="Select Colorspace to use")
        layout.row().prop(context.scene, "colorspace_dropdown")
        layout.prop(context.scene, "cr4b_save_to_file")
        layout.row().label(text="Start CR4B Tool")
        layout.row().operator("script.start_cr4b_tool")
        
        if context.scene.cr4b_tool_running:
            #Show Progress Label and Bar if CR4B Tool is running
            row = layout.row()
            split = row.split(factor=0.30, align=True)
            split.label(text="Progress:")
            split.prop(context.scene, "cr4b_progress", text="", slider=True)

def update_halo3_tag_path(self, context):
    log_to_file("inside halo3_tag_path update")
    # Do something when the value of halo3_tag_path is updated
    pass

def update_odst_tag_path(self, context):
    # Do something when the value of odst_tag_path is updated
    pass

def update_reach_tag_path(self, context):
    # Do something when the value of reach_tag_path is updated
    pass  
    
def update_export_path(self, context):
    # Do something when the value of reach_tag_path is updated
    pass     
    
def update_haloce_map_path(self, context):
    # Do something when the value of reach_tag_path is updated
    pass 

def update_halo2_map_path(self, context):
    # Do something when the value of reach_tag_path is updated
    pass 

def update_halo3_map_path(self, context):
    # Do something when the value of reach_tag_path is updated
    pass 

def update_halo3odst_map_path(self, context):
    # Do something when the value of reach_tag_path is updated
    pass 

def update_haloreach_map_path(self, context):
    # Do something when the value of reach_tag_path is updated
    pass 

def update_halo4_map_path(self, context):
    # Do something when the value of reach_tag_path is updated
    pass 

def update_halo5_map_path(self, context):
    # Do something when the value of reach_tag_path is updated
    pass 


     

def display_crab_ascii():
    log_to_file("   _.---.                       .---.")
    log_to_file("  '---,  `.___________________.'  _  `.")
    log_to_file("       )   ___________________   <_>  :")
    log_to_file("  .---'  .'   / <'     '> \   `.     .'")
    log_to_file("   `----'    (  / @   @ \  )    `---'")
    log_to_file("              \(_ _\_/_ _)/")
    log_to_file("            (\ `-/     \-' /)")
    log_to_file('             "===\     /==="')
    log_to_file("              .==')___(`==.  ")  
    log_to_file("             ' .='     `=.")
    log_to_file("Thank you for using Halo CR4B Tool!")
    log_to_file("Support: https://discord.gg/haloarchive")

class StartCR4BTool(bpy.types.Operator):
    bl_label = "Start CR4B Tool"
    bl_idname = "script.start_cr4b_tool"

    _timer = None

    def modal(self, context, event):
        if event.type == 'TIMER':
            try:
                progress = next(self.task)
                context.scene.cr4b_progress = progress
                if progress >= 100:
                    self.finish(context)
                    display_crab_ascii()
                    return {'FINISHED'}
            except StopIteration:
                self.finish(context)
                display_crab_ascii()
                return {'FINISHED'}

        return {'PASS_THROUGH'}

    def execute(self, context):
        filepath = context.preferences.addons[__name__].preferences.node_group_file
        node_group_name = "[APPEND] Halo Shader Categories" # replace with the name of your node group

        if node_group_name not in bpy.data.node_groups:
            with bpy.data.libraries.load(filepath) as (data_from, data_to):
                data_to.node_groups = [node_group_name]

        
        if context.scene.cr4b_save_to_file:
            file_path = bpy.context.preferences.addons[__name__].preferences.export_path + "[CR4B_console_log].txt"
            with open(file_path, 'w') as log_file:
                log_file.write("")  # Writing an empty string to wipe the file
        
        context.scene.cr4b_tool_running = True
        self.task = Start_CR4B_Tool()  # Create a generator object

        # Set up the timer for the modal operator
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def finish(self, context):
        context.scene.cr4b_tool_running = False  # Set the state to not running
        wm = context.window_manager
        wm.event_timer_remove(self._timer)

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        return {'CANCELLED'}


def update_dropdown(self, context):
    log_to_file("Selected Tags:", self.tag_dropdown)
    
def update_color_dropdown(self, context):
    log_to_file("Selected Colorspace:", self.colorspace_dropdown)
    
def update_halo3_tag_path(self, context):
    log_to_file("Halo 3 Tags Path:", self.halo3_tag_path)    
    context.scene.halo3_tag_path = self.halo3_tag_path

def update_odst_tag_path(self, context):
    log_to_file("Halo 3: ODST Tags Path:", self.odst_tag_path) 
    context.scene.odst_tag_path = self.odst_tag_path
    
def update_reach_tag_path(self, context):
    log_to_file("Halo Reach Tags Path:", self.reach_tag_path) 
    context.scene.reach_tag_path = self.reach_tag_path
  
def update_export_path(self, context):
    log_to_file("Export Path:", self.export_path) 
    context.scene.export_path = self.export_path  
    
def update_py360convert_path(self, context):
    log_to_file("Export Path:", self.py360convert_path) 
    context.scene.py360convert_path = self.py360convert_path     
    
def update_dropdown(self, context):
    # Clear file list when the dropdown changes
    context.scene.cr4b_file_list.clear()
    if (context.scene.cr4b_last_button == "render_model"):
        #load model list for given selection
        bpy.ops.cr4b.scan_render_model()
    
    elif (context.scene.cr4b_last_button == "scenario_structure_bsp"):
        #load level list for given selection
        bpy.ops.cr4b.scan_scenario_structure_bsp()
    
def register():
                    #Add-on Properties
    bpy.utils.register_class(CR4BAddonPreferences)
    #bpy.utils.register_class(TestAddonAppendNodeGroup)
    bpy.types.Scene.halo3_tag_path = bpy.props.StringProperty(name="Halo 3 Tags Directory", default="", update=update_halo3_tag_path)
    bpy.types.Scene.odst_tag_path = bpy.props.StringProperty(name="Halo 3: ODST Tags Directory", default="", update=update_odst_tag_path)
    bpy.types.Scene.reach_tag_path = bpy.props.StringProperty(name="Halo Reach Tags Directory", default="", update=update_reach_tag_path)
    bpy.types.Scene.export_path = bpy.props.StringProperty(name="Ripped Asset Export Directory", default="", update=update_export_path)
    bpy.types.Scene.py360convert_path = bpy.props.StringProperty(name="py360Convert Directory", default="", update=update_py360convert_path)
    bpy.types.Scene.cr4b_progress = bpy.props.FloatProperty(min=0.0, max=100.0, default=0.0, subtype='PERCENTAGE', description="CR4B Tool Progress")
    
    #Reclaimer path preferences
    bpy.types.Scene.reclaimer_path = bpy.props.StringProperty(name="Reclaimer CLI Directory", default="")
    
    #map files path preferences
    bpy.types.Scene.haloce_map_path = bpy.props.StringProperty(name="Halo CE .map Directory", default="", update=update_haloce_map_path)
    bpy.types.Scene.halo2_map_path = bpy.props.StringProperty(name="Halo 2 .map Directory", default="", update=update_halo2_map_path)
    bpy.types.Scene.halo3_map_path = bpy.props.StringProperty(name="Halo 3 .map Directory", default="", update=update_halo3_map_path)
    bpy.types.Scene.halo3odst_map_path = bpy.props.StringProperty(name="Halo 3 ODST .map Directory", default="", update=update_halo3odst_map_path)
    bpy.types.Scene.haloreach_map_path = bpy.props.StringProperty(name="Halo Reach .map Directory", default="", update=update_haloreach_map_path)
    bpy.types.Scene.halo4_map_path = bpy.props.StringProperty(name="Halo 4 .map Directory", default="", update=update_halo4_map_path)
    bpy.types.Scene.halo5_map_path = bpy.props.StringProperty(name="Halo 5 .map Directory", default="", update=update_halo5_map_path)
    
    bpy.utils.register_class(CR4B_FileItem)
    bpy.types.Scene.cr4b_file_list = bpy.props.CollectionProperty(type=CR4B_FileItem)
    
    bpy.utils.register_class(CR4B_ScanScenarioStructureBSP)
    bpy.utils.register_class(CR4B_ScanRenderModel)
    
    bpy.utils.register_class(CR4B_ImportFile)
    
    bpy.utils.register_class(CR4BProgressUpdater)
    
    bpy.utils.register_class(CR4B_FileListUI)
    bpy.types.Scene.cr4b_file_list_index = bpy.props.IntProperty()
    
    bpy.types.Scene.cr4b_tool_running = bpy.props.BoolProperty(default=False, description="CR4B Tool Running State")
    
    bpy.utils.register_class(InstallPy360ConvertOperator)
    
    # Property for storing the header suffix
    bpy.types.Scene.cr4b_header_suffix = bpy.props.StringProperty(default="")
    
    #create model reports
    bpy.utils.register_class(CR4B_CreateModelReport)
    
    
    
                    #Panel Properties
    #Light Tool Properties
    #bpy.utils.register_class(SpotLightProperties)
    #bpy.utils.register_class(AddSpotLightOperator)
    #bpy.types.Scene.spot_light_props = bpy.props.PointerProperty(type=SpotLightProperties)
    
    #CR4B Tool Properties
    #bpy.types.Scene.image_format = bpy.props.StringProperty(name="Image Format", default='.png')
    bpy.types.Scene.tag_dropdown = bpy.props.EnumProperty(
        items=[
            ("Halo 3", "Halo 3", "Tags for Halo 3"),
            ("Halo 3: ODST", "Halo 3: ODST", "Tags for Halo 3: ODST"),
            ("Halo Reach", "Halo Reach", "Tags for Halo Reach")
        ],
        name="Tags",
        description="Choose Tags to use for this Blender scene",
        #update=update_dropdown
    )
    bpy.types.Scene.colorspace_dropdown = bpy.props.EnumProperty(
        items=[
            ("Blender", "Blender", "Default Blender Colorspace"),
            ("AGX", "AGX", "AGX Colorspace")
        ],
        name="Colors",
        description="Choose Colorspace to use for this Blender scene",
        update=update_color_dropdown
    )
    
    # Tracking property for last button clicked
    bpy.types.Scene.cr4b_last_button = bpy.props.StringProperty(default="")

    # Checkbox property for showing .ass/jms import menu
    bpy.types.Scene.cr4b_show_import_menu = bpy.props.BoolProperty(
        name="Show model import menu",
        default=False
    )

    bpy.types.Scene.cr4b_last_tag = bpy.props.StringProperty(name="Last Selected Tag")

    # Dropdown property for selecting the image format
    bpy.types.Scene.image_format_dropdown = bpy.props.EnumProperty(
        name="Format",
        description="Select the image format",
        items=[
            ('.png', '.png', 'PNG Image Format'),
            ('.tif', '.tif', 'TIFF Image Format')
        ],
        default='.png'
    )

    bpy.types.Scene.cr4b_save_to_file = bpy.props.BoolProperty(
        name="Save Console Logging to file",
        default=False
    )
    
    bpy.types.Scene.halo_version_dropdown = bpy.props.EnumProperty(
        name="Halo Version",
        items=[
            ("Halo CE", "Halo CE", ""),
            ("Halo 2", "Halo 2", ""),
            ("Halo 3", "Halo 3", ""),
            ("Halo 3: ODST", "Halo 3: ODST", ""),
            ("Halo Reach", "Halo Reach", ""),
            ("Halo 4", "Halo 4", ""),
            ("Halo 5", "Halo 5", "")
        ],
        update=update_dropdown,
        description="Select Halo game to search"
    )
    
    bpy.types.Scene.file_format_dropdown = bpy.props.EnumProperty(
        name="File Format",
        items=get_file_format_items,
        update=update_dropdown,
        description="Select the file format"
    )
    
    #import model panel
    bpy.utils.register_class(CR4BImportPanel)
    bpy.utils.register_class(CR4BAddonPanel)
    bpy.utils.register_class(StartCR4BTool)

def unregister():
     
    
                    #Add-On Properties
    del bpy.types.Scene.halo3_tag_path
    del bpy.types.Scene.odst_tag_path
    del bpy.types.Scene.reach_tag_path
    del bpy.types.Scene.export_path
    del bpy.types.Scene.py360convert_path
    del bpy.types.Scene.cr4b_progress

    #reclaimer path
    del bpy.types.Scene.reclaimer_path 

    #map directory
    del bpy.types.Scene.haloce_map_path 
    del bpy.types.Scene.halo2_map_path 
    del bpy.types.Scene.halo3_map_path
    del bpy.types.Scene.halo3odst_map_path
    del bpy.types.Scene.haloreach_map_path
    del bpy.types.Scene.halo4_map_path
    del bpy.types.Scene.halo5_map_path

    bpy.utils.unregister_class(CR4B_FileItem)
    del bpy.types.Scene.cr4b_file_list
    
    bpy.utils.unregister_class(CR4B_ScanScenarioStructureBSP)
    bpy.utils.unregister_class(CR4B_ScanRenderModel)

    bpy.utils.unregister_class(CR4B_ImportFile)

    bpy.utils.unregister_class(CR4BProgressUpdater)

    bpy.utils.unregister_class(CR4B_FileListUI)
    del bpy.types.Scene.cr4b_file_list_index

    bpy.utils.unregister_class(InstallPy360ConvertOperator)

    # Tracking property for last button clicked
    del bpy.types.Scene.cr4b_last_button

    # Checkbox property for showing .ass/jms import menu
    del bpy.types.Scene.cr4b_show_import_menu

    del bpy.types.Scene.cr4b_last_tag

    # Dropdown property for selecting the image format
    del bpy.types.Scene.image_format_dropdown

    # Property for storing the header suffix
    del bpy.types.Scene.cr4b_header_suffix

    #console logging
    del bpy.types.Scene.cr4b_save_to_file

    del bpy.types.Scene.halo_version_dropdown
    
    del bpy.types.Scene.file_format_dropdown
    
    #create model reports
    bpy.utils.unregister_class(CR4B_CreateModelReport)
    
                    #Panel Properties
    #Light Tool Properties                
    #bpy.utils.unregister_class(SpotLightProperties)
    #bpy.utils.unregister_class(AddSpotLightOperator)  
    #del bpy.types.Scene.spot_light_props
                    
    #CR4B Tool Properties
    bpy.utils.unregister_class(CR4BAddonPreferences)

    #bpy.utils.unregister_class(TestAddonAppendNodeGroup)
    bpy.utils.unregister_class(StartCR4BTool)
    bpy.utils.unregister_class(CR4BAddonPanel)
    bpy.utils.unregister_class(CR4BImportPanel)

if __name__ == "__main__":
    register()





#TODO STILL

#FIX SUPPORT FOR PREFIXES TO TELL WHERE .SHADER FILES SHOULD COME FROM

#If default values are needed, spawn them and make sure they get plugged in!



# FIX PER PIXEL ENVIRNMENT MAP TINT COLOR

# Add extra import button for "shooting" objects onto the scene using an active camera

#Add a toggle so that if the code were to break, it continues instead. better user experience

# SOLVE HUGE BUG where when there are multiple .shader files that match, it reads the data from the wrong one
#(pymat_copy.e for the fusion coil)!
#  tends to cause default textures to be used when they shouldn't be

#add .biped tag reading support to get the Primary and Secondary Change Color values
#decal support - make them not cast shadows
#make sure time period for functions is grabbing
#add more support for default values plugging in

#add function support for bitmaps (like base_maps, detail_maps, etc)
#make list of ALL bitmaps that have "unknown" curve option
#base_map gamma is attaching to two points
# -terrain_shader support
# -foliage_shader support
# -if .bitmapfile doesn't exist when reading curve data then replace directory with default option
# -more edgecases for other shader combinations
# -self_illum support
# -self_illum detail support
#mirror mapping like this: https://cdn.discordapp.com/attachments/830517591184506972/1061725239018520626/image.png
#function support
#animations support?





























    
        #TexImage.bl_idname = "TexImage" + str(bitm)
        #TexImage.image = 
 

# def image_has_alpha(img):
    # b = 32 if img.is_float else 8
    # return (
        # img.depth == 2b or   # Grayscale+Alpha
        # img.depth == 4b      # RGB+Alpha
    # )




 
    #i.specular_color = 
    #i.specular_intensity =
    
    
    # # accessing all the nodes in that material
    # nodes = material.node_tree.nodes
            
    # # you can find the specific node by it's name
    # noise_node = nodes.get("Noise Texture")

    # # available inputs of that node
    # # log_to_file([x.identifier for x in noise_node.inputs])
    # # ['Vector', 'W', 'Scale', 'Detail', 'Distortion']

    # # change value of "W"
    # noise_node.inputs.get("W").default_value = 1

# # Since you want a Principled BSDF and the Material Output node
# # in your material, we can re-use the nodes that are automatically
# # created.
# principled_bsdf = nodes.get("Principled BSDF")
# material_output = nodes.get("Material Output")

# # Create Image Texture node and load the base color texture
# base_color = nodes.new('ShaderNodeTexImage')
# base_color.image = bpy.data.images.load(base_color_path)

# # Create Image Texture node and load the normal map
# normal_tex = nodes.new('ShaderNodeTexImage')
# normal_tex.image = bpy.data.images.load(normal_map_path)

# # Set the color space to non-color, since normal maps contain
# # the direction of the surface normals and not color data
# normal_tex.image.colorspace_settings.name = "Non-Color"

# # Create the Displacement node
# displacement = nodes.new('ShaderNodeDisplacement')

# # Connect the base color texture to the Principled BSDF
# links.new(principled_bsdf.inputs["Base Color"], base_color.outputs["Color"])

# # Connect the normal map to the Displacement node
# links.new(displacement.inputs["Height"], normal_tex.outputs["Color"])

# # Connect the Displacement node to the Material Output node
# links.new(material_output.inputs["Displacement"], displacement.outputs["Displacement"])



#gray_50_percent
    #base_map
    #self_illum
    #
    #
    #
  
#default_detail used
    #
    #
    #
    #
    #
    #

#CREATE NODE GROUP FOR CHIEFS SHADER
# You can do something like this: create the node group instance and set the existing node group as node tree for this new instance.

# import bpy

# C = bpy.context

# def instantiate_group(nodes, data_block_name):
    # group = nodes.new(type='ShaderNodeGroup')
    # group.node_tree = bpy.data.node_groups[data_block_name]
    # return group

# instantiate_group(C.object.material_slots[0].material.node_tree.nodes, 'NodeGroup')

#BITMAP OPTIONS
#options for bitmap_cruve
    #unknown
    #xRGB (gamma about 2.0)      gamma is really about 1.95
    #gamme 2.0
    #linear
    #sRGB


#IMPORT IMAGE TEXTURE NODE
#Import python
# import bpy
# from bpy import context, data, ops


# mat = bpy.data.materials.new(name="New_Mat")
# mat.use_nodes = True
# bsdf = mat.node_tree.nodes["Principled BSDF"]
# texImage = mat.node_tree.nodes.new('ShaderNodeTexImage')
# texImage.image = bpy.data.images.load("C:\\Users\\myName\\Downloads\\Textures\\Downloaded\\flooring5.jpg")
# mat.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])

# ob = context.view_layer.objects.active

# # Assign it to object
# if ob.data.materials:
    # ob.data.materials[0] = mat
# else:
    # ob.data.materials.append(mat)




#SHADER OPTIONS
#options for albedo
    # default
    # detail_blend
    # constant_color
    # two_change_color
    # four_change_color
    # three_detail_blend
    # two_detail_overlay
    # two_detail
    # color_mask
    # two_detail_black_point
    # two_change_color_anim_overlay
    # chameleon
    # two_change_color_chameleon
    # chameleon_masked
    # color_mask_hard_light
    # two_change_color_tex_overlay
    # chameleon_albedo_masked
    # custom_cube
    # two_color
    # scrolling_cube_mask
    # scrolling_cube
    # scrolling_texture_uv
    # texture_from_misc
#optons for bump_mapping
    # off
    # standard
    # detail
    # detail_masked
    # detail_plus_detail_masked
    # detail_unorm
#options for alpha_test
    # none
    # simple
#options for specular_map
    # no_specular_mask
    # specular_mask_from_diffuse
    # specular_mask_from_texture
    # specular_mask_from_color_texture
#options for material_model
    # diffuse_only
    # cook_torrance
    # two_lobe_phong
    # foliage
    # none
    # glass
    # organism
    # single_lobe_phong
    # car_paint
    # cook_torrance_custom_cube
    # cook_torrance_pbr_maps
    # cook_torrance_rim_fresnel
    # cook_torrance_scrolling_cube
    # cook_torrance_from_albedo
#options for environment_map
    # none
    # per_pixel
    # dynamic
    # from_flat_texture
    # custom_map
    # from_flat_exture_as_cubemap
#options for self_illumination
    # off
    # simple
    # 3_channel_self_illum
    # plasma
    # from_diffuse
    # illum_detail
    # meter
    # self_illum_times_diffuse
    # simple_with_alpha_mask
    # simple_four_change_color
    # illum_detail_world_space_four_cc
    # illum_change_color
#options for blend_mode
    # opaque
    # additive
    # multiply
    # alpha_blend
    # double_multiply
    # pre_multiplied_alpha
#options for parallax
    # off
    # simple
    # interpolated
    # simple_detail
#options for misc
    # first_person_never
    # first_person_sometimes
    # first_person_always
    # first_person_never_w/rotating_bitmaps




#loop through every model in blender scene
    #loop through each material slot
        #find .shader file with matching name
        #build class object with all that data
            #list
                #bitmap type (base_map, bump_map, etc)
                #bitmap name
                #bitmap directory
            #color tint values
            #scaling values for textures
        #spawn image texture for each bitmap found
        #create h3 shader by chief 
        
        
        
        
        
        
        #function notes
        
# 92 bytes after main offset is thr name of the function
# 36 bytes after name might be type of function
    # b'\x00' is basic
    # b'\x01' is basic?
    # b'\x08'  is curve 
    # b'\x03' is periodic
    # b'\x09' is exponent
    # b'\x02' is transition

#basic function
    # Time Period is 44 bytes after main offset
    # if 12 bytes in after function name is "tsgt" then no range name
        # if no range name, mark of tsgt_function_offset to be 12 bytes from function name
            # Min value is 28 bytes after tsgt_function_offset
            # Max value is 32 bytes after tsgt_function_offset
            # range toggle is at 25 bytes from tsgt_function_offset
                #int of 24 is toggle off
                #int of 25 is toggle on
            # function type/option is at 24 bytes from tsgt_function_offset
    # if 12 bytes in from function name is not "tsgt" then range name exists
        # set tsgt_function_offset to be after the end of range name - save it all as a string then use split() to chop off at 'tsgt' and save the front values as the range name and then find length of that for true offset start
            # Min value is 28 bytes after tsgt_function_offset
            # Max value is 32 bytes after tsgt_function_offset
            # range toggle is at 25 bytes from tsgt_function_offset
                #int of 24 is toggle off
                #int of 25 is toggle on
            # function type/option is at 24 bytes from tsgt_function_offset 
            
#curve function
    # Time Period is 44 bytes after main offset
    # if 12 bytes in after function name is "tsgt" then no range name
        # if no range name, mark start of tsgt_function_offset to be 12 bytes from function name
            # Min value is 28 bytes after tsgt_function_offset
            # Max value is 32 bytes after tsgt_function_offset
            # range toggle is at 25 bytes from tsgt_function_offset
                #int of 24 is toggle off
                #int of 25 is toggle on
            # function type/option is at 24 bytes from tsgt_function_offset
    # if 12 bytes in from function name is not "tsgt" then range name exists
        # set tsgt_function_offset to be after the end of range name - save it all as a string then use split() to chop off at 'tsgt' and save the front values as the range name and then find length of that for true offset start
            # Min value is 28 bytes after tsgt_function_offset
            # Max value is 32 bytes after tsgt_function_offset
            # range toggle is at 25 bytes from tsgt_function_offset
                #int of 24 is toggle off
                #int of 25 is toggle on
            # function type/option is at 24 bytes from tsgt_function_offset 
 
 
#periodic options:
# 0 - one
# 1 - zero
# 2 - cosine
# 3 - cosine [variable period]
# 4 - diagonal wave
# 5 - diagonal wave [variable period]
# 6 - slide
# 7 - slide [variable period]    
# 8 - noise
# 9 - jitter
# 10 - wander
# 11 - spark          
       
#periodic function
    # Time Period is 44 bytes after main offset
    # if 12 bytes in after function name is "tsgt" then no range name
        # range toggle is at 25 bytes from tsgt_function_offset
            #int of 24 is toggle off
            #int of 25 is toggle on
        # function type/option is at 24 bytes from tsgt_function_offset
        # Min value of chart is 28 bytes after tsgt_function_offset
        # Max value of chart is 32 bytes after tsgt_function_offset
        
        # Left Side function is at 56 bytes after tsgt_function_offset is 1 byte int
        # Left Side frequency value is at 60 bytes after tsgt_function_offset
        # Left Side phase value is at 64 bytes after tsgt_function_offset
        # Left Side min value is at 68 bytues after tsgt_function_offset
        # Left Side max value is at 72 bytes after tsgt_function_offset
        # Right Side function is at 76 bytes after tsgt_function_offset is 1 byte int
        # Right Side frequency value is at 80 bytes after tsgt_function_offset
        # Right side phase value is at 84 bytes after tsgt_function_offset
        # Right side min value is at 88 bytes after tsgt_function_offset
        # Right side max value is at 92 bytes after tsgt_function_offset
        # All abvoe info seems to repeat for 2nd line at 80 bytes from tsgt_function_offset
    # if 12 bytes in from function name is not "tsgt" then range name exists
        # set tsgt_function_offset to be after the end of range name - save it all as a string then use split() to chop off at 'tsgt' and save the front values as the range name and then find length of that for true offset start
        # range toggle is at 25 bytes from tsgt_function_offset
            #int of 24 is toggle off
            #int of 25 is toggle on
        # function type/option is at 24 bytes from tsgt_function_offset
        # Min value of chart is 28 bytes after tsgt_function_offset
        # Max value of chart is 32 bytes after tsgt_function_offset
        # Left Side function is at 56 bytes after tsgt_function_offset is 1 byte int
        # Left Side frequency value is at 60 bytes after tsgt_function_offset
        # Left Side phase value is at 64 bytes after tsgt_function_offset
        # Left Side min value is at 68 bytues after tsgt_function_offset
        # Left Side max value is at 72 bytes after tsgt_function_offset
        # Right Side function is at 76 bytes after tsgt_function_offset is 1 byte int
        # Right Side frequency value is at 80 bytes after tsgt_function_offset
        # Right side phase value is at 84 bytes after tsgt_function_offset
        # Right side min value is at 88 bytes after tsgt_function_offset
        # Right side max value is at 92 bytes after tsgt_function_offset
        # All abvoe info seems to repeat for 2nd line at 80 bytes from tsgt_function_offset        
       
    
       
#exponent function
    # Time Period is 44 bytes after main offset
    # if 12 bytes in after function name is "tsgt" then no range name
        # function type/option is at 24 bytes from tsgt_function_offset        
        # range toggle is at 25 bytes from tsgt_function_offset
            #int of 24 is toggle off
            #int of 25 is toggle on
        # Min value of chart is 28 bytes after tsgt_function_offset
        # Max value of chart is 32 bytes after tsgt_function_offset
        
        # Left Side Min value is at 56 bytes from tsgt_function_offset
        # Left Side Max Value is at 60 bytes from tsgt_function_offset
        # Left Side Exponent Value is at 64 bytes from tsgt_function_offset
        # Right Side Min Value is at 68 bytes from tsgt_function_offset
        # Right Side Max value is at 72 bytes from tsgt_function_offset
        # Right Side Exponent value is at 76 bytes from tsgt_function_offset
        # All abvoe info seems to repeat for 2nd line at 80 bytes from tsgt_function_offset
    # if 12 bytes in from function name is not "tsgt" then range name exists
        # set tsgt_function_offset to be after the end of range name - save it all as a string then use split() to chop off at 'tsgt' and save the front values as the range name and then find length of that for true offset start
        # function type/option is at 24 bytes from tsgt_function_offset        
        # range toggle is at 25 bytes from tsgt_function_offset
            #int of 24 is toggle off
            #int of 25 is toggle on
        # Min value of chart is 28 bytes after tsgt_function_offset
        # Max value of chart is 32 bytes after tsgt_function_offset
        # Left Side Min value is at 56 bytes from tsgt_function_offset
        # Left Side Max Value is at 60 bytes from tsgt_function_offset
        # Left Side Exponent Value is at 64 bytes from tsgt_function_offset
        # Right Side Min Value is at 68 bytes from tsgt_function_offset
        # Right Side Max value is at 72 bytes from tsgt_function_offset
        # Right Side Exponent value is at 76 bytes from tsgt_function_offset
        # All abvoe info seems to repeat for 2nd line at 80 bytes from tsgt_function_offset
        
        
        
#transition options
# 0 - linear
# 1 - early
# 2 - very early
# 3 - late
# 4 - very late
# 5 - cosine
# 6 - one
# 7 - zero
        
#transition function
    # Time Period is 44 bytes after main offset
    # if 12 bytes in after function name is "tsgt" then no range name
        # function type/option is at 24 bytes from tsgt_function_offset
        # range toggle is at 25 bytes from tsgt_function_offset
            #int of 24 is toggle off
            #int of 25 is toggle on
        # Min value of chart is 28 bytes after tsgt_function_offset
        # Max value of chart is 32 bytes after tsgt_function_offset
        
        # Left Side function option at 56 bytes in from tsgt_function_offset and it is 1 byte int
        # Left Side Min value is at 60 bytes in from tsgt_function_offset
        # Left Side Max value is at 64 bytes in from tsgt_function_offset
        # Right Side function option is at 68 bytes in from tsgt_function_offset and it is 1 byte int
        # Right Side Min value is at 72 bytes in from tsgt_function_offset
        # Right Side max value is at 76 bytes in from tsgt_function_offset
        # All abvoe left/right info seems to repeat for 2nd line at 80 bytes from tsgt_function_offset
   
   # if 12 bytes in from function name is not "tsgt" then range name exists
        # set tsgt_function_offset to be after the end of range name - save it all as a string then use split() to chop off at 'tsgt' and save the front values as the range name and then find length of that for true offset start        
        # function type/option is at 24 bytes from tsgt_function_offset
        # range toggle is at 25 bytes from tsgt_function_offset
            #int of 24 is toggle off
            #int of 25 is toggle on
        # Min value of chart is 28 bytes after tsgt_function_offset
        # Max value of chart is 32 bytes after tsgt_function_offset
        # Left Side function option at 56 bytes in from tsgt_function_offset and it is 1 byte int
        # Left Side Min value is at 60 bytes in from tsgt_function_offset
        # Left Side Max value is at 64 bytes in from tsgt_function_offset
        # Right Side function option is at 68 bytes in from tsgt_function_offset and it is 1 byte int
        # Right Side Min value is at 72 bytes in from tsgt_function_offset
        # Right Side max value is at 76 bytes in from tsgt_function_offset
        # All abvoe left/right info seems to repeat for 2nd line at 80 bytes from tsgt_function_offset

