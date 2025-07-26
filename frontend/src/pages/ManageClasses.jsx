// src/pages/ManageClasses.jsx
import React, { useState, useEffect } from "react";
import axios from "axios";

const ManageClasses = () => {
  const [className, setClassName] = useState("");
  const [classes, setClasses] = useState([]);
  const accessToken = localStorage.getItem("access_token");

  const fetchClasses = async () => {
    try {
      const response = await axios.get("http://127.0.0.1:8000/api/classrooms/", {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });
      setClasses(response.data);
    } catch (error) {
      console.error("Error fetching classes", error);
      alert("Failed to fetch classes: " + (error.response?.data?.detail || error.message));
    }
  };

  const handleAddClass = async () => {
    if (!className.trim()) return;

    try {
      await axios.post(
        "http://127.0.0.1:8000/api/classrooms/",
        { name: className },
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        }
      );
      setClassName("");
      fetchClasses();
    } catch (error) {
      console.error("Error adding class", error);
      alert("Failed to add class: " + (error.response?.data?.detail || error.message));
    }
  };

  const handleDeleteClass = async (id) => {
    try {
      await axios.delete(`http://127.0.0.1:8000/api/classrooms/${id}/`, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });
      fetchClasses();
    } catch (error) {
      console.error("Error deleting class", error);
      alert("Failed to delete class: " + (error.response?.data?.detail || error.message));
    }
  };

  useEffect(() => {
    fetchClasses();
  }, []);

  return (
    <div className="p-6 max-w-xl mx-auto">
      <h2 className="text-2xl font-bold mb-4">Manage Classes</h2>
      <div className="flex gap-2 mb-4">
        <input
          type="text"
          value={className}
          onChange={(e) => setClassName(e.target.value)}
          placeholder="Enter class name"
          className="border px-2 py-1 rounded w-full"
        />
        <button
          onClick={handleAddClass}
          className="bg-blue-600 text-white px-4 py-2 rounded"
        >
          Add Class
        </button>
      </div>

      <ul className="space-y-2">
        {classes.map((cls) => (
          <li
            key={cls.id}
            className="flex justify-between items-center bg-gray-100 p-2 rounded"
          >
            <span>{cls.name}</span>
            <button
              onClick={() => handleDeleteClass(cls.id)}
              className="text-red-600 font-semibold"
            >
              Delete
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ManageClasses;
