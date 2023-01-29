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
    amount = 500

    loops, loop_candidates = find_loops_in_box(origin - displacement(amount), origin + displacement(amount), timestamp)

    # work with loop candidates if no loop is fully in box
    if not loops:
        loops = loop_candidates

    find_lomer_query = f"""
    MATCH (l:Loop{{time:{timestamp}}})--(:Node)--(j:Junction{{type:1}})--(:Node)--(k:Loop) 
    WHERE l.global_id in {loops} 
    AND k.global_id in {loops}
    AND l.global_id < k.global_id  
    RETURN l.global_id as gid_start, k.global_id as gid_end
    """
    
    loop_pairs = run_query(find_lomer_query, {}).drop_duplicates()

    # find best fitting box for this timestamp
    current_best_box = (())
    for pair in loop_pairs.itertuples():
        if (pair[0] > 10):
            break
        _, _, box1 = fit_box_to_loop(pair[1], timestamp)
        _, _, box2 = fit_box_to_loop(pair[2], timestamp)
        p1, p2, merged_box = merge_boxes(box1, box2)
        if not current_best_box:
            current_best_box = (tuple(p1), tuple(p2))
        elif compute_distance_of_box_to_point(current_best_box[0], current_best_box[1], origin) > compute_distance_of_box_to_point(p1, p2, origin):
            current_best_box = (tuple(p1), tuple(p2))
    final_boxes[timestamp].append(current_best_box)
    print("Computation of bounding box for timestamp:", timestamp, "finished after", round(time.time() - ctime), "seconds.")

with open("../output/lomer_junction_bounding_box_res.json", "w") as f:
    f.write(json.dumps(final_boxes))