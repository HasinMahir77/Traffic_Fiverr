import React, { useState, useEffect } from "react";
import "./TrafficLight.css";
import Button from "react-bootstrap/Button";
import Modal from "react-bootstrap/Modal";
import { InputGroup, Form } from "react-bootstrap";
import "bootstrap/dist/css/bootstrap.min.css";

const TrafficLight = ({ serverIp, deviceName, initialSequence }) => {
  const [currentSequence, setCurrentSequence] = useState(initialSequence);
  const [glow, setGlow] = useState("");
  useEffect(() => {
    // Set the interval to call fetchGlow every 500ms
    const interval = setInterval(() => {
      fetchGlow();
    }, 500);

    // Cleanup the interval on component unmount
    return () => clearInterval(interval);
  }, []); // Empty dependency array ensures this effect only runs once, on mount

  const fetchGlow = async () => {
    try {
      const response = await fetch(serverIp + "/get_current_color");
      if (!response.ok) {
        throw new Error(`Error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json(); // Await the JSON data
      console.log(data); // Log the data
      setGlow(data); // Update the state with the fetched data
      setActiveLight(glow.color());
      setTime(timeLeft);
    } catch (err) {
      console.log(err.message); // Log the error message
    }
  };

  function capitalizeFirstLetter(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
  }

  // Light control
  const [activeLight, setActiveLight] = useState("");
  const handleClick = (color) => {
    setActiveLight(color);
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
        setCurrentSequence(data);
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
          <Button
            className="sequenceButton"
            variant="warning"
            onClick={openModal}
          >
            Sequence
          </Button>
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
