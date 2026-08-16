import LineChart, { type ChartDataPoint } from "./components/LineChart";
import "./styles.css";

const mockData: ChartDataPoint[] = [
  { label: "Jan", value: 24 }, { label: "Feb", value: 38 },
  { label: "Mar", value: 31 }, { label: "Apr", value: 52 },
  { label: "May", value: 47 }, { label: "Jun", value: 63 },
];

export default function ChartsPage() {
  return <section><header className="feature-heading"><h1>Static Charts</h1><p>A reusable chart example rendered with mock data.</p></header><article className="feature-card"><h2>Sample trend</h2><LineChart data={mockData} valueLabel="Sample value" /></article></section>;
}
