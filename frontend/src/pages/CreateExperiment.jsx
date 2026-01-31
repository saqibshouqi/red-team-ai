/**
 * Create Experiment Page
 */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { experimentsAPI, agentsAPI } from '../api/client';
import { Loader } from 'lucide-react';

function CreateExperiment() {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [strategies, setStrategies] = useState([]);
    const [models, setModels] = useState({ providers: [] });

    const [formData, setFormData] = useState({
        experiment_name: '',
        description: '',
        target_role: {
            name: '',
            description: '',
            persona: '',
            constraints: '',
            knowledge_domain: ''
        },
        attack_strategies: ['role_drift'],
        target_llm_provider: 'groq',
        target_model: 'llama-3.3-70b-versatile',
        num_turns: 10,
        temperature: 0.7,
        max_tokens: 1024
    });

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            const [strategiesData, modelsData] = await Promise.all([
                agentsAPI.getStrategies(),
                agentsAPI.getModels()
            ]);
            setStrategies(strategiesData);
            setModels(modelsData);
        } catch (error) {
            console.error('Error loading data:', error);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);

        try {
            // Prepare config
            const config = {
                ...formData,
                target_role: {
                    ...formData.target_role,
                    constraints: formData.target_role.constraints
                        .split('\n')
                        .filter(c => c.trim())
                }
            };

            const result = await experimentsAPI.create(config, true);
            navigate(`/experiments/${result.experiment_id}`);
        } catch (error) {
            console.error('Error creating experiment:', error);
            alert('Failed to create experiment: ' + error.message);
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (e) => {
        const { name, value } = e.target;
        if (name.startsWith('target_role.')) {
            const field = name.split('.')[1];
            setFormData(prev => ({
                ...prev,
                target_role: { ...prev.target_role, [field]: value }
            }));
        } else {
            setFormData(prev => ({ ...prev, [name]: value }));
        }
    };

    const toggleStrategy = (strategyKey) => {
        setFormData(prev => ({
            ...prev,
            attack_strategies: prev.attack_strategies.includes(strategyKey)
                ? prev.attack_strategies.filter(s => s !== strategyKey)
                : [...prev.attack_strategies, strategyKey]
        }));
    };

    return (
        <div className="max-w-4xl mx-auto">
            <h1 className="text-3xl font-bold mb-6">Create New Experiment</h1>

            <form onSubmit={handleSubmit} className="space-y-6">
                {/* Basic Info */}
                <div className="bg-white p-6 rounded-lg shadow-sm border">
                    <h2 className="text-xl font-semibold mb-4">Experiment Information</h2>
                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium mb-1">Experiment Name</label>
                            <input
                                type="text"
                                name="experiment_name"
                                value={formData.experiment_name}
                                onChange={handleChange}
                                required
                                className="w-full px-3 py-2 border rounded-md"
                                placeholder="e.g., customer_support_stress_test"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-1">Description</label>
                            <textarea
                                name="description"
                                value={formData.description}
                                onChange={handleChange}
                                className="w-full px-3 py-2 border rounded-md"
                                rows="3"
                                placeholder="Optional description of the experiment"
                            />
                        </div>
                    </div>
                </div>

                {/* Target Role */}
                <div className="bg-white p-6 rounded-lg shadow-sm border">
                    <h2 className="text-xl font-semibold mb-4">Target Agent Role</h2>
                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium mb-1">Role Name</label>
                            <input
                                type="text"
                                name="target_role.name"
                                value={formData.target_role.name}
                                onChange={handleChange}
                                required
                                className="w-full px-3 py-2 border rounded-md"
                                placeholder="e.g., Customer Support Agent"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-1">Description</label>
                            <textarea
                                name="target_role.description"
                                value={formData.target_role.description}
                                onChange={handleChange}
                                required
                                className="w-full px-3 py-2 border rounded-md"
                                rows="3"
                                placeholder="Detailed role description"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-1">Persona</label>
                            <textarea
                                name="target_role.persona"
                                value={formData.target_role.persona}
                                onChange={handleChange}
                                required
                                className="w-full px-3 py-2 border rounded-md"
                                rows="2"
                                placeholder="Personality and communication style"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-1">
                                Constraints (one per line)
                            </label>
                            <textarea
                                name="target_role.constraints"
                                value={formData.target_role.constraints}
                                onChange={handleChange}
                                className="w-full px-3 py-2 border rounded-md"
                                rows="4"
                                placeholder="Never share customer personal information&#10;Always verify identity before account changes"
                            />
                        </div>
                    </div>
                </div>

                {/* Attack Strategies */}
                <div className="bg-white p-6 rounded-lg shadow-sm border">
                    <h2 className="text-xl font-semibold mb-4">Attack Strategies</h2>
                    <div className="grid md:grid-cols-2 gap-3">
                        {strategies.map(strategy => (
                            <label key={strategy.key} className="flex items-start space-x-2 cursor-pointer">
                                <input
                                    type="checkbox"
                                    checked={formData.attack_strategies.includes(strategy.key)}
                                    onChange={() => toggleStrategy(strategy.key)}
                                    className="mt-1"
                                />
                                <div>
                                    <div className="font-medium">{strategy.name}</div>
                                    <div className="text-sm text-gray-600">{strategy.description}</div>
                                </div>
                            </label>
                        ))}
                    </div>
                </div>

                {/* Configuration */}
                <div className="bg-white p-6 rounded-lg shadow-sm border">
                    <h2 className="text-xl font-semibold mb-4">Configuration</h2>
                    <div className="grid md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium mb-1">Number of Turns</label>
                            <input
                                type="number"
                                name="num_turns"
                                value={formData.num_turns}
                                onChange={handleChange}
                                min="1"
                                max="100"
                                className="w-full px-3 py-2 border rounded-md"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-1">Temperature</label>
                            <input
                                type="number"
                                name="temperature"
                                value={formData.temperature}
                                onChange={handleChange}
                                min="0"
                                max="2"
                                step="0.1"
                                className="w-full px-3 py-2 border rounded-md"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-1">LLM Provider</label>
                            <select
                                name="target_llm_provider"
                                value={formData.target_llm_provider}
                                onChange={handleChange}
                                className="w-full px-3 py-2 border rounded-md"
                            >
                                {models.providers.map(p => (
                                    <option key={p.name} value={p.name}>{p.display_name}</option>
                                ))}
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-1">Model</label>
                            <select
                                name="target_model"
                                value={formData.target_model}
                                onChange={handleChange}
                                className="w-full px-3 py-2 border rounded-md"
                            >
                                {models.providers
                                    .find(p => p.name === formData.target_llm_provider)
                                    ?.models.map(m => (
                                        <option key={m} value={m}>{m}</option>
                                    ))}
                            </select>
                        </div>
                    </div>
                </div>

                {/* Submit */}
                <div className="flex justify-end space-x-4">
                    <button
                        type="button"
                        onClick={() => navigate('/')}
                        className="px-6 py-2 border rounded-md text-gray-700 hover:bg-gray-50"
                    >
                        Cancel
                    </button>
                    <button
                        type="submit"
                        disabled={loading}
                        className="px-6 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50 flex items-center"
                    >
                        {loading && <Loader className="animate-spin mr-2 h-4 w-4" />}
                        Create & Run Experiment
                    </button>
                </div>
            </form>
        </div>
    );
}

export default CreateExperiment;