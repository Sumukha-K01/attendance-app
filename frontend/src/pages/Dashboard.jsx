import { useNavigate } from "react-router-dom";

export default function Dashboard() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8 flex flex-col items-center">
      <h1 className="text-3xl font-bold mb-8">Welcome to Dashboard</h1>
      <div className="flex flex-col gap-4 w-full max-w-sm">
        <button onClick={() => navigate("/class-attendance")} className="bg-blue-600 hover:bg-blue-700 p-4 rounded-xl text-center transition">Class Attendance</button>
        <button onClick={() => navigate("/add-student")} className="bg-green-600 hover:bg-green-700 p-4 rounded-xl text-center transition">Add Student</button>
        <button onClick={() => navigate("/manage-classes")} className="bg-purple-600 hover:bg-purple-700 p-4 rounded-xl text-center transition">Manage Classes</button>
        <button onClick={() => navigate("/view-attendance")} className="bg-yellow-600 hover:bg-yellow-700 p-4 rounded-xl text-center transition">View Attendance</button>
      </div>
    </div>
  );
}
