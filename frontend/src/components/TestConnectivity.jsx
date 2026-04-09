import { useEffect, useState } from "react";
import axios from 'axios'

function TestConnectivity() {
  const [message, setMessage] = useState("Loading...");

  useEffect(() => {
    axios.get('http://localhost:8000/')
    .then(res => setMessage(res.data.message))
    .catch(() => setMessage("Error connecting to backend"))
  }, [])

  return (
    <div>
      <p>{message}</p>
    </div>
  )
}

export default TestConnectivity;