import concurrent.futures
import numpy as np
from tracking.prediction.kalman_filter import KalmanFilter
import random
import math
from itertools import chain
import re
import os

def kalman_tester(gt_path,dt, u_x, u_y, std_acc, x_std_meas, y_std_meas):
    ids = {}
    total_dist = 0
    with open(gt_path, "r") as f:
        for line in f:
            values = line.strip().split(",")
            id = int(values[1])
            bb_left = float(values[2])
            bb_top = float(values[3])
            bb_width = float(values[4])
            bb_height = float(values[5])
            if id not in ids:
                tmp = {}
                tmp['id'] = id
                coords = (bb_left+(bb_width//2),bb_top+(bb_height//2))
                tmp['coords'] = coords
                KF = KalmanFilter(dt, u_x,u_y, std_acc, x_std_meas, y_std_meas)
                KF.update(np.array([[coords[0]], [coords[1]]]))
                tmp['kalman'] = KF
                (x,y) = tmp['kalman'].predict()
                tmp['predict'] = (x.max(),y.max())
                ids[id] = tmp
            else:
                coords = (bb_left+(bb_width//2),bb_top+(bb_height//2))
                total_dist += math.dist(coords, ids[id]['predict'])
                ids[id]['kalman'].update(np.array([[coords[0]], [coords[1]]]))
                ids[id]['coords'] = coords
                (x,y) = ids[id]['kalman'].predict()
                ids[id]['predict'] = (x.max(),y.max())

    return total_dist, gt_path, dt, u_x, u_y, std_acc, x_std_meas, y_std_meas

def test(ss):
    # This is the function that will be executed with different 'param' values
    # This example simply returns the value of 'param' squared
    gt_path = './AlejandroAlonso/results/mot16/GroundTruth/'+str(ss[0])+'_manual.txt'

    best_results = []
    count_dt, count_ux, count_uy, count_stdacc, count_xstdmeas, count_ystdmemas = 0,0,0,0,0,0

    for dt in np.arange(0.3, 0.31, 1):
        count_dt +=1
        for u_x in np.arange(1,1.1,1):
            count_ux +=1
            for u_y in np.arange(1, 2.1, 0.1):
                count_uy +=1
                for std_acc in np.arange(6, 9.1, 0.1):
                    count_stdacc +=1
                    for x_std_meas in np.arange(0.1, 0.11, 1):
                        count_xstdmeas +=1
                        for y_std_meas in np.arange(0.1, 0.11, 1):
                            result = kalman_tester(gt_path,dt, u_x, u_y, std_acc, x_std_meas, y_std_meas)
                            #print("{:.2f} - ss{}".format(result, ss[0]))
                            count_ystdmemas +=1
                            if len(best_results) < 10 or result < best_results[-1][0]:
                                # Add the result to the top results list and sort the list
                                best_results.append((round(result,2), dt, u_x, u_y, std_acc, x_std_meas, y_std_meas, ss[0]))
                                best_results.sort()

                                # If the list has more than 10 elements, remove the worst result
                                if len(best_results) > 10:
                                    del best_results[-1]

                                count_dt, count_ux, count_uy, count_stdacc, count_xstdmeas, count_ystdmemas = 0,0,0,0,0,0
                            elif count_ystdmemas == 3:
                                count_ystdmemas=0
                                #print("Salgo count_ystdmemas")
                                break
                        if count_xstdmeas == 3:
                            count_xstdmeas=0
                            #print("Salgo count_xstdmeas")
                            break
                    if count_stdacc == 3:
                        count_stdacc=0
                        #print("Salgo count_stdacc")
                        break
                if count_uy == 3:
                    count_uy=0
                    #print("Salgo count_uy")
                    break
            if count_ux == 3:
                count_ux=0
                #print("Salgo count_ux")
                break
        print(str(ss) + "_" + str(dt) + "_" + str(u_x) + "_" + str(u_y) + "_" + str(std_acc) + "_" + str(x_std_meas) + "_" + str(y_std_meas) + "\n")
        if count_dt == 3:
            count_dt=0
            #print("Salgo count_dt")
            break

    return best_results

def main():
    # List of 'for' values that are used -i in executions of the 'test' function
    siteswaps = [(1,1), (3,3), (441,3), (423,3)]
    dts = np.arange(0.1, 1.1, 0.1)
    u_xs = range(1,61,1)
    u_ys = range(1,61,1)
    std_accs = range(1,61,1)
    x_std_meass = np.arange(0.1, 1.1, 0.1)
    y_std_meass = np.arange(0.1, 1.1, 0.1)
    test_batch = 1000
    num_batchs = 100

    """
    # We create an object of type ThreadPoolExecutor to execute the functions in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # For each value of 'param' we create a Future object that executes the 'test' function
        futures = {executor.submit(test, ss) for ss in siteswaps}
        # Wait for all executions of the 'test' function to finish
        concurrent.futures.wait(futures)

        # Write the results to a file "res_concretos.txt" with format: ss -> result
        with open("./AlejandroAlonso/results/mot16/Optimizer/res_concretos.txt", "w") as f:
            for future in futures:
                for result, dt, u_x, u_y, std_acc, x_std_meas, y_std_meas, ss in future.result():
                    f.write(str(ss) + "_" + str(dt) + "_" + str(u_x) + "_" + str(u_y) + "_" + str(std_acc) + "_" + str(x_std_meas) + "_" + str(y_std_meas) + " -> " + str(result) + "\n")
    """
    
    for i in range(num_batchs):
        # We create an object of type ThreadPoolExecutor to execute the functions in parallel
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # For each value of 'param' we create a Future object that executes the 'test' function
            futures = []
            for _ in range(test_batch): # num_tests is the number of tests you want to perform
                ss = random.choice(siteswaps)
                dt = random.choice(dts)
                u_x = random.choice(u_xs)
                u_y = random.choice(u_ys)
                std_acc = random.choice(std_accs)
                x_std_meas = random.choice(x_std_meass)
                y_std_meas = random.choice(y_std_meass)
                futures.append(executor.submit(kalman_tester, './AlejandroAlonso/results/mot16/GroundTruth/'+str(ss[0])+'_manual.txt', dt, u_x, u_y, std_acc, x_std_meas, y_std_meas))

                # Wait for all executions of the 'test' function to finish
                concurrent.futures.wait(futures)

                # Write the results to a file "res_random.txt" with format: ss_dt_ux_uy_stdacc_xstdmeas_ystdmeas -> result
                with open("./AlejandroAlonso/results/mot16/Optimizer/res_random_"+str(i)+".txt", "w") as f:
                    for future in futures:
                        total_dist, gt_path, dt, u_x, u_y, std_acc, x_std_meas, y_std_meas = future.result()
                        ss= re.search(r"\/(\d+)_manual\.txt$", gt_path).group(1)
                        f.write(str(ss) + "_" + str(dt) + "_" + str(u_x) + "_" + str(u_y) + "_" + str(std_acc) + "_" + str(x_std_meas) + "_" + str(y_std_meas) + " -> " + str(total_dist) + "\n")

def compare_random():
    thresholds = {}
    thresholds['1'] = 8158.89
    thresholds['3'] = 5200.8
    thresholds['441'] = 13767.37
    thresholds['423'] = 12767.0

    path = './AlejandroAlonso/results/mot16/Optimizer'
    output = 'res_concretos_extras.txt'

    with open(path+'/'+output, 'w') as output:
        directory = os.fsencode(path)
        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            if 'random' in filename:
                with open(path+'/'+filename, 'r') as content:
                    for line in content.readlines():
                        substrings = line.split("_")
                        ss = str(substrings[0])
                        dt = float(substrings[1])
                        u_x = int(substrings[2])
                        u_y = int(substrings[3])
                        std_acc = int(substrings[4])
                        x_std_meas = float(substrings[5])
                        y_std_meas = float(substrings[6].split(' ')[0])
                        res = float(substrings[6].split(' ')[-1])
                        if res < thresholds[ss]:
                            output.write(str(ss) + "\t" + str(dt) + "\t" + str(u_x) + "\t" + str(u_y) + "\t" + str(std_acc) + "\t" + str(x_std_meas) + "\t" + str(y_std_meas) + "\t" + str(res) + "\n")
                        

if __name__ == '__main__':
    compare_random()
