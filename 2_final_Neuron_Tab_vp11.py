import bpy
import bmesh

import numpy as np
from bpy.types import Operator
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector
import os
import time

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Operator,
                       AddonPreferences,
                       PropertyGroup,
                       )

import datetime
import math
from pathlib import Path

#####where will define all the bpy.context.scene attributes##########
#registration
bpy.types.Scene.username = bpy.props.StringProperty()
bpy.types.Scene.firstname = bpy.props.StringProperty()
bpy.types.Scene.lastname = bpy.props.StringProperty()
bpy.types.Scene.register_Status = bpy.props.StringProperty()



#login
bpy.types.Scene.username_Login = bpy.props.StringProperty()
bpy.types.Scene.login_Status = bpy.props.StringProperty()
bpy.types.Scene.login_Flag = bpy.props.BoolProperty()

#neuron ID picker
bpy.types.Scene.neuron_ID = bpy.props.StringProperty()
bpy.types.Scene.neuron_ID_Status = bpy.props.StringProperty()
bpy.types.Scene.labeled_Flag_ID = bpy.props.BoolProperty()
bpy.types.Scene.import_Neuron_Flag = bpy.props.BoolProperty()

#neuron username picker
bpy.types.Scene.status_picked = bpy.props.StringProperty()
bpy.types.Scene.neuron_username_Status = bpy.props.StringProperty()
bpy.types.Scene.username_neuron_ID = bpy.props.StringProperty()

#next available neuron picker
bpy.types.Scene.next_available_neuron_ID = bpy.props.StringProperty()
bpy.types.Scene.next_available_status = bpy.props.StringProperty()

#for the editing properties
bpy.types.Scene.last_Edited = bpy.props.StringProperty()
bpy.types.Scene.picked_Neuron_ID = bpy.props.StringProperty()
bpy.types.Scene.continue_edit_Status = bpy.props.StringProperty()
bpy.types.Scene.last_Status = bpy.props.StringProperty()
bpy.types.Scene.last_Edited_User = bpy.props.StringProperty()
bpy.types.Scene.load_local_status = bpy.props.StringProperty()



#for saving off the neuron:
bpy.types.Scene.status_To_Save = bpy.props.StringProperty()
bpy.types.Scene.percent_labeled = bpy.props.StringProperty()
bpy.types.Scene.complete_100_check = bpy.props.StringProperty()
bpy.types.Scene.complete_100_check_2 = bpy.props.StringProperty()
bpy.types.Scene.complete_100_check_save_flag = bpy.props.BoolProperty()

#for deleting
bpy.types.Scene.delete_Flag = bpy.props.BoolProperty()
bpy.types.Scene.delete_ID = bpy.props.StringProperty()
bpy.types.Scene.delete_status = bpy.props.StringProperty()




def reset_Scene_Variables(login_Flag=False):
    #registration
    bpy.context.scene.username = ""
    bpy.context.scene.firstname =""
    bpy.context.scene.lastname = ""
    bpy.context.scene.register_Status = ""
    
    
    
    #login
    
    bpy.context.scene.login_Status = ""
    if login_Flag == False:
        bpy.context.scene.login_Flag = False
        bpy.context.scene.username_Login = ""
    
    #neuron ID picker
    bpy.context.scene.neuron_ID = ""
    bpy.context.scene.neuron_ID_Status = ""
    bpy.context.scene.labeled_Flag_ID = False
    bpy.context.scene.import_Neuron_Flag = False

    #neuron username picker
    bpy.context.scene.status_picked = ""
    bpy.context.scene.neuron_username_Status = ""
    bpy.context.scene.username_neuron_ID = ""
    
    #next available picker
    bpy.context.scene.next_available_neuron_ID = ""
    bpy.context.scene.next_available_status = ""
    
    #for editing
    bpy.context.scene.last_Edited = ""
    bpy.context.scene.picked_Neuron_ID = ""
    bpy.context.scene.continue_edit_Status = ""
    bpy.context.scene.last_Status = ""
    bpy.context.scene.last_Edited_User  = ""
    
    #for saving off the neuron
    bpy.context.scene.status_To_Save = ""
    bpy.context.scene.percent_labeled = ""
    bpy.context.scene.complete_100_check = ""
    bpy.context.scene.complete_100_check_2 = ""
    bpy.context.scene.complete_100_check_save_flag = False

#for loading neurons
bpy.context.scene.load_local_status = ""
    
    #for deleting
    bpy.context.scene.delete_Flag = False
    bpy.context.scene.delete_ID = ""
    bpy.context.scene.delete_status = ""

def reset_Status_Flags():
    bpy.context.scene.register_Status = ""
    bpy.context.scene.neuron_ID_Status = ""
    bpy.context.scene.neuron_username_Status = ""
    bpy.context.scene.status_picked = ""
    bpy.context.scene.next_available_status = ""
    bpy.context.scene.delete_status = ""




def set_View():
    print("setting view back to original")
    
    lk = LabelKey()
    print("label Key table was created")
    
    #are that I want to make an allowance for: bpy.data.screens['Scripting'].areas
    
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            override = {'area': area, 'region': area.regions[-1]}
            #bpy.ops.view3d.view_pan(override, type='PANRIGHT')
            bpy.ops.view3d.view_lock_to_active(override)
            bpy.ops.view3d.view_lock_clear(override)
            
            #FOR SOME REASON ADDING THIS BEFORE IT HELPS GET IT CENTERED
            bpy.ops.view3d.view_all(override, center=False)
            
            
            #make sure can view all of the neuron
            bpy.ops.view3d.view_all(override, center=True)
            #way to set it:
            #1) User Persp
            bpy.ops.view3d.view_persportho(override)
            #2) Top Persp
            bpy.ops.view3d.viewnumpad(override,type='TOP')
            #3) Top Ortho
            bpy.ops.view3d.view_persportho(override)
            
            #putting at end just to make sure it works
            bpy.ops.view3d.view_all(override, center=False)

def edit_active_neuron():
    #check that there is an active object
    if(bpy.context.scene.objects.active == "None"):
        #set the status variable
        bpy.context.scene.continue_edit_Status = "No object is currently active!"
        return
    
    #get the name of the active neuron (if not then print out that no neuron is
    #currently selected
    name_of_active = bpy.context.scene.objects.active.name
    
    if("neuron" not in name_of_active):
        bpy.context.scene.continue_edit_Status = "Object selected is not neuron!"
        return

    bpy.ops.object.mode_set(mode='EDIT')
    #bpy.ops.mesh.select_all(action='TOGGLE')
    bpy.ops.mesh.select_all(action='DESELECT')
    
    #set the appropriate variables for the editing session
    ID = name_of_active[7:]
    bpy.context.scene.picked_Neuron_ID = name_of_active[7:]

    #go pull down the last time that the object was edited
#(SHOULD ALWAYS BE IN THE LABELS LIST)



reset_Status_Flags()
print("end of edit_active_neuron")


#receives the ID as a string of the neuron it wants
#AND MAKES SURE YOU ONLY CAN PULL DOWN YOUR OWN
def load_Neuron(ID):
    print("inside load Neuron")
    #create an object to the labels and the mesh_Table
    #already exist in labels_Table and mesh_Table
    username = bpy.context.scene.username_Login
    #get list of ID's from labeled to check if there
    username_labels_Table = (labels_Table & "author='"+ username + "'")
    labels_list = username_labels_Table.fetch("segment_id").tolist()
    
    from_Mesh_Flag = 0
    from_Labels_Flag = 0
    
    #convert ints to Strings
    if int(ID) not in labels_list:
        #don't need to get the labes because there are none
        from_Mesh_Flag = 1
        from_Labels_Flag = 0
    
    else:
        #don't need to push to labels table
        from_Mesh_Flag = 0
        from_Labels_Flag = 1
    
    #GOES THROUGH THE WHOLE PROCESS OF CREATING THE OBJECT AND IMPORTING IT
    
    
    #neuron_data = ((mesh_Table & "segment_ID="+ID).fetch(as_dict=True))[0]
    primary_key = dict(segmentation=1,decimation_ratio=0.35)
    neuron_data = ((ta3.Decimation & primary_key & "segment_ID="+ID).fetch(as_dict=True))[0]



verts = neuron_data['vertices'].astype(dtype=np.int32)
    faces = neuron_data['triangles'].astype(dtype=np.uint32)
    
    #*********Need to add in my own scale*****************#
    scale = 0.001
    
    #Makes the vertices as voxels and applies a scale to them
    not_centered_verts = [(x[0], x[2], x[1]) for x in (verts * scale).tolist()]
    #don't need the vertical count being added to the faces like in his because because
    new_faces = [(x[0], x[1], x[2]) for x in (faces).tolist()]
    
    offset = np.median(np.array(not_centered_verts), axis=0)
    print("offset = " + str(offset))
    new_verts = [(x[0] - offset[0], x[1] - offset[1], x[2] - offset[2]) for x in not_centered_verts]
    
    
    print("Length of vertices = " + str(len(new_verts)))
    print("Length of vertices = " + str(len(new_faces)))
    #-----------------END OF new way of importing using james cotton way------------------#
    mymesh = bpy.data.meshes.new("neuron-"+ID)
    mymesh.from_pydata(new_verts, [], new_faces)
    #object = bpy.data.objects.new(optional_Name, mesh)
    
    #uses the bmesh library to import:
    
    
    """ DOES THE SIMPLIFYING THAT I DON'T WANT ANYMORE
        bm = bmesh.new()
        bm.from_mesh(mymesh)
        print("Simplifying {}".format(len(bm.verts)))
        # bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0)
        #for i in range(5):
        #    bmesh.ops.smooth_vert(bm, verts=bm.verts, factor=0.5, use_axis_x=True, use_axis_y=True,
        #                          use_axis_z=True)  # , mirror_clip_x, mirror_clip_y, mirror_clip_z, clip_dist, use_axis_x, use_axis_y, use_axis_z)¶
        
        #finds groups of vertices closer than dist and merges them together
        bmesh.ops.automerge(bm, verts=bm.verts, dist=1e-6)
        
        for f in bm.faces:
        f.smooth = True
        
        #here it applies all the changes to the mesh
        bm.to_mesh(mymesh)
        print("Done {}".format(len(bm.verts)))
        bm.free()
        """
    #nothing has changed for the vertices with the triangles
    #print(new_verts)
    #print(new_faces)
    
    #************with these array of tuples can't just import
    #it because will give you ther error:
    #The truth value of an array with more than one element
    #is ambiguous. Use a.any() or a.all()
    #*************#
    #calculating the edges and the normals
    mymesh.update(calc_edges=True)
    mymesh.calc_normals()
    
    
    #mymesh.validate()
    
    #for i in range(0,10):
    #    print(mymesh.vertices[i].co)
    
    
    
    #print("filename right before list = " + filename)
    #objects_Matching_filename = [x for x in object_List if "neuron_mesh_36706215" in x]
    
    #print(objects_Matching_filename)
    object = bpy.data.objects.new("neuron-"+ID, mymesh)
    #object.location = bpy.context.scene.cursor_location
    object.location = Vector((0,0,0))
    bpy.context.scene.objects.link(object)
    
    object.lock_location[0] = True
    object.lock_location[1] = True
    object.lock_location[2] = True
    object.lock_scale[0] = True
    object.lock_scale[1] = True
    object.lock_scale[2] = True
    
    #rotate the z direction by 90 degrees so point correct way
    
    #object.rotation_euler[2] = 1.5708
    
    object.rotation_euler[0] = 4.53786
    object.rotation_euler[1] = 0.698132
    object.rotation_euler[2] = 0
    
    
    
    
    object.lock_rotation[0] = True
    object.lock_rotation[1] = True
    object.lock_rotation[2] = True
    
    
    #set view back to normal:
    set_View()
    
    
    #run the setup color command
    #bpy.ops.object.select_all(action='TOGGLE')
    create_local_colors(object)
    
    
    
    
    ###**********WILL GO THROUGH AND PUSH UNLABELED DATA TO DATABASE
    ####SO NO ONE ELSE WILL BE ABLE TO PULL THE SAME THING
    
    if from_Mesh_Flag == 1:
        print("from Mesh Flag option")
        #create array for faces, verts and edges with values of 0 for all
        #and then push to the labels database
        
        ob = bpy.data.objects["neuron-"+ID]
        
        me = ob.data
        edges_raw = ob.data.edges
        
        n_edges = len(edges_raw)
        n_vertices = neuron_data['n_vertices']
        n_traingles = neuron_data['n_triangles']
        
        print("inside mesh")
        print('n_vert = ' + str(n_vertices))
        print('n_tri = ' + str(n_traingles))
        
        #create empty ______ for them
        edges_labels = np.zeros(n_edges,dtype=np.uint8)
        vertices_labels = np.zeros(n_vertices,dtype=np.uint8)
        triangles_labels = np.zeros(n_traingles,dtype=np.uint8)
        
        #push to the labels database
        
        timestamp = str(datetime.datetime.now())
        print(timestamp[0:19])
        
        username_stored = bpy.context.scene.username_Login
        dateTime_stored = str(datetime.datetime.now())[0:19]
        
        segmentation=1
        decimation_ratio=0.35
        
        #now try making write
        labels_Table.insert1((segmentation,int(ID),decimation_ratio,username_stored,dateTime_stored,
                              vertices_labels,triangles_labels,edges_labels,"partial"))
                              
                              
                              
        print("just stored pulled neuron in the labels table")
    
    elif from_Labels_Flag == 1:
        print("from Labels Flag option")
        #get the labels
        #labels_list
        
        #get neuron info from the mesh table
        neuron_labels = ((labels_Table & "segment_ID="+ID & "author='"+ username + "'").fetch(as_dict=True))[0]
        
        verts_labels = neuron_labels['vertices']
        triangles_labels = neuron_labels['triangles']
        edges_labels = neuron_labels['edges']
        
        print("inside mesh")
        print('verts_labels = ' + str(len(verts_labels)))
        print('triangles_labels = ' + str(len(triangles_labels)))
        
        
        #need to add the labels to the newly created object
        ob = bpy.data.objects["neuron-"+ID]
        
        
        me = ob.data
        me.use_customdata_edge_bevel = True
        me.use_customdata_vertex_bevel = True
        
        #print("starting to hide everything")
        #iterate through all of the vertices
        verts_raw = ob.data.vertices
        #print(len(active_verts_raw))
        
        edges_raw = ob.data.edges
        
        #print(len(active_edges_raw))
        
        faces_raw = ob.data.polygons
        
        
        if len(edges_raw) != len(edges_labels):
            edges_labels = edges_labels = np.zeros(len(edges_raw),dtype=np.uint8)
            print("edges imported don't match the edges in neuron")
    
    
        print("inside mesh")
        print('verts_raw = ' + str(len(verts_raw)))
        print('faces_raw = ' + str(len(faces_raw)))
        
        #verts_labels = neuron_labels['vertices']
        #triangles_labels = neuron_labels['traingles']
        #edges_labels = neuron_labels['edges']
        
        bevel_Weights = get_Bevel_Weights()
        
        #iterate through all of the
        for i,k in enumerate(verts_raw):
            #set the bevel weight
            k.bevel_weight = bevel_Weights[int(verts_labels[i])]

for i,k in enumerate(edges_raw):
    #set the bevel weight
    k.bevel_weight = bevel_Weights[int(edges_labels[i])]
        
        
        #iterate through all of the face
        
        for i,k in enumerate(faces_raw):
            k.material_index = int(triangles_labels[i])



else:
    print("ERROR: neither the labels flag or the mesh flag are active")
    return
    
    
    
    
    
    #reset the flags
    from_Mesh_Flag = 0
    from_Labels_Flag = 0
    
    #go into edit mode
    print("trying to select the neuron")
    
    bpy.context.scene.objects.active = bpy.context.scene.objects["neuron-"+ID]
    #bpy.ops.object.mode_set(mode='EDIT')
    #bpy.ops.mesh.select_all(action='TOGGLE')
    edit_active_neuron()
    
    #does the label setting
    last_edited, last_status, last_user= (labels_Table & "segment_id="+ID & "author='"+ username + "'").fetch("date_time", "status","author")
    bpy.context.scene.last_Edited = str(last_edited[0])
    last_status_value = last_status[0]
    
    #get the dictionary of the status key
    
    bpy.context.scene.last_Status = last_status_value
    
    #set the user who was last to edit it
    bpy.context.scene.last_Edited_User = last_user[0]
    
    is_label_hidden = get_Hide_Flag()
    
    #make sure the faces are hidden if they should be
    if (is_label_hidden == True):
        hide_Labeled(mode=0,waitTime=0)
    else:  #show all of the faces
        #print ("Property Disabled")
        hide_Labeled(mode=1,waitTime=0)
    
    
    
    #make sure in solid mode
    for area in bpy.context.screen.areas: # iterate through areas in current screen
        if area.type == 'VIEW_3D':
            for space in area.spaces: # iterate through spaces in current VIEW_3D area
                if space.type == 'VIEW_3D': # check if space is a 3D view
                    space.viewport_shade = 'SOLID' # set the viewport shading to rendered

    bpy.ops.object.mode_set(mode='OBJECT')

#were for debugging purposes where was checking if there were vertices/faces lost
"""ob = bpy.data.objects["neuron-"+ID]
    
    
    me = ob.data
    me.use_customdata_edge_bevel = True
    me.use_customdata_vertex_bevel = True
    
    #print("starting to hide everything")
    #iterate through all of the vertices
    verts_raw = ob.data.vertices
    #print(len(active_verts_raw))
    
    edges_raw = ob.data.edges
    
    #print(len(active_edges_raw))
    
    faces_raw = ob.data.polygons
    
    
    
    
    print("AT THE END OF THE IMPORT FUNCTION")
    print('verts_raw = ' + str(len(verts_raw)))
    print('faces_raw = ' + str(len(faces_raw)))"""
        
        
        
        return

#continue_editing
class continue_editing(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.continue_editing"
    bl_label = "continue_editing"
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def execute(self, context):
        edit_active_neuron()
        #if not(print_Message == ""):
        #self.report({'INFO'}, print_Message)
        return {'FINISHED'}

#the npz file will look like this
#[segment_ID,author,date_time,vertices,triangles,edges,status]

#-----------------------------------------------importing local saved off files------------------------------------------------------------------------
def import_local_Neuron(filepath):
    
    try:
        neuron_labels = np.load(filepath)
    except:
        print("there is no file with that name in the same directory as the Blender project!")
        return

    #just need to unpack the label variables and then pull the neuron from the database and label it
    ID = str(neuron_labels["segment_ID"])
    bpy.context.scene.picked_Neuron_ID = ID
    #set the username for the last status
    bpy.context.scene.last_Edited_User = str(neuron_labels["author"])
    #set the time for the last status
    bpy.context.scene.last_Edited = str(neuron_labels["date_time"])
    bpy.context.scene.last_Status = str(neuron_labels["status"])

verts_labels = neuron_labels['vertices'].astype(dtype=np.int32)
triangles_labels = neuron_labels['triangles'].astype(dtype=np.int32)
edges_labels = neuron_labels['edges'].astype(dtype=np.int32)


#GOES THROUGH THE WHOLE PROCESS OF CREATING THE OBJECT AND IMPORTING IT
primary_key = dict(segmentation=1,decimation_ratio=0.35)
    neuron_data = ((ta3.Decimation & primary_key & "segment_ID="+ID).fetch(as_dict=True))[0]
    
    verts = neuron_data['vertices'].astype(dtype=np.int32)
    faces = neuron_data['triangles'].astype(dtype=np.uint32)
    
    #*********Need to add in my own scale*****************#
    scale = 0.001
    
    #Makes the vertices as voxels and applies a scale to them
    not_centered_verts = [(x[0], x[2], x[1]) for x in (verts * scale).tolist()]
    #don't need the vertical count being added to the faces like in his because because
    new_faces = [(x[0], x[1], x[2]) for x in (faces).tolist()]
    
    offset = np.median(np.array(not_centered_verts), axis=0)
    print("offset = " + str(offset))
    new_verts = [(x[0] - offset[0], x[1] - offset[1], x[2] - offset[2]) for x in not_centered_verts]
    
    
    print("Length of vertices = " + str(len(new_verts)))
    print("Length of vertices = " + str(len(new_faces)))
    #-----------------END OF new way of importing using james cotton way------------------#
    mymesh = bpy.data.meshes.new("neuron-"+ID)
    mymesh.from_pydata(new_verts, [], new_faces)
    #object = bpy.data.objects.new(optional_Name, mesh)
    
    #uses the bmesh library to import:
    
    
    mymesh.update(calc_edges=True)
    mymesh.calc_normals()
    
    
    #mymesh.validate()
    
    #for i in range(0,10):
    #    print(mymesh.vertices[i].co)
    
    
    
    #print("filename right before list = " + filename)
    #objects_Matching_filename = [x for x in object_List if "neuron_mesh_36706215" in x]
    
    #print(objects_Matching_filename)
    object = bpy.data.objects.new("neuron-"+ID, mymesh)
    #object.location = bpy.context.scene.cursor_location
    object.location = Vector((0,0,0))
    bpy.context.scene.objects.link(object)
    
    object.lock_location[0] = True
    object.lock_location[1] = True
    object.lock_location[2] = True
    object.lock_scale[0] = True
    object.lock_scale[1] = True
    object.lock_scale[2] = True
    
    #rotate the z direction by 90 degrees so point correct way
    
    #object.rotation_euler[2] = 1.5708
    object.rotation_euler[0] = 4.53786
    object.rotation_euler[1] = 0.698132
    object.rotation_euler[2] = 0
    
    
    
    object.lock_rotation[0] = True
    object.lock_rotation[1] = True
    object.lock_rotation[2] = True
    
    
    #set view back to normal:
    set_View()
    
    
    #run the setup color command
    #bpy.ops.object.select_all(action='TOGGLE')
    create_local_colors(object)
    
    
    #need to add the labels to the newly created object
    ob = bpy.data.objects["neuron-"+ID]
    
    
    me = ob.data
    me.use_customdata_edge_bevel = True
    me.use_customdata_vertex_bevel = True
    
    #print("starting to hide everything")
    #iterate through all of the vertices
    verts_raw = ob.data.vertices
    #print(len(active_verts_raw))
    
    edges_raw = ob.data.edges
    
    #print(len(active_edges_raw))
    
    faces_raw = ob.data.polygons
    
    #verts_labels = neuron_labels['vertices']
    #triangles_labels = neuron_labels['traingles']
    #edges_labels = neuron_labels['edges']
    
    bevel_Weights = get_Bevel_Weights()
    
    #iterate through all of the
    for i,k in enumerate(verts_raw):
        #set the bevel weight
        k.bevel_weight = bevel_Weights[int(verts_labels[i])]
    
    for i,k in enumerate(edges_raw):
        #set the bevel weight
        k.bevel_weight = bevel_Weights[int(edges_labels[i])]
    
    
    #iterate through all of the face
    
    for i,k in enumerate(faces_raw):
        k.material_index = int(triangles_labels[i])
    
    
    #go into edit mode
    print("trying to select the neuron")

bpy.context.scene.objects.active = bpy.context.scene.objects["neuron-"+ID]
#bpy.ops.object.mode_set(mode='EDIT')
#bpy.ops.mesh.select_all(action='TOGGLE')
edit_active_neuron()
    
    
    is_label_hidden = get_Hide_Flag()
    
    #make sure the faces are hidden if they should be
    if (is_label_hidden == True):
        hide_Labeled(mode=0,waitTime=0)
    else:  #show all of the faces
        #print ("Property Disabled")
        hide_Labeled(mode=1,waitTime=0)
    
    #setup the colors for the neuron
    
    #make sure in solidDID NOT Find ID in labeles table mode
    for area in bpy.context.screen.areas: # iterate through areas in current screen
        if area.type == 'VIEW_3D':
            for space in area.spaces: # iterate through spaces in current VIEW_3D area
                if space.type == 'VIEW_3D': # check if space is a 3D view
                    space.viewport_shade = 'SOLID' # set the viewport shading to rendered

    bpy.ops.object.mode_set(mode='OBJECT')


return






#-----------------------------------------------importing local saved off files------------------------------------------------------------------------









def importMesh(filepath, filename = "neuron"):
    #'C:/Users/svc_atlab/Documents/Celii/Blender_Plugin/neuron_mesh_36706215_with_edges.npz'
    #script that will add the neuron as mesh
    try:
        mesh_data = np.load(filepath)
    except:
        print("there is no file with that name in the same directory as the Blender project!")
        return
    """
        #####My way of importing that worked for the simpler meshes###########
        #print("inside loop")
        verts_old = mesh_data['vertices'].tolist()
        faces = mesh_data['triangles'].tolist()
        
        verts = [Vector(l) for l in verts_old]
        
        """
    """for i in range(0,10):
        print(verts_old[i])
        print(verts[i])"""
    
    
    
    #-----------------new way of importing using james cotton way------------------#
    verts = mesh_data['vertices'].astype(dtype=np.int32)
    faces = mesh_data['triangles'].astype(dtype=np.uint32)
    
    #*********Need to add in my own scale*****************#
    scale = 0.001
    
    #Makes the vertices as voxels and applies a scale to them
    not_centered_verts = [(x[0], x[2], x[1]) for x in (verts * scale).tolist()]
    #don't need the vertical count being added to the faces like in his because because
    new_faces = [(x[0], x[1], x[2]) for x in (faces).tolist()]
    
    offset = np.median(np.array(not_centered_verts), axis=0)
    print("offset = " + str(offset))
    new_verts = [(x[0] - offset[0], x[1] - offset[1], x[2] - offset[2]) for x in not_centered_verts]
    
    
    #print(new_verts)
    #print(new_faces)
    #-----------------END OF new way of importing using james cotton way------------------#
    mymesh = bpy.data.meshes.new(filename)
    mymesh.from_pydata(new_verts, [], new_faces)
    #object = bpy.data.objects.new(optional_Name, mesh)
    
    #uses the bmesh library to import:
    bm = bmesh.new()
    bm.from_mesh(mymesh)
    print("Simplifying {}".format(len(bm.verts)))
    # bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0)
    #for i in range(5):
    #    bmesh.ops.smooth_vert(bm, verts=bm.verts, factor=0.5, use_axis_x=True, use_axis_y=True,
    #                          use_axis_z=True)  # , mirror_clip_x, mirror_clip_y, mirror_clip_z, clip_dist, use_axis_x, use_axis_y, use_axis_z)¶
    
    #finds groups of vertices closer than dist and merges them together
    #bmesh.ops.automerge(bm, verts=bm.verts, dist=1e-6)
    
    for f in bm.faces:
        f.smooth = True
    
    #here it applies all the changes to the mesh
    bm.to_mesh(mymesh)
    print("Done {}".format(len(bm.verts)))
    bm.free()

    #nothing has changed for the vertices with the triangles
    #print(new_verts)
    #print(new_faces)

    #************with these array of tuples can't just import
#it because will give you ther error:
#The truth value of an array with more than one element
#is ambiguous. Use a.any() or a.all()
#*************#
#calculating the edges and the normals
mymesh.update(calc_edges=True)
    mymesh.calc_normals()
    
    
    #mymesh.validate()
    
    #for i in range(0,10):
    #    print(mymesh.vertices[i].co)
    
    
    
    #print("filename right before list = " + filename)
    #objects_Matching_filename = [x for x in object_List if "neuron_mesh_36706215" in x]
    
    #print(objects_Matching_filename)
    object = bpy.data.objects.new(filename, mymesh)
    #object.location = bpy.context.scene.cursor_location
    object.location = Vector((0,0,0))
    bpy.context.scene.objects.link(object)
    
    object.lock_location[0] = True
    object.lock_location[1] = True
    object.lock_location[2] = True
    object.lock_scale[0] = True
    object.lock_scale[1] = True
    object.lock_scale[2] = True
    
    #rotate the z direction by 90 degrees so point correct way
    
    #object.rotation_euler[2] = 1.5708
    object.rotation_euler[0] = 4.53786
    object.rotation_euler[1] = 0.698132
    object.rotation_euler[2] = 0
    
    
    
    object.lock_rotation[0] = True
    object.lock_rotation[1] = True
    object.lock_rotation[2] = True
    
    
    #set view back to normal:
    set_View()
    
    
    #run the setup color command
    #bpy.ops.object.select_all(action='TOGGLE')
    create_local_colors(object)
    
    
    """bpy.context.space_data.cursor_location[0] = 0
        bpy.context.space_data.cursor_location[1] = 0
        bpy.context.space_data.cursor_location[2] = 0
        
        
        for i in objects_Matching_filename:
        bbpy.data.objects[i].select = True
        
        bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)"""

#now deselect them if want
#will go through ever vertex and face and either hide or show it if it is labeled (based on what mode it is in)
#mode 0 = HIDE EVERY VERTEX/POLYGON THAT IS LABELED
#mode 1 = SHOW EVERY VERTEX/POLYGON THAT IS LABELED
def hide_Labeled(mode=0,waitTime=0):
    #if going to hide everything, can optionally make it weight 2 seconds before doing it:
    
    """ THIS IS JUST EXECUTING SCRIPT AND THEN WAITING 2 SECONDS,
        CANT GET BLENDER TO WAIT WITHOUT USING A MODULE, NOT WORTH IT....`
        if(mode == 0 and waitTime > 0):
        time.sleep(2)
        """
    
    #put into object mode so that the changes will be persisted
    currentMode = bpy.context.object.mode
    
    
    
    if(mode ==0): #then we will hide everything
        bpy.ops.object.mode_set(mode='OBJECT')
        ob = bpy.context.object
        ob.update_from_editmode()
        
        me = ob.data
        me.use_customdata_edge_bevel = True
        me.use_customdata_vertex_bevel = True
        
        #print("starting to hide everything")
        #iterate through all of the vertices
        verts_raw = ob.data.vertices
        active_verts_raw = [k for k in verts_raw if k.bevel_weight > 0.0]
        #print(len(active_verts_raw))
        
        edges_raw = ob.data.edges
        
        active_edges_raw = [k for k in edges_raw if k.bevel_weight > 0.0]
        #print(len(active_edges_raw))
        
        faces_raw = ob.data.polygons
        active_faces_raw = [k for k in faces_raw if k.material_index > 1]
        
        
        for k in active_verts_raw:
            k.select = False
            k.hide = True
        
        for k in active_edges_raw:
            k.select = False
            k.hide = True
        
        
        
        #iterate through all of the face
        
        #print(active_faces_raw)
        for k in active_faces_raw:
            k.select = False
            k.hide = True
        
        
        
        
        """
            #go through all of the edges and hide them as well
            edges = ob.data.edges
            face_edge_map = {ek: edges[i] for i, ek in enumerate(ob.data.edge_keys)}
            
            
            #might be making a list
            e = []
            for i in active_faces_raw:
            for ed in i.edge_keys:
            if not(face_edge_map[ed] in e):
            e.append(face_edge_map[ed])
            
            indexes = [jk.index for jk in e]
            
            for k in edges:
            if k.index in indexes:
            k.select = False
            k.hide = True
            
            """
        
        
        
        """
            print(e)
            for kk in e:
            print(kk.index)
            k.select = False
            k.hide = True
            print(k.hide)
            
            for yy in e:
            print(yy.hide)
            """
        
        
        
        """
            #go through using bmesh to make sure they are actually hidden
            mesh = bmesh.from_edit_mesh(ob.data)
            
            
            active_verts = [k for k in mesh.verts if k.hide == True]
            #print(active_verts)
            
            #go through and unhighlight the verts
            for k in active_verts:
            k.hide_set(True)
            
            
            #get the list of active faces
            active_faces = [k for k in mesh.faces if k.hide == True]
            #print(active_faces)
            print(active_faces_raw)
            #go through and unhighlight the verts
            for k in active_faces:
            k.hide_set(True)
            
            """
        if(currentMode == 'EDIT'):
            bpy.ops.object.mode_set(mode='EDIT')
        else:
            bpy.ops.object.mode_set(mode='OBJECT')
    
        print("done hiding")
        ob.data.update()
elif(mode ==1): #then we will show everything, so just show  every face and vertex
    print("starting to UN-hide everything")
    
    bpy.ops.object.mode_set(mode='OBJECT')
        ob = bpy.context.object
        ob.update_from_editmode()
        
        verts_raw = ob.data.vertices
        faces_raw = ob.data.polygons
        edges_raw = ob.data.edges
        
        for k in verts_raw:
            k.hide = False

    #iterate through all of the face

    for k in faces_raw:
        k.hide = False
        
        for k in edges_raw:
            k.hide = False


#GO BACK INTO whatever mode you were on
if(currentMode == 'EDIT'):
    bpy.ops.object.mode_set(mode='EDIT')
        else:
            bpy.ops.object.mode_set(mode='OBJECT')

    #OLD WAY OF GOING IT WITH BMESH
    """mesh = bmesh.from_edit_mesh(ob.data)
        
        for k in mesh.verts :
        k.hide_set(False)
        
        
        #get the list of active faces
        for k in mesh.faces:
        k.hide_set(False)
        
        print("done UN-hiding")
        ob.data.update()"""


else:
    print("incorrect mode entered")
    return
    ob.data.update()

def get_Hide_Flag():
    #insert code here
    return bpy.context.scene.my_tool.hide_Labels

def getColors():
    return ["no_color","no_color","Apical (blue)","Basal (yellow)","Oblique (green)"
            ,"Soma (red)","Axon (orange)","Dendrite (purple)","Distal (pink)",
            "Error (brown)","Unlabelable (tan)","Spine Head (rose)",
            "Spine (light pink)","Bouton (aqua)"]
def getLabels():
    return ["None","None","Apical","Basal","Oblique","Soma","Axon","Dendrite","Distal","Error","Unlabelable","Spine Head","Spine","Bouton"]

def get_Bevel_Weights():
    return [0.00,0.00,0.02,0.03,0.04,0.05,0.06,0.07,0.08,0.09,0.10,0.11,0.12,0.13]



#function that does the labeling:
def main(context, var):
    print("labeling neuron")
    print("button pressed was " + var)
    #bpy.context.object.active_material=bpy.data.materials["blue"]
    
    colors = getColors()
    
    #get the index and set the color equal to that
    
    #might need to update who is getting selected so use this
    
    
    if(var in colors):
        print("var in colors")
        index_number = colors.index(var)
        if(var == 'no_color'):
            index_number = 1
        #get all of the vertices and set bevel_weight and select = False
        bpy.ops.object.mode_set(mode='OBJECT')
        ob = bpy.context.object
        me = ob.data
        ob.update_from_editmode()
        #ob.data.update()
        #bpy.context.scene.update()
        
        bevel_Weights = get_Bevel_Weights()
        
        verts_raw = ob.data.vertices
        active_verts_raw = [k for k in verts_raw if k.select > 0]
        
        edges_raw = ob.data.edges
        active_edges_raw = [k for k in edges_raw if k.select > 0]
        
        #print("inside labeling edges raw length = " + str(len(active_edges_raw)))
        
        faces_raw = ob.data.polygons
        active_faces_raw = [k for k in faces_raw if k.select > 0]
        #print("active_faces_raw =" + str(active_faces_raw))
        
        
        me.use_customdata_edge_bevel = True
        me.use_customdata_vertex_bevel = True
        
        #iterate through all of the vertices
        #print(active_verts_raw)
        for k in active_verts_raw:
            k.bevel_weight = bevel_Weights[index_number]
            #print(k.bevel_weight)
            if(index_number == 1 or index_number == 0):
                #print("setting hide to 0 in vertices")
                k.hide = False
    
        active_verts_raw = [k for k in verts_raw if k.bevel_weight > 0.0]
        #print("active_verts_raw in labeling length = " + str(len(active_verts_raw)))
        
        
        
        #print(active_verts_raw)
        for k in active_edges_raw:
            k.bevel_weight = bevel_Weights[index_number]
            #print(k.bevel_weight)
            if(index_number == 1 or index_number == 0):
                #print("setting hide to 0 in vertices")
                k.hide = False

"""print("about to do all the vertices and edges")
    for v in verts_raw:
    print(v.bevel_weight)
    print("about to do all the vertices and edges")
    for e in edges_raw:
    print(e.bevel_weight)"""
        
        
        
        
        #iterate through all of the faces and set the color and selection = false
        for k in active_faces_raw:
            k.material_index = index_number
            if(index_number == 1 or index_number == 0):
                #print("setting hide to 0")
                #print("setting hide to 0 in vertices")
                k.hide = False
ob.data.update()
bpy.ops.object.mode_set(mode='EDIT')
######-----old way of setting the color---------######  may need to do this if setting index doesn't work
######color wasn't being set so had to use this way
#bpy.context.object.active_material_index = index_number
#bpy.ops.object.material_slot_assign()


#now need to hide all of the faces if the toggle switch is set to that
hideFlag = get_Hide_Flag()  #Hasn't been implemented yet
    
    if hideFlag > 0:
        hide_Labeled(mode=0,waitTime=3)
        
        #reset the percent_labeled because there was an adjustment
        bpy.context.scene.percent_labeled = ""
        bpy.context.scene.complete_100_check = ""
        bpy.context.scene.complete_100_check_2 = ""
        bpy.context.scene.complete_100_check_save_flag = False
        return ""

    if(var == "print"):
        ob = bpy.context.object
        if ob.type != 'MESH':
            print("Active object is not a Mesh")
            return None
        ob.update_from_editmode()
        me = ob.data

labels_List = getLabels()
return ("face index = " + str(me.polygons.active) + ": material = " + labels_List[me.polygons[me.polygons.active].material_index])

if(var == "reset view"):
    set_View()
    return ""
    if(var == "exit_edit_mode"):
        bpy.ops.object.mode_set(mode='OBJECT')
        return ""
    if(var == "delete_Neuron"):
        #check that
        
        if bpy.data.objects.get("neuron-"+bpy.context.scene.delete_ID) is not None:
            bpy.context.scene.delete_Flag = True
            bpy.context.scene.delete_status = "Delete neuron-" + bpy.context.scene.delete_ID + "?"
        else:
            bpy.context.scene.delete_Flag = False
            bpy.context.scene.delete_status = "neuron-" + bpy.context.scene.delete_ID + " does not exist"

if(var == "delete_No"):
    bpy.context.scene.delete_Flag = False
        bpy.context.scene.delete_status = ""
        bpy.context.scene.delete_ID = ""
        return ""
    if(var == "delete_Yes"):
        # deselect all
        bpy.ops.object.select_all(action='DESELECT')
        
        ID = bpy.context.scene.delete_ID
        
        if( ID != ""):
            bpy.data.objects['neuron-'+ID].select = True
            
            #delete the object from the scene
            bpy.ops.object.delete()
            
            #now need to set all of the settings
            if(bpy.context.scene.delete_ID == bpy.context.scene.picked_Neuron_ID):
                reset_Scene_Variables(login_Flag=True)
            
            bpy.context.scene.delete_Flag = False
            bpy.context.scene.delete_status = ""
            bpy.context.scene.delete_ID = ""
        
        return ""
return ""

#else:
#print out the labels of all of the active faces -- To be implemented




class Neuron_Label_Operator_a(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.neuron_label_operator_a"
    bl_label = "Neuron Label Operator_a"
    
    myVar = bpy.props.StringProperty(name="myVar")
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def execute(self, context):
        print_Message = main(context,self.myVar)
        if not(print_Message == ""):
            self.report({'INFO'}, print_Message)
        return {'FINISHED'}


class setup_colors(bpy.types.Operator):
    bl_idname = "object.setup_colors"
    bl_label = "setup colors"
    
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def execute(self, context):
        create_local_colors()
        return {'FINISHED'}

class load_file_operator(bpy.types.Operator):
    bl_idname = "object.load_file_operator"
    bl_label = "load_file_operator"
    
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    
    
    def execute(self, context):
        ##need to access component of panel and set it
        """print("File path = " + self.filepath)
            path, filename = os.path.split(self.filepath)
            print("filename = "+ filename)
            finalName, ext = os.path.splitext(filename)
            print("finalName = "+ finalName)
            
            print("ext = "+ ext)"""
        ##need to access component of panel and set it
        import_local_Neuron(self.filepath)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class submit_registration_login(bpy.types.Operator):
    bl_idname = "object.submit_registration_login"
    bl_label = "submit_registration_login"
    
    myRegVar = bpy.props.StringProperty(name="myRegVar")
    
    
    def execute(self, context):
        print("inside execute submit registration")
        return {'FINISHED'}
    
    def invoke(self, context, event):
        #where you want to put your code
        print("inside invoke submit registration login")
        
        #create an Authors object and pull all the usernames
        authors = Authors()
        current_User_Names = authors.fetch('username')
        
        if self.myRegVar == "logout":
            #need to reset all of the flags:
            reset_Scene_Variables()
            return {'RUNNING_MODAL'}
        
        
        
        if self.myRegVar == "register":
            username = context.scene.username
            
            firstname = context.scene.firstname
            lastname = context.scene.lastname
            name = firstname + " " + lastname
            
            
            print(username)
            print(name)
            if username in current_User_Names:
                print("inside register username matched")
                #set the text filed to say that username already exists and to pick new username
                context.scene.register_Status = "Username already exists, pick another"
            else:
                print("inside register username NOT!!! matched")
                authors.insert1((username,name),skip_duplicates=True)
                context.scene.register_Status = "Succss! Please login with username"
                
                #clear out the register button
                context.scene.firstname = ""
                context.scene.lastname = ""
                context.scene.username = ""
        
        
        else:
            username = context.scene.username_Login
            if username in current_User_Names:
                
                print("inside login user name matched")
                bpy.context.scene.login_Status = "Welcome " + username +": Now Pick Neuron"
                
                
                #should enable all of the other things
                #context.scene.firstname = "hellow"
                context.scene.login_Flag = True
            #bpy.context.screen.areas["VIEW_3D"].region["TOOLS"].tag_redraw()
            else:
                print("inside login user name NOT!!! matched")
                bpy.context.scene.login_Status = "Failure! username not registered"
                context.scene.login_Flag = False
#make sure the login panel is visible




                    return {'RUNNING_MODAL'}

def hide_Labels_Func(self, context):  #the call if you do something with button 1
    #if checked then hide all the labeled faceds
    if (self.hide_Labels == True):
        hide_Labeled(mode=0,waitTime=0)
    else:  #show all of the faces
        #print ("Property Disabled")
        hide_Labeled(mode=1,waitTime=0)

def visible_only_selection_func(self, context):  #the call if you do something with button 2
    #print("hello from button 2")
    if (self.visible_only_selection == True):
        bpy.context.space_data.use_occlude_geometry = True
    else:
        bpy.context.space_data.use_occlude_geometry = False

class MySettings(PropertyGroup):
    
    hide_Labels = BoolProperty(
                               name="Enable or Disable",
                               description="A bool property",
                               default = False,
                               update = hide_Labels_Func
                               )
                               visible_only_selection = BoolProperty(
                                                                     name="Enable or Disable",
                                                                     description="A bool property",
                                                                     default = False,
                                                                     update = visible_only_selection_func
                                                                     )


class RegisterPanel(bpy.types.Panel):
    """Creates a Panel that you can open in order to get the register fields"""
    bl_idname = "Register Layout"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Label Neurons"
    bl_label = "Register"
    bl_context = "objectmode"
    
    #register_Status = bpy.props.StringProperty(name="Register Statuts")
    #where to put the file name****************Not implemented yet
    register_Status = "regis. status";
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool
        
        #only want this drawn if in object mode
        if bpy.context.mode == "OBJECT":
            
            layout.row().prop(context.scene, "username")
            layout.row().prop(context.scene, "firstname")
            layout.row().prop(context.scene, "lastname")
            
            row = layout.row()
            #row.scale_y = 3.0
            row.label(text = "")
            row.operator("object.submit_registration_login", text="submit").myRegVar = "register"
            row = layout.row()
            #to be edited based on the registration status
            row.label(text = scene.register_Status)
            
            
            """
                # find the next text
                col = layout.column(align=True)
                row = col.row(align=True)
                row.prop(st, "find_text", text="")
                row.operator("text.find_set_selected", text="", icon='TEXT')
                col.operator("text.find")"""


class LoginPanel(bpy.types.Panel):
    """Creates a Panel that you can open in order to get the register fields"""
    bl_idname = "Login Layout"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Label Neurons"
    bl_label = "Login"
    bl_context = "objectmode"
    
    
    #where to put the file name****************Not implemented yet
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool
        
        #only want this drawn if in object mode
        if bpy.context.mode == "OBJECT":
            
            layout.row().prop(context.scene, "username_Login")
            
            row = layout.row()
            #row.scale_y = 3.0
            row.label(text = "")
            row.operator("object.submit_registration_login", text="login").myRegVar = "login"
            row = layout.row()
            #to be edited based on the registration status
            row.label(text = bpy.context.scene.login_Status)





################  Main function for picking the neuron you want to load  ##################
def main_Neuron_Picker(context, var):
    print("inside main_Neuron_Picker")
    print("var = "+var)
    
    if var == "ID":
        #retrieve the neuron ID
        ID = bpy.context.scene.neuron_ID
        print("ID = " + ID)
        ID = int(ID)
        
        
        #check edited database first for the neuron looking for
        currentLabels = Annotation()
        
        labeled_IDs = currentLabels.fetch("segment_id").tolist()
        
        if ID in labeled_IDs:
            print("Found ID in labeles table")
            #print success and the name of the neuron: Click Edit to start Labeling
            bpy.context.scene.neuron_ID_Status = "Found " + str(ID) + ": Click Import"
            bpy.context.scene.labeled_Flag_ID = True
        else:
            print("DID NOT Find ID in labeles table")
            bpy.context.scene.labeled_Flag_ID = False
    
        #check edited database first for the neuron looking for
        #mesh_Table = ta3.Mesh()
        
        
        #mesh_Dict = (ta3.Decimation & primary_key & "segment_id="+ID).fetch(as_dict=True)[0]
        
        #all_IDs = mesh_Table.fetch("segment_id").tolist()
        primary_key = dict(segmentation=1,decimation_ratio=0.35)
        all_IDs = (ta3.Decimation & primary_key).fetch("segment_id").tolist()
        
        if ID in all_IDs:
            print("Found ID in Mesh table")
            bpy.context.scene.labeled_Flag_ID = False
            #print success and the name of the neuron: Click Edit to start Labeling
            bpy.context.scene.neuron_ID_Status = "Found " + str(ID) + ": Click Import"
            bpy.context.scene.import_Neuron_Flag = True
else:
    print("DID NOT Find ID in the mesh table")
    if bpy.context.scene.labeled_Flag_ID == True:
        print("ERROR: FOUND NEURON IN LABELS BUT NOT MESH TABLE")
            bpy.context.scene.neuron_ID_Status = "Can't Find " + str(ID) + ": Try Another ID"
            
            bpy.context.scene.labeled_Flag_ID = False
            bpy.context.scene.import_Neuron_Flag = False
            return ""

elif var == "next_unlabeled":
    #get all of the list of neurons that have never been pulled
    #use the difference operator in datajoint
    #mesh_Table = ta3.Mesh()
    labels = Annotation()
    primary_key = dict(segmentation=1,decimation_ratio=0.35)
    mesh_list = (ta3.Decimation & primary_key).fetch("segment_id").tolist()
    #mesh_list = mesh_Table.fetch("segment_id").tolist() #old way of doing it without decimated list
    labels_list = labels.fetch("segment_id").tolist()
        
        difference = [x for x in mesh_list if x not in labels_list]
        print(difference)
        
        #make the 1st neuron in the list the one you get and then go
        #straight into editing it so there are no pull issues
        
        if len(difference) > 0:
            bpy.context.scene.next_available_neuron_ID = str(difference[0])
            bpy.context.scene.next_available_status = "Found neuron:" + str(difference[0])
            #call function that will automatically load neuron
            load_Neuron(str(difference[0]))
        else:
            bpy.context.scene.next_available_status = "NO MORE NEURONS LEFT"
            bpy.context.scene.next_available_neuron_ID = -1


elif var == "username_edit":
    #means want to send the neuron picked by the username to be edite
    if bpy.context.scene.status_picked !="":
        print("Want to edit neuron picked by username")
        bpy.context.scene.neuron_username_Status = "LOADING NEURON FOR EDIT..."
            load_Neuron(bpy.context.scene.username_neuron_ID)
        
        else:
            print("ERROR: ALLOWED TO CLICK EDIT WHEN NO NEURON STORED FOR USERNAME!")
elif var == "ID_edit":
    #means want to send the neuron picked by the username to be edite
    if bpy.context.scene.neuron_ID !="":
        print("Want to edit neuron picked by ID")
        bpy.context.scene.neuron_ID_Status = "LOADING NEURON FOR EDIT..."
            load_Neuron(bpy.context.scene.neuron_ID)
        
        else:
            print("ERROR: ALLOWED TO CLICK EDIT WHEN NO NEURON STORED FOR USERNAME!")
elif var == "exit_edit":
    bpy.ops.object.mode_set(mode='OBJECT')
    
    
    else:
        return ""
return ""

class picking_neuron(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.picking_neuron"
    bl_label = "picking_neuron"
    
    myPickVar = bpy.props.StringProperty(name="myPickVar")
    
    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        print_Message = main_Neuron_Picker(context,self.myPickVar)
        if not(print_Message == ""):
            self.report({'INFO'}, print_Message)
        return {'FINISHED'}


class ID_neuron_picker(bpy.types.Panel):
    """Creates a Panel that you can open in order to get the register fields"""
    bl_idname = "ID_neuron_picker"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Label Neurons"
    bl_label = "Add Neuron by ID"
    bl_context = "objectmode"
    
    
    #where to put the file name****************Not implemented yet
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool
        
        #only want this drawn if in object mode
        if bpy.context.mode == "OBJECT":
            row = layout.row()
            row.prop(context.scene, "neuron_ID")
            if context.scene.login_Flag != True:
                row.enabled = False
            else:
                row.enabled = True
        
            row = layout.row()
            #row.scale_y = 3.0
            row.label(text = "")
            row.operator("object.picking_neuron", text="Get Neuron").myPickVar = "ID"
            if context.scene.login_Flag == False or bpy.context.scene.neuron_ID == "":
                row.enabled = False
    else:
        row.enabled = True
            
            row = layout.row()
            #to be edited based on the registration status
            row.label(text = scene.neuron_ID_Status)
            
            
            row = layout.row()
            #row.scale_y = 3.0
            row.operator("object.picking_neuron", text="Import Neuron").myPickVar = "ID_edit"
            if context.scene.login_Flag == False or bpy.context.scene.neuron_ID == "" or bpy.context.scene.import_Neuron_Flag == False:
                row.enabled = False
            else:
                row.enabled = True


def execute_operator_neuron_picker(self, context):
    print(self.primitive)
    bpy.context.scene.status_picked = self.primitive

class statusProperties(bpy.types.PropertyGroup):
    mode_options = [
                    ("partial","partial",""),
                    ("complete","complete",""),
                    
                    ]
        
                    primitive = bpy.props.EnumProperty(
                                                       items=mode_options,
                                                       description="offers....",
                                                       default="partial",
                                                       update=execute_operator_neuron_picker
                                                       )

#will get the names of the neurons that belong to that user
def get_username_neurons(self, context):
    
    empty = [("None yet","None yet","")]
    if bpy.context.scene.username_Login != "" and bpy.context.scene.status_picked != "":
        #go get the names of the neurons from the database
        labels = Annotation()
        username = "'" + bpy.context.scene.username_Login + "'"
        filtered_labels = (labels & "author="+username
                           &"status='"+bpy.context.scene.status_picked+"'")
                           neurons_for_user = filtered_labels.fetch("segment_id").tolist()
                           
                           
                           #based on the length of the number of neurons that fit that description
                           if len(neurons_for_user) <= 0:
                               #return an empty tuple and print out to the user that no neurons fit that
                               context.scene.neuron_username_Status = "None of your neurons fit group"
                                   empty = [("None yet","None yet","")]
                                   return mode_options
                               else:
                                   #put the list into an enum
                                   items = []
                                   for i in neurons_for_user:
                                       items.append((str(i),str(i),""))
                                           
                                           print("items = ")
                                           print(items)
                                           return items
                                       else:
                                           return empty


#will execute when item is picked
def execute_operator_username_neuron_picked(self, context):
    print("inside function called after picked neuron in username tab")
    bpy.context.scene.username_neuron_ID = self.primitive
    ID = bpy.context.scene.username_neuron_ID
    bpy.context.scene.neuron_username_Status = "Found " + str(ID) + ": Click Import to start labeling"



class myNeuronsProperties(bpy.types.PropertyGroup):
    primitive = bpy.props.EnumProperty(
                                       items=get_username_neurons,
                                       description="offers....",
                                       update=execute_operator_username_neuron_picked
                                       )




####to be used for saving the neurons


class username_neuron_picker(bpy.types.Panel):
    """Creates a Panel that you can open in order to get the register fields"""
    bl_idname = "username_neuron_picker"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Label Neurons"
    bl_label = "Add Personal Neurons"
    bl_context = "objectmode"
    
    
    #where to put the file name****************Not implemented yet
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool
        
        #only want this drawn if in object mode
        if bpy.context.mode == "OBJECT":
            col = layout.column()
            col.label(text="Pick Status:")
            col.prop(context.scene.my_status_properties, "primitive")
            if context.scene.login_Flag != True:
                col.enabled = False
            else:
                col.enabled = True
    
            col = layout.column()
            col.label(text="Pick Neuron:")
            col.prop(context.scene.my_neurons_properties, "primitive")
            if context.scene.login_Flag != True or bpy.context.scene.status_picked == '':
                col.enabled = False
            else:
                col.enabled = True
            """
                row = layout.row()
                #row.scale_y = 3.0
                row.label(text = "")
                row.operator("object.picking_neuron", text="Get Neuron").myPickVar = "username"
                if context.scene.login_Flag != True or bpy.context.scene.status_picked == '' or bpy.context.scene.username_neuron_ID:
                col.enabled = False
                else:
                col.enabled = True"""


            row = layout.row()
            #to be edited based on the registration status
            row.label(text = scene.neuron_username_Status)

            row = layout.row()
            #row.scale_y = 3.0
            row.operator("object.picking_neuron", text="Import Neuron").myPickVar = "username_edit"
            if context.scene.login_Flag != True or bpy.context.scene.status_picked == '' or bpy.context.scene.username_neuron_ID =="":
                row.enabled = False
            else:
                row.enabled = True





class next_unlabeled_neuron_picker(bpy.types.Panel):
    """Creates a Panel that you can open in order to get the register fields"""
    bl_idname = "next_unlabeled_neuron_picker"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Label Neurons"
    bl_label = "Next Unlabeled Neuron"
    bl_context = "objectmode"
    
    neuron_Status = bpy.props.StringProperty(name="next_unlabeled_neuron_picker_Status")
    #where to put the file name****************Not implemented yet
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool
        
        #only want this drawn if in object mode
        if bpy.context.mode == "OBJECT":
            row = layout.row()
            row.operator("object.picking_neuron", text="Import Neuron").myPickVar = "next_unlabeled"
            if context.scene.login_Flag != True:
                row.enabled = False
            else:
                row.enabled = True
        
            row = layout.row()
            #to be edited based on the registration status
            row.label(text = bpy.context.scene.next_available_status)

class load_local_neuron(bpy.types.Panel):
    """Creates a Panel that you can open in order to get the register fields"""
    bl_idname = "load_local_neuron"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Label Neurons"
    bl_label = "Load Local Neuron"
    bl_context = "objectmode"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool
        
        #only want this drawn if in object mode
        if bpy.context.mode == "OBJECT":
            row = layout.row()
            row.operator("object.load_file_operator", text="Load File")
            if context.scene.login_Flag != True:
                row.enabled = False
            else:
                row.enabled = True
        
            row = layout.row()
            #to be edited based on the registration status
            row.label(text = bpy.context.scene.load_local_status)







"""def execute_operator(self, context):
    eval('bpy.ops.' + self.primitive + '()')
    
    
    class statusSavingProperties(bpy.types.PropertyGroup):
    mode_options = [
    ("mesh.primitive_plane_add", "Plane", '', 'MESH_PLANE', 0),
    ("mesh.primitive_cube_add", "Cube", '', 'MESH_CUBE', 1),
    ("mesh.primitive_circle_add", "Circle", '', 'MESH_CIRCLE', 2),
    ("mesh.primitive_uv_sphere_add", "UV Sphere", '', 'MESH_UVSPHERE', 3),
    ("mesh.primitive_ico_sphere_add", "Ico Sphere", '', 'MESH_ICOSPHERE', 4),
    ("mesh.primitive_cylinder_add", "Cylinder", '', 'MESH_CYLINDER', 5),
    ("mesh.primitive_cone_add", "Cone", '', 'MESH_CONE', 6),
    ("mesh.primitive_torus_add", "Torus", '', 'MESH_TORUS', 7)
    ]
    
    saving_status = bpy.props.EnumProperty(
    items=mode_options,
    description="offers....",
    default="mesh.primitive_plane_add",
    update=execute_operator
    )
    
    """

def calculate_Percent_Labeled():
    #going to calculate the number of neurons labeled:
    bpy.ops.object.mode_set(mode='OBJECT')
    ob = bpy.context.object
    ob.update_from_editmode()
    
    me = ob.data
    faces_raw = ob.data.polygons
    active_faces_raw = [k for k in faces_raw if k.material_index > 1]
    
    total_faces = len(faces_raw)
    total_labeled_faces = len(active_faces_raw)
    perc = round(float(total_labeled_faces)/float(total_faces)*100,2)
    bpy.context.scene.percent_labeled = str(perc)+"% faces labeled"





def execute_operator_neuron_saver(self, context):
    #set the variable that will be used for saving
    print("inside execute_operator_neuron_saver")
    bpy.context.scene.status_To_Save = self.primitive




class myNeuronsProperties_2(bpy.types.PropertyGroup):
    mode_options = [
                    ("partial","partial",""),
                    ("complete","complete",""),
                    
                    ]
        
                    primitive = bpy.props.EnumProperty(
                                                       items=mode_options,
                                                       description="offers....",
                                                       default="partial",
                                                       update=execute_operator_neuron_saver
                                                       )


def save_off_Neuron():
    #check to see if neuron was marked as complete and give warning if all
    bpy.ops.object.mode_set(mode='OBJECT')
    ob = bpy.context.object
    ob.update_from_editmode()
    
    me = ob.data
    faces_raw = ob.data.polygons
    active_faces_raw = [k for k in faces_raw if k.material_index > 1]
    
    if len(faces_raw) != len(active_faces_raw) and bpy.context.scene.complete_100_check_save_flag==False and bpy.context.scene.status_To_Save=="complete":
        bpy.context.scene.complete_100_check = "Not all faces labeled!"
        bpy.context.scene.complete_100_check_2 = "If OK, press Send again"
        bpy.context.scene.complete_100_check_save_flag = True
        return
    
    bpy.context.scene.complete_100_check_save_flag = False

#iterate through and save off all of the labels for vertices, edges, faces
ID = bpy.context.scene.picked_Neuron_ID
    #need to add the labels to the newly created object
    ob = bpy.data.objects["neuron-"+ID]
    
    
    me = ob.data
    #print("starting to hide everything")
    #iterate through all of the vertices
    verts_raw = ob.data.vertices
    #print(len(active_verts_raw))
    
    edges_raw = ob.data.edges
    
    #print(len(active_edges_raw))
    
    faces_raw = ob.data.polygons
    
    #download the size from the database
    
    
    n_edges = len(edges_raw)
    n_vertices = len(verts_raw)
    n_triangles = len(faces_raw)
    
    print("n_vertices = " + str(n_vertices))
    
    #make sure that length of verts, triangles are
    #same as in the mesh database
    
    primary_key = dict(segmentation=1,decimation_ratio=0.35)
    
    mesh_Dict = (ta3.Decimation & primary_key & "segment_id="+ID).fetch(as_dict=True)[0]
    
    
    
    #mesh_Dict = (mesh_Table & "segment_id="+ID).fetch(as_dict=True)[0] old way
    n_vertices_check = mesh_Dict['n_vertices']
    n_traingles_check = mesh_Dict['n_triangles']
    
    if (n_vertices_check != n_vertices) or (n_traingles_check != n_triangles):
        print("n_vertices = " + str(n_vertices))
        print("n_vertices_check = " + str(n_vertices_check))
        print("n_triangles = " + str(n_triangles))
        print("n_traingles_check = " + str(n_traingles_check))
        
        print("ERROR: vertices and traingles do NOT match")
        raise ValueError("ERROR: vertices and traingles do NOT match")
        return


    edges = np.zeros(n_edges,dtype=np.uint8)
    vertices = np.zeros(n_vertices,dtype=np.uint8)
    triangles = np.zeros(n_triangles,dtype=np.uint8)


    #iterate through all of the
for i,k in enumerate(verts_raw):
    #set the bevel weight
    vertices[i] = math.ceil(k.bevel_weight*100)
    
    for i,k in enumerate(edges_raw):
        #set the bevel weight
        edges[i] = math.ceil(k.bevel_weight*100)

for i,k in enumerate(faces_raw):
    triangles[i] = k.material_index
    
    #get ID, username, timestamp and status
    segment_ID = bpy.context.scene.picked_Neuron_ID
    author = bpy.context.scene.username_Login
    date_time = str(datetime.datetime.now())[0:19]
    status = bpy.context.scene.status_To_Save
    
    #insert the new row
    segmentation=1
    decimation_ratio=0.35
    
    labels_Table.insert1([segmentation,int(segment_ID),decimation_ratio,author,date_time,vertices,triangles,edges,status])
    
    #delete the current row with the same ID    #####need to decide if going to delete
    #(labels_Table & 'segment_ID='+ID).delete(verbose=False)
    
    #need to delete the neuron
    # deselect all
    bpy.ops.object.select_all(action='DESELECT')
    
    # selection
    bpy.data.objects['neuron-'+ID].select = True
    
    #need to save local copy
    #Name of folder = "local_neurons_saved"
    
    dir_path = os.path.dirname(os.path.realpath(__file__))
    
    data_folder = Path(dir_path)
    just_Folder = data_folder.parents[0]
    complete_path_Obj = just_Folder / "local_neurons_saved"
    
    
    added_string = segment_ID+"_"+author+"_"+ date_time[0:10]+"_"+date_time[11:].replace(":","-")+".npz"
    complete_path = complete_path_Obj / added_string
    
    complete_path = str(complete_path)
    
    """bpy.context.user_preferences.filepaths.script_directory = str(complete_path)
        
        
        
        
        
        file_parts = dir_path.split("/")
        file_parts.pop()
        #print(file_parts)
        just_Folder = "/".join(file_parts)
        complete_path = just_Folder + "local_neurons_saved"
        print(complete_path)"""
    
    
    #package up the data that would go to the database and save it locally name of the file will look something like this "4_bcelii_2018-10-01_12-12-34"
    #    np.savez("/Users/brendancelii/Google Drive/Xaq Lab/Datajoint Project/local_neurons_saved/"+segment_ID+"_"+author+"_"+
    #        date_time[0:9]+"_"+date_time[11:].replace(":","-")+".npz",segment_ID=segment_ID,author=author,
    #                    date_time=date_time,vertices=vertices,triangles=triangles,edges=edges,status=status)
    np.savez(complete_path,segment_ID=segment_ID,author=author,
             date_time=date_time,vertices=vertices,triangles=triangles,edges=edges,status=status)
        
             
             print(segment_ID+"_"+author+"_"+date_time[0:10]+"_"+date_time[11:].replace(":","-")+".npz")
             # remove it
             
             
             counter = 0
             #do a check that it was saved correctly 5 times and if not there
             new_Table = (labels_Table & "segment_id="+segment_ID  & "author='"+author+"'" & "date_time='"+date_time+"'").fetch()
             for i in range(0,5):
                 if new_Table.size > 0:
                     counter = counter + 1
                         else:
                             new_Table = (labels_Table & "segment_id="+segment_ID  & "author='"+author+"'" & "date_time='"+date_time+"'").fetch()

if not(counter>0):
    print("ERROR: neuron data was not sent to database correctly but was saved locally")
    raise ValueError("ERROR: neuron data was not sent to database correctly but was saved locally")
    else:
        #delete the current row with the same ID, username and the last time updated
        old_date_time = bpy.context.scene.last_Edited
        (labels_Table & "segment_id="+segment_ID & "author='"+author+"'" & "date_time='"+old_date_time+"'").delete(verbose="False")
        
        #delete the object from the scene
        bpy.ops.object.delete()
        
        #now need to set all of the settings
        reset_Scene_Variables(login_Flag=True)

#operator for the saving button
class finish_editing(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.finish_editing"
    bl_label = "finish_editing"
    
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def execute(self, context):
        save_off_Neuron()
        return {'FINISHED'}


#operator for the saving button
class get_percent_labeled(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.get_percent_labeled"
    bl_label = "get_percent_labeled"
    
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def execute(self, context):
        calculate_Percent_Labeled()
        return {'FINISHED'}


class MyDemoPanel(bpy.types.Panel):
    #Creates a Panel in the scene context of the properties editor
    bl_idname = "Tools_layout"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Label Neurons"
    bl_label = "Neuron Tab"
    
    
    #where to put the file name****************Not implemented yet
    file_Picked = "";
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool
        
        # Create a simple row.
        #layout.label(text=" Neuron Labels")
        #for the editing properties
        row = layout.row()
        row.label(text = "Logged in: " + bpy.context.scene.username_Login)
        row = layout.row()
        row.label(text = "Neuron ID: " + bpy.context.scene.picked_Neuron_ID)
        
        if bpy.context.mode == "EDIT_MESH":
            # Big render button
            ######currently not using setup colors####
            #row = layout.row()
            #row.operator("object.setup_colors", text="setup colors")
            row = layout.row()
            row.label(text = "Last Edited: " + bpy.context.scene.last_Edited)
            row = layout.row()
            row.label(text = "Last Status: " + bpy.context.scene.last_Status)
            
            row = layout.row()
            row.label(text = "Last User to Edit: " + bpy.context.scene.last_Edited_User )
            
            
            row = layout.row()
            #row.scale_y = 3.0
            row.operator("object.neuron_label_operator_a", text="reset view").myVar = "reset view"
            row = layout.row()
            row = layout.row()
            row = layout.row()
            row = layout.row()
            row = layout.row()
            #row.scale_y = 3.0
            row.operator("object.neuron_label_operator_a", text="remove Label").myVar = "no_color"
            
            # Big render button
            row = layout.row()
            #row.scale_y = 3.0
            row.operator("object.neuron_label_operator_a", text="Apical (blue)").myVar = "Apical (blue)"
            
            
            row = layout.row()
            #row.scale_y = 3.0
            row.operator("object.neuron_label_operator_a", text="Basal (yellow)").myVar = "Basal (yellow)"
            
            row = layout.row()
            #row.scale_y = 3.0
            row.operator("object.neuron_label_operator_a",  text="Oblique (green)").myVar = "Oblique (green)"
            
            # Big render button
            row = layout.row()
            #row.scale_y = 3.0
            row.operator("object.neuron_label_operator_a", text="Soma (red)").myVar = "Soma (red)"
            
            
            row = layout.row()
            #row.scale_y = 3.0
            row.operator("object.neuron_label_operator_a", text="Axon (orange)").myVar = "Axon (orange)"
            
            row = layout.row()
            #row.scale_y = 3.0
            row.operator("object.neuron_label_operator_a",  text="Dendrite (purple)").myVar = "Dendrite (purple)"
            
            
            # Big render button
            row = layout.row()
            #row.scale_y = 3.0
            row.operator("object.neuron_label_operator_a", text="Distal (pink)").myVar = "Distal (pink)"
            
            
            row = layout.row()
            #row.scale_y = 3.0
            row.operator("object.neuron_label_operator_a", text="Error (brown)").myVar = "Error (brown)"
            
            row = layout.row()
            #row.scale_y = 3.0
            row.operator("object.neuron_label_operator_a", text="Unlabelable (tan)").myVar = "Unlabelable (tan)"
            
            
            
            row = layout.row()
            #row.scale_y = 3.0
            row.operator("object.neuron_label_operator_a", text="print label").myVar = "print"
            
            # display the properties
            layout.prop(mytool, "hide_Labels", text="hide labeled")
            layout.prop(mytool, "visible_only_selection", text="Visible Only Selection")
            
            row = layout.row()
            row = layout.row()
            row = layout.row()
            row = layout.row()
            
            
            
            row = layout.row()
            row.operator("object.neuron_label_operator_a", text="Exit Edit Mode").myVar = "exit_edit_mode"
            
            row = layout.row()
            row = layout.row()
            row = layout.row()
            row = layout.row()
            row = layout.row()
            row = layout.row()
            row = layout.row()
            row = layout.row()
            # Create a simple row.
            layout.label(text=" Labels for Later:")
            row = layout.row()
            
            #row.scale_y = 3.0
            row.operator("object.neuron_label_operator_a",  text="Spine Head (rose)").myVar = "Spine Head (rose)"
            
            
            # Big render button
            row = layout.row()
            #row.scale_y = 3.0
            row.operator("object.neuron_label_operator_a", text="Spine (light pink)").myVar = "Spine (light pink)"
            
            
            
            row = layout.row()
            #row.scale_y = 3.0
            row.operator("object.neuron_label_operator_a", text="Bouton (aqua)").myVar = "Bouton (aqua)"
        
        
        #when the neuron is not being edited
        if bpy.context.mode == "OBJECT":
            
            row = layout.row()
            row = layout.row()
            #row.scale_y = 3.0
            row.operator("object.neuron_label_operator_a", text="reset view").myVar = "reset view"
            
            row = layout.row()
            row = layout.row()
            #row.scale_y = 3.0
            row.operator("object.continue_editing", text="Continue Editing")
            
            col = layout.column()
            col.label(text="Upload Neuron to Database:")
            
            col.prop(context.scene.my_neurons_properties_2, "primitive")
            if context.scene.login_Flag != True or bpy.context.scene.picked_Neuron_ID == '':
                col.enabled = False
            else:
                col.enabled = True
            
            row = layout.row()
            row.operator("object.get_percent_labeled", text="Get % Labeled")
            if context.scene.login_Flag != True or bpy.context.scene.picked_Neuron_ID == '' or bpy.context.scene.status_To_Save =="":
                row.enabled = False
            else:
                row.enabled = True
        
            row = layout.row()
            row.label(text = bpy.context.scene.percent_labeled)
            
            
            
            row = layout.row()
            row.operator("object.finish_editing", text="Send to Database")
            if context.scene.login_Flag != True or bpy.context.scene.picked_Neuron_ID == '' or bpy.context.scene.status_To_Save =="" or bpy.context.scene.percent_labeled =="":
                row.enabled = False
            else:
                row.enabled = True


row = layout.row()
    row.label(text = bpy.context.scene.complete_100_check )
    
    row = layout.row()
        row.label(text = bpy.context.scene.complete_100_check_2 )
        
        
        row = layout.row()
            row = layout.row()
            row = layout.row()
            row.operator("object.submit_registration_login", text="Logout").myRegVar = "logout"
            if bpy.context.scene.username_Login == "":
                row.enabled = False
        else:
            row.enabled = True
            
            
            row = layout.row()
            row.scale_y = 3.0
            row = layout.row()
            row.scale_y = 3.0
            row = layout.row()

class delete_neuron_without_saving(bpy.types.Panel):
    """Creates a Panel that you can open in order to get the register fields"""
    bl_idname = "delete_neuron_without_saving"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Label Neurons"
    bl_label = "Delete Neuron"
    bl_context = "objectmode"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool
        
        #only want this drawn if in object mode
        if bpy.context.mode == "OBJECT":
            row = layout.row()
            row.prop(context.scene, "delete_ID")
            
            
            row = layout.row()
            row.label(text = "Delete Neuron " + bpy.context.scene.delete_ID + " without saving" )
            row = layout.row()
            row.operator("object.neuron_label_operator_a", text="Delete neuron").myVar = "delete_Neuron"
            if (bpy.context.scene.delete_ID == ""):
                row.enabled = False
            else:
                row.enabled = True
        
            #row = layout.row()
            #row.label(text = "Are you sure?")
            row = layout.row()
            row.label(text = bpy.context.scene.delete_status)
            row = layout.row()
            row.operator("object.neuron_label_operator_a", text="Yes").myVar = "delete_Yes"
            if bpy.context.scene.delete_Flag == False or bpy.context.scene.delete_ID == "":
                row.enabled = False
    else:
        row.enabled = True
            
            row.operator("object.neuron_label_operator_a", text="No").myVar = "delete_No"
            if bpy.context.scene.delete_Flag == False or bpy.context.scene.delete_ID == "":
                row.enabled = False
            else:
                row.enabled = True





def create_global_colors():
    
    
    #get the list of colors already available in the bpy.data
    list = bpy.data.materials.keys()
    
    #adds all of the colors to the master list in blender file if they are not there already
    colors = getColors()
    #print(colors)
    diffuse_colors_list = [(0.800, 0.800, 0.800),(0.800, 0.800, 0.800),
                           (0.0, 0.0, 0.800),(0.800, 0.800, 0.0), #blue, "yellow
                           (0.0, 0.800, 0.0),(0.800, 0.0, 0.0),   #green, red
                           (0.800, 0.181, 0.013),(0.200, 0.0, 0.800), #orange, purple
                           (0.800, 0.0, 0.400),(0.250, 0.120, 0.059), #pink, brown
                           (0.800, 0.379, 0.232),(0.800, 0.019, 0.093), #tan, rose
                           (0.800, 0.486, 0.459),(0.0, 0.800, 0.527)] #light_pink, aqua
        
        
                           for i in range(0,len(colors)):
                               if not(colors[i] in list):
                                   mat = bpy.data.materials.new(name=colors[i]);
                                   mat.diffuse_color = diffuse_colors_list[i]
                                       else:  #if it already exists make sure to set colors list right
                                           bpy.data.materials[colors[i]].diffuse_color = diffuse_colors_list[i]

def create_local_colors(ob=bpy.context.object):
    #make sure all of the global colors are set correctly
    create_global_colors()
    #get current object
    #ob = bpy.context.object
    
    #get the colors list
    colors = getColors()
    
    #makes sure that length of color list matches the number of labels/colrs needed + 1
    if(ob.data != None):
        difference = len(ob.data.materials) - len(colors)
    else:
        print("materials was none")
        difference = -len(colors)
    
    #if less than 6 colors already then add the spots there
    if(difference < 0):
        for i in range(0,-difference):
            ob.data.materials.append(None)

#print(len(ob.data.materials))

#make sure the colors are in the correct order for the object

for i in range(0,len(colors)):
    ob.data.materials[i] = bpy.data.materials[colors[i]]

def ShowMessageBox(message = "", title = "Message Box", icon = 'INFO'):
    
    def draw(self, context):
        self.layout.label(message)
    
    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.my_tool = PointerProperty(type=MySettings)
    bpy.types.Scene.my_status_properties = bpy.props.PointerProperty(type=statusProperties)
    bpy.types.Scene.my_neurons_properties = bpy.props.PointerProperty(type=myNeuronsProperties)
    bpy.types.Scene.my_neurons_properties_2 = bpy.props.PointerProperty(type=myNeuronsProperties_2)
#bpy.types.Scene.my_status_saving_properties = bpy.props.PointerProperty(type=statusSavingProperties)

#bpy.utils.register_class(load_file_operator)
#bpy.utils.register_class(setup_colors)
#bpy.utils.register_class(Neuron_Label_Operator_a)
#bpy.utils.register_class(MyDemoPanel)


def unregister():
    bpy.utils.unregister_class(__name__)
    del bpy.types.Scene.my_tool
    del bpy.types.Scene.my_status_properties
    del bpy.types.Scene.my_neurons_properties
    
    del bpy.types.Scene.my_status_saving_properties





#*************Databae Code**************#####

#import sys
#sys.path.append("/Library/Frameworks/Python.framework/Versions/3.6/lib/python3.6/site-packages/")
#where you could put them /Users/brendancelii/Google Drive/Xaq Lab
#sys.path.append("/Users/brendancelii/Google Drive/Xaq Lab")

######block of code that will add the working folder to the lookup spots for scripts

"""dir_path = os.path.dirname(os.path.realpath(__file__))
    file_parts = dir_path.split("/")
    file_parts.pop()
    #print(file_parts)
    just_Folder = "/".join(file_parts)
    complete_path = just_Folder + "/blender_scripts/"
    print(complete_path)
    bpy.context.user_preferences.filepaths.script_directory = complete_path"""

#set the path in the user preferences

import datajoint as dj



if __name__ == "__main__":
    register()
    create_global_colors()
    try:
        print("neuron tab labeler started new")
        #setting the address and the username
        print("about to connect to database")
        dj.config['database.host'] = '10.28.0.34'
        dj.config['database.user'] = 'celiib'
        dj.config['database.password'] = 'newceliipass'
        #will state whether words are shown or not
        dj.config['safemode']=False
        print(dj.conn(reset=True))
    except:
        #Shows a message box with a specific message
        ShowMessageBox("Make sure connected to bcm-wifi!!")
        print("ERROR: Make sure connected to bcm-wifi!!")
#raise ValueError("ERROR: Make sure connected to bcm-wifi!!")

else:
    #connect_to_Databases()
    #create the database inside the server
    schema = dj.schema('microns_ta3',create_tables=False)
    ta3 = dj.create_virtual_module('ta3', 'microns_ta3')
    reset_Scene_Variables()
    
    @schema
        class Annotation(dj.Manual):
            definition = """
                # creates the labels for the mesh table
                -> ta3.Decimation
                author     : varchar(20)  # name of last editor
                date_time  : timestamp   #the last time it was edited
                ---
                vertices   : longblob     # label data for the vertices
                triangles  : longblob     # label data for the faces
                edges      : longblob     # label data for the edges
                status     : varchar(16)          # the index of the status descriptor that can be references by the StatusKey
                """
        
        
        # @schema
        # class Status(dj.Manual):
        #     definition = """
        #     -> Annotation
        #     ---
        #     (status) -> StatusKey
        #     """
        
        @schema
        class LabelKey(dj.Lookup):
            definition = """
                # maps numeric labels to descriptive labels
                numeric     : tinyint       # numeric label of the cell part
                ---
                real_name   : varchar(40)   # actual name of the label
                """
            contents = [
                        [0, 'no_color'],
                        [1, 'no_color'],
                        [2, 'Apical'],
                        [3, 'Basal'],
                        [4, 'Oblique'],
                        [5, 'Soma'],
                        [6, 'Axon'],
                        [7, 'Spine Head'],
                        [8, 'Spine'],
                        [9, 'Bouton']
                        ]
        
        @schema
        class Authors(dj.Manual):
            definition = """
                # maps numeric labels to descriptive labels
                username     : varchar(20)       # username the person pcisk
                ---
                real_name   : varchar(40)   #the real name of that corresponds to the username
                """
        
        #######DONE SETTING UP ALL OF THE TABLES#########
        
        #create reference to all of the tables
        labels_Table = Annotation()
        mesh_Table = ta3.Mesh()
        #status_key_table = StatusKey()
        label_key_table = LabelKey()
        author_table = Authors()
