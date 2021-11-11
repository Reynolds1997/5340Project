CS 5340 Final Project
Milestone 1 README
11/10/2021

Evan Parry U1000976 
Niko Novak U1209211

External Resources:
Used SciKit Learn and Pandas (as part of the mlModified.py program, which itself is a modification of the ml.py program from Programming Assignment 3)
https://scikit-learn.org/
https://pandas.pydata.org/

We also used the location, prefix, suffix, and preposition lists sused in Programming Assignment 3.

extract.py requires the presence of mlModified.py, mlFeatureExtractor.py, prefixes.txt, prepositions.txt, suffixes.txt, and the folders development-anskeys and development-docs with corresponding answer and raw files

Scikit and Pandas are already installed on the CADE machines, so we didn't include them in the IE-script.txt

Time Estimate:
In our testing, each individual document took less than one second to process.

Significant Contributions
Evan Parry: Modifying ml.py and mlFeatureExtractor.py to suit our purposes. Developed input and output data processing and formatting system. Developed extract.py "wrapper" program, which creates and deploys an ML model to sort the data.
Niko Novak: CADE testing, researching resources to use, pair programming and bug fixing on mlModified.py and mlFeatureExtractor.py

Known Problems:
Our lack of Outside words in our training data means that every word in a document will be tagged as some sort of feature. This is something we intend to correct in future versions.
