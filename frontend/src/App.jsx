import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Classes from "./pages/Classes";
import Attendance from "./pages/Attendance";
import AddStudent from "./pages/AddStudent";

import ManageClasses from "./pages/ManageClasses";
import ViewAttendance from "./pages/ViewAttendance";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/classes" element={<Classes />} />
        <Route path="/attendance/:classId" element={<Attendance />} />
        <Route path="/add-student" element={<AddStudent />} />
        <Route path="/manage-classes" element={<ManageClasses />} />
        <Route path="/class-attendance" element={<Classes />} />
        {/* <Route path="/house-attendance" element={<Houses />} /> */}
        <Route path="/view-attendance" element={<ViewAttendance />} />
      </Routes>
    </BrowserRouter>
  );
}

export const base_url = "http://127.0.0.1:8000/api";
export default App;
