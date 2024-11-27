import "./App.css";
import Modal from "react-bootstrap/Modal";
import "bootstrap/dist/css/bootstrap.min.css";
import TrafficLight from "./components/TrafficLight";
import { useState, useEffect } from "react";
import Button from "react-bootstrap/Button";
import { InputGroup, Form } from "react-bootstrap";
import Dropdown from "react-bootstrap/Dropdown";
import DropdownButton from "react-bootstrap/DropdownButton";
import { Preferences } from "@capacitor/preferences";
import { Capacitor } from "@capacitor/core";

function App() {
  const [deviceList, setDeviceList] = useState({});
  const [serverIp, setServerIp] = useState("");
  const [newServerIp, setNewServerIp] = useState("");
  const [serverModal, setServerModal] = useState(false);

  const handleServerIpChange = (event) => {
    setNewServerIp(event.target.value);
  };
  const openServerModal = () => {
    setServerModal(true);
  };
  const closeServerModal = () => {
    setServerModal(false);
  };

  // Set the server IP function
  async function setServerIP() {
    const fullServerIp = "http://" + newServerIp + ":5000"; // Construct the full server IP with port
    if (Capacitor.isNativePlatform()) {
      await Preferences.set({ key: "serverIP", value: fullServerIp });
    } else {
      localStorage.setItem("serverIP", fullServerIp);
    }
    setServerIp(fullServerIp); // Update state
    console.log("Server IP saved and updated:", fullServerIp);
    closeServerModal(); // Close the modal
  }

  // Get the server IP function
  async function getServerIP() {
    let savedIp = "";
    if (Capacitor.isNativePlatform()) {
      const { value } = await Preferences.get({ key: "serverIP" });
      savedIp = value;
    } else {
      savedIp = localStorage.getItem("serverIP");
    }
    if (savedIp) {
      setServerIp(savedIp);
      console.log("Retrieved Server IP:", savedIp);
    }
  }

  const fetchAllDevices = async () => {
    try {
      const response = await fetch(serverIp + `/getAllDevices/`);
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
    getServerIP();
    fetchAllDevices();
  }, [serverIp]);

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

  const addDevice = async () => {
    // Function to validate IP address format
    const isValidIP = (ip) => {
      const ipPattern = /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/; // Matches "1-3 digits . 1-3 digits . 1-3 digits . 1-3 digits"
      if (!ipPattern.test(ip)) return false; // If it doesn't match, it's invalid

      // Further check: ensure all parts are numbers between 0 and 255
      return ip.split(".").every((num) => {
        const n = Number(num);
        return n >= 0 && n <= 255;
      });
    };

    // Function to validate device name
    const isValidDeviceName = (name) => {
      const namePattern = /^[a-zA-Z0-9_-]+$/; // Allows only alphanumeric characters, underscores, and hyphens
      return namePattern.test(name);
    };

    // Validate newDeviceName
    if (!newDeviceName || !isValidDeviceName(newDeviceName)) {
      alert(
        "Invalid device name! Please use only letters, numbers, underscores, or hyphens, with no spaces."
      );
      return; // Stop execution if name is invalid
    }

    // Validate newDeviceIp
    if (!newDeviceIp || newDeviceIp.includes(" ") || !isValidIP(newDeviceIp)) {
      alert(
        "Invalid IP address! Please provide a valid IP (e.g., 192.168.0.1)."
      );
      return; // Stop execution if IP is invalid
    }

    try {
      const response = await fetch(serverIp + `/addDevice/${newDeviceName}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          type: "slave",
          ip: newDeviceIp,
        }), // Send device data as JSON
      });

      const result = await response.json();
      fetchAllDevices(); // Fetch updated list of devices

      if (response.ok) {
        alert(result.message); // Success message
      } else {
        alert(result.error); // Error message
      }
    } catch (error) {
      console.error("Error adding device:", error.message);
    }
    closeAddModal(); // Close the modal regardless of success or failure
  };
  const handleNewDeviceIpChange = (event) => {
    setNewDeviceIp(event.target.value);
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
        serverIp + `/removeDevice/${removeDeviceKey}`,
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
    fetchAllDevices();
    closeCloseModal();
  };

  return (
    <div className="App">
      <div className="controlHeader">
        <Button onClick={openServerModal} variant="warning">
          Server
        </Button>
        <Button onClick={openAddModal} variant="primary">
          Add
        </Button>
        <Button onClick={openCloseModal} variant="danger">
          Remove
        </Button>
      </div>
      <div className="ManualControls">
        {/* Dynamically render TrafficLights */}
        {Object.keys(deviceList).length > 0 ? (
          Object.keys(deviceList)
            .sort((a, b) => (a === "Master" ? -1 : b === "Master" ? 1 : 0)) // Sort "Master" to the top
            .map((key) => (
              <TrafficLight
                key={key} // use device key as the key for React
                className={key} // You can use the key for className or any other prop
                deviceName={key} // Pass the key as deviceName
                serverIp={serverIp}
              />
            ))
        ) : (
          <p>No devices available</p> // Show a message if no devices exist
        )}
      </div>
      {/* Server popup */}
      <Modal
        show={serverModal}
        onHide={closeServerModal}
        backdrop="static"
        keyboard={false}
        centered
      >
        <Modal.Header closeButton>
          <Modal.Title>Set Server</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <InputGroup size="sm" className="mb-3">
            <InputGroup.Text id="inputGroup-sizing-sm">
              Server Ip
            </InputGroup.Text>
            <Form.Control
              placeholder="0.0.0.0"
              aria-label="small"
              aria-describedby="inputGroup-sizing-sm"
              onChange={handleServerIpChange}
              value={newServerIp}
            />
          </InputGroup>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={closeServerModal}>
            Cancel
          </Button>
          <Button onClick={setServerIP} variant="primary">
            Set
          </Button>
        </Modal.Footer>
      </Modal>

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
              Object.keys(deviceList).map((key) =>
                key !== "Master" ? (
                  <Dropdown.Item
                    key={key}
                    as="button" // Turn this into a button to avoid refresh
                    eventKey={key} // Pass the key as the eventKey
                  >
                    {key}
                  </Dropdown.Item>
                ) : (
                  <></>
                )
              )
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
