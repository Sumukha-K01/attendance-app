import React, { useEffect, useState } from "react";
import axios from "axios";

const ViewAttendance = () => {
  const [classes, setClasses] = useState([]);
  const [selectedClass, setSelectedClass] = useState("");
  const [date, setDate] = useState("");
  const [attendance, setAttendance] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const accessToken = localStorage.getItem("access_token");

  useEffect(() => {
    // Fetch all classes
    axios
      .get("http://127.0.0.1:8000/api/classrooms/", {
        headers: { Authorization: `Bearer ${accessToken}` },
      })
      .then((res) => setClasses(res.data))
      .catch((err) => setError("Failed to load classes"));
  }, [accessToken]);

  const fetchAttendance = async () => {
    if (!selectedClass || !date) return;
    setLoading(true);
    setError(null);
    try {
      const res = await axios.get(
        `http://127.0.0.1:8000/api/attendance/by_class_date/?class_id=${selectedClass}&date=${date}`,
        { headers: { Authorization: `Bearer ${accessToken}` } }
      );
      setAttendance(res.data);
    } catch (err) {
      setError("Failed to fetch attendance");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col items-center p-10">
      <h2 className="text-3xl font-bold mb-6">View Attendance</h2>
      <div className="flex gap-4 mb-6">
        <select
          value={selectedClass}
          onChange={(e) => setSelectedClass(e.target.value)}
          className="p-2 rounded text-black"
        >
          <option value="">Select Class</option>
          {classes.map((cls) => (
            <option key={cls.id} value={cls.id}>
              {cls.name}
            </option>
          ))}
        </select>
        <input
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          className="p-2 rounded text-black"
        />
        <button
          onClick={fetchAttendance}
          className="bg-blue-600 px-4 py-2 rounded hover:bg-blue-700"
        >
          View
        </button>
      </div>
      {loading ? (
        <div>Loading...</div>
      ) : error ? (
        <div className="bg-red-800 px-4 py-2 rounded">{error}</div>
      ) : attendance.length > 0 ? (
        <table className="w-full max-w-xl bg-gray-800 rounded-lg">
          <thead>
            <tr>
              <th className="p-2">Student</th>
              <th className="p-2">Status</th>
            </tr>
          </thead>
          <tbody>
            {attendance.map((a) => (
              <tr key={a.id}>
                <td className="p-2">{a.student_name}</td>
                <td className="p-2">
                  {a.status === "present" ? (
                    <span className="text-green-400 font-bold">Present</span>
                  ) : (
                    <span className="text-red-400 font-bold">Absent</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <div>No attendance records found.</div>
      )}
    </div>
  );
};

export default ViewAttendance;
