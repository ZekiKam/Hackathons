import { CartesianGrid, ResponsiveContainer, BarChart, Bar, Rectangle, Tooltip, XAxis, YAxis, Cell } from "recharts";

export interface StatDataPoint {
    id: string;
    value: number;
}

export interface Stat {
    id: string;
    title: string;
    percentage: number;
    data: StatDataPoint[];
}

function BarChartBox({ title, percentage, data } : Stat) {
    const colors = ['#8884d8', '#82ca9d', '#ffc658', '#ff7c7c', '#8dd1e1', '#d084d0', '#ffb347'];

    const CustomTooltip = ({ active, payload }: any) => {
        if (active && payload && payload.length) {
            return (
                <div className="bg-gray-700 p-2 rounded border border-gray-600 text-white text-sm">
                    <p>{`ID: ${payload[0].payload.id}`}</p>
                    <p>{`Title: ${payload[0].payload.title}`}</p>
                    <p>{`Value: ${payload[0].value}%`}</p>
                </div>
            );
        }
        return null;
    };

    return (
        <div
            className="bg-gray-800 rounded-2xl shadow-md cursor-pointer flex flex-col justify-between select-none w-full h-full min-h-48"
        >
            <div className="flex-1 p-4 w-full h-full">
                <ResponsiveContainer width="100%" height={150}>
                    <BarChart data={data}>
                        <CartesianGrid strokeDasharray="1 1" stroke="#ccc" />
                        
                        <XAxis dataKey="id" />
                        <YAxis domain={[0, 100]} hide />
                        
                        <Tooltip content={<CustomTooltip />} />
                        
                        <Bar dataKey="value" maxBarSize={50} activeBar={<Rectangle stroke="blue" />}>
                            {data.map((_, index) => (
                                <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                            ))}
                        </Bar>
                    </BarChart>
                </ResponsiveContainer>
            </div>
            
            <div className="bg-gray-900 p-2 rounded-b-2xl text-center text-bold text-white text-md">
                {title}: {percentage}%
            </div>
        </div>
    );
}

export default BarChartBox;