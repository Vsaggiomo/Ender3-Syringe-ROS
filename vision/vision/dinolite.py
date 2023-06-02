
import rclpy
import cv2

from rclpy.node             import Node
from cv_bridge              import CvBridge, CvBridgeError
from sensor_msgs.msg        import Image


class DinoliteMicroscope(Node):

    def __init__(self):
        super().__init__('dinolite_node')
        self.publisher = self.create_publisher(Image, '/image_raw', 1)
        self.bridge = CvBridge()
        timer_period = 0.1 #seconds
        self.timer = self.create_timer(timer_period, self.capture)

        self.cam = cv2.VideoCapture(0)       #TODO: Make sure to check device number, otherwise read from some settings and find the device

    def capture(self):
        
        ret, image = self.cam.read()
        cv2.imshow("image" , image)
        if ret:
            #publish the image
            #uses CvBridge to convert cv_image to ROS message
            self.publisher.publish(self.bridge.cv2_to_imgmsg(image, "bgr8"))

        self.get_logger().info('Publishing images')
            

def main(args=None):
    rclpy.init(args=args)

    dinolite_node = DinoliteMicroscope()

    rclpy.spin(dinolite_node)

    # Destroy the node explicitly

    dinolite_node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
