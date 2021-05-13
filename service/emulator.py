import argparse
import datetime
import json
import jsonschema
import socket

MAX_JSON_LENGTH = 250

def main():
    parser = argparse.ArgumentParser(description='Emulator')
    parser.add_argument('--ip', default='127.0.0.1', help='Listening IP address')
    parser.add_argument('--port', default=26999, type=int, help='Listening UDP port')
    parser.add_argument('--buffer', default=1024, type=int, help='Buffer size')
    args = parser.parse_args()

    with open('../iamonameeting.schema.json', 'r') as f:
        schema = jsonschema.Draft7Validator(json.load(f))

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    sock.bind((args.ip, args.port))
    sock.settimeout(1) # On windows, Ctrl+C doesn't interrupt recvfrom() without a timeout

    while True:
        try:
            try:
                data, addr = sock.recvfrom(args.buffer)
            except socket.timeout:
                continue
        except KeyboardInterrupt:
            print('User pressed Ctrl+C, aborting')
            break

        msg = data.decode("utf-8")
        obj = json.loads(msg)

        now = datetime.datetime.now()
        ts = f'{now.hour:02}:{now.minute:02}:{now.second:02}'
        print(f'[{ts}] <{addr[0]}> {msg}')
        if len(msg) > MAX_JSON_LENGTH:
            print(f'JSON is too long: {len(msg)} > {MAX_JSON_LENGTH}')

        try:
            schema.validate(obj)
        except jsonschema.exceptions.ValidationError as e:
            print(f'JSON is not ok: {e.message}')

if __name__ == '__main__':
    main()
