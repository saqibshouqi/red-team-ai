/**
 * Home Page Component
 */
import React from 'react';
import { Link } from 'react-router-dom';
import { Shield, Target, Crosshair, Scale, ArrowRight } from 'lucide-react';

function HomePage() {
    return (
        <div className="space-y-12">
            {/* Hero Section */}
            <div className="text-center space-y-4">
                <h1 className="text-4xl font-bold text-gray-900">
                    Red Team AI
                </h1>
                <p className="text-xl text-gray-600 max-w-2xl mx-auto">
                    Production-grade platform for evaluating Role-Playing Language Agents
                    using adversarial testing and automated scoring
                </p>
                <div className="flex justify-center space-x-4 pt-4">
                    <Link
                        to="/create"
                        className="bg-red-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-red-700 flex items-center"
                    >
                        Create Experiment
                        <ArrowRight className="ml-2 h-5 w-5" />
                    </Link>
                    <Link
                        to="/experiments"
                        className="bg-white text-gray-700 px-6 py-3 rounded-lg font-medium border border-gray-300 hover:bg-gray-50"
                    >
                        View Experiments
                    </Link>
                </div>
            </div>

            {/* Features */}
            <div className="grid md:grid-cols-3 gap-8">
                <div className="bg-white p-6 rounded-lg shadow-sm border">
                    <Target className="h-10 w-10 text-red-600 mb-4" />
                    <h3 className="text-lg font-semibold mb-2">Target Agent</h3>
                    <p className="text-gray-600">
                        Define role-playing agents with specific personas, constraints, and behavioral rules
                    </p>
                </div>

                <div className="bg-white p-6 rounded-lg shadow-sm border">
                    <Crosshair className="h-10 w-10 text-red-600 mb-4" />
                    <h3 className="text-lg font-semibold mb-2">Interrogator Agent</h3>
                    <p className="text-gray-600">
                        Adversarial testing using multiple attack strategies to probe agent boundaries
                    </p>
                </div>

                <div className="bg-white p-6 rounded-lg shadow-sm border">
                    <Scale className="h-10 w-10 text-red-600 mb-4" />
                    <h3 className="text-lg font-semibold mb-2">Judging Agent</h3>
                    <p className="text-gray-600">
                        Automated evaluation with multiple metrics: role fidelity, drift, ethics, consistency
                    </p>
                </div>
            </div>

            {/* Metrics Overview */}
            <div className="bg-white p-8 rounded-lg shadow-sm border">
                <h2 className="text-2xl font-bold mb-6">Evaluation Metrics</h2>
                <div className="grid md:grid-cols-2 gap-6">
                    <div>
                        <h4 className="font-semibold text-lg mb-2">Role Fidelity Score</h4>
                        <p className="text-gray-600">
                            Measures how well the agent maintained its assigned role throughout the conversation
                        </p>
                    </div>
                    <div>
                        <h4 className="font-semibold text-lg mb-2">Drift Index</h4>
                        <p className="text-gray-600">
                            Quantifies progressive deviation from the original role definition
                        </p>
                    </div>
                    <div>
                        <h4 className="font-semibold text-lg mb-2">Ethical Deviation</h4>
                        <p className="text-gray-600">
                            Detects violations of defined constraints and ethical boundaries
                        </p>
                    </div>
                    <div>
                        <h4 className="font-semibold text-lg mb-2">Consistency Score</h4>
                        <p className="text-gray-600">
                            Identifies contradictions and inconsistencies in agent responses
                        </p>
                    </div>
                </div>
            </div>

            {/* Quick Start */}
            <div className="bg-blue-50 border border-blue-200 p-6 rounded-lg">
                <h3 className="text-lg font-semibold mb-3 text-blue-900">Quick Start</h3>
                <ol className="list-decimal list-inside space-y-2 text-blue-900">
                    <li>Define your target agent's role and constraints</li>
                    <li>Select attack strategies for testing</li>
                    <li>Configure experiment parameters (turns, models, temperature)</li>
                    <li>Run the experiment and review results</li>
                    <li>Export data for further analysis</li>
                </ol>
            </div>
        </div>
    );
}

export default HomePage;