class CommonParameters:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

def calculate_volume(common_params):
    print (x)
    print (common_params.x)
    volume = common_params.x * common_params.y * common_params.z
    return volume

def calculate_surface_area(common_params):
    surface_area = 2 * (common_params.x * common_params.y + common_params.x * common_params.z + common_params.y * common_params.z)
    return surface_area

def main():
    # create an instance of the CommonParameters class with the common parameters
    common_params = CommonParameters(x=2, y=3, z=4)

    # call the calculate_volume function with the common parameters
    volume = calculate_volume(common_params)
    print("Volume:", volume)

    # call the calculate_surface_area function with the common parameters
    surface_area = calculate_surface_area(common_params)
    print("Surface Area:", surface_area)


main()