import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Table, Card, Tag, Button, Space, message, Spin, Typography, Empty, Popconfirm } from 'antd';
import { EyeOutlined, DeleteOutlined, ReloadOutlined, PlusOutlined } from '@ant-design/icons';
import { experimentsAPI } from '../api/client';

const { Title, Text } = Typography;

function ExperimentsList() {
    const navigate = useNavigate();
    const [experiments, setExperiments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [total, setTotal] = useState(0);

    useEffect(() => {
        loadExperiments();
    }, []);

    const loadExperiments = async () => {
        setLoading(true);
        try {
            const data = await experimentsAPI.list();
            setExperiments(data.experiments);
            setTotal(data.total);
        } catch (error) {
            message.error('Failed to load experiments');
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (id) => {
        try {
            await experimentsAPI.delete(id);
            message.success('Experiment deleted successfully');
            loadExperiments();
        } catch (error) {
            message.error('Failed to delete experiment');
        }
    };

    const getStatusColor = (status) => {
        const colors = {
            pending: 'default',
            running: 'processing',
            completed: 'success',
            failed: 'error'
        };
        return colors[status] || 'default';
    };

    const columns = [
        {
            title: 'Name',
            dataIndex: 'name',
            key: 'name',
            ellipsis: true,
            render: (text, record) => (
                <Button
                    type="link"
                    onClick={() => navigate(`/experiments/${record.id}`)}
                    style={{ padding: 0 }}
                >
                    {text}
                </Button>
            )
        },
        {
            title: 'Status',
            dataIndex: 'status',
            key: 'status',
            width: 120,
            render: (status) => (
                <Tag color={getStatusColor(status)}>{status.toUpperCase()}</Tag>
            )
        },
        {
            title: 'Overall Score',
            dataIndex: 'overall_score',
            key: 'overall_score',
            width: 130,
            render: (score) => {
                if (score === null) return <Text type="secondary">-</Text>;
                const color = score >= 0.7 ? '#52c41a' : score >= 0.5 ? '#faad14' : '#ff4d4f';
                return <Text strong style={{ color }}>{score.toFixed(3)}</Text>;
            }
        },
        {
            title: 'Duration',
            dataIndex: 'duration_seconds',
            key: 'duration_seconds',
            width: 120,
            render: (duration) => duration ? (
                <Text>{duration.toFixed(1)}s</Text>
            ) : (
                <Text type="secondary">-</Text>
            )
        },
        {
            title: 'Created',
            dataIndex: 'created_at',
            key: 'created_at',
            width: 180,
            render: (date) => (
                <Text type="secondary">{new Date(date).toLocaleString()}</Text>
            )
        },
        {
            title: 'Actions',
            key: 'actions',
            width: 180,
            fixed: 'right',
            render: (_, record) => (
                <Space>
                    <Button
                        type="primary"
                        icon={<EyeOutlined />}
                        onClick={() => navigate(`/experiments/${record.id}`)}
                        size="small"
                    >
                        View
                    </Button>
                    <Popconfirm
                        title="Delete experiment"
                        description="Are you sure you want to delete this experiment?"
                        onConfirm={() => handleDelete(record.id)}
                        okText="Yes"
                        cancelText="No"
                        okButtonProps={{ danger: true }}
                    >
                        <Button
                            danger
                            icon={<DeleteOutlined />}
                            size="small"
                        >
                            Delete
                        </Button>
                    </Popconfirm>
                </Space>
            )
        }
    ];

    return (
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
            <Card>
                <Space style={{ width: '100%', justifyContent: 'space-between' }}>
                    <Title level={2} style={{ margin: 0 }}>
                        Experiments
                        {total > 0 && (
                            <Text type="secondary" style={{ fontSize: '18px', fontWeight: 'normal', marginLeft: 8 }}>
                                ({total})
                            </Text>
                        )}
                    </Title>
                    <Space>
                        <Button
                            icon={<ReloadOutlined />}
                            onClick={loadExperiments}
                            loading={loading}
                        >
                            Refresh
                        </Button>
                        <Button
                            type="primary"
                            icon={<PlusOutlined />}
                            onClick={() => navigate('/create')}
                        >
                            Create Experiment
                        </Button>
                    </Space>
                </Space>
            </Card>

            <Card>
                {loading ? (
                    <div style={{ textAlign: 'center', padding: '50px' }}>
                        <Spin size="large" />
                        <div style={{ marginTop: 16 }}>
                            <Text type="secondary">Loading experiments...</Text>
                        </div>
                    </div>
                ) : experiments.length === 0 ? (
                    <Empty
                        description={
                            <Space direction="vertical" size="small">
                                <Text type="secondary">No experiments found</Text>
                                <Button
                                    type="primary"
                                    icon={<PlusOutlined />}
                                    onClick={() => navigate('/create')}
                                >
                                    Create Your First Experiment
                                </Button>
                            </Space>
                        }
                    />
                ) : (
                    <Table
                        columns={columns}
                        dataSource={experiments}
                        rowKey="id"
                        pagination={{
                            pageSize: 10,
                            showSizeChanger: true,
                            showTotal: (total) => `Total ${total} experiments`,
                            pageSizeOptions: ['10', '20', '50', '100']
                        }}
                        scroll={{ x: 1000 }}
                    />
                )}
            </Card>
        </Space>
    );
}

export default ExperimentsList;
