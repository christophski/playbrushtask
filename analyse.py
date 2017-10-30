import csv
from dateutil import parser

csvs_written = 0


def number_of_entries(user_dict):
    # Count a user's number of entries
    count = 0
    for user in user_dict:
        count += len(user_dict[user]["data"])

    return count


def combine_entries(first_entry, second_entry):
    # Combine two entries and keep timestamp from first
    if first_entry[0] != second_entry[0]:
        raise ValueError("Cannot combine entries from two different IDs")
    else:
        return [first_entry[0], first_entry[1],
                round((float(first_entry[2]) + float(second_entry[2])), 2),
                round((float(first_entry[3]) + float(second_entry[3])), 2),
                round((float(first_entry[4]) + float(second_entry[4])), 2),
                round((float(first_entry[5]) + float(second_entry[5])), 2),
                round((float(first_entry[6]) + float(second_entry[6])), 2)]


def write_csv(output, filename, csv_count):
    # Write csv data to file
    filename = "%d_%s" % (csv_count, filename)
    print("Write %d entries to csv %s" % (len(output) - 1,
                                          filename))
    newcsv = open(filename, 'w')
    with newcsv:
        writer = csv.writer(newcsv)
        writer.writerows(output)

    return csv_count + 1


def write_user_csv(user_dict, filename, csv_count):
    # Set up csv output for user data
    # Set CSV headers
    output = [["group", "PBID", "mon", "tue", "wed",
               "thu", "fri", "sat", "sun", "total-brushes",
               "twice-brushes", "avg-brush-time"]]
    for user in user_dict:
        user_row = [
            user_dict[user]["group"],
            user,
            user_dict[user]["mon"],
            user_dict[user]["tue"],
            user_dict[user]["wed"],
            user_dict[user]["thu"],
            user_dict[user]["fri"],
            user_dict[user]["sat"],
            user_dict[user]["sun"],
            user_dict[user]["total_brushes"],
            user_dict[user]["twice_brushes"],
            user_dict[user]["average_brush_time"],
            ]
        output.append(user_row)

    return write_csv(output, filename, csv_count)


def write_group_csv(group_dict, filename, csv_count):
    # set up csv output for group data
    # Set up headers
    output = [['group', 'users', 'total-valid-brushes', 'avg-brushes-per-user',
               'avg-brush-duration', 'score', 'rank']]

    for group in group_dict:
        group_row = [
            group,
            group_dict[group]["valid_users_in_group"],
            group_dict[group]["total_valid_brush_sessions"],
            group_dict[group]["avg_brush_sessions_per_user"],
            group_dict[group]["avg_brush_time"],
            group_dict[group]["score"],
            group_dict[group]["rank"],
        ]
        output.append(group_row)

    return write_csv(output, filename, csv_count)


def brush_time(user_entry):
    # Return the total brush time for an entry
    output = float(user_entry[2]) + float(user_entry[3]) + float(user_entry[4])
    output += float(user_entry[5]) + float(user_entry[6])
    return output


# Load data into a dictionary
with open('1_rawdata.csv') as data_csv:
    rdr = csv.reader(data_csv)

    user_data = {}

    # Separate data into users in a dict
    count = 0
    for row in rdr:
        if count > 0:
            if any(row):
                # check if user is already in dict if not add
                if row[0] not in user_data:
                    user_data[row[0]] = {}
                    user_data[row[0]]["data"] = []
                # add user data to dict
                # convert timestamp to datetime

                newrow = [
                    row[0],
                    parser.parse(row[1]),
                    row[2],
                    row[3],
                    row[4],
                    row[5],
                    row[6]
                ]
                # Add data to the dictionary
                user_data[row[0]]["data"].append(newrow)
        else:
            headers = row
        count += 1

# Add a user's group to their dictionary
with open('2_groups.csv') as groups_csv:
    rdr = csv.reader(groups_csv)
    count = 0
    for row in rdr:
        if count > 0:
            if any(row):
                if row[1] in user_data:
                    user_data[row[1]]["group"] = row[0]
        count += 1

# Ensure data is in time order (looks like it is, but just in case)
for user in user_data:
    # Sort user's entrys by timestamp
    user_data[user]["data"].sort(key=lambda t: t[1])

# Combine entries less than two minutes apart
# Find the time difference between entries so we can combine
for user in user_data:
    # List to hold updated user entrys in
    user_updated = []
    # List to cumulate entrys in until gap is larger than 2 minutes
    holding_entry = []

    # For entry in user, check if less than two minute gap and combine
    for entry in user_data[user]["data"]:
        # Skip the first entry as there is nothing to compare it to
        if holding_entry == []:
            holding_entry = entry
        else:
            # Find the time difference
            td = entry[1] - holding_entry[1]
            # find diff in seconds
            td = td.total_seconds()

            # If gap is smaller than 2 mins, cumulate
            if td < 120.0:
                holding_entry = combine_entries(holding_entry, entry)
            else:
                # Otherwise add holding entry to user_updated
                user_updated.append(holding_entry)

                # Set current entry to holding entry
                holding_entry = entry

    # Add last entry to user_updated
    user_updated.append(holding_entry)

    # Update user
    user_data[user]["data"] = user_updated

# Remove entrys less than 20s long
for user in user_data:
    for entry in user_data[user]["data"]:
        if brush_time(entry) < 20.0:
            # print("Found a short one!")
            # print(entry)
            # Remove entry
            user_data[user]["data"].remove(entry)

# Remove users without any data left
empty_users = []
for user in user_data:
    if user_data[user]["data"] == []:
        empty_users.append(user)

for user in empty_users:
    del user_data[user]

# Leave only longest brush session for each morning or evening
for user in user_data:
    # List to hold longestbrush sessions in
    user_updated = []
    # List to hold current longest brush session for current morn/eve
    holding_entry = []

    # For entry in user
    for entry in user_data[user]["data"]:
        # print("")
        # print(entry)
        # print(holding_entry)
        # Skip the first entry as there is nothing to compare it to
        if holding_entry == []:
            holding_entry = entry
        else:
            # Check if same date, if not, put holding_entry in user_updated
            if holding_entry[1].date() != entry[1].date():
                user_updated.append(holding_entry)
                holding_entry = entry
            elif holding_entry[1].hour < 14:
                # Before 2pm
                if entry[1].hour < 14:
                    # Both before 2pm
                    # Check which is longer and keep the longest
                    # If holding is longest we keep it to compare to
                    # the next entry

                    if brush_time(entry) > brush_time(holding_entry):
                        # print("New entry is longer")
                        holding_entry = entry
                    else:
                        # print("existing entry is longer")
                        pass
                else:
                    # entry is in different part of the day so add
                    # holding to user_updated
                    user_updated.append(holding_entry)
                    holding_entry = entry
            else:
                # Entry is after 2pm
                if entry[1].hour < 14:
                    # This error shouldn't occur with correctly sorted data
                    print("This should never occur")
                else:
                    # Both entries after 2pm
                    # Check which is longer and keep the longest
                    # If holding is longest we keep it to compare to
                    # the next entry
                    if brush_time(entry) > brush_time(holding_entry):
                        # print("New entry is longer")
                        holding_entry = entry
                    else:
                        # print("existing entry is longer")
                        pass

    # Add last entry to user_updated
    user_updated.append(holding_entry)

    # Update user
    user_data[user]["data"] = user_updated


# How many times did the user brush on each day?
days_of_the_week = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

# for entry, find day of the week and increase in dict
for user in user_data:
    for entry in user_data[user]["data"]:
        dotw = entry[1].strftime("%a").lower()
        if dotw in user_data[user]:
            user_data[user][dotw] += 1
        else:
            user_data[user][dotw] = 1

# Set non-existent days to 0
for user in user_data:
    for dotw in days_of_the_week:
        if dotw in user_data[user]:
            pass
        else:
            user_data[user][dotw] = 0

# Find total brushes && twice brushes
for user in user_data:
    twice_brushes = 0
    total_brushes = 0
    for dotw in days_of_the_week:
        total_brushes += user_data[user][dotw]
        if user_data[user][dotw] == 2:
            twice_brushes += 1
    user_data[user]["total_brushes"] = total_brushes
    user_data[user]["twice_brushes"] = twice_brushes

# find average brush time
for user in user_data:
    cumulative_brush_time = 0
    count = 0
    for entry in user_data[user]["data"]:
        cumulative_brush_time += brush_time(entry)
        count += 1
    user_data[user]["average_brush_time"] = cumulative_brush_time / count

csvs_written = write_user_csv(user_data, 'user_analysis_output.csv',
                              csvs_written)


#
# GROUP ANALYSIS
#

groups_data = {}

for user in user_data:
    # If group is not in the dict, set it up
    usergroup = user_data[user]["group"]
    if usergroup not in groups_data:
        groups_data[usergroup] = {
            'valid_users_in_group': 0,
            'total_valid_brush_sessions': 0,
            'total_avg_brush_time': 0,
            'avg_brush_sessions_per_user': 0,
            'avg_brush_time': 0,
            'score': 0,
            'rank': 0,
        }

    groups_data[usergroup]["valid_users_in_group"] += 1
    groups_data[usergroup]["total_valid_brush_sessions"] += user_data[user]["total_brushes"]
    groups_data[usergroup]["total_avg_brush_time"] += user_data[user]["average_brush_time"]

# Calculate group averages and give the group a score
for group in groups_data:
    groups_data[group]["avg_brush_time"] = groups_data[group]["total_avg_brush_time"] / groups_data[group]["valid_users_in_group"]
    groups_data[group]["avg_brush_sessions_per_user"] = groups_data[group]["total_valid_brush_sessions"] / groups_data[group]["valid_users_in_group"]
    groups_data[group]["score"] = groups_data[group]["avg_brush_sessions_per_user"] * groups_data[group]["avg_brush_time"]

# Output the group rankings
groupscores = []
for group in groups_data:
    groupscores.append((group, groups_data[group]["score"]))

groupscores.sort(key=lambda t: t[1], reverse=True)

# Add rank to dictionary
count = 1
for group in groupscores:
    groups_data[group[0]]["rank"] = count
    count += 1

csvs_written = write_group_csv(groups_data, 'group_analysis_output.csv',
                               csvs_written)
