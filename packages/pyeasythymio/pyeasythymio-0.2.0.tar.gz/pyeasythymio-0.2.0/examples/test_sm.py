# Template BoundaryFollower

#from robotar import RobotAR
from pyeasythymio import EasyThymio

class StateMachine:
  def start(self):
    self.state = self.start_state

  def step(self, inp):
    ns, o = self.get_next_values(self.state, inp)
    self.state = ns
    return o

  def transduce(self, inp_list):
    output = []
    self.start()
    idk = 0
    while idx < len(inp_list) and not self.is_done():
      output.append(self.step(inp_list[idx]))
      idx += 1
    return output
  
  def start_state(self):
    pass

  def get_next_values(self, state, inp):
    pass

  def done(self, state):
    return False

  def is_done(self):
    return self.done(self.state)

class MyRobot(EasyThymio):
  def __init__(self, MySM):
    self.behaviour = MySM
    super().__init__()
  
  def run(self):
    self.behaviour.start()
    while not self.behaviour.is_done():
      self.update()
    self.stop()
      
  def update(self):
    output = self.behaviour.step(self)
    self.wheels(output[0], output[1])
 
class BoundaryFollower(StateMachine):
  start_state = 0
  def get_next_values(self, state, inp):
    left,right = inp.prox_ground.delta
    print(left, right)
    if inp.button_center == 1:
        return 'done', (0,0)
    next_state = state
    output = (50, 50)
    return next_state, output

  def done(self, state):
    return state == 'done'

sm = BoundaryFollower()   
robot = MyRobot(sm)
try:
    robot.run()
except:
    robot.stop()

