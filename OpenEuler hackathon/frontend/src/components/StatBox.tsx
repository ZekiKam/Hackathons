import { Line, CartesianGrid, ResponsiveContainer, Area, AreaChart, YAxis } from "recharts";

export interface StatDataPoint {
    value: number;
}

export interface Stat {
    id: string;
    title: string;
    percentage: number;
    data: StatDataPoint[];
}

interface StatBoxProps extends Stat {
    onClick?: () => void;
}

function StatBox({ title, percentage, data, onClick }: StatBoxProps) {
    return (
        <div
            onClick={onClick}
            className="bg-gray-800 rounded-2xl shadow-md cursor-pointer flex flex-col justify-between select-none w-full h-full min-h-48"
        >
            <div className="flex-1 p-4 w-full h-full">
                <ResponsiveContainer width="100%" height={150}>
                    <AreaChart data={data}>
                        <CartesianGrid strokeDasharray="1 1" stroke="#ccc" />

                        <YAxis domain={[0, 100]} hide />   {/* Force 0–100 scaling */}

                        <Area
                            type="linear"
                            dataKey="value"
                            stroke="#2563eb"
                            fill={(percentage < 40) ? "#00ff88" : percentage < 70 ? "#ffcc00" : "#ff0000"}
                            fillOpacity={0.4}
                            isAnimationActive={false}
                        />

                        <Line
                            type="linear"
                            dataKey="value"
                            stroke={(percentage < 40) ? "#00ff88" : percentage < 70 ? "#ffcc00" : "#ff0000"}
                            strokeWidth={2}
                            dot={false}
                            isAnimationActive={false}
                        />
                    </AreaChart>
                </ResponsiveContainer>
            </div>
            
            <div className="bg-gray-900 p-2 rounded-b-2xl text-center text-bold text-white text-md">
                {title}: {percentage}%
            </div>
        </div>
    );
}

export default StatBox;