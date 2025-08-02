# filename: main_simulator.py
import time
from simulation_env import SimulationEnvironment
from isolated_agent import PanyarinNeuralAI, Strategy # Import the modified AI

def print_dashboard(env, ai):
    """แสดงผลสถานะของระบบและ AI"""
    print(f"📊 SYSTEM STATE | CPU: {env.state['cpu_percent']:.1f}% | MEM: {env.state['mem_percent']:.1f}%")
    print(f"  Running Apps: {', '.join(sorted(list(env.state['running_apps'])))}")
    print(f"🤖 AI STATUS    | Strategy: {ai.current_strategy.name}")
    print("-" * 50)

def main():
    print("🚀 Initializing Panyarin AI Digital Sandbox...")
    
    # 1. สร้างห้องทดลองและ AI
    env = SimulationEnvironment()
    ai = PanyarinNeuralAI(
        psutil_mock=env.psutil_mock,
        subprocess_mock=env.subprocess_mock
    )

    print("✅ Simulation Ready. Starting main loop...\n")
    time.sleep(2)

    # 2. เริ่ม vòng lặp การจำลอง
    for tick in range(1, 1000): 
        print(f"\n--- Tick {tick} ---")

        # 3. กำหนดสถานการณ์ (Scenario Injection)
        if tick == 5:
            env.add_app('firefox')
        if tick == 10:
            env.add_app('steam') # <--- AI ควรจะเปลี่ยนเป็นโหมด GAMING
        if tick == 20:
            env.remove_app('steam') # <--- AI ควรจะกลับสู่โหมดปกติ
            env.add_app('blender')  # <--- AI ควรจะเปลี่ยนเป็นโหมด WORKSTATION
        if tick == 28:
            env.remove_app('blender')
            env.remove_app('firefox')

        # 4. ให้สภาพแวดล้อมและ AI ทำงาน 1 รอบ
        env.update_system_load()
        ai.main_loop_step()
        
        # 5. แสดงผลลัพธ์
        print_dashboard(env, ai)
        
        time.sleep(0.7) # หน่วงเวลาเพื่อให้เราอ่านทัน

    print("\n✅ Simulation Complete.")

if __name__ == "__main__":
    main()