class Test_init_duf:

    def test_get_init_duf_sh(self, client):
        res = client.get('/init-duf.sh')
        assert res.status_code == 200
        assert res.text


class Test_host:

    def test_add_and_ls(self, client):
        res = client.post('/api/host/add', json={
            'name': 'foo',
            'ip': '1.2.3.4',
        })
        assert res.status_code == 200

        res = client.post('/api/host/ls')
        assert res.status_code == 200
        hosts = res.json()['hosts']
        assert len(hosts) == 1
        host = hosts[0]
        assert host['name'] == 'foo'
        assert host['ip'] == '1.2.3.4'

    def test_edit_and_info_and(self, client):
        res = client.post('/api/host/add', json={
            'name': 'foo',
            'ip': '1.2.3.4',
        })
        host_id = res.json()['id']

        res = client.post('/api/host/edit', json={
            'id': host_id,
            'name': 'bar',
        })
        assert res.json() == {'id': host_id, 'name': 'bar', 'ip': '1.2.3.4'}

        res = client.post('/api/host/info', json={'target': 'bar'})
        assert res.json() == {'id': host_id, 'name': 'bar', 'ip': '1.2.3.4'}

    def test_edit_not_found(self, client):
        res = client.post('/api/host/edit', json={
            'id': 'foo',
        })
        assert res.status_code == 404

    def test_remove(self, client):
        res = client.post('/api/host/add', json={'name': 'foo'})
        host_id = res.json()['id']

        client.post('/api/host/add', json={'name': 'bar'})

        client.post('/api/host/remove', json={'target': host_id})
        client.post('/api/host/remove', json={'target': 'bar'})

        res = client.post('/api/host/ls')
        assert not res.json()['hosts']
