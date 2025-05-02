import json
from pprint import pprint

TOTAL_DURATION = 'total_duration'
CALL_COUNT = 'call_count'
NETWORK_DURATION = 'network_duration'
SERVER_DURATION = 'server_duration'

class TimingData:
    def __init__(self):
        self._run_data = {}  # key = run_id
        self._start_times = {}  # key = run_id
        self._end_times = {}  # key = run_id

    def start_time(self, time, run_id):
        self._start_times[run_id] = time

    def end_time(self, time, run_id):
        self._end_times[run_id] = time

    def dump_data(self, title, run_id):
        print(f"______________________________________ {title}")
        pprint(self._run_data[run_id])
        print("______________________________________")

    def init_from_json(self, json_string, run_id):
        timing_data = json.loads(json_string.value)
        self._run_data[run_id] = timing_data

    def add_method_duration(self, run_id, method_name, duration):
        if run_id not in self._run_data:
            self._run_data[run_id] = {}

        if method_name not in self._run_data[run_id]:
            self._run_data[run_id][method_name] = {
                TOTAL_DURATION: duration,
                CALL_COUNT: 1,
                NETWORK_DURATION: 0,  # not yet calculated
                SERVER_DURATION: 0  # not yet calculated
            }
            return

        method_stats = self._run_data[run_id][method_name]
        method_stats[CALL_COUNT] += 1
        method_stats[TOTAL_DURATION] += duration

    # ONLY used to present data to humans,
    def transform_and_round_ms(self, value):
        return round(value * 1000, 2)

    def transform_and_round_sec(self, value):
        return round(value, 2)

    def clear_statistics(self, run_id=None):
        if run_id:
            self._run_data.pop(run_id, None)
            self._start_times.pop(run_id, None)
            self._end_times.pop(run_id, None)
        else:
            self._run_data.clear()
            self._start_times.clear()
            self._end_times.clear()

    def incorporate_end_of_run_server_data(self, server_data: 'TimingData', run_id):
        if run_id not in self._run_data:
            raise ValueError(f"Run ID '{run_id}' not found in client data.")
        if run_id not in server_data._run_data:
            raise ValueError(f"Run ID '{run_id}' not found in server data.")

        total_server = 0
        client_methods = self._run_data[run_id]
        server_methods = server_data._run_data[run_id]

        #Fileter out methods with "timing_statistics" in the name, was causing problems
        client_method_set = {method for method in client_methods.keys() if "timing_statistics" not in method}
        server_method_set = {method for method in server_methods.keys() if "timing_statistics" not in method}

        if client_method_set != server_method_set:
            missing_in_client = server_method_set - client_method_set
            missing_in_server = client_method_set - server_method_set
            error_msg = "Mismatch in method names between client and server data."
            if missing_in_client:
                error_msg += f" Missing in client: {missing_in_client}."
            if missing_in_server:
                error_msg += f" Missing in server: {missing_in_server}."
            raise ValueError(error_msg)

        filtered_client_methods = {method: stats for method, stats in client_methods.items() if "timing_statistics" not in method}

        for method_name, client_stats in filtered_client_methods.items():
            server_stats = server_methods[method_name]
            server_total_duration = server_stats[TOTAL_DURATION]
            client_total_duration = client_stats[TOTAL_DURATION]
            client_stats[SERVER_DURATION] = server_total_duration
            network_duration = max(client_total_duration - server_total_duration, 0)
            client_stats[NETWORK_DURATION] = network_duration
            total_server += server_total_duration

    def get_statistics(self, run_id=None):
        if run_id:
            return self._get_statistics_for_run(run_id)
        else:
            return self._get_statistics_for_all_runs()

    def _get_statistics_for_all_runs(self):
        all_stats = {}
        for run_id in self._run_data.keys():
            if run_id not in self._start_times or run_id not in self._end_times:
                continue  # Skip this run_id (the initial run "DEFAULT NAME")
                          # TO DO, ELiminate this run_id entirely, refactor MyTorchCLient
            all_stats[run_id] = self._get_statistics_for_run(run_id)
        return all_stats
    
    def _get_statistics_for_run(self, run_id):
        if run_id not in self._run_data:
            return {}
        stats = {}
        for method, data in self._run_data[run_id].items():
            network_duration: float = data.get(NETWORK_DURATION)
            if network_duration is not None:
                network_duration = network_duration
            else:
                network_duration = 0.0
        
            server_duration: float = data.get(SERVER_DURATION)
            if server_duration is not None:
                server_duration = server_duration
            else:
                server_duration = 0.0
        
            total_duration: float = data.get(TOTAL_DURATION, 0)  # Default to 0 if not present
            call_count: int = data.get(CALL_COUNT, 0)  # Default to 0 if not present
            average_duration: float = (total_duration / call_count) if call_count else 0

            stats[method] = {
                CALL_COUNT: call_count,
                'average_duration': average_duration,
                TOTAL_DURATION: total_duration,
                SERVER_DURATION: server_duration,
                NETWORK_DURATION: network_duration
            }
        return stats
    
    def print_statistics(self, summary_only):
        all_stats = self.get_statistics()
        for run_id, run_stats in all_stats.items():
            display_name = run_id.split("::")[0]
            total_calls = sum(stats[CALL_COUNT] for stats in run_stats.values())
            total_compute_time = sum(stats[SERVER_DURATION] for stats in run_stats.values() if isinstance(stats[SERVER_DURATION], (int, float)))
            total_network_time = sum(stats[NETWORK_DURATION] for stats in run_stats.values() if isinstance(stats[NETWORK_DURATION], (int, float)))
            total_time = total_compute_time + total_network_time

            compute_percentage = (total_compute_time / total_time * 100) if total_time > 0 else 0
            network_percentage = (total_network_time / total_time * 100) if total_time > 0 else 0

            # Ensure rounding is properly applied for display
            compute_percentage = round(compute_percentage,2)
            network_percentage = round(network_percentage,2)

            # Summary for each run
            print()
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            print(f"Timing Data Summary for run {display_name}:")
            print()
            print(f"\tTotal Calls:\t\t{total_calls}")
            print(f"\tTotal Time:\t{self.transform_and_round_sec(total_time):7.2f} sec")
            print(f"\t...Network:\t{self.transform_and_round_sec(total_network_time):7.2f} sec")
            print(f"\t...Sever:\t{self.transform_and_round_sec(total_compute_time):7.2f} sec")
            print(f"\tPercentage in Compute: {compute_percentage}%")
            print(f"\tPercentage in Network: {network_percentage}%\n")

            if summary_only:
                continue

            # Method-wise details
            print()
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            print()
            print(f"By Method: Time taken")
            print()
            for method_name, method_stats in run_stats.items():
                # if method name is timing_statistics, skip it
                if "timing_statistics" in method_name:
                    continue
                network_duration = self.transform_and_round_ms(method_stats[NETWORK_DURATION]) if isinstance(method_stats[NETWORK_DURATION], (int, float)) else "N/A"
                server_duration = self.transform_and_round_ms(method_stats[SERVER_DURATION]) if isinstance(method_stats[SERVER_DURATION], (int, float)) else "N/A"
                avg_duration = method_stats[TOTAL_DURATION] / method_stats[CALL_COUNT]
                percent_of_total_network = (method_stats[NETWORK_DURATION] / total_network_time * 100) if total_network_time > 0 else 0
                percent_of_total_compute = (method_stats[SERVER_DURATION] / total_compute_time * 100) if total_compute_time > 0 else 0

                print(f"\tMethod:\t{method_name}")
                print(f"\t\tCall Count:\t{method_stats[CALL_COUNT]}")
                print(f"\t\tAverage time:\t{self.transform_and_round_ms(avg_duration):7.2f} ms")
                print(f"\t\tTotal time:\t\t{self.transform_and_round_ms(method_stats[TOTAL_DURATION]):7.2f} ms")
                print(f"\t\t...Network:\t\t{network_duration:7.2f} ms" if isinstance(method_stats[NETWORK_DURATION], (int, float)) else "      Network Duration: N/A")
                print(f"\t\t...Server:\t\t{server_duration:7.2f} ms" if isinstance(method_stats[SERVER_DURATION], (int, float)) else "      Server Duration: N/A")
                print("\t\tPercentage of all network time:\t{0:7.2f}%".format(percent_of_total_network))
                print("\t\tPercentage of all server time:\t{0:7.2f}%".format(percent_of_total_compute))
                print()
