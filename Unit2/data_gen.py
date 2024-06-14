import random
import json
from pathlib import Path
from random import randint, uniform

NUM_ELEVS = 6
MAX_REQS = 70
MIN_TIME = 1
MAX_TIME = 30
MAX_FLOOR = 11
MOVE_DELAYS = [0.2, 0.3, 0.4, 0.5, 0.6]
CAPACITIES = [3, 4, 5, 6, 7, 8]

def gen_arange(n):
    li = []
    for i in range(1, n + 1):
        li.append(i)
    return li

ids = gen_arange(MAX_REQS)
req_for_elevs = [0] * NUM_ELEVS
avail_elevs = gen_arange(NUM_ELEVS)
floors = gen_arange(MAX_FLOOR)
last_reset_time = [-5.0] * (NUM_ELEVS + 1)
can_reset = gen_arange(NUM_ELEVS)

class DataGenerator:
    def __init__(self):
        global command_limit
        self.input_num = MAX_REQS
        self.last_reset_time = [0, 0, 0, 0, 0, 0]
        self.time_list = []
        self.customerId_list = ids
        self.inputs = []
        self.normalElevatorId = avail_elevs
        self.generate_data()


    def generate_time_list(self):
        time = 1
        for i in range(MAX_REQS):
            time += random.choice([0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0])
            self.time_list.append(round(time,1))

    def gen_floors(self):
        global floors
        from_floor = floors.pop(randint(0, len(floors) - 1))
        to_floor = floors.pop(randint(0, len(floors) - 1))
        floors.append(from_floor)
        floors.append(to_floor)
        return from_floor, to_floor

    def generate_normal_reset(self, elevatorId, index) -> str:
        capacity = random.choice(CAPACITIES)
        move_time = random.choice(MOVE_DELAYS)
        return f"[{self.time_list[index]}]RESET-Elevator-{elevatorId}-{capacity}-{move_time}"

    def generate_DC_reset(self, elevatorId, index) -> str:
        capacity = random.choice(CAPACITIES)
        move_time = random.choice(MOVE_DELAYS)
        transfer_floor = random.randint(3, 9)
        return f"[{self.time_list[index]}]RESET-DCElevator-{elevatorId}-{transfer_floor}-{capacity}-{move_time}"

    def generate_request(self, index) -> str:
        customerId = self.customerId_list[index]
        from_floor, to_floor = self.gen_floors()
        return f"[{self.time_list[index]}]{customerId}-FROM-{from_floor}-TO-{to_floor}"

    def generate_data(self):
        req_num = MAX_REQS
        self.generate_time_list()
        for i in range(req_num):
            if random.random() < 0.15:
                is_DC_reset = random.random() < 0.2
                temp_elevator_id_list = self.normalElevatorId.copy()
                while True:
                    if len(temp_elevator_id_list) == 0:
                        self.inputs.append(self.generate_request(i))
                        break
                    else:
                        index = random.choice(range(0, len(temp_elevator_id_list)))
                    elevator_id = temp_elevator_id_list.pop(index)
                    if self.time_list[i] - self.last_reset_time[elevator_id - 1] < 4:  # 如果与上一次重置的间隔小于4s
                        if len(temp_elevator_id_list) == 0:
                            self.inputs.append(self.generate_request(i))
                            break
                        else:
                            continue
                    else:
                        if is_DC_reset:
                            self.inputs.append(self.generate_DC_reset(elevator_id, i))
                            self.normalElevatorId.remove(elevator_id)
                        else:
                            self.inputs.append(self.generate_normal_reset(elevator_id, i))
                        self.last_reset_time[elevator_id - 1] = self.time_list[i]
                        break
            else:
                self.inputs.append(self.generate_request(i))
        target = Path('stdin.txt')
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
        with open('stdin.txt', 'w') as file:
            for input in self.inputs:
                file.write(input + '\n')



if __name__ == '__main__':
    dataGenerator = DataGenerator()

