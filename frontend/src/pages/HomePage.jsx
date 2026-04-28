/**
 * Home Page Component
 */
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Typography, Card, Button, Row, Col, Space, Alert } from 'antd';
import { UserOutlined, ThunderboltOutlined, CheckCircleOutlined, ArrowRightOutlined } from '@ant-design/icons';

const { Title, Paragraph } = Typography;

function HomePage() {
    const navigate = useNavigate();

    return (
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
            {/* Hero Section */}
            <div style={{ textAlign: 'center', padding: '40px 0' }}>
                <Title level={1}>Red Team AI</Title>
                <Paragraph style={{ fontSize: '18px', maxWidth: '800px', margin: '0 auto 32px' }}>
                    Production-grade platform for evaluating Role-Playing Language Agents
                    using adversarial testing and automated scoring
                </Paragraph>
                <Space size="middle">
                    <Button
                        type="primary"
                        danger
                        size="large"
                        icon={<ArrowRightOutlined />}
                        onClick={() => navigate('/create')}
                    >
                        Create Experiment
                    </Button>
                    <Button
                        size="large"
                        onClick={() => navigate('/experiments')}
                    >
                        View Experiments
                    </Button>
                </Space>
            </div>

            {/* Features */}
            <Row gutter={[24, 24]}>
                <Col xs={24} sm={24} md={8}>
                    <Card>
                        <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                            <UserOutlined style={{ fontSize: '40px', color: '#ff4d4f' }} />
                            <Title level={4} style={{ margin: 0 }}>Target Agent</Title>
                            <Paragraph type="secondary">
                                Define role-playing agents with specific personas, constraints, and behavioral rules
                            </Paragraph>
                        </Space>
                    </Card>
                </Col>
                <Col xs={24} sm={24} md={8}>
                    <Card>
                        <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                            <ThunderboltOutlined style={{ fontSize: '40px', color: '#ff4d4f' }} />
                            <Title level={4} style={{ margin: 0 }}>Interrogator Agent</Title>
                            <Paragraph type="secondary">
                                Adversarial testing using multiple attack strategies to probe agent boundaries
                            </Paragraph>
                        </Space>
                    </Card>
                </Col>
                <Col xs={24} sm={24} md={8}>
                    <Card>
                        <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                            <CheckCircleOutlined style={{ fontSize: '40px', color: '#ff4d4f' }} />
                            <Title level={4} style={{ margin: 0 }}>Judging Agent</Title>
                            <Paragraph type="secondary">
                                Automated evaluation with multiple metrics: role fidelity, drift, ethics, consistency
                            </Paragraph>
                        </Space>
                    </Card>
                </Col>
            </Row>

            {/* Metrics Overview */}
            <Card title={<Title level={2} style={{ margin: 0 }}>Evaluation Metrics</Title>}>
                <Row gutter={[24, 24]}>
                    <Col xs={24} sm={24} md={12}>
                        <Space direction="vertical" size="small">
                            <Title level={4} style={{ margin: 0 }}>Role Fidelity Score</Title>
                            <Paragraph type="secondary">
                                Measures how well the agent maintained its assigned role throughout the conversation
                            </Paragraph>
                        </Space>
                    </Col>
                    <Col xs={24} sm={24} md={12}>
                        <Space direction="vertical" size="small">
                            <Title level={4} style={{ margin: 0 }}>Drift Index</Title>
                            <Paragraph type="secondary">
                                Quantifies progressive deviation from the original role definition
                            </Paragraph>
                        </Space>
                    </Col>
                    <Col xs={24} sm={24} md={12}>
                        <Space direction="vertical" size="small">
                            <Title level={4} style={{ margin: 0 }}>Ethical Deviation</Title>
                            <Paragraph type="secondary">
                                Detects violations of defined constraints and ethical boundaries
                            </Paragraph>
                        </Space>
                    </Col>
                    <Col xs={24} sm={24} md={12}>
                        <Space direction="vertical" size="small">
                            <Title level={4} style={{ margin: 0 }}>Consistency Score</Title>
                            <Paragraph type="secondary">
                                Identifies contradictions and inconsistencies in agent responses
                            </Paragraph>
                        </Space>
                    </Col>
                </Row>
            </Card>

            {/* Quick Start */}
            <Alert
                message={<Title level={4} style={{ margin: 0 }}>Quick Start</Title>}
                description={
                    <ol style={{ margin: '16px 0 0 0', paddingLeft: '20px' }}>
                        <li>Define your target agent's role and constraints</li>
                        <li>Select attack strategies for testing</li>
                        <li>Configure experiment parameters (turns, models, temperature)</li>
                        <li>Run the experiment and review results</li>
                        <li>Export data for further analysis</li>
                    </ol>
                }
                type="info"
                showIcon
            />
        </Space>
    );
}

export default HomePage;
