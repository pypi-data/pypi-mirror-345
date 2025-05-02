from typing import List, Tuple
import csv


def get_hosts(host_file: str, host_tags: str | None) -> Tuple[List, int]:
    """Read the hosts file and return a list of hosts to execute commands on."""
    hosts_to_execute: List[Tuple[str, str, int, str, str]] = []
    execute_tags = host_tags.split(",") if host_tags else []

    with open(host_file, "r", encoding="utf-8") as hosts:
        row_line = 1  # Start counting from 1 for human readability
        for row in csv.reader(hosts):
            if row and not row[0].startswith("#"):
                # Process the row only if it is not empty and not a comment
                try:
                    host_name = row[0]
                    ip_address = row[1]
                    ssh_port = int(row[2])
                    username = row[3]
                    key_path = row[4] if len(row) > 4 else ""
                    tags = row[5] if len(row) > 5 else ""
                except IndexError:
                    pass  # Ignore incomplete row
                except ValueError:
                    print(
                        f"Hosts file: {host_file} parse error at row {row_line}. Skipping!"
                    )
                else:
                    if host_tags is None or set(tags.split(":")).intersection(
                        set(execute_tags)
                    ):
                        hosts_to_execute.append(
                            (
                                host_name,
                                ip_address,
                                ssh_port,
                                username,
                                key_path,
                            )
                        )
            row_line += 1  # Row line always counts even if it is empty

    if hosts_to_execute:
        max_name_length = max(len(name) for name, *_ in hosts_to_execute)
        return (hosts_to_execute, max_name_length)
    return ([], 0)
