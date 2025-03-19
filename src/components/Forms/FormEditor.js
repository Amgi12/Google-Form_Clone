import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate, useParams } from 'react-router-dom';

const FormEditor = () => {
  const { formId } = useParams();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    questions: []
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (formId) {
      fetchForm();
    }
  }, [formId]);

  const fetchForm = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`/api/v1/forms/${formId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setFormData({
        title: response.data.title,
        description: response.data.description,
        questions: response.data.questions
      });
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to fetch form');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      if (formId) {
        await axios.put(`/api/v1/forms/${formId}`, formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
      } else {
        await axios.post('/api/v1/forms', formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
      }
      navigate('/forms');
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to save form');
    } finally {
      setLoading(false);
    }
  };

  const addQuestion = () => {
    setFormData({
      ...formData,
      questions: [
        ...formData.questions,
        {
          question_text: '',
          is_required: false,
          display_order: formData.questions.length
        }
      ]
    });
  };

  const updateQuestion = (index, field, value) => {
    const updatedQuestions = [...formData.questions];
    updatedQuestions[index] = {
      ...updatedQuestions[index],
      [field]: value
    };
    setFormData({
      ...formData,
      questions: updatedQuestions
    });
  };

  const removeQuestion = (index) => {
    setFormData({
      ...formData,
      questions: formData.questions.filter((_, i) => i !== index)
    });
  };

  const reorderQuestions = (fromIndex, toIndex) => {
    const questions = [...formData.questions];
    const [movedQuestion] = questions.splice(fromIndex, 1);
    questions.splice(toIndex, 0, movedQuestion);
    
    // Update display order
    const updatedQuestions = questions.map((q, i) => ({
      ...q,
      display_order: i
    }));

    setFormData({
      ...formData,
      questions: updatedQuestions
    });
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">
        {formId ? 'Edit Form' : 'Create New Form'}
      </h1>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Form Title
          </label>
          <input
            type="text"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Description
          </label>
          <textarea
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            rows="3"
          />
        </div>

        <div>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-medium">Questions</h2>
            <button
              type="button"
              onClick={addQuestion}
              className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
            >
              Add Question
            </button>
          </div>

          <div className="space-y-4">
            {formData.questions.map((question, index) => (
              <div
                key={index}
                className="bg-white p-4 rounded-lg shadow border border-gray-200"
              >
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <input
                      type="text"
                      value={question.question_text}
                      onChange={(e) => updateQuestion(index, 'question_text', e.target.value)}
                      placeholder="Question text"
                      className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                      required
                    />
                  </div>
                  <div className="flex items-center space-x-4 ml-4">
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={question.is_required}
                        onChange={(e) => updateQuestion(index, 'is_required', e.target.checked)}
                        className="rounded border-gray-300 text-indigo-600 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                      />
                      <span className="ml-2 text-sm text-gray-700">Required</span>
                    </label>
                    <button
                      type="button"
                      onClick={() => removeQuestion(index)}
                      className="text-red-600 hover:text-red-800"
                    >
                      Remove
                    </button>
                  </div>
                </div>

                <div className="flex space-x-2">
                  {index > 0 && (
                    <button
                      type="button"
                      onClick={() => reorderQuestions(index, index - 1)}
                      className="text-gray-600 hover:text-gray-800"
                    >
                      Move Up
                    </button>
                  )}
                  {index < formData.questions.length - 1 && (
                    <button
                      type="button"
                      onClick={() => reorderQuestions(index, index + 1)}
                      className="text-gray-600 hover:text-gray-800"
                    >
                      Move Down
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="flex justify-end space-x-4">
          <button
            type="button"
            onClick={() => navigate('/forms')}
            className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading}
            className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50"
          >
            {loading ? 'Saving...' : 'Save Form'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default FormEditor; 