import rclpy
import sys
import time
import math

from rclpy.node import Node
from std_msgs.msg import Float64
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
from .flow_detector import *


class DropletDetector(Node):
    """
        This node subscribes to the "/image_raw" topic and processes the images by detecting droplets in them.
        It publishes the droplet size on the "droplet_size" topic, the mask image on the "image/mask" topic, and the flow
        image on the "image/flow" topic.
        """

    def __init__(self, thr_min: int, thr_max: int, blur: int = 15,
                 blob_params=None, detection_window=None):
        """
        Initializes the DropletDetector node.

        Parameters:
        thr_min: The minimum threshold for blob detection.
        thr_max: The maximum threshold for blob detection.
        blur: The blurring kernel size. Defaults to 15.
        blob_params: The parameters for blob detection. Defaults to None.
        detection_window: The detection window in the image (in [x_min, y_min, x_max, y_max]). Defaults to None.
        """

        super().__init__('droplet_detector')
        self.set_threshold(thr_min, thr_max)
        self.set_blur(blur)
        self.set_blob_params(blob_params)
        self.detection_window = detection_window

        self._t0 = time.time()

        print(">> Publishing image to topic image/flow")
        print(">> Publishing mask to topic image/mask")
        self.image_pub = self.create_publisher(Image, "image/flow", 1)
        self.mask_pub = self.create_publisher(Image, "image/mask", 1)
        print(">> Publishing droplet size to topic droplet_size")
        self.droplet_pub = self.create_publisher(Float64, "droplet_size", 1)

        self.bridge = CvBridge()

        self.image_sub = self.create_subscription(Image, "/image_raw", self.callback, 1)
        print("<< Subscribed to topic /image_raw")


    def set_threshold(self, thr_min, thr_max):
        """
        Sets the threshold for blob detection.

        Parameters:
        thr_min: The minimum threshold for blob detection.
        thr_max: The maximum threshold for blob detection.
        """
        self._threshold = [thr_min, thr_max]

    def set_blur(self, blur):
        """
        Sets the threshold for blob detection.

        Parameters:
        blur: Sets value for Gaussian blur
        """
        self._blur = blur

    def set_blob_params(self, blob_params):
        """
        Set the blob detection parameters.

        Args:
        blob_params (dict): Blob detection parameters.
        """
        self._blob_params = blob_params

    def callback(self, data):
        """
        Callback function for image subscription.

        Args:
        data (Image): Incoming image data.
        """

        # Log that an image is being received
        self.get_logger().info("Received image from topic /image_raw")

        try:
            # Convert ROS image message to OpenCV image. Encode image in bgr8
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except CvBridgeError as e:
            # Log error and exit callback if conversion fails
            print(e)
            return  # Exit callback on error

        # Check if the image is large enough for processing (320x240)
        (rows, cols, channels) = cv_image.shape
        if cols > 60 and rows > 60:

            #define region of interest
            roi = self.detection_window

            # Call blob_detect function to detect droplets in the image
            # using specified parameters such as thresholds and blur
            keypoints, mask = blob_detect(cv_image, self._threshold[0], self._threshold[1], self._blur,
                                          blob_params=self._blob_params)
            # Blur the area outside the detection window to create a focus
            cv_image = blur_outside(cv_image, 10, roi)
            # Draw the detection window as a rectangle
            cv_image = draw_window(cv_image, self.detection_window, line=1)
            # Draw a frame around the image
            cv_image = draw_frame(cv_image)
            # Draw red circles around all the detected droplets
            # cv_image = draw_keypoints(cv_image, keypoints)

        # Calculate the average size of the detected droplets
        result = cv_image.copy()
        sum = 0
        count = 0
        
        roi_tl = (roi[0],roi[1])
        roi_br = (roi[2],roi[3])

        roi= (int(roi_tl[0]*cols), int(roi_tl[1]*rows), int(roi_br[0]*cols), int(roi_br[1]*rows))        

        # Iterate through all keypoints and draw circles
        for kp in keypoints:
            x, y = kp.pt
            r = kp.size / 2
            x, y, r = int(x), int(y), int(r)
            if x >= roi[0] and y >= roi[1] and x <= roi[2] and y <= roi[3]:
                cv2.circle(result, (x, y), r, (0, 255, 0), thickness=2)
                sum += kp.size
                count += 1
            else:
                if x < roi[0]:
                    xdiff = roi[0]-x
                elif x > roi[2]:
                    xdiff = x - roi[2]
                else:
                    xdiff = 0
                if y < roi[1]:
                    ydiff = roi[1]-x
                elif x > roi[3]:
                    ydiff = y - roi[3]
                else:
                    ydiff = 0
                distance_to_roi = math.sqrt(xdiff**2 + ydiff**2)
                if distance_to_roi < r:
                    cv2.circle(result, (x, y), r, (0, 255, 0), thickness=2)
                    sum += kp.size
                    count += 1
                else:
                    cv2.circle(result, (x, y), r, (255, 0, 0), thickness=2)
        try:
            # Show the image with the search window and droplets overlaid on top
            #cv2.imshow("Frame overlay", cv_image)
            framemsg = self.bridge.cv2_to_imgmsg(result, encoding = 'bgr8')
            self.image_pub.publish(framemsg)
            # Show image with the threshold mask applied to the original Image
            #cv2.imshow("Mask", mask)
            maskmsg = self.bridge.cv2_to_imgmsg(mask, encoding ='mono8')
            self.mask_pub.publish(maskmsg)
            # cv2.waitKey(1)
        except CvBridgeError as e:
            print(e)
        
        if count != 0:
            # Calculate average
            avg = sum / count

            # Log average diameter
            msgdata = 'Average diameter size (pixels) =  %s' % (avg)
            self.get_logger().info(" %s " % (msgdata))

            # Publish average diameter to topic "droplet_size"
            droplet = Float64()
            droplet.data = avg
            self.droplet_pub.publish(droplet)

            # Show the image with circles drawn around the detected droplets
            #cv2.imshow("result", result)
            #cv2.waitKey(1)
            
        fps = 1.0/(time.time()-self._t0)
        self._t0 = time.time()

def main(args=None):
    '''
    Main function that gets called when script is executed.
    Initialises parameters and creates instance of the DropletDetector class.

    Currently reads params from hardcoded config file; TODO: Change to some other form

    '''

    if args is None:
        args = sys.argv
    
    #with open("/home/bram/rospump/src/vision/vision/config.txt", 'r') as file:
    #    config_dict = {}
    #    for line in file:
    #        if line[0] != '#':  #ignores comments
    #            line = line.strip('\n')
    #            line = line.split()
    #            for elem in line:
    #                if elem.isdigit():
    #                    value = int(elem)                   #MAKE SURE NO FLOATS ARE NEEDED FOR VALUES IN SETTINGS
    #                elif elem != '=':    #ignores the = sign
    #                    identifier = elem
    #            config_dict[identifier] = value
    #hsv_min = (config_dict['hmin'],config_dict['smin'],config_dict['vmin'])
    #hsv_max = (config_dict['hmax'],config_dict['smax'],config_dict['vmax'])

    hmin = 145
    smin = 0
    vmin = 0
    hmax = 180
    smax = 255
    vmax = 255

    hsv_min = (hmin,smin,vmin)
    hsv_max = (hmax,smax,vmax)

    blur =  5 # config_dict['blur']

    #--- detection window respect to camera frame in [x_min, y_min, x_max, y_max] adimensional (0 to 1)
    x_min   = 0.4266
    x_max   = 0.6297
    y_min   = 0.0979
    y_max   = 0.3979

    detection_window = [x_min, y_min, x_max, y_max]

    params = cv2.SimpleBlobDetector_Params()

    # Change thresholds
    params.minThreshold = 0;
    params.maxThreshold = 100;
     
    # Filter by Area.
    params.filterByArea = True
    params.minArea = 20
    params.maxArea = 20000
     
    # Filter by Circularity
    params.filterByCircularity = True
    params.minCircularity = 0.1
     
    # Filter by Convexity
    params.filterByConvexity = True
    params.minConvexity = 0.2
     
    # Filter by Inertia
    params.filterByInertia = True
    params.minInertiaRatio = 0.7   

    rclpy.init(args=args)

    drop_detector = DropletDetector(hsv_min, hsv_max, blur, params, detection_window)
    
    rclpy.spin(drop_detector)

    drop_detector.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()



