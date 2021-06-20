#!/usr/bin/env python
# coding: utf-8

# # Detecting FEX from images
# 
# ## How to use the Feat Detector class.
# 
# *Written by Jin Hyun Cheong*
# 
# Here is an example of how to use the `Detector` class to detect faces, facial landmarks, Action Units, and emotions, from face images or videos. 
# 
# Let's start by installing Py-FEAT if you have not already done so or are using this notebook from Google Colab

# In[1]:


# !pip install -q py-feat


# ## Detecting facial expressions from images. 
# 
# First, load the detector class. You can specify which models you want to use.

# In[2]:


from feat import Detector
face_model = "retinaface"
landmark_model = "mobilenet"
au_model = "rf"
emotion_model = "resmasknet"
detector = Detector(face_model = face_model, landmark_model = landmark_model, au_model = au_model, emotion_model = emotion_model)


# Find the file you want to process. In our case, we'll use our test image `input.jpg`. 

# In[3]:


# Find the file you want to process.
from feat.tests.utils import get_test_data_path
import os
test_data_dir = get_test_data_path()
test_image = os.path.join(test_data_dir, "input.jpg")


# Here is what our test image looks like.

# In[4]:


from PIL import Image
import matplotlib.pyplot as plt
f, ax = plt.subplots()
im = Image.open(test_image)
ax.imshow(im);


# Now we use our initialized `detector` instance to make predictions with the `detect_image()` method.

# In[5]:


image_prediction = detector.detect_image(test_image)
# Show results
image_prediction


# The output is a `Fex` class instance which allows you to run the built-in methods for `Fex`. 
# 
# ## Visualizing detection results.
# 
# For example, you can easily plot the detection results.

# In[6]:


image_prediction.plot_detections();


# If you are interested in visualizing the head pose, you can do so simply by setting `pose=True`. This setting will overlay the x,y, and z-axis of the head onto the image.

# In[7]:


image_prediction.plot_detections(pose=True);


# ## Accessing face expression columns of interest.  
# 
# You can also access the columns of interests (AUs, emotion) quickly. 

# In[8]:


image_prediction.facebox()


# In[9]:


image_prediction.aus()


# In[10]:


image_prediction.emotions()


# In[11]:


image_prediction.facepose() # (in degrees)


# ## Detecting facial expressions and saving to a file. 
# 
# You can also output the results into file by specifying the `outputFname`. The detector will return `True` when it's finished. 

# In[12]:


detector.detect_image(test_image, outputFname = "output.csv")


# ## Loading detection results from saved file. 
# 
# The outputs can be loaded using our `read_feat()` function or a simple Pandas `read_csv()`. We recommend using `read_feat()` because that will allow you to use the full suite of Feat functionalities more easily.

# In[13]:


from feat.utils import read_feat
image_prediction = read_feat("output.csv")
# Show results
image_prediction


# In[14]:


import pandas as pd
image_prediction = pd.read_csv("output.csv")
# Show results
image_prediction


# ## Detecting facial expressions images with many faces. 
# Feat's Detector can find multiple faces in a single image. Let's also practice switching the emotion detector

# In[15]:


face_model = "img2pose" # img2pose acts as both a face detector and a face pose estimator
landmark_model = "mobilenet"
au_model = "logistic"
emotion_model = "fer"
facepose_model = "img2pose"
detector = Detector(face_model=face_model, landmark_model=landmark_model, au_model=au_model, 
                    emotion_model=emotion_model, facepose_model=facepose_model)

test_image = os.path.join(test_data_dir, "tim-mossholder-hOF1bWoet_Q-unsplash.jpg")
image_prediction = detector.detect_image(test_image)
# Show results
image_prediction


# ## Visualize multiple faces in a single image.

# In[16]:


image_prediction.plot_detections(pose=True);


# ## Detecting facial expressions from multiple images
# You can also detect facial expressions from a list of images. Just place the path to images in a list and pass it to `detect_images`. 

# In[17]:


# Find the file you want to process.
from feat.tests.utils import get_test_data_path
import os, glob
test_data_dir = get_test_data_path()
test_images = [file for file in glob.glob(os.path.join(test_data_dir, "*.jpg"))
               if not os.path.basename(file).startswith('no-face')]  # Avoid the test image with no face contained in it
print(test_images)

image_prediction = detector.detect_image(test_images)
image_prediction


# When you have multiple images, you can still call the plot_detection which will plot results for all input images. If you have a lot of images, we recommend checking one by one using slicing. 

# In[18]:


image_prediction.plot_detections();


# You can use the slicing function to plot specific rows in the detection results or for a particular input file.

# In[19]:


image_prediction.iloc[[1]].plot_detections();


# In[20]:


image_to_plot = image_prediction.input().unique()[1]
image_prediction.query("input == @image_to_plot").plot_detections();


# # Detecting FEX from videos
# Detecting facial expressions in videos is also easy by using the `detect_video()` method. This sample video is by [Wolfgang Langer](https://www.pexels.com/@wolfgang-langer-1415383?utm_content=attributionCopyText&utm_medium=referral&utm_source=pexels) from [Pexels](https://www.pexels.com/video/a-woman-exhibits-different-emotions-through-facial-expressions-3063838/).

# In[21]:


# Find the file you want to process.
from feat.tests.utils import get_test_data_path
import os, glob
test_data_dir = get_test_data_path()
test_video = os.path.join(test_data_dir, "WolfgangLanger_Pexels.mp4")

# Show video
from IPython.display import Video
Video(test_video, embed=True)


# Let's predict facial expressions from the video using the `detect_video()` method.

# In[22]:


video_prediction = detector.detect_video(test_video, skip_frames=24)
video_prediction.head()


# You can also plot the detection results from a video. The frames are not extracted from the video (that will result in thousands of images) so the visualization only shows the detected face without the underlying image.
# 
# The video has 24 fps and the actress show sadness around the 0:02, and happiness at 0:14 seconds.

# In[23]:


video_prediction.loc[[48]].plot_detections();


# In[24]:


video_prediction.loc[[17*24]].plot_detections(pose=True);


# We can also leverage existing pandas plotting functions to show how emotions unfold over time. We can clearly see how her emotions change from sadness to happiness.

# In[25]:


video_prediction.emotions().plot()


# In situations you want to predict EVERY frame of the video, you can ust leave out the `skip_frames` argument. Speed of processing may vary depending on the detector you use. 

# In[26]:


video_prediction = detector.detect_video(test_video)
video_prediction

