# Playbrush Data Analysis

## RULES
- Each row is a brushing session
- Merge sessions that are <2mins apart
- Total length of session = SUM(up, down, left right and none)
- Discard sessions <20s (after merges!)
- For multiple brushes in morning or evening, only keep longest
- Brushes before 2pm are morning, after are evening

How many times has the user brushed in the morning? and in the evening?
- 0 = no brush
- 1 = morning / evening brush
- 2 = morning & evening

user csv output headers:
`group,PBID,mon,tue,wed,thu,fri,sat,sun,total-brushes,twice-brushes,avg-brush-time`

## Steps:

Prepare data:
1. separate data into users
2. convert timestamps to datetime?
3. sort data by timestamp
4. combine entries that are 2m apart
5. total session length = SUM(up, down, left right and none)
6. discard sessions <20s long
7. separate brushes into morning and evening, discard all but longest
8. add group to user

User data:
1. How many times did the user brush? (mon, tue, wed, thu, fri, sat, sun)
2. total number of valid morning and evening brushes
3. Average time spent brushing per valid session

Group data:
1. how many valid brush sessions were observed total?
2. What is the average number of brushing sessions per user in that group?
3. What is the average brushing duration per user in that group?
4. Which group performed the best?
5. Rank the groups in terms of performance?