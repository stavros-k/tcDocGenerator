from ruamel.yaml import YAML
import os

yaml = YAML()

trains = os.listdir('charts')


def get_charts_of_train(train):
    return os.listdir(f"charts/{train}")


def get_data_of_chart_in_train(train, chart):
    with open(f"charts/{train}/{chart}/values.yaml", "r", encoding="utf_8") as f:
        return yaml.load(f)


def is_services_exist(values):
    return 'service' in values


def is_service_enabled(service):
    if 'enabled' in service:
        return service['enabled']
    else:
        return True


def get_port_protocol(port):
    return port['protocol'] if 'protocol' in port else "TCP"


def main():
    port_list = {}
    for train in trains:
        port_list[train] = []
        charts = get_charts_of_train(train)
        for chart in charts:
            data = get_data_of_chart_in_train(train, chart)
            if is_services_exist(data):
                services = data['service']
                for service_name, service in services.items():
                    if is_service_enabled(service):
                        for port_name, port in service['ports'].items():
                            protocol = "TCP"
                            # port_num, protocol = get_port_number_and_protocol(
                            #     port)
                            if 'enabled' in port:
                                if port['enabled']:
                                    port_num = port['port']
                                protocol = get_port_protocol(port)
                            else:
                                port_num = port['port']
                            # print("-----------------------------")
                            # print(f'Train name: {train}')
                            # print(f'Chart name: {chart}')
                            # print(f'Service enabled: {service_enabled}')
                            # print(f'Service name: {service}')
                            # print(f'Ports Enabled: {port_enabled}')
                            # print(f'Port name: {port_name}')
                            # print(f'Port Number: {port}')
                            port_list[train].append({
                                "train": train,
                                "chart": chart,
                                "service_name": service_name,
                                "port_name": port_name,
                                "port": port_num,
                                "protocol": protocol,
                                "note": ""
                            })
                    else:
                        port_list[train].append({
                            "train": train,
                            "chart": chart,
                            "service_name": service_name,
                            "port_name": "-",
                            "port": 0,
                            "protocol": "-",
                            "note": "Service Disabled"
                        })

    order = ["core", "stable", "games", "incubator", "dev"]
    os.remove("portlist.md")
    with open('portlist.md', 'a', encoding='utf-8') as f:
        for train in order:
            if train in port_list:
                # Sort first by name (because of apps with disabled services)
                sorted_port_list = sorted(
                    port_list[train], key=lambda d: d['chart'])
                # Then sort by port number
                sorted_port_list = sorted(
                    sorted_port_list, key=lambda d: d['port'])
                f.write(f'## {train.capitalize()}\n\n')
                f.write("| App | Service | Port Name | Port | Protocol | Note |\n")
                f.write("|:----|:-------:|:---------:|:----:|:--------:|:----:|\n")
                for port in sorted_port_list:
                    f.write(
                        f'|{port["chart"]}|{port["service_name"]}|{port["port_name"]}|{port["port"] if port["port"] > 0 else "-"}|{port["protocol"]}|{port["note"]}|\n')
                f.write('\n\n')


main()