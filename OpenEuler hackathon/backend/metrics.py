import csv, json, time, subprocess, datetime, psutil, shutil, uvicorn, threading

from ws_app import globalMetrics

#After every log, remove the old csv and jsonl files to start off with fresh metrics next time
CSV_PATH = "metrics.csv" 
JSONL_PATH = "metrics.jsonl" # jsonl is bigger than json!
SAMPLE_INTERVAL = 0.1

def read_gpu():
    if shutil.which("nvidia-smi") is None:
        return None
    try:
        out = subprocess.check_output(
            ["nvidia-smi",
             "--query-gpu=utilization.gpu,utilization.memory,memory.used,memory.total,temperature.gpu,power.draw",
             "--format=csv,noheader,nounits"],
            stderr=subprocess.DEVNULL,
            text=True
        ).strip()

    except subprocess.CalledProcessError:
        # GPU command failed (no driver / no device / unsupported environment)
        return None

    if not out:
        return None

    line = out.splitlines()[0]
    util, memutil, mem_used, mem_total, temp, power = [x.strip() for x in line.split(",")]
    return {
        "util": float(util),
        "mem_used": float(mem_used),
        "mem_total": float(mem_total),
        "temp": float(temp),
        "power": float(power),
    }

def per_core_str():
    cores = psutil.cpu_percent(interval=None, percpu=True) #returns a list of CPU usage percentages, one percentage per core
    return ";".join(f"{c:.1f}" for c in cores), len(cores) #round perentages to 1dp

def disk_net_rates(prev, now, dt):
    d0, n0 = prev #previous snapshot of disk and net I/O counters
    d1, n1 = now #current snapshot of disk and net I/O counters
    
    #Calculate raw rates in kB/s
    disk_read_kbs = (d1.read_bytes  - d0.read_bytes)  / dt / 1024.0
    disk_write_kbs = (d1.write_bytes - d0.write_bytes) / dt / 1024.0
    network_receive_kbs = (n1.bytes_recv  - n0.bytes_recv)  / dt / 1024.0
    network_transmit_kbs = (n1.bytes_sent  - n0.bytes_sent)  / dt / 1024.0
    
    # Convert to percentages (assuming reasonable maximums)
    # For disk: assume 500 MB/s as reasonable maximum (modern SSD)
    # For network: assume 100 MB/s as reasonable maximum (gigabit ethernet)
    max_disk_kbs = 500 * 1024  # 500 MB/s in kB/s
    max_network_kbs = 100 * 1024  # 100 MB/s in kB/s
    
    disk_read_pct = min(100.0, (disk_read_kbs / max_disk_kbs) * 100.0)
    disk_write_pct = min(100.0, (disk_write_kbs / max_disk_kbs) * 100.0)
    network_receive_pct = min(100.0, (network_receive_kbs / max_network_kbs) * 100.0)
    network_transmit_pct = min(100.0, (network_transmit_kbs / max_network_kbs) * 100.0)
    
    return disk_read_pct, disk_write_pct, network_receive_pct, network_transmit_pct

def run_server():
    uvicorn.run("ws_app:app", host="0.0.0.0", port=8000, reload=False)

def main():
    # Initialize uvicorn server in a separate thread
    t = threading.Thread(target=run_server, daemon=True)
    t.start()

    header = [
        "timestamp", #timestamp when sample was takem
        "cpu_overall", #overall CPU usage across all cores, 0-100% per core
        "cpu_per_core", #CPU usage of each core (separated by ;), again 0-100% per core
        "cpu_cores", #Number of core in VM
        "memory_usage", #Overall memory usage 0-100%
        "memory_used", #Absolute memory used in MB
        "total_memory", #Total memory available in MB
        "disk_read", #Disk read rate in kB/s
        "disk_write", #Disk write rate in kB/s
        "net_receive", #Network receive (downloads) rate in kB/s
        "net_transmit", #Network transmit (uploads) rate in kB/s
        #Corresponding fields will be empty unless Nvidia GPU is present!
        "gpu_usage", #GPU usage 0-100%
        "gpu_memory_usage", #GPU memory usage in MB
        "total_gpu_memory", #Total GPU memory in MB
        "gpu_temp", #GPU temperature in degrees Celsius
        "gpu_power", #GPU power consumption in Watts
    ]

    #Create CSV with header if no exisiting CSV files detected
    #Which is basically every time since we delete old files after every log
    try:
        with open(CSV_PATH, "x", newline="") as f:
            csv.writer(f).writerow(header)
    except FileExistsError:
        pass

    prev_disk = psutil.disk_io_counters() #take snapshot of disk I/O counters
    prev_net  = psutil.net_io_counters() #take snapshot of network I/O counters
    prev_t    = time.time()

    while True:
        t0 = time.time()
        ts = datetime.datetime.now(datetime.UTC).isoformat()

        #CPU total and per-core
        cpu_overall = psutil.cpu_percent(interval=None)
        cpu_per_core, ncores = per_core_str()

        #Memory
        vm = psutil.virtual_memory()
        mem_pct = vm.percent
        mem_used = vm.used / 1024 / 1024
        mem_total = vm.total / 1024 / 1024

        #Disk/ net I/O 
        now_disk = psutil.disk_io_counters()
        now_net = psutil.net_io_counters()
        now_t = time.time()
        dt = max(now_t - prev_t, 1e-6)
        rd, wr, rx, tx = disk_net_rates((prev_disk, prev_net), (now_disk, now_net), dt)
        prev_disk, prev_net, prev_t = now_disk, now_net, now_t

        #GPU telemetry if present (still idk what that is)
        g = read_gpu() or {}
        gpu_util = g.get("util")
        gpu_mem_used = g.get("mem_used")
        gpu_mem_total = g.get("mem_total")
        gpu_temp = g.get("temp")
        gpu_power = g.get("power")

        row = [
            ts,
            f"{cpu_overall:.1f}",
            cpu_per_core,
            ncores,
            f"{mem_pct:.1f}",
            f"{mem_used:.0f}",
            f"{mem_total:.0f}",
            f"{rd:.1f}",
            f"{wr:.1f}",
            f"{rx:.1f}",
            f"{tx:.1f}",
            "" if gpu_util is None else f"{gpu_util:.0f}",
            "" if gpu_mem_used is None else f"{gpu_mem_used:.0f}",
            "" if gpu_mem_total is None else f"{gpu_mem_total:.0f}",
            "" if gpu_temp is None else f"{gpu_temp:.0f}",
            "" if gpu_power is None else f"{gpu_power:.1f}",
        ]

        #Write CSV
        with open(CSV_PATH, "a", newline="") as f:
            csv.writer(f).writerow(row)

        #Write JSONL(think it's easier to integrate metrics to React with ?)
        payload = {
            "timestamp": ts,
            "cpu_overall": float(row[1]),
            "cpu_per_core": [float(x) for x in cpu_per_core.split(";")] if cpu_per_core else [],
            "cpu_cores": ncores,
            "memory_usage": float(row[4]),
            "memory_used": float(row[5]),
            "total_memory": float(row[6]),
            "disk_read": float(row[7]),
            "disk_write": float(row[8]),
            "net_receive": float(row[9]),
            "net_transmit": float(row[10]),
            "gpu_usage": None if row[11]=="" else float(row[11]),
            "gpu_memory_usage": None if row[12]=="" else float(row[12]),
            "total_gpu_memory": None if row[13]=="" else float(row[13]),
            "gpu_temp": None if row[14]=="" else float(row[14]),
            "gpu_power": None if row[15]=="" else float(row[15]),
        }
        with open(JSONL_PATH, "a") as jf:
            jf.write(json.dumps(payload) + "\n")

        global globalMetrics
        globalMetrics.appendleft(payload)
        
        t1 = time.time()
        time.sleep(max(0.0, SAMPLE_INTERVAL - (t1 - t0)))

if __name__ == "__main__":
    main()
    
