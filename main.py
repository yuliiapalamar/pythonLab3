import collections
import json


# Function 1: Find all tram numbers that go through a specific stop
def find_trams_at_stop(stop_name, tram_routes):
    trams = []
    for tram, directions in tram_routes.items():
        for direction, stops in directions.items():
            if stop_name in stops:
                trams.append(tram)
    if trams:
        return f"Трамваї, які проходять через зупинку '{stop_name}': {', '.join(sorted(list(set(trams))))}"
    return f"Зупинка '{stop_name}' не знайдена в жодному маршруті."


# Function 2: Calculate number of stops and transfers between two stops
def calculate_stops_and_transfers(start_stop, end_stop, tram_routes):
    if start_stop == end_stop:
        return 'Початкова і кінцева зупинки однакові.'
    queue = collections.deque([(start_stop, 0, None, [])])  # stop name, transfers, current_tram, path
    visited = set()

    while queue:
        current_stop, transfers, current_tram, path = queue.popleft()

        if current_stop == end_stop:
            total_transfers = transfers - 1
            total_stops = 0
            current_stop_index = tram_routes[path[0].split(',')[0]][path[0].split(',')[1]].index(start_stop)
            for item in path:
                tram_number = item.split(',')[0]
                direction = item.split(',')[1]
                next_stop = item.split(',')[2]
                total_stops += tram_routes[tram_number][direction].index(next_stop) - current_stop_index
                current_stop_index = tram_routes[tram_number][direction].index(next_stop)
            return f"Кількість зупинок: {total_stops}, кількість пересадок: {total_transfers}"

        # Prevent visiting the same stop multiple times
        if current_stop in visited:
            continue
        visited.add(current_stop)

        for tram, directions in tram_routes.items():
            for direction, stops in directions.items():
                if current_stop in stops:
                    stop_index = stops.index(current_stop)

                    # Check for forward direction
                    for i in range(stop_index + 1, len(stops)):
                        next_stop = stops[i]
                        new_transfers = transfers if current_tram == tram else transfers + 1
                        queue.append(
                            (next_stop, new_transfers, tram, path +
                             [
                                 f'{tram},{direction},{next_stop}']))

                    # Check for backward direction
                    for i in range(stop_index - 1, -1, -1):
                        next_stop = stops[i]
                        new_transfers = transfers if current_tram == tram else transfers + 1
                        queue.append(
                            (next_stop, new_transfers, tram, path +
                             [
                                 f'{tram},{direction},{next_stop}']))

    return "Маршруту не існує"

# Function 3: Find trams going through all stops in *args
def find_trams_through_all_stops(*stops, tram_routes):
    valid_trams = set(tram_routes.keys())

    for stop in stops:
        trams_at_stop = set()
        found = False
        for tram, directions in tram_routes.items():
            for direction, stops_list in directions.items():
                if stop in stops_list:
                    trams_at_stop.add(tram)
                    found = True

        if not found:
            return f"Зупинку '{stop}' не знайдено в жодному маршруті."

        valid_trams &= trams_at_stop

        if not valid_trams:
            return "Жоден маршрут не проходить через всі зазначені зупинки."

    if valid_trams:
        return f"Трамваї, які проходять через всі зупинки {', '.join(stops)}: {', '.join(valid_trams)}"
    return "Маршрутів, які проходять через всі зупинки, не знайдено."


# Function to find routes between stops (existing from previous code)
def find_routes_between_stops(start_stop, end_stop, tram_routes):
    if start_stop == end_stop:
        return 'Початкова і кінцева зупинки однакові.'
    queue = collections.deque([(start_stop, 0, None, [])])  # stop name, transfers, current_tram, path
    visited = set()

    while queue:
        current_stop, transfers, current_tram, path = queue.popleft()

        if current_stop == end_stop:
            return f"Потрібний шлях:\n{'\n'.join(path)}\nПотрібна кількість пересадок: {transfers - 1}"

        # Prevent visiting the same stop multiple times
        if current_stop in visited:
            continue
        visited.add(current_stop)

        for tram, directions in tram_routes.items():
            for direction, stops in directions.items():
                if current_stop in stops:
                    stop_index = stops.index(current_stop)

                    # Check for forward direction
                    for i in range(stop_index + 1, len(stops)):
                        next_stop = stops[i]
                        new_transfers = transfers if current_tram == tram else transfers + 1
                        queue.append(
                            (next_stop, new_transfers, tram, path +
                             [
                                 f'Сісти на трамвай номер {tram} який прямує до кінцевої зупинки "{stops[-1]}" та вийти на зупинці "{next_stop}"']))

                    # Check for backward direction
                    for i in range(stop_index - 1, -1, -1):
                        next_stop = stops[i]
                        new_transfers = transfers if current_tram == tram else transfers + 1
                        queue.append(
                            (next_stop, new_transfers, tram, path +
                             [
                                 f'Сісти на трамвай номер {tram} який прямує до кінцевої зупинки "{stops[-1]}" та вийти на зупинці "{next_stop}"']))

    return "Маршруту не існує"


def main():
    with open('TramStops.json', 'r', encoding='utf8') as file:
        tram_stops = json.load(file)

    print(find_trams_at_stop("Залізничний вокзал", tram_stops))
    print(find_routes_between_stops("Залізничний вокзал", "вул. Коломийська", tram_stops))
    print(calculate_stops_and_transfers("Залізничний вокзал", "вул. Коломийська", tram_stops))
    print(find_trams_through_all_stops("Залізничний вокзал", "пл. Франка", "вул. Коломийська", tram_routes=tram_stops))


if __name__ == "__main__":
    main()
