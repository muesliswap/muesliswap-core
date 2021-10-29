import os, json
from web3 import Web3

RPC_URL = "https://smartbch.greyh.at"
FACTORY_ADDR = "0x72cd8c0B5169Ff1f337E2b8F5b121f8510b52117"
ROUTER_ADDR = "0x87786fFa56d47a3862e272E67C82d9d9Fae14347"
WETH_ADDR = "0x3743eC0673453E5009310C727Ba4eaF7b3a1cc04"
DEPLOYER_ADDR = "0x1307cD19774Ee946474a9FdCd08374fa675DD038"
MILK_ADDR = "0xc8E09AEdB3c949a875e1FD571dC4b3E48FB221f0"
SPOON_ADDR = "0xcc0C48A4A2950AA2a0C7501cF2fEf9140ce8681F"

FACTORY_TX = '0x189339b4c82cd6b6d9d78f62bc21eacb4077ab280083630a853e97b8eaf8167a'
ROUTER_TX = '0xa2a6a54e855699a0fc2ba226baf580668a83ecb2123649d2a53fd00a6095b986'
FARMING_TX = '0x028a6a890d38dfb316d2e390fed0e019ca04b82387933c729efe81b9cc26426d'

provider = Web3.HTTPProvider(RPC_URL)
w3 = Web3(provider)
if not w3.isConnected():
    print(f"Error: Couldn't connect to {RPC_URL}")
    exit(1)

def compare_contract(w3, deploy_tx_hash, filename, name, args):
    deploy_tx = w3.eth.get_transaction(deploy_tx_hash)
    deploy_tx_code = deploy_tx['input']
    # deployed_code = binascii.hexlify(w3.eth.get_code(address)).decode('utf8')
    if not os.path.exists(filename):
        print(f"Error: file {filename} not found. Did you clone the repo and run yarn compile?")
        exit(1)
    with open(filename) as f:
        obj = json.load(f)
        try:
            compiled_code = obj['evm']['bytecode']['object']
        except:
            compiled_code = obj['bytecode']
        abi = obj['abi']
        contract = w3.eth.contract(abi=abi, bytecode=compiled_code)
        test_code = contract.constructor(*args).buildTransaction()['data']
    # print("Lengths: %d %d" % (len(test_code), len(deploy_tx_code)))
    
    # Metadata (last 32 bytes) differs by development environment and isn't comparable
    # See: https://ethereum.stackexchange.com/questions/94115/cannot-verify-contract-bytecode-has-small-difference
    solc_idx = test_code.find('736f6c63')
    metadata_idx = solc_idx - 64 - 2
    test_code = test_code[:metadata_idx] + test_code[solc_idx:]
    deploy_tx_code = deploy_tx_code[:metadata_idx] + deploy_tx_code[solc_idx:]

    if test_code == deploy_tx_code:
        print(f"[OK] Contract '{name}' deployed in tx {deploy_tx_hash} matches with {filename}")
        return True
    else:
        print(f"[ERR] Contract '{name}' deployed in tx {deploy_tx_hash} doesn't match with {filename} !")
        return False


if __name__ == "__main__":
    compare_contract(w3, FACTORY_TX, "./build/MuesliFactory.json", "factory", [DEPLOYER_ADDR])
    compare_contract(w3, ROUTER_TX, "../muesliswap-periphery/build/MuesliRouter.json", "router", 
        [FACTORY_ADDR, WETH_ADDR]  # constructor
    )
    compare_contract(w3, FARMING_TX, "../muesliswap-farming/build/contracts/MasterFarmer.json", "farmer", 
        [MILK_ADDR, SPOON_ADDR, DEPLOYER_ADDR, 0x2386f26fc10000, 1110595, 10]  # constructor
    )
