import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, Form, Input, InputNumber, Select, Checkbox, Button, Row, Col, message, Spin } from 'antd';
import { experimentsAPI, agentsAPI } from '../api/client';

const { TextArea } = Input;

function CreateExperiment() {
    const navigate = useNavigate();
    const [form] = Form.useForm();
    const [loading, setLoading] = useState(false);
    const [dataLoading, setDataLoading] = useState(true);
    const [strategies, setStrategies] = useState([]);
    const [models, setModels] = useState({ providers: [] });
    const [selectedProvider, setSelectedProvider] = useState('groq');

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
            setDataLoading(false);
        } catch (error) {
            message.error('Failed to load data');
            console.error('Error loading data:', error);
            setDataLoading(false);
        }
    };

    const handleSubmit = async (values) => {
        setLoading(true);

        try {
            const config = {
                experiment_name: values.experiment_name,
                description: values.description,
                target_role: {
                    name: values.role_name,
                    description: values.role_description,
                    persona: values.persona,
                    constraints: values.constraints.split('\n').filter(c => c.trim()),
                    knowledge_domain: values.knowledge_domain
                },
                attack_strategies: values.attack_strategies || ['role_drift'],
                target_llm_provider: values.target_llm_provider,
                target_model: values.target_model,
                num_turns: values.num_turns,
                temperature: values.temperature,
                max_tokens: 1024
            };

            const result = await experimentsAPI.create(config, true);
            message.success('Experiment created and started!');
            navigate(`/experiments/${result.experiment_id}`);
        } catch (error) {
            console.error('Error creating experiment:', error);
            message.error('Failed to create experiment: ' + error.message);
        } finally {
            setLoading(false);
        }
    };

    if (dataLoading) {
        return (
            <div style={{ textAlign: 'center', padding: '100px' }}>
                <Spin size="large" />
            </div>
        );
    }

    const providerModels = models.providers.find(p => p.name === selectedProvider)?.models || [];

    return (
        <div>
            <h1 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '24px' }}>
                Create New Experiment
            </h1>

            <Form
                form={form}
                layout="vertical"
                onFinish={handleSubmit}
                initialValues={{
                    num_turns: 10,
                    temperature: 0.7,
                    target_llm_provider: 'groq',
                    target_model: 'llama-3.3-70b-versatile',
                    attack_strategies: ['role_drift']
                }}
            >
                {/* Basic Info */}
                <Card title="Experiment Information" style={{ marginBottom: 24 }}>
                    <Row gutter={16}>
                        <Col span={24}>
                            <Form.Item
                                label="Experiment Name"
                                name="experiment_name"
                                rules={[{ required: true, message: 'Please enter experiment name' }]}
                            >
                                <Input placeholder="e.g., customer_support_stress_test" />
                            </Form.Item>
                        </Col>
                        <Col span={24}>
                            <Form.Item label="Description" name="description">
                                <TextArea rows={3} placeholder="Optional description of the experiment" />
                            </Form.Item>
                        </Col>
                    </Row>
                </Card>

                {/* Target Role */}
                <Card title="Target Agent Role" style={{ marginBottom: 24 }}>
                    <Row gutter={16}>
                        <Col span={24}>
                            <Form.Item
                                label="Role Name"
                                name="role_name"
                                rules={[{ required: true, message: 'Please enter role name' }]}
                            >
                                <Input placeholder="e.g., Customer Support Agent" />
                            </Form.Item>
                        </Col>
                        <Col span={24}>
                            <Form.Item
                                label="Description"
                                name="role_description"
                                rules={[{ required: true, message: 'Please enter role description' }]}
                            >
                                <TextArea rows={3} placeholder="Detailed role description" />
                            </Form.Item>
                        </Col>
                        <Col span={24}>
                            <Form.Item
                                label="Persona"
                                name="persona"
                                rules={[{ required: true, message: 'Please enter persona' }]}
                            >
                                <TextArea rows={2} placeholder="Personality and communication style" />
                            </Form.Item>
                        </Col>
                        <Col span={24}>
                            <Form.Item label="Knowledge Domain" name="knowledge_domain">
                                <Input placeholder="e.g., Customer Service, E-commerce" />
                            </Form.Item>
                        </Col>
                        <Col span={24}>
                            <Form.Item
                                label="Constraints (one per line)"
                                name="constraints"
                                rules={[{ required: true, message: 'Please enter at least one constraint' }]}
                            >
                                <TextArea
                                    rows={4}
                                    placeholder="Never share customer personal information&#10;Always verify identity before account changes"
                                />
                            </Form.Item>
                        </Col>
                    </Row>
                </Card>

                {/* Attack Strategies */}
                <Card title="Attack Strategies" style={{ marginBottom: 24 }}>
                    <Form.Item name="attack_strategies">
                        <Checkbox.Group style={{ width: '100%' }}>
                            <Row gutter={[16, 16]}>
                                {strategies.map(strategy => (
                                    <Col span={12} key={strategy.key}>
                                        <Checkbox value={strategy.key}>
                                            <div>
                                                <div style={{ fontWeight: 500 }}>{strategy.name}</div>
                                                <div style={{ fontSize: '12px', color: '#666' }}>
                                                    {strategy.description}
                                                </div>
                                            </div>
                                        </Checkbox>
                                    </Col>
                                ))}
                            </Row>
                        </Checkbox.Group>
                    </Form.Item>
                </Card>

                {/* Configuration */}
                <Card title="Configuration" style={{ marginBottom: 24 }}>
                    <Row gutter={16}>
                        <Col span={12}>
                            <Form.Item label="Number of Turns" name="num_turns">
                                <InputNumber min={1} max={100} style={{ width: '100%' }} />
                            </Form.Item>
                        </Col>
                        <Col span={12}>
                            <Form.Item label="Temperature" name="temperature">
                                <InputNumber min={0} max={2} step={0.1} style={{ width: '100%' }} />
                            </Form.Item>
                        </Col>
                        <Col span={12}>
                            <Form.Item label="LLM Provider" name="target_llm_provider">
                                <Select onChange={setSelectedProvider}>
                                    {models.providers.map(p => (
                                        <Select.Option key={p.name} value={p.name}>
                                            {p.display_name}
                                        </Select.Option>
                                    ))}
                                </Select>
                            </Form.Item>
                        </Col>
                        <Col span={12}>
                            <Form.Item label="Model" name="target_model">
                                <Select>
                                    {providerModels.map(m => (
                                        <Select.Option key={m} value={m}>
                                            {m}
                                        </Select.Option>
                                    ))}
                                </Select>
                            </Form.Item>
                        </Col>
                    </Row>
                </Card>

                {/* Submit */}
                <Form.Item>
                    <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
                        <Button onClick={() => navigate('/')}>
                            Cancel
                        </Button>
                        <Button type="primary" htmlType="submit" loading={loading} danger>
                            Create & Run Experiment
                        </Button>
                    </div>
                </Form.Item>
            </Form>
        </div>
    );
}

export default CreateExperiment;