// src/pages/Attendance.jsx

import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";
import { base_url } from "../App";

// Status options
const OPTIONS = [
  { label: "Present", value: "present" },
  { label: "Absent", value: "absent" },
  { label: "Leave", value: "leave" },
  { label: "Leave-SW", value: "leave-sw" },
  { label: "On-Duty", value: "on-duty" },
];

// Attendance types mapping
const ATT_TYPE_VALUES = {
  morning: "morning",
  evening: "evening_att",
};

const Attendance = () => {
  const { classId } = useParams();
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [attendance, setAttendance] = useState({});
  const [successMsg, setSuccessMsg] = useState("");
  const [attType, setAttType] = useState("morning");  // Default att_type 'morning'
  const accessToken = localStorage.getItem("access_token");

  // Function to fetch students and attendance
  const fetchData = () => {
    if (!classId) return;
    setLoading(true);
    setError(null);
    const today = new Date().toISOString().slice(0, 10);

    // First fetch students
    axios
      .get(`${base_url}/classrooms/${classId}/students/`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      })
      .then((res) => {
        setStudents(res.data);

        // Then fetch attendance for selected att_type and today
        return axios.get(
          `${base_url}/attendance/?classroom=${classId}&att_type=${ATT_TYPE_VALUES[attType]}&date=${today}`,
          { headers: { Authorization: `Bearer ${accessToken}` } }
        );
      })
      .then((attRes) => {
        // attRes.data expected: array of {student: id, status}
        const attObj = {};
        if (Array.isArray(attRes.data)) {
          attRes.data.forEach((a) => {
            attObj[a.student] = a.status;
          });
        }
        // Set attendance; default to 'present' if no value returned
        setAttendance(() => {
          const obj = {};
          students.forEach((student) => {
            obj[student.id] = attObj[student.id] || "present";
          });
          return obj;
        });
        setLoading(false);
      })
      .catch((err) => {
        if (err.response) {
          setError(
            `Failed to load data: ${err.response.status} ${err.response.statusText} - ${JSON.stringify(
              err.response.data
            )}`
          );
        } else {
          setError("Failed to load data: " + err.message);
        }
        setLoading(false);
      });
  };

  // Fetch data on mount and whenever attType or classId changes
  React.useEffect(() => {
    fetchData();
  }, [attType, classId]);

  const handleAttendanceChange = (studentId, status) => {
    setAttendance((prev) => ({ ...prev, [studentId]: status }));
  };

  const submitAttendance = async (e) => {
    e.preventDefault();
    setLoading(true);
    setSuccessMsg("");
    setError(null);
    try {
      const today = new Date().toISOString().slice(0, 10);
      
      const attendanceData = students.map((student) => ({
        student: student.id,
        date: today,
        status: attendance[student.id],
        att_type: ATT_TYPE_VALUES[attType],  // include att_type in POST as well, if your BE expects it
      }));
      await axios.post(`${base_url}/attendance/`, attendanceData, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      setSuccessMsg("Attendance marked successfully!");
    } catch (err) {
      setError(
        "Failed to mark attendance: " +
          (err.response?.data?.detail || err.message)
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-black text-white flex flex-col items-center justify-center p-6">
      <h2 className="text-4xl font-bold mb-4">Class Attendance</h2>
      
      {/* Attendance type selector */}
      <div className="mb-6 flex gap-4">
        {["morning", "evening"].map((type) => (
          <button
            key={type}
            type="button"
            className={`px-4 py-2 rounded ${
              attType === type
                ? "bg-green-600 text-white font-bold"
                : "bg-gray-700 text-gray-200"
            }`}
            onClick={() => setAttType(type)}
          >
            {type === "morning" ? "Morning" : "Evening"}
          </button>
        ))}
      </div>

      {successMsg && (
        <div className="bg-green-700 px-4 py-2 rounded mb-2">{successMsg}</div>
      )}

      {loading ? (
        <div className="animate-pulse bg-blue-800 px-6 py-3 rounded-lg shadow-xl">
          Loading student data...
        </div>
      ) : error ? (
        <div className="bg-red-800 px-6 py-3 rounded-lg shadow-xl">{error}</div>
      ) : (
        <div className="w-full max-w-md">
          <h3 className="text-2xl font-semibold mb-4">Students</h3>
          <form onSubmit={submitAttendance}>
            <ul className="flex flex-col gap-3">
              {students.length === 0 ? (
                <li className="text-gray-400">
                  No students found for this class.
                </li>
              ) : (
                students.map((student) => (
                  <li
                    key={student.id}
                    className="flex flex-col gap-2 p-3 bg-gray-800 rounded shadow"
                  >
                    <span>
                      {student.name} (Classroom ID: {student.classroom})
                    </span>
                    <div className="flex gap-2 mt-1">
                      {OPTIONS.map((opt) => (
                        <button
                          type="button"
                          key={opt.value}
                          className={`px-3 py-1 rounded border ${
                            attendance[student.id] === opt.value
                              ? "bg-green-600 border-green-500 text-white font-bold"
                              : "bg-gray-700 border-gray-500 text-gray-100"
                          } transition-colors duration-100`}
                          onClick={() =>
                            handleAttendanceChange(student.id, opt.value)
                          }
                          tabIndex={0}
                        >
                          {opt.label}
                        </button>
                      ))}
                    </div>
                  </li>
                ))
              )}
            </ul>
            <button
              type="submit"
              className="bg-green-600 text-white px-4 py-2 rounded mt-4 hover:bg-green-700"
            >
              Submit Attendance
            </button>
          </form>
        </div>
      )}
    </div>
  );
};

export default Attendance;
