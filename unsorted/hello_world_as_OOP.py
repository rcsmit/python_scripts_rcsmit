# Define a class for a greeting
class Greeting:
    # Define the constructor
    def __init__(self, message):
        self.message = message

    # Define a method to print the greeting
    def print_message(self):
        print(self.message)

# Create two instances of the Greeting class
hello_world = Greeting("Hello World")
hello_earth = Greeting("Hello Earth")

# Print the messages
hello_world.print_message()
hello_earth.print_message()
