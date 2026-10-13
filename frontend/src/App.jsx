
import { useEffect, useState } from "react";

function App() {
  const [facilities, setFacilities] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch("http://127.0.0.1:8000/facilities") //making rqsts to 8000
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to fetch facilities");
        }
        return response.json();
      })
      .then((data) => setFacilities(data))
      .catch((err) => setError(err.message));
  }, []);

  return (
    <div>
      <h1>Sports Slot Booking</h1>

      {error && <p>Error: {error}</p>}

      {facilities.map((facility) => (
        <p key={facility.id}>{facility.name}</p>
      ))}
    </div>
  );
}

export default App;
