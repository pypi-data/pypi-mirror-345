import ethernetip

def test_ports():
    assert ethernetip.ENIP_TCP_PORT == 44818, "Someone stole the specified port"

def test_eip():
    from unittest import mock

    with mock.patch('socket.socket') as mock_socket:
        mock_socket.return_value.recv.return_value = bytes(23)
        eip = ethernetip.EtherNetIP()
        assert eip.explicit == []
        c1 = eip.explicit_conn()
        c1.sock.connect.assert_called_with(('127.0.0.1', 44818))

