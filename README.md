# awsremars2019-revegas-workshop
Private code repo for the re:Vegas blackjack computer vision workshop

 - /ml
   - Contains python code and Jupyter notebooks related to training and processing images for card segmentation and rank detection
 - /backend
   - contains code related to:
     - reading camera footage (kinesis video streams, snippets from S3, TBD...)
     - Cropping footage for player hand location and dealer cards
     - running inference (using afore mentioned ML trained model)
     - keeping track of player and dealer hands
     - running count, true count of cards
     - heuristic blackjack "basic strategy" processing
     - publish inference results, totals, and strategy to serve frontend
   - /frontend
     - HTML, JS, CSS code for a frontend that displays results from the ML and backend
     - likely to use Amplify and AppSync
     - WSS to AppSync to display inference + betting strategy
     - "replay" camera footage with conventional CV outputs (mask, bounding box, confidence) over the cards