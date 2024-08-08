#Disclaimer!!!
#I (Cristata) did not write the original code to this.
#All I did was modify it to be used as a resource for my mini-event: Finish the Line.

#The original code was written by SylviBlossom and can be found here:
# https://github.com/SylviBlossom/fusion-line-checker

#Massive kudos to them for writing this!

import re

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

print("Calculating evolutions...")

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

# Print the sorted evolution lines for verification
for line in sorted_evolution_lines:
    print([displayName[pokemon_id] for pokemon_id in line])

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

import csv

print("Checking custom sprite status...")

# File paths
input_files = {
    'main': 'mainSprites.txt',
    'temp': 'tempSprites.txt',
    'alt': 'altSprites.txt'
}

# Output files
output_files_custom_sprites = {
    'main': 'export_main_sprites.csv',
    'temp': 'export_temp_sprites.csv',
    'alt': 'export_alt_sprites.csv'
}
output_files_fusion_lines = 'export_fusion_lines.csv'
output_files_fusiondex_links = 'export_fusiondex_links.csv'
output_files_sprite_statuses = 'export_sprite_statuses.csv'  # New output file for statuses

# Data storage for each category
customSpriteIDs = {'main': [], 'temp': [], 'alt': []}
customSpriteHEAD = {'main': {}, 'temp': {}, 'alt': {}}
customSpriteBODY = {'main': {}, 'temp': {}, 'alt': {}}
customSpriteStatus = {'main': {}, 'temp': {}, 'alt': {}}  # New dictionary to store status

# Function to read and populate data from a file
def read_custom_sprites(file_path, category):
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()  # Remove any leading/trailing whitespace or newline characters
            if line:
                parts = line.split('.')
                if len(parts) == 3:  # Adjusted to handle 'head', 'body', and 'status'
                    head = parts[0]
                    body = parts[1]
                    status = parts[2]
                    sprite_id = f"{head}.{body}"
                    
                    # Populate dictionaries for the specified category
                    customSpriteIDs[category].append(sprite_id)
                    customSpriteHEAD[category][sprite_id] = head
                    customSpriteBODY[category][sprite_id] = body
                    customSpriteStatus[category][sprite_id] = status  # Store status

# Read data from each file
for category, file_path in input_files.items():
    print(f"Reading data from {file_path}...")
    read_custom_sprites(file_path, category)
print("Done")

def has_custom_sprite(category, head, body):
    return f"{head}.{body}" in customSpriteIDs[category]

def print_sprite(category, head, body):
    if has_custom_sprite(category, head, body):
        return f"https://gitlab.com/CristataC/ftl-sprites/-/raw/master/CustomBattlers/{head}.{body}.png"
    return ""

def print_dex(head, body):
    dex_link = f"https://www.fusiondex.org/{head}.{body}"
    return dex_link

def print_fusion_line(head, body):
    visited = set()
    fusion_line = "|".join(traverse_fusion_line(head, body, visited))
    return fusion_line

def traverse_fusion_line(head, body, visited):
    visited.add((head, body))
    line = []
    for fusion in fusionLines[head][body]:
        if (fusion[0], fusion[1]) not in visited:
            subline = traverse_fusion_line(fusion[0], fusion[1], visited)
            line.extend(subline)
    line.insert(0, f"{head}.{body}")
    return line

from datetime import datetime

def export_custom_sprites(category):
    # Get the current time at the start of the function
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Generating CSV files for {category} sprites. (Start time: {current_time})")

    headNames = ["", ""]
    headIds = ["", ""]
    
    # Adding headers for sprite names and IDs
    print("Creating header names and IDs...")
    for head in range(1, 471):
        headNames.append(displayName[head])
        headIds.append(str(head))
    
    spriteRows = [",".join(headNames) + "\n", ",".join(headIds) + "\n"]
    print("Done")
    
    print("Generating sprite rows... (This may take a while!)")
    for body in range(1, 471):
        spriteRow = [displayName[body], str(body)]
        for head in range(1, 471):
            sprite = print_sprite(category, head, body)
            spriteRow.append(sprite)
            # Print progress for every 10 bodies
            if head % 470 == 0 and body % 10 == 0:
                start_body = max(1, body - 9)  # Calculate the start of the range, ensuring it doesn't go below 1
                end_body = body  # Current body is the end of the range
                print(f"({category} sprites) Processed all heads for bodies {start_body}-{end_body}.")
        spriteRows.append(",".join(spriteRow) + "\n")
    
    print(f"Exporting {category} sprites...")
    with open(output_files_custom_sprites[category], "w") as file:
        file.writelines(spriteRows)
    
    print(f"Finished exporting CSV file for {category} sprites at {current_time}.")

def export_fusion_data():
    print("Generating CSV files for fused evolution lines & fusiondex links. (Start time: {current_time})")
    
    headNames = ["", ""]
    headIds = ["", ""]
    for head in range(1, 471):
        headNames.append(displayName[head])
        headIds.append(str(head))
    
    dexRows = [",".join(headNames) + "\n", ",".join(headIds) + "\n"]
    fusionLineRows = [",".join(headNames) + "\n", ",".join(headIds) + "\n"]
    
    for body in range(1, 471):
        dexRow = [displayName[body], str(body)]
        fusionLineRow = [displayName[body], str(body)]
        
        for head in range(1, 471):
            dexRow.append(print_dex(head, body))
            fusionLineRow.append(print_fusion_line(head, body))
        
        dexRows.append(",".join(dexRow) + "\n")
        fusionLineRows.append(",".join(fusionLineRow) + "\n")
    
    print("Exporting fusion lines...")
    with open(output_files_fusion_lines, "w") as file:
        file.writelines(fusionLineRows)
        
    print(f"Finished exporting fusion lines at {current_time}.")
    
    print("Exporting fusiondex links...")
    with open(output_files_fusiondex_links, "w") as file:
        file.writelines(dexRows)
    
    print(f"Finished exporting fusiondex links at {current_time}.")

def export_sprite_statuses():
    print("Generating CSV file for sprite statuses. (Start time: {current_time})")
    
    headNames = ["", ""]
    headIds = ["", ""]
    for head in range(1, 471):
        headNames.append(displayName[head])
        headIds.append(str(head))
    
    statusRows = [",".join(headNames) + "\n", ",".join(headIds) + "\n"]
    
    for body in range(1, 471):
        statusRow = [displayName[body], str(body)]
        
        for head in range(1, 471):
            status = ""
            for category in input_files.keys():  # Iterate through all categories
                if has_custom_sprite(category, head, body):
                    status = customSpriteStatus[category].get(f"{head}.{body}", "")
                    break  # Break out of loop once status is found
            
            statusRow.append(status)
            
            if head % 470 == 0 and body % 10 == 0:
                start_body = max(1, body - 9)
                end_body = body
                print(f"Processed all heads for bodies {start_body}-{end_body}.")
        
        statusRows.append(",".join(statusRow) + "\n")
    
    print("Exporting sprite statuses...")
    with open(output_files_sprite_statuses, "w") as file:
        file.writelines(statusRows)
    
    print("Finished exporting CSV file for sprite statuses at {current_time}.")

print("")
print("Enter \"[head name]/[body name]\" to check an evolution line.")
print("Enter \"export\" to export the data as CSV.")
print("Enter \"stop\" to exit.")
print("")

while True:
    fuseInput = input("Input > ").lower()

    if fuseInput == "exit" or fuseInput == "quit" or fuseInput == "stop":
        break

    if fuseInput == "export":
        export_fusion_data()
        print("")
#         for category in input_files.keys():
#             export_custom_sprites(category)
#             print("")
        export_sprite_statuses()
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