# filename: gui_simulator.py
import sys, customtkinter, tkinter as tk
import traceback
from simulation_env import SimulationEnvironment
from isolated_agent import PanyarinNeuralAI, Strategy
from logger import Logger

class TextRedirector:
    def __init__(self, widget): self.widget = widget
    def write(self, text):
        try:
            if self.widget.winfo_exists():
                self.widget.configure(state="normal")
                self.widget.insert(tk.END, text)
                self.widget.see(tk.END)
                self.widget.configure(state="disabled")
        except Exception:
            sys.__stdout__.write(text)
    def flush(self): pass

class PanyarinAIControlRoom(customtkinter.CTk):
    ASCII_MOODS = {
        Strategy.DEFAULT:     " (•‿•)\n---------\n CALM",
        Strategy.POWER_SAVE:  " ( u . u)\n---------\n SLEEPING",
        Strategy.WORKSTATION: " (⌐■_■)\n---------\n FOCUSED",
        Strategy.GAMING:      " (ง'̀-'́)ง\n---------\n ENGAGED",
        "REFLEX":             " (°◇°)\n---------\n ALERT!",
        "CONFUSED":           " (•ิ_•ิ)?\n---------\n ADAPTING"
    }

    def __init__(self):
        super().__init__(); self.title("Panyarin AI Control Room (Hostile Environment Sim)"); self.geometry("1280x800")
        customtkinter.set_appearance_mode("Dark"); customtkinter.set_default_color_theme("blue")
        self.env = SimulationEnvironment(); self.ai = PanyarinNeuralAI(psutil_mock=self.env.psutil_mock, subprocess_mock=self.env.subprocess_mock)
        self.is_running = False; self.tick_speed_ms = 1000; self.app_checkboxes = {}; self.is_in_reflex_state = False
        self._create_widgets()
        sys.stdout = TextRedirector(self.log_textbox); sys.stderr = TextRedirector(self.log_textbox)
        Logger.info("Panyarin AI Control Room Initialized.")
        Logger.info("✅ System ready. Engage simulation scenarios.")
        self.update_dashboard()

    def _create_widgets(self):
        self.grid_columnconfigure(1, weight=1); self.grid_rowconfigure(0, weight=1)
        left_panel = customtkinter.CTkFrame(self, width=350, corner_radius=10); left_panel.grid(row=0, column=0, padx=15, pady=15, sticky="nsew"); left_panel.grid_propagate(False); left_panel.grid_rowconfigure(3, weight=1)
        
        sim_control_frame = customtkinter.CTkFrame(left_panel, fg_color="transparent"); sim_control_frame.grid(row=0, column=0, padx=10, pady=10, sticky="new"); sim_control_frame.grid_columnconfigure((0, 1), weight=1); customtkinter.CTkLabel(sim_control_frame, text="SIMULATION CONTROL", font=customtkinter.CTkFont(size=14, weight="bold")).grid(row=0, column=0, columnspan=2, pady=(0, 10)); self.start_button = customtkinter.CTkButton(sim_control_frame, text="▶️ Start", command=self.start_simulation); self.start_button.grid(row=1, column=0, padx=(0, 5), pady=5, sticky="ew"); self.stop_button = customtkinter.CTkButton(sim_control_frame, text="⏸️ Pause", command=self.stop_simulation, state="disabled"); self.stop_button.grid(row=1, column=1, padx=(5, 0), pady=5, sticky="ew")
        
        scenario_frame = customtkinter.CTkFrame(left_panel, fg_color="transparent"); scenario_frame.grid(row=1, column=0, padx=10, pady=10, sticky="new"); scenario_frame.grid_columnconfigure(0, weight=1); customtkinter.CTkLabel(scenario_frame, text="AUTOMATED SCENARIOS", font=customtkinter.CTkFont(size=14, weight="bold")).grid(row=0, column=0, pady=(10, 10))
        self.work_test_button = customtkinter.CTkButton(scenario_frame, text="💼 Run Workstation Task", command=self.run_workstation_test); self.work_test_button.grid(row=1, column=0, padx=0, pady=5, sticky="ew")
        self.thrashing_button = customtkinter.CTkButton(scenario_frame, text="💥 System Thrashing Test", fg_color="#6A1B9A", hover_color="#4A148C", command=self.run_thrashing_test); self.thrashing_button.grid(row=2, column=0, padx=0, pady=5, sticky="ew")
        self.stress_test_button = customtkinter.CTkButton(scenario_frame, text="🔥 Ultimate Stress Test", fg_color="#D32F2F", hover_color="#B71C1C", command=self.run_stress_test); self.stress_test_button.grid(row=3, column=0, padx=0, pady=5, sticky="ew")

        manual_frame = customtkinter.CTkFrame(left_panel, fg_color="transparent"); manual_frame.grid(row=2, column=0, padx=10, pady=10, sticky="new"); manual_frame.grid_columnconfigure(0, weight=1)
        customtkinter.CTkLabel(manual_frame, text="MANUAL APP CONTROL", font=customtkinter.CTkFont(size=14, weight="bold")).grid(row=0, column=0, pady=(10, 10))
        checkbox_frame = customtkinter.CTkFrame(manual_frame); checkbox_frame.grid(row=1, column=0, sticky="ew"); checkbox_frame.grid_columnconfigure((0, 1), weight=1)
        apps_to_test = {"Firefox": "🦊", "Steam": "🎮", "Blender": "🧊", "Kdenlive": "🎬", "OBS": "🔴"}
        for i, (app_name, emoji) in enumerate(apps_to_test.items()):
            var = customtkinter.StringVar(value="off")
            cb = customtkinter.CTkCheckBox(checkbox_frame, text=f"{emoji} {app_name}", variable=var, onvalue="on", offvalue="off")
            cb.grid(row=i//2, column=i%2, padx=10, pady=5, sticky="w")
            self.app_checkboxes[app_name.lower()] = (cb, var)
            
        action_frame = customtkinter.CTkFrame(manual_frame, fg_color="transparent"); action_frame.grid(row=2, column=0, pady=(10, 0)); action_frame.grid_columnconfigure((0, 1), weight=1); launch_selected_btn = customtkinter.CTkButton(action_frame, text="🚀 Launch Selected", command=self.launch_selected_apps); launch_selected_btn.grid(row=0, column=0, columnspan=2, pady=5, sticky="ew"); launch_all_btn = customtkinter.CTkButton(action_frame, text="💥 Launch ALL", command=self.launch_all_apps, fg_color="#F57C00", hover_color="#E65100"); launch_all_btn.grid(row=1, column=0, columnspan=2, pady=5, sticky="ew"); close_all_button = customtkinter.CTkButton(action_frame, text="❌ Close All Apps", fg_color="transparent", border_width=1, command=self.close_all_apps); close_all_button.grid(row=2, column=0, columnspan=2, pady=5, sticky="ew")

        mood_frame = customtkinter.CTkFrame(left_panel); mood_frame.grid(row=4, column=0, padx=10, pady=20, sticky="sew"); mood_frame.grid_columnconfigure(0, weight=1); customtkinter.CTkLabel(mood_frame, text="AI MOOD", font=customtkinter.CTkFont(size=14, weight="bold")).grid(row=0, column=0, pady=(10,0))
        self.ai_mood_label = customtkinter.CTkLabel(mood_frame, text=self.ASCII_MOODS[Strategy.DEFAULT], font=customtkinter.CTkFont(size=16, weight="bold"), justify="center")
        self.ai_mood_label.grid(row=1, column=0, pady=(0, 10), padx=10)
        
        right_panel = customtkinter.CTkFrame(self, fg_color="transparent"); right_panel.grid(row=0, column=1, padx=(0,15), pady=15, sticky="nsew"); right_panel.grid_columnconfigure(0, weight=1); right_panel.grid_rowconfigure(1, weight=1)
        info_frame = customtkinter.CTkFrame(right_panel); info_frame.grid(row=0, column=0, sticky="new"); info_frame.grid_columnconfigure((0, 1), weight=1)
        
        sys_met_frame = customtkinter.CTkFrame(info_frame, fg_color="transparent"); sys_met_frame.grid(row=0, column=0, padx=10, pady=(0,10), sticky="ew"); sys_met_frame.grid_columnconfigure(1, weight=1); customtkinter.CTkLabel(sys_met_frame, text="SYSTEM METRICS", font=customtkinter.CTkFont(size=12, weight="bold")).grid(row=0, column=0, columnspan=3, pady=(10,5))
        customtkinter.CTkLabel(sys_met_frame, text="CPU %").grid(row=1, column=0, padx=10, pady=2, sticky="w"); self.cpu_bar = customtkinter.CTkProgressBar(sys_met_frame); self.cpu_bar.grid(row=1, column=1, padx=10, pady=2, sticky="ew"); self.cpu_percent_label = customtkinter.CTkLabel(sys_met_frame, text="0.0 %", width=50, anchor="w"); self.cpu_percent_label.grid(row=1, column=2, padx=10, pady=2, sticky="w")
        customtkinter.CTkLabel(sys_met_frame, text="Mem %").grid(row=2, column=0, padx=10, pady=2, sticky="w"); self.mem_bar = customtkinter.CTkProgressBar(sys_met_frame); self.mem_bar.grid(row=2, column=1, padx=10, pady=2, sticky="ew"); self.mem_percent_label = customtkinter.CTkLabel(sys_met_frame, text="0.0 %", width=50, anchor="w"); self.mem_percent_label.grid(row=2, column=2, padx=10, pady=2, sticky="w")
        customtkinter.CTkLabel(sys_met_frame, text="I/O Wait %").grid(row=3, column=0, padx=10, pady=2, sticky="w"); self.io_bar = customtkinter.CTkProgressBar(sys_met_frame, progress_color="#FBC02D"); self.io_bar.grid(row=3, column=1, padx=10, pady=2, sticky="ew"); self.io_percent_label = customtkinter.CTkLabel(sys_met_frame, text="0.0 %", width=50, anchor="w"); self.io_percent_label.grid(row=3, column=2, padx=10, pady=2, sticky="w")
        
        # VVVVVV THIS IS THE CORRECTED/RESTORED SECTION VVVVVV
        # นำโค้ดที่หายไปกลับคืนมา
        ai_stat_frame = customtkinter.CTkFrame(info_frame, fg_color="transparent")
        ai_stat_frame.grid(row=0, column=1, padx=10, pady=(0,10), sticky="ew")
        ai_stat_frame.grid_columnconfigure(1, weight=1)
        customtkinter.CTkLabel(ai_stat_frame, text="AI CORE STATUS", font=customtkinter.CTkFont(size=12, weight="bold")).grid(row=0, column=0, columnspan=2, pady=(10,5))
        customtkinter.CTkLabel(ai_stat_frame, text="Strategy").grid(row=1, column=0, padx=10, pady=2, sticky="w")
        self.strategy_label = customtkinter.CTkLabel(ai_stat_frame, text="N/A", font=customtkinter.CTkFont(weight="bold"))
        self.strategy_label.grid(row=1, column=1, padx=10, pady=2, sticky="w")
        customtkinter.CTkLabel(ai_stat_frame, text="Governor").grid(row=2, column=0, padx=10, pady=2, sticky="w")
        self.governor_label = customtkinter.CTkLabel(ai_stat_frame, text="N/A")
        self.governor_label.grid(row=2, column=1, padx=10, pady=2, sticky="w")
        customtkinter.CTkLabel(ai_stat_frame, text="Action Failures").grid(row=3, column=0, padx=10, pady=2, sticky="w")
        self.failures_label = customtkinter.CTkLabel(ai_stat_frame, text="0", text_color="#E57373")
        self.failures_label.grid(row=3, column=1, padx=10, pady=2, sticky="w")
        # trigger_label ที่เป็นต้นเหตของปัญหา
        customtkinter.CTkLabel(ai_stat_frame, text="AI Trigger").grid(row=4, column=0, padx=10, pady=2, sticky="w")
        self.trigger_label = customtkinter.CTkLabel(ai_stat_frame, text="N/A", wraplength=250)
        self.trigger_label.grid(row=4, column=1, padx=10, pady=2, sticky="w")

        # แก้ไขการจัดวาง log_textbox
        self.log_textbox = customtkinter.CTkTextbox(right_panel, state="disabled", font=customtkinter.CTkFont(size=12), border_width=2)
        self.log_textbox.grid(row=1, column=0, padx=0, pady=(10,0), sticky="nsew")
        # ^^^^^^ THIS IS THE CORRECTED/RESTORED SECTION ^^^^^^
        
    def launch_selected_apps(self): Logger.user_action("Launching selected apps..."); [self.env.add_app(app_name) for app_name, (_, cb_var) in self.app_checkboxes.items() if cb_var.get() == "on"]
    def launch_all_apps(self): Logger.user_action("Launching ALL test applications..."); [self.env.add_app(app_name) or cb_var.set("on") for app_name, (_, cb_var) in self.app_checkboxes.items()]
    def close_all_apps(self): Logger.user_action("Closing all user applications..."); [cb_var.set("off") for _, (_, cb_var) in self.app_checkboxes.items()]; [self.env.remove_app(app) for app in list(self.env.state['running_apps'].keys() - {'python3', 'cinnamon'})]
    def run_workstation_test(self): Logger.scenario("INITIATING WORKSTATION TASK"); self.start_simulation() if not self.is_running else None; self.close_all_apps(); self.after(1000, lambda: self.env.add_app('blender')); self.after(3000, lambda: (Logger.scenario("Blender enters 'active' rendering state..."), self.env.set_app_state('blender', 'active'))); self.after(9000, lambda: (Logger.scenario("Blender render finished, returning to 'idle'."), self.env.set_app_state('blender', 'idle'))); self.after(11000, lambda: (self.close_all_apps(), Logger.scenario("WORKSTATION TASK COMPLETE.")))
    def run_thrashing_test(self): Logger.scenario("INITIATING SYSTEM THRASHING TEST"); self.thrashing_button.configure(state="disabled",text="Thrashing..."); self.start_simulation() if not self.is_running else None; self.close_all_apps(); self.after(1000, lambda: (Logger.scenario("PHASE 1: High CPU Task (Kdenlive)"), self.env.add_app('kdenlive', 'active'))); self.after(3000, lambda: (Logger.scenario("PHASE 2: Contention Task (Blender)"), self.env.add_app('blender', 'active'))); self.after(5000, lambda: (Logger.scenario("PHASE 3: I/O Saturation Event"), self.env.trigger_io_stress(40))); self.after(7000, lambda: (Logger.scenario("PHASE 4: Memory Crisis"), self.env.trigger_memory_stress(95))); self.after(12000, lambda: (Logger.scenario("PHASE 5: System Cooldown"), self.close_all_apps())); self.after(15000, lambda: (Logger.scenario("THRASHING TEST COMPLETE"), self.thrashing_button.configure(state="normal",text="💥 System Thrashing Test")))
    def run_stress_test(self): Logger.scenario("INITIATING ULTIMATE STRESS TEST"); self.stress_test_button.configure(state="disabled", text="Testing..."); self.start_simulation() if not self.is_running else None; self.close_all_apps(); self.after(2000, lambda: (Logger.scenario("PHASE 1: Launching light app..."), self.env.add_app('firefox'))); self.after(4000, lambda: (Logger.scenario("PHASE 2: Launching workstation app..."), self.env.add_app('blender', state='active'))); self.after(6000, lambda: (Logger.scenario("PHASE 3: Simulating gaming conflict..."), self.env.add_app('steam'))); self.after(8000, lambda: (Logger.scenario("PHASE 4: Triggering memory crisis..."), self.env.trigger_memory_stress(96))); self.after(10000, lambda: (Logger.scenario("PHASE 5: System cooldown..."), self.env.remove_app('steam'), self.env.remove_app('blender'))); self.after(12000, lambda: self.env.remove_app('firefox')); self.after(14000, lambda: (Logger.scenario("TEST COMPLETE."), self.stress_test_button.configure(state="normal", text="🔥 Ultimate Stress Test")))
    def start_simulation(self):
        if not self.is_running: self.is_running = True; self.start_button.configure(state="disabled"); self.stop_button.configure(state="normal"); Logger.info("Simulation Started."); self.simulation_tick()
    def stop_simulation(self):
        if self.is_running: self.is_running = False; self.start_button.configure(state="normal"); self.stop_button.configure(state="disabled"); Logger.info("Simulation Paused.")
    def simulation_tick(self):
        if not self.is_running: return
        self.env.update_system_load(); self.ai.main_loop_step(); self.update_dashboard(); self.after(self.tick_speed_ms, self.simulation_tick)

    def update_dashboard(self):
        cpu_val = self.env.state['cpu_percent']; mem_info = self.env.psutil_mock.virtual_memory(); io_val = self.env.state['io_wait']
        self.cpu_bar.set(cpu_val / 100); self.cpu_percent_label.configure(text=f"{cpu_val:.1f} %")
        self.mem_bar.set(mem_info.percent / 100); self.mem_percent_label.configure(text=f"{mem_info.percent:.1f} %")
        self.io_bar.set(io_val / 100); self.io_percent_label.configure(text=f"{io_val:.1f} %")
        self.failures_label.configure(text=str(len(self.ai.failure_tracker)))
        
        strategy_name = self.ai.current_strategy.name; strategy_text = strategy_name.replace("_", " ").upper()
        color_map = {"GAMING": "#E53935", "WORKSTATION": "#F57C00", "POWER_SAVE": "#43A047", "DEFAULT": "#78909C"}
        self.strategy_label.configure(text=strategy_text, text_color=color_map.get(strategy_name, "white"))
        self.governor_label.configure(text=self.env.state['governor']); self.trigger_label.configure(text=self.ai.last_trigger_reason)

        mood_color = color_map.get(strategy_name, "white"); mood_art = self.ASCII_MOODS.get(self.ai.current_strategy, self.ASCII_MOODS[Strategy.DEFAULT])
        if self.ai.tick_counter % 10 < 2 and self.ai.tick_counter > 0: mood_art = self.ASCII_MOODS["CONFUSED"]; mood_color="#90CAF9"
        if mem_info.percent > 90: mood_art = self.ASCII_MOODS["REFLEX"]; mood_color="#FBC02D"
        self.ai_mood_label.configure(text=mood_art, text_color=mood_color)

if __name__ == "__main__":
    try:
        app = PanyarinAIControlRoom()
        app.mainloop()
    except Exception as e:
        print("="*80)
        print("An unexpected error occurred and the application has to close.")
        print(f"ERROR: {e}")
        error_message = traceback.format_exc()
        print("TRACEBACK:\n", error_message)
        print("="*80)
        with open("crash_log.txt", "w", encoding="utf-8") as f:
            f.write(f"ERROR: {e}\n\n")
            f.write(error_message)
        input("Error details have been saved to crash_log.txt. Press Enter to exit...")