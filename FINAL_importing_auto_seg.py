import bpy


import csv
from collections import Counter
import random

def create_global_colors():  

    
    #get the list of colors already available in the bpy.data 
    list = bpy.data.materials.keys()  
    
    #adds all of the colors to the master list in blender file if they are not there already
    colors = getColors()
    #print(colors)
    diffuse_colors_list = [(0.800, 0.800, 0.800),(0.800, 0.800, 0.800),
    (0.0, 0.0, 0.800),(0.800, 0.800, 0.0), #blue, "yellow
    (0.0, 0.800, 0.0),(0.800, 0.0, 0.0),   #green, red
    (0.0, 0.800, 0.527),(0.049, 0.458, 0.800),(0.200, 0.0, 0.800), #aqua, off blue, purple
    (0.800, 0.0, 0.400),(0.250, 0.120, 0.059), #pink, brown
    (0.800, 0.379, 0.232),(0.800, 0.019, 0.093), #tan, rose
    (0.800, 0.486, 0.459),(0.309,0.689,0.170),(0.800, 0.181, 0.013)] #light_pink, #light green orange
    
    
    for i in range(0,len(colors)):
        if not(colors[i] in list):
            mat = bpy.data.materials.new(name=colors[i]);
            mat.diffuse_color = diffuse_colors_list[i]
        else:  #if it already exists make sure to set colors list right
            bpy.data.materials[colors[i]].diffuse_color = diffuse_colors_list[i]
            
def getColors():
    return ["no_color","no_color","Apical (blue)","Basal (yellow)","Oblique (green)"
                    ,"Soma (red)","Axon-Soma (aqua)","Axon-Dendr (off blue)","Dendrite (purple)","Distal (pink)",
                    "Error (brown)","Unlabelable (tan)","Spine Head (rose)",
                    "Spine (light pink)","Spine Neck (light green)","Bouton (aqua)"]
def getLabels():
    return ["None","None","Apical","Basal","Oblique","Soma","Axon-Soma","Axon_Dendr","Dendrite","Distal","Error","Unlabelable","Spine Head","Spine","Spine Neck","Bouton"]


######*******CHANGE TO USE SETS INSTEAD OF LISTS**********#############
def find_neighbors(labels_list,current_label,verts_to_Face,faces_raw,verts_raw):
    """will return the number of neighbors that border the segment"""
    
    #iterate over each face with that label
    #   get the vertices of that face
    #   get all the faces that have that vertice associated with that
    #   get the labels of all of the neighbor faces, for each of these labels, add it to the neighbors 
    #list if it is not already there and doesn't match the label you are currently checking
    #   return the list 
    
    #get the indexes of all of the faces with that label
    
    index_list = []
    for i,x in enumerate(labels_list):
        if x == current_label:
            index_list.append(i)
    
    verts_list = []
    faces_to_check = []
    for index in index_list:
        current_face = faces_raw[index]
        
        #get the vertices associates with face
        vertices = current_face.vertices
        
        #get the faces associated with the vertices
        for vert in vertices:
            faces_associated_vert = verts_to_Face[vert]
            for fac in faces_associated_vert:
                if fac not in faces_to_check:
                    #faces_to_check.append(fac)
                    faces_to_check.insert(0, fac)
    
    #have all of the faces to check
    neighbors_list = []
    for facey in faces_to_check:
        if labels_list[facey] != current_label and labels_list[facey]  not in neighbors_list:
            neighbors_list.append(labels_list[facey] )
    
    return neighbors_list
    
    
def relabel_segments(labels_list,current_label,new_label):
    for i,x in enumerate(labels_list):
        if x == current_label:
            labels_list[i] = new_label
            
    return labels_list
    
def classify_spines(labels_list,threshold=1000):

    
    #have to go into object mode to do some editing
    currentMode = bpy.context.object.mode

    bpy.ops.object.mode_set(mode='OBJECT')
    ob = bpy.context.object
    ob.update_from_editmode()
    
    #print("object_name = " + bpy.context.object.name)
    me = ob.data
    faces_raw = me.polygons
    verts_raw = me.vertices
    
    
    verts_to_Face = {}
    
    #initialize the lookup dictionary as empty lists
    for pre_vertex in verts_raw:
        verts_to_Face[pre_vertex.index] = []
        
    #print(len(verts_raw))
    #print(len(verts_to_Face))
    #print(verts_to_Face[1])
    
    
    #making the verts to face lookup
    for face in faces_raw:
        #get the vertices
        verts = face.vertices
        #add the index to the list for each of the vertices
        for vertex in verts:
            verts_to_Face[vertex].append(face.index)
    
    #get a printout of all of the labels and how many there are
    #1) iterate through the whole list and compile a summary of it using Counter library
    #2) if label is below threshold
    #3) check it for how many neighbors it has
    #4) if number of neighbors is 1 its only neighbor is big guy --> label spine
    #5) if number is 1 and neighbor is small guy --> label spine head
    #6) if number is 2 and neighbor is small guy and big guy --> label neck
    #7) else label error
    #8) DON'T NEED TO ASSIGN COLORS BECAUSE WILL DO THHIS LATER
    myCounter = Counter(labels_list)
    print(myCounter)
    
    big_labels = [i for i,j in myCounter.items() if j > threshold]
    print("big labels = " + str(big_labels))
    
    #if multiple big labels then print that out and ALERT
    if len(big_labels)>1:
        print("THERE ARE MULTIPLE BIG LABELS IN THIS OBJECT")
    
    small_labels = [i for i,j in myCounter.items() if j < threshold]
    print("small_labels = " + str(small_labels))
    
    total_unique_labels = len(myCounter.items()) + 20
    spine_label = 4 + total_unique_labels
    dendrite_label = 1 + total_unique_labels
    spine_head_label = 2 + total_unique_labels
    spine_neck_label = 3 + total_unique_labels
    unknown = 0 + total_unique_labels
    
    print(spine_label)
    print(dendrite_label)
    print(spine_head_label)
    print(spine_neck_label)
    print(unknown)
    
    newList = labels_list.copy()
    print(Counter(newList))
    print("start relabeling")
    
    #relabel all of the big labels
    for lab in big_labels:
        print("lab = " + str(lab))
        relabel_segments(newList,lab,dendrite_label)
    
    #print(newList)
    
    for s_label in small_labels:
        neighbor_labels = find_neighbors(labels_list,s_label,verts_to_Face,faces_raw,verts_raw)
        
        print("len of neighbors = " + str(len(neighbor_labels)))
        if len(neighbor_labels) == 1 and neighbor_labels[0] in big_labels:
            #assign the spine label for each label with that value
            relabel_segments(newList,s_label,spine_label)
        elif len(neighbor_labels) == 1 and neighbor_labels[0] in small_labels:
            relabel_segments(newList,s_label,spine_head_label)
        elif len(neighbor_labels) >= 2:
            big_flag = 0
            small_flag = 0
            """if neighbor_labels[0] in big_labels:
                if neighbor_labels[0] in small_labels:
                    spine_neck_flag = True
            
            if neighbor_labels[0] in small_labels:
                if neighbor_labels[0] in big_labels:
                    spine_neck_flag = True
            
            if spine_neck_flag == True:
                relabel_segments(newList,s_label,spine_neck_label)
            else:
                relabel_segments(newList,s_label,spine_neck_label) #should be qualified as unknown"""
            
            for neighbor in neighbor_labels:
                if neighbor in big_labels:
                    big_flag = big_flag + 1
                if neighbor in small_labels:
                    small_flag = small_flag + 1
            
            #if small_flag + big_flag > 10:
                #relabel_segments(newList,s_label,dendrite_label)
            if small_flag >=1 and big_flag >= 1:
                relabel_segments(newList,s_label,spine_neck_label)
            else:
                relabel_segments(newList,s_label,spine_label)
                
            
        else:
            print("less than 1 neighbors!")
            relabel_segments(newList,s_label,unknown)
        
    spine_label_new = 4 
    dendrite_label_new = 1 
    spine_head_label_new = 2 
    spine_neck_label_new = 3 
    unknown_new = 0  
    
    print("before the replacement")
    print(Counter(newList))
    
    relabel_segments(newList,spine_neck_label,spine_neck_label_new)
    relabel_segments(newList,dendrite_label,dendrite_label_new)
    relabel_segments(newList,spine_head_label,spine_head_label_new)
    relabel_segments(newList,spine_label,spine_label_new)
    relabel_segments(newList,unknown,unknown_new)
    
    
    print("results of new list")        
    print(Counter(newList))
    #print(newList)
    return newList
            


def set_View():
    print("setting view back to original")
    
    
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
            bpy.ops.view3d.viewnumpad(override,type='FRONT')
            #3) Top Ortho
            bpy.ops.view3d.view_persportho(override)
            
            #putting at end just to make sure it works
            bpy.ops.view3d.view_all(override, center=False)
            
            check_Verts_Match()


def rewrite_label(i,x,number_to_replace,verts_to_Face,faces_raw,verts_raw,big_labels,total_labels):
    #won't reassign the same big label to all of those with the same little label
    assign_All_Same = True
    
    
    
    print("On index " + str(i))
    print("x[i] aka label processing = " + str(x[i]))
    #print(len(x))
    #print(x)
    
    remaining_Faces = []
    
    """for i,j in enumerate(x):
        if j == x[i]:
            print(str(i) + ":" + str(j))
            #print(j)
            remaining_Faces.append(i)"""
            
    remaining_Faces = [z for z,j in enumerate(x) if j == x[i]]
    
    
    #print("remaining_Faces len = " + str(len(remaining_Faces)))
    #print("number to replace = " + str(number_to_replace))
    
    if number_to_replace != len(remaining_Faces):
        if x[i] == total_labels:
            return x
            
        raise ValueError("ERROR: faces to replace don't match the number of indexes found for that face")
        return []
    
    #0) Initialize replacement label
    #1) Find the face to relabel
    #2) ADD THIS FACE TO THE CHECKED FACES
    #2) FIND THE VERTICES ASSOCIATED WITH THIS FACE AND ADD TO VERTS TO CHECK
    #2) START another while loop that only breaks when there has been a replacement label found
    #4) For each vertices IN VERTS TO CHECK, find the faces associated with each, and add it to the FACES TO CHECK (IF IT HAS NOT ALREADY BEEN CHECKED)
        #add the vertices to checked verts so we don't end up redoing them
    #5) FOR each of the faces to check, find its label, and see if the label is in the big list
    #6)     If is in big list --> save the replacement label and break from loop
    #7)     If not --> add vertices associated with the face(that have not already been checked) to the verts to check list
    #OUTSIDE OF #2 WHILE LOOP
    #8) if the assign_All_Same flag
    #           is set to true --> assign the label to all of the faces with the same label to be replaced and pop all of them
    #           is false --> only assign the new label to the one being checked
    
    
    
    
    while remaining_Faces:
        counter = 0
        replacement_label = -1
        face_to_relabel = remaining_Faces[0]
        
        #print("face_to_relabel = " + str(face_to_relabel))
        
        checked_Faces = []
        checked_Verts = []
        verts_to_check = []
        faces_to_check = []
        
        checked_Faces.append(face_to_relabel)
        
        #get the vertices of the face
        face_vertices = faces_raw[face_to_relabel].vertices
        for vertex in face_vertices:
            verts_to_check.append(vertex)
        
        #loop that goes until replacement label is found
        while replacement_label <= -1:
            #this will stop the program from entering an endless cycle
            if verts_to_check == []:
                 print("no more verts to check, assigning face " + str(face_to_relabel) + " label " + str(total_labels))
                 replacement_label = total_labels
                 break
                
            counter = counter + 1
            #if counter > 1000:
                #print("didn't find big face yet, going through pass: " + str(counter))
            #iterates through each vertex to get all of the faces to check
            for vertices_checking in verts_to_check:
                #gets all of the faces associated with the vertex
                faces_with_vertex = verts_to_Face[vertices_checking]
                
                #puts all the faces to check into a list
                for fc in faces_with_vertex:
                    if (fc not in faces_to_check) and (fc not in checked_Faces):
                        faces_to_check.append(fc)
                if(vertices_checking not in checked_Verts):
                    checked_Verts.append(vertices_checking)
            
            verts_to_check = []
            
            
            #print("faces_to_check = " + str(faces_to_check))
            #iterate through all faces to find until a label from the big list is found
            for face in faces_to_check:
                if x[face] in big_labels:
                    replacement_label = x[face]
                    #print("found replacement label = " + str(replacement_label))
                    break
                else:
                    checked_Faces.append(face)
                    #add their vertices to the needs to be checked list if they haven't already been added
                    for vertex in faces_raw[face].vertices:
                        if (vertex not in checked_Verts) and (vertex not in verts_to_check):
                            verts_to_check.append(vertex)
            
            
                    
            
            faces_to_check = []
            #print("verts_to_check = " + str(verts_to_check))
            
        
        counter = 0
        #replace that faces label with the new label
        x[face_to_relabel] = replacement_label
        remaining_Faces.pop(0)
        
        if assign_All_Same != False:
            #print("assigning all the same")
            for faces in remaining_Faces:
                x[faces] = replacement_label   
        
            remaining_Faces = []
        
    return x

def merge_labels(x,threshold=50,number_Flag = False, seg_numbers=1,smooth_Flag=True):
    
    print("inside merge_labels")
    
    #have to go into object mode to do some editing
    currentMode = bpy.context.object.mode

    bpy.ops.object.mode_set(mode='OBJECT')
    ob = bpy.context.object
    ob.update_from_editmode()
    
    #print("object_name = " + bpy.context.object.name)
    me = ob.data
    faces_raw = me.polygons
    verts_raw = me.vertices
    
    #create a list of all the labels and which ones are the biggest ones
    from collections import Counter
    
    myCounter = Counter(x)

    big_labels = []
    for label,times in myCounter.items():
        if(times >= threshold):
            #print(str(label) + ":" + str(times))
            big_labels.append([label,times])

    big_labels.sort(key=lambda tup: tup[1], reverse=True)
    #print("BIG LABELS = " + str(big_labels))
    
    #reduce the number of items in the list if the number_Flag is set
    if(number_Flag == True):
        big_labels = big_labels[:seg_numbers]
        
    
    #need to assemble a dictionary that relates vertices to faces
    #*****making into a list if the speed is too slow*******#
    
    verts_to_Face = {}
    
    #initialize the lookup dictionary as empty lists
    for pre_vertex in verts_raw:
        verts_to_Face[pre_vertex.index] = []
        
    #print(len(verts_raw))
    #print(len(verts_to_Face))
    #print(verts_to_Face[1])
    
    for face in faces_raw:
        #get the vertices
        verts = face.vertices
        #add the index to the list for each of the vertices
        for vertex in verts:
            verts_to_Face[vertex].append(face.index)
            
    #print(verts_to_Face[1])
    
    big_labels_indexes = [x for x,i in big_labels]
    #print("big_labels_indexes="+str(big_labels_indexes))
    
    total_labels = len(myCounter.items())
    print(myCounter.items())
    
    print("len of big labels = " + str(len(big_labels_indexes)))
    #now need to change the labels
    print("len of faces_raw = " + str(len(faces_raw)))
    print("len of x = " + str(len(x)))
    if smooth_Flag == True:
        for i in range(0,len(faces_raw)):                                      ##########where we smooth out the labels##########
            if x[i] not in big_labels_indexes and x[i] != total_labels:
                number_to_replace = myCounter[x[i]]
                x = rewrite_label(i,x,number_to_replace,verts_to_Face,faces_raw,verts_raw,big_labels_indexes,total_labels)
        
    return x,total_labels
           




def get_random_color():
    ''' generate rgb using a list comprehension '''
    r, g, b = [round(random.random(),3) for i in range(3)]
    return (r, g, b)

def import_object(filename,ID,seg,clusters,smoothness):
    
    file_path = '/Users/brendancelii/Google Drive/Xaq Lab/Datajoint Project/Final_Script_Youtube/Final_Blender_Neuron_Label_with_bounding_and_check_test/'
    file = filename
    print("inside import object = " + str(file_path + file))
    imported_object = bpy.ops.import_scene.obj(filepath=str(file_path + file))
    obj_object = bpy.context.selected_objects[0] ####<--Fix
    print('Imported name: ', obj_object.name)

    newname = ""
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH' and obj.name.lower().startswith('neuron-' + str(ID) + '.'):
            obj.name = 'neuron-' + str(ID) + "-seg-" + str(seg) + "-"+str(clusters) + "-" + str(smoothness)
            newname = obj.name 
    
    return newname

def create_spine_colors(ob):
    color_keys = bpy.data.materials.keys()
    #delete all colors that are not part of the basic colors:
    accepted_colors = getColors()
    
    for i in range(0,len(bpy.data.materials.keys())):
        if(color_keys[i] not in accepted_colors):
            print("deleting material " + color_keys[i])
            bpy.data.materials.remove(bpy.data.materials[color_keys[i]])
        
        
    create_global_colors()
    
    ob.data.materials[0]           
    
    colors_to_add = ["Error (brown)",
    "Dendrite (purple)",
    "Spine Head (rose)",
    "Spine Neck (light green)",
    "Spine (light pink)"]
    
    
    ob.data.materials[0] = bpy.data.materials[colors_to_add[0]]
    
    for i in range(1,len(colors_to_add)):
        ob.data.materials.append(None)
    
    
    
    for i in range(0,len(colors_to_add)):
        ob.data.materials[i] = bpy.data.materials[colors_to_add[i]]


def segment_random_colors(ob,unique_segments,extraFlag):
    errorFlag = 0
    color_keys = bpy.data.materials.keys()
    '''for i in range(0,len(bpy.data.materials.keys())-16):
        print("deleting material " + color_keys[i])
        bpy.data.materials.remove(bpy.data.materials[color_keys[i]])'''
    
    #makes sure that nothing but the accepted colors are there    
    accepted_colors = getColors()
    for i in range(0,len(bpy.data.materials.keys())):
        if(color_keys[i] not in accepted_colors):
            print("deleting material " + color_keys[i])
            bpy.data.materials.remove(bpy.data.materials[color_keys[i]])
        
    
    
    if errorFlag == 1:
        for i in range(0,len(unique_segments)-1):
            #add the new color
            mat = bpy.data.materials.new(name=str(i));
            mat.diffuse_color = get_random_color()
            #assign it to the object
            ob.data.materials.append(mat)
    
        #add one more label so that the unlabelables get a label
        mat = bpy.data.materials.new("errors")
        mat.diffuse_color = get_random_color()
        ob.data.materials.append(mat)
    else:
        mat = bpy.data.materials.new(name=str("base"))
        mat.diffuse_color = [0.800,0.800,0.800]
        if(len(ob.data.materials.keys()) > 0):
            ob.data.materials[0] = mat
        else:
            ob.data.materials.append(mat)
            
        for i in range(1,len(unique_segments)):
            #add the new color
            mat = bpy.data.materials.new(name=str(i));
            mat.diffuse_color = get_random_color()
            #assign it to the object
            ob.data.materials.append(mat)
        if extraFlag == True:
            mat = bpy.data.materials.new(name=str(len(unique_segments)+1));
            mat.diffuse_color = get_random_color()
            #assign it to the object
            ob.data.materials.append(mat)


def import_segment_labels(obj_file,filename,segment,ID,clusters,smoothness,reseg_threshold=10000,number_Flag = False, seg_numbers=1,smooth_Flag=True,spine_threshold=400,classify_Spine_Flage=True):
    
    ID = str(ID)
    #import the csv file into a list
    location = "/Users/brendancelii/Documents/C++_code/cgal_testing/cgal_testing/"
    

    #"-segmentation_3_0.1.csv" how it looks
    
    with open(location + filename, 'r') as f:
      reader = csv.reader(f)
      your_list = list(reader)
    triangles_labels = []
    for item in your_list:
        triangles_labels.append(int(item[0]))
    
    
    #triangles_labels = (triangles_labels,threshold=2,number_Flag = False, seg_numbers=5) #OLD WAY
    
    print("inside load Neuron")
    #create an object to the labels and the mesh_Table
    #already exist in labels_Table and mesh_Table
    
    """
    primary_key = dict(segmentation=1,decimation_ratio=0.35)
    neuron_data = ((ta3.Decimation & primary_key & "segment_ID="+ID).fetch(as_dict=True))[0]


    
    verts = neuron_data['vertices'].astype(dtype=np.int32).tolist()
    faces = neuron_data['triangles'].astype(dtype=np.uint32).tolist()
    
    #-----------------END OF new way of importing using james cotton way------------------#
    
    '''# deselect all
    bpy.ops.object.select_all(action='DESELECT')
    # selection
    bpy.data.objects['neuron-421208'].select = True
    # remove it
    bpy.ops.object.delete()'''
    
    mymesh = bpy.data.meshes.new("neuron-"+ID)
    mymesh.from_pydata(verts, [], faces)
    
    
    mymesh.update(calc_edges=True)
    mymesh.calc_normals()


    object = bpy.data.objects.new("neuron-"+ID, mymesh)
    #object.location = bpy.context.scene.cursor_location
    object.location = Vector((0,0,0))
    bpy.context.scene.objects.link(object)
    """
    

    filename = 'neuron-' + str(ID) + '-seg-' + str(segment) + '.obj'
    newname = import_object(filename,ID,seg,clusters,smoothness)
    object = bpy.data.objects[newname]
    
    
    
    
    ### get a reference to the object and call it object
    
    object.lock_location[0] = True
    object.lock_location[1] = True
    object.lock_location[2] = True
    object.lock_scale[0] = True
    object.lock_scale[1] = True
    object.lock_scale[2] = True

    #rotate the z direction by 90 degrees so point correct way
    
    #object.rotation_euler[2] = 1.5708

    
    object.rotation_euler[0] = 1.5708
    object.rotation_euler[1] = 0
    object.rotation_euler[2] = 0



    
    object.lock_rotation[0] = True
    object.lock_rotation[1] = True
    object.lock_rotation[2] = True


    #set view back to normal:
    set_View()
    
    object.select = True

    ###11_08:  
    ######bpy.context.scene.objects.active = bpy.context.scene.objects["neuron-"+ID]
    
    print("inside segmentation, about to assign labels")
    #smooth out the triangle labels:
    triangles_labels,total_labels = merge_labels(triangles_labels,threshold=reseg_threshold,number_Flag = number_Flag, seg_numbers=seg_numbers,smooth_Flag=smooth_Flag)
    if classify_Spine_Flage == True:
        triangles_labels = classify_spines(triangles_labels,threshold=spine_threshold)
    
    print('triangles_labels = ' + str(len(triangles_labels)))
    
    print(Counter(triangles_labels))
    
    #need to add the labels to the newly created object
    ob = object
    
    
    me = ob.data
    
    #print("starting to hide everything")
    #iterate through all of the vertices
    verts_raw = ob.data.vertices
    #print(len(active_verts_raw))
    
    edges_raw = ob.data.edges
    
    #print(len(active_edges_raw))
    
    faces_raw = ob.data.polygons
    
  
            
    print("inside mesh")
    print(Counter(triangles_labels))
    print('verts_raw = ' + str(len(verts_raw)))
    print('faces_raw = ' + str(len(faces_raw)))
    
    
    #print number of unique labels
    unique_segments = list(Counter(triangles_labels).keys())
    
    #remove the errors from the list so won't get factored in
    print("total_labels = " + str(total_labels))
    if total_labels in unique_segments: 
        unique_segments.remove(total_labels)
        unique_segments.append(total_labels)
        errorFlag = 1
    
    segmentation_length = len(unique_segments) # equals to list(set(words))
    print(segmentation_length)

    unique_index_dict = {unique_segments[x]:x for x in range(0,segmentation_length)}
    
    
    print("unique_index_dict = " + str(len(unique_index_dict)))
    print("triangle_labels = " + str(len(triangles_labels)))
    
    #adds all of the labels to the faces
    for i,k in enumerate(faces_raw):
        #k.material_index = int(unique_index_dict[triangles_labels[i]])
        k.material_index = int(triangles_labels[i])
        
      
    

    #go into edit mode
    print("trying to select the neuron")
    
    bpy.context.scene.objects.active = object
    #bpy.ops.object.mode_set(mode='EDIT')
    #bpy.ops.mesh.select_all(action='TOGGLE')
    #edit_active_neuron()
    
    '''is_label_hidden = get_Hide_Flag()
    
    #make sure the faces are hidden if they should be
    if (is_label_hidden == True):
        hide_Labeled(mode=0,waitTime=0)
    else:  #show all of the faces
        #print ("Property Disabled")
        hide_Labeled(mode=1,waitTime=0)'''

    

    
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
    
    
    
    #####Assigning Random Color
    if(classify_Spine_Flage == True):
        create_spine_colors(ob)
    else:
        segment_random_colors(ob,unique_segments)
    
    #not assigning random color
    #spine_label_new = 4 
    #dendrite_label_new = 1 
    #spine_head_label_new = 2 
    #spine_neck_label_new = 3 
    #unknown_new = 0  
    
    ####Way to assign the specific color#####
    
    
    
    
    #add the materials to the local current object
    
    #makes sure that length of color list matches the number of labels/colrs needed + 1
    """if(ob.data != None):
        difference = len(unique_segments) - len(ob.data.materials) 
    else:
        print("materials was none")
    
    previous_ob_mat_length = len(ob.data.materials)
    
    add the number of colors missing
    if(difference > 0):
        for i in range(0,difference):
            ob.data.materials.append(None)"""
            
    #print(len(ob.data.materials))
    
    #make sure the colors are in the correct order for the object
    
    return filename, segmentation_length, Counter, newname




#####Things that need to be changed
#1) don't import the neuron from the database but load it locally and all parameters for segmentation
#2) Things need to specify: the segmentation file, the obj file

from auto_spine_labeler_vp4 import automatic_spine_classification_vp2,smooth_backbone
import csv
    
if __name__ == "__main__":
    
    '''
    neuron_ID = 421208

    clusters = 10
    smoothness = 0.05
    seg = 6
    seg_file = "neuron_" + str(neuron_ID) + "-" +str(seg) +"-segmentation_" + str(clusters) + "_" + str(smoothness)
    obj_file="neuron-"+str(neuron_ID) + "-seg-"+str(seg)+".obj"
    neuron_file, number_of_segments, Counter,newname = import_segment_labels(obj_file=obj_file,filename=seg_file+".csv",segment=seg,ID=neuron_ID,
            clusters=clusters,smoothness=smoothness,reseg_threshold=5,number_Flag = False, seg_numbers=1,smooth_Flag=False,spine_threshold=400,classify_Spine_Flage=False)
    
    
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
    
    location = "/Users/brendancelii/Google Drive/Xaq Lab/Datajoint Project/Final_Script_Youtube/Final_Blender_Neuron_Label_with_bounding_and_check_test/parameter_results/"
                
    file_name = '11_21_param_test_reviesed.csv'
    
    with open(location + file_name, 'a+') as csvfile:
                    spamwriter = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
                    spamwriter.writerow([neuron_ID,seg,clusters,smoothness,head_counter,neck_counter, spine_counter, stub_counter,shared_vert_threshold,max_backbone_threshold,backbone_threshold,secondary_threshold])
                

    #parameter testing to find optimal segmentation, clustering, and shared vert
    '''
    
    
    
    
    smoothing_array =["0.04", "0.05", "0.06", "0.07", "0.08", "0.09","0.10","0.11","0.12","0.13","0.14","0.15","0.20","0.30","0.40"]
    clusters_array= [ "5","6","7","8","9","10" ]
    shared_vert_threshold_array = [18,21,25]
    
    neuron_ID = 421208
    seg = 6
    
    for shared_vert in shared_vert_threshold_array:
        for clusters in clusters_array:
            for smoothy in smoothing_array:
                smoothness = str(smoothy) + "0000"
                seg_file = "neuron_" + str(neuron_ID) + "-" +str(seg) +"-segmentation_" + str(clusters) + "_" + str(smoothness)
                obj_file="neuron-"+str(neuron_ID) + "-seg-"+str(seg)+".obj"
                loc  = "neuron_seg_testing/"
                neuron_file, number_of_segments, Counter, newname= import_segment_labels(obj_file=obj_file,filename=loc + seg_file+".csv",segment=seg,ID=neuron_ID,
                clusters=clusters,smoothness=smoothness,reseg_threshold=5,number_Flag = False, seg_numbers=1,smooth_Flag=False,spine_threshold=400,classify_Spine_Flage=False)

                #make sure and select the neuron so active
                
                bpy.context.scene.objects.active = bpy.data.objects[newname]
                
                #call the smoothing backbone function and then automatic spine labeler
                max_backbone_threshold = 600
                backbone_threshold=200
                secondary_threshold=20
                shared_vert_threshold=shared_vert
                smooth_backbone(max_backbone_threshold = max_backbone_threshold,backbone_threshold=backbone_threshold
                            ,secondary_threshold=secondary_threshold,shared_vert_threshold=shared_vert_threshold,number_Flag = False, seg_numbers=1,smooth_Flag=True)
        
                head_counter,neck_counter, spine_counter, stub_counter = automatic_spine_classification_vp2()
                
                #print out the results to a file
                
                location = "/Users/brendancelii/Google Drive/Xaq Lab/Datajoint Project/Final_Script_Youtube/Final_Blender_Neuron_Label_with_bounding_and_check_test/parameter_results/"
                
                file_name = '11_21_param_test_reviesed.csv'
                 
                
                
                
                with open(location + file_name, 'a+') as csvfile:
                    spamwriter = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
                    spamwriter.writerow([neuron_ID,seg,clusters,smoothness,head_counter,neck_counter, spine_counter, stub_counter,shared_vert_threshold,max_backbone_threshold,backbone_threshold,secondary_threshold])
                
                #delete the object
                
                # deselect all
                bpy.ops.object.select_all(action='DESELECT')

                # selection
                bpy.data.objects[newname].select = True
                
                neuron_filename = str(neuron_ID) + "_" + str(seg) + "_"  + str(clusters) + "_" + str(smoothy) + "_" + str(shared_vert) + ".obj"
                target_file_2 = "/Users/brendancelii/Google Drive/Xaq Lab/Datajoint Project/Final_Script_Youtube/Final_Blender_Neuron_Label_with_bounding_and_check_test/automatically_labeled_neurons/" + neuron_filename

                bpy.ops.export_scene.obj(filepath=target_file_2)

                # remove it
                bpy.ops.object.delete()
                


