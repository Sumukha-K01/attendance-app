// src/pages/Attendance.jsx
import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";

const Attendance = () => {
  const { classId } = useParams();
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [marking, setMarking] = useState({});
  const [successMsg, setSuccessMsg] = useState("");
  const accessToken = localStorage.getItem("access_token");


  useEffect(() => {
    if (!classId) return;
    setLoading(true);
    axios
      .get(`http://127.0.0.1:8000/api/classrooms/${classId}/students/`, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      })
      .then((res) => {
        setStudents(res.data);
        setLoading(false);
      })
      .catch((err) => {
        if (err.response) {
          setError(`Failed to load students: ${err.response.status} ${err.response.statusText} - ${JSON.stringify(err.response.data)}`);
        } else {
          setError("Failed to load students: " + err.message);
        }
        setLoading(false);
      });
  }, [classId, accessToken]);

  if (!classId) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 to-black text-white flex flex-col items-center justify-center p-6">
        <h2 className="text-4xl font-bold mb-4">Class Attendance</h2>
        <div className="bg-red-800 px-6 py-3 rounded-lg shadow-xl">Error: No classId provided in URL. Please select a class from the class list.</div>
      </div>
    );
  }

  const markAttendance = async (studentId, status) => {
    setMarking((prev) => ({ ...prev, [studentId]: true }));
    setSuccessMsg("");
    setError(null);
    try {
      const today = new Date().toISOString().slice(0, 10);
      await axios.post(
        "http://127.0.0.1:8000/api/attendance/",
        {
          student: studentId,
          date: today,
          status,
        },
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        }
      );
      setSuccessMsg(`Marked as ${status} successfully!`);
    } catch (err) {
      setError("Failed to mark attendance: " + (err.response?.data?.detail || err.message));
    } finally {
      setMarking((prev) => ({ ...prev, [studentId]: false }));
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-black text-white flex flex-col items-center justify-center p-6">
      <h2 className="text-4xl font-bold mb-4">Class Attendance</h2>
      {successMsg && <div className="bg-green-700 px-4 py-2 rounded mb-2">{successMsg}</div>}
      {loading ? (
        <div className="animate-pulse bg-blue-800 px-6 py-3 rounded-lg shadow-xl">Loading student data...</div>
      ) : error ? (
        <div className="bg-red-800 px-6 py-3 rounded-lg shadow-xl">{error}</div>
      ) : (
        <div className="w-full max-w-md">
          <h3 className="text-2xl font-semibold mb-4">Students</h3>
          <ul className="flex flex-col gap-3">
            {students.length === 0 ? (
              <li className="text-gray-400">No students found for this class.</li>
            ) : (
              students.map((student) => (
                <li key={student.id} className="bg-gray-800 px-4 py-2 rounded-lg flex items-center justify-between gap-2">
                  <span>{student.name} (Classroom ID: {student.classroom})</span>
                  <div className="flex gap-2">
                    <button
                      className="bg-green-600 text-white px-3 py-1 rounded hover:bg-green-700 disabled:opacity-50"
                      disabled={marking[student.id]}
                      onClick={() => markAttendance(student.id, "present")}
                    >
                      Present
                    </button>
                    <button
                      className="bg-red-600 text-white px-3 py-1 rounded hover:bg-red-700 disabled:opacity-50"
                      disabled={marking[student.id]}
                      onClick={() => markAttendance(student.id, "absent")}
                    >
                      Absent
                    </button>
                  </div>
                </li>
              ))
            )}
          </ul>
        </div>
      )}
    </div>
  );
};

export default Attendance;
