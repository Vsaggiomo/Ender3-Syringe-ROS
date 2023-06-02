import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point
from std_msgs.msg import Float64, String
import time


class PIDControllerNode(Node):
    def __init__(self):
        super().__init__('pid_controller')
        self.get_logger().info("PID node initialized")

        # Initialize PID controller with some parameters
        self.Kp = 0.01  # Proportional gain
        self.Ki = 0.0  # Integral gain
        self.Kd = 0.0  # Derivative gain
        self.min_output = 0.15  # Minimum output value
        self.max_output = 2.0  # Maximum output value
        self.integral = 0  # Integral term
        self.last_error = 0  # Last error value
        self.last_time = self.get_clock().now()  # Last time the callback was called
        self.flow_speed = 0  # Flow speed value
        self.wanted_width = 80  # Desired width of the object to be tracked.                   #TODO: Change to read from settings instead of hardcoded
        if self.wanted_width <= 0:
            self.wanted_width = 0
        if self.wanted_width >= 200:
            self.wanted_width = 200
    
        self.start_time = None
        self.droplet_sizes = []
        self.secs_per_update = 95  # Time interval for updating the average droplet size
        self.droplet_update_interval = 10  # Time interval for recording droplet sizes

        # Create a subscription to the flow speed topic
        self.flow_speed_subscription = self.create_subscription(
            Float64,  # Data type of the message received
            'continuous_flow',  # Topic name
            self.flow_speed_callback,  # Callback function to handle the received message
            1)  # QoS settings

        # Create a subscription to the droplet size
        self.droplet_subscription = self.create_subscription(
            Float64,  # Data type of the message received
            'droplet_size',  # Topic name
            self.callback,  # Callback function to handle the received message
            1)  # QoS settings

        # Create a publisher for the control signal
        self.publisher = self.create_publisher(
            Float64,  # Data type of the message to be published
            'control_signal_topic',  # Topic name
            1)  # QoS settings
        
        self.subscription = self.create_subscription(
            String,   # Data type of the message to be published
            '/keyboard_input',  # Topic name
            self.keyboard_input_callback,   # Callback function to handle the received message
            1)  # QoS settings

        
    def flow_speed_callback(self, msg):
        self.flow_speed = msg.data
       
    def keyboard_input_callback(self,data): #function to change wanted width during experiment
        # get the pressed key
        key = data.data
        
        if key == 'c':
            self.wanted_width = 100

    def callback(self, msg):
        if self.start_time is None:
            self.start_time = time.time()

        current_time = time.time()
        elapsed_time = current_time - self.start_time

        if elapsed_time >= self.secs_per_update - self.droplet_update_interval:
            # Record the droplet size during the specified interval
            self.droplet_sizes.append(msg.data)
            self.get_logger().info("Measuring droplet sizes")

            if elapsed_time >= self.secs_per_update:
                # Calculate the average droplet size from the recorded sizes
                average_size = sum(self.droplet_sizes) / len(self.droplet_sizes)

                # Calculate the elapsed time since the last update
                now = self.get_clock().now()
                dt = (now - self.last_time).nanoseconds / 1e9

                # Calculate the error between the current position and the new reference
                error = self.wanted_width - average_size

                # Calculate the proportional term
                p = self.Kp * error * -1        #-1 due to since width is inversely related to speed, same for I and D term

                # Calculate the integral term
                self.integral += error * dt * -1
                i = self.Ki * self.integral

                # Calculate the derivative term
                derivative = ((error - self.last_error) / dt ) *-1
                d = self.Kd * derivative

                # Calculate the control signal as the sum of the three terms
                control_signal = self.flow_speed + p + i + d

                # Limit the control signal to the specified range
                control_signal = max(control_signal, self.min_output)
                control_signal = min(control_signal, self.max_output)
                message = str(control_signal)
                self.get_logger().info("New feedback rate " + message)
     

                # Publish the control signal as a Float64 message
                control_signal_msg = Float64()
                control_signal_msg.data = float(control_signal)
                self.publisher.publish(control_signal_msg)
                self.flow_speed = control_signal

                # Reset the droplet sizes list and update the start time
                self.droplet_sizes = []
                self.start_time = current_time

                # Update the last error and time for the next iteration
                self.last_error = error
                self.last_time = now
                
                # Update the secs_per_update to accomodate the new command
                self.secs_per_update = (control_signal / 0.1) * 33


def main(args=None):
    rclpy.init(args=args)

    pid_controller = PIDControllerNode()

    rclpy.spin(pid_controller)

    pid_controller.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
