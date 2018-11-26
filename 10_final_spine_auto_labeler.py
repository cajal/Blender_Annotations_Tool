import bpy

#This one will pull down some of the larger segments from the datajoint 
#table and then apply the automatic segmentation to them

#######Steps##############
'''1) Get the neuron the person wants to look at
2) Import the neuron and generate edges
3) Get the compartment_type person wants
4) Find the component_index that corresponds to the biggest one because that is the one we want
5) Delete all the edges, faces and vertices that do not correspond to these labels
6) Generate an OFF file for the current segment
7) Run the OFF file through the CGAL segmentation algorithm using the INPUT PARAMETERS
8) Run the auto spine labeler using the CGAL segmentation list
9) Label the colors of the auto labeled spines and show the final product
10) Output stats to a csv so they can be analyzed'''

####How to import from the segment table

import datajoint as dj
import numpy as np
import datetime
import math
from mathutils import Vector
from final_Neuron_Tab_vp13 import create_local_colors , set_View, create_bounding_box, create_global_colors

def select_Neuron():
    # deselect all
    bpy.ops.object.select_all(action='DESELECT')

    # selection
    for obj in bpy.data.objects:
        if "neuron" in obj.name:
            obj.select = True
            bpy.context.scene.objects.active = obj
            print("object was found and active")
            break

#1) Get the neuron the person wants to look at
#2) Import the neuron and generate edges

def filter_verts_and_faces(ID,compartment_type,component_index,verts,faces):
    #go and get the triangles and the vertices from the database
    comp = ta3.Compartment.Component()
    
    """compartment_type
    decimation_ratio
    segmentation
    segment_id"""
    
    primary_key = dict(segmentation=1, segment_id=ID, decimation_ratio=0.35,compartment_type=compartment_type, component_index=component_index)
    verts_label, triangles_label = (comp & primary_key).fetch('vertex_indices','triangle_indices')
    
    verts_label = verts_label.tolist()[0]
    triangles_label = triangles_label.tolist()[0]
    
    verts_keep = []
    faces_keep = []
    verts_lookup = {}
    
    for i,ver in enumerate(verts_label):
        verts_keep.append(verts[ver])
        verts_lookup[ver] = i
    
    #generate the new face labels
    for fac in triangles_label:
        faces_with_verts = faces[fac]
        new_tuple = []
        for v in faces_with_verts:
            new_tuple.append(verts_lookup[v])
        
        faces_keep.append(new_tuple)
    #check that the new verts and faces to return are same length as the indices
    """if len(triangles_label) != len(faces_keep) or len(verts_label) != len(verts_keep):
        print("ERROR THE FILTERED LABELS ARE NOT THE SAME SIZE AS THE INDICES LISTS!")"""
     
    return verts_keep,faces_keep
    
def load_Neuron_automatic_spine(ID,compartment_type,compartment_index):
    print("inside load Neuron")
 
    #neuron_data = ((mesh_Table & "segment_ID="+ID).fetch(as_dict=True))[0]
    primary_key = dict(segmentation=1,decimation_ratio=0.35)
    neuron_data = ((ta3.CleansedMesh & primary_key & "segment_ID="+ID).fetch(as_dict=True))[0]


    
    verts = neuron_data['vertices'].astype(dtype=np.int32).tolist()
    faces = neuron_data['triangles'].astype(dtype=np.uint32).tolist()
    
    #could filter the verts and the faces here for just the ones we want
    verts,faces = filter_verts_and_faces(ID,compartment_type,compartment_index,verts,faces)
    
    mymesh = bpy.data.meshes.new("neuron-"+ID)
    mymesh.from_pydata(verts, [], faces)
 
    mymesh.update(calc_edges=True)
    mymesh.calc_normals()

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

    object.rotation_euler[0] = 1.5708
    object.rotation_euler[1] = 0
    object.rotation_euler[2] = 0

    object.lock_rotation[0] = True
    object.lock_rotation[1] = True
    object.lock_rotation[2] = True


    #set view back to normal:
    set_View()

    #run the setup color command
    #bpy.ops.object.select_all(action='TOGGLE')
    
    #create_local_colors(object)

    #make sure in solid mode
    for area in bpy.context.screen.areas: # iterate through areas in current screen
        if area.type == 'VIEW_3D':
            for space in area.spaces: # iterate through spaces in current VIEW_3D area
                if space.type == 'VIEW_3D': # check if space is a 3D view
                    space.viewport_shade = 'SOLID' # set the viewport shading to rendered
    
    return object.name




##write the OFF file for the neuron

def write_Part_Neuron_Off_file(verts_for_off,faces_for_off,faces_indexes_for_off,segment_id,compartment_type_name,found_component_index,file_loc):
    print('inside write_Part_neuron')
    num_vertices = (len(verts_for_off))
    num_faces = len(faces_indexes_for_off)
    
    file_location = file_loc
    filename = "neuron_" + str(segment_id) + "_" + str(compartment_type_name) + "_" + str(found_component_index)
    f = open(file_location + filename + ".off", "w")
    f.write("OFF\n")
    f.write(str(num_vertices) + " " + str(num_faces) + " 0\n" )
    
    ob = bpy.context.object
    verts_raw = ob.data.vertices
    
    #iterate through and write all of the vertices in the file
    verts_lookup = {}
    
    counter = 0
    for vert_num in verts_for_off:
        f.write(str(verts_raw[vert_num].co[0]) + " " + str(verts_raw[vert_num].co[1]) + " " + str(verts_raw[vert_num].co[2])+"\n")
        verts_lookup[vert_num] = counter
        
        counter += 1
        
    faces_lookup_reverse = []
    counter = 0
    
    print("finished writing verts")
    for i in range(0,len(faces_indexes_for_off)):
        face_indices = faces_indexes_for_off[i]
        f.write("3 " + str(verts_lookup[face_indices[0]]) + " " + str(verts_lookup[face_indices[1]]) + " " + str(verts_lookup[face_indices[2]])+"\n")
        faces_lookup_reverse.append(faces_for_off[i])
        counter += 1
  
    print("finished writing faces")
    print("done_writing_off_file")
    #f.write("end")
    return filename,faces_lookup_reverse
    

def generate_off_file_for_compartment(segment_id, compartment_type_name,ob_Name,file_loc):
    
    comp = ta3.Compartment.Component()
    
    """compartment_type
    decimation_ratio
    segmentation
    segment_id"""
    
    primary_key = dict(segmentation=1, segment_id=segment_id, decimation_ratio=0.35,compartment_type=compartment_type_name)
    component_index, vertices = (comp & primary_key).fetch('component_index','vertex_indices')
    
    found_component_index = 0
    for i in range(0,len(component_index)):
        if len(vertices[i]) > 200:
            found_component_index = i
            break
    
    #just save off the indices faces into an OFF file
    verts_for_off = vertices[found_component_index]
    
    #get the verts_to_face lookup dictionary
    
    """
    verts_to_Face = {}
    
    #initialize the lookup dictionary as empty lists
    verts_raw = bpy.data.objects[ob_Name].data.vertices
    for pre_vertex in verts_raw:
        verts_to_Face[pre_vertex.index] = []
        
   
    
    faces_raw = bpy.data.objects[ob_Name].data.polygons
    #making the verts to face lookup
    for face in faces_raw:
        #get the vertices
        verts = face.vertices
        #add the index to the list for each of the vertices
        for vertex in verts:
            verts_to_Face[vertex].append(face.index)
    """
    print('finished making verts_to_face')
    
    select_Neuron()
    
    
    filename = "neuron_" + str(segment_id) + "_" + str(compartment_type_name) + "_" + str(found_component_index) + "_face_matrix.npz"
    complete_path = file_loc + "face_matrix/"+ filename
    
    try:
        face_matrix = np.load(complete_path)
    except:
        print("wasn't already a face matrix npz file")
        faces_raw = bpy.context.object.data.polygons
        faces_indexes_for_off = []
        faces_for_off = []
        for faz in faces_raw:
            verts_from_fac = faz.vertices
            active_Flag = True
            for ver in verts_from_fac:
                if ver not in verts_for_off:
                    active_Flag = False
                    break
            
            if active_Flag == True:
                faces_indexes_for_off.append(verts_from_fac)
                faces_for_off.append(faz.index)
        """
        for verts in verts_for_off:
            faces_from_vert = verts_to_Face[verts]
            
            for fac in faces_from_vert:
                if fac not in faces_for_off:
                    faces_for_off.append(fac)"""
                    
        
        
        #save off the faces_raw as an npz file
        np.savez(complete_path,faces_for_off=faces_for_off,faces_indexes_for_off=faces_indexes_for_off)
    else:
        print("ALREADY was a face matrix npz file")
        faces_for_off = face_matrix["faces_for_off"]
        faces_indexes_for_off = face_matrix["faces_indexes_for_off"]
        
    
    print('finished making faces_off')
    
    #now have the faces and the vertices that will be used by the compartment_type
    #send them to generate the off file
    filename,faces_lookup_reverse = write_Part_Neuron_Off_file(verts_for_off,faces_for_off,faces_indexes_for_off,segment_id,compartment_type_name,found_component_index,file_loc)
    
    return verts_for_off,faces_for_off,filename,faces_lookup_reverse,
     
        

def hide_non_compartment(verts_for_off,faces_for_off, ob_name):
    select_Neuron()
    currentMode = bpy.context.object.mode
    bpy.ops.object.mode_set(mode='OBJECT')
    ob = bpy.context.object
    ob.update_from_editmode()

    me = ob.data

    print("len(verts_for_off) = " + str(len(verts_for_off) ))
    print(verts_for_off)
    verts_raw = ob.data.vertices
    for vert in verts_for_off:
        verts_raw[vert].select = False
        verts_raw[vert].hide = True
    
    print("len(faces_for_off) = " + str(len(faces_for_off) ))
    
    
    
    
    #get the new face indexes from the database
    comp = ta3.Compartment.Component()
    
    compartment_type_name = "Apical"
    segment_id = 331199
    component_index = 0

    primary_key = dict(segmentation=1, segment_id=segment_id, decimation_ratio=0.35,compartment_type=compartment_type_name,component_index=component_index)
    face_labels = (comp & primary_key).fetch('triangle_indices')

    
    
    ####--------Trying new database
    
    
    print("len(face_labels.tolist()[0]) = " + str(len(face_labels.tolist()[0])))
    face_labels_final = face_labels.tolist()[0]
    faces_raw = ob.data.polygons
    for fac in face_labels_final:
        faces_raw[fac].select = True
        faces_raw[fac].hide = False
        faces_raw[fac].material_index = 2
    
    """faces_raw = ob.data.polygons
    for fac in faces_for_off:
        faces_raw[fac].select = True
        faces_raw[fac].hide = False
        faces_raw[fac].material_index = 1"""
    
    ob.data.materials.append(None)
    ob.data.materials.append(None)
    mat = bpy.data.materials.new("current_label");
    mat.diffuse_color = [.009,0.012,0.800]
    ob.data.materials[1] = mat
    
    
    

"""Tables we will use 
proofLabels = ta3.ProofreadLabel()
mesh_Table = ta3.CleansedMesh()
mesh_Table_35 = (mesh_Table & "decimation_ratio=0.35")

#This table only comes with the valuable attributes of 
#1) compartment_type: apical, basal....
#2) component_index: just need to pick the biggest one of all of these
#3) vertex_indices: the indices that have the labels that correspond to theh apical, basal, etc.



comp = ta3.Compartment.Component()

#comp

seg_id = 331199
label_type = "Apical"
big_list = list(zip(*(ta3.Compartment.Component() & 
           dict(segment_id=seg_id) & 
           dict(compartment_type=label_type)).fetch('segment_id',
                                                    'compartment_type', 'component_index', 'vertex_indices')))
                                                    
#Access the largest table
print(len(big_list[0][3]))


"""




def get_cgal_segmentation_csv(segment,ID,
                    clusters,smoothness,file_loc,off_file_name):
    csv_file_name = off_file_name + "-cgal_" + str(clusters) + "_"+str(smoothness) + ".csv"
    
    
    ID = str(ID)
    #import the csv file into a list
    

    #"-segmentation_3_0.1.csv" how it looks
    
    with open(file_loc + csv_file_name, 'r') as f:
      reader = csv.reader(f)
      your_list = list(reader)
    triangles_labels = []
    for item in your_list:
        triangles_labels.append(int(item[0]))
    
    #activate the current object
    select_Neuron()
    ob = bpy.context.object
    
    
    me = ob.data
    
    #print("starting to hide everything")
    #iterate through all of the vertices
    verts_raw = ob.data.vertices
    #print(len(active_verts_raw))
    
    edges_raw = ob.data.edges
    
    #print(len(active_edges_raw))
    
    faces_raw = ob.data.polygons
    
  
            
    print("inside mesh")
    #print(Counter(triangles_labels))
    print('verts_raw = ' + str(len(verts_raw)))
    print('faces_raw = ' + str(len(faces_raw)))
    
    
    #print number of unique labels
    unique_segments = list(Counter(triangles_labels).keys())
    
    
    segmentation_length = len(unique_segments) # equals to list(set(words))
    #print(segmentation_length)

    unique_index_dict = {unique_segments[x]:x for x in range(0,segmentation_length)}
    
    
    print("unique_index_dict = " + str(len(unique_index_dict)))
    print("triangle_labels = " + str(len(triangles_labels)))
    #adds all of the labels to the faces
    max_length = len(triangles_labels)
    
    #just iterate and add them to the faces
    for i,k in enumerate(faces_raw):
        k.material_index = int(unique_index_dict[triangles_labels[i]]) 
    
    
    #go into edit mode
    print("trying to select the neuron")
    
    select_Neuron()
    
    
    #make sure in solid mode
    for area in bpy.context.screen.areas: # iterate through areas in current screen
        if area.type == 'VIEW_3D':
            for space in area.spaces: # iterate through spaces in current VIEW_3D area
                if space.type == 'VIEW_3D': # check if space is a 3D view
                    space.viewport_shade = 'SOLID' # set the viewport shading to rendered
    
    bpy.ops.object.mode_set(mode='OBJECT')
    


            ######--------setting up the colors -------------###########
    ###assign the color to the object
    current_Material_length = len(bpy.data.materials)
    
    #remove all of the previous numbered colors
    color_keys = bpy.data.materials.keys()

    
    #generate new colors for the bpy.data global

    segment_random_colors(ob=ob,unique_segments=unique_segments,extraFlag=False)
    
    #these variables are set in order to keep the functions the same as FINAL_importing_auto_seg.py
    newname = ob.name
    
    return segmentation_length, newname

def generate_off_file_new(segment_id,compartment_type,found_component_index,ob_name,file_loc):
    print('inside generate_off_file_new')
    
    #get the faces and the vertices
    select_Neuron()
    ob = bpy.context.object
    
    triangles = ob.data.polygons
    vertices = ob.data.vertices
    
    num_vertices = (len(vertices))
    num_faces = len(triangles)
    
    
    file_location = file_loc
    filename = "neuron_" + str(segment_id) + "_" + str(compartment_type) + "_" + str(found_component_index)
    f = open(file_location + filename + ".off", "w")
    f.write("OFF\n")
    f.write(str(num_vertices) + " " + str(num_faces) + " 0\n" )
    
    
    #iterate through and write all of the vertices in the file
    for verts in vertices:
        f.write(str(verts.co[0]) + " " + str(verts.co[1]) + " " + str(verts.co[2])+"\n")
        
    for faces in triangles:
        verts_from_fac = faces.vertices
        f.write("3 " + str(verts_from_fac[0]) + " " + str(verts_from_fac[1]) + " " + str(verts_from_fac[2])+"\n")
    
    print("done_writing_off_file")
    #f.write("end")
    return filename



import sys
import numpy as np
#import matplotlib.pyplot as plt
import networkx as nx





from auto_spine_labeler_vp4 import automatic_spine_classification_vp2,smooth_backbone
from FINAL_importing_auto_seg import segment_random_colors
import csv
from collections import Counter

if __name__ == "__main__":
    first_half_flag = False
    
    ID = "331199"
    compartment_type = "Apical"
    compartment_index = 0
    clusters = "10"
    smoothness = "0.04"
    seg = "6"
    
    file_loc = "/Users/brendancelii/Google Drive/Xaq Lab/Datajoint Project/Automatic_Labelers/auto_segmented_big_segments/"
    
    if first_half_flag == True:
    #create_global_colors()
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
            print("Make sure connected to bcm-wifi!!")
            print("ERROR: Make sure connected to bcm-wifi!!")
            #raise ValueError("ERROR: Make sure connected to bcm-wifi!!")
        
        else:
            #connect_to_Databases()
            #create the database inside the server
            schema = dj.schema('microns_ta3',create_tables=False)
            ta3 = dj.create_virtual_module('ta3', 'microns_ta3')
            #reset_Scene_Variables()
        
        
        
        ob_name = load_Neuron_automatic_spine(ID,compartment_type,compartment_index)
        create_bounding_box()
        off_file_name = generate_off_file_new(ID,compartment_type,compartment_index,ob_name,file_loc)
        
        ##verts_for_off, faces_for_off,off_file_name, faces_lookup_reverse = generate_off_file_for_compartment(ID,compartment_type,ob_name,file_loc)
        ##hide_non_compartment(verts_for_off,faces_for_off,ob_name)
        
        #example of output off file name: neuron_331199_Apical_0
        
        #save off the reverse lookup table to use for another time
        ##lookup_file_name = off_file_name + "_faces_lookup.npz"
        ##complete_path = file_loc + "faces_lookup/" + lookup_file_name
        
        
        #save off the faces_raw as an npz file
        ##np.savez(complete_path,faces_lookup_reverse=faces_lookup_reverse)
    
    else:
        off_file_name = "neuron_331199_Apical_0"
        
        #goes and applies the segmentation created by the cgal function to the actual mesh
        segmentation_length, newname  = get_cgal_segmentation_csv(segment=seg,ID=ID,
                clusters=clusters,smoothness=smoothness,file_loc=file_loc,off_file_name=off_file_name)
            
        
        
        bpy.context.scene.objects.active = bpy.data.objects[newname]
                    
        
        
        max_backbone_threshold = 600
        backbone_threshold=200
        secondary_threshold=20
        shared_vert_threshold=25
        smooth_backbone(max_backbone_threshold = max_backbone_threshold,backbone_threshold=backbone_threshold
                    ,secondary_threshold=secondary_threshold,shared_vert_threshold=shared_vert_threshold,number_Flag = False, seg_numbers=1,smooth_Flag=True)
        
        head_counter,neck_counter, spine_counter, stub_counter = automatic_spine_classification_vp2()
        
        print("head_counter = " + str(head_counter))
        print("neck_counter = " + str(neck_counter))
        print("spine_counter = " + str(spine_counter))
        print("stub_counter = " + str(stub_counter))
        
            
            
            
            
            
        
    
   
    
    
    
    
    
    































