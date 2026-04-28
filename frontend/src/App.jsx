import React from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { Layout, Menu, Typography } from 'antd';
import { HomeOutlined, PlusOutlined, UnorderedListOutlined } from '@ant-design/icons';

import HomePage from './pages/HomePage';
import CreateExperiment from './pages/CreateExperiment';
import ExperimentsList from './pages/ExperimentsList';
import ExperimentDetails from './pages/ExperimentDetails';

const { Header, Content, Footer } = Layout;
const { Text } = Typography;

function AppContent() {
    const navigate = useNavigate();
    const location = useLocation();

    const menuItems = [
        {
            key: '/',
            icon: <HomeOutlined />,
            label: 'Home',
        },
        {
            key: '/create',
            icon: <PlusOutlined />,
            label: 'Create Experiment',
        },
        {
            key: '/experiments',
            icon: <UnorderedListOutlined />,
            label: 'Experiments',
        }
    ];

    const handleMenuClick = ({ key }) => {
        navigate(key);
    };

    return (
        <Layout style={{ minHeight: '100vh' }}>
            <Header style={{
                background: '#ff4d4f',
                padding: '0 50px'
            }}>
                <div style={{
                    maxWidth: '1400px',
                    margin: '0 auto',
                    display: 'flex',
                    alignItems: 'center'
                }}>
                    <Text
                        strong
                        style={{
                            color: 'white',
                            fontSize: '24px',
                            marginRight: '50px',
                            cursor: 'pointer'
                        }}
                        onClick={() => navigate('/')}
                    >
                        🔴 Red Team AI
                    </Text>
                    <Menu
                        theme="dark"
                        mode="horizontal"
                        selectedKeys={[location.pathname]}
                        items={menuItems}
                        onClick={handleMenuClick}
                        style={{
                            flex: 1,
                            minWidth: 0,
                            background: 'transparent',
                            borderBottom: 'none',
                            fontSize: '16px'
                        }}
                    />
                </div>
            </Header>

            <Content style={{
                padding: '24px 50px',
                background: '#f0f2f5',
                minHeight: 'calc(100vh - 64px - 70px)'
            }}>
                <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
                    <Routes>
                        <Route path="/" element={<HomePage />} />
                        <Route path="/create" element={<CreateExperiment />} />
                        <Route path="/experiments" element={<ExperimentsList />} />
                        <Route path="/experiments/:id" element={<ExperimentDetails />} />
                    </Routes>
                </div>
            </Content>

            <Footer style={{
                textAlign: 'center',
                background: '#f0f2f5',
                borderTop: '1px solid #d9d9d9'
            }}>
                <Text type="secondary">
                    Red Team AI ©2024 | Production-grade RPLA Evaluation Platform
                </Text>
            </Footer>
        </Layout>
    );
}

function App() {
    return (
        <Router>
            <AppContent />
        </Router>
    );
}

export default App;
