import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';

const FormList = () => {
  const [forms, setForms] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchForms();
  }, []);

  const fetchForms = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('/api/v1/forms', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setForms(response.data.forms);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to fetch forms');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (formId) => {
    if (!window.confirm('Are you sure you want to delete this form?')) return;

    try {
      const token = localStorage.getItem('token');
      await axios.delete(`/api/v1/forms/${formId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setForms(forms.filter(form => form.form_id !== formId));
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to delete form');
    }
  };

  const handlePublish = async (formId, isPublished) => {
    try {
      const token = localStorage.getItem('token');
      await axios.put(`/api/v1/forms/${formId}/publish`, 
        { is_published: !isPublished },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setForms(forms.map(form => 
        form.form_id === formId 
          ? { ...form, is_published: !isPublished }
          : form
      ));
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to update form status');
    }
  };

  if (loading) return <div className="text-center py-4">Loading...</div>;
  if (error) return <div className="text-red-600 text-center py-4">{error}</div>;

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">My Forms</h1>
        <Link
          to="/forms/create"
          className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
        >
          Create New Form
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {forms.map(form => (
          <div key={form.form_id} className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-2">{form.title}</h2>
            <p className="text-gray-600 mb-4">Responses: {form.response_count}</p>
            <div className="flex justify-between items-center">
              <span className={`px-2 py-1 rounded text-sm ${
                form.is_published 
                  ? 'bg-green-100 text-green-800'
                  : 'bg-yellow-100 text-yellow-800'
              }`}>
                {form.is_published ? 'Published' : 'Draft'}
              </span>
              <div className="space-x-2">
                <button
                  onClick={() => handlePublish(form.form_id, form.is_published)}
                  className="text-sm text-indigo-600 hover:text-indigo-800"
                >
                  {form.is_published ? 'Unpublish' : 'Publish'}
                </button>
                <Link
                  to={`/forms/${form.form_id}/edit`}
                  className="text-sm text-indigo-600 hover:text-indigo-800"
                >
                  Edit
                </Link>
                <button
                  onClick={() => handleDelete(form.form_id)}
                  className="text-sm text-red-600 hover:text-red-800"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default FormList; 