import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Table, Card, Tag, Button, Space, message, Spin } from 'antd';
import { EyeOutlined, DeleteOutlined, ReloadOutlined } from '@ant-design/icons';
import { experimentsAPI } from '../api/client';

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
            message.success('Experiment deleted');
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
            render: (text, record) => (
                <Button type="link" onClick={() => navigate(`/experiments/${record.id}`)}>
                    {text}
                </Button>
            )
        },
        {
            title: 'Status',
            dataIndex: 'status',
            key: 'status',
            render: (status) => (
                <Tag color={getStatusColor(status)}>{status.toUpperCase()}</Tag>
            )
        },
        {
            title: 'Overall Score',
            dataIndex: 'overall_score',
            key: 'overall_score',
            render: (score) => score !== null ? score.toFixed(3) : '-'
        },
        {
            title: 'Duration',
            dataIndex: 'duration_seconds',
            key: 'duration_seconds',
            render: (duration) => duration ? `${duration.toFixed(1)}s` : '-'
        },
        {
            title: 'Created',
            dataIndex: 'created_at',
            key: 'created_at',
            render: (date) => new Date(date).toLocaleString()
        },
        {
            title: 'Actions',
            key: 'actions',
            render: (_, record) => (
                <Space>
                    <Button
                        type="primary"
                        icon={<EyeOutlined />}
                        onClick={() => navigate(`/experiments/${record.id}`)}
                    >
                        View
                    </Button>
                    <Button
                        danger
                        icon={<DeleteOutlined />}
                        onClick={() => handleDelete(record.id)}
                    >
                        Delete
                    </Button>
                </Space>
            )
        }
    ];

    return (
        <div>
            <Card
                title={
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span>Experiments ({total})</span>
                        <Button
                            type="primary"
                            icon={<ReloadOutlined />}
                            onClick={loadExperiments}
                        >
                            Refresh
                        </Button>
                    </div>
                }
            >
                {loading ? (
                    <div style={{ textAlign: 'center', padding: '50px' }}>
                        <Spin size="large" />
                    </div>
                ) : (
                    <Table
                        columns={columns}
                        dataSource={experiments}
                        rowKey="id"
                        pagination={{ pageSize: 10 }}
                    />
                )}
            </Card>
        </div>
    );
}

export default ExperimentsList;