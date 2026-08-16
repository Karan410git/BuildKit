import { MapContainer, Marker, Popup, TileLayer } from "react-leaflet";
import "leaflet/dist/leaflet.css";

export type MapMarker = {
  id: string;
  label: string;
  position: [number, number];
};

type StaticMapProps = {
  center: [number, number];
  markers: MapMarker[];
  zoom?: number;
};

export default function StaticMap({ center, markers, zoom = 3 }: StaticMapProps) {
  return (
    <MapContainer center={center} zoom={zoom} className="map-container" scrollWheelZoom={false}>
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {markers.map((marker) => (
        <Marker key={marker.id} position={marker.position}>
          <Popup>{marker.label}</Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}
