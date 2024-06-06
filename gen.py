import math
import re
import os.path

SPRITEPACK_PATH = "sprites"

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
                #print(f"Found move level {evoLevel}: {evolution[2]} on {displayName[id]} (evolved at {lvl})")
                evoOptional = True
        else:
            evoOptional = True

        evoLevel = max(evoLevel, lvl)

        evolutions[id].append([evoId, evoLevel, evoOptional])
        register_evolutions(evoId, evoLevel, id)

for i in range(1, 471):
    if not hasPreEvo.get(nameFromId[i], False):
        register_evolutions(i, 1, None)

#for i in range(1, 421):
#    if evolvedFrom[i] != None:
#        print(f"{displayName[i]} can evolve from {displayName[evolvedFrom[i]]} at level {baseLevel[i]}")
#    else:
#        print(f"{displayName[i]} is a base pokemon")

print("Calculating all fused evolution lines...")

fusionLines = {}

def register_fusions(list, head, body):
    if [head, body] in list:
        return list
    list.append([head, body])
    for headEvo in evolutions[head]:
        soonerBody = False
        for bodyEvo in evolutions[body]:
            if bodyEvo[1] <= headEvo[1] and not bodyEvo[2]:
                soonerBody = True
                break
        if soonerBody:
            continue
        register_fusions(list, headEvo[0], body)
    for bodyEvo in evolutions[body]:
        soonerHead = False
        for headEvo in evolutions[head]:
            if headEvo[1] < bodyEvo[1] and not headEvo[2]:
                soonerHead = True
                break
        if soonerHead:
            continue
        register_fusions(list, head, bodyEvo[0])
    return list

for head in range(1, 471):
    fusionLines[head] = {}
    for body in range(1, 471):
        fusionLines[head][body] = register_fusions([], head, body)

#print("Checking custom sprite status...")
#
#customSpriteList = []
#
#for head in range(1, 471):
#    for body in range(1, 471):
#        if os.path.isfile(os.path.join(SPRITEPACK_PATH, "CustomBattlers", f"{head}.{body}.png")):
#            customSpriteList.append(f"{head}.{body}")
#
#customSprites = set(customSpriteList)

print("Done")


#def has_custom_sprite(head, body):
#    return f"{head}.{body}" in customSprites

#def print_percentage(head, body):
#    fusions = fusionLines[head][body]
#    count = 0.0
#    for fusion in fusions:
#        if has_custom_sprite(fusion[0], fusion[1]):
#            count += 1
#    return str((count / len(fusions)) * 100) + "%"

def print_fusion_line(head, body):
    nums = []
    for fusion in fusionLines[head][body]:
        nums.append(f"{fusion[0]}.{fusion[1]}")
    return "|".join(nums)

def print_sprite(head, body):
#    if has_custom_sprite(head, body):
#        return "Something has either gone horribly right or horribly wrong."
    return f"https://if.daena.me/{head}.{body}"

def export_csv():
    print("Exporting data...")

    headNames = ["",""]
    headIds = ["",""]
    for head in range(1, 471):
        headNames.append(displayName[head])
        headIds.append(str(head))
#    completionRows = [",".join(headNames)+"\n", ",".join(headIds)+"\n"]
    fusionLineRows = [",".join(headNames)+"\n", ",".join(headIds)+"\n"]
    spriteRows     = [",".join(headNames)+"\n", ",".join(headIds)+"\n"]
    for body in range(1, 471):
#        completionRow = [displayName[body], str(body)]
        fusionLineRow = [displayName[body], str(body)]
        spriteRow     = [displayName[body], str(body)]
        for head in range(1, 471):
#            completionRow.append(print_percentage(head, body))
            fusionLineRow.append(print_fusion_line(head, body))
            spriteRow    .append(print_sprite(head, body))
#        completionRows.append(",".join(completionRow) + "\n")
        fusionLineRows.append(",".join(fusionLineRow) + "\n")
        spriteRows    .append(",".join(spriteRow    ) + "\n")

#    print("Exporting completion chart...")
#    with open("export_completion.csv", "w") as file:
#        file.writelines(completionRows)
    
    print("Exporting fusion line chart...")
    with open("export_fusion_lines.csv", "w") as file:
        file.writelines(fusionLineRows)

#    print("Exporting sprite chart...")
    with open("export_sprites.csv", "w") as file:
        file.writelines(spriteRows)

    print("Done")

print("")
#print(f"Found {len(customSprites)} custom sprites")

print("")
print("Enter \"[head name]/[body name]\" to check an evolution line.")
print("Enter \"export\" to export the data as CSV.")
print("Enter \"stop\" to exit.")
print("")

while True:
    fuseInput = input("Fuse > ").lower()

    if fuseInput == "exit" or fuseInput == "quit" or fuseInput == "stop":
        break

    if fuseInput == "export":
        export_csv()
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
#        if has_custom_sprite(pair[0], pair[1]):
#            print(f"✓ {displayName[pair[0]]} / {displayName[pair[1]]}")
#        else:
            print(f"  {displayName[pair[0]]} / {displayName[pair[1]]}")
    
    print("")