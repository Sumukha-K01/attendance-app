import React, { useEffect, useState } from "react";
import axios from "axios";

const AddStudent = () => {
  const [name, setName] = useState("");
  const [rollNumber, setRollNumber] = useState("");
  const [classrooms, setClassrooms] = useState([]);
  const [selectedClass, setSelectedClass] = useState("");

  const accessToken = localStorage.getItem("access_token");

  useEffect(() => {
    const fetchClasses = async () => {
      try {
        const response = await axios.get("http://127.0.0.1:8000/api/classrooms/", {
          headers: { Authorization: `Bearer ${accessToken}` },
        });
        setClassrooms(response.data);
      } catch (error) {
        console.error("Failed to fetch classes", error);
      }
    };

    fetchClasses();
  }, [accessToken]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post("http://127.0.0.1:8000/api/students/", {
        name,
        roll_number: parseInt(rollNumber),
        classroom: parseInt(selectedClass),
      }, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });

      alert("Student added successfully!");
      setName("");
      setRollNumber("");
      setSelectedClass("");
    } catch (error) {
      alert("Failed to add student.");
      console.error(error);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
      <form onSubmit={handleSubmit} className="bg-white p-8 rounded shadow-md w-full max-w-md">
        <h2 className="text-xl font-bold mb-4">Add Student</h2>
        <input
          type="text"
          placeholder="Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="w-full border p-2 mb-3 rounded"
          required
        />
        <input
          type="number"
          placeholder="Roll Number"
          value={rollNumber}
          onChange={(e) => setRollNumber(e.target.value)}
          className="w-full border p-2 mb-3 rounded"
          required
        />
        <select
          value={selectedClass}
          onChange={(e) => setSelectedClass(e.target.value)}
          className="w-full border p-2 mb-3 rounded"
          required
        >
          <option value="">Select Class</option>
          {classrooms.map((cls) => (
            <option key={cls.id} value={cls.id}>
              {cls.name}
            </option>
          ))}
        </select>
        <button
          type="submit"
          className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 transition"
        >
          Add Student
        </button>
      </form>
    </div>
  );
};

export default AddStudent;
