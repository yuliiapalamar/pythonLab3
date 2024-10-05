import collections
import json


def find_routes_between_stops(start_stop, end_stop, tram_routes):
    queue = collections.deque([(start_stop, 0, None, [])])  # stop name, transfers, current_tram, path
    visited = set()

    while queue:
        current_stop, transfers, current_tram, path = queue.popleft()

        if current_stop == end_stop:
            return f"Потрібний шлях:\n{'\n'.join(path)}\nПотрібна кількість пересадок: {transfers}"

        # Prevent visiting the same stop multiple times
        if current_stop in visited:
            continue
        visited.add(current_stop)

        for tram, directions in tram_routes.items():
            for direction, stops in directions.items():
                if (current_stop in stops) and (current_stop != stops[-1]):
                    stop_index = stops.index(current_stop)

                    # Check for forward direction
                    for i in range(stop_index + 1, len(stops)):
                        next_stop = stops[i]
                        new_transfers = transfers if current_tram == tram else transfers + 1
                        queue.append(
                            (next_stop, new_transfers, tram, path +
                             [f'Сісти на трамвай номер {tram} який прямує до кінцевої зупинки "{stops[-1]}" та вийти на зупинці "{next_stop}"']))

                    # Check for backward direction
                    for i in range(stop_index - 1, -1, -1):
                        next_stop = stops[i]
                        new_transfers = transfers if current_tram == tram else transfers + 1
                        queue.append(
                            (next_stop, new_transfers, tram, path +
                             [f'Сісти на трамвай номер {tram} який прямує до кінцевої зупинки "{stops[-1]}" та вийти на зупинці "{next_stop}"']))

    return "Маршруту не існує"


def main():
    with open('TramStops.json', 'r', encoding='utf8') as file:
        tram_stops = json.load(file)
    start_stop = input("Enter starting stop: ")
    end_stop = input("Enter destination stop: ")

    result = find_routes_between_stops(start_stop, end_stop, tram_stops)
    print(result)


if __name__ == "__main__":
    main()
