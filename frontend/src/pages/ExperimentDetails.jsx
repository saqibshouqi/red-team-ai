import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Descriptions, Tag, Timeline, Statistic, Row, Col, Button, Spin, message, Tabs } from 'antd';
import { ArrowLeftOutlined, DownloadOutlined, ReloadOutlined } from '@ant-design/icons';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { experimentsAPI } from '../api/client';

function ExperimentDetails() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [experiment, setExperiment] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadExperiment();
    }, [id]);

    const loadExperiment = async () => {
        setLoading(true);
        try {
            const data = await experimentsAPI.get(id);
            setExperiment(data);
        } catch (error) {
            message.error('Failed to load experiment');
            console.error('Error loading experiment:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleExport = async () => {
        try {
            const data = await experimentsAPI.export(id, 'json');
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `experiment_${id}.json`;
            a.click();
            message.success('Exported successfully');
        } catch (error) {
            message.error('Failed to export');
        }
    };

    const handleRerun = async () => {
        try {
            message.loading({ content: 'Rerunning experiment...', key: 'rerun' });
            await experimentsAPI.run(id);
            message.success({ content: 'Experiment rerun started. Results will be updated when complete.', key: 'rerun' });
            // Reload experiment data after a short delay
            setTimeout(() => {
                loadExperiment();
            }, 2000);
        } catch (error) {
            message.error({ content: error.response?.data?.detail || 'Failed to rerun experiment', key: 'rerun' });
        }
    };

    if (loading) {
        return (
            <div style={{ textAlign: 'center', padding: '100px' }}>
                <Spin size="large" />
            </div>
        );
    }

    if (!experiment) {
        return <div>Experiment not found</div>;
    }

    const getStatusColor = (status) => {
        const colors = {
            pending: 'default',
            running: 'processing',
            completed: 'success',
            failed: 'error'
        };
        return colors[status] || 'default';
    };

    // Prepare chart data
    const chartData = experiment.scores?.turn_by_turn_scores || [];

    const tabItems = [
        {
            key: 'overview',
            label: 'Overview',
            children: (
                <>
                    <Descriptions bordered column={2}>
                        <Descriptions.Item label="Name">{experiment.name}</Descriptions.Item>
                        <Descriptions.Item label="Status">
                            <Tag color={getStatusColor(experiment.status)}>
                                {experiment.status.toUpperCase()}
                            </Tag>
                        </Descriptions.Item>
                        <Descriptions.Item label="Description" span={2}>
                            {experiment.description || 'No description'}
                        </Descriptions.Item>
                        <Descriptions.Item label="Target Role">
                            {experiment.config?.target_role?.name}
                        </Descriptions.Item>
                        <Descriptions.Item label="LLM Provider">
                            {experiment.config?.target_llm_provider} - {experiment.config?.target_model}
                        </Descriptions.Item>
                        <Descriptions.Item label="Number of Turns">
                            {experiment.config?.num_turns}
                        </Descriptions.Item>
                        <Descriptions.Item label="Temperature">
                            {experiment.config?.temperature}
                        </Descriptions.Item>
                        <Descriptions.Item label="Attack Strategies" span={2}>
                            {experiment.config?.attack_strategies?.map(s => (
                                <Tag key={s} color="red">{s}</Tag>
                            ))}
                        </Descriptions.Item>
                        <Descriptions.Item label="Start Time">
                            {experiment.start_time ? new Date(experiment.start_time).toLocaleString() : '-'}
                        </Descriptions.Item>
                        <Descriptions.Item label="End Time">
                            {experiment.end_time ? new Date(experiment.end_time).toLocaleString() : '-'}
                        </Descriptions.Item>
                        <Descriptions.Item label="Duration">
                            {experiment.duration_seconds ? `${experiment.duration_seconds.toFixed(2)}s` : '-'}
                        </Descriptions.Item>
                        <Descriptions.Item label="Created">
                            {new Date(experiment.created_at).toLocaleString()}
                        </Descriptions.Item>
                        {experiment.error_message && (
                            <Descriptions.Item label="Error" span={2}>
                                <div style={{ color: '#cf1322', whiteSpace: 'pre-wrap' }}>
                                    {experiment.error_message}
                                </div>
                            </Descriptions.Item>
                        )}
                    </Descriptions>

                    {experiment.scores && (
                        <Card style={{ marginTop: 24 }} title="Evaluation Scores">
                            <Row gutter={16}>
                                <Col span={8}>
                                    <Statistic
                                        title="Overall Score"
                                        value={experiment.scores.overall_score}
                                        precision={3}
                                        valueStyle={{ color: experiment.scores.overall_score > 0.7 ? '#3f8600' : '#cf1322' }}
                                    />
                                </Col>
                                <Col span={8}>
                                    <Statistic
                                        title="Role Fidelity"
                                        value={experiment.scores.role_fidelity_score}
                                        precision={3}
                                    />
                                </Col>
                                <Col span={8}>
                                    <Statistic
                                        title="Consistency"
                                        value={experiment.scores.consistency_score}
                                        precision={3}
                                    />
                                </Col>
                            </Row>
                            <Row gutter={16} style={{ marginTop: 16 }}>
                                <Col span={8}>
                                    <Statistic
                                        title="Drift Index"
                                        value={experiment.scores.drift_index}
                                        precision={3}
                                        valueStyle={{ color: experiment.scores.drift_index < 0.3 ? '#3f8600' : '#cf1322' }}
                                        suffix="(lower is better)"
                                    />
                                </Col>
                                <Col span={8}>
                                    <Statistic
                                        title="Ethical Deviation"
                                        value={experiment.scores.ethical_deviation_score}
                                        precision={3}
                                        valueStyle={{ color: experiment.scores.ethical_deviation_score < 0.3 ? '#3f8600' : '#cf1322' }}
                                        suffix="(lower is better)"
                                    />
                                </Col>
                            </Row>
                        </Card>
                    )}

                    {chartData.length > 0 && (
                        <Card style={{ marginTop: 24 }} title="Turn-by-Turn Performance">
                            <ResponsiveContainer width="100%" height={300}>
                                <LineChart data={chartData}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="turn" label={{ value: 'Turn', position: 'insideBottom', offset: -5 }} />
                                    <YAxis label={{ value: 'Score', angle: -90, position: 'insideLeft' }} />
                                    <Tooltip />
                                    <Legend />
                                    <Line type="monotone" dataKey="role_fidelity" stroke="#8884d8" name="Role Fidelity" />
                                    <Line type="monotone" dataKey="ethical_deviation" stroke="#ff7300" name="Ethical Deviation" />
                                    <Line type="monotone" dataKey="overall" stroke="#82ca9d" name="Overall" />
                                </LineChart>
                            </ResponsiveContainer>
                        </Card>
                    )}
                </>
            )
        },
        {
            key: 'conversation',
            label: 'Conversation',
            children: (
                <Card>
                    {experiment.conversation && experiment.conversation.length > 0 ? (
                        <Timeline
                            items={experiment.conversation.map((turn, index) => ({
                                key: index,
                                color: index % 2 === 0 ? 'blue' : 'green',
                                children: (
                                    <div>
                                        <div style={{ marginBottom: 8 }}>
                                            <Tag color="red">Turn {turn.turn_number}</Tag>
                                            <Tag color="orange">{turn.interrogator_strategy}</Tag>
                                            {turn.response_time_ms && (
                                                <Tag>{turn.response_time_ms.toFixed(0)}ms</Tag>
                                            )}
                                        </div>
                                        <Card size="small" style={{ marginBottom: 8, background: '#f0f2f5' }}>
                                            <strong>🔴 Interrogator:</strong>
                                            <div style={{ marginTop: 8 }}>{turn.interrogator_message}</div>
                                        </Card>
                                        <Card size="small" style={{ background: '#e6f7ff' }}>
                                            <strong>🎯 Target:</strong>
                                            <div style={{ marginTop: 8 }}>{turn.target_response}</div>
                                        </Card>
                                    </div>
                                )
                            }))}
                        />
                    ) : (
                        <div style={{ textAlign: 'center', padding: '50px', color: '#999' }}>
                            No conversation data available
                        </div>
                    )}
                </Card>
            )
        },
        {
            key: 'analysis',
            label: 'Detailed Analysis',
            children: (
                <Card>
                    {experiment.scores?.detailed_analysis ? (
                        <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit' }}>
                            {experiment.scores.detailed_analysis}
                        </pre>
                    ) : (
                        <div style={{ textAlign: 'center', padding: '50px', color: '#999' }}>
                            No analysis available
                        </div>
                    )}
                </Card>
            )
        }
    ];

    const canRerun = experiment.status === 'completed' || experiment.status === 'failed';

    return (
        <div>
            <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
                <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/experiments')}>
                    Back to Experiments
                </Button>
                <div style={{ display: 'flex', gap: 8 }}>
                    {canRerun && (
                        <Button
                            icon={<ReloadOutlined />}
                            onClick={handleRerun}
                            disabled={experiment.status === 'running'}
                        >
                            Rerun Experiment
                        </Button>
                    )}
                    <Button
                        type="primary"
                        icon={<DownloadOutlined />}
                        onClick={handleExport}
                    >
                        Export JSON
                    </Button>
                </div>
            </div>

            <Tabs items={tabItems} defaultActiveKey="overview" />
        </div>
    );
}

export default ExperimentDetails;
