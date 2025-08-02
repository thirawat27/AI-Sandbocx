# filename: simulation_env.py
import random, time
from logger import Logger

class MockSubprocess:
    def __init__(self, system_state): self.system_state = system_state
    def run(self, action_name, params):
        cmd_str = f"Action: {action_name} with params: {params}"
        Logger.action(f"Attempting to execute: '{cmd_str}'")
        
        # ทำให้ Action มีโอกาสล้มเหลวเมื่อระบบเครียด
        if self.system_state['system_stress_factor'] > 1.2 and random.random() < 0.3:
            raise PermissionError("Action failed due to high system stress!")

        if action_name == "set_governor": self.system_state['governor'] = params['governor']
        elif action_name == "drop_caches":
            # ทำให้ drop_caches ได้ผลน้อยลงเมื่อ I/O สูง
            mem_reduction = 10 if self.system_state['io_wait'] < 15 else 3
            self.system_state['mem_percent'] = max(20.0, self.system_state['mem_percent'] - mem_reduction)
        elif action_name == "renice_high_cpu": pass # จำลองว่าสำเร็จ
        elif action_name == "kill_most_mem_proc":
            # หาโปรเซสที่ใช้ mem สูงสุด (ที่ไม่ใช่ process ระบบ) แล้วฆ่าทิ้ง
            apps = self.system_state['running_apps']
            mem_map = self.system_state['resource_map']
            user_apps = {name: data for name, data in apps.items() if name not in {'python3', 'cinnamon'}}
            if not user_apps: return
            
            app_to_kill = max(user_apps.keys(), key=lambda app: mem_map.get(app, {}).get('active', {}).get('mem', 0))
            Logger.action(f"Killing '{app_to_kill}' to free up memory.")
            apps.pop(app_to_kill, None)

class MockPsutil:
    def __init__(self, system_state):
        self.system_state = system_state; self.total_memory_gb = 16.0 
    def cpu_percent(self, percpu=False): return self.system_state['cpu_percent']
    def virtual_memory(self):
        class MockMem:
            def __init__(self, state, total_mem):
                self.percent = state['mem_percent']; self.total = total_mem * (1024**3); self.used = self.total * (self.percent / 100)
        return MockMem(self.system_state, self.total_memory_gb)
    def process_iter(self, attrs):
        # ... ไม่เปลี่ยนแปลงจากเวอร์ชันก่อน ...
        processes = []
        for app_name, app_data in self.system_state['running_apps'].items():
            class MockProcess:
                def __init__(self, name, state, resource_map): 
                    self.info = {'name': name, 'pid': random.randint(1000, 20000)}; self._state = state; self._resource_map = resource_map
                def cpu_percent(self):
                    res_map = self._resource_map.get(self.info['name'], {})
                    state_res = res_map.get(self._state, {'cpu': [1,0], 'mem': 1})
                    base_cpu, spike = state_res['cpu']
                    # เพิ่ม CPU Spike แบบสุ่ม
                    current_cpu = base_cpu + random.uniform(-2, 2)
                    if random.random() < 0.1: current_cpu += spike
                    return current_cpu
            processes.append(MockProcess(app_name, app_data['state'], self.system_state['resource_map']))
        return processes
    def cpu_count(self): return 8

class SimulationEnvironment:
    def __init__(self):
        # Resource Map: [base_cpu, spike_cpu], mem
        self.resource_map = {
            'cinnamon':   {'idle': {'cpu': [2, 0], 'mem': 5}}, 'python3':    {'idle': {'cpu': [1, 0], 'mem': 3}},
            'firefox':    {'idle': {'cpu': [5, 15], 'mem': 10}},
            'steam':      {'idle': {'cpu': [2, 10], 'mem': 8}, 'active': {'cpu': [40, 20], 'mem': 20}},
            'blender':    {'idle': {'cpu': [2, 5], 'mem': 12}, 'active': {'cpu': [80, 15], 'mem': 40}},
            'kdenlive':   {'idle': {'cpu': [4, 10], 'mem': 15}, 'active': {'cpu': [75, 20], 'mem': 35}},
            'obs':        {'idle': {'cpu': [8, 10], 'mem': 10}, 'active': {'cpu': [30, 25], 'mem': 18}},
        }
        self.state = {
            'cpu_percent': 5.0, 'mem_percent': 18.0, 
            'running_apps': {'python3': {'state': 'idle'}, 'cinnamon': {'state': 'idle'}}, 
            'governor': 'schedutil', 'resource_map': self.resource_map,
            'io_wait': 0.0, 'system_stress_factor': 1.0 # สถานะใหม่
        }
        self.psutil_mock = MockPsutil(self.state); self.subprocess_mock = MockSubprocess(self.state)
    
    def add_app(self, app_name, state='idle'): Logger.user_action(f"Launching '{app_name}'..."); self.state['running_apps'][app_name] = {'state': state}
    def remove_app(self, app_name): Logger.user_action(f"Closing '{app_name}'..."); self.state['running_apps'].pop(app_name, None)
    def set_app_state(self, app_name, new_state):
        if app_name in self.state['running_apps']: self.state['running_apps'][app_name]['state'] = new_state; Logger.user_action(f"App '{app_name}' state changed to '{new_state}'")
    def trigger_memory_stress(self, level=95.0): Logger.scenario(f"Memory pressure event triggered! Setting MEM to {level}%."); self.state['mem_percent'] = level
    def trigger_io_stress(self, level=40.0): Logger.scenario(f"I/O saturation event triggered! Setting I/O Wait to {level}%."); self.state['io_wait'] = level

    def update_system_load(self):
        potential_cpu = 0; base_mem = 0
        
        for app_name, app_data in self.state['running_apps'].items():
            app_state = app_data['state']; res = self.resource_map.get(app_name, {}).get(app_state, {'cpu': [1,0], 'mem': 1})
            base_cpu, spike = res['cpu']
            potential_cpu += base_cpu
            if random.random() < 0.1: potential_cpu += spike # Add spike to potential
            base_mem += res['mem']

        # System Thrashing Logic
        if potential_cpu > 100:
            self.state['system_stress_factor'] = (potential_cpu / 100.0)
            actual_cpu = 100 - (self.state['system_stress_factor'] - 1) * 10 # CPU ลดลงเพราะ Thrashing
            # I/O Wait เพิ่มขึ้นอย่างรวดเร็วเมื่อเกิด Thrashing
            self.state['io_wait'] = min(99.0, self.state['io_wait'] + self.state['system_stress_factor'] * 5)
        else:
            self.state['system_stress_factor'] = 1.0
            actual_cpu = potential_cpu
            # I/O Wait ลดลงช้าๆ
            self.state['io_wait'] = max(0.0, self.state['io_wait'] - 5)

        self.state['cpu_percent'] = min(99.9, actual_cpu + random.uniform(-2, 2))
        
        if self.state['mem_percent'] < 90:
             self.state['mem_percent'] = min(99.9, base_mem + random.uniform(-1, 1))