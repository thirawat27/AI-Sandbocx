# filename: isolated_agent.py
import time, enum, statistics, os
from logger import Logger

class Event(enum.Enum):
    STRATEGY_APPLIED="กลยุทธ์ใหม่"; TACTICAL_BOOST="เสริมสมรรถนะเชิงรุก"; REFLEX_TRIGGERED="ตอบสนองฉับพลัน"
    ACTION_SUCCESS="ปฏิบัติการสำเร็จ"; ACTION_FAIL="ปฏิบัติการล้มเหลว"; LEARNING_CYCLE="ประมวลผลการเรียนรู้"
    APP_CRASH="ข้อผิดพลาดร้ายแรง"; EMERGENCY_ACTION="ปฏิบัติการฉุกเฉิน"

class Strategy(enum.Enum):
    DEFAULT="DEFAULT"; WORKSTATION="WORKSTATION"; GAMING="GAMING"; POWER_SAVE="POWER_SAVE"

class PanyarinNeuralAI:
    def __init__(self, psutil_mock, subprocess_mock):
        self.psutil = psutil_mock; self.subprocess = subprocess_mock; self.current_strategy = Strategy.DEFAULT
        self.active_optimizations = {}; self.cpu_count = self.psutil.cpu_count() or 1
        self.last_trigger_reason = "Initial State"; self.model, self.encoder, self.model_score = self._load_model()
        self.tick_counter = 0
        self.failure_tracker = {} # ติดตามความล้มเหลวของ Action
        self.performance_history = [] # เก็บประวัติประสิทธิภาพเพื่อการเรียนรู้
        
        # น้ำหนักเริ่มต้นสำหรับแต่ละกลยุทธ์ (AI จะปรับค่าเหล่านี้เอง)
        self.strategy_weights = {
            Strategy.GAMING: 1.0, Strategy.WORKSTATION: 1.0,
            Strategy.POWER_SAVE: 1.0, Strategy.DEFAULT: 1.0
        }
        
        Logger.info("Panyarin AI Agent Core v2.0 (Adaptive) initialized.")

    def _load_model(self):
        Logger.info("Simulation mode: Neural Network model is not loaded.")
        return "SimulatedModel", "SimulatedEncoder", 0.85 

    def get_system_snapshot(self):
        mem = self.psutil.virtual_memory()
        return {
            "timestamp": time.time(),
            "cpu_percent": self.psutil.cpu_percent(),
            "mem_percent": mem.percent,
            "running_apps": set(self.psutil.system_state['running_apps'].keys()),
            "io_wait": self.psutil.system_state['io_wait'] # ดึงข้อมูลใหม่
        }

    def strategic_assessment(self, snapshot):
        apps = snapshot["running_apps"]; cpu = snapshot["cpu_percent"]; io_wait = snapshot["io_wait"]
        scores = {s: 0 for s in Strategy}
        
        scores[Strategy.DEFAULT] = 10
        if any(app in {'steam', 'lutris'} for app in apps): scores[Strategy.GAMING] += 60
        if 'obs' in apps: scores[Strategy.GAMING] += 20; scores[Strategy.WORKSTATION] += 20
        if any(app in {'kdenlive', 'blender'} for app in apps): scores[Strategy.WORKSTATION] += 50
        if cpu > 75: scores[Strategy.GAMING] += 15; scores[Strategy.WORKSTATION] += 15
        if cpu > 50: scores[Strategy.GAMING] += 10; scores[Strategy.WORKSTATION] += 10
        if cpu < 20 and len(apps) < 5: scores[Strategy.POWER_SAVE] += 40
        
        # AI เรียนรู้ที่จะกลัว I/O Wait! มันจะลดคะแนนโหมด Performance ถ้า I/O สูง
        if io_wait > 20:
            scores[Strategy.GAMING] *= 0.5
            scores[Strategy.WORKSTATION] *= 0.7
            reason_io = f" (High I/O: {io_wait:.0f}%)"
        else:
            reason_io = ""

        # นำน้ำหนักที่ได้จากการเรียนรู้มาคูณกับคะแนน
        for strategy in scores:
            scores[strategy] *= self.strategy_weights[strategy]

        new_strategy = max(scores, key=scores.get)
        
        reason_map = {
            Strategy.GAMING: "Gaming session", Strategy.WORKSTATION: "Workstation task",
            Strategy.POWER_SAVE: "Low system activity", Strategy.DEFAULT: "System idle"
        }
        reason = reason_map.get(new_strategy, "Complex assessment") + reason_io

        if new_strategy != self.current_strategy:
            self.current_strategy = new_strategy; self.last_trigger_reason = reason
            Logger.log_ai_event(Event.STRATEGY_APPLIED, {"new_strategy": self.current_strategy.name, "reason": self.last_trigger_reason, "score": scores[new_strategy]})
            self.apply_strategy()
        
        # บันทึกข้อมูลสำหรับ Learning Cycle
        self.performance_history.append({'strategy': self.current_strategy, 'cpu': cpu, 'io_wait': io_wait, 'failures': len(self.failure_tracker)})

    def apply_strategy(self):
        gov = "performance" if self.current_strategy in [Strategy.GAMING, Strategy.WORKSTATION] else "powersave" if self.current_strategy == Strategy.POWER_SAVE else "schedutil"
        self.perform_action("set_governor", {"governor": gov})

    def tactical_maneuver(self, snapshot):
        if snapshot['cpu_percent'] > 70:
            Logger.log_ai_event(Event.TACTICAL_BOOST, {"reason": f"High CPU Load ({snapshot['cpu_percent']:.0f}%) detected"})
            self.perform_action("renice_high_cpu", {}, duration=120)

    def reflexive_response(self, snapshot):
        if snapshot["mem_percent"] > 90:
            Logger.log_ai_event(Event.REFLEX_TRIGGERED, {"reason": f"Critical Memory Pressure ({snapshot['mem_percent']:.0f}%)"})
            # ตรวจสอบว่าเคยทำ drop_caches ล้มเหลวหรือไม่
            if "drop_caches" in self.failure_tracker and time.time() - self.failure_tracker["drop_caches"] < 30:
                Logger.log_ai_event(Event.EMERGENCY_ACTION, {"action": "Attempting to kill highest memory process", "reason": "drop_caches failed recently"})
                self.perform_action("kill_most_mem_proc", {})
            else:
                self.perform_action("drop_caches", {}, duration=15)

    def learning_cycle(self):
        if not self.performance_history: return
        
        # วิเคราะห์ข้อมูลย้อนหลัง
        avg_cpu = statistics.mean(p['cpu'] for p in self.performance_history)
        max_io = max(p['io_wait'] for p in self.performance_history)
        total_failures = sum(1 for p in self.performance_history if p['failures'] > 0)
        
        adjustments = []
        # ตรรกะการเรียนรู้แบบง่าย: ถ้าประสิทธิภาพโดยรวมแย่ ให้ลดความมั่นใจในกลยุทธ์ที่ใช้บ่อย
        if avg_cpu > 80 or max_io > 30 or total_failures > 1:
            strategy_counts = statistics.Counter(p['strategy'] for p in self.performance_history)
            most_used_strategy = strategy_counts.most_common(1)[0][0]
            
            # ลดน้ำหนักของกลยุทธ์ที่ใช้แล้วผลออกมาไม่ดี
            self.strategy_weights[most_used_strategy] *= 0.95
            adjustments.append(f"Reduced weight for {most_used_strategy.name} due to poor performance (High CPU/IO/Failures)")
        else:
             # ถ้าผลงานดี ให้รางวัลกลยุทธ์ที่ใช้บ่อย
            strategy_counts = statistics.Counter(p['strategy'] for p in self.performance_history)
            most_used_strategy = strategy_counts.most_common(1)[0][0]
            self.strategy_weights[most_used_strategy] = min(1.2, self.strategy_weights[most_used_strategy] * 1.05)
            adjustments.append(f"Increased weight for {most_used_strategy.name} due to good performance")

        Logger.log_ai_event(Event.LEARNING_CYCLE, {"adjustments": " | ".join(adjustments) if adjustments else "No adjustments needed."})
        self.performance_history.clear() # เริ่มเก็บข้อมูลใหม่
        self.failure_tracker.clear()

    def perform_action(self, action_name, params, duration=60):
        if action_name in self.active_optimizations and time.time() < self.active_optimizations[action_name]['expiry']: return
        try:
            # subprocess.run ตอนนี้สามารถโยน Exception ได้
            self.subprocess.run(action_name, params)
            Logger.log_ai_event(Event.ACTION_SUCCESS, {"action": action_name, "params": params})
            self.active_optimizations[action_name] = {'expiry': time.time() + duration}
        except Exception as e:
            self.failure_tracker[action_name] = time.time() # บันทึกความล้มเหลว
            Logger.log_ai_event(Event.ACTION_FAIL, {"action": action_name, "error": str(e)})

    def main_loop_step(self):
        try:
            self.tick_counter += 1
            snapshot = self.get_system_snapshot()
            self.strategic_assessment(snapshot)
            self.tactical_maneuver(snapshot)
            self.reflexive_response(snapshot)
            if self.tick_counter % 10 == 0: # เรียนรู้ทุก 10 Ticks
                self.learning_cycle()
        except Exception as e:
            import traceback; Logger.log_ai_event(Event.APP_CRASH, {"reason": str(e), "traceback": traceback.format_exc()})