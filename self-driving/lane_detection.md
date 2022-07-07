### Lane Detection
[[code]](https://github.com/wallaceloos/Computer_Vision/blob/master/codes/lane_detection.py) 

<p align="justify"> Lane detection plays an important role in autonomous vehicles, because it ensures safe driving practices. After recording a video from the jetbot’s camera, I have decided to apply a lane detection algorithm to it. It is a simple algorithm that can be divided into 4 parts: 1) camera calibration, 2) edge detection, 3) perspective correction, and 4) line estimation. However, it is important to remember that  there are many modern lane detection methods in the literature, and this algorithm is very simple and probably will not perform well for complex environments. This implementation was inspired by this repository: https://github.com/maunesh/advanced-lane-detection-for-self-driving-cars and the book, Hands-On Vision and Behavior for Self-Driving Cars, by Luca Venturi and Krishtof Korda. A summary of the algorithm is presented below. 
  
<p align="center">
<img src="https://github.com/wallaceloos/Computer_Vision/blob/master/self-driving/videos/lane_detection.gif" width="30%" height="30%">
</p>

#### Camera Calibration
  
<p align="justify"> Due to the barrel distortion introduced by the jetbot’s camera lens, the first step required is to correct the image distortion caused by it. In order to perform this correction, we can use the extrinsic and intrinsic camera parameters. These parameters are extracted using a camera calibration algorithm. The extrinsic parameter consists of the location of the camera in the 3D world, and the intrinsic parameters are the optical center and focal length of the camera. After the calibration we use the radial distortion coefficients of the lens to correct the image. The calibration camera used in this example was the chessboard pattern with the Scaramuzza et. al calibration algorithm.

<p align="center">
<img src="https://github.com/wallaceloos/Computer_Vision/blob/master/self-driving/images/fig1_lane_detection.png" width="36%" height="36%"> 
</p>

#### Edge Detection

<p align="justify"> The next step to detect the lanes is to segment the edges on the road. This segmentation was made on a different color space, HSL (for hue, saturation, lightness), and then, we use the Sobel edge detector over the lightness channel and select the edges above a threshold x. 

<p align="center"> 
<img src="https://github.com/wallaceloos/Computer_Vision/blob/master/self-driving/images/fig2_lane_detection.png" width="36%" height="36%"> 
</p>

#### Perspective Correction

<p align="justify"> The perspective projection makes straight lines look curved, and then the real distance of the objects cannot easily be interpreted, and it is also difficult to identify curving lanes. To correct this perspective effect, we can perform an orthogonal top-down projection aka bird’s-eye view.  

<p align="center">
<img src="https://github.com/wallaceloos/Computer_Vision/blob/master/self-driving/images/fig3_lane_detection.png" width="36%" height="36%"> 
</p>

#### Line Estimation

<p align="justify"> The line estimation is performed by 1) computing the histogram of the sum of the pixels over the columns of the image, 2) and then sliding a window through the edges to record the pixels that will be used to estimate a line. The estimated lines are brought back to the native space.

<p align="center">
<img src="https://github.com/wallaceloos/Computer_Vision/blob/master/self-driving/images/fig4_lane_detection.png" width="36%" height="36%"> 
</p>

The same algorithm can be applied on different images as well. However, it is necessary to adjust the perspective step. 
<p align="center">
<img src="https://github.com/wallaceloos/Computer_Vision/blob/master/self-driving/videos/lane_road_detection.gif" width="30%" height="30%">
</p>
