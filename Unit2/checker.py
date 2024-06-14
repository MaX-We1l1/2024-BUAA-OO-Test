from typing import Union, Dict, List
import re

NUM_ELEVS = 6
MAX_PEOPLE_NUM = 6
MAX_FLOOR = 11
MAX_REQS = 200
eps = 0.0000001


class Elev():
    def __init__(self, id) -> None:
        self.id = id
        self.num = 0
        self.current_floor = 1
        self.open = 0
        self.last_action_time = 0.0
        self.last_open_time = 0.0

        self.capacity = 6
        self.move_delay = 0.4
        self.reset_status = "none"
        self.reset_req = []
        self.reset_move = 0
        self.reset_accept_time = 0.0
        self.reset_begin_time = 0.0
        self.receive = {}
        self.passengers = {}

        self.transFloor = 0
        self.sub_type = None

    def idStr(self) -> str:
        if self.sub_type is None:
            return str(self.id)
        else:
            return str(self.id) + "-" + self.sub_type

    def getPartnerId(self) -> int:
        if self.id > NUM_ELEVS:
            return self.id - NUM_ELEVS
        else:
            return self.id + NUM_ELEVS


def input_check(inputfile: str) -> dict[int, list[int]]:
    with open(inputfile) as f:
        lines = f.readlines()
    waiters = {}
    for i in range(len(lines)):
        line = lines[i]
        match = re.search(r'\[(.*?)]', line)
        if match:
            line = line.replace(match.group(0), '')
        else:
            continue
        parts = line.split('-')
        first_element = parts[0]
        # reset请求
        if first_element == 'RESET':
            continue

        waiter_id = int(parts[0])
        from_floor = int(parts[2])
        goal_floor = int(parts[4])
        waiters[waiter_id] = [0, from_floor, goal_floor, 0]  # 记录乘客上电梯情况，出发楼层，目标楼层,结束位
    return waiters


def output_check(outputfile: str) -> Union[list, str]:  # 参考了高鹏飞同学的处理
    with open(outputfile) as f:
        lines = f.readlines()
    actions = []
    for i in range(len(lines)):
        line = lines[i]
        matcher = re.match(r'\[\s*(\d+\.\d+)\]([A-Z_]+).*', line)
        try:
            if matcher.group(2) in ['ARRIVE', 'OPEN', 'CLOSE', 'RECEIVE']:
                matcher = re.match(r'\[\s*(\d+\.\d+)\]([A-Z_]+)-(\d+)-(\d+(?:-A|-B)?)', line)
                actions.append(
                    [float(matcher.group(1)), matcher.group(2), int(matcher.group(3)), matcher.group(4)])
            elif matcher.group(2) in ['IN', 'OUT']:
                matcher = re.match(r'\[\s*(\d+\.\d+)\]([A-Z_]+)-(\d+)-(\d+)-(\d+(?:-A|-B)?)', line)
                actions.append([float(matcher.group(1)), matcher.group(2), int(matcher.group(3)), int(matcher.group(4)),
                                matcher.group(5)])
            elif matcher.group(2) == 'RESET_ACCEPT':
                if line.count('-') == 3:
                    matcher = re.match(r'\[\s*(\d+\.\d+)\]([A-Z_]+)-(\d+)-(\d+)-(\d+\.\d+)', line)
                    actions.append([float(matcher.group(1)), matcher.group(2), matcher.group(3), int(matcher.group(4)),
                                    float(matcher.group(5))])
                else:
                    matcher = re.match(r'\[\s*(\d+\.\d+)\]([A-Z_]+)-(\d+)-(\d+)-(\d+)-(\d+\.\d+)', line)
                    actions.append([float(matcher.group(1)), matcher.group(2), matcher.group(3), int(matcher.group(4)),
                                    int(matcher.group(5)), float(matcher.group(6))])
            elif matcher.group(2) in ['RESET_BEGIN', 'RESET_END']:
                matcher = re.match(r'\[\s*(\d+\.\d+)\]([A-Z_]+)-(\d+(?:-A|-B)?)', line)
                actions.append([float(matcher.group(1)), matcher.group(2), matcher.group(3)])
            else:
                return '第' + str(i + 1) + '行输出格式错误'
        except:
            return '第' + str(i + 1) + '行输出格式错误'
    return actions


def check(waiters, actions):
    elevators = {}
    for i in range(1, 7):
        elevators[str(i)] = Elev(i)
    received_waiters = {}
    cur_time = 0

    for i in range(0, len(actions)):
        action = actions[i]
        tmp_id = ''
        if action[0] < cur_time:
            return '时光回溯了兄弟'  #
        cur_time = action[0]

        if action[1] in ['RESET_ACCEPT', 'RESET_BEGIN', 'RESET_END']:
            tmp_id = action[2]
        elif action[1] in ['RECEIVE', 'ARRIVE', 'OPEN', 'CLOSE']:
            tmp_id = action[3]
        elif action[1] in ['IN', 'OUT']:
            tmp_id = action[4]
        if tmp_id not in elevators.keys():
            return '第' + str(action[0]) + '秒电梯' + tmp_id + '不存在'

        if action[1] == 'RESET_ACCEPT':
            if elevators[tmp_id].reset_status != "none":
                return '第' + str(action[0]) + '秒电梯' + str(action[2]) + '还未结束上次重置'
            elevators[tmp_id].reset_status = "accepted"
            elevators[tmp_id].reset_accept_time = cur_time
            elevators[tmp_id].reset_req.append(action)
            elevators[tmp_id].reset_move = 0
        elif action[1] == 'RESET_BEGIN':
            if elevators[tmp_id].reset_status != "accepted":
                return '第' + str(action[0]) + '秒电梯' + str(action[2]) + '没收到重置信号'
            elif elevators[tmp_id].num > 0:
                return '第' + str(action[0]) + '秒电梯' + str(action[2]) + '内部还有人'
            elif elevators[tmp_id].open == 1:
                return '第' + str(action[0]) + '秒电梯' + str(action[2]) + '还没关门就开始reset'
            elif elevators[tmp_id].reset_move > 2:
                return '第' + str(action[0]) + '秒电梯' + str(action[2]) + '没在2次移动内重置'
            elevators[tmp_id].reset_status = "begin"
            elevators[tmp_id].reset_req.append(action)
            elevators[tmp_id].reset_begin_time = action[0]
            for pid in elevators[tmp_id].receive:  # 取消receive约束
                waiters[pid] = elevators[action[2]].receive[pid]
                received_waiters.pop(pid)
            elevators[tmp_id].receive.clear()
        elif action[1] == 'RESET_END':
            if elevators[tmp_id].reset_status != "begin":
                return '第' + str(action[0]) + '秒电梯' + str(action[2]) + '不能在这个时候重置'
            elif action[0] - elevators[tmp_id].reset_begin_time > 5 + 0.01:
                return '第' + str(action[0]) + '秒电梯' + str(action[2]) + 'reset 太慢'
            elif action[0] - elevators[action[2]].reset_begin_time < 1.2 - 0.01:
                return '第' + str(action[0]) + '秒电梯' + str(action[2]) + 'reset 太快'
            if elevators[action[2]].reset_req[0].__len__() != 5:
                # double
                elevators[action[2]].reset_status = "none"
                elevators[action[2]].last_action_time = elevators[action[2]].reset_req[0][0]
                elevators[action[2]].move_delay = elevators[action[2]].reset_req[0][4]
                elevators[action[2]].capacity = elevators[action[2]].reset_req[0][3]
                elevators[action[2] + '-A'] = Elev(action[2])
                elevators[action[2] + '-A'].capacity = elevators[action[2]].reset_req[0][4]
                elevators[action[2] + '-A'].move_delay = elevators[action[2]].reset_req[0][5]
                elevators[action[2] + '-A'].last_action_time = elevators[action[2]].reset_req[0][0]
                elevators[action[2] + '-B'] = Elev(action[2])
                elevators[action[2] + '-B'].capacity = elevators[action[2]].reset_req[0][4]
                elevators[action[2] + '-B'].move_delay = elevators[action[2]].reset_req[0][5]
                elevators[action[2] + '-B'].last_action_time = elevators[action[2]].reset_req[0][0]
                elevators[action[2] + '-A'].transFloor = elevators[action[2] + '-B'].transFloor = \
                    elevators[action[2]].reset_req[0][3]
                elevators[action[2] + '-A'].current_floor = elevators[action[2] + '-A'].transFloor - 1
                elevators[action[2] + '-B'].current_floor = elevators[action[2] + '-B'].transFloor + 1
                elevators.pop(action[2])
            else:
                elevators[action[2]].capacity = elevators[action[2]].reset_req[0][3]
                elevators[action[2]].move_delay = elevators[action[2]].reset_req[0][4]
                elevators[action[2]].reset_status = "none"
                elevators[action[2]].last_action_time = elevators[action[2]].reset_req[0][0]
                elevators[action[2]].reset_req = []
        elif action[1] == 'ARRIVE':
            elev = elevators[action[3]]
            if elev.current_floor == action[2]:
                return '第' + str(action[0]) + '秒电梯' + str(action[3]) + '没有发生位置移动'
            if action[2] > 11 or action[2] < 1:
                return '第' + str(action[0]) + '秒电梯' + str(action[3]) + '不在正确楼层范围'
            if action[3] == (action[3].count('A') == 1 and action[2] > elevators[action[3]].transFloor) or \
                    (action[3].count('B') == 1 and action[2] < elevators[action[3]].transFloor):
                return '第' + str(action[0]) + '秒电梯' + action[3] + '不知道怎么逾越了另一台双轿厢'
            elif action[0] - elevators[action[3]].last_action_time < elevators[action[3]].move_delay - 0.02:
                return '第' + str(action[0]) + '秒电梯' + str(action[3]) + '超速了'  # 覆盖了双轿厢的初始化后的移动
            elif elevators[action[3]].open == 1:
                return '第' + str(action[0]) + '秒电梯' + str(action[3]) + '还没关门就移动'
            elif elevators[action[3]].num == 0 and elevators[action[3]].receive == []:
                if action[3].count('-') > 0 and elevators[action[3]].current_floor == elevators[action[3]].transFloor:
                    pass
                else:
                    return '第' + str(action[0]) + '秒电梯' + str(action[3]) + '没人就移动'
            elif elevators[action[3]].reset_status == "begin":
                return '第' + str(action[0]) + '秒电梯' + str(action[3]) + '重置期间禁止移动'
            elif abs(elevators[action[3]].current_floor - action[2]) != 1:
                return '第' + str(action[0]) + '秒电梯' + str(action[3]) + '移动超过1层'
            elif action[3].count('A') == 1 and elevators[action[3]].transFloor == action[2] \
                    and elevators[action[3].replace('A', 'B')].current_floor == action[2]:
                return '第' + str(action[0]) + '秒电梯' + str(action[3]) + '撞了'
            elif action[3].count('B') == 1 and elevators[action[3]].transFloor == action[2] \
                    and elevators[action[3].replace('B', 'A')].current_floor == action[2]:
                return '第' + str(action[0]) + '秒电梯' + str(action[3]) + '撞了'
            if elev.reset_status == "accepted":
                elev.reset_move += 1
            elev.current_floor = action[2]
            elev.last_action_time = action[0]
        elif action[1] == 'RECEIVE':
            if action[2] in received_waiters.keys():
                return '第' + str(action[0]) + '秒电梯' + str(action[3]) + '乘客' + str(action[2]) + '被重复分配'
            elif elevators[action[3]].reset_status == "begin":
                return '第' + str(action[0]) + '秒电梯' + str(action[3]) + '重置期间禁止receive乘客'
            received_waiters[action[2]] = waiters[action[2]]
            elevators[action[3]].receive[action[2]] = waiters[action[2]]
            waiters.pop(action[2])
        elif action[1] == 'IN':
            if elevators[action[4]].reset_status == "begin":
                return '第' + str(action[0]) + '秒电梯' + str(action[4]) + '重置期间禁止进入'
            elif elevators[action[4]].current_floor != action[3]:
                return '第' + str(action[0]) + '秒电梯' + str(action[4]) + '人掉进电梯井了'
            elif elevators[action[4]].open == 0:
                return '第' + str(action[0]) + '秒电梯' + str(action[4]) + '人撞在门上面了'
            elif elevators[action[4]].num + 1 > elevators[action[4]].capacity:
                return '第' + str(action[0]) + '秒电梯' + str(action[4]) + '超载'
            elif action[2] not in elevators[action[4]].receive:
                return '第' + str(action[0]) + '秒电梯' + str(action[4]) + '乘客' + str(action[2]) + '未分配'
            elif received_waiters[action[2]][1] != action[3]:
                return '第' + str(action[0]) + '秒电梯' + str(action[4]) + '乘客' + str(action[2]) + '瞬移到别的楼层进电梯'
            elevators[action[4]].passengers[action[2]] = received_waiters[action[2]]
            elevators[action[4]].num += 1
            elevators[action[4]].passengers[action[2]] = received_waiters[action[2]]
        elif action[1] == 'OUT':
            if elevators[action[4]].reset_status == "begin":
                return '第' + str(action[0]) + '秒电梯' + str(action[4]) + '重置期间禁止出去'
            elif elevators[action[4]].current_floor != action[3]:
                return '第' + str(action[0]) + '秒电梯' + str(action[4]) + '人出来的楼层不对'
            elif elevators[action[4]].open == 0:
                return '第' + str(action[0]) + '秒电梯' + str(action[4]) + '还没开门就出去'
            elif action[2] not in elevators[action[4]].passengers.keys():
                return '第' + str(action[0]) + '秒电梯' + str(action[4]) + '乘客' + str(action[2]) + '不在电梯里'
            if elevators[action[4]].passengers[action[2]][2] != action[3]:
                waiters[action[2]] = elevators[action[4]].passengers[action[2]]
                waiters[action[2]][1] = action[3]
            elevators[action[4]].receive.pop(action[2])
            received_waiters.pop(action[2])
            elevators[action[4]].passengers.pop(action[2])
            elevators[action[4]].num -= 1
        elif action[1] == 'OPEN':
            if elevators[action[3]].reset_status == "begin":
                return '第' + str(action[0]) + '秒电梯' + str(action[3]) + '重置期间禁止开关门'
            elif elevators[action[3]].current_floor != action[2]:
                return '第' + str(action[0]) + '秒电梯' + str(action[3]) + '开门楼层与上次到达楼层不符'
            elif elevators[action[3]].open:
                return '第' + str(action[0]) + '秒电梯' + str(action[3]) + '门本来就是开着的'
            elevators[action[3]].open = 1
            elevators[action[3]].last_open_time = action[0]
            elevators[action[3]].last_action_time = action[0]
        elif action[1] == 'CLOSE':
            if elevators[action[3]].reset_status == "begin":
                return '第' + str(action[0]) + '秒电梯' + str(action[3]) + '重置期间禁止开关门'
            elif elevators[action[3]].current_floor != action[2]:
                return '第' + str(action[0]) + '秒电梯' + str(action[3]) + '关门楼层与上次到达楼层不符'
            elif elevators[action[3]].open == 0:
                return '第' + str(action[0]) + '秒电梯' + str(action[3]) + '还没开门就关门'
            elif action[0] - elevators[action[3]].last_open_time < 0.4 - 0.02:  # 有容错
                return '第' + str(action[0]) + '秒电梯' + str(action[3]) + '开关门时间过短'
            elevators[action[3]].open = 0
            elevators[action[3]].last_action_time = action[0]
    for i in elevators.items():
        if i[1].reset_status != "none":
            return '电梯' + i[0] + '还未结束重置'
        if i[1].passengers != {}:
            return '电梯' + i[0] + '还有乘客'
        if i[1].receive:
            return '电梯' + i[0] + '还有没送的乘客'
        if i[1].open:
            return '电梯' + i[0] + '还没关门'
    if received_waiters != {}:
        return '还有乘客没送完'
    return 'Accepted!'


if __name__ == '__main__':
    input = input_check('stdin.txt')
    # print(input)
    output = output_check('output.txt')
    # print(output)
    print(check(input, output))
