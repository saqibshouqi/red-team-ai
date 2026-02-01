import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Layout, Menu } from 'antd';
import { HomeOutlined, ExperimentOutlined, PlusOutlined, UnorderedListOutlined } from '@ant-design/icons';

import HomePage from './pages/HomePage';
import CreateExperiment from './pages/CreateExperiment';
import ExperimentsList from './pages/ExperimentsList';
import ExperimentDetails from './pages/ExperimentDetails';

const { Header, Content, Footer } = Layout;

function App() {
    const menuItems = [
        {
            key: 'home',
            icon: <HomeOutlined />,
            label: <Link to="/">Home</Link>
        },
        {
            key: 'create',
            icon: <PlusOutlined />,
            label: <Link to="/create">Create Experiment</Link>
        },
        {
            key: 'experiments',
            icon: <UnorderedListOutlined />,
            label: <Link to="/experiments">Experiments</Link>
        }
    ];

    return (
        <Router>
            <Layout style={{ minHeight: '100vh' }}>
                <Header style={{ display: 'flex', alignItems: 'center', background: '#dc2626' }}>
                    <div style={{ color: 'white', fontSize: '20px', fontWeight: 'bold', marginRight: '50px' }}>
                        🔴 Red Team AI
                    </div>
                    <Menu
                        theme="dark"
                        mode="horizontal"
                        items={menuItems}
                        style={{ flex: 1, minWidth: 0, background: '#dc2626' }}
                    />
                </Header>

                <Content style={{ padding: '24px 50px', background: '#f5f5f5' }}>
                    <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
                        <Routes>
                            <Route path="/" element={<HomePage />} />
                            <Route path="/create" element={<CreateExperiment />} />
                            <Route path="/experiments" element={<ExperimentsList />} />
                            <Route path="/experiments/:id" element={<ExperimentDetails />} />
                        </Routes>
                    </div>
                </Content>

                <Footer style={{ textAlign: 'center', background: '#f5f5f5' }}>
                    Red Team AI ©2024 | Production-grade RPLA Evaluation Platform
                </Footer>
            </Layout>
        </Router>
    );
}

export default App;