import notify2
import requests
import collections
import time
import datetime


def compute_diff(xs, ys, d='viewers'):
    added = []
    removed = []
    for k, v in ys.items():
        prev = xs.pop(k, ())
        add = set(v) - set(prev)
        rm = set(prev) - set(v)
        suffix = '' if k == d else '(%s)' % k
        added.extend(x + suffix for x in add)
        removed.extend(x + suffix for x in rm)
    return sorted(added), sorted(removed)


def summary(chatters):
    count = sum(len(v) for k, v in chatters.items())
    elena = [c for k, v in chatters.items() for c in v
             if c.startswith('elena')]
    return ', '.join(elena) if elena else '%s chatters, no elena' % count


def main():
    notify2.init('elena')

    session = requests.Session()
    url = 'https://tmi.twitch.tv/group/user/darbian/chatters'
    response = session.get(url).json(
        object_pairs_hook=collections.OrderedDict)

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
        join, leave = compute_diff(chatters, response['chatters'])
        chatters = response['chatters']
        diffstat = '+%s-%s' % (len(join), len(leave))
        print(datetime.datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'),
              diffstat)
        if join or leave:
            msg = '%s joined\n%s left' % (
                ', '.join(join), ', '.join(leave))
            n.update(summary(chatters), msg)
            n.show()


if __name__ == '__main__':
    main()
