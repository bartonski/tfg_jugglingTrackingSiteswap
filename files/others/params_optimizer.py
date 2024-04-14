import concurrent.futures
import numpy as np
import math
from prediction.seq_preprocessing import point_extractor
from metrics.motmetrics import motMetricsEnhancedCalculator
import random
def test(ss, threshold):
    # This is the function that will be executed with different 'param' values
    source_path = './dataset/ss'+str(ss[0])+'_red_AlejandroAlonso.mp4'
    res,_ = point_extractor(source_path,convergence_threshold=1, x_mul_threshold=threshold,  visualize=False)
    res1 = res >= ss[1][0] and res <= ss[1][0]
    res2 = abs(((ss[1][1]-ss[1][0]) //2) - res)
    print("{}\t{}\t{}\t{}\t{}".format(ss, threshold, res, res1, res2))
    return "{}\t{}\t{}\t{}\t{}".format(ss, threshold, res, res1, res2)

def main():
    # List of 'for' values that are used -i in executions of the 'test' function
    siteswaps = [(1,(482,632)), (3,(570,600)), (441,(530,557)), (423,(555,590)), (5,(545, 575))]
    #siteswaps = [(3,(570,600)),]
    theshold = [1, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.01]
    #theshold = [0.6,]
    # We create an object of type ThreadPoolExecutor to execute the functions in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # For each value of 'param' we create a Future object that executes the 'test' function
        futures = {executor.submit(test, ss, theshold_value): (ss, theshold_value) for ss in siteswaps for theshold_value in theshold}

        # Wait for all executions of the 'test' function to finish
        concurrent.futures.wait(futures)
        with open("./AlejandroAlonso/results/res_seq_optimizer.txt", "w") as f:
            for future in futures:
                f.write(f'{future.result()}\n')

if __name__ == '__main__':
    main()
