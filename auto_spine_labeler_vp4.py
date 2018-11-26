import bpy
from collections import Counter
import numpy as np
#labels_list = all of the labels in the mesh in order
#current_label = trying to find the neighbors for this label
#verts_to_Face = lookup dictionary for verts to faces
#faces_raw, verts_raw: face and vertices objects of the mesh


######*******CHANGE TO USE SETS INSTEAD OF LISTS**********#############
def find_neighbors(labels_list,current_label,verts_to_Face,faces_raw,verts_raw):
    """will return the number of neighbors that border the segment"""
    
    #iterate over each face with that label
    #   get the vertices of that face
    #   get all the faces that have that vertice associated with that
    #   get the labels of all of the neighbor faces, for each of these labels, add it to the neighbors 
    #list if it is not already there and doesn't match the label you are currently checking
    #   return the list 
    
    #get the indexes of all of the faces with that label that you want to find the neighbors for
    index_list = []
    for i,x in enumerate(labels_list):
        if x == current_label:
            index_list.append(i)
    
    verts_checked = []
    faces_checked = []
    neighbors_list = []
    neighbors_shared_vert = {}
    for index in index_list:
        current_face = faces_raw[index]
        
        #get the vertices associates with face
        vertices = current_face.vertices
        
        #get the faces associated with the vertices of that specific face
        for vert in vertices:
            #will only check each vertex once
            if vert not in verts_checked:
                verts_checked.append(vert)
                faces_associated_vert = verts_to_Face[vert]
                for fac in faces_associated_vert:
                    #make sure it is not a fellow face with the label who we are looking for the neighbors of
                    if (fac not in index_list):
                        #check to see if checked the the face already
                        if (fac not in faces_checked):
                            if(labels_list[fac] not in neighbors_list):
                                #add the vertex to the count of shared vertices
                                neighbors_shared_vert[labels_list[fac]] = 0 
                                #only store the faces that are different
                                neighbors_list.append(labels_list[fac])
                                #faces_to_check.append(fac)
                                #faces_to_check.insert(0, fac)
                            #increment the number of times we have seen that label face
                            neighbors_shared_vert[labels_list[fac]] = neighbors_shared_vert[labels_list[fac]] + 1
                            #now add the face to the checked list
                            faces_checked.append(fac)
    
    #have all of the faces to check
    
    """for facey in faces_to_check:
        if labels_list[facey] != current_label and labels_list[facey]  not in neighbors_list:
            neighbors_list.append(labels_list[facey] )"""
    
    number_of_faces = len(index_list)
    return neighbors_list,neighbors_shared_vert,number_of_faces

    
def relabel_segments(labels_list,current_label,new_label):
    for i,x in enumerate(labels_list):
        if x == current_label:
            labels_list[i] = new_label
            
    return labels_list
    

def generate_labels_list(faces_raw):
    labels_list = []
    #print("length of faces_raw = " + str(len(faces_raw)))
    #print("lenth of current materials = " + str(len(bpy.context.object.data.materials.keys())))
    for i in range(0,len(faces_raw)):
        if(faces_raw[i].material_index < len(bpy.context.object.data.materials.keys())):
            labels_list.append(bpy.context.object.data.materials[faces_raw[i].material_index].name)
        else: 
            labels_list.append("backbone")
    
    return labels_list

def generate_verts_to_face_dictionary(faces_raw,verts_raw):
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
            
    return verts_to_Face
    

#using merge labels as a starting point
def smooth_backbone(max_backbone_threshold = 400,backbone_threshold=300,secondary_threshold=100,shared_vert_threshold=30,number_Flag = False, seg_numbers=1,smooth_Flag=True):
    #things that could hint to backbone
    #1) larger size
    #2) touching 2 or more larger size
    #have to go into object mode to do some editing
    currentMode = bpy.context.object.mode

    bpy.ops.object.mode_set(mode='OBJECT')
    ob = bpy.context.object
    ob.update_from_editmode()
    
    #print("object_name = " + bpy.context.object.name)
    me = ob.data
    
    faces_raw = me.polygons
    verts_raw = me.vertices
    
    labels_list = generate_labels_list(faces_raw)
    
        
    #need to assemble a dictionary that relates vertices to faces
    #*****making into a list if the speed is too slow*******#
    
    
    
    
    verts_to_Face = generate_verts_to_face_dictionary(faces_raw,verts_raw)

    
    
    
    
    
    
    #add new color and reassign all of the labels with those colors as the backbone label
    num_colors = len(bpy.context.object.data.materials.keys())
    
    backbone_color = (0.004,0.254,0.800)
    
    #create new color
    if "backbone" not in bpy.data.materials.keys():
        mat = bpy.data.materials.new(name="backbone");
        mat.diffuse_color = backbone_color
        #assign it to the object
        ob.data.materials.append(mat)
    
    ####don't do this so they show up black#####
    #add the new color to the object if not have already
    """if "backbone" not in bpy.context.object.data.materials.keys():
        ob = bpy.context.object
        ob.data.materials.append(None)
        ob.data.materials[num_colors] = bpy.data.materials["backbone"]"""
    
    
    #create a list of all the labels and which ones are the biggest ones
    from collections import Counter
    
    
    myCounter = Counter(labels_list)

    spine_labels = []
    backbone_labels = []
    
    #may not want to relabel until the end in order to preserve the labels in case label a big one wrong
    for label,times in myCounter.items():
        if(times >= backbone_threshold):
            #print(str(label) + ":" + str(times))
            backbone_labels.append(label)   
        else:
            spine_labels.append(label) 

    print(backbone_labels)
    #do a couple pass throughs in order to make sure got it all
    for i in range(0,6):
        
        print("in smoothing round " + str(i))

 
        
        #need to go through and unlabel the vertices that do not have a lot of shared vertices with other big labels
        ############    TO DO #####################
        ####ALSO CHECK SHARED VERT BECAUSE DON'T THINK WORKING#########33
        #print("backbone_labels = " + str(backbone_labels))
        for backbone in backbone_labels:
            if myCounter[backbone] < max_backbone_threshold:#print("working on big label = " + backbone)
            
                current_label = backbone
                neighbors_list,neighbors_shared_vert,number_of_faces = find_neighbors(labels_list,current_label,verts_to_Face,faces_raw,verts_raw)
                
                #if myCounter[backbone] < backbone_threshold:
                    
                
                    
                backbone_count_flag = False
                total_backbone_shared_verts = 0
                
                for neighbor in neighbors_list:
                    if neighbor in backbone_labels:
                        total_backbone_shared_verts = total_backbone_shared_verts + neighbors_shared_vert[neighbor] 
                        
                
                if (total_backbone_shared_verts > shared_vert_threshold):
                    backbone_count_flag = True


                
                
                
                if backbone_count_flag == False:
                    print("new small label found for label = " + backbone)
                    print("total_backbone_shared_verts = "+str(total_backbone_shared_verts))
                    backbone_labels.remove(backbone)
                    spine_labels.append(backbone)
                
        
        for sp_label in spine_labels:
            #print("working on small label =  " + sp_label)
            #if sp_label not in backbone_labels:
            current_label = sp_label
            neighbors_list,neighbors_shared_vert,number_of_faces = find_neighbors(labels_list,current_label,verts_to_Face,faces_raw,verts_raw)
            if(current_label[0:3] == "336"):
                print("info for " + str(current_label))
                print("neighbors_list = " + str(neighbors_list))
                print("neighbors_shared_vert[neighbor] = " + str(neighbors_shared_vert))
                print("backbone_labels = " + str(backbone_labels))
                print("shared_vert_threshold = "+ str(shared_vert_threshold))
            total_backbone_shared_verts = 0
            
            for neighbor in neighbors_list:
                if neighbor in backbone_labels:
                    total_backbone_shared_verts = total_backbone_shared_verts + neighbors_shared_vert[neighbor] 
                    
                    
            #check if it is a false label
            if (total_backbone_shared_verts > shared_vert_threshold): 
                            
                    print("new backbone label found for label = " + sp_label)
                    print("total_backbone_shared_verts = "+str(total_backbone_shared_verts))
                    
                    backbone_labels.append(current_label)
                    spine_labels.remove(current_label)
                     
                            
    #go through and switch the label of hte 
    #may not want to relabel until the end in order to preserve the labels in case label a big one wrong
    for i in range(0,len(labels_list)):
        if labels_list[i] in backbone_labels:
            labels_list[i] = "backbone"
            faces_raw[i].material_index = num_colors
    




def get_neighbor_verts(label_name):
        
    currentMode = bpy.context.object.mode

    bpy.ops.object.mode_set(mode='OBJECT')
    ob = bpy.context.object
    ob.update_from_editmode()
    
    #print("object_name = " + bpy.context.object.name)
    me = ob.data
    
    faces_raw = me.polygons
    verts_raw = me.vertices
    
    labels_list = generate_labels_list(faces_raw)
    
        
    #need to assemble a dictionary that relates vertices to faces
    #*****making into a list if the speed is too slow*******#
    
    
    verts_to_Face = generate_verts_to_face_dictionary(faces_raw,verts_raw)
    
    neighbors_list,neighbors_shared_vert,number_of_faces = find_neighbors(labels_list,label_name,verts_to_Face,faces_raw,verts_raw)
    
    return neighbors_list,neighbors_shared_vert,labels_list





"""  Example of what I want outputed into npz file

connections = {"55":["288","127"],"127":["55"],"288":["345","55","backbone"],
               "345":["288","71","137","backbone"],"71":["345"],
               "137":["345","backbone"]}

#put zero for the backbone connections so doesn't screw up the shared vertices percent calculations
shared_vertices = {"55":[4,4],"127":[4],"288":[4,4,0],
               "345":[6,4,9,0],"71":[4],
               "137":[14,0]}

mesh_number = {"55":80,"127":34,"288":16,"345":7,"71":28,"137":28,"backbone":0}

"""





#generates the stats: connections on who it is connected to), shared_verts (how many vertices it shares between it's neighbor), mesh_number (number of face for that label)
def export_connection(label_name, outputFlag="False",file_name="None"):
    print("hello from export_connection")
    #find all the neighbors of the label
    
    currentMode = bpy.context.object.mode

    bpy.ops.object.mode_set(mode='OBJECT')
    ob = bpy.context.object
    ob.update_from_editmode()
    
    #print("object_name = " + bpy.context.object.name)
    me = ob.data
    
    faces_raw = me.polygons
    verts_raw = me.vertices
    
    labels_list = generate_labels_list(faces_raw)
    
        
    #need to assemble a dictionary that relates vertices to faces
    #*****making into a list if the speed is too slow*******#
    
    verts_to_Face = generate_verts_to_face_dictionary(faces_raw,verts_raw)
    
    
    total_labels_list = []
    faces_checked = []
    faces_to_check = [label_name]
    
    still_checking_faces = True
        
    connections = {}
    shared_vertices = {}
    mesh_number = {}
    
    while still_checking_faces:
        #will exit if no more faces to check
        if not faces_to_check:
            still_checking_faces = False
            break
        
        for facey in faces_to_check:
            if facey != "backbone":
                neighbors_list,neighbors_shared_vert,number_of_faces = find_neighbors(labels_list,facey,verts_to_Face,faces_raw,verts_raw)
                
                
                
                #reduce the shared vertices with a face and the backbone to 0 so doesn't mess up the shared vertices percentage
                pairs = list(neighbors_shared_vert.items())
                pre_connections = [k for k,i in pairs]
                pre_shared_vertices = [i for k,i in pairs]
                
                
                
                
                if ("backbone" in pre_connections):
                    back_index = pre_connections.index("backbone")
                    pre_shared_vertices[back_index] = 0
         
                
                connections[facey] = pre_connections
                shared_vertices[facey] = pre_shared_vertices
                mesh_number[facey] = number_of_faces

                
                for neighbors in neighbors_list:
                    if (neighbors != "backbone") and (neighbors not in faces_to_check) and (neighbors not in faces_checked):
                        faces_to_check.append(neighbors)
                
                faces_to_check.remove(facey)
                faces_checked.append(facey)
        
        #append the backbone to the graph structure
        mesh_number["backbone"] = 0
    
    print("faces_checked = " + str(faces_checked))
    
    #save off the file to an npz file
    
    
    if(outputFlag == True):
        complete_path = str("/Users/brendancelii/Google Drive/Xaq Lab/Datajoint Project/Automatic_Labelers/spine_graphs/"+file_name)
        
        
        
        #package up the data that would go to the database and save it locally name of the file will look something like this "4_bcelii_2018-10-01_12-12-34"
    #    np.savez("/Users/brendancelii/Google Drive/Xaq Lab/Datajoint Project/local_neurons_saved/"+segment_ID+"_"+author+"_"+
    #        date_time[0:9]+"_"+date_time[11:].replace(":","-")+".npz",segment_ID=segment_ID,author=author,
    #					date_time=date_time,vertices=vertices,triangles=triangles,edges=edges,status=status)
        np.savez(complete_path,connections=connections,shared_vertices=shared_vertices,mesh_number=mesh_number ) 
    
    return connections,shared_vertices,mesh_number
   
    
        
        

####For automatic spine labeling
def find_endpoints(G,mesh_number):
    #will first calculate all the shortest paths for each of the nodes
    
    node_list = list(G.nodes)
    node_list.remove("backbone")
    
    shortest_paths = {}
    for node in node_list:
        shortest_paths[node] = [k for k in nx.all_shortest_paths(G,node,"backbone")]
    
    endpoints = []
    #identify the nodes that are not a subset of other nodes
    for node in node_list:
        other_nodes = [k for k in node_list if k != node ]
        not_unique = 0
        for path in shortest_paths[node]:
            not_unique_Flag = False
            for o_node in other_nodes:
                for o_shortest_path in shortest_paths[o_node]:
                    if set(path) <= set(o_shortest_path):
                        not_unique_Flag = True
                        
            if not_unique_Flag == True:
                not_unique = not_unique + 1
                
        #decide if unique endpoint
        if not_unique < len(shortest_paths[node]):   # this means there is a unique path
            
            if not_unique != 0:
                print(node + "-some unique and some non-unique paths for endpoint")
            endpoints.append(node)
        
    #print(endpoints)  
    longest_paths_list = []
    for end_node in endpoints:
        longest_path = 0
        for path in shortest_paths[end_node]:
            path_length = 0
            for point in path:
                path_length = path_length + mesh_number[point]
            if path_length > longest_path:
                longest_path = path_length
        
        longest_paths_list.append((end_node,longest_path))
        
    #print(longest_paths_list)
    longest_paths_list.sort(key=lambda pair: pair[1], reverse=True)
    #print(longest_paths_list)
    ranked_endpoints = [x for x,i in longest_paths_list]
    endpoint_paths_lengths = [i for x,i in longest_paths_list]
    
    enpoint_path_list = {}
    for endpt in ranked_endpoints:
        enpoint_path_list[endpt] = shortest_paths[endpt]
        
    
    #ranked_endpoints, longest_paths_list = (list(t) for t in zip(*sorted(zip(endpoints, longest_paths_list))))
    
    
    return ranked_endpoints, enpoint_path_list 
            
                        


#strategy: 
'''
1) starts with current head
2) finds all the neighbors and for each neighbor
     a. finds the vertices it shares with the head
     b. if the ratio of shared vertices to mesh is high enough then they are split heads
     c. add both meshes to the split heads list (if not already added)
     d. add any of the meshes added to split heads to be checked if not already checked
3) repeat until no more heads to check
'''

def get_split_heads(label_name, path,split_head_threshold,connections,shared_vertices,mesh_number):
    final_split_heads = []
    head_to_check = [label_name]
    heads_checked = []
    
    
    #have a baseline threshold for split faces 
    
    
    while head_to_check:
        for possible_head in head_to_check:
            print("possible_head = " + str(possible_head))
            heads_checked.append(possible_head)
            neighbors = connections[possible_head]
            for i in range(0,len(neighbors)):
                if(neighbors[i] not in heads_checked):
                    verts_sharing = shared_vertices[possible_head][i]
                    if verts_sharing/mesh_number[possible_head] > split_head_threshold:
                        if possible_head not in final_split_heads:
                            final_split_heads.append(possible_head)
                        if neighbors[i] not in final_split_heads:
                            final_split_heads.append(neighbors[i])
                        if (neighbors[i] not in head_to_check) and (neighbors[i] not in heads_checked):
                            head_to_check.append(neighbors[i] )
                print("final_split_heads = " + str(final_split_heads))
            head_to_check.remove(possible_head)
    
    print("final_split_heads = " + str(final_split_heads))
    return final_split_heads

                        
                
                
        
#implement the algorithm that will classify 
#the neurons based on the graph strucutre

####example input for function
'''connections = {"55":["288","127"],"127":["55"],"288":["345","55","backbone"],
               "345":["288","71","137","backbone"],"71":["345"],
               "137":["345","backbone"]}

#put zero for the backbone connections so doesn't screw up the shared vertices percent calculations
shared_vertices = {"55":[4,4],"127":[4],"288":[4,4,0],
               "345":[6,4,9,0],"71":[4],
               "137":[14,0]}

mesh_number = {"55":80,"127":34,"288":16,"345":7,"71":28,"137":28,"backbone":0}'''

def classify_spine(connections,shared_vertices,mesh_number):
    print("inside classify_spine")
    head_threshold = 0.15
    split_head_threshold = 0.40
    underneath_threshold = 0.13
    

    #the only solid number threshold
    stub_threshold = 40
    path_threshold = 20

    #make a new dictionary to hold the final labels of the spine
    end_labels = {k:"none" for k in mesh_number.keys()}


    #only one segment so label it as a spine
    if len(connections.keys()) <= 1:
        end_labels[list(connections.keys())[0]] = "spine_one_seg"


    total_mesh_faces = sum([k for i,k in mesh_number.items()])
    print("total_mesh_faces = " + str( total_mesh_faces))

    #create the graph from these
    G=nx.Graph(connections)

    endpoint_labels,shortest_paths = find_endpoints(G,mesh_number)

    print("endpoint_labels = "+str(endpoint_labels))
    print("shortest_paths = "+str(shortest_paths))



    #plt.subplot()
    #nx.draw(G,with_labels=True,font_weight='bold')

    #labels to use for testing
    no_significance = 0   #when the label is not above threshold but has yet to be found a correct label yet
    head_hat = 1   #the little bumps onto of the head
    head_reg = 2   #normal head label
    head_split = 3 #when the segmentation splits the heads into big parts
    neck_under_head = 4 #when the segmentation algorithm has found the head 
                        #and then just makes everything under it in path a neck
    neck_no_head = 5  #when there is not enough base or segments underneath the segment to make
                    #it qualifiable as a head, so instead label it as a neck
    neck_no_head_on_path  = 6
    neck_no_significant_base = 7
    neck_no_sign_already_label = 8 #when the neck part is not significant and then runs 
                                    #into a label already labeled neck from previous one --> so just label neck as well
    neck_reg = 9  # regular neck label


    spine_one_seg = 10 #when there is only one segment in the whole structure
    spine_head_disagree = 11 #when there is a disagreement on whether a label should be a head or not
                        #the items labeled head will be changed to just a spine
    #spine_no_head = #don't think need this

    spine_no_head_at_all = 12


    stub_head = 13 #on second pass, the top part and the whole structure doesn't qualify 
                    #as above the whole_spine significance threshold, label as stub
    stub_neck = 14 #on second pass, the bottom part and the whole structure doesn't qualify              #as above the whole_spine significance threshold, label as stub
    unsure = 15

    #make a new dictionary to hold the final labels of the spine
    end_labels = {k:"none" for k in mesh_number.keys()}
    end_labels["backbone"] = "backbone"

    print("end_labels at beginning")
    print(end_labels)



    for endpoint in endpoint_labels:
        print("at beginning of endpoint loop with label = "+ str(endpoint))
        #get the shortest path lists
        endpoint_short_paths = shortest_paths[endpoint]
        for path in endpoint_short_paths:
            path.remove("backbone")
            path_total_mesh_faces = sum([k for i,k in mesh_number.items() if i in path])
            print("path_total_mesh_faces = "+str(path_total_mesh_faces))
            print("at beginning of path loop with path = "+ str(path))
            travel_index = 0
            head_found = False
            label_everything_above_as_head = False
            while (head_found == False ) and travel_index < len(path):
                current_face = path[travel_index]
                if  mesh_number[current_face]/float(path_total_mesh_faces) < head_threshold:
                    #then not of any significance BUT ONLY REASSIGN IF NOT HAVE ASSIGNMENT***
                    if end_labels[current_face] == "none":
                        end_labels[current_face] = "no_significance"
                    travel_index = travel_index + 1
                else:
                    #end_labels[current_face] = "head_reg" WAIT TO ASSIGN TILL LATER
                    if "neck" != end_labels[current_face][0:4]:   #if not already labeled as spine
                        head_found = True
                        label_everything_above_as_head = True
                    else:
                        travel_index = travel_index + 1


            print("end of first while loop, travel_index = "+ str(travel_index) + " head_found = "+ str(head_found))
            ############Added new threshold that makes it so path length can't be really small
            if path_total_mesh_faces<path_threshold:
                head_found = False
            
            if travel_index < len(path):
                travel_face = path[travel_index]
            else:
                travel_face = path[travel_index-1]
                travel_index = travel_index-1
            #if there does not exist a head, then replace all unlabeled faces as neck:
            
            
                
            

            #check to see if sharing the alot of faces with one of it's neighbor
            """split_head = []




            verts_array = shared_vertices(connections[path[travel_index]])
            for i in range(0,len(connections[path[travel_index]])):
                split_head_names = get_split_heads(verts_array[i])
                if verts_array[i]>split_head_threshold:"""

            #see if there are any labels that border it that also share a high percentage of faces
            if head_found == True:
                ##will return the names of the faces that have unusually high verts sharing
                split_head_labels = get_split_heads(path[travel_index],path,split_head_threshold,connections,shared_vertices,mesh_number)
                print("split_head_labels = " + str(split_head_labels))


                if split_head_labels:
                    print("adding the split head labels")
                    for split_label in split_head_labels:
                        #######may need to add in CHECK FOR ALREADY LABELED
                        if "head" == end_labels[split_label][0:4] or end_labels[split_label] == "none":
                            end_labels[split_label] = "head_split"
                        else:
                            end_labels[split_label] = "spine_head_disagree"

                    if "head" == end_labels[travel_face][0:4] or end_labels[travel_face] == "none":
                        end_labels[travel_face] = "head_split"
                    else:
                        end_labels[travel_face] = "spine_head_disagree"

                    label_everything_above_as_head = True
            
            
            if head_found == True:
                #check to see if there is enough faces below it to really qualify as head
                number_mesh_under_head = sum([mesh_number[path[i]] for i in range(travel_index+1,len(path)) if end_labels[path[i]][0:4] != "head"])
                print("number_mesh_under_head = " + str(number_mesh_under_head))

                if number_mesh_under_head/float(path_total_mesh_faces) < underneath_threshold: 
                    ######Will overwrite everything underneath
                    print("not enough base under head so labeling as neck")
                    #label all of the meshes above
                    "neck_no_significant_base"
                    for i in range(0,len(path)):
                        if end_labels[path[i]] == "none" or end_labels[path[i]] == "no_significance":
                            end_labels[path[i]] = "neck_no_significant_base"
                    
                    #label all of the split heads as well as neck
                    for sh in split_head_labels:
                        end_labels[sh] = "neck_no_significant_base"

                    label_everything_above_as_head = False
                    head_found = False
            
            if head_found == False:
                print("no head found so labeling as neck")
                #######WILL NOT OVERWRITE UNLESS LABELED AS NO SIGNIFICANCE
                for i in path: 

                    if end_labels[i] == "no_significance" or end_labels[i] == "none":
                        end_labels[i] = "neck_no_head_on_path"

                label_everything_above_as_head = False



            print("label_everything_above_as_head = " + str(label_everything_above_as_head))
            #need to label any of those above it in the chain labeled as insignificant to heads
            if label_everything_above_as_head == True:
                if end_labels[travel_face] == "none":
                    print("labeled as head reg")
                    end_labels[travel_face] = "head_reg"
                #else:               ########don't need this because don't want to overwrite already written spine neck
                    #if "head" not in end_labels[travel_index]:
                        #end_labels[travel_index] = "spine_head_disagree"


                #will label everything above it as a head and then everything below it as neck
                #####need to account for special case where not overwrite the head_split####
                if "head" == end_labels[travel_face][0:4]:
                    print('labeling all no_significance above as head hats')
                    for i in range(0,travel_index):
                        current_label = path[i]
                        if end_labels[current_label] == "no_significance":
                            end_labels[current_label] = "head_hat"
                        else:
                            if "head" != end_labels[current_label][0:4]:
                                end_labels[current_label] = "spine_head_disagree"
                    print('labeling all below head as necks')
                    for i in range(travel_index+1,len(path)):
                        current_label = path[i]
                        if current_label not in split_head_labels:
                            end_labels[current_label] = "neck_under_head"
                else:
                    print("head not present so labeling everything above as neck_hat")
                    for i in range(0,travel_index):
                        current_label = path[i]
                        #####need to account for special case where not overwrite the head_split####
                        if end_labels[current_label] == "no_significance":
                            end_labels[current_label] == "neck_hats"

            print("at end of one cycle of big loop")
            print("end_labels = " + str(end_labels))

            #what about a head being accidentally written under another head? 
            #####you should not write a head to a spine that has already been labeled as under a head
            #####you should overwrite all labels under a head as spine_under_head

    print("outside of big loop")
    print("end_labels = " + str(end_labels))

    #if no heads present at all label as spines
    spine_flag_no_head = False

    for face,label in end_labels.items():
        if "head" == label[0:4]:
            spine_flag_no_head = True

    if spine_flag_no_head == False:
        print("no face detected in all of spine")
        for label_name in end_labels.keys():
            end_labels[label_name] = "spine_no_head_at_all"


    #once done all of the paths go through and label things as stubs
    if total_mesh_faces < stub_threshold:
        print("stub threshold triggered")
        for label_name in end_labels.keys():
            if "head" == end_labels[label_name][0:4]:
                end_labels[label_name] = "stub_head"

            elif "neck" == end_labels[label_name][0:4]:
                end_labels[label_name] = "stub_neck"
            else:
                end_labels[label_name] = "stub_spine"
            
    
    
    end_labels["backbone"] = "backbone"

    ###To Do: replace where look only in 1st four indexes
    return end_labels


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
    "Spine (light pink)",
    "Bouton (aqua)"]
    
    
    ob.data.materials[0] = bpy.data.materials[colors_to_add[0]]
    
    for i in range(1,len(colors_to_add)):
        ob.data.materials.append(None)
    
    
    
    for i in range(0,len(colors_to_add)):
        ob.data.materials[i] = bpy.data.materials[colors_to_add[i]]






import sys
import numpy as np
#import matplotlib.pyplot as plt
import networkx as nx




################### Actual Spine Classification #######################
         
def automatic_spine_classification_vp2():
    
    #process of labeling
    """1) Get a list of all of the labels
    2) Iterate through the labels and for each:
        a. Get the connections, verts_shared and mesh_sizes for all labels connected to said label 
        b. Run the automatic spine classification to get the categories for each label
        c. Create a new list that stores the categories for each label processed
        d. repeat until all labels have been processed
    3) Delete all the old colors and then setup the global colors with the regular labels
    4) Change the material index for all labels based on the categorical classification"""
    
    currentMode = bpy.context.object.mode

    bpy.ops.object.mode_set(mode='OBJECT')
    ob = bpy.context.object
    ob.update_from_editmode()
    
    #print("object_name = " + bpy.context.object.name)
    me = ob.data
    
    faces_raw = me.polygons
    verts_raw = me.vertices
    
    labels_list = generate_labels_list(faces_raw)
    
    final_spine_labels = labels_list.copy()
    
    processed_labels = []
    
    myCounter = Counter(labels_list)
    complete_labels =  [label for label,times in myCounter.items()]
    
    head_counter = 0
    spine_counter = 0
    neck_counter = 0
    stub_counter = 0
    for i in range(0,len(complete_labels)):
        if complete_labels[i] != "backbone" and complete_labels[i] not in processed_labels:
            #get the conenections, shared vertices and mesh sizes for the whole spine segment in which label is connected to
            connections,shared_vertices,mesh_number = export_connection(complete_labels[i], outputFlag="False",file_name="None")
            
            #send that graph data to the spine classifier to get labels for that
            final_labels = classify_spine(connections,shared_vertices,mesh_number)
            head_Flag = False
            spine_Flag = False
            stub_Flag = False
            neck_Flag = False
            #relabel the list accordingly
            for key,value in final_labels.items():
                if value[0:4] == "head":
                    head_Flag = True
                if value[0:4] == "spin":
                    spine_Flag = True
                if value[0:4] == "stub":
                    stub_Flag = True
                if value[0:4] == "neck":
                    neck_Flag = True
                
                
                relabel_segments(final_spine_labels,key,value)
                #add them to the list of processed labels
                processed_labels.append(key)
            if head_Flag == True:
                head_counter += 1
            if spine_Flag == True:
                spine_counter += 1
            if stub_Flag == True:
                stub_counter += 1
            if neck_Flag == True:
                neck_counter += 1
            
            
    
    #delete all the old colors for the object and then add back the local regular colors
    create_spine_colors(ob)
    
    '''COLORS FOR THE LABELING
    colors_to_add = ["Error (brown)",
    "Dendrite (purple)",
    "Spine Head (rose)",
    "Spine Neck (light green)",
    "Spine (light pink)"]'''
    
    
    #assign the colors to the faces:
    for i in range(0,len(faces_raw)):
        if final_spine_labels[i][0:4] == "head":
            faces_raw[i].material_index = 2
        elif final_spine_labels[i][0:4] == "neck":
            faces_raw[i].material_index = 3
        elif final_spine_labels[i] == "backbone":
            faces_raw[i].material_index = 1
        elif final_spine_labels[i][0:4] == "spin":
            faces_raw[i].material_index = 4
        elif final_spine_labels[i][0:4] == "stub":
            faces_raw[i].material_index = 5
        else:
            faces_raw[i].material_index = 0
    
    
    return head_counter,neck_counter, spine_counter, stub_counter
        

    
    
     
            
        











if __name__ == "__main__":
    print('hello')
    
    head_counter,neck_counter, spine_counter, stub_counter = automatic_spine_classification_vp2()
                
    #smooth_backbone(max_backbone_threshold = 600,backbone_threshold=200,secondary_threshold=20,shared_vert_threshold=25,number_Flag = False, seg_numbers=1,smooth_Flag=True)
    '''
    head_counter = automatic_spine_classification_vp2()
    print("head_counter = " + str(head_counter))
    number = "85"
    #export_connection(number,"neck_with_little_hat-38.045")
    
    
    
    
    
    
    label = number
    neighbors_list,neighbors_shared_vert, labels_list = get_neighbor_verts(label)

    print("neighbors_list = " + str(neighbors_list))
    print("neighbors_shared_vert = " + str(neighbors_shared_vert))
    
    
    backbone_threshold=300
    myCounter = Counter(labels_list)
    print("length of label = " + str(myCounter[label]))

    spine_labels = []
    backbone_labels = []
    
    #may not want to relabel until the end in order to preserve the labels in case label a big one wrong
    for label,times in myCounter.items():
        if(times >= backbone_threshold):
            #print(str(label) + ":" + str(times))
            backbone_labels.append((label,times))   
        else:
            spine_labels.append(label) 
    print("backbone_labels")
    print(backbone_labels)
    print(myCounter["backbone"])
    
    '''

