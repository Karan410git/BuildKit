import { CartesianGrid, Line, LineChart as RechartsLineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export type ChartDataPoint = { label: string; value: number };
type LineChartProps = { data: ChartDataPoint[]; valueLabel?: string };

export default function LineChart({ data, valueLabel = "Value" }: LineChartProps) {
  return <div className="chart-container" role="img" aria-label={`${valueLabel} line chart`}><ResponsiveContainer width="100%" height="100%"><RechartsLineChart data={data} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="label" /><YAxis /><Tooltip formatter={(value: number) => [value, valueLabel]} /><Line type="monotone" dataKey="value" name={valueLabel} stroke="#2563eb" strokeWidth={3} activeDot={{ r: 6 }} /></RechartsLineChart></ResponsiveContainer></div>;
}
