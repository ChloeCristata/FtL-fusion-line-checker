#Disclaimer!!!
#I (Cristata) did not write the original code to this.
#All I did was modify it slightly to be used as a resource for my mini-event: Finish the Line.

#The original code was written by SylviBlossom and can be found here:
# https://github.com/SylviBlossom/fusion-line-checker

#Massive kudos to them for writing this!

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

#for i in range(1, 421):
#    if evolvedFrom[i] != None:
#        print(f"{displayName[i]} can evolve from {displayName[evolvedFrom[i]]} at level {baseLevel[i]}")
#    else:
#        print(f"{displayName[i]} is a base pokemon")

print("Calculating all fused evolution lines...")

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
        for headEvo in evolutions[head]:
            for bodyEvo in evolutions[body]:
                if bodyEvo[1] == headEvo[1] and not bodyEvo[2] or headEvo[2]:
                    register_fusions(list, headEvo[0], bodyEvo[0], 'simultaneous')  # Register fusion between evolved head and evolved body
                    register_fusions(list, head, bodyEvo[0], 'simultaneous')         # Register fusion between unevolved head and evolved body
                    register_fusions(list, headEvo[0], body, 'simultaneous')         # Register fusion between evolved head and unevolved body
    
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



#If you're reading this, you probably understand how this code works better than I do tbh
#I literally don't understand coding like... at all. I just bashed my head into a wall until I figured some stuff out.
#Then when I stopped figuring stuff out I just cheated and asked an AI to help me.
#To my credit tho, the AI was both incredibly smart and incredibly stupid and even with help it was A CHORE to get it to work.
                
#I don't want to just like... delete what I had managed to do by myself tho because then it'd feel like a waste of time which...
#...is debateable. On one hand: good brain workout, on the other: I had other things to do and... I didn't... RIP.
#Anyways--here's my abandoned WIP version:

#fusionLines = {}

#def register_fusions(list, head, body):
#    if [head, body] in list:
#        return list
#    list.append([head, body])
#    for headEvo in evolutions[head]:
#        soonerBody = False
#        equalBody = False
#        for bodyEvo in evolutions[body]:
#            if bodyEvo[1] < headEvo[1] and not bodyEvo[2]:
#                soonerBody = True
#            elif bodyEvo[1] == headEvo[1] and not bodyEvo[2]:
#                equalBody = True
#                break
#        if soonerBody:  
#            register_fusions(list, headEvo[0], body)
#        elif equalBody: 
#            register_fusions(list, headEvo[0], bodyEvo[0])
#    for bodyEvo in evolutions[body]:
#        soonerHead = False
#        equalHead = False
#        for headEvo in evolutions[head]:
#            if headEvo[1] < bodyEvo[1] and not headEvo[2]:
#                soonerHead = True
#            elif headEvo[1] == bodyEvo[1] and not headEvo[2]:
#                equalHead = True
#                break
#        if soonerHead: 
#            register_fusions(list, head, bodyEvo[0])
#        elif equalHead:
#            register_fusions(list, headEvo[0], bodyEvo[0])
#    return list

#for head in range(1, 471):
#    fusionLines[head] = {}
#    for body in range(1, 471):
#        fusionLines[head][body] = register_fusions([], head, body)


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
#        return "If you aren't peeking at the code right now, I have serious questions."
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
    
    
    
    
# Just so I don't lose it.... here's a list of every pokemon in IF, sorted by evolution line:
# Bulbasaur, Ivysaur, Venusaur
# Charmander, Charmeleon, Charizard
# Squirtle, Wartortle, Blastoise
# Caterpie, Metapod, Butterfree
# Weedle, Kakuna, Beedrill
# Pidgey, Pidgeotto, Pidgeot
# Rattata, Raticate
# Spearow, Fearow
# Ekans, Arbok
# Sandshrew, Sandslash
# Nidoran F, Nidorina, Nidoqueen
# Nidoran M, Nidorino, Nidoking
# Vulpix, Ninetales
# Zubat, Golbat, Crobat
# Oddish, Gloom, Vileplume, Bellossom
# Paras, Parasect
# Venonat, Venomoth
# Diglett, Dugtrio
# Meowth, Persian
# Psyduck, Golduck
# Mankey, Primeape
# Growlithe, Arcanine
# Poliwag, Poliwhirl, Poliwrath, Politoed
# Abra, Kadabra, Alakazam
# Machop, Machoke, Machamp
# Bellsprout, Weepinbell, Victreebel
# Tentacool, Tentacruel
# Geodude, Graveler, Golem
# Ponyta, Rapidash
# Slowpoke, Slowbro, Slowking
# Magnemite, Magneton, Magnezone
# Farfetch'd
# Doduo, Dodrio
# Seel, Dewgong
# Grimer, Muk
# Shellder, Cloyster
# Gastly, Haunter, Gengar
# Onix, Steelix
# Drowzee, Hypno
# Krabby, Kingler
# Voltorb, Electrode
# Exeggcute, Exeggutor
# Cubone, Marowak
# Lickitung, Lickilicky
# Koffing, Weezing
# Rhyhorn, Rhydon, Rhyperior
# Tangela, Tangrowth
# Kangaskhan
# Horsea, Seadra, Kingdra
# Goldeen, Seaking
# Staryu, Starmie
# Scyther, Scizor
# Pinsir
# Tauros
# Magikarp, Gyarados
# Lapras
# Ditto
# Eevee, Vaporeon, Jolteon, Flareon, Espeon, Umbreon, Leafeon, Glaceon, Sylveon
# Porygon, Porygon2, Porygon-Z
# Omanyte, Omastar
# Kabuto, Kabutops
# Aerodactyl
# Articuno
# Zapdos
# Moltres
# Dratini, Dragonair, Dragonite
# Mewtwo
# Mew
# Chikorita, Bayleef, Meganium
# Cyndaquil, Quilava, Typhlosion
# Totodile, Croconaw, Feraligatr
# Sentret, Furret
# Hoothoot, Noctowl
# Ledyba, Ledian
# Spinarak, Ariados
# Chinchou, Lanturn
# Pichu, Pikachu, Raichu
# Cleffa, Clefairy, Clefable
# Igglybuff, Jigglypuff, Wigglytuff
# Togepi, Togetic, Togekiss
# Natu, Xatu
# Mareep, Flaaffy, Ampharos
# Hoppip, Skiploom, Jumpluff
# Aipom, Ambipom
# Sunkern, Sunflora
# Yanma, Yanmega
# Wooper, Quagsire
# Murkrow, Honchkrow
# Misdreavus, Mismagius
# Unown
# Girafarig
# Pineco, Forretress
# Dunsparce
# Gligar, Gliscor
# Snubbull, Granbull
# Qwilfish
# Shuckle
# Heracross
# Sneasel, Weavile
# Teddiursa, Ursaring
# Slugma, Magcargo
# Swinub, Piloswine, Mamoswine
# Corsola
# Remoraid, Octillery
# Delibird
# Skarmory
# Houndour, Houndoom
# Phanpy, Donphan
# Stantler
# Smeargle
# Tyrogue, Hitmonlee, Hitmonchan, Hitmontop
# Smoochum, Jynx
# Elekid, Electabuzz, Electivire
# Magby, Magmar, Magmortar
# Miltank
# Raikou
# Entei
# Suicune
# Larvitar, Pupitar, Tyranitar
# Lugia
# Ho-Oh
# Celebi
# Azurill, Marill, Azumarill
# Wynaut, Wobbuffet
# Bonsly, Sudowoodo
# Mime Jr., Mr. Mime
# Happiny, Chansey, Blissey
# Munchlax, Snorlax
# Mantyke, Mantine
# Treecko, Grovyle, Sceptile
# Torchic, Combusken, Blaziken
# Mudkip, Marshtomp, Swampert
# Ralts, Kirlia, Gardevoir, Gallade
# Kecleon
# Beldum, Metang, Metagross
# Bidoof, Bibarel
# Spiritomb
# Gible, Gabite, Garchomp
# Mawile
# Lileep, Cradily
# Anorith, Armaldo
# Cranidos, Rampardos
# Shieldon, Bastiodon
# Absol
# Duskull, Dusclops, Dusknoir
# Arceus
# Turtwig, Grotle, Torterra
# Chimchar, Monferno, Infernape
# Piplup, Prinplup, Empoleon
# Nosepass, Probopass
# Honedge, Doublade, Aegislash
# Pawniard, Bisharp
# Kyogre
# Groudon
# Rayquaza
# Dialga
# Palkia
# Giratina
# Regigigas
# Darkrai
# Genesect
# Reshiram
# Zekrom
# Kyurem
# Rotom
# Litwick, Lampent, Chandelure
# Pyukumuku
# Klefki
# Mimikyu
# Deino, Zweilous, Hydreigon
# Latias
# Latios
# Deoxys
# Jirachi
# Nincada, Ninjask, Shedinja
# Riolu, Lucario
# Slakoth, Vigoroth, Slaking
# Wailmer, Wailord
# Shinx, Luxio, Luxray
# Aron, Lairon, Aggron
# Trapinch, Vibrava, Flygon
# Feebas, Milotic
# Bagon, Shelgon, Salamence
# Klink, Klang, Klinklang
# Zorua, Zoroark
# Budew, Roselia, Roserade
# Drifloon, Drifblim
# Buneary, Lopunny
# Shroomish, Breloom
# Shuppet, Banette
# Solosis, Duosion, Reuniclus
# Cottonee, Whimsicott
# Sandile, Krokorok, Krookodile
# Yamask, Cofagrigus
# Joltik, Galvantula
# Ferroseed, Ferrothorn
# Axew, Fraxure, Haxorus
# Golett, Golurk
# Fletchling, Fletchinder, Talonflame
# Larvesta, Volcarona
# Stunfisk
# Sableye
# Venipede, Whirlipede, Scolipede
# Tyrunt, Tyrantrum
# Snorunt, Glalie, Froslass
# Oricorio Baile
# Oricorio Pom-Pom
# Oricorio Pa'u
# Oricorio Sensu
# Trubbish, Garbodor
# Carvanha, Sharpedo
# Phantump, Trevenant
# Noibat, Noivern
# Swablu, Altaria
# Goomy, Sliggoo, Goodra
# Regirock
# Regice
# Registeel
# Necrozma
# Stufful, Bewear
# Dhelmise
# Mareanie, Toxapex
# Hawlucha
# Cacnea, Cacturne
# Sandygast, Palossand
# Amaura, Aurorus
# Rockruff, Lycanroc Midnight, Lycanroc Midday
# Meloetta Aria
# Meloetta Pirouette
# Cresselia
# Bruxish
# Ultra Necrozma