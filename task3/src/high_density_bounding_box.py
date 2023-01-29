from utility import *
import time
from collections import defaultdict
import json

origin = np.array([6187.5, 6187.5, 6187.5])
displacement = lambda x: np.array([x, x, x])
final_boxes = defaultdict(list)

print("Starting computation of bounding boxes ...")
ctime = time.time()
for timestamp in range(50,10000,50):
    amounts = [100, 200, 300, 400, 500]
    current_best_box = (())
    current_best_density = 0
    global_density = calculate_density_in_box(timestamp)
    for amount in amounts:
        box_density = calculate_density_in_box(timestamp, origin - displacement(amount), origin + displacement(amount))
        if box_density > current_best_density and box_density > 2*global_density:
            current_best_density = box_density
            current_best_box = (tuple(origin - displacement(amount)), tuple(origin + displacement(amount)))
    if current_best_density != 0:
        final_boxes[timestamp].append(current_best_box)
    print("Computation of bounding box for timestamp", timestamp, "finished after", round(time.time() - ctime), "seconds, global density was", global_density)

with open("../output/high_density_bounding_box_res.json", "w") as f:
    f.write(json.dumps(final_boxes))