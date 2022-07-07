import cv2
import numpy as np
import matplotlib.pyplot as plt
import glob

"""
 1) Edge detection
 2) Bird'view
 3) Line detection
 4) Inverse perspective
"""

def edge_detection(img, thr = 40):
  img_hsl = cv2.cvtColor(img[...,::-1], cv2.COLOR_BGR2HLS)
  _,_,l = cv2.split(img_hsl)
  edge_vertical = cv2.Sobel(l, cv2.CV_64F, 1, 0, ksize=3)
  edge_vertical = np.float32(edge_vertical)

  edge_horizontal = cv2.Sobel(l, cv2.CV_64F, 0, 1, ksize=3)
  edge_horizontal = np.float32(edge_horizontal)

  gradmag = np.sqrt(edge_vertical**2 + edge_horizontal**2) > thr
  return  np.float32(gradmag)

def bird_view_transform(img, perspective_correction):

  IMAGE_H = img.shape[0]
  IMAGE_W = img.shape[1]

  bird_view_image = cv2.warpPerspective(img, perspective_correction, (200, 100), flags=cv2.INTER_LINEAR)
  return bird_view_image

def find_lanes_histogram(hist_lane, thr = 6):
  size_h = len(hist_lane)
  max_index_left = np.argmax(hist_lane[0:size_h//2])
  if hist_lane[max_index_left] < thr:
    max_index_left = -1

  max_index_right = np.argmax(hist_lane[(size_h//2):])+size_h//2
  if hist_lane[max_index_right] < thr:
    max_index_right = -1

  return max_index_left, max_index_right

def fit_line(line_avg, lane_indexes, non_zero_x, non_zero_y, beta = 0.95):

  if len(lane_indexes) == 0:
    return False, [], []

  lane_indexes = np.concatenate(lane_indexes, axis=0 )
  x = non_zero_x[lane_indexes]
  y = non_zero_y[lane_indexes]

  ploty = np.linspace(0, 100, 200)

  line_fit = np.polynomial.polynomial.polyfit(y, x, 2)

  if line_avg == None:
    line_avg = line_fit
  else:
    line_avg =  beta * line_avg + (1 - beta) * line_fit

  line_fit = line_avg[2] * ploty ** 2 + line_avg[1] *ploty + line_avg[0]

  pts_line = list(zip(list(line_fit), list(ploty)))

  return True, line_avg, pts_line

def slide_window(img, hist_lane, line_avg_left, line_avg_right, num_windows,  margin = 30, min_num_pixel = 10):
  img_h = img.shape[0]
  win_h = int(img_h/num_windows)
  non_zero = img.nonzero()
  non_zero_y = np.array(non_zero[0])
  non_zero_x = np.array(non_zero[1])

  left_lane_indexes = []
  right_lane_indexes = []

  out_img = img.copy()

  left_x, right_x  = find_lanes_histogram(hist_lane)

  for idx_window in range(num_windows):
    # Y range that we are analyzing
    win_y_top = img_h - idx_window * win_h
    win_y_bottom = win_y_top - win_h

    # X range where we expect the left lane to land
    if left_x != -1:
      win_x_left_min = left_x - margin
      win_x_left_max = left_x + margin

      non_zero_left = ((non_zero_y >= win_y_bottom) & (non_zero_y < win_y_top) & (non_zero_x >= win_x_left_min) & (
      non_zero_x < win_x_left_max)).nonzero()[0]


      if len(non_zero_left) > 0:
        left_lane_indexes.append(non_zero_left)

      if len(non_zero_left) > min_num_pixel:
        #cv2.rectangle(out_img, (win_x_left_min, win_y_bottom), (win_x_left_max, win_y_top), (255, 255, 255), 2)
        left_x = int(np.mean(non_zero_x[non_zero_left]))

    # X range where we expect the right lane to land
    if right_x != -1:
      win_x_right_min = right_x - margin
      win_x_right_max = right_x + margin

      non_zero_right = ((non_zero_y >= win_y_bottom) & (non_zero_y < win_y_top) & (non_zero_x >= win_x_right_min) & (
            non_zero_x < win_x_right_max)).nonzero()[0]

      if len(non_zero_right) > 0:
          right_lane_indexes.append(non_zero_right)

      if len(non_zero_right) > min_num_pixel:
          right_x = int(np.mean(non_zero_x[non_zero_right]))

  status, line_avg_left, fit_line_left = fit_line(line_avg_left, left_lane_indexes, non_zero_x, non_zero_y)
  status, line_avg_right, fit_line_right = fit_line(line_avg_right, right_lane_indexes, non_zero_x, non_zero_y)

  return fit_line_left, fit_line_right

def draw_rectangle(img, fit_line_left, fit_line_right, color_lane):

  list_points_line = []
  order_list = 0
  for elem in [fit_line_left, fit_line_right]:
    if len(elem) > 0:
      if order_list == 0:
        for pts in elem:
          list_points_line.append(pts)
      else:
        for pts in reversed(elem):
          list_points_line.append(pts)
      order_list = 1

  if len(fit_line_left) > 0:
    list_points_line.append(fit_line_left[0])

  contours = []
  if len(list_points_line) > 1:
    for i in range(len(list_points_line)-1):
      ptA = list_points_line[i]
      ptB = list_points_line[i+1]
      contours.append([ptA[0], ptA[1]])
      contours.append([ptB[0], ptB[1]])
    contours = np.asarray(contours).astype(np.int32)
    cv2.fillPoly(img, pts = [contours], color =color_lane)

  return img

def draw_lanes(img, fit_line_left, fit_line_right):

  if len(fit_line_left) > 0 and len(fit_line_right) > 0:
    img = draw_rectangle(img, fit_line_left, fit_line_right, (0,255,0))

  return img

def line_detection(img):
  hist_lane = np.sum(img, axis=0)
  fit_line_left, fit_line_right = slide_window(img, hist_lane, None, None, 10, 10)

  out_img = np.zeros([img.shape[0], img.shape[1], 3], dtype=np.uint8)
  out_img = draw_lanes(out_img, fit_line_left, fit_line_right)

  if len(fit_line_left) > 0:
    cv2.polylines(out_img, np.int32([np.asarray(fit_line_left)]), 0, (0,0,255), 6)
  if len(fit_line_right) > 0:
    cv2.polylines(out_img, np.int32([np.asarray(fit_line_right)]), 0, (0,0,255), 6)

  return out_img

def inverse_perspective(img, perspective_correction_inv, IMAGE_W, IMAGE_H):
  native_img = cv2.warpPerspective(img, perspective_correction_inv, (IMAGE_W, IMAGE_H), flags=cv2.INTER_LINEAR)
  return native_img


if __name__ == "__main__":

    """#### Calibration parameters"""
    mtx = np.load('misc/mtx.npy')
    dist = np.load('misc/dist.npy')

    img_path = 'misc/img_jetbot_distor.png'
    img = cv2.imread(img_path)
    img = cv2.resize(img, (448,448))
    img_cor = cv2.undistort(img, mtx, dist, None, mtx)

    pt_A = [200, 190]#
    pt_B = [150, 448]
    pt_C = [515, 448]
    pt_D = [361, 190]
    src = np.float32([pt_A, pt_B, pt_C, pt_D])
    dst = np.float32([[45, 0], [45, 100], [180, 100], [180, 0]])
    perspective_correction = cv2.getPerspectiveTransform(src, dst)
    perspective_correction_inv = cv2.getPerspectiveTransform(dst,src)

    plt.figure(figsize=(5,5), dpi=250)
    edge_img = edge_detection(img_cor,60)
    bird_view_img = bird_view_transform(edge_img, perspective_correction)
    line_img = line_detection(bird_view_img)
    native_space = inverse_perspective(line_img, perspective_correction_inv, edge_img.shape[1], edge_img.shape[0])
    result = cv2.addWeighted(img_cor, 1.0, native_space, 0.3, 0)
    plt.imshow(result[...,::-1])
    plt.axis('off')
    plt.show()
