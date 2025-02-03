import datetime
import codecs
import csv
import re

#regex to find date within message
date_and_time = re.compile(r'\(\d\d\d\d-\d\d-\d\d \d\d:\d\d\)')

#regex to find messages with at least one 3-letter word in them
words = re.compile(r'[a-zA-Z]{3}')

#open file and split into message lines
entire_log = codecs.open('groupme_logs.txt', 'r', 'utf+8').readlines()


messages = []
for line in entire_log:
    if '(SYS)' not in line[:5]: #ignoring system lines (name change, add person)
        try:
            message = []
            message.append(line.split(date_and_time.findall(line)[0])[0])
            message.append(date_and_time.findall(line)[0])
            rest_of_message = ''
            for i in line.split(date_and_time.findall(line)[0])[1].split(': ')[1:]:
                rest_of_message += i + ': '
            rest_of_message = rest_of_message[:-2]
            message.append(rest_of_message)
            messages.append(message) #splits each message into name, date, and message, then adds
        except:
            continue

for number, message in enumerate(messages): #makes each timestamp into a datetime object
    timestamp = message[1][1:-1]

    date = timestamp.split(' ')[0]
    time = timestamp.split(' ')[1]

    year = int(date.split('-')[0])
    month = int(date.split('-')[1])
    day = int(date.split('-')[2])
    hour = int(time.split(':')[0])
    minutes = int(time.split(':')[1])

    messages[number][1] = datetime.datetime(year, month, day, hour, minutes)

nicknames = []
for line in entire_log:
    if '(SYS)' in line[:6] and 'changed name to' in line:
        names = line.split(': ')[1]
        changes = names.split(' changed name to ')
        for number, name in enumerate(nicknames):
            if changes[0] in name[1]:
                nicknames[number][1].append(changes[1].strip())
                break
        else:
            nicknames.append((changes[0], [changes[1].strip()]))

for number, message in enumerate(messages): #replaces all nicknames with original name in message info
    for name in nicknames:
        if message[0] in name[1]:
            messages[number][0] = name[0]

for number, message in enumerate(messages): #replaces all nicknames with original name in summons
    for name in nicknames:
        for nickname in name[1]:
            if '@' + nickname in message[2]:
                messages[number][2] = message[2].replace(nickname, name[0])


all_names = []
for message in messages: #list of all names who have sent messages
    if message[0] not in all_names:
    	all_names.append(message[0])

all_words = [] #just adds all messages into one long list of words
for message in messages:
    for word in message[2].split(' '):
        all_words.append(word)

with open('groupme_logs.csv', 'wb') as csvfile:
    new_csv = csv.writer(csvfile, delimiter=',')
    entire_thing = []
    for message in messages:
        row = []
        row.append(codecs.encode(message[0], 'ascii', 'backslashreplace'))
        row.append(message[1])
        row.append(codecs.encode(message[2], 'ascii', 'backslashreplace').lower()[:-1])
        entire_thing.append(row)
    new_csv.writerows(entire_thing)


#~~~~~~~~~~~~~end of setup portion~~~~~~~~~~~~~~~~~~

total_messages = len(messages)
avg_message_length = len(all_words)/total_messages #average number of words per message

#~~~~~~~~~~FINDING MESSAGE NUMBER PER PERSON~~~~~~~~~~~~~~~~
message_number_per_person = {}  #finds total number of messages sent by each person
for name in all_names:
    message_number_per_person[name] = 0
for message in messages:
    message_number_per_person[message[0]] += 1

sorted_message_number_per_person = sorted(message_number_per_person, key=lambda x: message_number_per_person[x])[::-1]

total_words_per_person = {} #finds total number of words sent by each person
for name in all_names:
    total_words_per_person[name] = 0
for message in messages:
    total_words_per_person[message[0]] += len(message[2].split(' '))

message_length_per_person = {} #finds average message length of each person
for name in all_names:
    message_length_per_person[name] = total_words_per_person[name]/message_number_per_person[name]

sorted_message_length_per_person = sorted(message_length_per_person, key=lambda x: message_length_per_person[x])[::-1]

for person in all_names: #removes inactive people because sample bias
    if message_number_per_person[person] < 100:
        sorted_message_length_per_person.remove(person)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#~~~~~~~~~~ALL CAPS SECTION~~~~~~~~~~~~~~~~

caps_messages = [] #list of all messages written in all caps
for message in messages:
    if message[2].upper() == message[2] and words.findall(message[2]):
        caps_messages.append(message)

percentage_caps = round(float(len(caps_messages))/float(total_messages),4)*100

caps_messages_per_person = {} #finds number of messages in all caps per person
for name in all_names:
    caps_messages_per_person[name] = 0
for message in caps_messages:
    caps_messages_per_person[message[0]] += 1

caps_percentages_per_person = {} #finds percentage of each person's messages in all caps
for name in all_names:
    caps_percentages_per_person[name] = 0
for name in caps_messages_per_person:
    caps_percentages_per_person[name] = round(float(caps_messages_per_person[name])/float(message_number_per_person[name]), 4)*100

sorted_caps_percentages_per_person = sorted(caps_percentages_per_person, key=lambda x: caps_percentages_per_person[x])[::-1]

for person in all_names: #removes inactive people because sample bias
    if message_number_per_person[person] < 100:
        sorted_caps_percentages_per_person.remove(person)


#~~~~~~~~~~TIME SECTION~~~~~~~~~~~~~~~~
longest_time = datetime.timedelta(0) #finds longest interval between 2 consecutive messages
longest_interval = (0,0)
for index in range(1,total_messages):
    if messages[index][1] - messages[index-1][1] > longest_time:
        longest_time = messages[index][1] - messages[index-1][1]
        longest_interval = (messages[index-1][1], messages[index][1])

most_active_day = (0, 0) #finds most active day
day = messages[0][1].date()
day_messages = 0
for message in messages: #loops through and keeps adding 1 to the current day count if it's the same day
    if message[1].date() == day:
        day_messages += 1
    else: #if this is the first message of the next day, it changes the day, checks to see if it broke the active day record, then sets the new day's count to 1
        if day_messages > most_active_day[1]:
            most_active_day = (message[1].date() - datetime.timedelta(1), day_messages)
        day = message[1].date()
        day_messages = 1

#~~~~~~~~~~~~~~MOST SUMMONED PEOPLE~~~~~~~~~~~~~~~~~~~~~~~~~~~~
summons_per_person = {}  #finds total number of messages sent by each person
for name in all_names:
    summons_per_person[name] = 0
for message in messages:
    for name in all_names:
        if '@' + name in message[2]:
            summons_per_person[name] += 1

sorted_summons_percentages_per_person = sorted(summons_per_person, key=lambda x: summons_per_person[x])[::-1]
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#~~~~~~~~~~~~~~PRINTING SECTION~~~~~~~~~~~~~~~~~~~~~~~~~~~~

print '-------Dab-8 GroupMe Analysis 3000 (Deluxe Edition)-------\n\n'
print 'Active since ' + str(messages[0][1])
print 'Total number of messages: ' + str(total_messages)
print '\n'
print 'Top 10 most active members:'
n = 1
for person in sorted_message_number_per_person[:10]:
    print '\t' + str(n) + ') ' + person + ': ' + str(message_number_per_person[person]) + ' messages'
    n += 1
print '\n'
print 'Average message length: ' + str(avg_message_length) + ' words'
print 'Top 10 most verbose members:'
n = 1
for person in sorted_message_length_per_person[:10]:
    print '\t' + str(n) + ') ' + person + ': ' + str(message_length_per_person[person]) + ' words/message'
    n += 1
print '\n'
print 'Percentage of messages in all caps: ' + str(percentage_caps) + '%'
print 'Top 10 most screamy members:'
n = 1
for person in sorted_caps_percentages_per_person[:10]:
    print '\t' + str(n) + ') ' + person + ': ' + str(caps_percentages_per_person[person]) + '%'
    n += 1
print '\n'
print 'Top 10 most summoned members:'
n = 1
for person in sorted_summons_percentages_per_person[:10]:
    print '\t' + str(n) + ') ' + person + ': ' + str(summons_per_person[person]) + ' summons'
    n += 1
print '\n'
print '\n'
print 'Most active day: ' + str(most_active_day[0]) + ' (' + str(most_active_day[1]) + ' messages)'
print 'Longest time between consecutive messages: ' + str(longest_time)
print '\tfrom ' + str(longest_interval[0]) + ' to ' + str(longest_interval[1])
