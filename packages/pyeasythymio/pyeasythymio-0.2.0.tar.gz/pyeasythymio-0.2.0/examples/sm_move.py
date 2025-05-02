from pyeasythymio import ThymioSM

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
robot = ThymioSM(sm)
try:
    robot.run()
except:
    robot.stop()

