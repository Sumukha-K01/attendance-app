// src/pages/Classes.jsx
import React from "react";
import { useNavigate } from "react-router-dom";

const Classes = () => {
  const navigate = useNavigate();
  const classes = Array.from({ length: 10 }, (_, i) => `Class ${i + 1}`);

  const handleClick = (className) => {
    navigate(`/attendance/${className}`);
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col items-center p-10">
      <h2 className="text-3xl font-bold mb-10">Select a Class</h2>

      <div className="flex flex-col gap-4 w-full max-w-xs">
        {classes.map((className) => (
          <button
            key={className}
            onClick={() => handleClick(className)}
            className="bg-blue-600 text-white py-3 rounded-xl shadow-md hover:bg-blue-700 hover:scale-105 transition-transform duration-300"
          >
            {className}
          </button>
        ))}
      </div>
    </div>
  );
};

export default Classes;
