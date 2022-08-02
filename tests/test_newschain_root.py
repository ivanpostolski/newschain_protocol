from ctypes import util
from xxlimited import new
import pytest
import brownie
from brownie import NewsChainRoot,NewsChainContractv0,accounts,Contract,TestUtilityContract
import os,binascii
import traceback

# @pytest.fixture(scope="module", autouse=True)
# def newschain_contract(NewsChainContractv0, accounts):
#     t = accounts[0].deploy(NewsChainContractv0)
#     yield t

@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


def test_register_1(accounts):
    nv1 = accounts[0].deploy(NewsChainContractv0)
    nroot = accounts[0].deploy(NewsChainRoot)
    nroot.register_version(0, nv1, nv1.abi)


def test_register_1_api(accounts):
    nv1 = accounts[0].deploy(NewsChainContractv0)
    nroot = accounts[0].deploy(NewsChainRoot)
    rv = nroot.register_version(42, nv1, nv1.abi)
    assert 42 == rv.events['newschain_version']['api'] 

def test_register_1_address(accounts):
    nv1 = accounts[0].deploy(NewsChainContractv0)
    nroot = accounts[0].deploy(NewsChainRoot)
    rv = nroot.register_version(42, nv1, nv1.abi)
    assert nv1.address == rv.events['newschain_version']['contract_address'] 

def test_register_1_abi(accounts):
    nv1 = accounts[0].deploy(NewsChainContractv0)
    nroot = accounts[0].deploy(NewsChainRoot)
    rv = nroot.register_version(42, nv1, nv1.abi)
    assert str(nv1.abi) == str(rv.events['newschain_version']['contract_abi'])

def test_register_2_api(accounts):
    nv1 = accounts[0].deploy(NewsChainContractv0)
    nv2 = accounts[0].deploy(NewsChainContractv0)
    nroot = accounts[0].deploy(NewsChainRoot)
    nroot.register_version(0, nv1, nv1.abi)
    rv = nroot.register_version(1, nv2, nv2.abi)
    assert 1 == rv.events['newschain_version']['api']

def test_register_2_address(accounts):
    nv1 = accounts[0].deploy(NewsChainContractv0)
    nv2 = accounts[0].deploy(NewsChainContractv0)
    nroot = accounts[0].deploy(NewsChainRoot)
    nroot.register_version(0, nv1, nv1.abi)
    rv = nroot.register_version(1, nv2, nv2.abi)
    assert nv2.address == rv.events['newschain_version']['contract_address'] 

def test_register_2_abi(accounts):
    nv1 = accounts[0].deploy(NewsChainContractv0)
    nv2 = accounts[0].deploy(NewsChainContractv0)
    nroot = accounts[0].deploy(NewsChainRoot)
    nroot.register_version(0, nv1, nv1.abi)
    rv = nroot.register_version(1, nv2, nv2.abi)
    assert str(nv2.abi) == str(rv.events['newschain_version']['contract_abi']) 

def test_view_add_version_from_wrong_account(accounts):
    nv1 = accounts[0].deploy(NewsChainContractv0)
    nv2 = accounts[1].deploy(NewsChainContractv0)
    nroot = accounts[0].deploy(NewsChainRoot)
    with pytest.raises(AttributeError):
        nroot.register_version(0, nv1, nv1.abi,{'from':accounts[1]})


