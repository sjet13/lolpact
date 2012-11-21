#Simply adds commands for every 1000's. Awesome function!
def com(number):
    s = '%d' % number
    groups = []
    while s and s[-1].isdigit():
        groups.append(s[-3:])
        s = s[:-3]
    return s + ','.join(reversed(groups))


#gets seconds. Turns 32:20 (MM:SS) into seconds for mathing
def getsec(s):
    l = s.split(':')
    return int(l[0]) * 60 + int(l[1])


#Turns 24243 (S) into HH:MM:SS (or MM:SS if under 1 hour)
def gethour(t):
    m, s = divmod(t, 60)
    h, m = divmod(m, 60)
    time = '%d:%02d:%02d' % (h, m, s)
    if h == 0:
        time = '%02d:%02d' % (m, s)
    return time
