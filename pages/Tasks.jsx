import { useState, useEffect, useCallback } from 'react';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

function getToken() {
  return localStorage.getItem('access_token');
}

async function apiFetch(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${getToken()}`,
      ...options.headers,
    },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Request failed: ${res.status}`);
  }
  return res.status === 204 ? null : res.json();
}

const STATUS_LABELS = { pending: 'Pending', in_progress: 'In Progress', completed: 'Completed' };
const PRIORITY_LABELS = { low: 'Low', medium: 'Medium', high: 'High' };
const STATUS_COLORS = { pending: '#f59e0b', in_progress: '#3b82f6', completed: '#22c55e' };
const PRIORITY_COLORS = { low: '#6b7280', medium: '#f97316', high: '#ef4444' };

function Badge({ label, color }) {
  return (
    <span style={{
      display: 'inline-block',
      padding: '2px 10px',
      borderRadius: 12,
      fontSize: 12,
      fontWeight: 600,
      color: '#fff',
      backgroundColor: color,
    }}>
      {label}
    </span>
  );
}

function TaskCard({ task, onStatusChange, onEdit, onDelete }) {
  const [loading, setLoading] = useState(false);

  const nextStatus = {
    pending: 'in_progress',
    in_progress: 'completed',
    completed: 'pending',
  }[task.status];

  async function handleStatusToggle() {
    setLoading(true);
    try {
      await apiFetch(`/tasks/${task.id}/status/`, {
        method: 'PATCH',
        body: JSON.stringify({ status: nextStatus }),
      });
      onStatusChange(task.id, nextStatus);
    } catch (e) {
      alert(e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{
      background: '#fff',
      borderRadius: 12,
      padding: '16px',
      marginBottom: 12,
      boxShadow: '0 1px 4px rgba(0,0,0,0.08)',
      borderLeft: `4px solid ${STATUS_COLORS[task.status]}`,
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 8 }}>
        <h3 style={{ margin: 0, fontSize: 15, fontWeight: 600, color: '#111', flex: 1 }}>
          {task.title}
        </h3>
        <div style={{ display: 'flex', gap: 6, flexShrink: 0 }}>
          <button
            onClick={() => onEdit(task)}
            style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: 16, padding: '4px 6px' }}
            aria-label="Edit"
          >✏️</button>
          <button
            onClick={() => onDelete(task.id)}
            style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: 16, padding: '4px 6px' }}
            aria-label="Delete"
          >🗑️</button>
        </div>
      </div>

      {task.description && (
        <p style={{ margin: '8px 0 0', fontSize: 13, color: '#555', lineHeight: 1.5 }}>
          {task.description}
        </p>
      )}

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginTop: 12, alignItems: 'center' }}>
        <Badge label={STATUS_LABELS[task.status]} color={STATUS_COLORS[task.status]} />
        <Badge label={PRIORITY_LABELS[task.priority]} color={PRIORITY_COLORS[task.priority]} />
        {task.is_overdue && <Badge label="Overdue" color="#dc2626" />}
        {task.due_date && (
          <span style={{ fontSize: 12, color: '#777' }}>📅 {task.due_date}</span>
        )}
      </div>

      <div style={{ marginTop: 12 }}>
        <button
          onClick={handleStatusToggle}
          disabled={loading}
          style={{
            padding: '8px 16px',
            borderRadius: 8,
            border: 'none',
            background: STATUS_COLORS[nextStatus],
            color: '#fff',
            fontWeight: 600,
            fontSize: 13,
            cursor: 'pointer',
            minWidth: 120,
          }}
        >
          {loading ? '...' : `Mark ${STATUS_LABELS[nextStatus]}`}
        </button>
      </div>
    </div>
  );
}

const EMPTY_FORM = { title: '', description: '', priority: 'medium', status: 'pending', due_date: '' };

function TaskForm({ initial, onSave, onClose }) {
  const [form, setForm] = useState(initial || EMPTY_FORM);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  async function handleSubmit(e) {
    e.preventDefault();
    if (!form.title.trim()) { setError('Title is required'); return; }
    setSaving(true);
    setError('');
    try {
      const payload = { ...form, due_date: form.due_date || null };
      if (initial?.id) {
        await apiFetch(`/tasks/${initial.id}/`, { method: 'PUT', body: JSON.stringify(payload) });
      } else {
        await apiFetch('/tasks/', { method: 'POST', body: JSON.stringify(payload) });
      }
      onSave();
    } catch (e) {
      setError(e.message);
    } finally {
      setSaving(false);
    }
  }

  const inputStyle = {
    width: '100%',
    padding: '10px 12px',
    borderRadius: 8,
    border: '1px solid #d1d5db',
    fontSize: 14,
    boxSizing: 'border-box',
    marginTop: 4,
  };

  return (
    <div style={{
      position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.4)',
      display: 'flex', alignItems: 'flex-end', justifyContent: 'center',
      zIndex: 1000, padding: 0,
    }}>
      <div style={{
        background: '#fff', borderRadius: '16px 16px 0 0',
        width: '100%', maxWidth: 480, padding: '24px 20px',
        maxHeight: '90vh', overflowY: 'auto',
      }}>
        <h2 style={{ margin: '0 0 20px', fontSize: 18 }}>
          {initial?.id ? 'Edit Task' : 'New Task'}
        </h2>
        {error && <p style={{ color: '#dc2626', fontSize: 13, marginBottom: 12 }}>{error}</p>}
        <form onSubmit={handleSubmit}>
          <label style={{ fontSize: 13, fontWeight: 600, color: '#374151' }}>
            Title *
            <input
              style={inputStyle}
              value={form.title}
              onChange={e => setForm(f => ({ ...f, title: e.target.value }))}
              placeholder="e.g. Water the maize field"
              required
            />
          </label>

          <label style={{ fontSize: 13, fontWeight: 600, color: '#374151', display: 'block', marginTop: 14 }}>
            Description
            <textarea
              style={{ ...inputStyle, minHeight: 80, resize: 'vertical' }}
              value={form.description}
              onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
              placeholder="Optional details..."
            />
          </label>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginTop: 14 }}>
            <label style={{ fontSize: 13, fontWeight: 600, color: '#374151' }}>
              Priority
              <select style={inputStyle} value={form.priority} onChange={e => setForm(f => ({ ...f, priority: e.target.value }))}>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </label>

            <label style={{ fontSize: 13, fontWeight: 600, color: '#374151' }}>
              Status
              <select style={inputStyle} value={form.status} onChange={e => setForm(f => ({ ...f, status: e.target.value }))}>
                <option value="pending">Pending</option>
                <option value="in_progress">In Progress</option>
                <option value="completed">Completed</option>
              </select>
            </label>
          </div>

          <label style={{ fontSize: 13, fontWeight: 600, color: '#374151', display: 'block', marginTop: 14 }}>
            Due Date
            <input
              type="date"
              style={inputStyle}
              value={form.due_date}
              onChange={e => setForm(f => ({ ...f, due_date: e.target.value }))}
            />
          </label>

          <div style={{ display: 'flex', gap: 10, marginTop: 20 }}>
            <button
              type="submit"
              disabled={saving}
              style={{
                flex: 1, padding: '12px', borderRadius: 8,
                border: 'none', background: '#16a34a', color: '#fff',
                fontWeight: 700, fontSize: 15, cursor: 'pointer',
              }}
            >
              {saving ? 'Saving...' : initial?.id ? 'Update' : 'Create'}
            </button>
            <button
              type="button"
              onClick={onClose}
              style={{
                flex: 1, padding: '12px', borderRadius: 8,
                border: '1px solid #d1d5db', background: '#fff',
                fontWeight: 600, fontSize: 15, cursor: 'pointer',
              }}
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default function Tasks() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editingTask, setEditingTask] = useState(null);

  const loadTasks = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const params = new URLSearchParams();
      if (statusFilter) params.set('status', statusFilter);
      if (priorityFilter) params.set('priority', priorityFilter);
      const query = params.toString() ? `?${params}` : '';
      const data = await apiFetch(`/tasks/${query}`);
      setTasks(Array.isArray(data) ? data : data.results ?? []);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [statusFilter, priorityFilter]);

  useEffect(() => { loadTasks(); }, [loadTasks]);

  function handleStatusChange(id, newStatus) {
    setTasks(prev => prev.map(t => t.id === id ? { ...t, status: newStatus } : t));
  }

  async function handleDelete(id) {
    if (!confirm('Delete this task?')) return;
    try {
      await apiFetch(`/tasks/${id}/`, { method: 'DELETE' });
      setTasks(prev => prev.filter(t => t.id !== id));
    } catch (e) {
      alert(e.message);
    }
  }

  const filterBtn = (active) => ({
    padding: '6px 14px',
    borderRadius: 20,
    border: '1px solid #d1d5db',
    background: active ? '#16a34a' : '#fff',
    color: active ? '#fff' : '#374151',
    fontWeight: 600,
    fontSize: 13,
    cursor: 'pointer',
  });

  return (
    <div style={{ maxWidth: 480, margin: '0 auto', padding: '16px 12px', fontFamily: 'system-ui, sans-serif' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <h1 style={{ margin: 0, fontSize: 22, fontWeight: 700, color: '#111' }}>Farm Tasks</h1>
        <button
          onClick={() => { setEditingTask(null); setShowForm(true); }}
          style={{
            padding: '10px 18px', borderRadius: 10,
            border: 'none', background: '#16a34a', color: '#fff',
            fontWeight: 700, fontSize: 14, cursor: 'pointer',
          }}
        >
          + New Task
        </button>
      </div>

      {/* Filters */}
      <div style={{ marginBottom: 16 }}>
        <p style={{ fontSize: 12, fontWeight: 600, color: '#6b7280', marginBottom: 6, textTransform: 'uppercase' }}>Status</p>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          {[['', 'All'], ['pending', 'Pending'], ['in_progress', 'In Progress'], ['completed', 'Completed']].map(([val, label]) => (
            <button key={val} onClick={() => setStatusFilter(val)} style={filterBtn(statusFilter === val)}>{label}</button>
          ))}
        </div>
        <p style={{ fontSize: 12, fontWeight: 600, color: '#6b7280', marginBottom: 6, marginTop: 10, textTransform: 'uppercase' }}>Priority</p>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          {[['', 'All'], ['high', 'High'], ['medium', 'Medium'], ['low', 'Low']].map(([val, label]) => (
            <button key={val} onClick={() => setPriorityFilter(val)} style={filterBtn(priorityFilter === val)}>{label}</button>
          ))}
        </div>
      </div>

      {/* Content */}
      {loading && <p style={{ textAlign: 'center', color: '#6b7280' }}>Loading tasks...</p>}
      {error && <p style={{ color: '#dc2626', textAlign: 'center' }}>{error}</p>}
      {!loading && !error && tasks.length === 0 && (
        <div style={{ textAlign: 'center', padding: '40px 0', color: '#9ca3af' }}>
          <p style={{ fontSize: 32 }}>🌱</p>
          <p>No tasks yet. Create one to get started.</p>
        </div>
      )}
      {tasks.map(task => (
        <TaskCard
          key={task.id}
          task={task}
          onStatusChange={handleStatusChange}
          onEdit={(t) => { setEditingTask(t); setShowForm(true); }}
          onDelete={handleDelete}
        />
      ))}

      {/* Form Modal */}
      {showForm && (
        <TaskForm
          initial={editingTask}
          onSave={() => { setShowForm(false); setEditingTask(null); loadTasks(); }}
          onClose={() => { setShowForm(false); setEditingTask(null); }}
        />
      )}
    </div>
  );
}
