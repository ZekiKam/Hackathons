import asyncio
import json
import platform
import psutil
import cpuinfo

try:
    import GPUtil
except ImportError:
    GPUtil = None

from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from starlette.websockets import WebSocketDisconnect
from collections import deque

app = FastAPI()
#app.mount("/", StaticFiles(directory="./frontend/dist", html=True), name="static") # to bundle React frontend

# Global variable to hold latest metrics for websocket access
globalMetrics = deque(maxlen=10)

max_disk_rate = 1
max_net_rate = 1

async def collect_stats():
    return {
        "stats": [
            { "id": "cpu", "title": "CPU", "data": getData("cpu_overall") },
            { "id": "gpu", "title": "GPU", "data": getData("gpu_usage") },
            { "id": "mem", "title": "Memory", "data": getData("memory_usage") },
            { "id": "gtemp", "title": "GPU Temp", "data": getData("gpu_temp") },
            { "id": "gpower", "title": "GPU Power", "data": getData("gpu_power") },
            { "id": "gmem", "title": "GPU Memory", "data": getData("gpu_memory_usage") },
            { "id": "disk", "title": "Disk I/O", "data": getDiskIOData() },
            { "id": "net", "title": "Network I/O", "data": getNetworkIOData() },
        ],
        "cores": getCoresData(),
        "info": [
            getInfo()
        ]
    }

def getData(key):
    return [d[key] for d in globalMetrics if key in d]

def getCoresData():
    # Get all cpu_per_core data from globalMetrics
    all_cores_data = [d["cpu_per_core"] for d in globalMetrics if "cpu_per_core" in d]
    
    if not all_cores_data:
        return []
    
    # Determine number of cores from the first entry
    num_cores = len(all_cores_data[0]) if all_cores_data else 0
    
    # Restructure data: instead of [time][core], we want [core][time]
    cores_by_core = []
    for core_idx in range(num_cores):
        core_data = []
        for time_data in all_cores_data:
            if core_idx < len(time_data):
                core_data.append({"value": time_data[core_idx]})
        cores_by_core.append(core_data)
    
    return cores_by_core

def getDiskIOData():
    # Combine disk read and write percentages into a single metric (max disk activity)
    read_data = getData("disk_read")
    write_data = getData("disk_write")
    
    # Return the maximum of read/write as overall disk activity percentage
    combined_data = []

    for i in range(min(len(read_data), len(write_data))):
        rate = max(read_data[i], write_data[i])

        global max_disk_rate

        if rate > max_disk_rate:
            max_disk_rate = rate

        combined_data.append(max(read_data[i], write_data[i]) / max_disk_rate * 100)
    
    return combined_data

def getNetworkIOData():
    # Combine network receive and transmit percentages into a single metric (max network activity)
    receive_data = getData("net_receive")
    transmit_data = getData("net_transmit")
    
    # Return the maximum of receive/transmit as overall network activity percentage
    combined_data = []
    for i in range(min(len(receive_data), len(transmit_data))):
        rate = max(receive_data[i], transmit_data[i])

        global max_net_rate

        if rate > max_net_rate:
            max_net_rate = rate

        combined_data.append(rate / max_net_rate * 100)
    
    return combined_data

def getInfo():
    # CPU
    cpu_info = cpuinfo.get_cpu_info()
    cpu_model = cpu_info.get("brand_raw", "Unknown CPU")
    cores_physical = psutil.cpu_count(logical=False)
    cores_logical = psutil.cpu_count(logical=True)

    # Memory
    vm = psutil.virtual_memory()
    mem_gb = round(vm.total / (1024**3), 1)

    # GPU
    gpu_strs = []
    if GPUtil:
        try:
            for g in GPUtil.getGPUs():
                gpu_strs.append(f"{g.name} ({round(g.memoryTotal/1024,1)} GB)")
        except Exception:
            gpu_strs.append("No GPU detected")
    else:
        gpu_strs.append("No GPU detected")

    # OS
    os_str = f"{platform.system()} {platform.release()}"

    # Final formatted string
    return (
        f"OS: {os_str}\n"
        f"CPU: {cpu_model} ({cores_physical}C/{cores_logical}T)\n"
        f"Memory: {mem_gb} GB\n"
        f"GPU(s): {', '.join(gpu_strs)}"
    )
    

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connected")

    try:
        while True:
            payload = await collect_stats()  # call your existing collector
            await websocket.send_text(json.dumps(payload))
            await asyncio.sleep(0.5)  # throttle sending

    except WebSocketDisconnect:
        print("Client disconnected:", WebSocketDisconnect)
