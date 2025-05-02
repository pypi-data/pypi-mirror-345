from pyeasythymio import EasyThymio

robot = EasyThymio()
robot.wheels(50, 50)
robot.sleep(5)
robot.stop()
