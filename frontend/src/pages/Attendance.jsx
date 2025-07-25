// src/pages/Attendance.jsx
import React from "react";
import { useParams } from "react-router-dom";

const Attendance = () => {
  const { className } = useParams();

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-black text-white flex flex-col items-center justify-center p-6">
      <h2 className="text-4xl font-bold mb-4">{className} Attendance</h2>
      <p className="text-lg text-gray-300 mb-8">
        (Coming soon: student list & attendance marking)
      </p>
      <div className="animate-pulse bg-blue-800 px-6 py-3 rounded-lg shadow-xl">
        Loading student data...
      </div>
    </div>
  );
};

export default Attendance;
