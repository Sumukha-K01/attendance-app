import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { base_url } from "../App";
const Classes = () => {
  const [classes, setClasses] = useState([]);
  const navigate = useNavigate();
  const accessToken = localStorage.getItem("access_token");

  useEffect(() => {
    axios
      .get(`${base_url}/classrooms/`, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      })
      .then((res) => setClasses(res.data))
      .catch((err) => {
        console.error("Error loading classes", err);
        alert("Failed to load classes: " + (err.response?.data?.detail || err.message));
      });
  }, [accessToken]);

  const handleClick = (classId) => {
    navigate(`/attendance/${classId}`);
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col items-center p-10">
      <h2 className="text-3xl font-bold mb-10">Select a Class</h2>

      <div className="flex flex-col gap-4 w-full max-w-xs">
        {classes.map((cls) => (
          <button
            key={cls.id}
            onClick={() => handleClick(cls.id)}
            className="bg-blue-600 text-white py-3 rounded-xl shadow-md hover:bg-blue-700 hover:scale-105 transition-transform duration-300"
          >
            {cls.name} (ID: {cls.id})
          </button>
        ))}
      </div>
    </div>
  );
};

export default Classes;
