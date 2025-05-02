from tdmclient import ClientAsync 
import time

class EasyThymio:
    def __init__(self):
        self.client = ClientAsync()
        self.__aseba_code = ""
        self.__sensor_value = None
        self.sound_system(0)

    def stop(self):
        self.leds_top(0, 0, 0)
        self.wheels(0, 0)
        self.sound_system(1)
        self.client.disconnect()

    def on_variables_changed(self, node, variables):
        try:
            self.__data = variables[self.__sensor_name]
        except KeyError:
            pass  

    @property
    def button_backward(self):
        self.run_command(self.sensors)
        return self.__sensor_value.button.backward

    @property
    def button_center(self):
        self.run_command(self.sensors)
        return self.__sensor_value.button.center
    
    @property
    def button_forward(self):
        self.run_command(self.sensors)
        return self.__sensor_value.button.forward
    
    @property
    def button_left(self):
        self.run_command(self.sensors)
        return self.__sensor_value.button.left
    
    @property
    def button_right(self):
        self.run_command(self.sensors)
        return self.__sensor_value.button.right

    @property
    def prox_horizontal(self):
        self.run_command(self.sensors)
        return self.__sensor_value.prox.horizontal

    @property
    def prox_ground(self):
        self.run_command(self.sensors)
        return self.__sensor_value.prox.ground

    @property
    def prox_ground_ambiant(self):
        self.run_command(self.sensors)
        return self.__sensor_value.prox.ground.ambiant
    
    @property
    def prox_ground_delta(self):
        self.run_command(self.sensors)
        return self.__sensor_value.prox.ground.delta    
    
    @property
    def prox_ground_reflected(self):
        self.run_command(self.sensors)
        return self.__sensor_value.prox.ground.reflected

    @property
    def acc(self):
        self.run_command(self.sensors)
        return self.__sensor_value.acc
        
    @property
    def temperature(self):
        self.run_command(self.sensors)
        return self.__sensor_value.temperature

    async def sensors(self):
        with await self.client.lock() as node:
            await node.wait_for_variables()
            self.__sensor_value = node.v

    async def actuators(self):
        with await self.client.lock() as node:
                try:
                    error = await node.compile(self.__aseba_code)
                    if error is not None:
                        print(f"Compilation error: {error['error_msg']}")
                    else:
                        await node.watch(events=True)
                        error = await node.run()
                        if error is not None:
                            print(f"Error {error['error_code']}")
                except ValueError:
                    print("Unexpected value")
                #self.client.process_waiting_messages()

    def run_command(self, type):
        self.client.run_async_program(type)
        print(f"Running {self.__aseba_code}")

    def leds_circle(self, br0, br1, br2, br3, br4, br5, br6, br7):
        self.__aseba_code = f"call leds.circle({br0},{br1},{br2},{br3},{br4},{br5},{br6},{br7})"
        self.run_command(self.actuators)

    def leds_top(self, red, green, blue):
        self.__aseba_code = f"call leds.top({red},{green},{blue})"
        self.run_command(self.actuators)

    def leds_bottom_right(self, red, green, blue):
        self.__aseba_code = f"call leds.bottom.right({red},{green},{blue})"
        self.run_command(self.actuators)

    def leds_bottom_left(self, red, green, blue):
        self.__aseba_code = f"call leds.bottom.left({red},{green},{blue})"
        self.run_command(self.actuators)

    def leds_buttons(self, br0, br1, br2, br3):
        self.__aseba_code = f"call leds.buttons({br0},{br1},{br2},{br3})"
        self.run_command(self.actuators)

    def leds_leds_prox_h(self, br0, br1, br2, br3, br4, br5, br6, br7):
        self.__aseba_code = f"call leds.leds_prox_h({br0},{br1},{br2},{br3},{br4},{br5},{br6},{br7})"
        self.run_command(self.actuators)

    def leds_leds_prox_v(self, br0, br1):
        self.__aseba_code = f"call leds.leds_prox_v({br0},{br1})"
        self.run_command(self.actuators)

    def leds_rc(self, br):
        self.__aseba_code = f"call leds.rc({br})"
        self.run_command(self.actuators)

    def leds_sound(self, br):
        self.__aseba_code = f"call leds.sound({br})"
        self.run_command(self.actuators)

    def leds_temperature(self, r, g):
        self.__aseba_code = f"call leds.temperature({r},{g})"
        self.run_command(self.actuators)

    def sound_system(self, sound_id):
        self.__aseba_code = f"call sound.system({sound_id})"
        self.run_command(self.actuators)

    def sound_duration(self, sound_id, duration):
        self.__aseba_code = f"call sound.duration({sound_id},{duration})"
        self.run_command(self.actuators)

    def sound_record(self, sound_id):
        self.__aseba_code = f"call sound.record({sound_id})"
        self.run_command(self.actuators)

    def sound_play(self, sound_id):
        self.__aseba_code = f"call sound.play({sound_id})"
        self.run_command(self.actuators)

    def sound_replay(self, sound_id):
        self.__aseba_code = f"call sound.replay({sound_id})"
        self.run_command(self.actuators)



    def wheels(self, left, right):
        self.__aseba_code = f"motor.left.target={left}\nmotor.right.target={right}"
        self.run_command(self.actuators)

if __name__ == "__main__":
    et = EasyThymio()
    print(et.prox_horizontal[2])
    print(et.temperature)
    print(et.prox_ground.delta[0], et.prox_ground.delta[1])
    print(et.acc[0], et.acc[1], et.acc[2])
    while True:
        print(et.button_backward)
        if et.button_backward:
            break
        time.sleep(0.5)
    et.stop()