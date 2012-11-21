#!/usr/bin/env python
from __future__ import division
from datetime import datetime
from utils import com, getsec, gethour
from collections import defaultdict, OrderedDict
import time
import os
import json
import re
import msvcrt
import sys

#set clearscreen to win32 or linux
clear_fn = 'cls' if sys.platform == 'win32' else 'clear'
usrdrive = os.getenv('SystemDrive')

loop = True  # Main loop
listofgames = []  # A list of games that are being imported.

clear_fn = 'cls' if sys.platform == 'win32' else 'clear'  # clearscreen crossplatform

overallstats = {}  # Dict of overall stats for a player

# list of stats I care about
aggregate_stats = ['kills', 'deaths', 'assists', 'physicalDamageDealt', 'magicDamageDealt', 'physicalDamageTaken', 'magicDamageTaken', 'lost', 'gold', 'healed', 'minions', 'neutralMinionsKilled']

#list of Settings:
settingexplain = ['God Mode', 'Show Players with 1 game played in list.', 'Extended player info.', 'EXPERIMENTAL-Show Leveling rate (NYI).', 'Show overall averages when showing champ info.', 'Main profile.', 'Smurf Profile', 'Compare your main profile to others. (NYI)']
setting = ['0', '1', '1', '1', '1', 'AndyBear13', 'None', '1']
settingloc = ['0', '1', '2', '3', '4', '5', '6', '7']


#list all player names that have been played with
def lister():
    quit = ''
    count = 0
    global setting
    os.system(clear_fn)
    print 'List all Players (list), or type in a name'
    usrinput = raw_input('Enter: ')
    if usrinput == 'list':
        os.system(clear_fn)
        count = 0
        players = defaultdict(int)  # dict for counting how many times a player has been played with.
        l = []  # Temp list for displaying players and times played with.
        print 'Player Name - Times played with\n'
        for f in full:
            players[f['summoner']] += 1

        for key, value in sorted(players.iteritems(), reverse=True, key=lambda (v, k): (k, v)):
            if setting[1] == '0':
                if value == 1:
                    continue
            a = '%s - %s' % (key.ljust(19), value)
            l.append(a)
            if len(l) == 2:
                print '    '.join(l)
                l = []
            count += 1

            if count >= 30:
                print '\nPress a key to view more or Q to enter a profile name or quit.\n'
                quit = msvcrt.getch()
                count = 0
            if quit == 'q' or quit == 'Q':
                break
        if len(l) == 1:
            print ''.join(l)

        usrinput = raw_input('Enter a profile name or hit enter to continue: ')
        select = False
        for x in full:
            if usrinput == x['summoner']:
                select = True

        if select:
            selection(usrinput)
        else:
            print '\nNo summoner by that name, try again. Remember search is case sensitive.\n'
            print 'Press a key to continue'
            msvcrt.getch()
    else:
        select = False
        for x in full:
            if usrinput == x['summoner']:
                select = True

        if select:
            selection(usrinput)
        else:
            print '\nNo summoner by that name, try again. Remember search is case sensitive.\n'
            print 'Press a key to continue'
            msvcrt.getch()


def settings():
    #changes settings. Mostly for printing more or less information. Also choosing favourite summoners.
    #possibly save these settings between sessions.
    os.system(clear_fn)
    global setting
    defloop = True
    while defloop:
        os.system(clear_fn)
        print 'Settings: Hit your selection to toggle a setting, or (Q) to exit and save.'
        for x in range(len(setting)):
            if x == 0:
                continue
            if setting[x] == '1':
                print '(%s) - State: ON - Setting: %s' % (x, settingexplain[x])
            elif setting[x] == '0':
                print '(%s) - State: OFF - Setting: %s' % (x, settingexplain[x])
            else:
                print '(%s) - State: %s - Setting: %s' % (x, setting[x], settingexplain[x])

        print 'Enter a Selection:'
        usrinput = msvcrt.getch()

        for x in range(len(setting)):
            if usrinput == '0':
                break
            if usrinput == settingloc[x]:
                if setting[x] == '0':
                    setting[x] = '1'
                else:
                    setting[x] = '0'
        if usrinput == '0':
            if setting[0] == '0':
                setting[0] = '1'
                print 'GM ENABLED'
            else:
                setting[0] = '0'
                print 'GONE'

        if usrinput == '5':
            usrinput = raw_input('Enter your main characters profile Name: ')
            setting[5] = usrinput
        if usrinput == '6':
            usrinput = raw_input('Enter your smurf characters profile Name: ')
            setting[6] = usrinput

        if usrinput == 'q' or usrinput == 'Q':
            break


def overall(usrinput):
    os.system(clear_fn)
    length = 0
    #vars
    usr_stats = overallstats.get(usrinput)
    if not usr_stats:
        usr_stats = defaultdict(int)

    for x in full:
        if usrinput == x['summoner']:
            for k in aggregate_stats:
                usr_stats[k] += x.get(k, 0)

            if x['won']:
                usr_stats['won'] += 1
            if not x['won']:
                usr_stats['lost'] += 1
            length += getsec(x['length'])
    #total game length
    tlength = gethour(length)
    #avg game length = alength
    alength = length / (usr_stats['won'] + usr_stats['lost'])
    alength = gethour(alength)
    #print it!
    print '~Total Stats Across All Games for %s~ \n' % (usrinput)
    print 'Games: %s - Wins: %s - Losses %s - Win: %.2f%% - Time Played: %s' % (usr_stats['won'] + usr_stats['lost'], usr_stats['won'], usr_stats['lost'], usr_stats['won'] / (usr_stats['won'] + usr_stats['lost']) * 100, tlength)
    try:
        print 'Kills: %s - Deaths: %s - Assists: %s - KDR: %.2f \n' % (com(usr_stats['kills']), com(usr_stats['deaths']), com(usr_stats['assists']), usr_stats['kills'] / usr_stats['deaths'])
    except ZeroDivisionError:
        print 'Kills: %s - Deaths: %s - Assists: %s - KDR: 0 \n' % (com(usr_stats['kills']), com(usr_stats['deaths']), com(usr_stats['assists']))
    print 'Damage Dealt'
    print 'Phyiscal: %s - Magical: %s - Total: %s \n' % (com(usr_stats['physicalDamageDealt']), com(usr_stats['magicDamageDealt']), com(usr_stats['physicalDamageDealt'] + usr_stats['magicDamageDealt']))
    print 'Damage Received'
    print 'Phyiscal: %s - Magical: %s - Total: %s \n' % (com(usr_stats['physicalDamageTaken']), com(usr_stats['magicDamageTaken']), com(usr_stats['physicalDamageTaken'] + usr_stats['magicDamageTaken']))
    print 'Gold: %s - Healing: %s - CreepScore: %s \n' % (com(usr_stats['gold']), com(usr_stats['healed']), com(usr_stats['neutralMinionsKilled'] + usr_stats['minions']))
    print 'Time Averages/Min'
    print 'Game Length: %s - Gold: %s - CS: %.2f ' % (alength, com((usr_stats['gold'] / length) * 60), ((usr_stats['neutralMinionsKilled'] + usr_stats['minions']) / length) * 60)
    print 'Kills: %.2f - Deaths: %.2f - Assists: %.2f \n' % ((usr_stats['kills'] / length) * 60, (usr_stats['deaths'] / length) * 60, (usr_stats['assists'] / length) * 60)

    print 'Press a Key to continue'
    msvcrt.getch()


#Poops out a list of champions that have been used. May add how many times champion has been used.
def champs(summ):
    defloop = True
    while defloop:
        l = []
        o = []
        os.system(clear_fn)
        for x in full:
            if summ == x['summoner']:
                if x['champion'] in o:
                    continue
                o.append(x['champion'])
                l.append(x['champion'])

                if len(l) == 2:
                    print '\t   '.join(l)
                    l = []
        if len(l) == 1:
            print '    '.join(l)
        usrinput = raw_input('\nEnter a Champion name to view more info on it, or type Q to quit:\n')

        if usrinput == 'q' or usrinput == 'Q':
            break

        if usrinput in o:
            champinfo(usrinput, summ)
            break

        else:
            print 'Not a valid champion selection. Press a key to try again.'
            msvcrt.getch()


def champinfo(champ, summ):
    length = 0
    overall_length = 0
    usr_stats = overallstats.get(champ)
    overall_stats = overallstats.get(summ)
    if not overall_stats:
        overall_stats = defaultdict(int)
    if not usr_stats:
        usr_stats = defaultdict(int)
    #Gather stats for the champion selected.
    for x in full:
        if summ == x['summoner']:
            if champ == x['champion']:
                for k in aggregate_stats:
                    usr_stats[k] += x.get(k, 0)
                if x['won']:
                    usr_stats['won'] += 1
                if not x['won']:
                    usr_stats['lost'] += 1
                length += getsec(x['length'])
    #Gather stats from all of the summoners champ if setting is enabled.
    if setting[4] == '1':
        for x in full:
            if summ == x['summoner']:
                for k in aggregate_stats:
                    overall_stats[k] += x.get(k, 0)
                if x['won']:
                    overall_stats['won'] += 1
                if not x['won']:
                    overall_stats['lost'] += 1
                overall_length += getsec(x['length'])
        #total Game length = tlength
        #overall_tlength = gethour(overall_length)
        #avg game length = alength
        overall_alength = overall_length / (overall_stats['won'] + overall_stats['lost'])
        overall_alength = gethour(overall_alength)

    #total game length
    tlength = gethour(length)
    #avg game length = alength
    alength = length / (usr_stats['won'] + usr_stats['lost'])
    alength = gethour(alength)
    os.system(clear_fn)

    print '~Total Stats Across All Games for %s with %s~ \n' % (summ, champ)
    print 'Games: %s - Wins: %s - Losses %s - Win: %.2f%% - Time Played: %s' % (usr_stats['won'] + usr_stats['lost'], usr_stats['won'], usr_stats['lost'], usr_stats['won'] / (usr_stats['won'] + usr_stats['lost']) * 100, tlength)
    try:
        print 'Kills: %s - Deaths: %s - Assists: %s - KDR: %.2f \n' % (com(usr_stats['kills']), com(usr_stats['deaths']), com(usr_stats['assists']), usr_stats['kills'] / usr_stats['deaths'])
    except ZeroDivisionError:
        print 'Kills: %s - Deaths: %s - Assists: %s - KDR: 0 \n' % (com(usr_stats['kills']), com(usr_stats['deaths']), com(usr_stats['assists']))
    print 'Damage Dealt'
    print 'Phyiscal: %s - Magical: %s - Total: %s \n' % (com(usr_stats['physicalDamageDealt']), com(usr_stats['magicDamageDealt']), com(usr_stats['physicalDamageDealt'] + usr_stats['magicDamageDealt']))
    print 'Damage Received'
    print 'Phyiscal: %s - Magical: %s - Total: %s \n' % (com(usr_stats['physicalDamageTaken']), com(usr_stats['magicDamageTaken']), com(usr_stats['physicalDamageTaken'] + usr_stats['magicDamageTaken']))
    print 'Gold: %s - Healing: %s - CreepScore: %s \n' % (com(usr_stats['gold']), com(usr_stats['healed']), com(usr_stats['neutralMinionsKilled'] + usr_stats['minions']))
    print 'Time Averages/Min'
    print 'Game Length: %s - Gold: %s - CS: %.2f ' % (alength, com((usr_stats['gold'] / length) * 60), ((usr_stats['neutralMinionsKilled'] + usr_stats['minions']) / length) * 60)
    print 'Kills: %.2f - Deaths: %.2f - Assists: %.2f' % ((usr_stats['kills'] / length) * 60, (usr_stats['deaths'] / length) * 60, (usr_stats['assists'] / length) * 60)

    if setting[4] == '1':
        print '\nTime Averages/Min over all champions'
        print 'Game Length: %s - Gold: %s - CS: %.2f ' % (overall_alength, com((overall_stats['gold'] / overall_length) * 60), ((overall_stats['neutralMinionsKilled'] + overall_stats['minions']) / overall_length) * 60)
        print 'Kills: %.2f - Deaths: %.2f - Assists: %.2f' % ((overall_stats['kills'] / overall_length) * 60, (overall_stats['deaths'] / overall_length) * 60, (overall_stats['assists'] / overall_length) * 60)
    print '\nPress a Key to continue'
    msvcrt.getch()


#Not sure if this is a good feature.
def maps(summ):
    count = 0
    os.system(clear_fn)
    quit = ''
    for x in full:
        if summ == x['summoner']:
            count += 1
            print 'Champion: %s' % (x['champion'])
            print 'Date: %s - Won: %s - Length: %s' % (x['datetime'], x['won'], x['length'])
            try:
                print 'Kills: %s - Deaths: %s - Assists: %s - KDR: %.2f' % (x['kills'], x['deaths'], x['assists'], x['kills'] / x['deaths'])
            except ZeroDivisionError:
                print 'Kills: %s - Deaths: %s - Assists: %s - KDR: 0' % (x['kills'], x['deaths'], x['assists'])

            print 'Dealt: Phyiscal: %s - Magical: %s - Total: %s' % (com(x['physicalDamageDealt']), com(x['magicDamageDealt']), com(x['physicalDamageDealt'] + x['magicDamageDealt']))
            print 'Received: Phyiscal: %s - Magical: %s - Total: %s' % (com(x['physicalDamageTaken']), com(x['magicDamageTaken']), com(x['physicalDamageTaken'] + x['magicDamageTaken']))
            print 'Gold: %s - Healing: %s - CreepScore: %s ' % (com(x['gold']), com(x['healed']), com(x['neutralMinionsKilled'] + x['minions']))
            length = getsec(x['length'])
            print 'Gold/Min: %s - CS/Min: %.2f\n' % (com((x['gold'] / length) * 60), ((x['neutralMinionsKilled'] + x['minions']) / length) * 60)

            if quit == 'q' or quit == 'Q':
                break

            if count >= 2:
                print 'Press a key to view more or Q to quit\n'
                quit = msvcrt.getch()
                count = 0
                os.system(clear_fn)
    print '\nPress a Key to continue'
    msvcrt.getch()


def sort(summ):
    print 'Sort by: Champion (1), Date (2), Game Length (3)'
    usrinput = msvcrt.getch()

    os.system(clear_fn)
    count = 0
    ID = 0
    quit = ''
    alist = defaultdict(lambda: defaultdict(int))  # dict for counting how many times a champion has be used.
    for x in full:
        ID += 1
        if summ == x['summoner']:
            dates = datetime.strptime(x['datetime'], '%Y-%m-%d %H:%M:%S')
            alist[x['match']]['date'] = dates
            alist[x['match']]['champion'] = x['champion']
            alist[x['match']]['length'] = x['length']
            alist[x['match']]['won'] = x['won']
            alist[x['match']]['ID'] = str(ID)

    asort = OrderedDict(sorted(alist.iteritems(), key=lambda x: x[1]['date']))

    if usrinput == '1':
        asort = OrderedDict(sorted(alist.iteritems(), key=lambda x: x[1]['champion']))

    if usrinput == '2':
        asort = OrderedDict(sorted(alist.iteritems(), key=lambda x: x[1]['date']))

    if usrinput == '3':
        asort = OrderedDict(sorted(alist.iteritems(), key=lambda x: x[1]['length']))

    for k, v in asort.iteritems():
        print 'Champion: %s - Date: %s - ID: %s' % (v['champion'], v['date'], v['ID'])
        print 'Length: %s - Won: %s \n' % (v['length'], v['won'])
        count += 1

        if count >= 7:
            print 'Press a key to view more or Q to enter an ID or quit.\n'
            quit = msvcrt.getch()
            count = 0
            if quit == 'q' or quit == 'Q':
                break
            os.system(clear_fn)

    usrinput = raw_input('Enter an ID to view that game, or just hit enter: ')

    for k, v in asort.iteritems():
        if v['ID'] == usrinput:
            gameid(summ, k)


def gameid(summ, matchid):
    count = 0
    page = 1
    quit = ''
    for x in full:
        if matchid == x['match']:
            if summ == x['summoner']:
                myteam = x['team']
                originalteam = x['team']
                os.system(clear_fn)
                print 'Your Info \n'
                print 'Champion: %s - Team: %s' % (x['champion'], x['team'])
                print 'Date: %s - Won: %s - Length: %s' % (x['datetime'], x['won'], x['length'])
                try:
                    print 'Kills: %s - Deaths: %s - Assists: %s - KDR: %.2f' % (x['kills'], x['deaths'], x['assists'], x['kills'] / x['deaths'])
                except ZeroDivisionError:
                    print 'Kills: %s - Deaths: %s - Assists: %s - KDR: 0' % (x['kills'], x['deaths'], x['assists'])

                print 'Dealt: Phyiscal: %s - Magical: %s - Total: %s' % (com(x['physicalDamageDealt']), com(x['magicDamageDealt']), com(x['physicalDamageDealt'] + x['magicDamageDealt']))
                print 'Received: Phyiscal: %s - Magical: %s - Total: %s' % (com(x['physicalDamageTaken']), com(x['magicDamageTaken']), com(x['physicalDamageTaken'] + x['magicDamageTaken']))
                print 'Gold: %s - Healing: %s - CreepScore: %s' % (com(x['gold']), com(x['healed']), com(x['neutralMinionsKilled'] + x['minions']))
                length = getsec(x['length'])
                print 'Gold/Min: %s - CS/Min: %.2f\n' % (com((x['gold'] / length) * 60), ((x['neutralMinionsKilled'] + x['minions']) / length) * 60)

    print 'Press a Key to view your teams info.\n'
    msvcrt.getch()

    #Teammate and enemy INFO
    for t in range(2):
        for x in full:
            if matchid == x['match']:
                if summ == x['summoner']:
                    continue
                elif myteam == x['team']:
                    if count == 0:
                        os.system(clear_fn)
                        print '~Player: %s~' % (page)

                    count += 1
                    try:
                        x['minions'] + 1
                    except KeyError:
                        print 'Summoner: %s - Champion: %s - ~LEAVER~\n' % (x['summoner'], x['champion'])
                        continue
                    print 'Summoner: %s - Champion: %s - Team: %s' % (x['summoner'], x['champion'], x['team'])
                    if setting[2] == '0':
                        print 'Kills: %s - Deaths: %s - Assists: %s - CreepScore: %s \n' % (x['kills'], x['deaths'], x['assists'], com(x['neutralMinionsKilled'] + x['minions']))

                    if setting[2] == '1':
                        try:
                            print 'Kills: %s - Deaths: %s - Assists: %s - KDR: %.2f' % (x['kills'], x['deaths'], x['assists'], x['kills'] / x['deaths'])
                        except ZeroDivisionError:
                            print 'Kills: %s - Deaths: %s - Assists: %s - KDR: 0' % (x['kills'], x['deaths'], x['assists'])
                        print 'Dealt: Phyiscal: %s - Magical: %s - Total: %s' % (com(x['physicalDamageDealt']), com(x['magicDamageDealt']), com(x['physicalDamageDealt'] + x['magicDamageDealt']))
                        print 'Received: Phyiscal: %s - Magical: %s - Total: %s' % (com(x['physicalDamageTaken']), com(x['magicDamageTaken']), com(x['physicalDamageTaken'] + x['magicDamageTaken']))
                        print 'Gold: %s - Healing: %s - CreepScore: %s ' % (com(x['gold']), com(x['healed']), com(x['neutralMinionsKilled'] + x['minions']))
                        length = getsec(x['length'])
                        print 'Gold/Min: %s - CS/Min: %.2f\n' % (com((x['gold'] / length) * 60), ((x['neutralMinionsKilled'] + x['minions']) / length) * 60)

                    if count >= 1:
                        print '\nPress a key to view more or Q to quit\n'
                        quit = msvcrt.getch()
                        count = 0
                        page += 1
                    if quit == 'q' or quit == 'Q':
                        break
        if myteam == originalteam:
            print 'Press a Key to view enemy teams info.\n'
        else:
            print 'Finished: Press a key to quit.'
        msvcrt.getch()

        page = 1
        count = 0
        if myteam == 1:
            myteam = 2
        if myteam == 2:
            myteam = 1


def selection(summ):
    defloop = True
    while defloop:
        os.system(clear_fn)
        print 'Summoner: %s' % (summ)
        print 'Overall Stats (1), Champion (2), Map (3), Sort (4), Back (6)'
        usrinput = msvcrt.getch()
        if usrinput == '1':
            overall(summ)

        if usrinput == '2':
            champs(summ)

        if usrinput == '3':
            maps(summ)

        if usrinput == '4':
            sort(summ)

        if usrinput == '6':
            break


#json with all the collected info
p = open('%s/dropbox/code/python/app/lolpact/complete.json' % (usrdrive))
full = json.load(p)
p.close()

#load file and make it searchable.
try:  # Home Path
    for files in os.listdir('%s/Users/Administrator/Documents/LOLReplay/replays' % (usrdrive)):
        if files.endswith('.lrf_done'):
            listofgames.append(files)
except:  # Work path
    for files in os.listdir('%s/' % (usrdrive)):
        if files.endswith('.lrf5'):
            listofgames.append(files)

print 'Reading new files...\n'
for gamecount in range(len(listofgames)):
    print listofgames[gamecount]
    #opens (by default) C:/<first file in directory>
    try:  # can be deleted latars
        o = open('%s/Users/Administrator/Documents/LOLReplay/replays/%s' % (usrdrive, listofgames[gamecount]), 'r')  # Home Path
    except:
        o = open('%s/%s' % (usrdrive, listofgames[gamecount]), 'r')  # Work Path

    data = o.read()
    o.close()
    fullpath = '%s/Users/Administrator/Documents/LOLReplay/replays/' % (usrdrive) + listofgames[gamecount]
    #os.rename(fullpath,fullpath + '_done')
    x = 0

    #Grabs the date of the match
    tempdate = re.search(r'"createTime"[\s\S].*(PM|AM)"', data)
    x = tempdate.group()
    z = x[14:-1]
    date = datetime.strptime(z, '%b %d, %Y %I:%M:%S %p')
    date = str(date)

    #Match duration "matchLength":1247,
    temptime = re.findall(r'"matchLength"\s*(\:.*?\,)', data)
    temptime = int(temptime[0][1:-1])
    seconds = int(temptime % 60)
    #To fix seconds being rounded. (20 is 2 instead.)
    if seconds < 9:
        seconds = seconds * 10

    seconds = str(seconds)
    minutes = str(int(temptime / 60))
    length = minutes + ':' + seconds

    #Readies the json file of the matches results
    data = re.findall(r'"players":\s*(\[.*?\])', data)
    data = json.loads(data[0])

    for x in data:
        x['match'] = listofgames[gamecount]
        x['datetime'] = date
        x['length'] = length
        #Checks for stats that may be missing, adds 0 value if so.
        try:
            x['neutralMinionsKilled'] + 1
        except KeyError:
            x['neutralMinionsKilled'] = 0
        try:
            x['healed'] + 1
        except KeyError:
            x['healed'] = 0
        try:
            x['magicDamageDealt'] + 1
        except KeyError:
            x['magicDamageDealt'] = 0
    #Add delay, some errors if it reads files to fast?

    time.sleep(0.2)
    full = full + data

#write to json file
write_file = open('%s/dropbox/code/python/app/lolpact/complete.json' % (usrdrive), 'w')
write_file.write(json.dumps(full, indent=4))
write_file.close()

#main Menu
while loop:
    os.system(clear_fn)
    print 'League of Legends Player and Champion Tracker - LoLPaCT'
    print 'Favourites (1), Search Players (2), Settings (3) Exit (6):'
    usrinput = msvcrt.getch()
    if usrinput == '1':
        print '\n%s(1), %s(2)' % (setting[5], setting[6])
        usrinput = msvcrt.getch()
        select = False
        if usrinput == '1':
            for x in full:
                if setting[5] == x['summoner']:
                    select = True
            if select:
                selection(setting[5])
            else:
                print 'Please set a main profile in settings before using favourites.\nPress a key to continue'
                msvcrt.getch()
                continue
            usrinput = ''

        if usrinput == '2':
            for x in full:
                if setting[6] == x['summoner']:
                    select = True
            if select:
                selection(setting[6])
            else:
                print 'Please set a main profile in settings before using favourites.\nPress a key to continue'
                msvcrt.getch()
                continue
            usrinput = ''

    elif usrinput == '2':
        lister()

    elif usrinput == '3':
        settings()

    elif usrinput == '6':
        os.system(clear_fn)
        break
