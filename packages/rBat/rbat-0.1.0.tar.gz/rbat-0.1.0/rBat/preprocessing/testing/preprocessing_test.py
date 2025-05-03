import numpy as np
import pandas as pd
import os
from sklearn.metrics import recall_score, precision_score, accuracy_score, f1_score
from preprocessing.testing.testing_helpers.ma_smoothing import moving_average
from preprocessing.smoothing import lowess, repeated_running_medians
from preprocessing.Preprocessor import Preprocessor

PRE_PATH = "preprocessing/testing/test_data/preprocessed/"
RAW_PATH = "preprocessing/testing/test_data/raw/"
PROGRESSION = 1
LINGERING = 0

def segmentation_testing():
    overall_accuracy = 0
    overall_recall   = 0
    overall_precision = 0
    overall_tp_fp = 0
    overall_tp_fn = 0

    raw_files = os.listdir(RAW_PATH) 
    pre_files = os.listdir(PRE_PATH)

    prepro = Preprocessor()

    for raw_file in raw_files:
        trial_id = raw_file.split("_")[-2]
        pre_file = None
        for file in pre_files:
            if file.split("_")[-2] == trial_id:
                pre_file = file
                break
        
        # Collect raw files
        names = ["Sample no.","Time","X","Y"]
        raw_data = pd.read_csv(RAW_PATH + raw_file, names = names, usecols = range(4))
        header_idx = 0

        for i in range(len(raw_data)):
            if raw_data.loc[i,"Sample no."] == "Sample no.":
                header_idx = i + 1
                break
        raw_data = raw_data[header_idx:].reset_index(drop=True)
        raw_data["Sample no."] = raw_data["Sample no."].astype(int)


        # Collect labels
        names  = ["Sample no.", "X_S","Y_S","V_S","SegmentType_S"]
        labels = pd.read_csv(PRE_PATH + pre_file, names = names)[['Sample no.','SegmentType_S']]
        labels["Sample no."] = raw_data["Sample no."].astype(int)
        
        # Merge data and labels and drop nan rows
        data = raw_data.merge(labels,'left','Sample no.')
        
        data = data[(data["X"] != "-") | (data["Y"] != "-")]        
        
        raw_data = data[["Sample no.","Time","X","Y"]].to_numpy().astype(float)
        true_labels   = data[["SegmentType_S"]].to_numpy().astype(float) 

        print(f"Segmentation test: {trial_id}")
        print(f"\tdata file:\t {raw_file}")
        print(f"\tlabels file:\t {pre_file}")

        test_data = prepro.preprocess_data(raw_data)

        test_labels = test_data[:,-1]

        print(f"\t accuracy:\t{accuracy_score(true_labels,test_labels):.4f}")
        print(f"\t precision:\t{precision_score(true_labels,test_labels,pos_label=PROGRESSION):.4f}")
        print(f"\t recall:\t{recall_score(true_labels,test_labels,pos_label=PROGRESSION):.4f}")
        print(f"\t F1 score:\t{f1_score(true_labels,test_labels,pos_label=PROGRESSION):.4f}")

        tp_fp = (test_labels == PROGRESSION).sum()
        tp_fn = (true_labels == PROGRESSION).sum()

        overall_tp_fp  += tp_fp
        overall_tp_fn  += tp_fn
        overall_accuracy += accuracy_score(true_labels,test_labels)
        overall_precision += tp_fp * precision_score(true_labels,test_labels,pos_label=PROGRESSION)
        overall_recall += tp_fn * recall_score(true_labels,test_labels,pos_label=PROGRESSION)

    print(f"Overall Accuracy:\t{overall_accuracy/len(raw_files):.4f}")
    print(f"Overall Precision:\t{overall_precision/overall_tp_fp:.4f}")
    print(f"Overall Recall:\t{overall_recall/overall_tp_fn:.4f}")
    print(f"Overall F1 Score:\t{(2*(overall_precision/overall_tp_fp)*(overall_recall/overall_tp_fn))/((overall_precision/overall_tp_fp)+(overall_recall/overall_tp_fn)):.4f}")

def lowess_testing():
    raw_files = os.listdir(RAW_PATH) 
    
    tot_dist_lowess = 0
    tot_dist_ma = 0

    for file in raw_files:
        trial_id = file.split("_")[-2]
        
        # Collect raw files
        names = ["Sample no.","Time","X","Y"]
        data = pd.read_csv(RAW_PATH + file, names = names, usecols = range(4))
        header_idx = 0

        for i in range(len(data)):
            if data.loc[i,"Sample no."] == "Sample no.":
                header_idx = i + 1
                break
        data = data[header_idx:].reset_index(drop=True)
                
        data = data[(data["X"] != "-") | (data["Y"] != "-")]        
        
        X = data["X"].to_numpy().astype(float)
        Y = data["Y"].to_numpy().astype(float)
        
        trial_id = file.split("_")[-2]
        print(f"LOWESS test: {trial_id}")

        X_lowess = lowess(X, 2, 24, 2)
        Y_lowess = lowess(Y, 2, 24, 2)

        X_ma,_   = moving_average(X,24,12,1.3)
        Y_ma,_   = moving_average(X,24,12,1.3)
        
        dist_lowess = np.sum(np.abs(np.diff(X_lowess))) + np.sum(np.abs(np.diff(Y_lowess)))
        dist_ma     = np.sum(np.abs(np.diff(X_ma))) + np.sum(np.abs(np.diff(Y_ma)))
        print(f"\tLOWESS distance traveled:\t{dist_lowess:.2f}")
        print(f"\tMA distance traveled:\t\t{dist_ma:.2f}")
        tot_dist_lowess += dist_lowess
        tot_dist_ma += dist_ma
    print(f"Total LOWESS distance traveled:\t{tot_dist_lowess:.2f}")
    print(f"Total MA distance traveled:\t{tot_dist_ma:.2f}")
    assert tot_dist_ma < tot_dist_lowess

def rrm_testing():
    raw_files = os.listdir(RAW_PATH) 
    
    tot_dist_rrm = 0
    tot_dist_ma = 0

    for file in raw_files:
        trial_id = file.split("_")[-2]
        
        # Collect raw files
        names = ["Sample no.","Time","X","Y"]
        data = pd.read_csv(RAW_PATH + file, names = names, usecols = range(4))
        header_idx = 0

        for i in range(len(data)):
            if data.loc[i,"Sample no."] == "Sample no.":
                header_idx = i + 1
                break
        data = data[header_idx:].reset_index(drop=True)
                
        data = data[(data["X"] != "-") | (data["Y"] != "-")]        
        
        X = data["X"].to_numpy().astype(float)
        Y = data["Y"].to_numpy().astype(float)
        
        trial_id = file.split("_")[-2]
        print(f"RRM test: {trial_id}")

        X_rrm, X_arr_rrm = repeated_running_medians(X, [7, 5, 3, 3], 12, 1.3)
        Y_rrm, Y_arr_rrm = repeated_running_medians(X, [7, 5, 3, 3], 12, 1.3)

        X_ma,X_arr_ma   = moving_average(X,7,12,1.3)
        Y_ma,Y_arr_ma   = moving_average(X,7,12,1.3)
        
        dist_rrm = 0
        dist_ma = 0
        # Distance only during arrest periods.
        for arr in X_arr_rrm:
            dist_rrm += np.sum(np.abs(np.diff(X_rrm[arr[0]:arr[1]+1])))
        for arr in Y_arr_rrm:
            dist_rrm += np.sum(np.abs(np.diff(Y_rrm[arr[0]:arr[1]+1])))
        for arr in X_arr_ma:
            dist_ma += np.sum(np.abs(np.diff(X_ma[arr[0]:arr[1]+1])))
        for arr in Y_arr_ma:
            dist_ma += np.sum(np.abs(np.diff(Y_ma[arr[0]:arr[1]+1])))

        print(f"\tRRM distance traveled during arrests:\t{dist_rrm:.2f}")
        print(f"\tMA distance traveled during arrests:\t{dist_ma:.2f}")
        tot_dist_rrm += dist_rrm
        tot_dist_ma += dist_ma
    print(f"\tTotal RRM distance traveled during arrests:\t{tot_dist_rrm:.2f}")
    print(f"\tTotal MA distance traveled during arrests:\t{tot_dist_ma:.2f}")
    assert tot_dist_ma > tot_dist_rrm


segmentation_testing()