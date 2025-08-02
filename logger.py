# filename: logger.py
import datetime

class Logger:
    """
    คลาสสำหรับจัดการการแสดงผล Log ทั้งหมดให้สวยงามและเข้าใจง่าย
    ใช้ static methods เพื่อให้สามารถเรียกใช้ได้จากทุกที่โดยไม่ต้องสร้าง object
    """
    EMOJI_MAP = {
        "AI_DECISION": "🧠",
        "AI_ACTION": "⚡️",
        "AI_REFLEX": "🩹",
        "EMERGENCY_ACTION": "💀", # เพิ่ม Event สำหรับการกระทำขั้นรุนแรง
        "SUCCESS": "✅",
        "FAILURE": "❌",
        "INFO": "ℹ️",
        "USER": "🧑‍💻",
        "SCENARIO": "🔥",
        "LEARNING_CYCLE": "📚"
    }

    @staticmethod
    def _get_timestamp():
        return datetime.datetime.now().strftime("%H:%M:%S")

    @staticmethod
    def info(message):
        print(f"[{Logger._get_timestamp()}] {Logger.EMOJI_MAP['INFO']} {message}")

    @staticmethod
    def user_action(message):
        print(f"[{Logger._get_timestamp()}] {Logger.EMOJI_MAP['USER']} {message}")
        
    @staticmethod
    def scenario(message):
        print(f"[{Logger._get_timestamp()}] {Logger.EMOJI_MAP['SCENARIO']} {message}")

    @staticmethod
    def action(message):
        print(f"  [{Logger._get_timestamp()}] {Logger.EMOJI_MAP['AI_ACTION']} {message}")

    @staticmethod
    def log_ai_event(event, details):
        """
        แปลง Event และ Details ของ AI ให้เป็นประโยคที่มนุษย์อ่านเข้าใจ
        """
        timestamp = Logger._get_timestamp()
        msg = ""

        if event.name == "STRATEGY_APPLIED":
            strategy = details.get('new_strategy', 'UNKNOWN').replace("_", " ")
            reason = details.get('reason', 'no reason specified')
            score = details.get('score', 0)
            msg = f"{Logger.EMOJI_MAP['AI_DECISION']} Strategy set to {strategy} (Score: {score:.0f}). Reason: {reason}"
        
        elif event.name == "TACTICAL_BOOST":
            reason = details.get('reason', 'High CPU load expected')
            msg = f"{Logger.EMOJI_MAP['AI_DECISION']} Tactical Boost: Proactively managing resources. Reason: {reason}"

        elif event.name == "REFLEX_TRIGGERED":
            reason = details.get('reason', 'System critical')
            msg = f"{Logger.EMOJI_MAP['AI_REFLEX']} Reflex Action Triggered! Reason: {reason}"
        
        elif event.name == "EMERGENCY_ACTION":
            action = details.get('action', 'unspecified action')
            reason = details.get('reason', 'no reason specified')
            msg = f"{Logger.EMOJI_MAP['EMERGENCY_ACTION']} Escalation! {action}. Reason: {reason}"
            
        elif event.name == "ACTION_SUCCESS":
            action = details.get('action', 'unspecified action')
            msg = f"  {Logger.EMOJI_MAP['SUCCESS']} Action '{action}' executed successfully."
            
        elif event.name == "ACTION_FAIL":
            action = details.get('action', 'unspecified action')
            error = details.get('error', 'unknown error')
            msg = f"  {Logger.EMOJI_MAP['FAILURE']} Action '{action}' failed! Error: {error}"

        elif event.name == "APP_CRASH":
            reason = details.get('reason', 'Unknown critical failure')
            msg = f"{Logger.EMOJI_MAP['FAILURE']} CRITICAL ERROR: {reason}"
        
        elif event.name == "LEARNING_CYCLE":
            adjustments = details.get('adjustments', 'No adjustments made.')
            msg = f"{Logger.EMOJI_MAP['LEARNING_CYCLE']} Learning cycle: Analyzing performance... Adjustments: {adjustments}"

        else:
            msg = f"{event.name}: {details}"

        print(f"[{timestamp}] {msg}")