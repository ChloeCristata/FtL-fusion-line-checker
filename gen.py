# Disclaimer!!!
# I (Cristata) did not write the original code to this.
# All I did was modify it to be used as a resource for my mini-event: Finish the Line.

# The original code was written by SylviBlossom and can be found here:
# https://github.com/SylviBlossom/fusion-line-checker

# Massive kudos to them for writing this!



                    # I had little to no part in writing the following sections of this code:


import re
import csv
from collections import defaultdict

def chunks(arr: list, n: int):
    for i in range(0, len(arr), n):
        yield arr[i:i + n]

nameFromId = {}
idFromName = {}
idFromDisplayName = {}
displayName = {}

moveLevels = {}
rawEvolutions = {}
hasPreEvo = {}

print("Parsing pokemon data...")

with open("pokemon.txt") as file:
    processing = None

    for rawline in file:
        line = rawline.rstrip()

        if line[0] == "#":
            continue
        elif line[0] == "[":
            processing = int(line[1:-1])

            rawEvolutions[processing] = []
            moveLevels[processing] = {}
            if not processing in hasPreEvo:
                hasPreEvo[processing] = False

            continue

        if processing == None:
#            print("Unexpected line")
            continue
        
        match = re.match(r"(\S+)\s*=\s*(.+)", line)
        if match == None:
            continue

        matchKey = match.group(1)
        matchValue = match.group(2)

        if matchKey == "Name":
            if processing == 29:
                matchValue = "Nidoran F"
            elif processing == 32:
                matchValue = "Nidoran M"
            elif processing == 430:
                matchValue = "Oricorio Baile"
            elif processing == 431:
                matchValue = "Oricorio Pom-Pom"
            elif processing == 432:
                matchValue = "Oricorio Pa'u"
            elif processing == 433:
                matchValue = "Oricorio Sensu"
            elif processing == 464:
                matchValue = "Lycanroc Midday"
            elif processing == 465:
                matchValue = "Lycanroc Midnight"
            elif processing == 466:
                matchValue = "Meloetta Aria"
            elif processing == 467:
                matchValue = "Meloetta Pirouette"
            elif processing == 470:
                matchValue = "Ultra Necrozma"
            displayName[processing] = matchValue
            idFromDisplayName[matchValue.lower()] = processing
        elif matchKey == "InternalName":
            nameFromId[processing] = matchValue
            idFromName[matchValue] = processing
        elif matchKey == "Moves":
            for chunk in chunks(matchValue.split(","), 2):
                moveLevels[processing][chunk[1]] = int(chunk[0])
        elif matchKey == "Evolutions":
            rawEvolutions[processing] = list(chunks(matchValue.split(","), 3))
            for evolution in rawEvolutions[processing]:
                hasPreEvo[evolution[0]] = True

print("Calculating evolution lines...")
print("Done")

evolutions = {}
baseLevel = {}
evolvedFrom = {}

def register_evolutions(id, lvl, preEvo):
    if id in evolutions:
        return  # Skip if already registered

    evolutions[id] = []
    baseLevel[id] = lvl
    evolvedFrom[id] = preEvo

    for evolution in rawEvolutions[id]:
        evoId = idFromName[evolution[0]]
        evoLevel = lvl
        evoOptional = False

        if evolution[1] == "Level":
            evoLevel = int(evolution[2])
        elif (evolution[1] == "HasMove") and (evolution[2] in moveLevels[id]):
            evoLevel = int(moveLevels[id][evolution[2]])
            if evoLevel <= lvl:
                evoOptional = True
        else:
            evoOptional = True

        evoLevel = max(evoLevel, lvl)

        evolutions[id].append([evoId, evoLevel, evoOptional])
        register_evolutions(evoId, evoLevel, id)

# Start by registering evolution lines for Pokémon with no pre-evolutions
for i in range(1, 471):
    if not hasPreEvo.get(nameFromId[i], False):
        register_evolutions(i, 1, None)

# Sort the evolution lines based on the evolution relationships
sorted_evolution_lines = []
visited = set()

def traverse_evolution_line(pokemon_id):
    visited.add(pokemon_id)
    line = [pokemon_id]
    for evo_id, _, _ in evolutions[pokemon_id]:
        if evo_id not in visited:
            line.extend(traverse_evolution_line(evo_id))
    return line

for pokemon_id in evolutions.keys():
    if pokemon_id not in visited:
        sorted_evolution_lines.append(traverse_evolution_line(pokemon_id))

# Convert Pokémon IDs to their display names
sorted_evolution_lines_with_names = [
    [displayName[pokemon_id] for pokemon_id in line]
    for line in sorted_evolution_lines
]

# Create a dictionary to store sorted evolution lines by the lowest Pokémon name
sorted_name_to_evolution_line = {}

# Create a dictionary to map each display name to its evolution line
name_to_evolution_line = {}
for line in sorted_evolution_lines_with_names:
    # Extract valid Pokémon names that exist in idFromDisplayName
    valid_pokemon_names = [pokemon_name for pokemon_name in line if pokemon_name.lower() in idFromDisplayName]
    
    if valid_pokemon_names:
        # Find the lowest valid Pokémon ID from the valid names using idFromDisplayName
        lowest_id = min(idFromDisplayName[name.lower()] for name in valid_pokemon_names)
        # Find the corresponding Pokémon name for the lowest ID
        lowest_name = displayName[lowest_id]
        name_to_evolution_line[lowest_name] = line

# Check if name_to_evolution_line has entries
if not name_to_evolution_line:
    print("No valid Pokémon names found in evolution lines.")
else:
    # Sort the evolution lines based on the lowest ID in the line
    sorted_evolution_lines_sorted_by_names = sorted(
        name_to_evolution_line.values(),
        key=lambda line: min(idFromDisplayName[name.lower()] for name in line if name.lower() in idFromDisplayName)
    )

    # Create a dictionary to map each lowest Pokémon name to its sorted evolution line
    for line in sorted_evolution_lines_sorted_by_names:
        # Find the lowest valid Pokémon ID from the line
        lowest_id = min(idFromDisplayName[name.lower()] for name in line if name.lower() in idFromDisplayName)
        # Find the corresponding Pokémon name for the lowest ID
        lowest_name = displayName[lowest_id]
        sorted_name_to_evolution_line[lowest_name] = line

    # Write the sorted evolution lines with display names to a file
    with open("sorted_pokemon_lines.txt", "w", newline='') as file:
        writer = csv.writer(file)
        writer.writerows(sorted_evolution_lines_sorted_by_names)

print("")
print("All evolution lines have been sorted below and exported to 'sorted_pokemon_lines.txt' for further use.")
print("")

# Print the sorted evolution lines with display names for verification
for line in sorted_evolution_lines_sorted_by_names:
    print(line)

fusionLines = {}

def register_fusions(list, head, body, evolution_type='sequential'):
    if [head, body] in list:
        return list
    list.append([head, body])
    
    if evolution_type == 'sequential':
        # Head evolves first
        for headEvo in evolutions[head]:
            soonerBody = False
            for bodyEvo in evolutions[body]:
                if bodyEvo[1] < headEvo[1] and not bodyEvo[2]:
                    soonerBody = True
                    break
            if soonerBody:
                continue
            register_fusions(list, headEvo[0], body, 'sequential')
            
        # Body evolves first
        for bodyEvo in evolutions[body]:
            soonerHead = False
            for headEvo in evolutions[head]:
                if headEvo[1] < bodyEvo[1] and not headEvo[2]:
                    soonerHead = True
                    break
            if soonerHead:
                continue
            register_fusions(list, head, bodyEvo[0], 'sequential')
    
    elif evolution_type == 'simultaneous':
        head_evolutions = evolutions[head]
        body_evolutions = evolutions[body]
        
        # Register initial simultaneous evolutions
        for headEvo in head_evolutions:
            for bodyEvo in body_evolutions:
                if bodyEvo[1] == headEvo[1] and not bodyEvo[2] or headEvo[2]:
                    register_fusions(list, headEvo[0], bodyEvo[0], 'simultaneous')
                    register_fusions(list, head, bodyEvo[0], 'simultaneous')
                    register_fusions(list, headEvo[0], body, 'simultaneous')
        
        # Check for subsequent sequential evolutions after simultaneous evolution
        for headEvo in head_evolutions:
            for bodyEvo in body_evolutions:
                if bodyEvo[1] > headEvo[1] and not bodyEvo[2]:
                    register_fusions(list, headEvo[0], body, 'sequential')
                if headEvo[1] > bodyEvo[1] and not headEvo[2]:
                    register_fusions(list, head, bodyEvo[0], 'sequential')
    
    return list

# Initialize fusionLines dictionary
for head in range(1, 471):
    fusionLines[head] = {}
    for body in range(1, 471):
        fusionLines[head][body] = []  # Initialize fusionLines[head][body] as an empty list

# Populate fusionLines with fusion registrations
for head in range(1, 471):
    for body in range(1, 471):
        if head == body:  # If head and body are the same, consider simultaneous evolution
            fusionLines[head][body] = register_fusions([], head, body, evolution_type='simultaneous')
        elif [head, body] in fusionLines[head][body]:  # Check if fusion already registered
            continue
        else:
            # Check if head evolves before body
            if any(headEvo[1] < bodyEvo[1] for headEvo in evolutions[head] for bodyEvo in evolutions[body]):
                fusionLines[head][body] = register_fusions([], head, body, evolution_type='sequential')
            # Check if body evolves before head
            elif any(bodyEvo[1] < headEvo[1] for bodyEvo in evolutions[body] for headEvo in evolutions[head]):
                fusionLines[head][body] = register_fusions([], head, body, evolution_type='sequential')
            # If neither, then simultaneous evolution
            else:
                fusionLines[head][body] = register_fusions([], head, body, evolution_type='simultaneous')
                
            # If head doesn't evolve, but body does, consider all body evolutions
            if not evolutions[head]:
                for bodyEvo in evolutions[body]:
                    fusionLines[head][body] += register_fusions([], head, bodyEvo[0], evolution_type='sequential')
            # If body doesn't evolve, but head does, consider all head evolutions
            if not evolutions[body]:
                for headEvo in evolutions[head]:
                    fusionLines[head][body] += register_fusions([], headEvo[0], body, evolution_type='sequential')

            # If both head and body don't evolve, consider all combinations of evolutions
            if not evolutions[head] and not evolutions[body]:
                for headEvo in evolutions[head]:
                    for bodyEvo in evolutions[body]:
                        fusionLines[head][body] += register_fusions([], headEvo[0], bodyEvo[0], evolution_type='simultaneous')

print("")
print("Checking custom sprite status...")

file_path = 'spritestatuses.txt'

customSpriteIDs = set()
customSpriteHEAD = {}
customSpriteBODY = {}
customSpriteStatus = {}

# Open the file and read each line
with open(file_path, 'r') as file:
    for line in file:
        line = line.strip()
        if line:
            parts = line.split('.')
            if len(parts) == 3:
                head, body, status = parts
                sprite_id = f"{head}.{body}"
                customSpriteIDs.add(sprite_id)
                customSpriteHEAD[sprite_id] = head
                customSpriteBODY[sprite_id] = body
                customSpriteStatus[sprite_id] = status
            else:
                print(f"Skipping invalid line: {line}")

print("Done")

def has_custom_sprite(head, body):
    return f"{head}.{body}" in customSpriteIDs

def print_status(head, body):
    return customSpriteStatus.get(f"{head}.{body}", "No custom sprites yet!")

def print_sprite(head, body):
    if has_custom_sprite(head, body):
        return f"https://gitlab.com/CristataC/ftl-sprites/-/raw/master/CustomBattlers/{head}.{body}.png"
    return " "

def print_dex(head, body):
    return f"https://www.fusiondex.org/{head}.{body}"

def print_fusion_line(head, body):
    visited = set()
    return "|".join(traverse_fusion_line(head, body, visited))

def traverse_fusion_line(head, body, visited):
    visited.add((head, body))
    line = [f"{head}.{body}"]
    for fusion in fusionLines[head][body]:
        if (fusion[0], fusion[1]) not in visited:
            line.extend(traverse_fusion_line(fusion[0], fusion[1], visited))
    return line

def export_csv_data():
    print("Generating CSV files for custom sprites, fused evolution lines, and fusiondex links.")
    
    headNames = ["", ""] + [displayName[i] for i in range(1, 471)]
    headIds = ["", ""] + [str(i) for i in range(1, 471)]
    
    # Prepare CSV data
    dexRows = [headNames, headIds]
    fusionLineRows = [headNames, headIds]
    spriteRows = [headNames, headIds]

    for body in range(1, 471):
        dexRow = [displayName[body], str(body)]
        fusionLineRow = [displayName[body], str(body)]
        spriteRow = [displayName[body], str(body)]

        for head in range(1, 471):
            sprite_id = f"{head}.{body}"
            dexRow.append(print_dex(head, body))
            fusionLineRow.append(print_fusion_line(head, body))
            spriteRow.append(print_sprite(head, body))
            
            # Print progress for every 10 bodies
            if head % 470 == 0 and body % 47 == 0:
                start_body = max(1, body - 46)
                end_body = body
                print(f"Processed all heads for bodies {start_body}-{end_body}.")

        dexRows.append(dexRow)
        fusionLineRows.append(fusionLineRow)
        spriteRows.append(spriteRow)

    # Write CSV files in bulk
    with open("export_custom_sprites.csv", "w", newline='') as file:
        writer = csv.writer(file)
        writer.writerows(spriteRows)

    with open("export_fusion_lines.csv", "w", newline='') as file:
        writer = csv.writer(file)
        writer.writerows(fusionLineRows)

    with open("export_fusiondex_links.csv", "w", newline='') as file:
        writer = csv.writer(file)
        writer.writerows(dexRows)

    print("Finished generating and exporting CSV files for custom sprites, fused evolution lines, and fusiondex links.")

def export_sprite_statuses():
    print("Generating CSV file for sprite statuses.")

    headNames = ["", ""] + [displayName[i] for i in range(1, 471)]
    headIds = ["", ""] + [str(i) for i in range(1, 471)]
    
    statusRows = [headNames, headIds]

    for body in range(1, 471):
        statusRow = [displayName[body], str(body)]
        
        for head in range(1, 471):
            statusRow.append(print_status(head, body))
            
            # Print progress for every 10 bodies
            if head % 470 == 0 and body % 47 == 0:
                start_body = max(1, body - 46)
                end_body = body
                print(f"Processed all heads for bodies {start_body}-{end_body}.")
                
        statusRows.append(statusRow)
    
    # Write CSV file in bulk
    with open("export_sprite_statuses.csv", "w", newline='') as file:
        writer = csv.writer(file)
        writer.writerows(statusRows)
    
    print("Finished exporting CSV file for sprite statuses.")


                    # I had little to no part in writing the following sections of this code:


print("")
print("Enter \"[head name]/[body name]\" to check an evolution line.")
print("Enter \"export\" to export the data as CSV.")
print("Enter \"info\" for info on the CSV sheets.")
print("Enter \"stop\" to exit.")
print("")

while True:
    fuseInput = input("Input > ").lower()

    if fuseInput in ("exit", "quit", "stop"):
        break

    if fuseInput == "export":
        export_csv_data()
        print("")
        export_sprite_statuses()
        print("")
        continue


                    # Well, except for the "info" part, that's all me:


    if fuseInput == "info":
        print("")
        print("\"export\" will generate data for the following CSV files:")
        print("")
        print("	export_custom_sprites.csv")
        print("	export_fusion_lines.csv")
        print("	export_fusiondex_links.csv")
        print("	export_sprite_statuses.csv")
        print("")
        print("Each of these files corresponds to a sheet within the auto-chart.")
        print("These sheets contain essential data!")
        print("As such, they MUST be re-exported monthly once fusiondex.org has been updated to the newest sprite pack.")
        print("")
        print("")
        print("Before exporting, make sure to run \"spritecheck.py\"!")
        print("\"Spritecheck.py\" generates a TXT file which is used by \"export_sprite_statuses.csv\".")
        print("If it isn't updated, then the CSV file won't be updated either.")
        print("")
        print("")
        print("Once exported, the corresponding sheets within the auto-chart will need to be updated.")
        print("To update the auto-chart sheets...")
        print("")
        print("	1. Use ctrl+A to select all of the cells in the sheet,")
        print("	2. Press the delete key to clear the cells,")
        print("	3. Navigate the menus: File > Import > Upload > Browse,")
        print("	4. Select the corresponding CSV file,")
        print("	5. Change \"Import location\" to \"Append to current sheet\",")
        print("	6. Hit \"Import Data\".")
        print("")
        print("(Repeat for all of the sheets/CSV files)")
        print("")
        print("")
        print("")
        print("--SCROLL UP FOR INFO--")
        print("Or enter a new input below!")
        print("")
        continue
    
    fusion = fuseInput.split("/")
    if len(fusion) != 2:
        print("Invalid input ( Head / Body )")
        print("")
        continue

    headInput = fusion[0].strip()
    bodyInput = fusion[1].strip()
    head = 0
    body = 0

    if headInput.isnumeric():
        head = int(headInput)
    elif headInput.lower() in idFromDisplayName:
        head = idFromDisplayName[headInput.lower()]
    elif headInput.upper() in idFromName:
        head = idFromName[headInput.upper()]

    if bodyInput.isnumeric():
        body = int(bodyInput)
    elif bodyInput.lower() in idFromDisplayName:
        body = idFromDisplayName[bodyInput.lower()]
    elif bodyInput.upper() in idFromName:
        body = idFromName[bodyInput.upper()]
    
    if head < 1 or head > 470 or body < 1 or body > 470:
        print("Invalid input ( Head / Body )")
        print("")
        continue

    for pair in fusionLines[head][body]:
        print(f"  {displayName[pair[0]]} / {displayName[pair[1]]}")

    print("")