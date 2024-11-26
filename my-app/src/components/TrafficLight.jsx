import React, { useState, useEffect } from "react";
import "./TrafficLight.css";
import Button from "react-bootstrap/Button";
import Modal from "react-bootstrap/Modal";
import { InputGroup, Form } from "react-bootstrap";
import "bootstrap/dist/css/bootstrap.min.css";

const TrafficLight = ({ serverIp, deviceName }) => {
  const [mode, setMode] = useState("auto");
  const [connected, setConnected] = useState(false);
  useEffect(() => {
    // Set the interval to update UI every 300ms
    const interval = setInterval(() => {
      updateUi();
    }, 300);

    // Cleanup the interval on component unmount
    return () => clearInterval(interval);
  }); // Empty dependency array ensures this effect only runs once, on mount

  const updateUi = async () => {
    try {
      const response = await fetch(serverIp + "/getStatus/" + deviceName);

      if (!response.ok) {
        // If response is not ok, throw an error
        throw new Error(`Error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json(); // Await the JSON data
      console.log(data); // Log the data

      // Only update connected when status changes
      setConnected(data.status !== 0 && data.arduino !== 0); // Set connected to true if status is not 0

      // Update other states based on the response data
      setMode(data.mode);
      if (data.mode === "auto") {
        setActiveLight(data.color);
        setTime(data.timeLeft);
      } else if (data.mode === "manual") {
        setActiveLight(data.manualColor);
        setTime("M");
      }
    } catch (err) {
      // Log the error and set connected to false in case of failure
      console.error(err.message);
      setConnected(false); // Ensure connected is set to false on error
    }
  };

  const setManualColor = async (color) => {
    const url = serverIp + "/setManualColor/" + deviceName;
    const payload = { manualColor: color }; // Your data to send

    try {
      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload), // Convert data to JSON string
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }

      const result = await response.json(); // Parse JSON response
      console.log("Response:", result);
    } catch (error) {
      console.error("Error sending POST request:", error);
    }
  };
  const changeMode = async () => {
    const url = serverIp + "/setMode/" + deviceName;

    let payload; // Declare payload outside the blocks
    if (mode === "auto") {
      payload = { mode: "manual" }; // Assign value based on condition
    } else {
      payload = { mode: "auto" }; // Assign value based on condition
    }

    try {
      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload), // Convert data to JSON string
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }

      const result = await response.json(); // Parse JSON response
      console.log("Response:", result);
    } catch (error) {
      console.error("Error sending POST request:", error);
    }
  };

  function capitalizeFirstLetter(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
  }

  // Light control
  const [activeLight, setActiveLight] = useState("");
  const handleClick = (color) => {
    setManualColor(color);
  };

  // Sequence control popup
  const [showModal, setShowModal] = useState(false);
  const openModal = () => {
    setShowModal(true);
  };
  const closeModal = () => {
    setShowModal(false);
  };

  // New Sequence selections
  const [sequence, setSequence] = useState([]); // RGY
  const [sequenceTime, setSequenceTime] = useState([]); // Times for RGY

  const handleAddColor = (color) => {
    setSequence((prevSequence) => [...prevSequence, color]);
    setSequenceTime((prevTimes) => [...prevTimes, ""]); // Initialize the time with an empty string
  };

  const handleTimeChange = (index, value) => {
    // Update time for a specific color in the sequence
    setSequenceTime((prevTimes) => {
      const updatedTimes = [...prevTimes];
      updatedTimes[index] = value;
      return updatedTimes;
    });
  };

  const generateSequenceJson = () => {
    const sequenceJson = sequence.map((color, index) => ({
      color,
      time: sequenceTime[index],
    }));
    console.log(sequenceJson); // Log the generated sequence
    closeModal();
    return sequenceJson;
  };

  const cancelSequenceSelection = () => {
    setSequence([]);
    setSequenceTime([]);
    closeModal();
  };
  const setNewSequence = async () => {
    try {
      const data = generateSequenceJson();
      console.log(data);
      const response = await fetch(serverIp + `/changeSequence/${deviceName}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data), // Send device data as JSON
      });

      const result = await response.json();
      if (response.ok) {
        alert(result.message); // Success message
      } else {
        alert(result.error); // Error message
      }
    } catch (error) {
      console.error("Error adding device:", error.message);
    }
    closeModal();
  };

  const [time, setTime] = useState("00");

  return (
    <div className="parentContainer">
      <span className="label">{deviceName ? deviceName : ""}</span>
      <div className="childContainer">
        <Button variant={connected ? "success" : "danger"} onClick={changeMode}>
          {mode === "auto" ? "A" : "M"}
        </Button>
        <div className="traffic-light-bar">
          <button
            className={`traffic-light red ${
              activeLight === "red" ? "active" : ""
            }`}
            onClick={() => handleClick("red")}
          ></button>
          <button
            className={`traffic-light yellow ${
              activeLight === "yellow" ? "active" : ""
            }`}
            onClick={() => handleClick("yellow")}
          ></button>
          <button
            className={`traffic-light green ${
              activeLight === "green" ? "active" : ""
            }`}
            onClick={() => handleClick("green")}
          ></button>
        </div>

        <div className="timer">
          <div className="timer-value">{time}</div>
          {mode === "auto" ? (
            <Button
              className="sequenceButton"
              variant="warning"
              onClick={openModal}
            >
              Sequence
            </Button>
          ) : (
            <></>
          )}
        </div>

        {/* Mode selection popup */}
        <Modal keyboard={false} show={showModal} onHide={closeModal} centered>
          <Modal.Header className="bg-dark text-light">
            <Modal.Title>Select Sequence</Modal.Title>
          </Modal.Header>
          <Modal.Body className="modalBody bg-dark text-light">
            <div className="sequenceButtonDiv">
              {sequence.includes("red") ? (
                <></>
              ) : (
                <Button
                  variant="danger"
                  className="RButton"
                  onClick={() => handleAddColor("red")}
                >
                  Red
                </Button>
              )}
              {sequence.includes("green") ? (
                <></>
              ) : (
                <Button
                  variant="success"
                  className="GSButton"
                  onClick={() => handleAddColor("green")}
                >
                  Green
                </Button>
              )}
              {sequence.includes("yellow") ? (
                <></>
              ) : (
                <Button
                  variant="warning"
                  className="YButton"
                  onClick={() => handleAddColor("yellow")}
                >
                  Yellow
                </Button>
              )}
              <Button variant="secondary" onClick={cancelSequenceSelection}>
                Cancel
              </Button>
            </div>

            <div className="selectionDisplay">
              {sequence.map((color, index) => (
                <InputGroup size="sm" className="mb-3" key={index}>
                  <InputGroup.Text id="inputGroup-sizing-sm">
                    {capitalizeFirstLetter(color)}
                  </InputGroup.Text>
                  <Form.Control
                    type="number"
                    value={sequenceTime[index] || ""}
                    onChange={(e) => handleTimeChange(index, e.target.value)}
                    aria-label="Small"
                    aria-describedby="inputGroup-sizing-sm"
                    placeholder="Time in seconds"
                    min="0"
                    step="1"
                  />
                </InputGroup>
              ))}
              {sequence.length === 3 && sequenceTime.length === 3 && (
                <Button
                  variant="success"
                  className="GSButton"
                  onClick={() => setNewSequence()}
                >
                  Set Sequence
                </Button>
              )}
            </div>
          </Modal.Body>
        </Modal>
      </div>
    </div>
  );
};

export default TrafficLight;
