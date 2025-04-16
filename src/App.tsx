import { useState, useEffect } from "react";

import OffScreen from "./components/OffScreen.tsx";
import Button from "./components/Button.tsx";

import "./App.css";

import { BsCaretRightFill } from "react-icons/bs";

import {
  MapContainer,
  TileLayer,
  Marker,
  useMapEvents,
  Polyline,
  Rectangle,
} from "react-leaflet";
import "leaflet/dist/leaflet.css";
import "leaflet-control-geocoder";
import { Icon, LatLngExpression } from "leaflet";

function HandleClick({
  // markers,
  setMarker,
}: {
  markers: LatLngExpression[];
  setMarker: Function;
}) {
  useMapEvents({
    click(e) {
      const newMarker: LatLngExpression = [e.latlng.lat, e.latlng.lng];

      setMarker((prevMarkers: LatLngExpression[]) => {
        if (prevMarkers.length < 2) {
          return [...prevMarkers, newMarker]; // Add marker if less than 2
        } else {
          return [prevMarkers[0], newMarker]; // Replace last marker
        }
      });
    },
  });
  return null;
}

async function getNearestLocation(lat: number, lon: number): Promise<string> {
  const url = `https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lon}&format=json`;

  try {
    const response = await fetch(url);
    const data = await response.json();

    if (data && data.display_name) {
      return data.display_name;
    } else {
      return "Location Not Found";
    }
  } catch (error) {
    console.error("Error finding location: ", error);
    return "Error finding location";
  }
}

function findDistance(path: LatLngExpression[]): number {
  let sum = 0;
  const R = 3958.8; //radius of earth in miles. if you want distance in other units, then change this to another unit.

  for (let i = 0; i < path.length - 1; i++) {
    const [lat1, lon1] = path[i] as [number, number];
    const [lat2, lon2] = path[i + 1] as [number, number];

    //below is the haversine function that will get the distance between two coordinates
    // d = 2 * R * asin(sqrt(a))
    // a = sin²(Δlat/2) + cos(lat1) * cos(lat2) * sin²(Δlong/2)

    const lat1Rad = lat1 * (Math.PI / 180);
    const lon1Rad = lon1 * (Math.PI / 180);
    const lat2Rad = lat2 * (Math.PI / 180);
    const lon2Rad = lon2 * (Math.PI / 180);

    const diffLat = lat2Rad - lat1Rad;
    const diffLon = lon2Rad - lon1Rad;

    const a =
      Math.sin(diffLat / 2) ** 2 +
      Math.cos(lat1Rad) * Math.cos(lat2Rad) * Math.sin(diffLon / 2) ** 2;
    const d = 2 * R * Math.asin(Math.sqrt(a));

    sum += d;
  }

  return sum;
}

function App() {
  //handle selection of the algo method used
  const [selectedMethod, setSelectedMethod] = useState("Dijkstra's");
  console.log("Selected Method:", selectedMethod);

  // markers
  const [markers, setMarker] = useState<LatLngExpression[]>([]);
  const [shortestPath, setShortestPath] = useState<LatLngExpression[]>([]);

  const searchBounds: [[number, number], [number, number]] = [
    [29.204, -83.104], // SW
    [30.048, -81.605], // NE corner (lat, lon)
  ];

  const destinationIcon = new Icon({
    iconUrl: "./public/placeholder.png",
    iconSize: [40, 40],
    iconAnchor: [20, 40],
  });

  const homeIcon = new Icon({
    iconUrl: "./public/home.png",
    iconSize: [40, 40],
    iconAnchor: [20, 40],
  });

  const center: [number, number] = [29.622069801647613, -82.62269247880934];
  const [offScreenVisible, setOSVisibility] = useState(true);

  const [executionTime, setExecutionTime] = useState<string | null>(null);
  const [distance, setDistance] = useState<string | null>(null);

  const [pathNotFound, setPathNotFound] = useState(false);

  const [destinationLocation, setDestinationLocation] = useState<string | null>(
    null
  );
  const [startLocation, setStartLocation] = useState<string | null>(null);

  // when there are two markers, find the shortest path
  useEffect(() => {
    const fetchData = async () => {
      if (markers.length === 2) {
        fetchShortestPath();
      } else {
        setShortestPath([]);
        setPathNotFound(false);
        if (!markers[0]) {
          setStartLocation("");
        }
        if (!markers[1]) {
          setDestinationLocation("");
        }
        if (markers[0]) {
          const [lat1, lon1] = markers[0] as [number, number];
          setStartLocation(await getNearestLocation(lat1, lon1));
          console.log(startLocation);
        }
      }
    };
    fetchData();
  }, [markers]);

  const [numMarkers, setNumMarkers] = useState(markers.length);

  useEffect(() => {
    setNumMarkers(markers.length);
  }, [markers]);

  // make the function that finds the shortest path
  const fetchShortestPath = async () => {
    const startTime = performance.now();
    // if no two markers, stop
    if (markers.length < 2) {
      return;
    }
    //get the data request from python file
    try {
      setShortestPath([]);
      setExecutionTime("Loading...");
      setDistance("Loading...");
      setPathNotFound(false);

      if (markers[1]) {
        const [lat2, lon2] = markers[1] as [number, number];
        setDestinationLocation(await getNearestLocation(lat2, lon2));
        console.log(destinationLocation);
      }

      //select the correct URL based off the algorithm
      let base_url = "http://127.0.0.1:5000/";
      let url = "";

      console.log("Algo selected is: " + selectedMethod);
      if (selectedMethod == "Dijkstra's") {
        url = base_url + "dijkstras";
        //console.log("Dijkstras loaded!")
      } else if (selectedMethod == "BFS") {
        url = base_url + "bfs";
        //console.log("BFS loaded!")
      } else if (selectedMethod == "DFS") {
        url = base_url + "dfs";
        //console.log("DFS loaded!")
      } else {
        //console.log("Method did not load :(")
      }

      const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ point1: markers[0], point2: markers[1] }),
      });

      if (response.status === 404) {
        setPathNotFound(true);
      } else {
        setPathNotFound(false);
      }

      const endTime = performance.now();

      // set the shortest path to the given path
      const data = await response.json();
      // console.log("Received Path from Flask:", data.path); // Debugging log

      if (data.path) {
        setShortestPath(data.path);
        markers[0] = data.path[0];
        markers[1] = data.path[data.path.length - 1];
        setExecutionTime(((endTime - startTime) / 1000).toFixed(3));
        setDistance(findDistance(data.path).toFixed(1));
        // console.log(data.path);
        // console.log(data.path.length);
      }
    } catch (error) {
      console.error("Error fetching shortest path:", error);
    }
  };

  useEffect(() => {
    fetchShortestPath();
  }, [selectedMethod]);

  return (
    <>
      <MapContainer
        center={center}
        zoom={10}
        style={{ height: "100%", width: "100%" }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <TileLayer
          attribution='<a href="https://extract.bbbike.org/extract.html
">BBBike</a>'
          url="https://extract.bbbike.org/extract.html"
        />
        <TileLayer
          attribution='<a href="https://www.flaticon.com/free-icons/pin
">Flaticon</a>'
          url="https://www.flaticon.com/free-icons/pin"
        />
        <TileLayer
          attribution='<a href="https://www.freepik.com/icons/404
">FreePik</a>'
          url="https://www.freepik.com/icons/404"
        />

        <HandleClick markers={markers} setMarker={setMarker} />

        <Rectangle
          bounds={searchBounds}
          pathOptions={{ color: "gray", weight: 2, fillOpacity: 0 }}
        ></Rectangle>

        {markers.map((position, index) => (
          <>
            <Marker
              key={index}
              position={position}
              icon={index === 0 ? homeIcon : destinationIcon}
              eventHandlers={{
                click: () =>
                  setMarker((prev) => prev.filter((_, i) => i !== index)),
              }}
            ></Marker>
          </>
        ))}

        {/* draw the shortest path */}
        {shortestPath.length > 0 && markers.length === 2 && (
          <Polyline positions={shortestPath} color="blue" weight={5} />
        )}
      </MapContainer>

      <div className="overlay">
        {offScreenVisible ? (
          <OffScreen
            destination={[markers[1]]}
            start={[markers[0]]}
            onClose={() => setOSVisibility(false)}
            executionTime={executionTime}
            numMarkers={numMarkers}
            lengthPath={shortestPath.length}
            pathNotFound={pathNotFound}
            distance={distance}
            startLocation={startLocation}
            destinationLocation={destinationLocation}
            selectedMethod={selectedMethod}
            setSelectedMethod={setSelectedMethod}
          />
        ) : (
          <Button
            icon={BsCaretRightFill}
            onClick={() => setOSVisibility(true)}
          ></Button>
        )}
      </div>
      <div>
        <img
          src={pathNotFound ? "/404active.png" : "/404static.png"}
          alt="404 Static Image"
          style={{
            position: "fixed", // Fixes the image in place relative to the viewport
            bottom: "2%",
            right: "2%",
            width: "105px",
            height: "125px",
            objectFit: "contain",
            opacity: pathNotFound ? 1 : 0.5,
            transition: "opacity 0.1s ease-in-out",
          }}
        />
      </div>
    </>
  );
}

export default App;
