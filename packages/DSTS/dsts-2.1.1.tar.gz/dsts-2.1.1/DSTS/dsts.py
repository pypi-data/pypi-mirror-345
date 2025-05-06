import numpy as np
from DSTS.calibration2 import *
from DSTS.mixup import *
from DSTS.y1_generation import *
from DSTS.utils import NNsorting

class dsts:
    def __init__(self, sort, centering, scale_method, test_method, method='DecisionTree'):
        """
        Initialize the dsts class with the specified method.
        
        Parameters:
        method (str): The method to use for data synthesis. Possible values are 'DecisionTree', 'condGMM', 'LR'.
        feature_match (bool): Whether to match feature order using NN.
        """
        self.sort = sort
        self.method = method
        self.centering = centering
        self.scale_method = scale_method
        self.test_method = test_method


    def fit(self, data):            
        try:
            self.data = np.array(data)
        except :
            raise ValueError("Data cannot be converted to numpy ndarray")
        
        self.dim = data.ndim
        if self.dim != 3:
            raise ValueError("Data dimension needs to be 3.")
    
        self.data = self.__test(self.data)


    def generate(self, tot_iter=5, aug=5, n_comp=2) -> np.ndarray:
        """
        Synthesizes a new time series using DS2 algorithms.

        Parameters:
        ite (int, optional): The number of calibration iterations for each timestamp. 
                             Defaults to 3. 
        tot_iter (int, optional): The number of calibration loops for whole time series. 
                                  Default to 4.
        aug (int): The multiplier for the size of the synthesized data relative to the original data. 
                   Defaults to 5.
        n_comp (int, optional): The number of mixture components in GMM. 
                                Default is 2.
        
        Returns:
        np.ndarray: The synthesized data array of shape (size * aug, length).

        """
        size, length, var = self.data.shape
        if aug>1:
            k = 5
        else:
            k=5

        # handle sorting method
        print("Start mixup")
        rmixup, sf_mixup = r_mixup(self.data, k, self.centering, self.scale_method, self.test_method)    
        
        # Generate y1 for scale method y1 and ymax
        if self.scale_method == 'noscale':
            pass
        else:
            if self.method=='DecisionTree':
                if self.scale_method == 'y1':
                    sf_star = dt_draw_y1(self.data, rmixup, sf_mixup, self.sort)
                # elif self.scale_method == 'ymax':
                #     sf_star = dt_draw_ymax(self.data, rmixup, k)

            elif self.method=='GMM':
                if self.scale_method == 'y1':
                    sf_star = gmm_draw_y1(self.data, rmixup, sf_mixup, self.sort)
                # elif self.scale_method == 'ymax':
                #     sf_star = gmm_draw_ymax(self.data, rmixup, sf_mixup, self.sort)
                                
            elif self.method=='condGMM':
                sf_star = condGMM_draw_y1(self.data, rmixup, n_comp, self.sort)

            elif self.method=='LR':
                sf_star = lr_draw_y1(self.data, rmixup, self.sort)


        # Combine scale factors and r mixup to generate augmented synthetic samples
        if self.scale_method == 'y1':
            synth = sf_star[:,np.newaxis,:]*rmixup
            synth-=self.epsilon 

        elif self.scale_method == 'ymax':
            synth = sf_mixup*rmixup
            synth-=self.epsilon

        elif self.scale_method == 'noscale':
            synth = rmixup
            synth-=self.epsilon

        self.data = self.data-self.epsilon


        print("Start Calibration")
        calib_data = calibration(self.data, synth, tot_iter, aug)
        final_data = calib_data

        return final_data
       

    def __test(self, data):
        # Check if data contains any NaN values
        if np.isnan(data).any():
            raise ValueError("Your data must not contain any NaN values.", flush=True)

        self.epsilon = 0
        if np.any(data<=0):
            self.epsilon=np.abs(data.min())+1
            data = data+self.epsilon
            print(f"WARNING! Your data contains non-positive values. Epsilon {self.epsilon} added.", flush=True)
            

        return data
        
