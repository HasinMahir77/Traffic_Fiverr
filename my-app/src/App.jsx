import "./App.css";
import Modal from "react-bootstrap/Modal";
import "bootstrap/dist/css/bootstrap.min.css";
import TrafficLight from "./components/TrafficLight";
import { useState, useEffect } from "react";
import Button from "react-bootstrap/Button";
import { InputGroup, Form } from "react-bootstrap";
import Dropdown from "react-bootstrap/Dropdown";
import DropdownButton from "react-bootstrap/DropdownButton";

function App() {
  const [deviceList, setDeviceList] = useState({});

  const fetchAllDevices = async () => {
    try {
      const response = await fetch(`http://127.0.0.1:5000/getAllDevices/`);
      if (!response.ok) {
        throw new Error(`Error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json(); // Await the JSON data
      console.log(data); // Log the data
      setDeviceList(data); // Update the state with the fetched data
    } catch (err) {
      console.log(err.message); // Log the error message
    }
  };

  useEffect(() => {
    let interval;

    if (Object.keys(deviceList).length === 0) {
      interval = setInterval(() => {
        fetchAllDevices(); // Try fetching devices every 0.5 seconds
      }, 500);
    }
    // Clear the interval if data is received or on component unmount
    if (Object.keys(deviceList).length > 0) {
      clearInterval(interval);
    }

    return () => clearInterval(interval); // Cleanup interval on component unmount
  }, [deviceList]); // Effect runs when deviceList changes

  // Mode States
  const [modeModal, setModeModal] = useState(false);

  const openModeModal = () => {
    setModeModal(true);
  };
  const closeModeModal = () => {
    setModeModal(false);
  };
  const [mode, setMode] = useState("Manual");
  const handleModeChange = (newMode) => {
    setMode(newMode);
    closeModeModal();
  };

  // Add Device States
  const [addModal, setAddModal] = useState(false);
  const [newDeviceName, setNewDeviceName] = useState("");
  const handleNewDeviceNameChange = (event) => {
    setNewDeviceName(event.target.value);
  };
  const [newDeviceIp, setNewDeviceIp] = useState("");
  const handleNewDeviceIpChange = (event) => {
    setNewDeviceIp(event.target.value);
  };
  const addDevice = async () => {
    try {
      const response = await fetch(
        `http://127.0.0.1:5000/addDevice/${newDeviceName}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            type: "slave",
            ip: newDeviceIp,
            status: 1,
          }), // Send device data as JSON
        }
      );

      const result = await response.json();
      fetchAllDevices();
      if (response.ok) {
        alert(result.message); // Success message
      } else {
        alert(result.error); // Error message
      }
    } catch (error) {
      console.error("Error adding device:", error.message);
    }
    closeAddModal();
  };
  const openAddModal = () => {
    setAddModal(true);
  };
  const closeAddModal = () => {
    setNewDeviceIp("");
    setNewDeviceName("");
    setAddModal(false);
  };

  // Remove Device States
  const [closeModal, setCloseModal] = useState(false);
  const [removeDeviceKey, setRemoveDeviceKey] = useState("");
  const openCloseModal = () => {
    setCloseModal(true);
  };
  const closeCloseModal = () => {
    setCloseModal(false);
    setRemoveDeviceKey("");
  };
  const handleRemoveDeviceSelect = (key) => {
    setRemoveDeviceKey(key);
    console.log("Selected: " + key);
  };
  const removeDevice = async () => {
    try {
      const response = await fetch(
        `http://127.0.0.1:5000/removeDevice/${removeDeviceKey}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json", // Set headers as needed
            // Add other headers if required (e.g., Authorization)
          },
        }
      );
      const result = await response.json();
      if (response.ok) {
        alert(result.message); // Success message
      } else {
        alert(result.error); // Error message
      }
    } catch (error) {
      console.error("Error adding device:", error.message);
    }
    closeCloseModal();
  };

  return (
    <div className="App">
      <div className="controlHeader">
        <Button onClick={openAddModal} variant="primary">
          Add Device
        </Button>
        <Button onClick={openCloseModal} variant="danger">
          Remove Device
        </Button>
      </div>
      <div className="ManualControls">
        <div className="header">
          <span className="modeLabel">{mode} mode</span>
        </div>

        <TrafficLight className="M" device="0" />
        <TrafficLight className="1" device="1" />
        <TrafficLight className="2" device="2" />
        <TrafficLight className="3" device="3" />
        <TrafficLight className="4" device="4" />
        <TrafficLight className="5" device="5" />
        <div className="footer">
          <Button variant="secondary" onClick={openModeModal}>
            Select Mode
          </Button>
          <Button variant="primary">Save</Button>
        </div>
      </div>

      {/* Mode selection popup */}
      <Modal
        keyboard={false}
        show={modeModal}
        backdrop="static"
        onHide={closeModeModal}
        centered
      >
        <Modal.Header className="bg-dark text-light">
          <Modal.Title>Select Mode</Modal.Title>
        </Modal.Header>
        <Modal.Body className="bg-dark text-light">
          <Button
            variant="dark"
            onClick={() => handleModeChange("Auto")}
            className="w-100 mb-2"
          >
            Auto
          </Button>
          <Button
            variant="dark"
            onClick={() => handleModeChange("Manual")}
            className="w-100"
          >
            Manual
          </Button>
        </Modal.Body>
      </Modal>

      {/* Add Device popup */}
      <Modal
        show={addModal}
        onHide={closeAddModal}
        backdrop="static"
        keyboard={false}
        centered
      >
        <Modal.Header closeButton>
          <Modal.Title>Add Device</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <InputGroup size="sm" className="mb-3">
            <InputGroup.Text id="inputGroup-sizing-sm">Name</InputGroup.Text>
            <Form.Control
              placeholder="Device X"
              aria-label="small"
              aria-describedby="inputGroup-sizing-sm"
              onChange={handleNewDeviceNameChange}
              value={newDeviceName}
            />
          </InputGroup>
          <InputGroup size="sm" className="mb-3">
            <InputGroup.Text id="inputGroup-sizing-sm">
              IP Address
            </InputGroup.Text>
            <Form.Control
              placeholder="0.0.0.0"
              aria-label="small"
              aria-describedby="inputGroup-sizing-sm"
              onChange={handleNewDeviceIpChange}
              value={newDeviceIp}
            />
          </InputGroup>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={closeAddModal}>
            Cancel
          </Button>
          <Button onClick={addDevice} variant="primary">
            Add
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Remove Device popup */}
      <Modal
        show={closeModal}
        onHide={closeCloseModal}
        backdrop="static"
        keyboard={false}
        centered
      >
        <Modal.Header closeButton>
          <Modal.Title>Remove Device</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <DropdownButton
            onSelect={handleRemoveDeviceSelect}
            id="dropdown-basic-button"
            title={removeDeviceKey === "" ? "Select Device" : removeDeviceKey}
          >
            {Object.keys(deviceList).length > 0 ? (
              Object.keys(deviceList).map((key) => (
                <Dropdown.Item
                  key={key}
                  as="button" // Turn this into a button to avoid refresh
                  eventKey={key} // Pass the key as the eventKey
                >
                  {key}
                </Dropdown.Item>
              ))
            ) : (
              <Dropdown.Item disabled>No devices available</Dropdown.Item>
            )}
          </DropdownButton>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={closeCloseModal}>
            Cancel
          </Button>
          <Button variant="danger" onClick={removeDevice}>
            Remove
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
}

export default App;
