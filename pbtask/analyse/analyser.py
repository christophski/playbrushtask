import csv
from dateutil import parser


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


def brush_time(user_entry):
    # Return the total brush time for an entry
    output = float(user_entry[2]) + float(user_entry[3]) + float(user_entry[4])
    output += float(user_entry[5]) + float(user_entry[6])
    return output


def analyse(rawdata_csv, group_csv):
    # Load data into a dictionary
    with open(rawdata_csv) as datacsv:
        rdr = csv.reader(datacsv)

        userdata = {}

        # Separate data into users in a dict
        count = 0
        for row in rdr:
            if count > 0:
                if any(row):
                    # check if user is already in dict if not add
                    if row[0] not in userdata:
                        userdata[row[0]] = {}
                        userdata[row[0]]["data"] = []
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
                    userdata[row[0]]["data"].append(newrow)
            else:
                headers = row
            count += 1

    # Add a user's group to their dictionary
    with open(group_csv) as groupscsv:
        rdr = csv.reader(groupscsv)
        count = 0
        for row in rdr:
            if count > 0:
                if any(row):
                    if row[1] in userdata:
                        userdata[row[1]]["group"] = row[0]
            count += 1

    # Ensure data is in time order (looks like it is, but just in case)
    for user in userdata:
        # Sort user's entrys by timestamp
        userdata[user]["data"].sort(key=lambda t: t[1])

    # Combine entries less than two minutes apart
    # Find the time difference between entries so we can combine
    for user in userdata:
        # List to hold updated user entrys in
        user_updated = []
        # List to cumulate entrys in until gap is larger than 2 minutes
        holding_entry = []

        # For entry in user, check if less than two minute gap and combine
        for entry in userdata[user]["data"]:
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
        userdata[user]["data"] = user_updated

    # Remove entrys less than 20s long
    for user in userdata:
        for entry in userdata[user]["data"]:
            if brush_time(entry) < 20.0:
                # print("Found a short one!")
                # print(entry)
                # Remove entry
                userdata[user]["data"].remove(entry)

    # Remove users without any data left
    empty_users = []
    for user in userdata:
        if userdata[user]["data"] == []:
            empty_users.append(user)

    for user in empty_users:
        del userdata[user]

    # Leave only longest brush session for each morning or evening
    for user in userdata:
        # List to hold longestbrush sessions in
        user_updated = []
        # List to hold current longest brush session for current morn/eve
        holding_entry = []

        # For entry in user
        for entry in userdata[user]["data"]:
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
        userdata[user]["data"] = user_updated


    # How many times did the user brush on each day?
    daysoftheweek = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

    # for entry, find day of the week and increase in dict
    for user in userdata:
        for entry in userdata[user]["data"]:
            dotw = entry[1].strftime("%a").lower()
            if dotw in userdata[user]:
                userdata[user][dotw] += 1
            else:
                userdata[user][dotw] = 1

    # Set non-existent days to 0
    for user in userdata:
        for dotw in daysoftheweek:
            if dotw in userdata[user]:
                pass
            else:
                userdata[user][dotw] = 0

    # Find total brushes && twice brushes
    for user in userdata:
        twice_brushes = 0
        total_brushes = 0
        for dotw in daysoftheweek:
            total_brushes += userdata[user][dotw]
            if userdata[user][dotw] == 2:
                twice_brushes += 1
        userdata[user]["total_brushes"] = total_brushes
        userdata[user]["twice_brushes"] = twice_brushes

    # find average brush time
    for user in userdata:
        cumulative_brush_time = 0
        count = 0
        for entry in userdata[user]["data"]:
            cumulative_brush_time += brush_time(entry)
            count += 1
        userdata[user]["average_brush_time"] = cumulative_brush_time / count


    #
    # GROUP ANALYSIS
    #

    groups = {}

    for user in userdata:
        # If group is not in the dict, set it up
        usergroup = userdata[user]["group"]
        if usergroup not in groups:
            groups[usergroup] = {
                'valid_users_in_group': 0,
                'total_valid_brush_sessions': 0,
                'total_avg_brush_time': 0,
                'avg_brush_sessions_per_user': 0,
                'avg_brush_time': 0,
                'score': 0,
                'rank': 0,
            }

        groups[usergroup]["valid_users_in_group"] += 1
        groups[usergroup]["total_valid_brush_sessions"] += userdata[user]["total_brushes"]
        groups[usergroup]["total_avg_brush_time"] += userdata[user]["average_brush_time"]

    # Calculate group averages and give the group a score
    for group in groups:
        groups[group]["avg_brush_time"] = groups[group]["total_avg_brush_time"] / groups[group]["valid_users_in_group"]
        groups[group]["avg_brush_sessions_per_user"] = groups[group]["total_valid_brush_sessions"] / groups[group]["valid_users_in_group"]
        groups[group]["score"] = groups[group]["avg_brush_sessions_per_user"] * groups[group]["avg_brush_time"]

    # Output the group rankings
    groupscores = []
    for group in groups:
        groupscores.append((group, groups[group]["score"]))

    groupscores.sort(key=lambda t: t[1], reverse=True)

    # Add rank to dictionary
    count = 1
    for group in groupscores:
        groups[group[0]]["rank"] = count
        count += 1

    return userdata, groups
