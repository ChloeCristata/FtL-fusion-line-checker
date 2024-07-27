#Disclaimer!!!
#I (Cristata) did not write the original code to this.
#All I did was modify it slightly to be used as a resource for my mini-event: Finish the Line.

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
        
        # Register fusions between simultaneous evolutions
        for headEvo in head_evolutions:
            for bodyEvo in body_evolutions:
                if bodyEvo[1] == headEvo[1] and not bodyEvo[2] or headEvo[2]:
                    register_fusions(list, headEvo[0], bodyEvo[0], 'simultaneous')  # Evolved head with evolved body
                    register_fusions(list, head, bodyEvo[0], 'simultaneous')         # Unevolved head with evolved body
                    register_fusions(list, headEvo[0], body, 'simultaneous')         # Evolved head with unevolved body
        
        # Check if head has more stages than body
        if len(head_evolutions) > len(body_evolutions):
            for i in range(len(body_evolutions), len(head_evolutions)):
                head_stage = head_evolutions[i][0]
                register_fusions(list, head_stage, body, 'simultaneous')
        
        # Check if body has more stages than head
        elif len(body_evolutions) > len(head_evolutions):
            for i in range(len(head_evolutions), len(body_evolutions)):
                body_stage = body_evolutions[i][0]
                register_fusions(list, head, body_stage, 'simultaneous')
    
    return list

for head in range(1, 471):
    fusionLines[head] = {}
    for body in range(1, 471):
        fusionLines[head][body] = []  # Initialize fusionLines[head][body] as an empty list

for head in range(1, 471):
    for body in range(1, 471):
        if head == body:  # If head and body are the same list item, consider simultaneous evolution
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

def print_dex(head, body):
    dex_link = f"https://www.fusiondex.org/{head}.{body}"
#     print(f"DEBUG: Head={head}, Body={body}, Dex Link={dex_link}")  # Print debug info
    return dex_link

def print_fusion_line(head, body):
    visited = set()
    fusion_line = "|".join(traverse_fusion_line(head, body, visited))
#     print(f"DEBUG: Head={head}, Body={body}, Fusion Line={fusion_line}")  # Print debug info
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

def export_csv():
    print("Exporting data as CSV files...")

    headNames = ["", ""]
    headIds = ["", ""]
    for head in range(1, 471):
        headNames.append(displayName[head])
        headIds.append(str(head))
    
    fusionLineRows = [",".join(headNames) + "\n", ",".join(headIds) + "\n"]
    dexRows = [",".join(headNames) + "\n", ",".join(headIds) + "\n"]
    
    for body in range(1, 471):
        fusionLineRow = [displayName[body], str(body)]
        dexRow = [displayName[body], str(body)]
        
        for head in range(1, 471):
            fusionLineRow.append(print_fusion_line(head, body))
            dexRow.append(print_dex(head, body))
        
        fusionLineRows.append(",".join(fusionLineRow) + "\n")
        dexRows.append(",".join(dexRow) + "\n")
        
    print("Exporting fusion line chart...")
    with open("export_fusion_lines.csv", "w") as file:
        file.writelines(fusionLineRows)

    print("Exporting fusiondex links...")
    with open("export_fusiondex_links.csv", "w") as file:
        file.writelines(dexRows)

    print("Done")

print("")

import requests

SPRITEPACK_BASE_URL = "https://gitlab.com/CristataC/ftl-sprites/-/raw/master/CustomBattlers"

def export_sprite_completion():
    print("Exporting sprite completion...")

    headNames = ["", ""]
    headIds = ["", ""]
    for head in range(1, 471):
        headNames.append(displayName[head])
        headIds.append(str(head))
    
    completionRows = [",".join(headNames)+"\n", ",".join(headIds)+"\n"]
    
    for body in range(1, 471):
        completionRow = [displayName[body], str(body)]
        
        for head in range(1, 471):
            completionRow.append(print_percentage(head, body))
        
        completionRows.append(",".join(completionRow) + "\n")
    
    print("Exporting sprite completion chart...")
    with open("export_completion.csv", "w") as file:
        file.writelines(completionRows)

    print(f"Found {len(customSprites)} custom sprites.")

print("")
print("Enter \"[head name]/[body name]\" to check an evolution line.")
print("Enter \"export\" to export the data as CSV.")
print("Enter \"check sprites\" to check sprite completion and export the data as CSV.")
print("Enter \"stop\" to exit.")
print("")

while True:
    fuseInput = input("Input > ").lower()
            
    import time

    MAX_RETRIES = 3

    def sprite_exists(head, body):
        url = f"{SPRITEPACK_BASE_URL}/{head}.{body}.png"
        print(f"Checking sprite at URL: {url}")
        
        failed_urls = []
        
        retries = 0
        while retries < MAX_RETRIES:
            try:
                response = requests.head(url, allow_redirects=True)
                
                if response.status_code == 200:
                    print(f"Sprite found: {head}.{body}")
                    return True
                elif response.status_code == 302:
                    print(f"Redirected to: {response.headers['Location']}")
                    return False  # Handle redirection scenario
                else:
                    print(f"Sprite not found: {head}.{body}")
                    return False
            
            except requests.exceptions.RequestException as e:
                print(f"Request error occurred: {e}")
                failed_urls.append(url)
                retries += 1
                if retries < MAX_RETRIES:
                    print(f"Retrying ({retries}/{MAX_RETRIES})...")
                    time.sleep(1)  # Adding a small delay before retrying
        
        print(f"Failed to retrieve sprite after {MAX_RETRIES} attempts.")
        return False, failed_urls

        print(f"The following URLs could not be retrieved: {failed_urls}")

    customSpriteList = []

    for head in range(1, 471):
        for body in range(1, 471):
            if sprite_exists(head, body):
                customSpriteList.append(f"{head}.{body}")

    customSprites = set(customSpriteList)

    print("Done")

    def has_custom_sprite(head, body):
        return f"{head}.{body}" in customSprites

    def print_percentage(head, body):
       fusions = fusionLines[head][body]
       count = 0.0
       for fusion in fusions:
           if has_custom_sprite(fusion[0], fusion[1]):
               count += 1
       return str((count / len(fusions)) * 100) + "%"

    if fuseInput == "exit" or fuseInput == "quit" or fuseInput == "stop":
        break

    if fuseInput == "export":
        export_csv()
        print("")
        continue
    
    if fuseInput == "check sprites":
        sprite_exists()
        export_sprite_completion()
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
        if has_custom_sprite(pair[0], pair[1]):
            print(f"✓ {displayName[pair[0]]} / {displayName[pair[1]]}")
        else:
            print(f"  {displayName[pair[0]]} / {displayName[pair[1]]}")

    print("")