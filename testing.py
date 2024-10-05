from main import find_trams_at_stop, calculate_stops_and_transfers, find_trams_through_all_stops, find_routes_between_stops
import json


def run_tests(test_data):
    result_string = ''
    for test in test_data['tests']:
        function_name = test['function_name']
        inputs = test['input']
        expected_output = test['expected_output']

        if function_name == 'find_trams_at_stop':
            actual_output = find_trams_at_stop(*inputs)
        elif function_name == 'calculate_stops_and_transfers':
            actual_output = calculate_stops_and_transfers(*inputs)
        elif function_name == 'find_trams_through_all_stops':
            actual_output = find_trams_through_all_stops(*inputs[:-1], tram_routes=inputs[-1])
        elif function_name == 'find_routes_between_stops':
            actual_output = find_routes_between_stops(*inputs)
        else:
            print(f"Unknown function: {function_name}")
            continue

        test_passed = actual_output == expected_output

        result_string += f"Function: {function_name}\n"
        result_string += f"Input: {inputs}\n"
        result_string += f"Expected Output: {expected_output}\n"
        result_string += f"Actual Output: {actual_output}\n"
        result_string += f"Test Passed: {test_passed}\n"
        result_string += "-" * 40 + '\n'

    return result_string


if __name__ == "__main__":
    with open('tests.json', 'r', encoding='utf-8') as f:
        tests = json.load(f)

    result = run_tests(tests)
    with open('TestProtocol.txt', 'w', encoding='utf8') as file:
        file.write(result)
