import os
import uuid
import json
import hmac
import hashlib
import threading
from base64 import b64encode, b64decode

import websocket
import arrow

from .constants import HEADERS
from .aes import AES


class DeviceLogin(object):
    def __init__(self, url, ws_data, session_id):
        self._url = url
        self._ws_data = ws_data
        self._session_id = session_id
        self._token_data = None
        self._stop = False
        self._ws = None
        self._sequence_number = 0

    def connect(self):
        headers = {
            'Sec-WebSocket-Key': b64encode(os.urandom(16)).decode('utf-8'),
            'Sec-WebSocket-Protocol': 'vnd.dss.edge.paired.enc+json+binary',
        }
        headers.update(HEADERS)

        self._ws = websocket.create_connection(self._url + '?id='+self._ws_data['pairing']['id'], suppress_origin=True, header=headers)
        rcv_data = self._decrypt_websocket_frame(self._ws.recv())
        assert rcv_data['data']['verification'] == self._ws_data['pairing']['verification']

        snd_data = {
            'data': {'challengeCode': rcv_data['data']['challengeCode']},
            'id': str(uuid.uuid4()),
            'type': 'urn:dss:event:edge:sdk:pairingClientChallenge', 
            'schemaurl': 'https://github.bamtech.co/schema-registry/schema-registry/blob/master/dss/event/edge/1.0.0/sdk/pairing-client-challenge.oas2.yaml', 
            'source': 'urn:dss:source:sdk:android:google:tv', 
            'time': arrow.utcnow().format('YYYY-MM-DDTHH:mm:ss.SSSZZ'),
            'datacontenttype': 'application/json; charset=utf-8', 
            'subject': 'sessionId={}'.format(self._session_id),
        }
        snd_raw = self._encrypt_websocket_frame(snd_data)
        self._ws.send(snd_raw, opcode=0x2)

        rcv_data = self._decrypt_websocket_frame(self._ws.recv())
        assert rcv_data['type'] == 'urn:dss:transport:edge:event:authenticated'

        self._thread = threading.Thread(target=self._worker)
        self._thread.daemon = True
        self._thread.start()

    def _decrypt_websocket_frame(self, frame):
        assert frame, "No data returned"

        algo_param = b64decode(self._ws_data['algorithmParameter'])
        aes_key = bytes(algo_param[:16])
        hmac_key = bytes(algo_param[16:48])
        
        hmac_received = frame[:32]
        ciphertext = frame[32:]

        h = hmac.new(hmac_key, ciphertext, hashlib.sha256)
        assert hmac.compare_digest(h.digest(), hmac_received), "HMAC mismatch"

        seq = int.from_bytes(frame[32:40], byteorder='big')
        iv = frame[40:56]
        ciphertext = frame[56:]

        plaintext = AES(aes_key).decrypt_cfb(ciphertext, iv=iv).decode('utf-8')
        return json.loads(plaintext)

    def _encrypt_websocket_frame(self, data):
        self._sequence_number += 1

        algo_param = b64decode(self._ws_data['algorithmParameter'])
        aes_key = bytes(algo_param[:16])
        hmac_key = bytes(algo_param[16:48])

        plaintext = json.dumps(data, separators=(",", ":"), ensure_ascii=False).encode('utf-8')

        iv = os.urandom(16)
        seq_num_bytes = self._sequence_number.to_bytes(8, byteorder='big')

        ciphertext = AES(aes_key).encrypt_cfb(plaintext, iv=iv)
        buffer = seq_num_bytes + iv + ciphertext
        h = hmac.new(hmac_key, buffer, hashlib.sha256)
        hmac_value = h.digest()
        return hmac_value + buffer

    def token_data(self):
        return self._token_data

    @property
    def result(self):
        return self._token_data is not None

    def is_alive(self):
        return self._thread.is_alive()

    def stop(self):
        self._stop = True
        if self._ws:
            self._ws.close()
        self._thread.join()

    def _worker(self):
        while not self._stop:
            resp = self._ws.recv()
            if not resp:
                break

            data = self._decrypt_websocket_frame(resp)
            if 'urn:dss:event:offDeviceLogin:refresh'.lower() in data['type'].lower():
                self._token_data = data['data']
                break
