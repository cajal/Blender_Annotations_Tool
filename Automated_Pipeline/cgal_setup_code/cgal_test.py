import cgal_Segmentation_Module
import time

start_time = time.time()
print(start_time)

print("about to start")
fil_loc = "/Users/brendancelii/Documents/"
filename = "neuron_28571618_Basal_1"

cgal_Segmentation_Module.cgal_segmentation(fil_loc,filename,16,0.04)
print("finished")
print("--- %s seconds ---" % (time.time() - start_time))
