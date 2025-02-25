from tracking.data_saver_files.mot16_utils import load_data 
from files.prediction.seq_extractor import seq_extraction, seq_extraction_cuadrants
from prediction.seq_preprocessing import point_extractor
from files.prediction.ss_prediction import get_full_ss_string, prediction

if __name__ == "__main__":
    ss = '3'
    num_balls = 3
    source_path_video = '/home/alex/tfg_jugglingTrackingSiteswap/dataset/jugglingLab/ss'+ss+'_red_JugglingLab.mp4'
    #source_path_video = '/home/alex/tfg_jugglingTrackingSiteswap/dataset/tanda2/ss'+ss+'_red2_AlejandroAlonso.mp4'
    source_path_file = '/home/alex/tfg_jugglingTrackingSiteswap/AlejandroAlonso/results/mot16/Tracking/'+ss+'_ColorTrackingMaxBalls.txt'

    ids = load_data(source_path_file)
    print("--> Cuadrants")
    point = point_extractor(source_path_video, y_mul_threshold=0.21)
    #point = (515, 952)
    print(point)
    seq = seq_extraction_cuadrants(ids, point, 0, 0)
    print("Seq:")
    print(seq)
    full_pred = get_full_ss_string(seq[0])
    pred = prediction(seq[0], num_balls)
    print("Full_ss_string:")
    print(full_pred)
    print("Pred:")
    print(pred)
    print("--> Coords")
    seq = seq_extraction(ids)
    print("Seq:")
    print(seq)
    full_pred = get_full_ss_string(seq)
    pred = prediction(seq, num_balls)
    print("Full_ss_string:")
    print(full_pred)
    print("Pred:")
    print(pred)
