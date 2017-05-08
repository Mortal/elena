import notify2
import requests
import collections
import time
import datetime
import json


VERSION = '0.1'
USER_AGENT = 'https://github.com/Mortal/elena ' + VERSION
CHANNEL = 'darbian'
PREFIX = 'elena'
APP_NAME = 'elena'


def summary(chatters):
    count = sum(len(v) for k, v in chatters.items())
    found = [c for k, v in chatters.items() for c in v
             if c.startswith(PREFIX)]
    return (', '.join(found) if found else
            '%s chatters, no %s' % (count, PREFIX))


def compute_diff(xs, ys, d='viewers'):
    added = []
    removed = []
    for k, v in ys.items():
        prev = xs.pop(k, ())
        add = set(v) - set(prev)
        rm = set(prev) - set(v)
        suffix = '' if k == d else '(%s)' % k
        added.extend(sorted(x + suffix for x in add))
        removed.extend(sorted(x + suffix for x in rm))
    return added, removed


def save_response(response):
    now_str = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = 'chatters/%s_%s.json' % (CHANNEL, now_str)
    try:
        with open(filename, 'w') as fp:
            json.dump(response, fp)
    except OSError as exn:
        print("Failed to open %r for writing: %s" %
              (filename, exn))


def main():
    notify2.init(APP_NAME)

    session = requests.Session()
    session.headers['User-Agent'] = USER_AGENT
    url = 'https://tmi.twitch.tv/group/user/%s/chatters' % CHANNEL
    response = session.get(url).json(
        object_pairs_hook=collections.OrderedDict)

    save_response(response)
    chatters = response['chatters']
    msg = ', '.join('%s %s' % (len(v), k)
                    for k, v in chatters.items() if v)
    n = notify2.Notification(summary(chatters), msg,
                             'notification-message-im')
    n.show()

    while True:
        time.sleep(60)
        response = session.get(url).json(
            object_pairs_hook=collections.OrderedDict)
        save_response(response)
        join, leave = compute_diff(chatters, response['chatters'])
        chatters = response['chatters']
        summ = summary(chatters)
        print(datetime.datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'), summ)
        if join or leave:
            msg = '%s joined\n%s left' % (
                ', '.join(join), ', '.join(leave))
            print(msg)
            n.update(summ, msg)
            n.show()


if __name__ == '__main__':
    main()
