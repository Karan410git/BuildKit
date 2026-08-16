import StaticMap, { type MapMarker } from "./components/StaticMap";

const mockMarkers: MapMarker[] = [
  { id: "location-a", label: "Sample location A", position: [40.7128, -74.006] },
  { id: "location-b", label: "Sample location B", position: [51.5072, -0.1276] },
  { id: "location-c", label: "Sample location C", position: [28.6139, 77.209] },
];

export default function MapsPage() {
  return (
    <section>
      <header className="feature-heading">
        <h1>Static Maps</h1>
        <p>A reusable map example rendered with mock markers.</p>
      </header>
      <article className="feature-card">
        <h2>Sample locations</h2>
        <StaticMap center={[30, 10]} markers={mockMarkers} zoom={2} />
      </article>
    </section>
  );
}
