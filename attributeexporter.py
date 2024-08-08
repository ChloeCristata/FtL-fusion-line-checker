import os

NAME_REPLACEMENTS = {
    32: "Nidoran M",
    430: "Oricorio Baile",
    431: "Oricorio Pom-Pom",
    432: "Oricorio Pa'u",
    433: "Oricorio Sensu",
    464: "Lycanroc Midday",
    465: "Lycanroc Midnight",
    466: "Meloetta Aria",
    467: "Meloetta Pirouette",
    470: "Ultra Necrozma"
}

def read_pokemon_file(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
    
    pokemontxt = []
    current_pokemon = {}
    for line in lines:
        line = line.strip()
        if line.startswith("["):
            if current_pokemon:
                pokemontxt.append(current_pokemon)
                current_pokemon = {}
            current_pokemon['ID'] = line[1:-1]
        elif line.startswith("Name = "):
            current_pokemon['Name'] = line[len("Name = "):]
        elif line.startswith("Evolutions = "):
            evo_info = line[len("Evolutions = "):]
            evo_split = evo_info.split(',')
            current_pokemon['Evolutions'] = {
                'Name': evo_split[0],
                'Method': evo_split[1],
                'Trigger': evo_split[2]
            }
        elif '=' in line:
            attr, value = line.split('=', 1)
            attr = attr.strip().lower()  # Normalize to lowercase
            value = value.strip()
            # Try to convert to a float for numerical attributes
            try:
                value = float(value)
            except ValueError:
                pass
            current_pokemon[attr] = value
    
    if current_pokemon:
        pokemontxt.append(current_pokemon)
    
    return pokemontxt

def read_pokemon_order(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file.readlines()]

def parse_comparison(value):
    operators = {'<': lambda x, v: x < v,
                  '>': lambda x, v: x > v,
                  '<=': lambda x, v: x <= v,
                  '>=': lambda x, v: x >= v,
                  '=': lambda x, v: x == v}
    
    for op in operators:
        if value.startswith(op):
            try:
                number = float(value[len(op):].strip())
                return operators[op], number
            except ValueError:
                return None, None
    return None, None

def find_pokemon_by_attribute(pokemontxt, attribute, value):
    attribute = attribute.lower()
    comparison_func, num_value = parse_comparison(value)
    result = []
    
    for pokemon in pokemontxt:
        attr_value = pokemon.get(attribute)
        if isinstance(attr_value, (int, float)):
            if comparison_func:
                if comparison_func(attr_value, num_value):
                    result.append(pokemon)
        elif isinstance(attr_value, str):
            if comparison_func is None:
                attr_value = attr_value.lower()
                value = value.lower()
                if attr_value == value:
                    result.append(pokemon)
    
    return result

def filter_pokemon_by_any(pokemontxt, filters):
    filtered_pokemon = []
    for pokemon in pokemontxt:
        match = False
        for attr, values in filters:
            attr = attr.lower()
            values = set(val.strip().lower() for val in values.split(','))
            attr_value = pokemon.get(attr, '').lower()
            if any(val in values for val in attr_value.split(',')):
                match = True
                break
        if match:
            filtered_pokemon.append(pokemon)
    return filtered_pokemon

def filter_pokemon_by_all(pokemontxt, filters):
    for attr, val in filters:
        attr = attr.lower()
        pokemontxt = find_pokemon_by_attribute(pokemontxt, attr, val)
    return pokemontxt

def export_list(pokemon_list, filename):
    with open(filename, 'w') as file:
        for pokemon in pokemon_list:
            file.write(f"{pokemon['Name']}\n")

def sort_pokemon_by_order(pokemon_list, order):
    order_dict = {name: index for index, name in enumerate(order)}
    sorted_pokemon = [pokemon for pokemon in pokemon_list if pokemon['Name'] in order_dict]
    sorted_pokemon.sort(key=lambda pokemon: order_dict.get(pokemon['Name'], float('inf')))
    return sorted_pokemon

def apply_name_replacements(pokemon_list):
    for pokemon in pokemon_list:
        # Check if the ID is in the replacement dictionary
        pokemon_id = int(pokemon.get('ID', -1))  # Default to -1 if ID is missing
        if pokemon_id in NAME_REPLACEMENTS:
            pokemon['Name'] = NAME_REPLACEMENTS[pokemon_id]
    return pokemon_list

import copy

def main():
    filename = 'pokemon.txt'
    order_filename = 'pokemonlist_ALL.txt'
    all_pokemontxt = read_pokemon_file(filename)
    order_list = read_pokemon_order(order_filename)
    
    while True:
        # Get initial filter from user
        print(f"Enter one of the following inputs:")
        print(f"")
        print(f"'categories' shows a list of criteria categories")
        print(f"'values' shows a list of all values for a specific category")
        print(f"'numbers' provides info on formatting numerical input values")
        print(f"'unlisted' provides info on unlisted criteria categories")
        print(f"")
        print(f"'filter' will allow you to view & export lists of Pokemon based on various criteria")
        print(f"")
        initialInput = input("Input > ").lower()
        print(f"")
            
        if initialInput == "categories":
            while True:
                print(f"TYPE1")
                print(f"TYPE2")
                print(f"GenderRate")
                print(f"GrowthRate")
                print(f"Compatibility")
                print(f"Height")
                print(f"Weight")
                print(f"Color")
                print(f"Shape")
                print(f"Habitat")
                print(f"")
                print(f"Categories are NOT case-sensitive.")
                print(f"")
                print(f"")
                print(f"Scroll up to view all criteria categories,")
                print(f"OR:")
                break  # Exit the 'categories' loop

        elif initialInput == "numbers":
            while True:
                print(f"Numerical Values:")
                print(f"- -- - -- -")
                print(f"When inputting a numerical value, you MUST include one of the following operators.")
                print(f"-------")
                print(f"equal to:")
                print(f"=")
                print(f"-------")
                print(f"less than:")
                print(f"<")
                print(f"-------")
                print(f"less than or equal to:")
                print(f"<=")
                print(f"-------")
                print(f"greater than:")
                print(f">")
                print(f"-------")
                print(f"greater than or equal to:")
                print(f">=")
                print(f"-------")
                print(f"ALWAYS include the decimal point.")
                print(f"For example; to filter for values which are equal to 1, you would enter '=1.0' instead of '=1'")
                print(f"")
                print(f"")
                print(f"Scroll up for info,")
                print(f"OR:")
                break  # Exit the 'numbers' loop

        elif initialInput == "unlisted":
            while True:
                print(f"Unlisted Categories:")
                print(f"- -- - -- -")
                print(f"All of the categories are taken from 'pokemon.txt', which is itself taken from the Infinite Fusion game.")
                print(f"As such, there are several \"categories\" which are not listed in the 'categories' list.")
                print(f"- - -")
                print(f"You CAN enter them into the filter, but either;")
                print(f"A. they're not worth filtering for")
                print(f"OR")
                print(f"B. their functionaility is limited and/or broken")
                print(f"- - -")
                print(f"")
                print(f"All unlisted categories are sorted below into header groups;")
                print(f"these headers explain why their respective categories were omitted.")
                print(f"")
                print(f"-------")
                print(f"| All values are unique:")
                print(f"vvv")
                print(f"'InternalName'")
                print(f"'Kind'")
                print(f">>> this is the official Pokedex category: i.e. Bulbasaur is the 'Seed' Pokemon <<<")
                print(f"'Pokedex'")
                print(f">>> technically some Pokemon share Pokedex categories, but that's very uncommon <<<")
                print(f"-------")
                print(f"| Doesn't process data correctly:")
                print(f"(the code isn't set up to process multiple numerical values within a single category)")
                print(f"vvv")
                print(f"'BaseStats'")
                print(f"'EffortPoints'")
                print(f">>> how many EVs are received for KO-ing this Pokemon <<<")
                print(f"'Moves'")
                print(f">>> includes both level and name data for natural movesets <<<")
                print(f"-------")
                print(f"| Rarely (if ever) relevent:")
                print(f"vvv")
                print(f"'BaseEXP'")
                print(f">>> how much EXP is received for KO-ing this Pokemon <<<")
                print(f"'TutorMoves'")
                print(f"'StepsToHatch'")
                print(f"'WildItemCommon'")
                print(f"'WildItemUncommon'")
                print(f"-------")
                print(f"| Incomplete data:")
                print(f"vvv")
                print(f"'Generation'")
                print(f">>> this info is NOT included for Pokemon whose ID numbers range from 1 to 420 <<<")
                print(f"-------")
                print(f"| Battle positioning:")
                print(f"vvv")
                print(f"'BattlerPlayerX'")
                print(f"'BattlerPlayerY'")
                print(f"'BattlerEnemyX'")
                print(f"'BattlerEnemyY'")
                print(f"'BattlerShadowX'")
                print(f"'BattlerShadowSize'")
                print(f"-------")
                print(f"")
                print(f"")
                print(f"Scroll up for info,")
                print(f"OR:")
                break  # Exit the 'unlisted' loop
            
        elif initialInput == "values":
            while True:
                category = input("Enter category to view values: ").strip().lower()
                # Collect unique values for the specified category
                value_list = set()
                for pokemon in all_pokemontxt:
                    if category in pokemon:
                        value_list.add(str(pokemon[category]).strip().lower())
                # Print the unique values
                if value_list:
                    print(f"")
                    print(f"Unique values for category '{category}':")
                    print(f"")
                    for value in sorted(value_list):
                        print(value)
                    print(f"")
                    print(f"Scroll up to view all unique values for the category '{category}'")
                    print(f"OR:")
                else:
                    print(f"No values found for category '{category}'.")
                    print(f"")
                break  # Exit the 'values' loop
    
        elif initialInput == "filter":
            while True:
                attribute = input("Enter a search criteria: ").strip().lower()
                value = input("Enter a value to search for: ").strip().lower()
                
                # Generate initial list
                filters = [(attribute, value)]
                pokemontxt = find_pokemon_by_attribute(all_pokemontxt, attribute, value)
                pokemontxt = sort_pokemon_by_order(pokemontxt, order_list)
                
                # Make a copy of the original dataset for filtering
                unmodified_pokemontxt = copy.deepcopy(all_pokemontxt)
                
                # Apply all filters to get the updated list of Pokémon
                filtered_pokemontxt = filter_pokemon_by_any(unmodified_pokemontxt, filters)
                
                # Sort the filtered list
                sorted_pokemontxt = sort_pokemon_by_order(filtered_pokemontxt, order_list)
                
                # Apply name replacements on the sorted list
                final_pokemontxt = apply_name_replacements(sorted_pokemontxt)
                
                # Print the updated list of Pokémon with current filters
                print(f"\nPokémon which match ANY of the selected filters:")
                for pokemon in final_pokemontxt:
                    print(f"{pokemon['Name']}")
                
                action = input("\nDo you want to export this list, add another attribute, compare with another attribute, or cancel? (export/add/compare/cancel): ").strip().lower()
                
                if action == 'export':
                    if final_pokemontxt:
                        if last_action == 'add':
                            filter_str = 'ANY_' + '_'.join([f"{attr}_{val}" for attr, val in filters])
                        elif last_action == 'compare':
                            filter_str = 'ALL_' + '_'.join([f"{attr}_{val}" for attr, val in filters])
                        else:
                            filter_str = '_'.join([f"{attr}_{val}" for attr, val in filters])
                        
                        export_filename = f"{filter_str}.txt"
                        export_list(final_pokemontxt, export_filename)
                        print(f"List exported to {export_filename}, cancelling current filters and returning to initial input prompt.")
                        break
                
                if action in ("cancel", "exit", "quit", "stop"):
                    print(f"\nCancelling current filters.")
                    break
                
                elif action == 'add':
                    attribute = input("Enter a search criteria: ").strip().lower()
                    value = input("Enter a value to search for: ").strip().lower()
                    filters.append((attribute, value))
                    
                    # Make a copy of the original dataset for filtering
                    unmodified_pokemontxt = copy.deepcopy(all_pokemontxt)
                    
                    # Apply all filters to get the updated list of Pokémon
                    filtered_pokemontxt = filter_pokemon_by_any(unmodified_pokemontxt, filters)
                    
                    # Sort the filtered list
                    sorted_pokemontxt = sort_pokemon_by_order(filtered_pokemontxt, order_list)
                    
                    # Apply name replacements on the sorted list
                    final_pokemontxt = apply_name_replacements(sorted_pokemontxt)
                    
                    # Print the updated list of Pokémon with current filters
                    print(f"\nPokémon which match ANY of the selected filters:")
                    for pokemon in final_pokemontxt:
                        print(f"{pokemon['Name']}")
                    
                    # Print which filters are currently applied
                    print(f"\nCurrent filters applied:")
                    for attr, val in filters:
                        print(f"'{attr}' criteria is '{val}'")
                    
                    last_action = 'add'
                
                elif action == 'compare':
                    attribute = input("Enter a search criteria: ").strip().lower()
                    value = input("Enter a value to search for: ").strip().lower()
                    filters.append((attribute, value))
                    
                    # Make a copy of the original dataset for filtering
                    unmodified_pokemontxt = copy.deepcopy(all_pokemontxt)
                    
                    # Apply all filters to get the updated list of Pokémon
                    filtered_pokemontxt = filter_pokemon_by_all(unmodified_pokemontxt, filters)
                    
                    # Sort the filtered list
                    sorted_pokemontxt = sort_pokemon_by_order(filtered_pokemontxt, order_list)
                    
                    # Apply name replacements on the sorted list
                    final_pokemontxt = apply_name_replacements(sorted_pokemontxt)
                    
                    # Print the updated list of Pokémon with all filters applied
                    print(f"\nPokémon which match ALL of the selected filters:")
                    for pokemon in final_pokemontxt:
                        print(f"{pokemon['Name']}")
                    
                    # Print which filters are currently applied
                    print(f"\nCurrent filters applied:")
                    for attr, val in filters:
                        print(f"'{attr}' criteria is '{val}'")
                    
                    last_action = 'compare'
                
                else:
                    print("Invalid option. Please type 'export', 'add', 'compare'.")
                    continue

if __name__ == "__main__":
    main()