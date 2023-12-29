import pandas as pd
import xgboost as xgb

# Predicitons Generator Class.
class Predictions_Generator:
    ''' Arguments:\n
            model_path - Path to the model.
    '''
    
    def __init__(self, model_path) -> None:
        
        # Load the model.
        self.model = xgb.XGBClassifier()
        self.model.load_model(model_path)
        
        # Current Accuracy Score.
        self.model_accuracy = 0.987164

    # Function that creates DataFrame with specific columns names.
    def create_dataframe(self, X) -> pd.DataFrame:
        
        # Round every value up to 6 decimals.
        for i in range(len(X)):
            X[i] = round(X[i], 6)
        
        # Return a complete DataFrame.
        return pd.DataFrame([X], columns=['MEAN_RR', 'MEDIAN_RR', 'SDRR', 'RMSSD', 'SDSD', 'SDRR_RMSSD'])
    
    # Main function for predictions generation.
    def generate_prediction(self, X) -> int:
        ''' Arguments:\n
                X - a float array that contains the following structure:\n
                ['MEAN_RR', 'MEDIAN_RR', 'SDRR', 'RMSSD', 'SDSD', 'SDRR_RMSSD']
        '''
        
        # Create a DataFrame from 'X'.
        X_pred = self.create_dataframe(X)
        
        # Generate prediction.
        y_pred = self.model.predict(X_pred)
        
        if (y_pred[0] == 0):
            return 0
        else:
            return 1