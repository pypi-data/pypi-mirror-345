from .file import get_json_data
from loguru import logger

evm_network_file_name = 'evm_network.json'


def get_network(name: str):
    if not name:
        return None
    network_ = get_json_data(file_name=evm_network_file_name)
    if name not in network_:
        logger.warning(f'network : {name} is not in {evm_network_file_name}')
        return None
    if 'rpc' not in network_[name]:
        logger.warning(
            f'network : {name} has no rpc in {evm_network_file_name}')
        return None
    return network_[name]


def get_rpc(name: str):
    network_ = get_network(name=name)
    if network_:
        return network_['rpc']
    return None


def get_chain_id(name: str):
    network_ = get_network(name=name)
    if not network_:
        return None
    if 'chain_id' not in network_:
        return None
    return network_['chain_id']


if __name__ == '__main__':
    from .const import ETH
    net = get_network(name=ETH)
    print(net['rpc'])
