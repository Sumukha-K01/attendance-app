import { useEffect, useState } from "react";
import axios from "axios";

export default function ManageClasses() {
  const [classrooms, setClassrooms] = useState([]);
  const [newClassName, setNewClassName] = useState("");

  const fetchClasses = async () => {
    const res = await axios.get("http://localhost:8000/api/classrooms/");
    setClassrooms(res.data);
  };

  useEffect(() => {
    fetchClasses();
  }, []);

  const handleAddClass = async () => {
    await axios.post("http://localhost:8000/api/classrooms/", { name: newClassName });
    setNewClassName("");
    fetchClasses();
  };

  const handleDeleteClass = async (id) => {
    await axios.delete(`http://localhost:8000/api/classrooms/${id}/`);
    fetchClasses();
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <h1 className="text-3xl font-bold mb-6">Manage Classes</h1>
      <div className="flex mb-6 gap-4">
        <input
          className="p-2 text-black rounded-lg"
          placeholder="Enter class name"
          value={newClassName}
          onChange={(e) => setNewClassName(e.target.value)}
        />
        <button
          onClick={handleAddClass}
          className="bg-blue-600 px-4 py-2 rounded-lg hover:bg-blue-700"
        >
          Add Class
        </button>
      </div>

      <ul className="space-y-3">
        {classrooms.map((cls) => (
          <li
            key={cls.id}
            className="bg-gray-800 p-4 rounded-lg flex justify-between items-center"
          >
            <span>{cls.name}</span>
            <button
              onClick={() => handleDeleteClass(cls.id)}
              className="bg-red-600 px-3 py-1 rounded hover:bg-red-700"
            >
              Delete
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
