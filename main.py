import os
import json
from pipeline import Customer360Orchestrator

def run_all_scenarios_separately():
    print("==================================================")
    print(" INTER-IIT TECH MEET 15.0: AGENTIC CUSTOMER 360")
    print(" Running & Organizing Scenarios Individually")
    print("==================================================")
    
    scenarios = ["scenario_01", "scenario_02", "scenario_03"]
    
    for scenario in scenarios:
        scenario_path = scenario
        if not os.path.exists(scenario_path):
            print(f"[WARNING] Folder '{scenario}' not found. Skipping.")
            continue
            
        print(f"\n[INFO] Processing {scenario}...")
        
        # 1. Load History Seed (Warm-up state)
        history_path = os.path.join(scenario_path, "history_seed.jsonl")
        history_events = []
        if os.path.exists(history_path):
            print(f"[INFO] Loading history seed from {history_path}")
            with open(history_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        history_events.append(json.loads(line))
        
        # 2. Load Live Stream Events
        stream_path = os.path.join(scenario_path, "live_stream.jsonl")
        if not os.path.exists(stream_path):
            # Fallback agar koi aur naam ho
            alt_streams = [f for f in os.listdir(scenario_path) if f.endswith(".jsonl") and "history" not in f]
            if alt_streams:
                stream_path = os.path.join(scenario_path, alt_streams[0])
            else:
                print(f"[WARNING] No live stream found in {scenario}!")
                continue
                
        print(f"[INFO] Reading live stream from {stream_path}")
        live_events = []
        with open(stream_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    live_events.append(json.loads(line))
        
        # Run orchestrator
        orchestrator = Customer360Orchestrator()
        
        # Agar history hai, toh pehle history process karke state build karein (bina output record kiye ya quiet mode mein)
        # Ya phir poori stream ko combine karke pass karein: History + Live Stream
        full_event_stream = history_events + live_events
        
        if not full_event_stream:
            print(f"[WARNING] Event stream is empty for {scenario}")
            continue

        orchestrator.process_event_stream(full_event_stream)
        
        # Rename the output file to match the scenario
        output_dir = "output" # ya "customer_360" jo bhi aapka output folder ho
        if not os.path.exists(output_dir):
            output_dir = "customer_360"
            
        if os.path.exists(output_dir):
            output_files = [os.path.join(output_dir, f) for f in os.listdir(output_dir) if f.startswith("inferred_events_")]
            if output_files:
                latest_output = max(output_files, key=os.path.getmtime)
                new_output_name = os.path.join(output_dir, f"inferred_events_{scenario}.json")
                if os.path.exists(latest_output) and latest_output != new_output_name:
                    os.replace(latest_output, new_output_name)
                    print(f"[SUCCESS] Saved scenario output to: {new_output_name}")

if __name__ == "__main__":
    run_all_scenarios_separately()