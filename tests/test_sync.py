import time
import logging
import copy
from . import run_server_in_context, get_free_port

logger = logging.getLogger(__name__)


def test_sync():
    port_1 = get_free_port()
    port_2 = get_free_port()
    server_url1 = 'http://localhost:%d' % port_1
    server_url2 = 'http://localhost:%d' % port_2
    server_urls = '%s,%s' % (server_url1, server_url2)

    json_data_1 = [{"id": "123456789", "update_token": "AA1234"}]
    json_data_2 = [{"id": "987654321", "update_token": "AA9876"}]
    # gack, for some reason we assertion failures hang the tests when done within the 'with'
    # so for now we just check all the assertions after the with
    with run_server_in_context(server_urls=server_urls, port=port_1) as server_1:
        with run_server_in_context(server_urls=server_urls, port=port_2) as server_2:
            logger.info('server1 is: %s' % server_1)
            logger.info('server2 is: %s' % server_2)
            resp_1_1 = server_1.sync()
            resp_1_1_data = resp_1_1.json()
            resp_2_1 = server_2.sync()
            resp_2_1_data = resp_2_1.json()
            server_1.send_status_json(contacts=json_data_1)
            server_2.send_status_json(contacts=json_data_2)
            time.sleep(4)
            resp_1_2 = server_1.sync()
            resp_1_2_data = resp_1_2.json()
            resp_2_2 = server_2.sync()
            resp_2_2_data = resp_2_2.json()
    assert resp_1_1.status_code == 200
    assert 'contact_ids' not in resp_1_1_data or len(resp_1_1_data.get('contact_ids')) == 0
    assert resp_2_1.status_code == 200
    assert 'contact_ids' not in resp_2_1_data or len(resp_2_1_data.get('contact_ids')) == 0

    # all_contacts = sort_list_of_dictionaries(json_data_1 + json_data_2)

    all_contacts1_2 = copy.deepcopy(json_data_1 + json_data_2)
    all_contacts1_2[1]['path'] = [server_url2]
    assert 'contact_ids' in resp_1_2_data and len(resp_1_2_data.get('contact_ids')) > 0
    assert 'contact_ids' in resp_2_2_data and len(resp_2_2_data.get('contact_ids')) > 0
    # This test wont work - it cant compare "path:[...]" BUT its not equal anyway
    assert [i["id"] for i in resp_1_2_data['contact_ids']] == ["123456789", "987654321"]
    assert resp_1_2_data['contact_ids'][1]['path'][0] == server_url2
    assert [i["id"] for i in resp_2_2_data['contact_ids']] == ["987654321", "123456789"]
    assert resp_2_2_data['contact_ids'][1]['path'][0] == server_url1
    return
