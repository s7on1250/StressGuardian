# StressGuardian
Telegram bot that can determine whether you are stressed. You only need to send a video message to it.

How it works:

Firstly, using OpenCV, the bot detects the user's face, specifically the forehead.
Then, the bot detects changes in the color of the skin due to blood flow near the skin.
After that, the bot builds HRV (Heart Rate Variability) metrics and sends them to the machine learning model (XGBoost is used in this project).
Using a dataset from Kaggle and papers referenced within it (https://www.kaggle.com/datasets/qiriro/swell-heart-rate-variability-hrv), we trained the machine learning model.
Finally, the bot simply sends the result indicating whether the user is stressed.
