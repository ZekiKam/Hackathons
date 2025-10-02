import { useState, useEffect } from "react";
import StatBox from "./StatBox";
import { AnimatePresence, motion } from "framer-motion";

function Dashboard() {
    const [expanded, setExpanded] = useState(false);

    const [stats, setStats] = useState([
        { id: "cpu", title: "CPU", data: [] },
        { id: "gpu", title: "GPU", data: [] },
        { id: "mem", title: "Memory", data: [] },
        { id: "gtemp", title: "GPU Temp", data: [] },
        { id: "gpower", title: "GPU Power", data: [] },
        { id: "gmem", title: "GPU Memory", data: [] },
        { id: "disk", title: "Disk I/O", data: [] },
        { id: "net", title: "Network I/O", data: [] },
    ]);
    const [cores, setCores] = useState([[{value: 0}], [{value: 10}], [{value: 50}], [{value: 100}]]);
    const [info, setInfo] = useState(["N/A"]);

    useEffect(() => {
        const socket = new WebSocket("ws://localhost:8000/ws");

        socket.onopen = () => console.log("WS connected");
        socket.onclose = () => console.log("WS closed");
        socket.onerror = (err) => console.error("WS error", err);
        
        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);

            //console.log("WS message:", data.stats);
            
            setStats(data.stats);
            setCores(data.cores);
            setInfo(data.info);
        };
        return () => socket.close();
    }, []);
    

    return (
        <div className="p-4 grid grid-cols-3 auto-rows-fr gap-4 w-full h-full">
            
            <div
                onClick={undefined}
                className="bg-gray-800 rounded-2xl shadow-md cursor-pointer flex flex-col justify-between select-none w-full h-full min-h-48"
            >
                <div className="flex-1 p-4 w-full h-full text-left">
                    {info.map((line, index) => (
                        <pre key={index} className="text-md text-gray-300 mb-1">
                            {line}
                        </pre>
                    ))}
                </div>
                
                <div className="bg-gray-900 p-2 rounded-b-2xl text-center text-bold text-white text-md">
                    &#9432; System Information
                </div>
            </div>

            {stats
                .filter(stat => Array.isArray(stat.data) && stat.data[0] != null)
                .map(stat => (
                    <StatBox
                        key={stat.id}
                        id={stat.id}
                        title={stat.title}
                        percentage={stat.data.length > 0 ? Math.floor(stat.data[stat.data.length - 1]) : 0}
                        data={stat.data.filter(v => v !== null && v !== undefined && !isNaN(v)).map(v => ({ value: v }))}
                        onClick={stat.id === "cpu" ? () => setExpanded(true) : undefined}
                    />
                ))}

            <AnimatePresence>
                {expanded && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 bg-black/70 flex justify-center items-center"
                        onClick={() => setExpanded(false)}
                    >
                        <motion.div
                            initial={{ scale: 0.8 }}
                            animate={{ scale: 1 }}
                            exit={{ opacity: 0, scale: 0.95 }}
                            transition={{ duration: 0.3 }}
                            className="bg-gray-1000 rounded-2xl p-4 grid grid-cols-3 gap-10 w-3/4 h-3/4 overflow-y-auto"
                            onClick={(e) => e.stopPropagation()}>

                            {cores.map((p, i) => (
                                <StatBox
                                    key={i}
                                    id={`core-${i}`}
                                    title={`Core ${i + 1}`}
                                    percentage={p.length > 0 ? Math.floor(p[p.length - 1].value) : 0}
                                    data={cores[i]}
                                />
                            ))}
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
export default Dashboard;