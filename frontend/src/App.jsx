import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Classes from "./pages/Classes";
import Attendance from "./pages/Attendance";
import AddStudent from "./pages/AddStudent";
import ManageClasses from "./pages/ManageClasses";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/classes" element={<Classes />} />
        <Route path="/attendance/:className" element={<Attendance />} />
        <Route path="/add-student" element={<AddStudent />} />
        <Route path="/manage-classes" element={<ManageClasses />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
